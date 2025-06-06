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
sim.add_timestep(60)

point = GeospatialFlattener.parse_point(epicenter)

raise ValueError((sim.get_elevation(point), sim.get_wave_elevation(point)))