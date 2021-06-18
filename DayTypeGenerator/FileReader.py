import pandas as pd
import streamlit as st


@st.cache
def readInputFile(argOptions):
    if argOptions.format == "csv":
        df = readInputFileCSV(argOptions)
    return df


def readInputFileCSV(argOptions):
    columnIndex = {"ID1": argOptions.ID1,
                   "ID2": argOptions.ID2,
                   "timestamp": argOptions.timestamp,
                   "flow": argOptions.flow,
                   "speed": argOptions.speed}

    columnType = {"ID1": "str",
                  "ID2": "str",
                  "timestamp": "datetime",
                  "flow": "float64",
                  "speed": "float64"}

    columnNames = {}
    dtypes = {}
    for key, value in columnIndex.items():
        if int(value) >= 0:
            columnNames[key] = value
            if columnType[key] != "datetime":
                dtypes[value] = columnType[key]

    # sort columns by value index so that we can set corresponding names
    columnNames = {k: v for k, v in sorted(columnNames.items(), key=lambda item: item[1])}

    df = pd.read_csv(argOptions.inputFile,
                     sep=argOptions.fileSeparator,
                     header=(None if argOptions.header == "False" else 0),
                     usecols=columnNames.values(),
                     dtype=dtypes,
                     parse_dates=[columnNames["timestamp"]],
                     compression=(None if argOptions.compression == "None" else argOptions.compression))

    # set standard column names
    df.columns = columnNames.keys()

    # column conversion operations
    if 'flow' in columnNames:
        df['flow'] *= argOptions.flowFactor
    if 'speed' in columnNames:
        df['speed'] *= argOptions.speedFactor

    return df
