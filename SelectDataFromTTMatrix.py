# coding=utf-8
__author__ = 'hentenka'
import pandas as pd
import geopandas as gpd
import SelectFiles_tools as sf
import os, sys
from googleplaces import GooglePlaces
from shapely.geometry import Point

# File paths
data_folder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"

# List shape files
all_shapes = sf.parseShapefilePaths(data_folder)

# Filter out unnecessary files
data09_paths = sf.filterFilesByName(all_shapes, "_2009_Aggregated_By_YKR_grid")

# Make a list of origin YKR IDs that will be included in the analyses
data = gpd.read_file(data09_paths[0])
ykr_ids = list(data['YKR_ID'].values)

# Make a list of destination YKR IDs that will be included in the analyses
# ------------------------------------------------------------------------

# Geocode locations of Shopping centers using Google Places
shopping_centers = {'Itis, Helsinki':None, 'Kauppakeskus Jumbo, Vantaa':None, 'Iso Omena, Espoo':None, 'Kampin metroasema, Helsinki':None,
                    'Kauppakeskus Ruoholahti, Helsinki':None, 'Kauppakeskus Myyrmanni, Vantaa':None, 'Sello, Espoo':None}

#Authenticate
apiKey = 'AIzaSyB6TMLFoMNwPAlHQ3p2TBR7NNaY_UrCQ7Q'
gp = GooglePlaces(apiKey)

for center in shopping_centers:
    location = gp.text_search(center)
    coords = location.places[0].geo_location
    shopping_centers[center] = Point(coords['lng'], coords['lat'])

# Create a GeoDataFrame from the centers
coordsys = {u'no_defs': True, u'datum': u'WGS84', u'proj': u'longlat'}
centers = gpd.GeoDataFrame(shopping_centers.items(), columns=['Center', 'geometry'], crs=coordsys, geometry='geometry')

# Change projection to EurefFin
centersEF = centers.to_crs(crs=data.crs)

# Export centers to Shapefile
#centers_shape = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Shopping_Centers_EurefFin.shp"
#centersEF.to_file(centers_shape, driver="ESRI Shapefile")

# Make spatial join to YKR-grid for finding out the YKR ids of shopping centers







