import FileReader as fr
import utils as ut
import DataCleansing as dc
import DataAnalysis as da
import DataSmoothing as ds
import DayTypeClustering as dtc
import KPIsCalculation as kc
import SummaryReports as sr
import pandas as pd
import streamlit as st


def processSingleMeasure(rawDataframe, cleanDataframe, pivotKeyDateDF, dataframeColumnIndex,
                         measureType, measureUnit, thresholdPercentage, thresholdValue, argOptions):
    """
    INPUT notes:
    - measureType = can be ONLY   Speed|Flow
    """
    # ==============================================================================================================
    #                                               DATA ANALYSIS
    # ==============================================================================================================
    da.DataAnalysisVisualization(data=rawDataframe, AnalysisType=measureType, unit=measureUnit,
                                 threshold=thresholdPercentage, column_index=dataframeColumnIndex, cap=thresholdValue)

    st.write(da.DataAnalysisStatistics(data=rawDataframe, column_index=dataframeColumnIndex, title='Raw Data Statistic'))

    st.write(da.DataAnalysisStatistics(data=cleanDataframe, column_index=dataframeColumnIndex, title='Clean Data Statistic'))

    da.PivotDataframeHeatmap(DataFrame=pivotKeyDateDF,
                             title=f'{measureType} Data Count Percentage - Max possible counts {ut.timeBucketNumber(argOptions.TimeResolution)}',
                             timeBucketNumber=ut.timeBucketNumber(argOptions.TimeResolution))

    # ==============================================================================================================
    #                                               DATA UNIQUE ENTRIES
    # ==============================================================================================================
    # build the set of unique keys and the set of corresponding unique dates

    uniqueDatesGivenAKey = {}
    uniqueKeys = cleanDataframe[cleanDataframe[measureType.lower()] >= 0]['KeyID'].unique()
    for key in uniqueKeys:
        uniqueDatesGivenAKey[key] = cleanDataframe[(cleanDataframe['KeyID'] == key) & (cleanDataframe[measureType.lower()] >= 0)]['Date'].unique()

    # ==============================================================================================================
    #                                               DATA SMOOTHING
    # ==============================================================================================================
    st.subheader("Data Smoothing")
    smoothDF = ds.smoothDataframe(cleanDataframe, argOptions, uniqueDatesGivenAKey, dataframeColumnIndex)

    # plot raw and smooth profiles
    IDOption = st.selectbox("Key ID", uniqueKeys, key='IDOption'+measureType)
    DateOption = st.selectbox("Date", uniqueDatesGivenAKey[IDOption], key='DateOption'+measureType)
    da.plotSeriesOriginalAndSmooth(smoothDF[IDOption].index,
                                   cleanDataframe[(cleanDataframe['KeyID'] == IDOption) & (cleanDataframe['Date'] == DateOption)][measureType.lower()],
                                   smoothDF[IDOption][DateOption],
                                   "Key ID = " + str(IDOption) + " ; Date = " + str(DateOption),
                                   measureUnit)

    # ==============================================================================================================
    #                                            CLUSTERING INDIVIDUAL KEY
    # ==============================================================================================================
    if argOptions.enableProfileClustering:
        st.subheader("Clustering Single Measurement Sections")

        sectionClusterDF, sectionClusterCentersDF = dtc.IndividualDetectorClusteringResult(smoothDF)
        numberOfClusters = [len(df.index) for df in sectionClusterCentersDF.values()]
        st.write(da.DataAnalysisStatistics(data=pd.DataFrame(numberOfClusters), column_index=0,
                                           title='Statistic of Number of Clusters'))

        da.plotSeriesNumberOfClusters(list(sectionClusterCentersDF.keys()), numberOfClusters,
                                      title="",
                                      xlabel="Key ID",
                                      ylabel="Number of Clusters")

        IDOptionCluster = st.selectbox("Key ID", uniqueKeys, key='IDOptionCluster'+measureType)

        da.CalendarHeatMap(sectionClusterDF[IDOptionCluster],
                           title='Cluster Calendar Heatmap' + " (Key ID = " + str(IDOptionCluster)+")",
                           measureType=measureType)

        da.plotClusterParallelByClusterID(sectionClusterDF[IDOptionCluster],
                                          title='Cluster Associations by Cluster-ID' + " (Key ID = " + str(IDOptionCluster)+")")
        da.plotClusterParallelByWeekday(sectionClusterDF[IDOptionCluster],
                                        title='Cluster Associations by Weekday' + " (Key ID = " + str(IDOptionCluster)+")")

        clusterOption = st.selectbox("Cluster ID", sectionClusterDF[IDOptionCluster]['ClusterGroup'].unique(),
                                     key='clusterOption'+measureType)

        dates = list(sectionClusterDF[IDOptionCluster][sectionClusterDF[IDOptionCluster]['ClusterGroup'] == clusterOption]['Date'])

        da.plotSeriesClusterOriginal(smoothDF[IDOption].index, cleanDataframe, IDOptionCluster, dates,
                                     title='Original Profiles ' + "(Key ID = " + str(IDOptionCluster) + " - Cluster ID = " + str(clusterOption) +")",
                                     ylabel=measureUnit,
                                     measureType=measureType)
        da.plotSeriesClusterSmoothed(smoothDF[IDOption].index, smoothDF, IDOptionCluster, dates,
                                     title='Smoothed Profiles' + "(Key ID = " + str(IDOptionCluster) + " - Cluster ID = " + str(clusterOption) +")",
                                     ylabel=measureUnit)
        da.plotBoxPlotClusterSmoothed(smoothDF, sectionClusterCentersDF, IDOptionCluster, clusterOption, dates,
                                      title='Box-Plot Smoothed Profiles' + "(Key ID = " + str(IDOptionCluster) + " - Cluster ID = " + str(clusterOption) +")",
                                      ylabel=measureUnit)

        # ==============================================================================================================
        #                                               CALCULATING KPIs
        # ==============================================================================================================
        MAE_singleKey = kc.KPI(smoothDF, sectionClusterDF, sectionClusterCentersDF, "MAE")
        MAPE_singleKey = kc.KPI(smoothDF, sectionClusterDF, sectionClusterCentersDF, "MAPE")
        MSE_singleKey = kc.KPI(smoothDF, sectionClusterDF, sectionClusterCentersDF, "MSE")
        RMSE_singleKey = kc.KPI(smoothDF, sectionClusterDF, sectionClusterCentersDF, "RMSE")

        kpi_summary = kc.KPIsSummaryTable([MAE_singleKey[IDOptionCluster],
                                           MAPE_singleKey[IDOptionCluster],
                                           MSE_singleKey[IDOptionCluster],
                                           RMSE_singleKey[IDOptionCluster]])

        st.subheader(f'KPI Summary Table KeyID: {IDOptionCluster}')
        st.write(kpi_summary)

        # ==============================================================================================================
        #                                              EXPORT CSV RESULTS
        # ==============================================================================================================
        sr.DetectorClusterSummaryCSV(sectionClusterDF, '.\\Results\\Individual_Cluster_Results.csv')

        kpi_summary = pd.DataFrame(columns=['KeyID', 'MAE', 'MAPE', 'MSE', 'RMSE'])
        kpi_summary.to_csv(".\\Results\\Individual_Cluster_KPIs.csv", index=False, mode="w", header=True)
        for key in uniqueKeys:
            kpi_summary = kc.KPIsSummaryTable([MAE_singleKey[key],
                                               MAPE_singleKey[key],
                                               MSE_singleKey[key],
                                               RMSE_singleKey[key]])
            kpi_summary["KeyID"] = key
            kpi_summary.to_csv(".\\Results\\Individual_Cluster_KPIs.csv",
                               columns=['KeyID', 'MAE', 'MAPE', 'MSE', 'RMSE'],
                               index=False, mode="a", header=False)

    # ==============================================================================================================
    #                                        CLUSTERING AT NETWORK LEVEL
    # ==============================================================================================================
    if argOptions.enableNetworkClustering:
        st.subheader("Clustering at Network Level for Day-Type Definition")

        #TODO: make the K selection via elbow logic or sihlouette avg score
        networkclusterResult, network_labels = dtc.clusteringNetworkData(dtc.networkSimilarityMatrix(sectionClusterDF),
                                                         numberOfClusters=argOptions.KmeansNumberOfFlowCluster)

        da.CalendarHeatMap(networkclusterResult, title='Cluster Calendar Heatmap', measureType=measureType)

        da.plotClusterParallelByClusterID(networkclusterResult, title='Cluster Associations by Cluster-ID')

        da.plotClusterParallelByWeekday(networkclusterResult, title='Cluster Associations by Weekday')

        # ==============================================================================================================
        #                                               CALCULATING KPIs
        # ==============================================================================================================
        pairwise_distance = dtc.networkDistanceMatrix(dtc.networkSimilarityMatrix(sectionClusterDF))
        network_kpis_summary = kc.NetworkKpisIntegration(pairwise_distance, network_labels)

        st.subheader("Network-Wide KPIs Summary Table")
        st.write(network_kpis_summary)

        # ==============================================================================================================
        #                                              EXPORT CSV RESULTS
        # ==============================================================================================================
        sr.NetworkClusterSummaryCSV(networkclusterResult, '.\\Results\\Network_Cluster_Results.csv')

        network_kpis_summary.to_csv(".\\Results\\Network_Cluster_KPIs.csv", index=False)


def run(argOptions):
    print("Reading input")
    df = fr.readInputFile(argOptions)
    st.subheader('Raw Data Sample (first 100 rows)')
    st.dataframe(df.head(100))

    print("Cleaning data")
    cleanDF, cap_flow, cap_speed, pivotKeyDateFlowDF, pivotKeyDateSpeedDF = dc.cleanData(df, argOptions)

    if argOptions.flow >= 0:
        print("Processing Flow")
        processSingleMeasure(rawDataframe=df, cleanDataframe=cleanDF, pivotKeyDateDF=pivotKeyDateFlowDF,
                             dataframeColumnIndex=argOptions.flow, measureType='Flow', measureUnit='Veh/h',
                             thresholdPercentage=argOptions.flowThreshold, thresholdValue=cap_flow,
                             argOptions=argOptions)
    if argOptions.speed >= 0:
        print("Processing Speed")
        processSingleMeasure(rawDataframe=df, cleanDataframe=cleanDF, pivotKeyDateDF=pivotKeyDateSpeedDF,
                             dataframeColumnIndex=argOptions.speed, measureType='Speed', measureUnit='Km/h',
                             thresholdPercentage=argOptions.speedThreshold, thresholdValue=cap_speed,
                             argOptions=argOptions)
