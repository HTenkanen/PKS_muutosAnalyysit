import os, sys
import pandas as pd
import geopandas as gpd
import numpy as np

def parseShapefilePaths(topFolder):
    paths = []
    for root, dirs, files in os.walk(topFolder):
        for filename in files:
            if filename.endswith('.shp'):
                paths.append(os.path.join(root,filename))
    return paths

def filterFilesByName(file_path_list, filter_text):
    filtered_files = []
    for file in file_path_list:
        if filter_text in os.path.basename(file):
            filtered_files.append(file)
    return filtered_files

# File paths
dataFolder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"
ykr_grid = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\ShapeFileet\MetropAccess_YKR_grid\MetropAccess_YKR_grid_FinlandZone2.shp"

# List shapefiles
all_shapes = parseShapefilePaths(dataFolder)

# Get files that we are interested in (i.e. including YKR-ID information)
filter_text = "_YKR_join"
shapes = filterFilesByName(all_shapes, filter_text)

for shape in shapes:
    data = gpd.read_file(shape)

    #Group by YKR_id
    grouped = data.groupby('YKR')

    #Empty GeoDataFrame for results
    results = gpd.GeoDataFrame(crs=data.crs)

    i = 0
    for group in grouped:

        # Skip points outside MetropAccess-YKR-grid (i.e. 'YKR' value is 1)
        if not group[0] == 1:
            time = group[1]['min_time']
            meanTime, minTime, maxTime = int(round(time.mean(),0)), int(round(time.min(),0)), int(round(time.max(),0))

            orig_data = group[1][['YKR']].copy()

            # Set new index (or indices)
            orig_data.index = [x+i for x in range(len(orig_data))]

            stats_df = pd.DataFrame(np.array([[meanTime, minTime, maxTime]]), columns=['meanTime', 'minTime', 'maxTime'], index=pd.Index([i]))
            combined_df = pd.concat((orig_data, stats_df), axis=1)
            results = results.append(combined_df)
            i+=1

    # Drop NaN values resulting from grouped items
    results = results.dropna(axis=0, how='any')

    # Join with YKR-Grid
    ykr = gpd.read_file(ykr_grid)
    join = results.merge(results, how='outer', left_on='YKR', right_on='YKR_ID')

    # Generate outputName
    shoppingCenter = os.path.basename(shape).replace("_YKR_join.shp", "_Aggregated_By_YKR_grid.shp")
    outputShape = os.path.join(dataFolder, shoppingCenter)

    join.to_file(outputShape, driver="ESRI Shapefile")




