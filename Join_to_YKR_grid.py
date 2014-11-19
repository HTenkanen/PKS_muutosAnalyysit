__author__ = 'hentenka'
import geopandas as gpd
import pandas as pd
import sys
from rtree import index

idx = index.Index()

def iterateAllPolys(polygon, point, source_column):
    """Iterates over polygons"""
    if polygon['geometry'].contains(point['geometry']):
        print "Found"
        return polygon[source_column]

def iteratePoints(point, poly_df, source_column, fast_search):
    """Iterates over points"""
    if not fast_search:
        return poly_df.apply(iterateAllPolys, axis=1, point=point, source_column=source_column)
    else:
        for poly in poly_df.iterrows():
            if poly[1]['geometry'].contains(point['geometry']):
               return poly[1][source_column]

def pointInPolygon(point_df, poly_df, sourceColumn_in_poly, targetColumn_in_point, fast_search=True):
    """Iterates over points"""
    data = point_df[targetColumn_in_point] = point_df.apply(iteratePoints, axis=1, poly_df=poly_df, source_column=sourceColumn_in_poly, fast_search=fast_search)
    return data

# Filepaths
YKR_grid = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_FinlandZone2.shp"
itis_fp = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Itakeskus_travelTimes_2009.shp"

ykr = gpd.read_file(YKR_grid)
itis = gpd.read_file(itis_fp)

result = pointInPolygon(point_df=itis, poly_df=ykr, sourceColumn_in_poly='YKR_ID', targetColumn_in_point='YKR', fast_search=True)

#for row in ykr.iterrows():

#    if row[1]['geometry'].contains(r1['geometry'].values[0]):
#        print "Found!"
#        print row[1]['YKR_ID']
#        break

