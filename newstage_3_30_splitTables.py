#%% [markdown]
# # Stage: Split Tables
# Purpose of this stage is to enable a table to split into mutiple tables based on the values in a single identified column:
# - The range of values in the identified column are identified;
# - A filter is applied to the source table based on each of the values;
# - A new table is created based with naming convention of source table + column used for split + value.

#%%
#%%
# Import all of the libraries we need to use...
import pandas as pd
import azureml.dataprep as dprep
import os as os
import re as re
import collections
from azureml.dataprep import value, ReplacementsValue
from azureml.dataprep import col
from azureml.dataprep import Dataflow
from commonDataFlowProcessingLoop import dataFlowProcessingLoop
from commonPackageHandling import saveDataFlowPackage, openDataFlowPackage
from commonInventoryCreation import getColumnStats, getDataFlowStats

# Let's also set up global variables and common functions...
previousStageNumber = '23'
thisStageNumber = '30'

def splitTableBasedOnSingleColumn(dataName, previousStageNumber, thisStageNumber, qualityFlag, operatorToUse, operationFlag):
    
    dataFlow, fullPackagePath = openDataFlowPackage(dataName, previousStageNumber, qualityFlag)
    
    if dataFlow:

        print('{0}: loaded package from path {1}'.format(dataName, fullPackagePath))

        dataProfile = dataFlow.get_profile()

        # Set up empty intermediate dataframes that we will use to build up inventories at both dataFlow and column level
        dataFlowInventoryIntermediate = pd.DataFrame()
        columnInventoryIntermediate = pd.DataFrame()

        if operationFlag != '':

            # First, grab the unique set of values in the column
            valuesInColumn = dataProfile.columns[operationFlag].value_counts

            # Now filter the original data flow based on each unique value in turn and fork a new data flow!
            for valueToSplitOn in valuesInColumn:

                newDataFlow = dataFlow.filter(dataFlow[operationFlag] == valueToSplitOn.value)

                # Create a new name for this data flow based on concatenation of source dataflow, column name and value used for filter
                newDataName = dataName + '_' + operationFlag + '_' + valueToSplitOn.value

                newDataProfile = newDataFlow.get_profile()

                # Now generate column and data flow inventories
                columnInventory = getColumnStats(newDataProfile, newDataName, thisStageNumber, operatorToUse, operationFlag)
                dataFlowInventory = getDataFlowStats(newDataFlow, newDataProfile, newDataName, thisStageNumber, operatorToUse, operationFlag)

                # Capture the column inventory for the new dataflow
                columnInventoryIntermediate = columnInventoryIntermediate.append(columnInventory)

                # Capture the data flow inventory for the new data flow
                dataFlowInventoryIntermediate = dataFlowInventoryIntermediate.append(dataFlowInventory)
                
                # Finally save the data flow so it can be passed onto the next stage of the process...
                targetPackagePath = saveDataFlowPackage(newDataFlow, newDataName, thisStageNumber, qualityFlag)
                print('{0}: saved package to {1}'.format(newDataName, targetPackagePath))
        
        else:
            print('{0}: no operation required'.format(dataName))
    
        # Generate column and data flow inventories for the source dataflow
        columnInventory = getColumnStats(dataProfile, dataName, thisStageNumber, operatorToUse, operationFlag)
        columnInventoryIntermediate = columnInventoryIntermediate.append(columnInventory)

        dataFlowInventory = getDataFlowStats(dataFlow, dataProfile, dataName, thisStageNumber, operatorToUse, operationFlag)
        dataFlowInventoryIntermediate = dataFlowInventoryIntermediate.append(dataFlowInventory)

        # Finally save the data flow so it can be passed onto the next stage of the process...
        targetPackagePath = saveDataFlowPackage(dataFlow, dataName, thisStageNumber, qualityFlag)
        print('{0}: saved package to {1}'.format(dataName, targetPackagePath))

        # Now return all of the components badk to the main loop...
        return dataFlow, columnInventoryIntermediate, dataFlowInventoryIntermediate

    else:
        print('{0}: no package file found at location {1}'.format(dataName, fullPackagePath))
        return None, None, None



#%%
dataFlowInventoryAll = dataFlowProcessingLoop(previousStageNumber, thisStageNumber, 'A', 'SplitTable', splitTableBasedOnSingleColumn)

#%%
dataFlowInventoryAll