import arcpy
import numpy as np
import matplotlib.pyplot as plt
from math import floor
from statistics import median

from Tools.Simulator.EarthquakeGenerator import Earthquake
from Tools.Simulator.GeospatialFlattener import parse_point

class FluidSimulation:
    EARTH_RADIUS = 6378.1370

    def __init__(self, bathymetry_topography):
        wkid = arcpy.da.Describe(bathymetry_topography)["spatialReference"].factoryCode
        if (wkid != 4326):
            arcpy.management.ProjectRaster(bathymetry_topography, "wgs84_bathytopo", arcpy.SpatialReference(4326), "BILINEAR")
            bathymetry_topography = "wgs84_bathytopo"
        else:
            bathymetry_topography = arcpy.da.Describe(bathymetry_topography)["catalogPath"]
        self.base_elevation = arcpy.RasterToNumPyArray(bathymetry_topography, nodata_to_value=0)
        self.shape = self.base_elevation.shape
        self.water_height = np.maximum(np.zeros_like(self.base_elevation), -1 * self.base_elevation)
        self.velocity_x = np.zeros_like(self.base_elevation)
        self.velocity_y = np.zeros_like(self.base_elevation)
        self.accel_x = np.zeros_like(self.base_elevation)
        self.accel_y = np.zeros_like(self.base_elevation)

    def add_earthquake(self, epicenter, magnitude, fault_heading, fault_dip, fault_slip):
        pass

    def add_timestep(self, delta):
        # delta in seconds
        pass

    def get_elevation(self, latlong):
        return self._interpolate(
            self.base_elevation,
            self._longlat_to_yx(latlong)
        )

    def get_wave_elevation(self, latlong):
        return self._interpolate(
            self.base_elevation + self.water_height,
            self._longlat_to_yx(latlong)
        )

    def _interpolate(self, arr, index):
        y = median([int(floor(index[0])), 0, arr.shape[0]-1])
        x = median([int(floor(index[1])), 0, arr.shape[1]-1])
        y_2 = median([int(floor(index[0])) + 1, 0, arr.shape[0]-1])
        x_2 = median([int(floor(index[1])) + 1, 0, arr.shape[1]-1])
        NW = (y, x)
        SW = (y_2, x)
        NE = (y, x_2)
        SE = (y_2, x_2)
        mod_y = (index[0] - int(floor(index[0])))
        mod_x = (index[1] - int(floor(index[1])))
        return (
            (1 - mod_y) * (1 - mod_x) * arr[NW] +
            mod_y * (1 - mod_x) * arr[SW] +
            (1 - mod_y) * mod_x * arr[NE] +
            mod_y * mod_x * arr[SE]
        )

    def _longlat_to_yx(self, longlat):
        arr_x = (longlat.X + 180) / 360 * self.shape[1]
        arr_y = (longlat.Y - 90) / -180 * self.shape[0]
        return (arr_y, arr_x)

    def _yx_to_longlat(self, yx):
        lat_X = yx[1] * 360 / self.shape[1] - 180
        long_Y = yx[0] * -180 / self.shape[0] + 90
        return arcpy.Point(lat_X, long_Y)

# fig, ax = plt.subplots()
# ax.imshow(self.base_elevation)
# yx = self._longlat_to_yx(arcpy.Point(longitude, latitude))
# ax.scatter(yx[1], yx[0], color='red', marker='o', s=25)
# plt.show()