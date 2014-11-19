__author__ = 'hentenka'
import geopandas as gpd
import pandas as pd

# Filepaths
YKR_grid = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_FinlandZone2.shp"

ykr = gpd.read_file(YKR_grid)
print ykr[0:3]
