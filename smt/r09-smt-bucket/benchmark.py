"""
A simple benchmarking script for comparing the efficiency of
non-incremental and incremental BMC.
"""

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#

import timeit


def min_med_max(data):
    """Return the minimum, median and maximum of the argument data list."""
    assert isinstance(data, list) and len(data) > 0
    n = len(data)
    sorted_data = sorted(data)
    return (sorted_data[0], sorted_data[int(n/2)], sorted_data[n-1])


def benchmark():
    """Running time comparison of non-incremental and incremental BMC."""
    instance_args = '([29,9,5],18), 8, out=None'
    repeats = 5
    print('Benchmarking the non-incremental version...')
    res_non_inc = timeit.repeat(f'solve_with_bmc({instance_args})',
                                setup='from bmc import solve_with_bmc',
                                repeat=repeats, number=1)
    print('Benchmarking the incremental version...')
    res_inc = timeit.repeat(f'solve_with_incremental_bmc({instance_args})',
                            setup='from bmc import solve_with_incremental_bmc',
                            repeat=repeats, number=1)
    print('Non-incremental [min,med,max] in seconds: [%.3f,%.3f,%.3f]' %
          min_med_max(res_non_inc))
    print('Incremental     [min,med,max] in seconds: [%.3f,%.3f,%.3f]' %
          min_med_max(res_inc))


if __name__ == '__main__':
    benchmark()
