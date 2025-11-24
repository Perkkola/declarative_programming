"""
Solve the bucket problem with SMT and Z3.
Do not modify this file, the grader will use an unmodified one.
"""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

import sys
from z3 import Solver, sat, unsat, unknown, is_true, z3
from assignment import create_bucket_vars, create_action_selectors, \
    initial_state_formula, goal_state_formula, \
    exactly_one_action_formula, step_formula


class TraceValidationError(Exception):
    """
    This exception is raised if an execution trace contains errors,
    meaning that it is not a valid execution of the buckets system.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def print_solution(bucket_capacities, goal, var_decls, bound, model,
                   out=sys.stdout):
    """
    Print (and validate) the solution found.
    """
    assert isinstance(bucket_capacities, list)
    nof_buckets = len(bucket_capacities)
    assert isinstance(goal, int) and goal >= 0
    assert isinstance(bound, int) and bound >= 1
    assert isinstance(model, z3.ModelRef)

    def err(msg: str):
        """In case of an error, raise a TraceValidationError exception."""
        raise TraceValidationError(msg)

    (bucket_vars_at, action_selectors_at) = var_decls
    assert len(bucket_vars_at) == bound
    assert len(action_selectors_at) == bound-1

    # Some helper functions
    def log(txt):
        if out is not None:
            out.write(txt+'\n')

    def decode_state(i: int):
        assert 1 <= i <= bound
        state = []
        for bucket in range(0, nof_buckets):
            if model[bucket_vars_at[i-1][bucket]] is None:
                err('The model does not define the values of all the buckets')
            state.append(model[bucket_vars_at[i-1][bucket]].as_long())
        return state

    prev_state = []
    prev_action = []
    current_state = decode_state(1)
    for i in range(1, bound+1):
        log(f'  State {i}: {current_state}')

        for bucket in range(0, nof_buckets):
            if not 0 <= current_state[bucket] <= bucket_capacities[bucket]:
                err(f'The bucket {bucket} contains illegal amount '
                    f'{current_state[bucket]} of water at time step {i}')

        # Validate the previous action
        if i > 1:
            if prev_action[0] == 'fill':
                bucket = int(prev_action[1])
                if current_state[bucket] != bucket_capacities[bucket]:
                    err(f'The bucket {bucket} is not properly filled '
                        f'at time step {i-1}')
                # Check that the contents of other buckers stay the same
                for other in range(0, nof_buckets):
                    if other != bucket and \
                       current_state[other] != prev_state[other]:
                        err(f'The amount of water in the bucket {other} '
                            f'changes unexpectedly at time step {i-1}')
            elif prev_action[0] == 'empty':
                bucket = int(prev_action[1])
                if current_state[bucket] != 0:
                    err(f'The bucket {bucket} is not properly '
                        f'emptied at time step {i-1}')
                # Check that the contents of other buckers stay the same
                for other in range(0, nof_buckets):
                    if other != bucket and \
                       current_state[other] != prev_state[other]:
                        err(f'The amount of water in the bucket {other} '
                            f'changes unexpectedly at time step {i-1}')
            elif prev_action[0] == 'pour':
                bucket_from = int(prev_action[1])
                bucket_to = int(prev_action[3])
                if not ((prev_state[bucket_from] + prev_state[bucket_to] ==
                         current_state[bucket_from] + current_state[bucket_to])
                        and
                        (current_state[bucket_from] == 0 or
                         current_state[bucket_to] ==
                         bucket_capacities[bucket_to])):
                    err(f'The bucket {bucket_from} is not properly poured '
                        f'into the bucket {bucket_to} at time step {i-1}')
                # Check that the contents of other buckers stay the same
                for other in range(0, nof_buckets):
                    if other not in (bucket_from, bucket_to) and \
                       prev_state[other] != current_state[other]:
                        err(f'The amount of water in the bucket {other} '
                            f'changes unexpectedly at time step {i-1}')
            else:
                err('The set of actions contains illegal variables')

        # Decode and validate the action
        if i < bound:
            prev_state = current_state
            current_state = decode_state(i+1)

            (fills_at_i, empties_at_i, pours_at_i) = action_selectors_at[i-1]
            actions_at_i = fills_at_i + empties_at_i
            for pours_bucket_at_i in pours_at_i:
                actions_at_i += pours_bucket_at_i
            true_actions = [act for act in actions_at_i if is_true(model[act])]
            if len(true_actions) == 0:
                err(f'No action selected at time step {i}')
            if len(true_actions) > 1:
                err(f'More than one action selected at time step {i}')
            prev_action = str(true_actions[0]).split('_')
            log(f'  Action {i}: '+(' '.join(prev_action[:-2])))

    # Validate the goal
    goal_buckets = [b for b in range(0, nof_buckets)
                    if current_state[b] == goal]
    if len(goal_buckets) == 0:
        raise TraceValidationError(f'None of the buckets in the last state '
                                   f'contains {goal} liters of water')


def solve_with_bmc(instance, max_bound, out=sys.stdout):
    """
    Solve the bucket instance with bounded model checking.
    Do not modify this method.
    """
    assert isinstance(max_bound, int) and max_bound >= 1
    (bucket_capacities, goal) = instance
    assert len(bucket_capacities) >= 1
    assert isinstance(goal, int)
    nof_buckets = len(bucket_capacities)

    def log(txt):
        if out:
            out.write(txt+'\n')

    solution = 'unknown'

    for bound in range(1, max_bound+1):
        log(f'Getting the encoding for the bound {bound}')

        # Bucket variables for all states
        bucket_vars_at = [create_bucket_vars(i, nof_buckets)
                          for i in range(1, bound+1)]
        action_selectors_at = [create_action_selectors(i, nof_buckets)
                               for i in range(1, bound)]

        # Create the solver instance
        solver = Solver()

        # Force the initial state to be legal
        solver.add(initial_state_formula(bucket_vars_at[1-1]))

        # Force the last state to be a goal state
        solver.add(goal_state_formula(bucket_vars_at[bound-1], goal))

        # Must take exactly one action
        for i in range(1, bound):
            solver.add(exactly_one_action_formula(action_selectors_at[i-1]))

        # Encode the actions
        for i in range(1, bound):
            solver.add(step_formula(bucket_capacities,
                                    bucket_vars_at[i-1],
                                    action_selectors_at[i-1],
                                    bucket_vars_at[i-1+1]))

        # Check if we have a solution already
        log(f'Solving the encoding for the bound {bound}')
        result = solver.check()
        log(f'Done, the result is: {result}')
        if result == unsat:
            # No solution yet
            # End of story?
            if bound == max_bound:
                solution = 'not found'
                break
        elif result == sat:
            # Yes, a solution found!
            model = solver.model()
            log(f'The bucket capacities are: {bucket_capacities}')
            log(f'The goal is: {goal}')
            log('The solution is:')
            print_solution(bucket_capacities, goal,
                           (bucket_vars_at, action_selectors_at),
                           bound, model, out)
            solution = 'found'
            break
        else:
            assert result == unknown
            log(f'"unknown" (with reason "{solver.reason_unknown()}") '
                f'returned by the solver, aborting')
            solution = 'error'
            break

    return solution


def solve_with_incremental_bmc(instance, max_bound, out=sys.stdout):
    """
    Solve the bucket instance with incremental bounded model checking.
    Do not modify this method.
    """
    assert isinstance(max_bound, int) and max_bound >= 1
    (bucket_capacities, goal) = instance
    assert len(bucket_capacities) >= 1
    assert isinstance(goal, int)
    nof_buckets = len(bucket_capacities)

    def log(txt):
        if out:
            out.write(txt+'\n')

    solution = 'unknown'

    # Bucket variables for the initial state (time 1)
    bucket_vars_at_i = create_bucket_vars(1, nof_buckets)

    # We remember all the created state and action selection variables
    # because we need them when validating and printing the solution
    bucket_vars_at = [bucket_vars_at_i]
    action_selectors_at = []

    # Create one solver instance that we'll use all the time
    solver = Solver()

    # Force the initial state to be legal
    log('Getting the encoding for the bound 1')
    solver.add(initial_state_formula(bucket_vars_at_i))

    bound = 1
    while True:
        # Create a backtracking point for solver state
        solver.push()
        # Temporarily force the last state to be a goal state
        solver.add(goal_state_formula(bucket_vars_at_i, goal))

        # Check if we have a solution already
        log(f'Solving the encoding for the bound {bound}')
        result = solver.check()
        log(f'Done, the result is: {result}')
        if result == unsat:
            # No solution yet
            # End of story?
            if bound == max_bound:
                solution = 'not found'
                break
            # Retract the goal state formula
            solver.pop()

            log(f'Getting the encoding for the bound {bound+1}')

            # Create action selector variables
            action_selectors_at_i = create_action_selectors(bound, nof_buckets)
            action_selectors_at.append(action_selectors_at_i)
            # Create next state bucket variables
            bucket_vars_at_next_i = create_bucket_vars(bound+1, nof_buckets)
            bucket_vars_at.append(bucket_vars_at_next_i)

            # Must take exactly one action
            solver.add(exactly_one_action_formula(action_selectors_at_i))

            # Encode the actions
            solver.add(step_formula(bucket_capacities,
                                    bucket_vars_at_i,
                                    action_selectors_at_i,
                                    bucket_vars_at_next_i))

            bucket_vars_at_i = bucket_vars_at_next_i
            bound += 1
        elif result == sat:
            # Yes, a solution found!
            model = solver.model()
            log(f'The bucket capacities are: {bucket_capacities}')
            log(f'The goal is: {goal}')
            log('The solution is:')
            print_solution(bucket_capacities, goal,
                           (bucket_vars_at, action_selectors_at),
                           bound, model, out)
            solution = 'found'
            break
        else:
            assert result == unknown
            log(f'"unknown" (with reason "{solver.reason_unknown()}") '
                f'returned by the solver, aborting')
            solution = 'error'
            break

    return solution
