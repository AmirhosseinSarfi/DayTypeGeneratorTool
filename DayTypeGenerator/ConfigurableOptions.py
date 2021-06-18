import argparse
import streamlit as st
import os
import json
from PIL import Image


def parseArgument(parserObject):
    parserObject.add_argument('--GUI',
                              default="False",
                              choices=['False', 'True'],
                              help="Option to enable Streamlit GUI")

    parserObject.add_argument('--conf',
                              default=None,
                              help="Option to enable reading from JSON file")

    parserObject.add_argument('--inputFile',
                              type=argparse.FileType('r'),
                              help="Filename of input data")

    parserObject.add_argument('--compression',
                              default='None',
                              choices=['None', 'zip', 'gzip', 'bz2', 'xz'],
                              help="Specify the file compression. If using ‘zip’, the ZIP file must contain only "
                                   "one data file to be read in")

    parserObject.add_argument('--format',
                              default="csv",
                              choices=['csv'],
                              help="Input file format")

    parserObject.add_argument('--fileSeparator',
                              default=",",
                              choices=[',', ';', '|'],
                              help="File separator")

    parserObject.add_argument('--header',
                              default='False',
                              choices=['True', 'False'],
                              help="Specify if the input data has or not a header")

    parserObject.add_argument('--TimeResolution',
                              type=int,
                              default=15,
                              help="Define Time Resolution in Minutes")

    parserObject.add_argument('--ID1',
                              default=-1,
                              help="Column index for ID1")

    parserObject.add_argument('--ID2',
                              default=-1,
                              help="Column index for ID2")

    parserObject.add_argument('--timestamp',
                              default=-1,
                              help="Column index for timestamp")

    parserObject.add_argument('--flow',
                              default=-1,
                              help="Column index for flow value")

    parserObject.add_argument('--speed',
                              default=-1,
                              help="Column index for speed value")

    parserObject.add_argument('--flowFactor',
                              type=float,
                              default=1.0,
                              help="Conversion factor to Vehicle/Hour")

    parserObject.add_argument('--speedFactor',
                              type=float,
                              default=1.0,
                              help="Conversion factor to Km/Hour")

    parserObject.add_argument('--keepFlowZero',
                              type=bool,
                              default=True,
                              help="Boolean to decide to keep or not flow values exactly equal to zero")

    parserObject.add_argument('--keepSpeedZero',
                              type=bool,
                              default=True,
                              help="Boolean to decide to keep or not speed values exactly equal to zero")

    parserObject.add_argument('--flowThreshold',
                              type=float,
                              default=100.0,
                              help="Percentage threshold to cut on the right the Flow distribution")

    parserObject.add_argument('--speedThreshold',
                              type=float,
                              default=100.0,
                              help="Percentage threshold to cut on the right the Speed distribution")

    parserObject.add_argument('--maximumMissingPercentageFlow',
                              type=float,
                              default=100.0,
                              help="Maximum percentage of missing data for a flow profile")

    parserObject.add_argument('--maximumMissingPercentageSpeed',
                              type=float,
                              default=100.0,
                              help="Maximum percentage of missing data for a speed profile")

    parserObject.add_argument('--smoothingKernelPercentage',
                              type=float,
                              default=10.0,
                              help="Percentage of time items of the time profiles for defining the width of the smoothing kernel")

    parserObject.add_argument('--enableProfileClustering',
                              type=bool,
                              default=False,
                              help="Enable the capability to cluster profiles for each single ID")

    parserObject.add_argument('--enableNetworkClustering',
                              type=bool,
                              default=False,
                              help="Enable network clustering for Day-Type definition")

    parserObject.add_argument('--KmeansNumberOfFlowCluster',
                              type=int,
                              default=12,
                              help="Define Number of Flow Data Clusters by K-Means Clustering Algorithm")

    parserObject.add_argument('--KmeansNumberOfSpeedCluster',
                              type=int,
                              default=12,
                              help="Define Number of Speed Data Clusters by K-Means Clustering Algorithm")

    args = parserObject.parse_args()

    # REMINDER: each new option must be added also under this conditional branch
    if args.GUI == 'True':
        st.sidebar.header("Input File")
        args.inputFile = st.sidebar.text_input('Input Filename', args.inputFile, key="inputfile")
        args.compression = st.sidebar.radio('File compression', ("None", "zip", "gzip", "bz2", "xz"), key="compression")
        args.format = st.sidebar.selectbox('Input File Format', ("csv",), key="format")
        args.fileSeparator = st.sidebar.selectbox('Input File Separator', (",", ";", "|"), key="separator")
        args.header = st.sidebar.radio('Does file have header?', ("False", "True"), key="header")
        args.TimeResolution = int(st.sidebar.text_input('Time Resolution in Minutes', value=args.TimeResolution, key="TimeResolution"))
        args.ID1 = st.sidebar.number_input('Column index ID1', min_value=-1, value=args.ID1, key="ID1")
        args.ID2 = st.sidebar.number_input('Column index ID2', min_value=-1, value=args.ID2, key="ID2")
        args.timestamp = st.sidebar.number_input('Column index Timestamp', min_value=-1, value=args.timestamp,
                                                 key="timestamp")
        args.flow = st.sidebar.number_input('Column index Flow', min_value=-1, value=args.flow, key="flow")
        args.speed = st.sidebar.number_input('Column index Speed', min_value=-1, value=args.speed, key="speed")
        args.flowFactor = float(st.sidebar.text_input('Flow conversion factor to Veh/h', value=args.flowFactor, key="flowFactor"))
        args.speedFactor = float(st.sidebar.text_input('Speed conversion factor to Km/h', value=args.speedFactor, key="speedFactor"))

        st.sidebar.header("Data Cleansing")
        if args.flow >= 0:
            args.keepFlowZero = st.sidebar.checkbox("Keep Flow zeros", True, key="keepFlowZero")
            args.flowThreshold = float(st.sidebar.slider("Flow Threshold Percentage", 0, 100, 100))
            args.maximumMissingPercentageFlow = float(st.sidebar.slider("Max Missing Flow Percentage", 0, 100, 100))
        if args.speed >= 0:
            args.keepSpeedZero = st.sidebar.checkbox("Keep Speed zeros", True, key="keepSpeedZero")
            args.speedThreshold = float(st.sidebar.slider("Speed Threshold Percentage", 0, 100, 100))
            args.maximumMissingPercentageSpeed = float(st.sidebar.slider("Max Missing Speed Percentage", 0, 100, 100))

        st.sidebar.header("Data Smoothing")
        args.smoothingKernelPercentage = float(st.sidebar.slider("Percentage for kernel smoothing width", 0, 100, 10))

        st.sidebar.header("Clustering")
        args.enableProfileClustering = st.sidebar.checkbox("Enable clustering of profiles for each ID", False,
                                                           key="enableProfileClustering")
        if args.enableProfileClustering:
            args.enableNetworkClustering = st.sidebar.checkbox("Enable network clustering for Day-Type definition",
                                                               False,
                                                               key="enableNetworkClustering")
            if args.flow >= 0:
                args.KmeansNumberOfFlowCluster = int(st.sidebar.number_input('Number of network clusters (based on Flow data)',
                                                                           min_value=2,
                                                                           value=args.KmeansNumberOfFlowCluster,
                                                                           key="KmeansNumberOfFlowCluster"))
            if args.speed >= 0:
                args.KmeansNumberOfSpeedCluster = int(
                    st.sidebar.number_input('Number of network clusters (based on Speed data)',
                                          min_value=2,
                                          value=args.KmeansNumberOfSpeedCluster,
                                          key="KmeansNumberOfSpeedCluster"))
    if args.conf:
        json_filename = ".\\conf\\" + args.conf if os.path.basename(args.conf) == args.conf else args.conf
        with open(json_filename, 'r') as json_file:
            data = json.load(json_file)
            args.inputFile = data["inputFile"]
            args.compression = data["compression"]
            args.format = data["format"]
            args.fileSeparator = data["fileSeparator"]
            args.header = data["header"]
            args.TimeResolution = data["TimeResolution"]
            args.ID1 = data["ID1"]
            args.ID2 = data["ID2"]
            args.timestamp = data["timestamp"]
            args.flow = data["flow"]
            args.speed = data["speed"]
            args.flowFactor = data["flowFactor"]
            args.speedFactor = data["speedFactor"]
            args.keepFlowZero = data["keepFlowZero"]
            args.keepSpeedZero = data["keepSpeedZero"]
            args.flowThreshold = data["flowThreshold"]
            args.speedThreshold = data["speedThreshold"]
            args.maximumMissingPercentageFlow = data["maximumMissingPercentageFlow"]
            args.maximumMissingPercentageSpeed = data["maximumMissingPercentageSpeed"]
            args.smoothingKernelPercentage = data["smoothingKernelPercentage"]
            args.enableProfileClustering = data['enableProfileClustering']
            args.enableNetworkClustering = data["enableNetworkClustering"]
            args.KmeansNumberOfFlowCluster = data["KmeansNumberOfFlowCluster"]
            args.KmeansNumberOfSpeedCluster = data["KmeansNumberOfSpeedCluster"]
    return args


