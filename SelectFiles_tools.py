__author__ = 'hentenka'

import os, sys, random, shutil
import pandas as pd

def listFiles(topPath):
    ''' Creates a list from Travel Time Matrix file paths that are found from the directory and sub-folders of "topPath" '''
    f = []
    for root, dirs, files in os.walk(topPath):
        for filename in files:
            if filename.startswith('time_to_'):
                f.append(os.path.join(root, filename))
    return f

def selectFilesQuery(inputFilesList,inputIDs):
    ''' Searches files based on inputIDs (YKR-ID) from the "inputFilesList" '''
    selected = []
    for id in inputIDs:
        q = 'time_to_' + str(id) + '.txt'
        for file in inputFilesList:
            basename = os.path.basename(file)
            if q in basename:
                selected.append(file)
                break
    return selected

def selectIdsQuery(inputFilesList,searchIDs,searchColumn, sep):
    ''' Searches YKR-IDs from files based on inputIDs (YKR-ID) from the "inputFilesList" and returns a pandas DataFrame from the results '''
    selectedData = pd.DataFrame()
    for file in inputFilesList:
        data = pd.read_csv(file, sep=sep)
        selection = data[data[searchColumn].isin(searchIDs)]
        selectedData = selectedData.append(selection)
    return selectedData

def selectRandom(inputList, sampleSize):
    '''Creates a random selection of files with chosen sample size'''
    return random.sample(inputList, sampleSize)

def copyFiles(inputFilesList, destinationFolder):
    '''Copies files to a chosen destination folder'''

    #If folder does not exist, create one.
    if not os.path.isdir(destinationFolder):
        os.mkdir(destinationFolder)

    for file in inputFilesList:
        shutil.copy2(file, destinationFolder)

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

def main():

    ##################
    #Examples of usage
    ##################

    #Determine file paths
    #--------------------

    inputFolder = r"...\MetropAccess-matka-aikamatriisi_TOTAL"
    outputFolder = r"...\Test"

    #-----------------------------------------------------------------------------------
    #Create a random selection from files and save those to specified location on a disk
    #-----------------------------------------------------------------------------------

    #List all Matrix files within folders
    files = listFiles(inputFolder)

    #Create random selection with chosen sample size
    randFiles = selectRandom(files, 600)

    #Copy randomly selected files to a directory
    copyFiles(randFiles, outputFolder)

    #--------------------------------------------------------------------------------------
    #Select specified files based on YKR-IDs and save those to specified location on a disk
    #--------------------------------------------------------------------------------------

    #Create a list of YKR-IDs that you want to pick
    YKR_ids = [5894644,5970404] #An example

    #Select files based on list of YKR-IDs
    selectedFiles = selectFilesQuery(files, YKR_ids)

    #Copy selected files to a directory
    copyFiles(randFiles, outputFolder)

    #-----------------------------------------------------------------------------------------------------------------
    #Search individual origin YKR-IDs to a selected destination YKR-IDs and save those to a disk in a single text-file
    #-----------------------------------------------------------------------------------------------------------------

    #Determine origin YKR-IDs and destination YKR-IDs
    origIDs = [5889215,5890939,5890963,5918561]
    destIDs = [5965417, 5991522]

    #Select files to chosen destinations
    destFiles = selectFilesQuery(files, destIDs)

    #Search chosen origin YKR-IDs within the selected files
    selection = selectIdsQuery(destFiles, origIDs, searchColumn='from_id', sep=';')

    #Save selection to disk
    out = r"...\Travel_times_from_chosen_originIDs_to_selected_destinationIDs.txt"
    selection.to_csv(out, sep=';', index=False)

if __name__ == '__main__':
    main()
