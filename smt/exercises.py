# Import Z3 so that we can use it
from z3 import *

if __name__ == '__main__':      
    s = Solver()
    S = DeclareSort('S')
    BitVec()
    x, y, z = Consts('x y z', S)
    f = Function('f', S, S)
    h = Function('h', S, S)
    g = Function('g', S, S, S)

    # s.add(And(x == f(y), y != f(x)))
    # s.add(And(f(f(x)) == y, f(z) == z, x == z, y != z))
    # s.add(And(x == y, y == z, g(f(x), y) != g(f(z), z)))
    s.add(And(f(h(x)) == y, h(f(x)) != y))

    status = s.check() 
    assert status == sat
    print(s.model())