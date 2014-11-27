__author__ = 'hentenka'
import pandas as pd
import os, sys
import numpy as np
import geopandas as gpd

# Paths
#dataFolder = r"C:\HY-Data\HENTENKA\MetropAccess-Reititin_1.2\MetropAccess-Reititin\bin\Results"
dataFolder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\Results2017"
population = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\YKR_asukkaat2013.shp"
outputF = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"

paths = []

# Parse results text files
for root, dirs, files in os.walk(dataFolder):
    for filename in files:
        if filename.endswith('results.txt'):
            paths.append(os.path.join(root, filename))

full_data = pd.DataFrame()

# Collect all data to single dataframe
for result in paths:
    data = pd.read_csv(result, sep=';')

    # Select columns
    data = data[['from_id', 'to_id', 'total_route_time', 'route_distance']]
    full_data = full_data.append(data)

# Change -99999.99 to NaN
full_data = full_data.replace(to_replace={'total_route_time': {-99999.99: np.nan}})

# Round distance values to full meters
full_data['PT_dist'] = full_data.apply(lambda x: np.round(x['route_distance']), axis=1)
full_data = full_data[['from_id', 'to_id', 'total_route_time','PT_dist']]
full_data.columns = ['from_id', 'to_id', 'PT_total_t','PT_dist']

# Drop NaNs
full_data = full_data.dropna(axis=0, subset=['PT_total_t'])

# Group by destination
grouped = full_data.groupby('to_id')

# Read ykr-grid and population stats
pop = gpd.read_file(population)

# Create output names for the results
outputNames = {5878070: 'Jumbo_2017.shp', 5902043: 'Myyrmanni_2017.shp', 5936704: 'Sello_2017.shp', 5944003: 'Itis_2017.shp', 5975373: 'Kamppi_2017.shp', 5978593: 'Iso_Omena_2017.shp', 5980260: 'Ruoholahti_2017.shp'}

for id, group in grouped:

    # Join Reititin results with YKR-grid (incl. population stats)
    join = pop.merge(group, how='inner', left_on='YKR_ID', right_on='from_id')

    # Choose columns
    join = join[['from_id', 'to_id', 'PT_total_t','PT_dist', 'Sum_ASYHT', 'geometry']]
    join.columns = ['from_id', 'to_id', 'PTtotT_17','PT_dist17', 'Asuk13', 'geometry']

    outPath = os.path.join(outputF, outputNames[id])
    join.to_file(outPath, driver="ESRI Shapefile")

    break



