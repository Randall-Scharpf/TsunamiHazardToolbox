import arcpy
import numpy as np
import matplotlib.pyplot as plt
import math
from statistics import median

from Tools.Simulator.EarthquakeGenerator import Earthquake

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
        earthquake = Earthquake(magnitude, fault_heading, fault_dip, fault_slip)
        epc_yx = self._longlat_to_yx(epicenter)
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                coord = (y,x)
                r, heading = self._longlat_distance_heading(epicenter, self._yx_to_longlat(coord))
                theta = math.pi / 180 * (90 - heading)
                self.water_height[coord] += earthquake.get_uplift(x - epc_yx[0], y - epc_yx[1])

    def _longlat_distance_heading(self, longlat_a, longlat_b):
        long1 *= longlat_a.X * math.pi / 180
        lat1 *= longlat_a.Y * math.pi / 180
        long2 *= longlat_b.X * math.pi / 180
        lat2 *= longlat_b.Y * math.pi / 180
        x1 = math.sin(long1) * math.cos(lat1)
        y1 = math.cos(long1) * math.cos(lat1)
        z1 = math.sin(lat1)
        x2 = math.sin(long2) * math.cos(lat2)
        y2 = math.cos(long2) * math.cos(lat2)
        z2 = math.sin(lat2)
        vecang = math.acos(x1*x2 + y1*y2 + z1*z2)
        return (vecang * self.EARTH_RADIUS, 0)

    def add_timestep(self, delta):
        for y in range(1, self.shape[0] - 1):
            for x in range(1, self.shape[1] - 1):
                surface_gradient = (
                    (self.base_elevation[y,x+1] + self.water_height[y,x+1]) - (self.base_elevation[y,x-1] + self.water_height[y,x-1]),
                    (self.base_elevation[y+1,x] + self.water_height[y+1,x]) - (self.base_elevation[y-1,x] + self.water_height[y-1,x])
                )
                drag = (
                    -0.01 * math.hypot(self.velocity_x[y,x], self.velocity_y[y,x]) / self.water_height[y,x] * self.velocity_x,
                    -0.01 * math.hypot(self.velocity_x[y,x], self.velocity_y[y,x]) / self.water_height[y,x] * self.velocity_y,
                )
                self.accel_x[y,x] = 9.8 * surface_gradient[0] + drag[0]
                self.accel_y[y,x] = 9.8 * surface_gradient[1] + drag[1]
        change_in_height = np.zeros_like(self.water_height)
        for y in range(self.shape[0]):
            for x in range(self.shape[1]):
                yy = y + 0.001 * (delta * self.velocity_y[y, x] + 0.5 * delta ** 2 * self.accel_y[y, x])
                xx = x + 0.001 * (delta * self.velocity_x[y, x] + 0.5 * delta ** 2 * self.accel_x[y, x])
                change_in_height[y, x] -= self.water_height[y, x]
                y_1 = median([int(math.floor(yy)), 0, self.shape[0]-1])
                x_1 = median([int(math.floor(xx)), 0, self.shape[1]-1])
                y_2 = median([int(math.floor(yy)) + 1, 0, self.shape[0]-1])
                x_2 = median([int(math.floor(xx)) + 1, 0, self.shape[1]-1])
                mod_y = (yy - int(math.floor(yy)))
                mod_x = (xx - int(math.floor(xx)))
                NW = (y_1, x_1)
                SW = (y_2, x_1)
                NE = (y_1, x_2)
                SE = (y_2, x_2)
                change_in_height[NW] += (1 - mod_y) * (1 - mod_x) * self.water_height[y, x]
                change_in_height[SW] += (mod_y) * (1 - mod_x) * self.water_height[y, x]
                change_in_height[NE] += (1 - mod_y) * (mod_x) * self.water_height[y, x]
                change_in_height[SE] += (mod_y) * (mod_x) * self.water_height[y, x]
        self.water_height += change_in_height
        self.velocity_x += self.accel_x * delta
        self.velocity_y += self.accel_y * delta

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
        y = median([int(math.floor(index[0])), 0, arr.shape[0]-1])
        x = median([int(math.floor(index[1])), 0, arr.shape[1]-1])
        y_2 = median([int(math.floor(index[0])) + 1, 0, arr.shape[0]-1])
        x_2 = median([int(math.floor(index[1])) + 1, 0, arr.shape[1]-1])
        NW = (y, x)
        SW = (y_2, x)
        NE = (y, x_2)
        SE = (y_2, x_2)
        mod_y = (index[0] - int(math.floor(index[0])))
        mod_x = (index[1] - int(math.floor(index[1])))
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
