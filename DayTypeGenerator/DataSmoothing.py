import utils as ut

import pandas as pd
import math
import streamlit as st


def kernel(n):
    """
    We build here a triangular kernel of half-width n. The first element of the tuple is the position of the kernel
    wrt to the center, while the second element of the tuple is the weight of the kernel to be used to weight the
    function values with which the kernel will be convolved
    """
    return [(k, n - abs(k)) for k in range(-n, n + 1)]


def convolve(f, g):
    """
    This function will simply take the kernel and the signal and convolve them, i.e. substitute the signal data with
    the sum of the product of the kernel values for the corresponding signal elements
    """
    r = [y * f.shift(x) for (x, y) in g]
    return pd.concat(r, axis=1).sum(axis=1)


def smooth(f, g):
    """
    This function finalize the smoothing operation by taking the convolution signal and normalizing it for the kernel
    weights taking into account the NaN values too
    """
    chi_f = f.apply(lambda x: 0.0 if pd.isna(x) else 1.0)
    f_ext = pd.concat([f, chi_f], axis=1).prod(axis=1)
    a = convolve(f_ext, g)
    b = convolve(chi_f, g)
    return a.div(b)


def DataSmoothing(FinalDataFrame, ValueColumnIndex, kernelFunction):
    """
    This function will perform a smoothing of the input signal convolving it with a triangular kernel
    """
    finalCleanPivotTable = pd.pivot_table(data=FinalDataFrame, index='Time', columns='Date',
                                          values=FinalDataFrame.columns[ValueColumnIndex], aggfunc='first')

    SmoothDataFrame = pd.DataFrame()
    for col in finalCleanPivotTable:
        SmoothDataFrame[col] = smooth(finalCleanPivotTable[col], kernelFunction)

    return SmoothDataFrame


@st.cache(allow_output_mutation=True)
def smoothDataframe(FinalDataFrame, argOptions, IDvsDateDictionary, ValueColumnIndex):
    """
    This function will return a dictionary of key-dataframe, each dataframe corresponding to a key of the clean dataset
    and for which the data are smoothed.
    """
    cleanDF = {}
    for key, value in IDvsDateDictionary.items():
        result_df = FinalDataFrame[(FinalDataFrame['KeyID'] == key) & (FinalDataFrame['Date'].isin(value))]
        cleanDF[key] = result_df

    kernelHalfWidth = math.ceil(argOptions.smoothingKernelPercentage * ut.timeBucketNumber(argOptions.TimeResolution) / 200)
    kernelFunction = kernel(kernelHalfWidth)

    smoothDF = {}
    for key, df in cleanDF.items():
        smoothDF[key] = DataSmoothing(df, ValueColumnIndex, kernelFunction)

    return smoothDF
