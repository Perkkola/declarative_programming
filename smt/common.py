"""
Common methods for solving the frequency allocation problem with Z3.
"""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

from z3 import Int


def assignment_var(cell: int):
    """
    Get the integer valued Z3 variable for the frequency of "cell".
    do NOT mdify this method, the grader uses an unmodified version.
    """
    assert isinstance(cell, int) and cell >= 0
    return Int(f'frequency_of_cell_{cell}')


class AssignmentValidationException(Exception):
    """The exception raised when assignment validation fails."""


def validate_assignment(assignment: list[int],
                        separation: list[list[int]],
                        illegal: list[bool]):
    """
    Validate a frequency assignment with respect to
    the given "separation" and "illegal" matrices.
    Returns nothing if the validation passes, and
    raises an AssignmentValidationException if the validation fails.
    """
    def err(msg: str):
        raise AssignmentValidationException(msg)

    nof_cells = len(separation)
    assert nof_cells > 0
    nof_frequencies = len(illegal[0])
    assert nof_frequencies > 0

    if len(assignment) != nof_cells:
        err(f'assignment has {len(assignment)} cells instead of {nof_cells}')

    for (celli, freq) in enumerate(assignment):
        if freq not in range(0, nof_frequencies):
            err(f'the cell {celli} is assigned to an illegal frequency {freq}')

    for cell1 in range(0, nof_cells):
        for cell2 in range(0, nof_cells):
            diff = abs(assignment[cell1] - assignment[cell2])
            min_diff = separation[cell1][cell2]
            if diff < min_diff:
                err(f'the difference between the frequencies of '
                    f'the cells {cell1} and {cell2} is less than {min_diff}')

    for cell in range(0, nof_cells):
        freq = assignment[cell]
        if illegal[cell][freq]:
            err(f'the cell {cell} is assigned to an illegal frequency {freq}')
