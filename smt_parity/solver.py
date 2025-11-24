"""Solve a two-player parity game with the Z3 SMT solver."""

import sys
from z3 import Solver, sat, unsat, unknown, is_true
from assignment import get_s_var, get_t_var, \
    force_initial_node, guess_eloise_strategy, \
    force_abelard_successors, force_nodes_with_incoming_edges, \
    remove_abelard_wins
from validate import check_solution


def solve_parity_game(edges, initial_node, eloise_nodes, omega,
                      out=sys.stdout):
    """
    Solve a two-player parity game with two priorities 0 and 1.
    The arguments are as follows.
    - edges is the directed edge relation given as
      a set of (source, target) pairs.
    - initial_node is the initial node of the play.
    - eloise_nodes are nodes of the play controlled by Eloise,
      all other nodes are controlled by Abelard.
    - omega is a function from nodes to priorities 0 and 1
      given as a dictionary.
    See the assignment text for description of parity games, some comments:
    - Eloise will win all plays where the priority 0 is seen infinitely often
    - If Eloise has a winning strategy, she also has a positional
      one, playing exactly the same outgoing edge each time she
      leaves a node controlled by her
    - The main idea of the encoding is to guess Eloise's strategy,
      compute a fixpoint of states and edges reachable by any play,
      and then to add constraints which remove all models that contain
      a loop where Abelard would win.
    """
    # edges should be a set of pairs of the form (v, w)
    assert isinstance(edges, set)
    nof_edges = len(edges)
    assert nof_edges >= 1
    for edge in edges:
        assert isinstance(edge, tuple) and len(edge) == 2
    # Extract the set of nodes from the edge list
    nodes = set()
    for (source, target) in edges:
        nodes.add(source)
        nodes.add(target)
    nof_nodes = len(nodes)
    assert initial_node in nodes
    assert isinstance(eloise_nodes, set)
    assert eloise_nodes.issubset(nodes)
    abelard_nodes = nodes.difference(eloise_nodes)
    # All the priorities should be either 0 or 1
    assert isinstance(omega, dict)
    assert set(omega.keys()) == nodes
    for (node, priority) in omega.items():
        assert node in nodes
        assert priority in {0, 1}
    # In and out neighbours of nodes
    edges_in = {node: [] for node in nodes}
    edges_out = {node: [] for node in nodes}
    for (source, target) in edges:
        edges_out[source].append(target)
        edges_in[target].append(source)
    # Each node should have at least one successor
    for node in nodes:
        assert len(edges_out[node]) > 0

    # Helper functions
    def log(txt):
        if out:
            out.write(txt+'\n')

    solution = None
    log('---')
    log(f'{nof_nodes} nodes: {nodes}')
    log(f'{nof_edges} edges: {edges}')
    log(f'initial node: {initial_node}')
    log(f'Eloise nodes: {eloise_nodes}')
    log(f'Abelard nodes: {abelard_nodes}')
    log(f'priorities: {omega}')

    # Create one solver instance that we'll use all the time
    solver = Solver()

    solver.add(force_initial_node(initial_node))

    if len(eloise_nodes) > 0:
        solver.add(guess_eloise_strategy(eloise_nodes, edges_out))

    if len(abelard_nodes) > 0:
        solver.add(force_abelard_successors(abelard_nodes, edges_out))

    solver.add(force_nodes_with_incoming_edges(nodes, edges_in))

    solver.add(remove_abelard_wins(edges, omega))

    # print(solver)

    result = solver.check()
    log(f'The solver says: {result}')

    strategy = {}

    if result == unsat:
        log("Abelard wins!")
        solution = "nonexistent"
    elif result == sat:
        model = solver.model()
        log(f'The model:\n{model}')

        # Decode the solution: S nodes
        s_nodes = {node for node in nodes if is_true(model[get_s_var(node)])}
        log(f'The S nodes: {s_nodes}')

        # Decode the solution: T edges
        t_edges = {edge for edge in edges if is_true(model[get_t_var(edge)])}
        log(f'The T edges: {t_edges}')

        strategy = check_solution(nodes, edges, initial_node,
                                  eloise_nodes, abelard_nodes,
                                  omega, edges_out, edges_in, s_nodes, t_edges)

        log("Eloise wins!")
        solution = "found"
    else:
        assert result == unknown
        log(f'"unknown" (with reason "{solver.reason_unknown()}") returned '
            f'by the solver, aborting')
        solution = 'error'

    if len(strategy) != 0:
        log(f'Winning strategy for Eloise is: {strategy}')

    return (solution, strategy)
