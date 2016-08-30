"""Unit tests for fixed_point."""

import sys
import unittest

from fixed_point import fixed_point as fp
from fixed_point import Logger

class TestFixedPoint(unittest.TestCase):
    def test_nonrecursive(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, _):
            return 5
        self.assertEquals(5, f(10))

    def test_linear_recursion(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            if not x:
                return 1
            return x * f_(x-1)

        self.assertEquals(120, f(5))


    def test_tree_recursion(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            if x == 0 or x == 1:
                return 1
            return f_(x-1) + f_(x-2)
        self.assertEquals(13, f(6))

    def test_self_cycle(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            return f(x)

        self.assertEquals(0, f(5))

    def test_cycle_size_2(self):
        graph = {
            'a': 'b',
            'b': 'a',
        }
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            assert x in graph
            return f_(graph[x])
        self.assertEquals(0, f('a'))

    def test_cycle_size_5(self):
        graph = {
            'a': 'b',
            'b': 'c',
            'c': 'd',
            'd': 'e',
            'e': 'a',
        }

        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            return f_(graph[x])

        self.assertEquals(0, f('a'))

    def test_path_by_cycle(self):
        graph = {
            'start': 'cycle-1',
            'cycle-1': 'cycle-2',
            'cycle-2': 'cycle-1',
        }

        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            return f(graph[x])

        self.assertEquals(0, f('start'))

    def test_non_latice(self):
        # What does it take for a function to qualify for the @fp decorator, logger?
        # Can we detect that a function doesn't qualify?
        # I suspect it's impossible to detect generally, but here are some
        # functions that do not qualify:
        logger = Logger()
        @fp(int, logger)
        def ever_increasing_self_loop(x, f_):
            return f_(x) + 1

        logger = Logger()
        @fp(int, logger)
        def unbounded_set(x, f_):
            return f_(x+1)

        logger = Logger()
        @fp(bool, logger)
        def unstable(x, f_):
            return not f_(x)


    def test_increaser(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            return min(f_(x) + 1, 100)
        self.assertEquals(100, f(0))

    def test_two_calls_does_work_once(self):
        logger = Logger()
        @fp(int, logger)
        def f(x, f_):
            if x <= 0:
                return 0
            return f_(x - 1) + 1
        self.assertEquals(5, f(5))
        # TODO(jasonpr): Check that we return immediately.
        self.assertEquals(5, f(5))

    def test_reevaluate_late(self):
        children = {
            # Note that order of hub's children matters to our test.
            # The last child that hub checks, c, should cause an
            # invalidation and re-evaluation of a and b.
            'hub': ['a', 'b', 'c'],
            'a': ['hub'],
            'b': ['hub'],
            'c': ['hub'],
        }

        hot = {'c'}

        logger = Logger()
        @fp(bool, logger)
        def f(x, f_):
            return x in hot or any(f_(child) for child in children[x])

        # As if the order even matters...
        self.assertTrue(f('b'))
        self.assertTrue(f('a'))
        self.assertTrue(f('hub'))
        self.assertTrue(f('c'))


if __name__ == '__main__':
    unittest.main()
