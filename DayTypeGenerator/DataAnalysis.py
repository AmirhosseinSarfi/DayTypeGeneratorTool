import streamlit as st
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px


def DataAnalysisVisualization(data, AnalysisType, unit, threshold, column_index, cap):
    """
    A simple function to plot the histogram of the specified column of a dataframe, its normalized cumulative, and
    horizontal and vertical lines corresponding to a threshold.
    """
    st.title(f'{AnalysisType} Data Analysis')

    plt.figure(figsize=(10, 4))
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(10, 5), sharex=True)

    axs[0].hist(data.iloc[:, column_index].dropna(), density=True, bins=20, histtype='stepfilled', linewidth=2.5,
                color='teal')

    axs[0].set_title(f"{AnalysisType} Distribution", weight='bold')
    axs[0].set_xlabel(f'{AnalysisType} ({unit})')
    axs[0].set_xlim(0, )
    axs[0].axvline(x=cap, linewidth=3.5, linestyle='--', color='r')

    axs[1].set_title("Normalized Cumulative Distribution", weight='bold')
    axs[1].set_xlabel(f'{AnalysisType} ({unit})')
    axs[1].hist(data.iloc[:, column_index].dropna(), cumulative=True, density=True, bins=90, histtype='step',
                linewidth=3, color='teal')

    x1, y1 = [0, cap], [threshold / 100, threshold / 100]
    x2, y2 = [cap, cap], [0, threshold / 100]
    axs[1].plot(x1, y1, x2, y2, c='r', linewidth=2.3)

    st.write(f"The {AnalysisType} threshold is: ", round(cap, 3), f"({unit})")
    st.pyplot()


def DataAnalysisStatistics(data, column_index, title):
    """
    Function used only to print descriptive statistics as given by pandas, i.e
    - count | mean | std | min | 25% | 50% | 75% | max
    for a specified column of a dataframe
    """
    st.write(title)
    return pd.DataFrame(data.iloc[:, column_index]).describe().T


def PivotDataframeHeatmap(DataFrame, title, timeBucketNumber):
    """
    Function to visualize the heatmap of a pivot dataframe. Percentage and absolute number
    """
    fig = go.Figure(data=go.Heatmap(
        z=(100 * DataFrame / timeBucketNumber),
        x=DataFrame.columns,
        y=DataFrame.transpose().columns,
        hovertext=DataFrame,
        zmin=0,
        zmax=100,
        colorscale='Viridis'))

    fig.update_layout(
        title=title,
        xaxis_nticks=36)

    st.plotly_chart(fig)


def plotSeriesNumberOfClusters(xvalue, yvalue, title, xlabel, ylabel):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xvalue,
                             y=yvalue,
                             mode='markers',
                             name='---'))
    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'},
        xaxis_title=xlabel,
        yaxis_title=ylabel)

    st.plotly_chart(fig)


def plotSeriesOriginalAndSmooth(xvalue, yvalue1, yvalue2, title, ylabel):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xvalue,
                             y=yvalue1,
                             mode='lines+markers',
                             name='Original'))

    fig.add_trace(go.Scatter(x=xvalue,
                             y=yvalue2,
                             mode='lines+markers',
                             name='Smoothed'))
    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'},
        yaxis_title=ylabel)

    st.plotly_chart(fig)


def plotSeriesClusterOriginal(xvalue, originalDF, ID, dates, title, ylabel, measureType):
    fig = go.Figure()
    for d in dates:
        fig.add_trace(go.Scatter(x=xvalue,
                                 y=originalDF[(originalDF['KeyID'] == ID) & (originalDF['Date'] == d)][measureType.lower()],
                                 mode='lines+markers',
                                 name=str(d)))

    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'},
        yaxis_title=ylabel,
        showlegend=True)

    st.plotly_chart(fig)


def plotSeriesClusterSmoothed(xvalue, smoothDF, ID, dates, title, ylabel):
    fig = go.Figure()
    for d in dates:
        fig.add_trace(go.Scatter(x=xvalue,
                                 y=smoothDF[ID][d],
                                 mode='lines+markers',
                                 name=str(d)))
    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'},
        yaxis_title=ylabel,
        showlegend=True)

    st.plotly_chart(fig)


def plotBoxPlotClusterSmoothed(smoothDF, clusterCenterDF, ID, clusterID, dates, title, ylabel):
    times = [t.strftime("%H:%M") for t in smoothDF[ID].index]
    N = len(times)
    y_data = []
    for t in range(N):
        tmpList = []
        for d in dates:
            tmpList.append(smoothDF[ID][d].iloc[t])
        y_data.append(tmpList)

    fig = go.Figure()
    representativeIndex = clusterCenterDF[ID][clusterCenterDF[ID]['ClusterGroup'] == clusterID]['ClusterCenterIndex'].to_list()
    dd = smoothDF[ID].iloc[:, representativeIndex].columns

    fig.add_trace(go.Scatter(x=times, y=list(smoothDF[ID][dd[0]]),
                             mode='lines+markers',
                             marker_color='black',
                             name=str("Representative")))

    for xd, yd in zip(times, y_data):
        fig.add_trace(go.Box(
            y=yd,
            name=xd,
            showlegend=False,
            notched=True,
            whiskerwidth=0.2,
            marker_color='gray',
            marker_size=2,
            line_width=1)
        )

    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'},
        yaxis_title=ylabel)

    st.plotly_chart(fig)


