__author__ = 'hentenka'
import geopandas as gpd
import pandas as pd
import numpy as np
import sys, os

def pointToCoords(row, pointCol, xCol, yCol):
    row[xCol] = row[pointCol].x
    row[yCol] = row[pointCol].y
    return row

def polyCentroidToCoords(row, polyCol, xCol, yCol):
    row[xCol] = row[polyCol].centroid.x
    row[yCol] = row[polyCol].centroid.y
    return row

# File paths
origPath = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Itis_travelTimes_2013.shp"
destPath = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Shopping_Centers_EurefFin.shp"
origOut = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\PKS_MuutosAnalyysit_OriginPoints_WGS84.txt"
destOut = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\PKS_MuutosAnalyysit_DestinationPoints_WGS84.txt"


# Read files
origins = gpd.read_file(origPath)
destins = gpd.read_file(destPath)

# Convert to WGS84 projection
orig84 = origins.to_crs(epsg=4326)
dest84 = destins.to_crs(epsg=4326)

# Create wkt-coordinate columns
orig84['x_wgs'] = None
orig84['y_wgs'] = None
orig84 = orig84.apply(polyCentroidToCoords, axis=1, polyCol='geometry', xCol='x_wgs', yCol='y_wgs')

dest84['x_wgs'] = None
dest84['y_wgs'] = None
dest84 = dest84.apply(pointToCoords, axis=1, pointCol='geometry', xCol='x_wgs', yCol='y_wgs')

# Choose data to output
orig84 = orig84[['from_id', 'x_wgs', 'y_wgs']]
dest84 = dest84[['YKR_ID', 'x_wgs', 'y_wgs']]

# Rename columns
orig84.columns = ['id', 'x_wgs', 'y_wgs']
dest84.columns = ['id', 'x_wgs', 'y_wgs']

# Save to text files
orig84.to_csv(origOut, sep=';', index=False)
dest84.to_csv(destOut, sep=';', index=False)


data = pd.read_csv(origOut, sep=';')
outFolder = "C:\HY-Data\HENTENKA\KOODIT\PKS_muutosAnalyysit\ReititinFiles\OriginBlocks"
filename = "_PKS_MuutosAnalyysit_OriginPoints_WGS84.txt"


block_size = 250
row_count = float(len(data))
iterations = int(row_count / block_size + 1)

i = 0
name_idx = 0
for block in xrange(iterations):
    try:
        block_data = data[i:i+block_size]
    except:
        block_data = data[i:]

    outName = os.path.join(outFolder, "%s%s" % (name_idx, filename))
    block_data.to_csv(outName, sep=';', index=False)
    i+=block_size
    name_idx+=1


# Create Reititin commands

file_paths = []
cmd_file = "run_batch_Reititin_PKS_muutosAnalyysit.txt"
batch_folder = r"C:\HY-Data\HENTENKA\KOODIT\PKS_muutosAnalyysit\ReititinFiles"
f = open(os.path.join(batch_folder, cmd_file), 'w')
i = 0
command1 = "route.bat"
command3 = "PKS_MuutosAnalyysit_DestinationPoints_WGS84.txt --conf=confMassaAjo.json --extra=newMetroWithFeederLines.shp --base-path=C:\HY-Data\HENTENKA\MetropAccess_Reititin_KalkatiJemma\data_20141114"


for root, dirs, files in os.walk(outFolder):
    for filename in files:
        command2 = "--out-avg=%s_PKS_muutosAnalyysit2017_results.txt --out-kml=%s_PKS_muutosAnalyysit2017_results.kml" % (i, i)

        out_command = "%s %s %s %s\n" % (command1, filename, command2, command3)

        i+=1
        print out_command
        f.write(out_command)

f.close()



