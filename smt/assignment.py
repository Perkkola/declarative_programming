"""
Encode a frequency allocation problem into SMT with Z3.
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
from z3 import Int, Bool, And, Or, Not, Implies, If, Abs

from common import assignment_var


def encode(nof_cells: int, nof_frequencies: int,
           separation: list[list[int]],
           illegal: list[list[bool]]):
    """
    Build a Z3 formula over the variables
    {assignment_var(0),...,assignment_var(nof_cells-1)}
    whose models are in one-to-one correspondence
    to the the valid frequency assignments
    for cells 0,...,nof_cells-1 and frequencies 0,...,nof_frequencies-1'
    with the frequency separation matrix "separation" and
    illegal frequencies mapping "illegal".
    """
    # Input validation
    assert nof_cells >= 1
    assert nof_frequencies >= 1
    # "separation" should be a symmetric nof_cells*nof_cells matrix whose
    # diagonal is zero and other elements are non-negative
    assert len(separation) == nof_cells
    for cell1 in range(0, nof_cells):
        assert len(separation[cell1]) == nof_cells
        assert separation[cell1][cell1] == 0, \
            "separation matrix diagonal is not zero"
        for cell2 in range(0, nof_cells):
            assert isinstance(separation[cell1][cell2], int)
            assert separation[cell1][cell2] >= 0, \
                "separation matrix entries cannot be negative"
            assert separation[cell1][cell2] == separation[cell2][cell1], \
                "separation matrix is not symmetric"
    # "illegal" should be a nof_cells*nof_frequencies Boolean matrix
    assert len(illegal) == nof_cells
    for cell in range(0, nof_cells):
        assert len(illegal[cell]) == nof_frequencies
        for freq in range(0, nof_frequencies):
            assert isinstance(illegal[cell][freq], bool)

    formula = True
    for i in range(nof_cells):
        formula = And(formula, assignment_var(i) >= 0, assignment_var(i) < nof_frequencies)
        for j in range(nof_cells):
            formula = And(formula, Abs(assignment_var(i) - assignment_var(j)) >= separation[i][j])
        for k in range(nof_frequencies):
            formula = And(formula, Implies(illegal[i][k], assignment_var(i) != k))
    # INSERT YOUR CODE HERE, replacing True above with the real thing
    return formula