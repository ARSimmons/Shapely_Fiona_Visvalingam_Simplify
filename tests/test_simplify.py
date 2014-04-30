__author__ = 'asimmons'

from simplify import *
from nose.tools import *
import unittest


class test_TriangleCalculator(unittest.TestCase):

  """
  'TriangleCalculator' calculate the effective area of a triangle given
  its vertices -- and returns an area result


  in first test, the triangle with the given points [[0,0],[1,0],[0,1]]
  has a known area of .5

  in second test, the triangle with the given points [[0,0],[0,1],[0,2]]
  has a known area of 0
  """

  def test_calcArea(self):
    # area of 3 coords is .5
    mytriangle_one = TriangleCalculator([0,0], 0)
    mytriangle_two = TriangleCalculator([1,0], 0)
    mytriangle_three = TriangleCalculator([0,1], 0)

    # set prevTriangle & nextTriangle

    mytriangle_two.prevTriangle = mytriangle_one

    mytriangle_two.nextTriangle = mytriangle_three

    result = mytriangle_two.calcArea()

    assert_equal(result, 0.5)

  def test_calcArea_zero_area(self):
    mytriangle_one = TriangleCalculator([0,0], 0)
    mytriangle_two = TriangleCalculator([0,1], 0)
    mytriangle_three = TriangleCalculator([0,2], 0)

    # set prevTriangle & nextTriangle

    mytriangle_two.prevTriangle = mytriangle_one

    mytriangle_two.nextTriangle = mytriangle_three

    result = mytriangle_two.calcArea()

    assert_equal(result, 0)


class test_GeomSimplify(unittest.TestCase):

    def test_simplify_line_remove_zero_area(self):
        # because the area is 0 all coords are returned

       g = GeomSimplify()
       array = [(-1000,0),(0,1),(0,0),(1,0),(2,0),(2,1),(1000,0)]

       line = LineString(array)

       simpleline = g.simplify_line(line, 0)

       result = list(simpleline.coords)

       assert_equal(result, [(-1000,0),(0,1),(0,0),(1,0),(2,0),(2,1),(1000,0)])

    def test_simplify_line_remove_five_pts(self):
        # because end points/beginning points return no
        # areas there are only 5 triangle areas initially calculated
        # triangle1 [(1000,0), (2,1), (2,0)] area = 499, pt 2,1
        # triangle2 [(2,1), (2,0), (1,0)] area = .5, pt 2,0 TO BE REMOVED
        # triangle3 [(2,0), (0,0), (0,1)] area = .5, pt 0,0 TO BE REMOVED
        # triangle4 [(0,0), (1,0), (2,0)] area = 0, pt 1,0 TO BE REMOVED
        # triangle5 [(-1000,0), (0,1), (0,0)] area = 500, pt 0,1
        # after the removal of the area= 0, you create 2 new areas
        # (that are also removed because 1 < 10)
        # triangle1 [(0,1), (0,0), (2,0)] area = 1, pt 0,0 TO BE REMOVED
        # triangle2 [(0,0), (2,0), (2,1)] area = 1, pt 2,0 TO BE REMOVED
       g = GeomSimplify()
       array = [(-1000,0),(0,1),(0,0),(1,0),(2,0),(2,1),(1000,0)]

       line = LineString(array)

       simpleline = g.simplify_line(line, 10)

       result = list(simpleline.coords)

       assert_equal(result, [(-1000.0, 0.0), (0.0, 1.0), (1000.0, 0.0)])

    def test_simplify_multiline_zero_area(self):
        # construct a collection containing two linestrings with 3 coords each
        # have a threshold of 0 so retains all orig
        # coordinates
        # for line 1: [(0,0),(0,1),(4,3)] area= 2 pt 0,1
        # for line 2: [(0,1),(1,1),(2,4)] area= 1.5 pt 1,1
       g = GeomSimplify()
       array = [[(0,0),(0,1),(4,3)], [(0,1),(1,1),(2,4)]]
       mline = MultiLineString(array)
       simpleline = g.simplify_multiline(mline, 0)
       simplecoordslist = []

       for line in simpleline.geoms:
           simplecoordslist.append(list(line.coords))

       assert_equal(simplecoordslist,array)

    def test_simplify_multiline_remove_one_pt(self):
        # construct a collection containing two linestrings with 3 coords each
        # have a threshold of 1.7 so coord 1,1 will be removed
        # for line 1: [(0,0),(0,1),(4,3)] area= 2 pt 0,1
        # for line 2: [(0,1),(1,1),(2,4)] area= 1.5 pt 1,1 TO BE REMOVED
       g = GeomSimplify()
       array = [[(0,0),(0,1),(4,3)], [(0,1),(1,1),(2,4)]]
       mline = MultiLineString(array)
       simpleline = g.simplify_multiline(mline, 1.7)
       simplecoordslist = []

       for line in simpleline.geoms:
           simplecoordslist.append(list(line.coords))

       assert_equal(simplecoordslist, [[(0,0),(0,1),(4,3)], [(0,1),(2,4)]])

    def test_simplify_multiline_two_lines_on_top_of_each_other(self):
        # construct a collection containing two linestrings with 3 coords each
        # that are on top of each other. Make sure the same coord is
        # removed from both
        # for line 1: [(0,1),(1,1),(2,4)] area= 1.5 pt 1,1 TO BE REMOVED
        # for line 2: [(0,1),(1,1),(2,4)] area= 1.5 pt 1,1 TO BE REMOVED
       g = GeomSimplify()
       array = [[(0,1),(1,1),(2,4)], [(0,1),(1,1),(2,4)]]
       mline = MultiLineString(array)
       simpleline = g.simplify_multiline(mline, 1.7)
       simplecoordslist = []

       for line in simpleline.geoms:
           simplecoordslist.append(list(line.coords))

       assert_equal(simplecoordslist, [[(0,1),(2,4)], [(0,1),(2,4)]])


    def test_simplify_ring_eliminate_ring(self):
        # ring deleted because triangle area is .5 (i.e.< 10) & a ring must have a min of 3 pts
        # result will return 'None' if simplified
        g = GeomSimplify()

        array = ([(0, 0), (1, 1), (1, 0)])

        ring = LinearRing(array)

        simplering = g.simplify_ring(ring, 10)

        assert_equal(simplering, None)

    def test_simplify_ring_eliminate_one_pt(self):
        g = GeomSimplify()
        # triangle1 [(8,2), (-4,2), (0,0)] area = 12, pt -4,2
        # triangle2 [(0,0),(5,4),(8,2)] area = 11, pt 5,4 TO BE REMOVED
        # triangle3 [(5,4), (8,2), (-4,2)] area = 12, pt 8,2
        # triangle4 [(-4,2), (0,0), (5,4)] area = 13, pt 0,0
        array = ([(0,0), (5,4), (8,2), (-4,2)])

        ring = LinearRing(array)

        simplering = g.simplify_ring(ring, 11.5)

        result = list(simplering.coords)

        assert_equal(result, [(0.0, 0.0), (8.0, 2.0), (-4.0, 2.0), (0.0, 0.0)])

## TO DO tests for simplify_polygon and simplify_multipolygon ##

#    def test_simplify_polygon(self):
#        # construct a valid polygon (i.e. not self-intersecting) with a hole
#        ext = [(0,0),(0,2),(2,2),(2,0),(0,0)]
#        int = [(1,1),(1,1.5),(1.5,1.5),(1.5,1)]
#        myPoly = Polygon(ext,[int])


if __name__ == "__main__":
    unittest.main()
