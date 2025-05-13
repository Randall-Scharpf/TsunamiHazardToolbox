import os
import requests

PROJECT_PATH = r"D:\Files\Documents\ArcGIS\Projects\GEOG181C_FinalProject"
GEODB_PATH = os.path.join(PROJECT_PATH, "GEOG181C_FinalProject_arcpy.gdb")
LAB_DATA_PATH = os.path.join(PROJECT_PATH, "LabData")
OUTPUT_PATH = os.path.join(PROJECT_PATH, "output")

NOAA_NGDC_URL_FORMAT = (
    "https://gis.ngdc.noaa.gov/arcgis/rest/services/DEM_mosaics/DEM_all/ImageServer/exportImage?"
    "bbox={left},{top},{right},{bottom}&bboxSR=4326&size={width},{height}&"
    "imageSR=4326&format=tiff&pixelType=F32&interpolation=+RSP_NearestNeighbor&compression=LZ77&"
    "renderingRule={{&quot;rasterFunction&quot;:&quot;none&quot;}}&"
    "mosaicRule={{&quot;where&quot;:&quot;Name='{dataset}'&quot;}}&"
    "f=image"
)

def lat_fmt(num):
    num = round(num)
    if (num >= 0):
        return f"{num}n"
    else:
        return f"{-num}s"

def lon_fmt(num):
    num = round(num)
    if (num >= 0):
        return f"{num}e"
    else:
        return f"{-num}w"

BASE_COLS = 9
BASE_ROWS = 8
dx = 360/BASE_COLS
dy = 89*2/BASE_ROWS
for xi in range(BASE_COLS):
    x = dx * xi - 180
    for yi in range(BASE_ROWS):
        y = dy * yi - 89
        tile_name = f"etopo2022-ice15s_{lon_fmt(x)}-{lon_fmt(x+dx)}_{lat_fmt(y)}-{lat_fmt(y+dy)}" + os.path.extsep + "tiff"
        tile_path = os.path.join(LAB_DATA_PATH, tile_name)
        if (os.path.exists(tile_path) and os.path.getsize(tile_path) > 0):
            print(f"Base tile {tile_name} appears to already be fetched, delete it to fetch a fresh copy.")
            continue
        print(f"Fetching base tile {tile_name}...", end="\t\t")
        url = NOAA_NGDC_URL_FORMAT.format(dataset="ETOPO_2022_v1_15s_surface_elev",left=x,right=x+dx,top=y,bottom=y+dy,width=dx*240,height=dy*240)
        response = requests.get(url)
        tile = open(tile_path, "wb")
        tile.write(response.content)
        tile.close()
        print(f"finished ({BASE_ROWS*xi+yi+1}/{BASE_COLS*BASE_ROWS})")
