# Import all of the libraries we need to use
import pandas as pd
import azureml.dataprep as dprep
import os as os
import re as re
import collections
import datetime
from azureml.dataprep import value
from azureml.dataprep import col
from azureml.dataprep import Dataflow

# Let's also set up global variables and common functions...
# NOTE - still to figure out how to do this from a single file and import it successfully.
#%%
# Path to the source data
dataPath = "./data"

# Path to the location where the dataprep packags that are created
packagePath = "./packages"

# Name of package file
packageFileSuffix = "_package.dprep"

# A helper function to create full package path
def createFullPackagePath(packageName, stage, qualityFlag):
    thisStagePath = packagePath + '/' + packageName + '/' + stage

    if not os.path.isdir(thisStagePath):
        os.mkdir(thisStagePath)

    return thisStagePath + '/' + packageName + '_' + qualityFlag + packageFileSuffix

# A save package helper function
def savePackage(dataFlowToPackage, packageName, stage, qualityFlag):
    fullPackagePath = createFullPackagePath(packageName, stage, qualityFlag)
    dataFlowToPackage.save(fullPackagePath)
    return fullPackagePath

def saveColumnInventoryForTable(columnInventory, packageName, stage):
    thisStagePath = packagePath + '/' + packageName + '/' + stage

    if not os.path.isdir(thisStagePath):
        os.mkdir(thisStagePath)

    columnInventory.to_csv(thisStagePath + '/' + 'columnInventory_' + stage + '_Out.csv', index = None)

# An open package helper function
def openPackage(packageName, stage, qualityFlag):
    fullPackagePath = createFullPackagePath(packageName, stage, qualityFlag)
    dataFlow = Dataflow.open(fullPackagePath)
    return dataFlow

# A data profiling helper function to capture column metrics in a standard way
def getTableStats(dataProfile, dataName, stage):
    columnStats = pd.DataFrame(columns = [ \
        'DataName', \
        'Stage', \
        'ColumnName', \
        'Type', \
        'Min', \
        'Max', \
        'RowCount', \
        'MissingCount', \
        'NotMissingCount', \
        'ErrorCount', \
        'EmptyCount', \
        'Mean', \
        'ValueCount'])
    columnStats = pd.DataFrame.to_string(columns=['Min', 'Max'])
    for item in dataProfile.columns.values():
        
        if item.value_counts == None:
            valueCount = None
        else:
            valueCount = len(item.value_counts)

        columnStats = columnStats.append({'DataName' : dataName, \
        'Stage' : stage, \
        'ColumnName' : item.column_name, \
        'Type' : item.type, \
        'Min' : item.min, \
        'Max' : item.max, \
        'RowCount' : item.count, \
        'MissingCount' : item.missing_count, \
        'NotMissingCount' : item.not_missing_count, \
        'ErrorCount' : item.error_count, \
        'EmptyCount' : item.empty_count, \
        'Mean' : item.mean, \
        'ValueCount' : valueCount}, ignore_index = True)
    
    columnStats.insert(2, 'DateTime', datetime.datetime.now())
    
    return columnStats

# An open package helper function with full path as parameter
def openPackageFromFullPath(fullPath):
    dataFlow = Dataflow.open(fullPath)
    return dataFlow
