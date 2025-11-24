"""
Encode a bucket problem into SMT-based bounded model checking problem in Z3.
"""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

# Do NOT edit or add the import statements.
# ... except if you need other Z3 methods, import them in the statement below.
# This is probably not needed as the ones below are enough for an encoding.
from z3 import Int, Bool, And, Or, Not, Implies, If

#
# Some auxiliary functions are defined first, it is probably a good idea
# to have a look on them, too.
# The parts that you should fill are marked with "INSERT YOUR CODE HERE".
#


def create_bucket_vars(i: int, nof_buckets: int):
    """
    Create new integer typed bucket Z3 variables for the time step i.
    Intuition: in a satisfying truth assignment, the value of bucket_b_at_i
    gives the amount of water contained in bucket b at time step i.
    Bucket numbering starts from 0, not 1.
    Do not modify this method, the grader will use an unmodified one.
    """
    assert isinstance(i, int) and i >= 1
    assert isinstance(nof_buckets, int) and nof_buckets >= 1
    return [Int(f'bucket_{b}_at_{i}') for b in range(0, nof_buckets)]
    # The same without list comprehension would be as follows:
    # buckets_at_i = []
    # for bucket in range(0, nof_buckets):
    #     buckets_at_i.append(Int(f'bucket_{bucket}_at_{i}'))
    # return buckets_at_i


def create_action_selectors(i: int, nof_buckets: int):
    """
    Create new boolean Z3 variables for selecting the actions
    at the time step i.
    Returns a triple (fills_at_i, empties_at_i, pours_at_i), where
    - fills_at_i is a 1D array and
      fills_at_i[b] = fill_b_at_i for each b in [0..nof_buckets-1],
    - empties_at_i is a 1D array and
      empties_at_i[b] = empties_b_at_i for each b in [0..nof_buckets-1], and
    - pours_at_i is a 2D array and
      pours_at_i[b1][b2] = pour_b1_to_b2_at_i for b1,b2 in [0..nof_buckets-1].
    Intuitions:
    - If fill_b_at_i holds, then at i:th action the bucket b is filled,
      i.e. the bucket b contains bucket_capacities[b] liters of water
      at the time step i+1.
    - If empty_b_at_i holds, then at i:th action the bucket b is emptied,
      i.e. the bucket b contains 0 liters of water at the time step i+1.
    - If pour_b1_to_b2_at_i holds, then at i:th action the contents of
      the bucket b1 are poured into bucket b2,
      i.e. at time step i+1 the bucket b2 contains the water it
      contained at time step i and all the water of the bucket b1
      that could fit in b2; b1 will contains the water it contained
      at time step i but that could not fit in b2.
    Do not modify this method, the grader will use an unmodified one.
    """
    assert isinstance(i, int) and i >= 1
    assert isinstance(nof_buckets, int) and nof_buckets >= 1
    fills_at_i = [Bool(f'fill_{b}_at_{i}') for b in range(0, nof_buckets)]
    empties_at_i = [Bool(f'empty_{b}_at_{i}') for b in range(0, nof_buckets)]
    pours_at_i = [[(Bool(f'pour_{b1}_to_{b2}_at_{i}') if b1 != b2 else False)
                   for b2 in range(0, nof_buckets)]
                  for b1 in range(0, nof_buckets)]
    return (fills_at_i, empties_at_i, pours_at_i)


def exactly_one_formula(formulas):
    """
    Return a Z3 formula that evaluates to true if and only if
    exactly one of the argument formulas evaluates to true.
    This is a straightforward, quadratic size construction ---
    better ones do exist.
    Do not modify this method, the grader will use an unmodified one.
    """
    if len(formulas) == 0:
        return False
    if len(formulas) == 1:
        return formulas[0]
    at_least_one = Or(formulas)
    at_least_two = Or([And(f1, f2) for f1 in formulas for f2 in formulas
                       if f2 is not f1])
    # Note: we have to use "is not" instead of "!=" above because
    # f2 != f1 would be a Z3 formula "f2 != f1",
    # but here we want to check whether f2 is not the same object as f1.
    return And(at_least_one, Not(at_least_two))


def exactly_one_action_formula(action_selectors_at_i):
    """
    Return a Z3 formula that evaluates to true if and only if
    exactly one of the action selector vars in action_selectors_at_i does.
    This basically only takes care of the fact that
    pours_at_i is a 2D array, while fills_at_i and empties_at_i are 1D arrays.
    Do not modify this method, the grader will use an unmodified one.
    """
    (fills_at_i, empties_at_i, pours_at_i) = action_selectors_at_i
    actions_at_i = fills_at_i + empties_at_i
    for pours_bucket_at_i in pours_at_i:
        actions_at_i += pours_bucket_at_i
    return exactly_one_formula(actions_at_i)


def initial_state_formula(bucket_vars_at_i):
    """
    Make and return the initial state Z3 constraint
    forcing that the buckets are empty in the beginning.
    Do not modify this method, the grader will use an unmodified one.
    """
    assert isinstance(bucket_vars_at_i, list)
    assert len(bucket_vars_at_i) > 0
    # Note: "bucket_var == 0" below is a Z3 formula, not an immediate evalution
    return And([bucket_var == 0 for bucket_var in bucket_vars_at_i])


def goal_state_formula(bucket_vars_at_i, goal: int):
    """
    Make and return the Z3 goal constraint stating that at least one of
    the buckets contains the correct (goal) liters of water.
    """
    assert isinstance(bucket_vars_at_i, list)
    assert len(bucket_vars_at_i) > 0
    assert isinstance(goal, int) and goal >= 0
    # INSERT YOUR CODE HERE and replace "True" with the real thing
    formula = True
    return formula


def step_formula(bucket_capacities,
                 bucket_vars_at_i,
                 action_selector_vars_at_i,
                 bucket_vars_at_next_i):
    """
    Make the formula enforcing that the step from
    from the current state (bucket_vars_at_i)
    to the next one (bucket_var_at_next_i)
    corresponds to the action selected (action_selectors_at_i).
    Enforcing that exactly one action is taken is handled elsewhere,
    so not to be worried about here.
    """
    assert isinstance(bucket_capacities, list)
    nof_buckets = len(bucket_capacities)
    assert isinstance(bucket_vars_at_i, list)
    assert len(bucket_vars_at_i) == nof_buckets
    assert isinstance(bucket_vars_at_next_i, list)
    assert len(bucket_vars_at_next_i) == nof_buckets
    (fills_at_i, empties_at_i, pours_at_i) = action_selector_vars_at_i

    # The place to collect the Z3 constraint formulas
    constraints = []

    #
    # First, handle the fills_at_i actions
    #
    for bucket in range(0, nof_buckets):
        # Action: the bucket gets filled
        act = bucket_vars_at_next_i[bucket] == bucket_capacities[bucket]
        # Frame: the other buckets keep their contents
        frame = And([(bucket_vars_at_next_i[other] == bucket_vars_at_i[other])
                     for other in range(0, nof_buckets) if other != bucket])
        # fills_at_i[bucket] implies the action and the frame
        constraints.append(Implies(fills_at_i[bucket], And(act, frame)))

    #
    # Second, the same for empties_at_i
    #
    # INSERT YOUR CODE HERE

    #
    # Finally, the same for pours_at_i
    #
    # INSERT YOUR CODE HERE
    return And(constraints)
