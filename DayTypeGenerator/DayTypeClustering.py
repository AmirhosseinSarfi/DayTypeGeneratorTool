import numpy as np
import pandas as pd
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import KMeans
import streamlit as st


# ==============================================================================================================
#                                            CLUSTERING INDIVIDUAL KEY
# ==============================================================================================================
@st.cache
def similarityMatrix(FinalSmoothedDataFrame):
    """
    The function will compute the similarity matrix among all the profiles of one ID element via a correlation
    measure. The dot product between two profiles will be done, only where both are defined, and normalized with
    respect the sqrt of the norms of the two profiles.
    The matrix is clearly symmetric and on the diagonal it will be set the value of 1
    """
    dates = FinalSmoothedDataFrame.columns
    values = FinalSmoothedDataFrame.values.T
    size = len(dates)
    similarity_matrix = []
    for k in range(0, size):
        correlation = []
        M1 = (np.nansum(values[k] ** 2))
        for j in range(0, size):
            if k == j:
                value = 1.0
            else:
                H = np.nansum(values[k] * values[j])
                M2 = (np.nansum(values[j] ** 2))
                # M1 and M2 should never be 0 if it happens it means we have to handle better the cleaning
                value = H / ((M1 * M2) ** .5)
            correlation.append(value)
        similarity_matrix.append(correlation)

    similarityDF = pd.DataFrame(similarity_matrix, index=dates, columns=dates)

    return similarityDF


def IndividualDetectorClusteringResult(FinalSmoothedDataFrame):
    """
    This function will perform the affinity propagation clustering returning a dictionary of KeyID and dataframes
    where for each date is associated the cluster id obtained. Moreover the indexes of the centroids of each cluster
    are returned.
    """
    individual_clustering = {}
    centers_clustering = {}

    for keyID, df in FinalSmoothedDataFrame.items():
        dates = df.columns
        similarityDF = similarityMatrix(df)

        clustering = AffinityPropagation(affinity='precomputed').fit(similarityDF)
        labels = clustering.labels_
        centers = clustering.cluster_centers_indices_

        cluster_result = pd.DataFrame(zip(dates, labels), columns=['Date', 'ClusterGroup'])
        cluster_centers = pd.DataFrame(zip(range(0, len(centers)), centers), columns=['ClusterGroup', 'ClusterCenterIndex'])

        individual_clustering[keyID] = cluster_result
        centers_clustering[keyID] = cluster_centers

    return individual_clustering, centers_clustering


# ==============================================================================================================
#                                        CLUSTERING AT NETWORK LEVEL
# ==============================================================================================================
@st.cache
def networkSimilarityMatrix(singleLocationClusteringDF):
    """
    In order to perform a clustering for day-type definition at network level, if we will use Affinity algorithm (or
    whatever else in the future in which the number of cluster is not specified) and so an appropriate similarity between
    the dates has to be enforced.
    The key idea is to build a dataframe where for each tuple (keyID,clusterGroupID) we will have a ONE for the dates
    contributing at clustering of single KeyID and such ClustergroupID and a ZERO elsewhere. Once such big dataframe is
    filled we will define the similarity between two days looking to their ONE-ZERO patterns and defining the similarity
    as the count of the double ones over the count of the KeyID that have data in the both considered days

                         date1    date2    date3
    KeyID   ClusterID
      A         1         1        1         0
      A         2         0        0         1
      B         1         1        1         1
      C         1         0        1         1

      So
      Similarity(date1,date2) = 2 / 2
      Similarity(date1,date3) = 1 / 3
      Similarity(date2,date3) = 2 / 3

      Note: the similarity can be computed easily doing matrix algebra manipulations on top of the above sketched
      dataframe

      Note that self-similarity is granted to be 1 :)
      Note that you can see such definition of the ratio of intersection of 1-0 strings over the cardinality of the
      corresponding biclique keyID set, so for a given intersection value the bigger is the size of the biclique the
      smaller is the similarity as naively expected
    """
    # rebuild the whole dataframe
    setOfDays = set()
    for key in singleLocationClusteringDF:
        for d in singleLocationClusteringDF[key]['Date'].unique():
            setOfDays.add(d.strftime("%Y-%m-%d"))

    IDcol = []
    ClusterCol = []
    key2cluster2days = {}
    for key in singleLocationClusteringDF:
        key2cluster2days[key] = {}
        for cl in singleLocationClusteringDF[key]['ClusterGroup'].unique():
            IDcol.append(key)
            ClusterCol.append(cl)
            key2cluster2days[key][cl] = [d.strftime("%Y-%m-%d") for d in list(singleLocationClusteringDF[key][singleLocationClusteringDF[key]['ClusterGroup'] == cl]['Date'])]

    # print(key2cluster2days)

    tmpDF = pd.DataFrame(IDcol, columns=['KeyID'])
    tmpDF['ClusterGroup'] = ClusterCol
    for d in setOfDays:
        tmpDF[d] = np.zeros(len(tmpDF.index))

    for key in key2cluster2days:
        for cl in key2cluster2days[key]:
            for d in key2cluster2days[key][cl]:
                indexRow = tmpDF.index[(tmpDF['KeyID'] == key) & (tmpDF['ClusterGroup'] == cl)].tolist()
                tmpDF.at[indexRow[0], d] = 1.0

    # print(tmpDF)

    simNumerator = []
    for d in setOfDays:
        simNumerator.append(tmpDF[d].to_numpy())
    num = np.asarray(simNumerator, dtype=np.float32)

    # print(np.matmul(num, num.T))

    pivotTmpDF = tmpDF.pivot_table(index=['KeyID'], values=list(setOfDays), aggfunc=lambda x: x.sum())
    # print(pivotTmpDF)

    simDenominator = []
    for d in setOfDays:
        simDenominator.append(pivotTmpDF[d].to_numpy())
    den = np.asarray(simDenominator, dtype=np.float32)

    # print(np.matmul(den, den.T))

    similarityMatrixDays = np.nan_to_num(np.divide(np.matmul(num, num.T), np.matmul(den, den.T)))
    # print(similarityMatrixDays)

    similarityMatrixDaysDF = pd.DataFrame(similarityMatrixDays, index=list(setOfDays), columns=list(setOfDays))
    # print(similarityMatrixDaysDF)

    return similarityMatrixDaysDF


@st.cache
def networkDistanceMatrix(similarityMatrixDaysDF):
    """
    In order to perform a clustering for day-type definition at network level, we will use a K-mean algorithm (or
    whatever else in the future in which the number of cluster must be specified) and so an appropriate distance between
    the dates has to be enforced. Here we will simply define the distance matrix as a function of the similarity matrix.
    """
    # you could try to implement other functions mapping the similarity to the distance, just taking care to
    # monotonic decreasing in similarity with proper boundary values
    Network_Distance_Matrix = np.exp(-similarityMatrixDaysDF) - np.exp(-1)

    return Network_Distance_Matrix


def clusteringNetworkData(similarityMatrixDaysDF, numberOfClusters):
    """
    The idea of such clustering is to define a set of day-types valid for the entire network starting from the profiles
    of flow or speed and having clustered them for each single location.
    """
    Network_Distance_Matrix = networkDistanceMatrix(similarityMatrixDaysDF)

    clustering = KMeans(n_clusters=numberOfClusters, precompute_distances=True)
    clustering.fit(Network_Distance_Matrix)
    labels = clustering.labels_

    cluster_result = pd.DataFrame(zip(pd.to_datetime(similarityMatrixDaysDF.columns), labels), columns=['Date', 'ClusterGroup'])

    return cluster_result, labels
