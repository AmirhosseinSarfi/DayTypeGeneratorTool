import numpy as np
import pandas as pd
from sklearn import metrics
import itertools
from functools import reduce


# ======================================================================================================================
#                                        INDIVIDUAL DETECTOR KPIs CALCULATION
# ======================================================================================================================
def KPI(smoothDF, ClusterDF, ClusterCentersDF, KPItype):
    """
    With this function we will compute the for each cluster
    - MAE indicator, i.e. the Mean Absolute Error,
    - MAPE indicator, i.e. the Mean Absolute Percentage Error
    - MSE indicator, i.e. the Mean Squared Error
    - RMSE indicator, i.e. the Root Mean Squared Error
    Because we are dealing with time series we have to compute the absolute errors for each point of the time profiles
    and then we have to average all of them. Note that this is OK only under the following caveat, i.e. that the time
    profiles have the same temporal discretization. If one of the two data of the profile is missing we will skip the error
    computation.
    """
    KPI_results = {}

    for keyID, df in ClusterCentersDF.items():
        clusterGroups = df['ClusterGroup']
        KPI_ = []

        for k in clusterGroups:
            representativeIndex = df[df['ClusterGroup'] == k]['ClusterCenterIndex'].to_list()
            center = smoothDF[keyID][smoothDF[keyID].iloc[:, representativeIndex].columns[0]]

            cluster_dates = ClusterDF[keyID][ClusterDF[keyID]['ClusterGroup'] == k]['Date']
            errors = []
            for cd in cluster_dates:
                cl_val = smoothDF[keyID].loc[:, cd]
                if KPItype == "MAE":
                    error = list(abs(cl_val - center))
                elif KPItype == "MAPE":
                    error = list(abs((cl_val - center) / cl_val))
                elif KPItype == "MSE":
                    error = list(np.power((cl_val - center), 2))
                elif KPItype == "RMSE":
                    error = list(np.power((cl_val - center), 2))
                else:
                    print("ERROR: unknow KPI type")

                errors.append(error)

            if KPItype == "MAE" or KPItype == "MAPE" or KPItype == "MSE":
                KPI_.append(np.nanmean(list(itertools.chain(*errors))))
            elif KPItype == "RMSE":
                KPI_.append(np.sqrt(np.nanmean(list(itertools.chain(*errors)))))

        KPI_results[keyID] = pd.DataFrame(zip(clusterGroups, KPI_), columns=['ClusterGroup', KPItype])

    return KPI_results


def KPIsSummaryTable(dataframeList):
    """
    This function take a list of all dataframe for one keyID and merge them on the "ClusterGroup" column
    creating a single table with all the KPIs
    """
    df_final = reduce(lambda left, right: pd.merge(left, right, on='ClusterGroup'), dataframeList)

    return df_final


# ======================================================================================================================
#                                        NETWORK-WIDE KPIs CALCULATION 
# ======================================================================================================================
def SilhoutteScore(X, labels):
    """
    This function returns the mean Silhouette Coefficient over all samples.
    The best value is 1 and the worst value is -1. Values near 0 indicate overlapping clusters.
    """
    kpi_value = metrics.silhouette_score(X, labels, metric='precomputed')
    return ['Silhoutte', kpi_value, '[Bad = -1, Good = 1]']


def CalinskiHarabaszScore(X, labels):
    """
    The score is defined as ratio between the within-cluster dispersion and the between-cluster dispersion.
    There is no "acceptable" cut-off value. The higher the value, the "better" is the solution.
    """
    kpi_value = metrics.calinski_harabasz_score(X, labels)
    return ['Calinski-Harabasz', kpi_value, 'The higher the better']


def DaviesBouldinScore(X, labels):
    """
    The minimum score is zero, with lower values indicating better clustering.
    """
    kpi_value = metrics.davies_bouldin_score(X, labels)
    return ['Davies-Bouldin', kpi_value, 'The lower the better']


def NetworkKpisIntegration(X, labels):
    result = [SilhoutteScore(X, labels),
              CalinskiHarabaszScore(X, labels),
              DaviesBouldinScore(X, labels)]

    result = pd.DataFrame(result)
    result.columns = ['KPI', 'Value', 'Description']

    return result
