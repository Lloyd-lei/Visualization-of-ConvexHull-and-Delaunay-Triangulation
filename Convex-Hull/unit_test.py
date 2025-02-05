import unittest
from convex_hull_api import DataCloud

class TestConvexHullAlgorithms(unittest.TestCase):
    def setUp(self):
        # multiple points
        self.points_square = [(0,0), (0,1), (1,0), (1,1)]
        self.points_triangle = [(0,0), (1,1), (2,0)]
        self.points_complex = [(0,0), (1,2), (2,2), (2,0), (1,1), (3,1), (1,0)]
        # edge case test:
        # only two points
        self.points_two = [(3,3), (4,4)]
        # only one points
        self.points_one = [(5,5)]
    
    def test_graham_scan_square(self):
        dc = DataCloud(self.points_square)
        hull = dc.graham_scan()
        # (0,0)->(1,0)->(1,1)->(0,1) and closure
        expected_hull = [(0,0),(1,0),(1,1),(0,1),(0,0)]
        self.assertEqual(hull, expected_hull, "Graham Scan: square hull mismatch.")

    def test_jarvis_march_triangle(self):
        dc = DataCloud(self.points_triangle)
        hull = dc.jarvis_march()
        # (0,0)->(2,0)->(1,1) and closure
        expected_hull = [(0,0),(1,1),(2,0),(0,0)]
        self.assertEqual(hull, expected_hull, "Jarvis March: triangle hull mismatch.")

    def test_quickhull_complex(self):
        dc = DataCloud(self.points_complex)
        hull = dc.quickhull()
        # expect (0,0)->(2,0)->(3,1)->(2,2)->(1,2)->(0,0) and closure
        expected_hull = [(0, 0), (2, 0), (3, 1), (2, 2), (1, 2), (0, 0)]
        self.assertEqual(hull, expected_hull, "QuickHull: complex hull mismatch.")

    def test_monotone_chain_two_points(self):
        dc = DataCloud(self.points_two)
        hull = dc.monotone_chain()
        # only two, closure
        expected_hull = [(3,3), (4,4), (3,3)]
        self.assertEqual(hull, expected_hull, "Monotone Chain: two points hull mismatch.")

    def test_jarvis_march_one_point(self):
        dc = DataCloud(self.points_one)
        hull = dc.jarvis_march()
        # one point, convex is the point 
        expected_hull = [(5,5)]
        self.assertEqual(hull, expected_hull, "Jarvis March: single point hull mismatch.")

    def test_return_steps(self):
        # test if return expected values
        dc = DataCloud(self.points_square)
        steps = dc.graham_scan(return_steps=True)
        # steps is a stack list contains iterature procedures
        self.assertTrue(len(steps) > 0, "Should return at least one step.")
        # the last point must enclose with the first point
        self.assertEqual(steps[-1], [(0,0),(1,0),(1,1),(0,1),(0,0)],
                         "Graham Scan: final step hull mismatch.")
    
if __name__ == '__main__':
    unittest.main()
