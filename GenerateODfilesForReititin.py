__author__ = 'hentenka'
import geopandas as gpd

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

print orig84[0:5]
print dest84[0:5]