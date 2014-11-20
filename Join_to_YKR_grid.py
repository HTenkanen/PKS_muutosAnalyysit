__author__ = 'hentenka'
import geopandas as gpd
import sys, os
from rtree import index

def buildRtree(polygon_df):
    idx = index.Index()
    for poly in polygon_df.iterrows():
        idx.insert(poly[0], poly[1]['geometry'].bounds)
    return idx

def querySpatialIndex(point, poly_df, poly_rtree, source_column):
    """Find poly containing the point"""
    point_coords = point['geometry'].coords[:][0]
    for idx_poly in poly_rtree.intersection( point_coords ):
        if poly_df['geometry'][idx_poly:idx_poly+1].values[0].contains(point['geometry']):
            return poly_df[source_column][idx_poly:idx_poly+1].values[0]
    return None

def pointInPolygon(point_df, poly_df, poly_rtree, sourceColumn_in_poly, targetColumn_in_point, fast_search=True):
    """Iterates over points"""
    data = point_df
    data[targetColumn_in_point] = None
    data[targetColumn_in_point] = point_df.apply(querySpatialIndex, axis=1, poly_df=poly_df, poly_rtree=poly_rtree, source_column=sourceColumn_in_poly)
    return data

def parseShapefilePaths(topFolder):
    paths = []
    for root, dirs, files in os.walk(topFolder):
        for filename in files:
            if filename.endswith('.shp'):
                paths.append(os.path.join(root,filename))
    return paths

# Filepaths
YKR_grid = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_FinlandZone2.shp"
pointfolder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"
shapefiles = parseShapefilePaths(pointfolder)

# Read Ykr-grid
ykr = gpd.read_file(YKR_grid)

# Build R-tree spatial index for polygons
rtree = buildRtree(ykr)

# Iterate over point Shapefiles and associate YKR-ID for each point
for pointfile in shapefiles:
    data = gpd.read_file(pointfile)

    # Make spatial join --> find YKR-ID for each point
    joinWithYkr = pointInPolygon(point_df=data, poly_df=ykr, poly_rtree=rtree, sourceColumn_in_poly='YKR_ID', targetColumn_in_point='YKR')

    # Generate outputname
    output = os.path.join(os.path.dirname(pointfile), os.path.basename(pointfile)[:-4] + "_YKR_join.shp")

    # Write outputfile
    joinWithYkr.to_file(output, driver="ESRI Shapefile")


