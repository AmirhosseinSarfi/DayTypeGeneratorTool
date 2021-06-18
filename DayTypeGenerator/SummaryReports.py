import pandas as pd
import datetime


def DetectorClusterSummaryCSV(ClusterResult, FileName):
    """
    the "ClusterResult" dataframe is the clustering result containing "ClusterGroup" and corresponded "Date"
    with the mentioned named. The function dump a CSV file including "WeekDay" and "Month" name with
    "ClusterGroup" in ascending order.
    """
    final_result = pd.DataFrame([])
    for key, df in ClusterResult.items():
        res = df.sort_values(["ClusterGroup"], ascending=True)
        res["KeyID"] = list((key,) * len(df))
        res["WeekDay"] = res["Date"].apply(lambda x: datetime.date.strftime(x, "%A"))
        res["Month"] = res["Date"].apply(lambda x: x.month)
        res = res[["KeyID", "ClusterGroup", "Date", "WeekDay", "Month"]]
        final_result = pd.concat([final_result, res])
    final_result.to_csv(FileName, index=False)


def NetworkClusterSummaryCSV(ClusterResult, FileName):
    result = ClusterResult.sort_values(["ClusterGroup"], ascending=True)
    result["WeekDay"] = result["Date"].apply(lambda x: datetime.date.strftime(x, "%A"))
    result["Month"] = result["Date"].apply(lambda x: x.month)
    result = result[["ClusterGroup", "Date", "WeekDay", "Month"]]

    result.to_csv(FileName, index=False)