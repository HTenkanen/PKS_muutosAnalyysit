__author__ = 'hentenka'
import geopandas as gpd
import pandas as pd
import os, sys
import SelectFiles_tools as sf
import numpy as np


def combineResults(input_file_list, outputFileName):

    # Read files in
    for file in input_file_list:
        if "2017" in file:
            data17 = gpd.read_file(file)
        elif "2013" in file:
            data13 = gpd.read_file(file)
        elif "2009" in file:
            data09 = gpd.read_file(file)

    # Drop duplicate geometries
    data13 = data13.drop(labels='geometry', axis=1)
    data17 = data17.drop(labels='geometry', axis=1)

    # Join datasets
    join09_13 = data09.merge(data13, how='inner', left_on ='YKR_ID', right_on='from_id')
    join09_13.drop(labels=['from_id', 'to_id'], inplace=True, axis=1)
    full_join = join09_13.merge(data17, how='inner', left_on='YKR_ID', right_on='from_id')


    # Rename columns
    full_join.columns = [u'Asuk09', u'YKR_ID', u'geometry', u'maxT09', u'meanT09', u'minT09', u'Asuk13', u'Car_D13', u'Car_T13', u'PT_D13', u'PT_T13', u'PT_ToT13', u'PT_D17', u'PT_T17', u'PT_ToT17', u'from_id', u'Asuk17', u'to_id']

    # Choose and reorder
    join = full_join[[ u'from_id', u'to_id', u'maxT09', u'meanT09', u'minT09', u'Asuk09', u'PT_T13', u'PT_ToT13', u'PT_D13', u'Car_T13', u'Car_D13', u'Asuk13', u'PT_T17', u'PT_ToT17', u'PT_D17', u'Asuk17', u'geometry']]

    # Set -1 values to NaN
    join = join.replace(to_replace={'PT_T13': {-1: np.nan}})

    # Drop NaNs
    join = join.dropna()

    # Calculate accessibility differences
    join['Dif09_13'] = None
    join['Dif09_17'] = None
    join['Dif13_17'] = None
    join['Dif09_13'] = join['meanT09'] - join['PT_T13']
    join['Dif09_17'] = join['meanT09'] - join['PT_T17']
    join['Dif13_17'] = join['PT_T13'] - join['PT_T17']

    # Save output
    folder = os.path.dirname(input_file_list[0])
    outfile = os.path.join(folder, outputFileName)

    join.to_file(outfile, driver="ESRI Shapefile")

    print outfile


# File paths
data_folder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\RECALCULATES"

shapes = sf.parseShapefilePaths(data_folder)

omena = sf.filterFilesByName(shapes, filter_text='Omena')
itis = sf.filterFilesByName(shapes, filter_text='It')
sello = sf.filterFilesByName(shapes, filter_text='Sello')
kamppi = sf.filterFilesByName(shapes, filter_text='Kamp')
myyrmanni = sf.filterFilesByName(shapes, filter_text='Myyrman')
ruoho = sf.filterFilesByName(shapes, filter_text='Ruoho')
jumbo = sf.filterFilesByName(shapes, filter_text='Jumbo')


iter_list = [[omena, "Iso_Omena_Accessibility_ChangeAnalysis_years_09_13_17.shp"], [itis, "Itis_Accessibility_ChangeAnalysis_years_09_13_17.shp"],
             [sello, "Sello_Accessibility_ChangeAnalysis_years_09_13_17.shp"],[kamppi, "Kamppi_Accessibility_ChangeAnalysis_years_09_13_17.shp"],
             [myyrmanni, "Myyrmanni_Accessibility_ChangeAnalysis_years_09_13_17.shp"], [ruoho, "Ruoholahti_Accessibility_ChangeAnalysis_years_09_13_17.shp"],
             [jumbo, "Jumbo_Accessibility_ChangeAnalysis_years_09_13_17.shp"]]

# Iterate over files and combine results
for center in iter_list:
    combineResults(center[0], center[1])
