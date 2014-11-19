# -*- coding: cp1252 -*-
import pandas as pd
import geopandas as gpd
import os, sys
from shapely.geometry import Point

def coordToPoint(row, lat, lon):
    return Point(row[lon], row[lat])

#Analyse travel times to following shopping centers
ShoppingCenters = ["Myyrmanni", "Jumbo", "Sello", "Iso-Omena", "Kauppakeskus_Ruoholahti", "Kampin_keskus", "Itäkeskus"]

# File paths
data_top_folder = r'C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset'
output_folder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"
analysisTime = "_arki_12-13"
data_folders = []
data_files = []

for center in ShoppingCenters:
    data_folders.append(os.path.join(data_top_folder, "%s%s" % (center, analysisTime)))

# Create full paths to files
for folder in data_folders:
    for root, dirs, files in os.walk(folder):
        individual_center = []
        for filename in files:
            if filename.startswith("timedata_"):
                individual_center.append(os.path.join(root, filename))
        data_files.append(individual_center)


# Get Coordsys
coorsys_file = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\time_to_Jumbo_2009.shp"
c = gpd.read_file(coorsys_file)
coordsys = c.crs

# Find fastest route between Origin and Destination (Shopping center)
for ind_center in data_files:

    # Read data in as pandas DataFrame
    data1 = pd.read_csv(ind_center[0], sep=',', header=None, names=['id', 'x', 'y', 'PT_total_time1'])
    data2 = pd.read_csv(ind_center[1], sep=',', header=None, names=['id', 'x', 'y', 'PT_total_time2'])
    data3 = pd.read_csv(ind_center[2], sep=',', header=None, names=['id', 'x', 'y', 'PT_total_time3'])

    # Join datasets by 'id'
    join1 = pd.merge(data1, data2, how='outer', left_on = 'id', right_on='id')
    join2 = join1.merge(data3, how='outer', left_on = 'id', right_on='id')
    data = join2[['id', 'x', 'y', 'PT_total_time1', 'PT_total_time2', 'PT_total_time3']].copy()

    # Find shortest time
    data['min_time'] = data.loc[:, ['PT_total_time1', 'PT_total_time2', 'PT_total_time3']].min(axis=1)

    # Create geometries from coordinates
    data['geometry'] = data.apply(coordToPoint, axis=1, lat='y', lon='x')

    # Generate output filepath
    filename = os.path.basename(os.path.dirname(ind_center[0])).replace(analysisTime, '_travelTimes_2009.shp')
    outpath = os.path.join(output_folder, filename)

    # Make sure that there are no ääkkösiä in filepaths
    outpath = outpath.replace('ä', 'a')
    outpath = outpath.replace('ö', 'o')

    # Export to shapefile
    geo = gpd.GeoDataFrame(data, geometry='geometry', crs=coordsys)
    geo.to_file(outpath, driver="ESRI Shapefile")

