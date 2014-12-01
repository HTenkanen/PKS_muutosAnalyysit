__author__ = 'hentenka'
import geopandas as gpd
import pandas as pd
import sys
from shapely.ops import cascaded_union, unary_union
import spatial_tools as st
import numpy as np


def mergePolys(df, attributeDataDictionary, dictionary_row_index):

    pols = []
    for idx, row in df.iterrows():
        pols.append(row['geometry'])
    merge = unary_union(pols)
    valuesToList = [item[dictionary_row_index] for item in attributeDataDictionary.values()]
    contents = [[merge] + valuesToList]
    headers = ['geometry'] + attributeDataDictionary.keys()

    data = gpd.GeoDataFrame(contents, columns=headers, geometry='geometry')
    return data

def calculatePopEstimates(row, ykr_as, pop2013, pop2017, growth, ykr_count, target):
    if row[ykr_as] > row[pop2013]:
        if row[ykr_count] > 0:
            estim_pop = row[pop2017]/row[ykr_count]
            if estim_pop > row[ykr_as]:
                return int(np.round(estim_pop, 0))
            else:
                return int(row[ykr_as])
        else:
            return int(row[ykr_as])
    elif int(row[ykr_as]) == 0:
        return 0

    elif int(row[ykr_as]) == 1:
        if row[ykr_count] > 0:
            estim_pop = row[pop2017]/row[ykr_count]
            if estim_pop > row[ykr_as]:
                return int(np.round(estim_pop, 0))
            else:
                return int(row[ykr_as])
    else:
        try:
            value = row[ykr_as]*row[growth]
            return int(np.round(value, 0))
        except:
            return np.nan


# File paths
pop_estimates = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\VaestoEnnusteet\PKS_Vaestoennusteet2012_2021_Cleaned.csv"   # Source: http://www.hri.fi/fi/dataset/paakaupunkiseudun-vaestoennuste-2012-2021
pks_sub_regions = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Seutukartta\PKS_pienalueet.shp"  # Source: http://www.hri.fi/fi/dataset/seutukartta
output = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\VaestoEnnusteet\PKS_VaestoEnnusteet_2017.shp"
ykr_grid = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\YKR_asukkaat2013.shp"

pop = pd.read_csv(pop_estimates, sep=';')
pks = gpd.read_file(pks_sub_regions)
pks_coordsys = pks.crs

# Fill pop.Mapcode to exact 10 digits long (enabling join with pks)
pop['RegionCode'] = pop.apply(lambda x: str(x['Mapcode']).zfill(10), axis=1)

# Merge polygons of Kauniainen to a single polygon
kauniainen = pks.loc[pks['KUNTA'] == '235']
selectRow = kauniainen[[u'KOKOTUN', u'KUNTA', u'Mtryhm', u'NIMI_ISO', u'Nimi', u'PIEN', u'SUUR', u'TILA']][0:1]
dict = selectRow.to_dict()
row_index = selectRow.index.values[0]
merged_kauniainen = mergePolys(kauniainen, dict, row_index)

# Update KOKOTUN value for Kauniainen
merged_kauniainen['KOKOTUN'] = '2351000000'

# Remove multiple Kauniainen polygons from original pks data
pks_subset = pks.loc[pks['KUNTA'] != '235']

# Add merged Kauniainen to pks_subset
pks_mod = pks_subset.append(merged_kauniainen)

