#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

"""Encode an integer interval coloring problem instance to a CNF instance."""

# Do not change or add import statements
from pysat.formula import CNF


def encode(n: int, nof_colors: int, break_symmetries: bool) -> CNF:
    """
    Encode an integer interval coloring problem instance to a CNF instance.
    """

    assert n >= 1, 'n must be positive'
    assert nof_colors >= 1, "the amount of colors must be positive"

    # A helper function that you *should* use!
    # Do NOT modify
    def v_cnf(i: int, c: int) -> int:
        """
        Return the positive integer CNF variable number
        for the encoding variable v_{i,c} denoting
        that the number i should be colored with the color c.
        Do NOT modify this method.
        """
        assert 1 <= i <= n
        assert 1 <= c <= nof_colors
        return (i-1)*nof_colors+(c-1)+1

    # The number of variables in the instance; at least n*nof_colors
    # Do NOT modify this directly.
    nof_vars = n*nof_colors

    # A helper function that you may use (you do NOT have to).
    # If you use auxiliary variables, make sure that they do not introduce
    # extra solutions, i.e. solutions that are the same when projected to
    # the important variables of form v_{i,c}.
    def new_aux_variable() -> int:
        """
        Allocate a new auxiliary CNF variable.
        Do NOT modify this function.
        """
        nonlocal nof_vars
        nof_vars += 1
        return nof_vars

    # The clauses in the CNF instance.
    # To add a clause such as (v_{1,1} | !v_{1,2} | !v_{1,3}),
    # write clauses.append([v_cnf(1,1),-v_cnf(1,2),-v_cnf(1,3)]).
    # Do NOT modify
    cnf = CNF()

    # INSERT YOUR CODE HERE
    # It should only add appropriate clauses to "cnf"
    for vertex in range(1, n + 1):
      cnf.append([v_cnf(vertex, color) for color in range(1, nof_colors + 1)]) #At least one color
      for color_1 in range(1, nof_colors + 1):
        for color_2 in range(color_1 + 1, nof_colors + 1):
           cnf.append([-v_cnf(vertex, color_1), -v_cnf(vertex, color_2)]) #At most one color

    for color in range(1, 1 + nof_colors):
        for vertex_1 in range(1, n + 1):
            for vertex_2 in range(1, n + 1):
               if vertex_1 + vertex_2 <= n:
                  cnf.append([-v_cnf(vertex_1, color), -v_cnf(vertex_2, color), -v_cnf(vertex_1 + vertex_2, color)])
          
    # Symmetry breaking if requested
    if break_symmetries:
        # If/when you implement the symmetry reduction,
        # replace "pass" with your own code
        # OPTIONALLY INSERT YOUR CODE HERE
        cnf.append([v_cnf(1, 1)])
        for c in range(2, nof_colors + 1):
            for i in range(1, n + 1):
                clause = [-v_cnf(i, c)]
                for j in range(1, i):
                    clause.append(v_cnf(j, c - 1))
                cnf.append(clause)


    return cnf
