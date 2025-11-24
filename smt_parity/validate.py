"""A helper to check the validity of a solution."""


class ValidationError(Exception):
    """
    An exception thrown when a model is not consistent
    with the problem statement.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def check_solution(nodes, edges, initial_node,
                   e_nodes, a_nodes, omega,
                   edges_out, edges_in, s_nodes, t_edges):
    """
    Check that the found model is a valid game strategy
    with which Eloise can win.
    """
    # Input arguments validation
    assert isinstance(nodes, set)
    assert isinstance(e_nodes, set)
    assert isinstance(a_nodes, set)
    assert e_nodes.union(a_nodes) == nodes
    assert initial_node in nodes
    assert isinstance(s_nodes, set)
    assert s_nodes.issubset(nodes)
    assert isinstance(edges, set)
    assert isinstance(t_edges, set)
    assert t_edges.issubset(edges)

    def err(msg: str):
        """A ValidationError is raised in case of an error."""
        raise ValidationError(msg)

    def is_reachable_with_priority_one_s_nodes(start_node, goal_node,
                                               nodes_seen):
        """
        Recursively check for a loop where Abelard wins -
        rather inoptimal for large game graphs.
        """
        assert omega[start_node] == 1
        assert start_node in s_nodes

        if start_node in nodes_seen:
            return

        nodes_seen.add(start_node)

        for neighbour in edges_out[start_node]:
            if omega[neighbour] != 1:
                continue
            if neighbour not in s_nodes:
                continue
            if (start_node, neighbour) not in t_edges:
                continue

            if neighbour == goal_node:
                err(f'A loop won by Abelard found that goes through '
                    f'the node {goal_node} and '
                    f'only uses guessed-to-be-reachable nodes '
                    f'with priority 1!')

            is_reachable_with_priority_one_s_nodes(neighbour, goal_node,
                                                   nodes_seen)

    # A mapping from nodes to nodes
    strategy = {}

    # Check that the initial node is in the guessed nodes
    if initial_node not in s_nodes:
        err('The initial node is not included in the S nodes set')

    # Check that guessed reachable Eloise nodes have exactly one outgoing edge
    for v in e_nodes.intersection(s_nodes):
        out = [w for w in edges_out[v] if (v, w) in t_edges]
        if len(out) != 1:
            err(f'Guessed reachable Eloise node {v} does not '
                f'have exactly one outgoing edge but {len(out)}')
        strategy[v] = out[0]

    # Check that guessed reachable Abelard nodes have all outgoing edges
    for v in a_nodes.intersection(s_nodes):
        out = [w for w in edges_out[v] if (v, w) in t_edges]
        if len(out) != len(edges_out[v]):
            err(f'Guessed reachable Abelard node {v} does not have all '
                f'of its {len(edges_out[v])} outgoing edges')

    # Check that all guessed edges force their destination vertex to the model
    for (v, w) in t_edges:
        if w not in s_nodes:
            err(f'Node {w} is not guessed reachable even though '
                f'it has an incoming edge T_{v}_{w}')

    # Check that non-guessed nodes have no incoming edges
    #for v in nodes.difference(s_nodes):
    #    inn = [w for w in edges_in[v] if (w, v) in t_edges]
    #    if len(inn) > 0:
    #        err(f'Non-guessed node {v} has incoming edges')

    # Check that non-guessed nodes have no outgoing edges
    #for v in nodes.difference(s_nodes):
    #    out = [w for w in edges_out[v] if (v, w) in t_edges]
    #    if len(out) > 0:
    #        err(f'The non-guessed node {v} has outgoing edges')

    # Check for if the model contains any loops Abelard would win
    # by using a slow recursive approach

    for v in nodes:
        if omega[v] != 1:
            continue
        if v not in s_nodes:
            continue
        nodes_seen = set()
        is_reachable_with_priority_one_s_nodes(v, v, nodes_seen)

    return strategy
