"""
The main solve routine for finding frequency assignments
for instances given in JSON format.
"""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

import argparse
import json

from z3 import Solver, sat, Or

from common import assignment_var, validate_assignment
from assignment import encode


def get_assignments(nof_cells: int, formula, nof_models: int):
    """
    Find at most nof_models frequency assignments by
    enumerating the models of "formula".
    """
    result = []
    solver = Solver()
    solver.add(formula)
    while len(result) < nof_models and solver.check() == sat:
        model = solver.model()
        assignment = [0 for _ in range(0, nof_cells)]
        for cell in range(0, nof_cells):
            if (v := model[assignment_var(cell)]) is not None:
                assignment[cell] = v.as_long()
        result.append(assignment)
        # Block this assignment in order to find the next new one
        disjunction = []
        for cell in range(0, nof_cells):
            disjunction.append(assignment_var(cell) != assignment[cell])
        solver.add(Or(disjunction))
    return result


def main():
    """
    The main solve routine called from the CLI.
    """
    argp = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Solve a frequency allocation problem instance '
        'by using the Z3 SMT solver.')
    argp.add_argument('filename', help='the instance in JSON format')
    argp.add_argument('-n', type=int, default=100, metavar='N',
                      help='produce atmost N solutions')
    argp.add_argument('--no-validation', action='store_true')
    args = argp.parse_args()

    with open(args.filename, 'r', encoding='utf-8') as handle:
        instance = json.load(handle)
    # print(instance)
    nof_cells = instance['nof_cells']
    nof_frequencies = instance['nof_frequencies']
    separation = instance['separation']
    illegal = instance['illegal']
    formula = encode(nof_cells, nof_frequencies, separation, illegal)
    # print(formula)

    # Get the frequency assignments
    assignments = get_assignments(nof_cells, formula, args.n)
    print(f'Assignments found: {len(assignments)}')
    # Print and validate the frequency assignments
    for assignment in assignments:
        print(f'assignment = {assignment}')
        if not args.no_validation:
            validate_assignment(assignment, separation, illegal)


if __name__ == '__main__':
    main()
