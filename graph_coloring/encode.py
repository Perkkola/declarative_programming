#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

"""Encode k-coloring instances to propositional SAT instances."""

# Do NOT edit or add the import statements
from typing import Set, Tuple

from pysat.formula import CNF


def encode(nof_vertices: int, edges: Set[Tuple[int, int]],
           nof_colors: int) -> CNF:
    """
    Encode the given k-coloring instance into
    propositional CNF SAT instance.
    Arguments:
    - "nof_vertices" is the number of the vertices in the graph to be colored.
      The vertices are represented with integers from 1 to n.
    - "edges" is the set of edges in the graph,
      each edge being a pair (v1, v2) with v1 < v2.
    - nof_colors is the number of available colors.
    Returns a CNF instance whose satisfying truth assignments are in
    one-to-one correspondence to the colorings of the graph that
    use at most "nof_colors" different colors.
    """
    # A helper function that you *should* use!
    # Do NOT modify this function.
    def xvar(vertex: int, color: int) -> int:
        """
        Return the CNF variable for
        the encoding variable x_{vertex,color}
        denoting that "vertex" should be colored with "color".
        """
        assert 1 <= vertex <= nof_vertices
        assert 1 <= color <= nof_colors
        return (vertex-1)*nof_colors+(color-1)+1

    # The number of variables in the instance,
    # at least nof_vertices * nof_colors.
    # Do NOT modify this variable directly.
    nof_vars = nof_vertices * nof_colors

    # A helper function that you can use (but you don't have to).
    # Do NOT modify this function.
    def new_aux_variable() -> int:
        """Allocate a new auxiliary CNF variable."""
        nonlocal nof_vars
        nof_vars += 1
        return nof_vars

    # The constructed CNF instance
    cnf = CNF()

    # INSERT YOUR CODE HERE
    # It should only append appropriate clauses to "cnf".'
    for vertex in range(1, nof_vertices + 1):
      cnf.append([xvar(vertex, color) for color in range(1, nof_colors + 1)]) #At least one color
      for color_1 in range(1, nof_colors + 1):
        for color_2 in range(color_1 + 1, nof_colors + 1):
           cnf.append([-xvar(vertex, color_1), -xvar(vertex, color_2)]) #At most one color

    for edge in edges:
       for color in range(1, nof_colors + 1):
        cnf.append([-xvar(edge[0], color), -xvar(edge[1], color)])

    #For every edge, c(u) =/= c(v)
    return cnf
