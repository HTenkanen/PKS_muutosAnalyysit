# coding=utf-8
__author__ = 'hentenka'
import geopandas as gpd
import SelectFiles_tools as sf
import os, sys
from googleplaces import GooglePlaces
from shapely.geometry import Point
import spatial_tools as st

# File paths
data_folder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin"
data_path = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Kampin_keskus_travelTimes_2009_Aggregated_By_YKR_grid.shp"
population = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\YKR_asukkaat2013.shp"

# Make a list of origin YKR IDs that will be included in the analyses
data = gpd.read_file(data_path)
pop = gpd.read_file(population)
orig_ykr_ids = list(data['YKR_ID'].values)

# Make a list of destination YKR IDs that will be included in the analyses
# ------------------------------------------------------------------------

# Geocode locations of Shopping centers using Google Places (Note! Using googleplaces.text_search uses 10 times more quota!)

shopping_centers = {'Itis, Helsinki':None, 'Kauppakeskus Jumbo, Vantaa':None, 'Iso Omena, Espoo':None, 'Kauppakeskus Kamppi, Helsinki':None,
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

# Build R-tree spatial index for polygons
rtree = st.buildRtree(data)

# Make spatial join to YKR-grid for finding out the YKR ids of shopping centers
spatial_join = st.pointInPolygon(point_df=centersEF, poly_df=data, poly_rtree=rtree, sourceColumn_in_poly='YKR_ID', targetColumn_in_point='YKR_ID')

# Generate proper name for shopping centers
spatial_join['name'] = spatial_join['Center'].str.split(',').str.get(0).str.replace('Kauppakeskus', '').str.replace(' ', '')

# Export centers to Shapefile
centers_shape = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Shopping_Centers_EurefFin.shp"
spatial_join.to_file(centers_shape, driver="ESRI Shapefile")

spatial_join = gpd.read_file("C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\Shopping_Centers_EurefFin.shp")

# List all travel time matrix files
ttm_folder = r"C:\HY-Data\HENTENKA\Python\MassaAjoNiputus\MetropAccess-matka-aikamatriisi_Ajot_2014_04\MetropAccess-matka-aikamatriisi_TOTAL_FixedInternalCells"
ttm_files = sf.listFiles(ttm_folder)

# Create Travel Time YKR-grid Shapefiles to shopping centers
for destination in spatial_join.iterrows():
    matrix_file = sf.selectFilesQuery(ttm_files, [destination[1]['YKR_ID']])

    # Search chosen origin YKR-IDs within the selected files
    selection = sf.selectIdsQuery(matrix_file, orig_ykr_ids, searchColumn='from_id', sep=';')

    # Join with YKR_grid
    join = data.merge(selection, how='inner', left_on='YKR_ID', right_on='from_id')

    # Choose columns
    join = join[['from_id', 'to_id', 'PT_total_time', 'Car_time']]

    # Join with population dataset
    pop_join = join.merge(pop, how='inner', left_on='from_id', right_on='YKR_ID')

    # Choose columns
    pop_join = pop_join[['from_id', 'to_id', 'PT_total_time', 'Car_time', 'Sum_ASYHT', 'geometry']]

    # Rename columns
    pop_join.columns = ['from_id', 'to_id', 'PT_tot_t', 'Car_time', 'Asuk13', 'geometry']

    # Create GeoDataFrame
    geo = gpd.GeoDataFrame(pop_join, geometry='geometry', crs=data.crs)

    # Generate filepath
    outpath = os.path.join(data_folder, destination[1]['name']+ "_travelTimes_2013.shp")

    # Write Shapefile
    geo.to_file(outpath, driver="ESRI Shapefile")
