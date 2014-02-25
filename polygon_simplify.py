#! /usr/bin/env python
# encoding: utf-8

###############################################
## Arielle Simmons                           ##
## GIS Data Engineer                         ##
## Date created:  February 7, 2014           ##
## Date modified: February 23, 2014          ##
###############################################

## This script is to created to simplify
## Polygons using the
## Visvalingam algorithm found here
## http://www2.dcs.hull.ac.uk/CISRG/publications/DPs/DP10/DP10.html

## Threshold is the area of the largest allowed triangle

## testing purposes:
## a = PolygonSimplify()
## a.simplify_ring(0)
## print a.simplify_ring(0)

## a = RingTriangle([[0,0],[1,0],[0,1]])
## a.calcArea()

## points = [[0,0],[1,0],[0,1]]
## p1 = points[0]
## p2 = points[1]
## p3 = points[2]
## abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p1[1] - p3[1]) + p3[0] * (p1[1] - p2[1])) / 2.0

## a.process_file(r'I:\It_19\Simplify_polygons\test_data\multipoly_data\area_code_2007_MULTIPOLY_1.shp', r'I:\It_19\Simplify_polygons\test_data\multipoly_data\area_code_2007_MULTIPOLY_test.shp',5000)
# a = PolygonSimplify(); a.process_file(r'I:\It_19\Simplify_polygons\test_data\multipoly_data\polygon.shp', r'I:\It_19\Simplify_polygons\test_data\multipoly_data\poly_test.shp',5000)

import fiona
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
import heapq
import shapely
from shapely.geometry.polygon import LinearRing
import copy

class RingTriangle:
    def __init__(self, point, index):
        # Need to add better validation

        # Save instance variables
        self.point = point
        self.ringIndex = index
        self.prevTriangle = None
        self.nextTriangle = None

    # enables the instantiation of 'PolygonTriangle' to be compared
    # by the calcArea().
    def __cmp__(self, other):
        return cmp(self.calcArea(), other.calcArea())

    ## calculate the effective area of a triangle given
    ## its vertices -- using the cross product
    def calcArea(self):
        # Add validation
        if not self.prevTriangle or not self.nextTriangle:
            print "ERROR:"

        p1 = self.point
        p2 = self.prevTriangle.point
        p3 = self.nextTriangle.point
        area = abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p1[1] - p3[1]) + p3[0] * (p1[1] - p2[1])) / 2.0
        print area
        return area

class PolygonSimplify:

    def simplify_ring(self, ring, threshold):

        # Build list of RingTriangles
        triangleRing = []
        ## each triangle contains an index and a point (x,y)
        for index, point in enumerate(ring.coords[:-1]):
            triangleRing.append(RingTriangle(point, index))

        # Hook up triangles with next and prev references (doubly-linked list)
        for index, triangle in enumerate(triangleRing):
            # set prevIndex to be the adjacent point to index
            prevIndex = index - 1
            if prevIndex < 0:
                # if prevIndex is less than 0, then it means index = 0, and
                # the prevIndex is set to last value in the index
                # (i.e. adjacent to index[0])
                prevIndex = len(triangleRing) - 1
            # set nextIndex adjacent to index
            nextIndex = index + 1
            if nextIndex == len(triangleRing):
                # if nextIndex is equivalent to the length of the array
                # set nextIndex to 0
                nextIndex = 0
            triangle.prevTriangle = triangleRing[prevIndex]
            triangle.nextTriangle = triangleRing[nextIndex]

        # Build a min-heap from the RingTriangle list
        heapq.heapify(triangleRing)

        # Simplify
        while len(triangleRing) > 2:
            # if the smallest triangle is greater than the threshold, we can stop
            if triangleRing[0].calcArea() >= threshold:
                break
            else:
                triangle = heapq.heappop(triangleRing)
                prev = triangle.prevTriangle
                next = triangle.nextTriangle
                prev.nextTriangle = next
                next.prevTriangle = prev

        # Handle case where we've removed too many points for the ring to be a polygon
        if len(triangleRing) < 3:
            return None

        # Create an list of indices from the triangleRing heap
        indexList = []
        for triangle in triangleRing:
            indexList.append(triangle.ringIndex)

        # Sort the index list
        indexList.sort()

        # Create a new simplified ring
        simpleRing = []
        for index in indexList:
            simpleRing.append(ring.coords[index])

        # ...
        simpleRing.append(simpleRing[0])

        # Convert list into LinearRing
        simpleRing = LinearRing(simpleRing)

        # print statements for debugging to check if points are being reduced...
        print "Starting size: " + str(len(ring.coords))
        print "Ending size: " + str(len(simpleRing.coords))

        return simpleRing


    def simplify_multipolygon(self, mpoly, threshold):
        # break multipolygon into polys
        polyList = mpoly.geoms
        simplePolyList = []

        # call simplify_polygon() on each
        for poly in polyList:
            simplePoly = self.simplify_polygon(poly, threshold)
            #if not none append to list
            if simplePoly:
                simplePolyList.append(simplePoly)

        # check that polygon count > 0, otherwise return None
        if not simplePolyList:
            return None

        # put back into multipolygon
        return MultiPolygon(simplePolyList)

    def simplify_polygon(self, poly, threshold):

        # Get exterior ring
        simpleExtRing = self.simplify_ring(poly.exterior, threshold)

        # If the exterior ring was removed by simplification, return None
        if simpleExtRing is None:
            return None

        simpleIntRings = []
        for ring in poly.interiors:
        ## added 'ring' to the parentheses, then 'poly.interiors' --  original only had threshold
            simpleRing = self.simplify_ring(poly.interiors, threshold)
            if simpleRing is not None:
                simpleIntRings.append(simpleRing)
        return shapely.geometry.Polygon(simpleExtRing, simpleIntRings)

    def process_file(self, inFile, outFile, threshold):

        with fiona.open(inFile, 'r') as input:
            meta = input.meta
            # The outFile has the same crs, schema as inFile
            with fiona.open(outFile, 'w', **meta) as output:

            # Read shapely geometries from file
            # Loop through all shapely objects
                for myGeom in input:

                    myShape = shape(myGeom['geometry'])

                    if isinstance(myShape, Polygon):
                        myShape = self.simplify_polygon(myShape, threshold)
                    elif isinstance(myShape, MultiPolygon):
                        myShape = self.simplify_multipolygon(myShape, threshold)
                    else:
                        raise ValueError('Unhandled geomtry type: ' + repr(myShape.type))

                    # write to outfile
                    if myShape is not None:
                        output.write({'geometry':mapping(myShape), 'properties': myGeom['properties']})