def plotClusterParallelByClusterID(singleKeyClusterDF, title):
    df = pd.DataFrame(singleKeyClusterDF['ClusterGroup'], columns=['ClusterGroup'])
    dfDate = pd.DataFrame(pd.to_datetime(singleKeyClusterDF['Date'], format="%Y-%m-%d"),
                          columns=['Date'])
    years = [d.strftime("%Y") for d in dfDate['Date']]
    df['years'] = years
    months = [d.strftime("%B") for d in dfDate['Date']]
    df['months'] = months
    weekday = [d.strftime("%A") for d in dfDate['Date']]
    df['weekday'] = weekday
    fig = px.parallel_categories(df,
                                 color="ClusterGroup", color_continuous_scale='Viridis',
                                 labels={'ClusterGroup': 'Cluster ID', 'months': 'Month', 'weekday': 'Weekday',
                                         'years': 'Year'})
    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'})

    st.plotly_chart(fig)


def plotClusterParallelByWeekday(singleKeyClusterDF, title):
    df = pd.DataFrame(singleKeyClusterDF['ClusterGroup'], columns=['ClusterGroup'])
    dfDate = pd.DataFrame(pd.to_datetime(singleKeyClusterDF['Date'], format="%Y-%m-%d"),
                          columns=['Date'])
    years = [d.strftime("%Y") for d in dfDate['Date']]
    df['years'] = years
    months = [d.strftime("%B") for d in dfDate['Date']]
    df['months'] = months
    weekday = [d.weekday() for d in dfDate['Date']]
    df['weekday'] = weekday
    fig = px.parallel_categories(df,
                                 color="weekday", color_continuous_scale='Viridis',
                                 labels={'ClusterGroup': 'Cluster ID', 'months': 'Month', 'weekday': 'Weekday',
                                         'years': 'Year'})

    fig.update_layout(
        title={
            'text': title,
            'yanchor': 'top'})

    st.plotly_chart(fig)


def CalendarHeatMap(Cluster_Result, title, measureType):
    clusterOption = Cluster_Result['ClusterGroup'].unique()

    clusterSelection = [-1]
    datesToFlatten = []
    for cid in clusterOption:
        clusterSelection.append(cid)

        tmpdates = list(Cluster_Result[Cluster_Result['ClusterGroup'] == cid]['Date'])
        datesToFlatten.append(tmpdates)
    dates = list(itertools.chain(*datesToFlatten))  # these are datetime.date() types

    years = np.unique(np.array([d.strftime("%Y") for d in Cluster_Result['Date']]))
    for y in years:
        st.subheader('Clustering Year ' + str(y))

        # plot the calendar heatmap of the cluster results with a slider to select to show just one cluster in case
        clusterIDheatmap = st.slider(
            'Select the cluster ID to be visualized on the calendar heatmap in Yellow (-1 for all of them)',
            min_value=-1, max_value=int(max(clusterSelection)), key='clusterIDheatmap'+measureType)

        all_days = pd.date_range(start='1/1/'+str(y), end='31/12/'+str(y), freq='D')

        clusterDF = pd.DataFrame([-np.Inf for d in all_days], columns=['ClusterID'], index=all_days)
        clusterDF['week'] = [d.isocalendar()[1] for d in all_days]
        clusterDF['weekday'] = [d.isocalendar()[2] for d in all_days]
        for d in dates:
            clustergroupvalue = Cluster_Result[Cluster_Result['Date'] == d]['ClusterGroup'].iloc[0]
            if clusterIDheatmap == -1:
                clusterDF.at[d, 'ClusterID'] = clustergroupvalue
            else:
                if clustergroupvalue == clusterIDheatmap:
                    clusterDF.at[d, 'ClusterID'] = clustergroupvalue
                else:
                    clusterDF.at[d, 'ClusterID'] = -1

        pivotClusterDF = clusterDF.pivot_table(index=clusterDF.columns[clusterDF.columns.get_loc('weekday')],
                                               columns=clusterDF.columns[clusterDF.columns.get_loc('week')],
                                               values=clusterDF.columns[clusterDF.columns.get_loc('ClusterID')])
        months = []
        for w in list(pivotClusterDF.columns):
            lastdayweek = pd.to_datetime(str(y)+str(w) + "6", format="%Y%U%w")
            months.append(lastdayweek.strftime("%B")+"-week_"+str(w))

        hoverDate = pd.DataFrame([d.strftime("%Y-%m-%d") for d in all_days], columns=['Date'])
        hoverDate['week'] = [d.isocalendar()[1] for d in all_days]
        hoverDate['weekday'] = [d.isocalendar()[2] for d in all_days]
        pivotHoverDate = hoverDate.pivot_table(index=hoverDate.columns[hoverDate.columns.get_loc('weekday')],
                                               columns=hoverDate.columns[hoverDate.columns.get_loc('week')],
                                               values=hoverDate.columns[hoverDate.columns.get_loc('Date')],
                                               aggfunc=lambda x: ' '.join(str(v) for v in x))

        fig = go.Figure(data=go.Heatmap(
            z=pivotClusterDF,
            x=months,
            y=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            hovertext=pivotHoverDate,
            colorscale='Viridis'))

        fig.update_layout(
            title=title,
            xaxis_nticks=14)

        st.plotly_chart(fig)
