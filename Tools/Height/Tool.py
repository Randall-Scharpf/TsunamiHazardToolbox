import arcpy
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time

aprx = arcpy.mp.ArcGISProject("CURRENT")
sys.path.append(os.path.split(aprx.filePath)[0])

# TODO: implement this tool

from Tools.Simulator import FluidSimulation
from Tools.Simulator import GeospatialFlattener

import importlib
FluidSimulation = importlib.reload(FluidSimulation)
GeospatialFlattener = importlib.reload(GeospatialFlattener)

topography = arcpy.GetParameter(0)
epicenter = arcpy.GetParameter(1)
magnitude = arcpy.GetParameter(2)
fault_heading = arcpy.GetParameter(3)
dip_angle = arcpy.GetParameter(4)
slip_angle = arcpy.GetParameter(5)

sim = FluidSimulation.FluidSimulation(topography)
epicenter_point = GeospatialFlattener.parse_point(epicenter)
sim.add_earthquake(
    epicenter_point,
    float(magnitude),
    float(fault_heading),
    float(dip_angle),
    float(slip_angle)
)

fig, ax = plt.subplots()
ax.imshow(sim.base_elevation + sim.water_height)
# yx = self._longlat_to_yx(arcpy.Point(longitude, latitude))
# ax.scatter(yx[1], yx[0], color='red', marker='o', s=25)
plt.show()
