import unittest
from z3 import Solver, sat
from assignment import create_bucket_vars, create_action_selectors, \
    exactly_one_action_formula, \
    initial_state_formula, goal_state_formula, step_formula

#
# Author: Tommi Junttila, Aalto University.
# Only personal student use on the Aalto University course
# CS-E3220 Declarative Programming is allowed.
# Redistribution in any form, including posting to public or
# shared repositories or forums, is not allowed.
#


class TestFunctions(unittest.TestCase):
    def setup(self):
        pass

    def test_initial_formula(self):
        bucket_vars = create_bucket_vars(1, 3)
        s = Solver()
        s.add(initial_state_formula(bucket_vars))
        self.assertTrue(s.check() == sat)
        m = s.model()
        # None is returned for variables whose value is irrelevant,
        # the encoding should not allow this
        self.assertTrue(m[bucket_vars[0]] is not None)
        self.assertTrue(m[bucket_vars[1]] is not None)
        self.assertTrue(m[bucket_vars[2]] is not None)
        # Check the values
        self.assertTrue(m[bucket_vars[0]].as_long() == 0)
        self.assertTrue(m[bucket_vars[1]].as_long() == 0)
        self.assertTrue(m[bucket_vars[2]].as_long() == 0)

    def test_goal_formula(self):
        bucket_vars = create_bucket_vars(1, 3)
        s = Solver()
        s.add(goal_state_formula(bucket_vars, 5))
        self.assertTrue(s.check() == sat)
        m = s.model()
        # Check the values
        self.assertTrue((m[bucket_vars[0]] is not None and
                         m[bucket_vars[0]].as_long() == 5) or
                        (m[bucket_vars[1]] is not None and
                         m[bucket_vars[1]].as_long() == 5) or
                        (m[bucket_vars[2]] is not None and
                         m[bucket_vars[2]].as_long() == 5))

    def test_step_formula(self):
        bucket_vars = create_bucket_vars(1, 3)
        action_vars = create_action_selectors(1, 3)
        (fills_vars, empties_vars, pours_vars) = action_vars
        bucket_vars_next = create_bucket_vars(2, 3)
        s = Solver()
        s.add(exactly_one_action_formula(action_vars))
        s.add(step_formula([4, 5, 6], bucket_vars, action_vars, bucket_vars_next))

        # Test one "fills" scenario
        s.push()
        s.add(fills_vars[1], bucket_vars[1] == 2)
        self.assertTrue(s.check() == sat)
        m = s.model()
        # None is returned for variables whose value is irrelevant,
        # the encoding should not allow this
        self.assertTrue(m[bucket_vars_next[0]] is not None)
        self.assertTrue(m[bucket_vars_next[1]] is not None)
        self.assertTrue(m[bucket_vars_next[2]] is not None)
        # Check the values
        self.assertTrue(m[bucket_vars_next[0]].as_long() ==
                        m[bucket_vars[0]].as_long())
        self.assertTrue(m[bucket_vars_next[1]].as_long() == 5)
        self.assertTrue(m[bucket_vars_next[2]].as_long() ==
                        m[bucket_vars[2]].as_long())
        s.pop()

        # Test one "empties" scenario
        s.push()
        s.add(empties_vars[1], bucket_vars[1] == 2)
        self.assertTrue(s.check() == sat)
        m = s.model()
        # None is returned for variables whose value is irrelevant,
        # the encoding should not allow this
        self.assertTrue(m[bucket_vars_next[0]] is not None)
        self.assertTrue(m[bucket_vars_next[1]] is not None)
        self.assertTrue(m[bucket_vars_next[2]] is not None)
        # Check the values
        self.assertTrue(m[bucket_vars_next[0]].as_long() ==
                        m[bucket_vars[0]].as_long())
        self.assertTrue(m[bucket_vars_next[1]].as_long() == 0)
        self.assertTrue(m[bucket_vars_next[2]].as_long() ==
                        m[bucket_vars[2]].as_long())
        s.pop()

        # Test one "pours" scenario
        s.push()
        s.add(pours_vars[1][2], bucket_vars[1] == 2, bucket_vars[2] == 3)
        self.assertTrue(s.check() == sat)
        m = s.model()
        # None is returned for variables whose value is irrelevant,
        # the encoding should not allow this
        self.assertTrue(m[bucket_vars_next[0]] is not None)
        self.assertTrue(m[bucket_vars_next[1]] is not None)
        self.assertTrue(m[bucket_vars_next[2]] is not None)
        # Check the values
        self.assertTrue(m[bucket_vars_next[0]].as_long() ==
                        m[bucket_vars[0]].as_long())
        self.assertTrue(m[bucket_vars_next[1]].as_long() == 0)
        self.assertTrue(m[bucket_vars_next[2]].as_long() == 5)
        s.pop()

        # And one more
        s.push()
        s.add(pours_vars[1][2], bucket_vars[1] == 2, bucket_vars[2] == 5)
        self.assertTrue(s.check() == sat)
        m = s.model()
        # None is returned for variables whose value is irrelevant,
        # the encoding should not allow this
        self.assertTrue(m[bucket_vars_next[0]] is not None)
        self.assertTrue(m[bucket_vars_next[1]] is not None)
        self.assertTrue(m[bucket_vars_next[2]] is not None)
        # Check the values
        self.assertTrue(m[bucket_vars_next[0]].as_long() ==
                        m[bucket_vars[0]].as_long())
        self.assertTrue(m[bucket_vars_next[1]].as_long() == 1)
        self.assertTrue(m[bucket_vars_next[2]].as_long() == 6)
        s.pop()


if __name__ == '__main__':
    unittest.main()
