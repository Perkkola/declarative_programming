#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

"""Encode an induced sub-graph isomorphism problem to a CNF SAT instance."""

# Do not change or add import statements
from pysat.formula import CNF
from graph import Graph


def encode(pattern: Graph, target: Graph) -> CNF:
    """Encode the induced sub-graph isomorhism problem between
    pattern and target graphs to CNF SAT problem."""

    # A helper function that you *should* use!
    # Do NOT modify this function.
    def m_cnf(p_vertex: int, t_vertex: int):
        """
        Return the positive integer CNF variable number
        of the encoding variable m_{p_vertex,t_vertex} denoting that
        the pattern vertex p_vertex is mapped to the target vertex t_vertex.
        """
        assert 1 <= p_vertex <= pattern.nof_vertices
        assert 1 <= t_vertex <= target.nof_vertices
        return (t_vertex-1)*pattern.nof_vertices+(p_vertex-1)+1

    # The number of variables in the instance,
    # at least pattern.nof_vertices * target.nof_vertices
    # Do NOT modify this directly.
    nof_vars = pattern.nof_vertices * target.nof_vertices

    # A helper function that you may use (you do not have to).
    # If you use auxiliary variables, make sure that they do not introduce
    # extra models, i.e. models that are the same when projected to
    # the important variables of form m_{p,v}.
    # Do NOT modify this function.
    def new_aux_variable():
        """Allocate a new auxiliary CNF variable."""
        nonlocal nof_vars
        nof_vars += 1
        return nof_vars

    # The clauses in the CNF instance.
    # To add a clause such as (m_{1,1} | !m_{1,2} | !m_{1,3}),
    # write cnf.append([m_cnf(1,1), -m_cnf(1,2), -m_cnf(1,3)])
    cnf = CNF()

    # INSERT YOUR CODE HERE
    # It should only add appropriate clauses to "clauses" as descibed above.
    # The CNF ecoding should be such that each satisfying truth assignment,
    # when projected to the m_{p,v} literals,
    # corresponds to an induced subgraph isomorphism m as follows:
    # if m_{p,v} is true, then m(p) = v.
    # Thus you should encode the following constraints in CNF:
    # - The m_{p,v} literals encode an injection m
    #   from the pattern graph vertices {1,...,pattern.nof_vertices}
    #   to the target graph vertices {1,...,target.nof_vertices}.
    # - The injection m encoded by the m_{p,v} literals preserves both
    #   adjacency (existence of edges between vertices)
    #   as well as
    #   non-adjacency (non-existence of edges between vertices).
    # See the file graph.py for the graph interface allowing one to
    # obtain the edge relations of the pattern and target graphs in question.


   

    #Injection
    for p_vertex in range(1, pattern.nof_vertices + 1):
        cnf.append([m_cnf(p_vertex, t_vertex) for t_vertex in range(1, target.nof_vertices + 1)])

        #At least one and at most one pattern vertex maps to target
        for t_vertex_1 in range(1, target.nof_vertices + 1):
            for t_vertex_2 in range(t_vertex_1 + 1, target.nof_vertices + 1):
                cnf.append([-m_cnf(p_vertex, t_vertex_1), -m_cnf(p_vertex, t_vertex_2)])

    #At most one pattern vertex per target
    for t_vertex in range(1, target.nof_vertices + 1):
        for p_vertex_1 in range(1, pattern.nof_vertices + 1):
            for p_vertex_2 in range(p_vertex_1 + 1, pattern.nof_vertices + 1):
                cnf.append([-m_cnf(p_vertex_1, t_vertex), -m_cnf(p_vertex_2, t_vertex)])

    #If p_vertex_1 gets mapped to t_vertex, then all p_vertex_1 neighbors get mapped to some neighbor of t_vertex
    for p_vertex_1 in range(1, pattern.nof_vertices + 1):
        for p_vertex_2 in pattern.neighbours[p_vertex_1]:
            for t_vertex in range(1, target.nof_vertices + 1):
                clause = [-m_cnf(p_vertex_1, t_vertex)]
                clause.extend([m_cnf(p_vertex_2, t_neighbor) for t_neighbor in target.neighbours[t_vertex]])
                cnf.append(clause)

    #If p_vertex_2 is not a neighbor of p_vertex_1, then p_vertex_2 must not get mapped to any neighbor of t_vertex
    for p_vertex_1 in range(1, pattern.nof_vertices + 1):
        for p_vertex_2 in range(p_vertex_1 + 1, pattern.nof_vertices + 1):
            if p_vertex_2 not in pattern.neighbours[p_vertex_1]:
                for t_vertex in range(1, target.nof_vertices + 1):
                    for t_neighbor in target.neighbours[t_vertex]:
                        cnf.append([-m_cnf(p_vertex_1, t_vertex), -m_cnf(p_vertex_2, t_neighbor)])

    return cnf
