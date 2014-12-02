import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import SelectFiles_tools as sf
import numpy as np
import os

def createTravelTimeScale(upper_limit_in_minutes):
    data = pd.DataFrame()
    for time in xrange(int(upper_limit_in_minutes)):
        data = data.append([time])
    data.columns = ['Time']
    data.reset_index(inplace=True, drop=True)
    return data

def associatePopulationToMinutes(data_df, travel_mode, population_column):
    time_groups = data_df.groupby(travel_mode)
    reached_pop = pd.DataFrame()
    for idx, time in time_groups:
        population = int(time[population_column].sum())
        time = int(idx)
        reached_pop = reached_pop.append([[time, population]])
    reached_pop.columns = ['Time', 'Population']
    reached_pop.reset_index(inplace=True, drop=True)
    return reached_pop

def accessiblePopulationWithinTime(time_df, data_df, travel_mode, population_column):
    accessible_population = associatePopulationToMinutes(data_df, travel_mode, population_column)
    join = time_df.merge(accessible_population, left_on='Time', right_on='Time', how='outer')
    join = join.fillna(0)
    if travel_mode == 'PT_T17' and population_column == 'Asuk13':
        travel_mode = 'PT_T17_base'
    columnName = "CumPop_%s" % travel_mode
    join[columnName] = join.Population.cumsum(skipna=True)
    return join


def plotAccessiblePopulation(df, columns_list, max_time, name, outputFolder):
    plt.clf()
    fig, ax = plt.subplots(1)
    for column in columns_list:
        label = "_".join(column[1].split('_')[1:])
        if label == 'PT_T13':
            label = "2013"
        elif label == 'PT_T17':
            label = "2017"
        elif label == 'PT_T17_base':
            label = "2017 - Vaestoennusteeton"
        else:
            label = "2009"
        if label == "2017 - Vaestoennusteeton":
            ax.plot(df[column[0]].values, df[column[1]].values, lw=1.5, label=label, color='grey', ls='--')
        else:
            ax.plot(df[column[0]].values, df[column[1]].values, lw=1.5, label=label)


    # Adjust x and y-ticks
    max_time=170
    ax.xaxis.set_ticks(np.arange(0,max_time,15))
    ax.yaxis.set_ticks(np.arange(0,1200000, 100000))

    # Set grid lines
    gridlines = ax.get_xgridlines()
    gridlines.extend( ax.get_ygridlines() )

    for line in gridlines:
                line.set_linewidth(.28)
                line.set_linestyle('dotted')
    ax.grid(True)

    # Set labels
    ax.set_xlabel("Aika (minuuttia)", fontsize=12,labelpad=3.5)
    ax.set_ylabel("Saavutetut asukkaat", fontsize=12,labelpad=3.5)

    # Set legend
    ax.legend(loc='lower right')

    # Set title
    plt.title("Kauppakeskus %s - Joukkoliikenteella saavutetut asukkaat vuosina 2009, 2013 ja 2017" % name, fontsize=13)

    # Resize
    fig.set_size_inches(11.5, 6.35) #(Width, Height)

    # Save figure
    outputPath = os.path.join(outputFolder, name+".png")
    plt.savefig(outputPath, dpi=500)  #, bbox_inches='tight')
    plt.close()


# File paths
data_folder = r"C:\HY-Data\HENTENKA\PKS_saavutettavuusVertailut\Kauppakeskukset\NopeimmatAjatKauppakeskuksiin\RECALCULATES"
shapes = sf.parseShapefilePaths(data_folder)
files = sf.filterFilesByName(shapes, "Accessibility_Change")

for fp in files:
    data = gpd.read_file(fp)

    max_travel_time = data[['meanT09','PT_T13', 'PT_T17']].max().values.max()
    ttm_frame = createTravelTimeScale(max_travel_time)

    # Calculate cumulative populations for different years
    access_pop_PT09 = accessiblePopulationWithinTime(time_df=ttm_frame, data_df=data, travel_mode='meanT09', population_column='Asuk09')
    access_pop_PT13 = accessiblePopulationWithinTime(time_df=ttm_frame, data_df=data, travel_mode='PT_T13', population_column='Asuk13')
    access_pop_PT17 = accessiblePopulationWithinTime(time_df=ttm_frame, data_df=data, travel_mode='PT_T17', population_column='Asuk17')
    access_baseline13 = accessiblePopulationWithinTime(time_df=ttm_frame, data_df=data, travel_mode='PT_T17', population_column='Asuk13')

    # Drop population columns
    access_pop_PT09.drop(labels='Population', inplace=True, axis=1)
    access_pop_PT13.drop(labels='Population', inplace=True, axis=1)
    access_pop_PT17.drop(labels='Population', inplace=True, axis=1)
    access_baseline13.drop(labels='Population', inplace=True, axis=1)

    # Join datasets together
    join_pop = access_pop_PT09.merge(access_pop_PT13, left_on='Time', right_on='Time', how='inner')
    join_pop = join_pop.merge(access_pop_PT17, left_on='Time', right_on='Time', how='inner')
    join_pop = join_pop.merge(access_baseline13, left_on='Time', right_on='Time', how='inner')

    # Generate name
    name = os.path.basename(fp).split('_')[0]
    if name == 'Iso':
        name = 'Iso-Omena'

    # Visualize accessibility (location based accessibility)
    plotAccessiblePopulation(df=join_pop, columns_list=[['Time', 'CumPop_meanT09'], ['Time', 'CumPop_PT_T13'], ['Time', 'CumPop_PT_T17'], ['Time', 'CumPop_PT_T17_base']], max_time=max_travel_time, name=name, outputFolder=data_folder)


