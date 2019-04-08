"""
Simple spatial algorithms required for package functionality.

Algorithms include generation of Voronoi diagrams and spacing points on a landscape using Lloyd's algorithm.
"""
from __future__ import absolute_import

import copy
import logging
import math

try:
    from osgeo import osr, ogr
except ImportError as ie:  # pragma: no cover
    logging.warning("Could not import from osgeo: {}".format(ie))
try:
    from scipy.spatial import Voronoi
except ImportError as ie:  # pragma: no cover
    logging.warning("Cannot import Voronoi from scipy.spatial: {}".format(ie))


def calculate_distance_between(x1, y1, x2, y2):
    """
    Calculates the distance between the points (x1, y1) and (x2, y2)

    .. note:: Returns the absolute value

    :param x1: x coordinate of the first point
    :param y1: y coordinate of the first point
    :param x2: x coordinate of the second point
    :param y2: y coordinate of the second point
    :return: the absolute distance between the points
    """
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def calculate_centre_of_mass(points_list):
    """
    Calculates the centre of mass for the non-intersecting polygon defined by points_list.

    .. note:: the centre of mass will be incorrect for intersecting polygons.

    .. note::

            it is assumed that points_list defines, in order, the vertices of the polygon. The last
            point is assumed to connect to the first point.

    :param points_list: a list of x, y points defining the non-intersecting polygon
    :return: the x,y centre of mass
    """
    centre_x = 0
    centre_y = 0
    area = 0
    size = len(points_list)
    points_list.append(points_list[0])
    for i, each in enumerate(points_list):
        if i == size:
            break
        added_area = each[0] * points_list[i + 1][1] - points_list[i + 1][0] * each[1]
        area += added_area
        centre_x += (each[0] + points_list[i + 1][0]) * added_area
        centre_y += (each[1] + points_list[i + 1][1]) * added_area
    area *= 0.5
    try:
        centre_x /= 6 * area
        centre_y /= 6 * area
    except ZeroDivisionError:
        raise ValueError("Points not ordered in polygon")
    return centre_x, centre_y


def lloyds_algorithm(points_list, maxima, n=7):
    """
    Equally spaces the points in the given landscape defined by (0, x_max), (0, y_max) using Lloyd's algorithm.

    Algorthim is:

    - Reflect the points at x=0, x=x_max, y=0 and y=y_max to make boundaries of the Voronoi diagram on the original
     set of points have finite edges
    - Define the Voronoi diagram separating the points
    - Find the centres of the regions of the voronoi diagram for our original set of points
    - Move the our points to the centres of their voronoi regions
    - Repeat n times (for convergence)
    - Edits the points_list to contain the equally-spaced points

    .. note:: all points are assumed to be in the range x in (0, x_max) and y in (0, y_max)

    :param points_list: a list of points to be equally spaced in the landscape
    :param maxima: the maximum size of the landscape to space out within
    :param n: the number of iterations to perform Lloyd's algorthim for.
    :return list containing the new point centres.
    """
    # Note that lloyd's algorithm is only tested at quite a high level
    for num in range(n):
        vor = Voronoi(reflect_dimensions(points_list, maximums=maxima))
        include_regions = []
        # Find our set of points
        for point_index, point in enumerate(vor.points):
            if 0 <= point[0] < maxima[0] and 0 <= point[1] < maxima[1]:
                include_regions.append(vor.point_region[point_index])
        # Find which regions we want to use
        # Find the centres of our regions
        points_list = []
        for region_index in include_regions:
            vertices_to_average = []
            for vertex in vor.regions[region_index]:
                vertices_to_average.append([vor.vertices[vertex][0], vor.vertices[vertex][1]])
            points_list.append(calculate_centre_of_mass(vertices_to_average))
    return points_list


def reflect_dimensions(points, maximums):
    """
    Reflects the provided points across x=0, y=0, x=x_max and y=y_max (essentially tiling the
    polygon 4 times, around the original polygon).

    :param list points: a list of 2-d points to reflect
    :param tuple maximums: tuple containing the x and y maximums
    :return: a list of reflected points
    """
    max_x, max_y = maximums
    out_points = copy.copy(points)
    for reflection_y in [-0.0001, max_y + 0.0001]:
        for point in points:
            out_points.append([point[0], reflection_y + (reflection_y - point[1])])
    for reflection_x in [-0.0001, max_x + 0.0001]:
        for point in points:
            out_points.append([reflection_x + (reflection_x - point[0]), point[1]])
    return out_points


def archimedes_spiral(centre_x, centre_y, radius, theta):
    """
    Gets the x, y coordinates on a spiral, given a radius and theta

    :param int centre_x: the x coordinate of the centre of the spiral
    :param int centre_y: the y coordinate of the centre of the spiral
    :param float radius: the distance from the centre of the spiral
    :param float theta: the angle of rotation

    :return: tuple of x and y coordinates
    :rtype: tuple
    """
    return int(math.floor(radius * math.cos(theta) + centre_x)), int(math.floor(radius * math.sin(theta) + centre_y))


def convert_coordinates(x, y, input_srs, output_srs):
    """
    Converts the coordinates from the input srs to the output srs.

    :param x: the x coordinate to transform
    :param y: the y coordinate to transform
    :param input_srs: the input srs to transform from
    :param output_srs: the output srs to transform to

    :rtype: list
    :return: transformed [x, y] coordinates
    """
    coord_transform = osr.CoordinateTransformation(input_srs, output_srs)
    # create a geometry from coordinates
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    point.Transform(coord_transform)
    return point.GetX(), point.GetY()


def estimate_sigma_from_distance(distance, n):
    """
    Estimates the sigma value from a rayleigh distribution (2-d normal) from a total distance travelled in n steps.

    :param float distance: the total distance travelled
    :param int n: the number of steps

    :return: an estimation of the sigma value required to generate the distance travelled in n steps
    """
    return distance * (2.0 / (math.pi * n)) ** 0.5
