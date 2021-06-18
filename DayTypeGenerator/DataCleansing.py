import numpy as np
import streamlit as st


@st.cache
def cleanData(rawDataFrame, argOptions):
    """
    Function to be used to clean the data set. Fundamental and first step in the data pipeline process

    The two basic steps (but more can be added) to be implemented should be
    1) validity value check
    2) outliers detection (manual/automatic) and removal
    """

    # just a deep copy of the input because outside we would like to work
    # on both original raw data and cleaned one
    rawDataCopy = rawDataFrame.copy(deep=True)

    validDF = checkValidity(rawDataCopy, argOptions)
    outlierDF, cap_flow, cap_speed = checkOutliers(validDF, argOptions)
    dataAugmentedDF = datetimeAndKeyOptimization(outlierDF, argOptions)
    pivotFlowDF, pivotSpeedDF, completeDF = checkCompleteness(dataAugmentedDF, argOptions)

    return completeDF, cap_flow, cap_speed, pivotFlowDF, pivotSpeedDF


def checkValidity(rawDataFrame, argOptions):
    """
    Function to check minimal and natural constraints of input data

    We are dealing with flows and speeds so they must not be negative at all
    """
    if argOptions.flow >= 0:
        rawDataFrame.iloc[:, argOptions.flow].mask(rawDataFrame.iloc[:, argOptions.flow] < 0, inplace=True)

    if argOptions.speed >= 0:
        rawDataFrame.iloc[:, argOptions.speed].mask(rawDataFrame.iloc[:, argOptions.speed] < 0, inplace=True)

    return rawDataFrame


def checkOutliers(validDataFrame, argOptions):
    """
    Function dedicated to remove outlier data

    Outlier detection is a tricky job and doing it fully automatic in a good way is a matter of complex data
    manipulation, so we decided to give to the user the capability to see the distribution of both speed and flow
    values so that he can choose a percentage threshold to cut out the RIGHT tail of the distribution.
    The functions returns the clean data-set and also the corresponding speed and flow threshold values based
    on the user percentile thresholds.
    The function remove also flow and/or speed values exactly equal to zero as decided by th user
    """
    cap_flow = None
    cap_speed = None

    if argOptions.flow >= 0:
        cap_flow = np.percentile(a=validDataFrame.iloc[:, argOptions.flow].dropna(), q=argOptions.flowThreshold)
        validDataFrame.iloc[:, argOptions.flow].mask(validDataFrame.iloc[:, argOptions.flow] > cap_flow, inplace=True)
        if not argOptions.keepFlowZero:
            validDataFrame.iloc[:, argOptions.flow].mask(validDataFrame.iloc[:, argOptions.flow] == 0, inplace=True)

    if argOptions.speed >= 0:
        cap_speed = np.percentile(a=validDataFrame.iloc[:, argOptions.speed].dropna(), q=argOptions.speedThreshold)
        validDataFrame.iloc[:, argOptions.speed].mask(validDataFrame.iloc[:, argOptions.speed] > cap_speed, inplace=True)
    if not argOptions.keepSpeedZero:
        validDataFrame.iloc[:, argOptions.speed].mask(validDataFrame.iloc[:, argOptions.speed] == 0, inplace=True)

    return validDataFrame, cap_flow, cap_speed


def datetimeAndKeyOptimization(finalCleanDataframe, argOptions):
    """
    This function will expand the dataframe adding a column just storing the date and another one just storing the time
    because it is useful in subsequent processing steps. Moreover the primary key as a single field will be created
    taking ID1 or the concatenation ID1;ID2 in order to have just a single column for querying the IDs
    """
    finalCleanDataframe['Date'] = [d.date() for d in finalCleanDataframe.iloc[:, argOptions.timestamp]]
    finalCleanDataframe['Time'] = [d.time() for d in finalCleanDataframe.iloc[:, argOptions.timestamp]]

    if argOptions.ID2 >= 0:
        finalCleanDataframe['KeyID'] = finalCleanDataframe.iloc[:, argOptions.ID1] + ";" + finalCleanDataframe.iloc[:, argOptions.ID2]
    else:
        finalCleanDataframe['KeyID'] = finalCleanDataframe.iloc[:, argOptions.ID1]

    # maybe here we could set the index of the dataframe to KeyID ...

    return finalCleanDataframe


def checkCompleteness(outlierDataframe, argOptions):
    """
    Function dedicated to drop time profiles having to much missing data, based on maximum allowed percentage
    defined by the user for both the flow and the speed data.

    Pivot tables are used for data visualization and user interaction
    """
    profileKeyNames = outlierDataframe.loc[:, 'KeyID']

    pivotKeyDateFlowDF = None
    if argOptions.flow > 0:
        pivotKeyDateFlowDF = outlierDataframe.pivot_table(index=profileKeyNames,
                                                          columns=outlierDataframe.columns[outlierDataframe.columns.get_loc('Date')],
                                                          values=outlierDataframe.columns[argOptions.flow],
                                                          aggfunc=lambda x: x.count())

        pivotKeyDateFlowDF.mask(100 - pivotKeyDateFlowDF > argOptions.maximumMissingPercentageFlow, inplace=True)

        IDdatesFlow = {}
        for ID in pivotKeyDateFlowDF.index:
             IDdatesFlow[ID] = pivotKeyDateFlowDF.loc[ID, :].dropna().index.astype(str).tolist()

        for key, value in IDdatesFlow.items():
            outlierDataframe.iloc[:, argOptions.flow].mask((outlierDataframe.loc[:, 'KeyID'] == key) &
                                                           (np.logical_not(outlierDataframe.loc[:, 'Date'].astype(str).isin(value))),
                                                           inplace=True)

    pivotKeyDateSpeedDF = None
    if argOptions.speed > 0:
        pivotKeyDateSpeedDF = outlierDataframe.pivot_table(index=profileKeyNames,
                                                           columns=outlierDataframe.columns[outlierDataframe.columns.get_loc('Date')],
                                                           values=outlierDataframe.columns[argOptions.speed],
                                                           aggfunc=lambda x: x.count())

        pivotKeyDateSpeedDF.mask(100 - pivotKeyDateSpeedDF > argOptions.maximumMissingPercentageSpeed, inplace=True)

        IDdatesSpeed = {}
        for ID in pivotKeyDateSpeedDF.index:
            IDdatesSpeed[ID] = pivotKeyDateSpeedDF.loc[ID, :].dropna().index.astype(str).tolist()

        for key, value in IDdatesSpeed.items():
            outlierDataframe.iloc[:, argOptions.speed].mask((outlierDataframe.loc[:, 'KeyID'] == key) &
                                                            (np.logical_not(outlierDataframe.loc[:, 'Date'].astype(str).isin(value))),
                                                            inplace=True)

    return pivotKeyDateFlowDF, pivotKeyDateSpeedDF, outlierDataframe
