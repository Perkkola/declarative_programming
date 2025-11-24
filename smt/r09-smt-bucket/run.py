"""Run some tests on the bucket problem."""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

from bmc import solve_with_bmc, solve_with_incremental_bmc

if __name__ == '__main__':
    print('Testing non-incremental BMC')
    solve_with_bmc(([9, 5], 3), 9)
    print('')

    print('Testing incremental BMC')
    solve_with_incremental_bmc(([12, 5, 6], 9), 8)
    print('')