# Join
join = pks_mod.merge(pop, how='inner', left_on='KOKOTUN', right_on='RegionCode')
selection = join[[u'KOKOTUN', u'RegionCode', u'Nimi', u'geometry', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']]
selection.columns = [u'KOKOTUN', u'RegionCode', u'Nimi', u'geometry', 'Pop2000', 'Pop2001', 'Pop2002', 'Pop2003', 'Pop2004', 'Pop2005', 'Pop2006', 'Pop2007', 'Pop2008', 'Pop2009', 'Pop2010', 'Pop2011', 'Pop2012', 'Pop2013', 'Pop2014', 'Pop2015', 'Pop2016', 'Pop2017', 'Pop2018', 'Pop2019', 'Pop2020', 'Pop2021']

# Change . to 0
selection = selection.replace('.', 1)

# Change datatype to integer
selection[['Pop2013', 'Pop2017']] = selection[['Pop2013', 'Pop2017']].astype(int)

# Calculate population change (percentage) between years 2013 and 2017
selection['Pop13vs17'] = selection['Pop2017'] / selection['Pop2013']

pop_data = gpd.GeoDataFrame(selection, geometry='geometry', crs=pks_coordsys)

# Read Population-YKR-2013
ykr_poly = gpd.read_file(ykr_grid)
ykr_coordsys = ykr_poly.crs

# Calculate poly centroids from ykr_poly
ykr_poly['centroid'] = None
spatial = st.SpatialTools()
ykr_poly = ykr_poly.apply(spatial.calculateCentroid, axis=1, source_column='geometry', target_column='centroid')

# Determine point as geometry for the dataframe
ykr_poly.columns = [u'Count_', u'Sum_ASYHT', u'YKR_ID', u'polygon', u'x', u'y', u'geometry']
ykr_point = ykr_poly  # Rename variable to clarify

# Ensure that datasets are in the same coordinate system
pop_data_reproj = pop_data.to_crs(crs=ykr_coordsys)

# Create RTree spatial index for population data polygons
idx = spatial.buildRtree(pop_data_reproj)

# Determine for each ykr_grip (point) the Region Code of pop_estimate dataset
join_popEstim_ykr = spatial.pointInPolygon(point_df=ykr_point, poly_df=pop_data_reproj, poly_rtree=idx, sourceColumn_in_poly='RegionCode', targetColumn_in_point='RegionCod')

# Select columns from population estimate dataset to the join
pop_select = pop_data[[u'RegionCode', u'Nimi', u'Pop2000', u'Pop2001', u'Pop2002', u'Pop2003', u'Pop2004', u'Pop2005', u'Pop2006', u'Pop2007', u'Pop2008', u'Pop2009', u'Pop2010', u'Pop2011', u'Pop2012', u'Pop2013', u'Pop2014', u'Pop2015', u'Pop2016', u'Pop2017', u'Pop2018', u'Pop2019', u'Pop2020', u'Pop2021', u'Pop13vs17']]

# Join the datasets based on RegionCode
ykr_pop_estim = join_popEstim_ykr.merge(pop_select, left_on='RegionCod', right_on='RegionCode', how='inner')

# Select cells that did not have population in 2013
new_areas = ykr_pop_estim.loc[ykr_pop_estim['Pop2013'] == 1]

# Group by RegionCode
grouped = new_areas.groupby('RegionCode')

# Create empty data frame
ykr_count = pd.DataFrame()

# Iterate over groups and calculate how many YKR cells are within new_areas
for index, group in grouped:
    code = group['RegionCode'].values[0]
    count = len(group)
    ykr_count = ykr_count.append([[code,count]])

ykr_count.reset_index(inplace=True, drop=True)
ykr_count.columns = ['RegCode', 'Ykr_count']

# Join ykr_counts to data
ykr_pop_estim = ykr_pop_estim.merge(ykr_count, how='outer', left_on='RegionCode', right_on='RegCode')

# Fill NaN to -1
ykr_pop_estim.fillna(value=-1, inplace=True)

# Calculate population estimates for year 2017
ykr_pop_estim['pop_esti17'] = None
ykr_pop_estim['pop_esti17'] = ykr_pop_estim.apply(calculatePopEstimates, axis=1, ykr_as='Sum_ASYHT', pop2013='Pop2013', pop2017='Pop2017', growth='Pop13vs17', target='pop_estim17', ykr_count='Ykr_count')

# Set geometry back to Polygons
ykr_pop_estim.columns = [u'Count_', u'Sum_ASYHT', u'YKR_ID', u'geometry', u'x', u'y', u'point', u'RegionCod', u'RegionCode', u'Nimi', u'Pop2000', u'Pop2001', u'Pop2002', u'Pop2003', u'Pop2004', u'Pop2005', u'Pop2006', u'Pop2007', u'Pop2008', u'Pop2009', u'Pop2010', u'Pop2011', u'Pop2012', u'Pop2013', u'Pop2014', u'Pop2015', u'Pop2016', u'Pop2017', u'Pop2018', u'Pop2019', u'Pop2020', u'Pop2021', u'Pop13vs17', u'RegCode', u'Ykr_count', u'pop_esti17']

# Drop point and RegionCod columns
ykr_pop_estim = ykr_pop_estim.drop(labels=['point', 'RegionCod', 'RegCode'], axis=1)

# Create GeoDataFrame
geo = gpd.GeoDataFrame(ykr_pop_estim, geometry='geometry', crs=ykr_coordsys)

geo.to_file(output, driver="ESRI Shapefile")
