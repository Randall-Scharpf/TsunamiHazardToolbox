import arcpy

import numpy as np
import os
import random

def get_random_32_letters():
    return "".join([chr(random.randint(ord('a'), ord('z'))) for i in range(32)])

def get_unused_fc_name():
    # generate a feature class name which is very unlikely to be in use
    name = get_random_32_letters()
    # make sure it truly isn't already used and, if needed, try again
    if (name in arcpy.ListFeatureClasses()):
        name = get_unused_fc_name()
    return name

class BathyTopoMercator:
    def __init__(self, topography):
        self.topography = topography

    def getPeakAntipodes(self):
        max_height = 0
        max_height_loc = (-1, -1)
        for x in range(5):
            for y in range(8):
                zone_left = arcpy.Point(x * 36 - 180, y * 22.25 - 89)
                zone_right = arcpy.Point((x if x<5 else x-5) * 36, y * -22.25 + 66.75)
                arr_left = arcpy.RasterToNumPyArray(self.topography.dataSource, zone_left, 8640, 5340)
                arr_right = arcpy.RasterToNumPyArray(self.topography.dataSource, zone_right, 8640, 5340)
                arr_anti = np.flip(arr_right, axis=0)
                arr_min = np.minimum(arr_left, arr_anti)
                arr_argmax = np.unravel_index(np.argmax(arr_min), arr_min.shape)
                if (arr_min[arr_argmax] > max_height):
                    max_height = arr_min[arr_argmax]
                    max_height_loc = arcpy.Point(zone_left.X + arr_argmax[1] / 240, zone_left.Y + 22.25 - arr_argmax[0] / 240)
        return [max_height_loc, arcpy.Point(max_height_loc.X + 180, -1 * max_height_loc.Y)]

def parse_point(point_layer):
    projected_point_layer = arcpy.management.Project(point_layer, get_unused_fc_name(), arcpy.SpatialReference(4326))
    with arcpy.da.SearchCursor(projected_point_layer, ["SHAPE@XY"]) as cursor:
        point = next(cursor)
    arcpy.management.Delete(projected_point_layer)
    return point[0]
