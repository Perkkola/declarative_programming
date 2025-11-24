"""Encode parity game in a Z3 SMT formula."""

# Do NOT edit or add the import statements.
# ... except if you need other Z3 methods, import them in the statement below.
# This is probably not needed as the ones below are enough for an encoding.
from z3 import Bool, Int, Not, And, Or, Implies, If

#
# Some auxiliary functions are defined first, it is probably a good idea
# to have a look on them, too.
# The parts that you should fill are marked with "INSERT YOUR CODE HERE".
#


def exactly_one_formula(formulas):
    """
    Return a formula that evaluates to true if and only if
    exactly one of the argument formulas evaluates to true.
    This is a straightforward, quadratic construction; better ones do exist.
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


def get_s_var(node):
    """
    States of the game guessed to be reachable (the S node set)
    are represented, for each "node", with a Boolean variable "S_node".
    Do NOT modify this method.
    """
    return Bool(f'S_{node}')


def get_t_var(edge):
    """
    The strategy of Eloise and all outgoing edges of Abelard (the T edge set)
    are represented, for each edge (v, w), with predicate "T_v_w".
    Do NOT modify this method.
    """
    assert isinstance(edge, tuple) and len(edge) == 2
    (source, target) = edge
    return Bool(f'T_{source}_{target}')


def get_x_var(node):
    """
    The integer variables "x_node" are needed, for each "node",
    to check that no loop in the game is won by Abelard.
    Do NOT modify this method.
    """
    return Int(f'x_{node}')


def force_initial_node(initial_node):
    """
    Return the constraint forcing the initial node to be in the game.
    Do NOT modify this method.
    """
    return get_s_var(initial_node)


def guess_eloise_strategy(eloise_nodes, edges_out):
    """
    Eloise should guess exactly one outgoing edge for
    each guessed to be reachable node.
    Arguments:
    - eloise_nodes is the set of Eloise's nodes
    - edges_out is a dictionary mapping each node to a list of
      outgoing edge neighbour nodes.
    """
    assert isinstance(eloise_nodes, set)
    assert isinstance(edges_out, dict)
    constraints = []
    for node in eloise_nodes:
        out_edge_vars = [get_t_var((node, w)) for w in edges_out[node]]
        constraints.append(Implies(get_s_var(node),
                                   exactly_one_formula(out_edge_vars)))
    return And(constraints)


def force_abelard_successors(abelard_nodes, edges_out):
    """
    Abelard nodes that have been guessed to be reachable
    (ie, in the S node set)
    will force also all their outgoing edges to be reachable
    (ie, in the T edge set).
    Arguments:
    - abelard_nodes is the set of Abelard's nodes
    - edges_out is a dictionary mapping each node to a list of
      outgoing edge neighbour nodes.
    """
    assert isinstance(abelard_nodes, set)
    assert isinstance(edges_out, dict)
    constraints = []
    for node in abelard_nodes:
        out_edge_vars = [get_t_var((node, w)) for w in edges_out[node]]
        for var in out_edge_vars:
            constraints.append(Implies(get_s_var(node),
                                var))
    return And(constraints)


def force_nodes_with_incoming_edges(nodes, edges_in):
    """
    Force nodes with guessed reachable incoming edges (ie, in the T edge set)
    to also be guessed to be reachable (ie, in the S node set).
    Arguments:
    - nodes is the set of all nodes
    - edges_in is a dictionary mapping each node to a list of
      incoming edge neighbour nodes.
    """
    constraints = []
    for node in nodes:
        for v in edges_in[node]:
            constraints.append(Implies(get_t_var((v, node)),
                                    get_s_var(node)))
            
    # for node in nodes:
    #     ors = []
    #     for v in edges_in[node]:
    #         ors.append(get_t_var((v, node)))
                       
    #     constraints.append(Implies(Or(ors),
    #                                 get_s_var(node)))
    return And(constraints)


def remove_abelard_wins(edges, omega):
    """
    Remove all models which contain a guessed-to-be-reachable loop
    consisting of only nodes with priority 1.
    Arguments:
    - edges is the set of all adges, each edge being a pair (source, target).
    - omega is the priority function mapping all nodes to {0,1}.
    """
    assert isinstance(edges, set)
    assert isinstance(omega, dict)
    constraints = []
    for edge in edges:
        v = edge[0]
        w = edge[1]

        constraints.append(Implies(
            And(get_t_var((v, w)), omega[v] == 1),
            get_x_var(v) > get_x_var(w)
        ))
    return And(constraints)
