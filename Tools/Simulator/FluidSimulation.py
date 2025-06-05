import arcpy
import numpy as np
import matplotlib.pyplot as plt

class FluidSimulation:
    def __init__(self, bathymetry_topography):
        wkid = arcpy.da.Describe(bathymetry_topography)["spatialReference"].factoryCode
        if (wkid != 4326):
            arcpy.management.ProjectRaster(bathymetry_topography, "wgs84_bathytopo", arcpy.SpatialReference(4326), "CUBIC")
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

    def get_elevation(self, latitude, longitude):
        arr_x = (longitude + 180) / 360 * self.shape[1]
        arr_y = (latitude - 90) / -180 * self.shape[0]
        # fig, ax = plt.subplots()
        # ax.imshow(self.base_elevation)
        # ax.scatter(arr_x, arr_y, color='red', marker='o', s=25)
        # plt.show()
        return self.base_elevation[
            int(arr_y),
            int(arr_x)
        ]

    def get_wave_elevation(self, latitude, longitude):
        arr_x = (longitude + 180) / 360 * self.shape[1]
        arr_y = (latitude - 90) / -180 * self.shape[0]
        # fig, ax = plt.subplots()
        # ax.imshow(self.base_elevation + self.water_height)
        # ax.scatter(arr_x, arr_y, color='red', marker='o', s=25)
        # plt.show()
        return self.base_elevation[
            int(arr_y),
            int(arr_x)
        ] + self.water_height[
            int(arr_y),
            int(arr_x)
        ]