def checkOption(boolCondition, errorMessage, errorImage):
    if boolCondition:
        st.image(errorImage, caption=errorMessage, width=128, format='PNG')
        raise Exception("CONFIGURATION ERROR: ", errorMessage)


def checkArgument(argOptions):

    ImageErrorDirectory = ".\\images\\error.png"

    errorImg = Image.open(ImageErrorDirectory)
    optionsAreOK = True

    checkOption(argOptions.inputFile is None or not os.path.exists(argOptions.inputFile),
                'Input file not found',
                errorImg)

    # REMINDER: put in OR all supported future formats
    checkOption(not (argOptions.format == "csv"),
                'File format not supported',
                errorImg)

    # REMINDER: put in OR all supported future file separators
    checkOption(not (argOptions.fileSeparator == "," or
                     argOptions.fileSeparator == ";" or
                     argOptions.fileSeparator == "|"),
                'File separator not supported',
                errorImg)

    checkOption(int(argOptions.ID1) < 0,
                'Key ID1 must be specified',
                errorImg)

    checkOption(int(argOptions.timestamp) < 0,
                'Timestamp must be specified',
                errorImg)

    checkOption(int(argOptions.flow) < 0 and int(argOptions.speed) < 0,
                'Speed and/or Flow must be specified',
                errorImg)

    checkOption(float(argOptions.flowFactor) < 0.0,
                'Flow conversion factor must be greater than zero',
                errorImg)

    checkOption(float(argOptions.speedFactor) < 0.0,
                'Speed conversion factor must be greater than zero',
                errorImg)

    checkOption(float(argOptions.flowThreshold) > 100.0 or float(argOptions.flowThreshold) < 0.0,
                'Flow threshold must be a percentage value (between 0% and 100%)',
                errorImg)

    checkOption(float(argOptions.speedThreshold) > 100.0 or float(argOptions.speedThreshold) < 0.0,
                'Speed threshold must be a percentage value (between 0% and 100%)',
                errorImg)

    return optionsAreOK


