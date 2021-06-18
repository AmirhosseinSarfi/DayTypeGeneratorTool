# Day-Type Generator
A data driven tool for:
 * Performing Statistical Data Analysis of flow/speed profiles,
 * Clustering flow/speed time profiles of individual detectors,
 * Defining network-wide Day-Types using cluster results on individual detectors

Keep in mind that today you are allowed to run the tool against CSV like data, but 
more important, remind that the profile data must be temporally equi-spaced within a day and 
all them must have the same time discretization. Running the tool via web-app
you will be able to see several charts and evaluate on the fly how the results are, 
how the data themselves are, you can fine tune easily the tool options and check 
if you are getting better of worst results thanks to the plots and the KPIs 
shown. 

If you run the tool not via the web-app, but in batch via for example the JSON 
configuration file, you will get only the final CSV results for the clustering and 
day-types (if you asked for them ;-)). These results are clearly produced also 
if you run the tool via web-app, and you can find them into the folder "Results" 
of the tool. In total you can find 4 files

1. Individual_Cluster_Results.csv
2. Individual_Cluster_KPIs.csv
3. Network_Cluster_Results.csv
4. Network_Cluster_KPIs.csv
 
The header of each of this files should be self-explaining in describing which kind 
of data you have into the file. 

**Individual_Cluster_Results**
````shell script
KeyID, ClusterGroup, Date, WeekDay, Month
````

**Individual_Cluster_KPIs**
````shell script
KeyID, MAE, MAPE, MSE, RMSE
````

**Network_Cluster_Results**

Here are defined the day-types. Each cluster group is a day-type.
````shell script
ClusterGroup, Date, WeekDay, Month
````

**Network_Cluster_KPIs**

Here 3 KPIs are reported for evaluating the goodness of the network clustering,
so that varying the number of the day-types you like to have, you can find 
the best compromise between such number a good values of that KPIs:
* Silhoutte
* Calinski-Harabasz
* Davies-Bouldin
````shell script
KPI, Value, Description
````

## How to install
* Install Anaconda (Individual Edition from https://www.anaconda.com/)

* Open Anaconda Prompt shell as admin

![anaconda_prompt](docs\pictures\anaconda_prompt.png)

* Place the tool folder where you like (for example "C:\dev\DayTypeGenerator") 
and locate yourself there by the Anaconda Prompt shell.

* Create the new virtual environment for such tool, (it will be named 
DayTypeGenerator):
    ```shell script
    conda env create -f environment.yml
    ```
   It will be created usually under "C:\ProgramData\Anaconda3\envs"
   
* Activate the virtual environment: 
    ```shell script
    conda activate DayTypeGenerator
    ```

## How to use
You can run the tool by one of the following ways:
1. Command Line Specifying Single Options
2. Command Line Specifying a Configuration File
3. Run via GUI with Streamlit (c)

#### Option 1. Command Line Specifying Single Options
Open your shell and run the following command
````shell script
python DayTypeGenerator [--options]
````
Keep in mind that you must provide several options as described in the configuration section.

#### Option 2. Command Line Specifying a Configuration File
```shell script
python DayTypeGenerator --conf DefaultConfigFile.json
```
Keep in mind that the configuration file in JSON format must respect the rules reported 
into the configuration section. 

#### Option 3. Run via GUI with Streamlit (c)
This option gave the possibility of setting configuration parameters and tracking results in a user-friendly web-app format. 
<br> To use this option open your shell and run the following command:
```shell script
streamlit run DayTypeGenerator\__main__.py -- --GUI True 
```
## Configuration Options
The configuration options of the tool are reported below, where for each bullet point 
is reported the name of the option, its type, its default value, and a minimal description 
aimed to explain for what the option is needed. 
An example of JSON configuration file is found into the "conf/" folder of the tool.

 * **inputFile** 
 <br> **DataType:** String  
**Default:** None 
 <br>Filename, inclusive of its extension, of the file containing the data. Provide it
 with the absolute or relative filepath.  
 <br>***Note:** If you put it into the "data" folder of the tool, you can write for example:* 
````shell script
.\data\my_input.csv
````
 * **compression** 
<br>**DataType:** String
<br>**Default:** None
<br> Defining the file compression type. 
<br> ***Note1:** The supported formats are: *'zip'*, *'gzip'*, *'bz2'*, *'xz'.** 
<br>***Note2:** If using *compressed* format, it has to contain only one input data file.*

 * **format** 
<br>**DataType:** String
<br>**Default:** csv
<br> Defining the input file format.
<br> ***Note:** Tool supports only CSV format*

 * **fileSeparator** 
<br>**DataType:** String 
<br>**Default:** ","
<br> Defining the separator of values in input file.
<br> ***Note** The supported separators are *","* or *";"* or *"|"**

 * **header** 
<br>**DataType:** Boolean 
<br>**Default:** False
<br> Specifying whether the input file has a header line or not.

 * **TimeResolution** 
<br>**DataType:**  Integer
<br>**Default:** 15
<br> Defining time interval between two consecutive recorded data in minutes. 

 * **ID1** 
<br>**DataType:** Integer
<br>**Default:** -1 
<br> Defining the column index (zero-based) containing the identifier of the detector.
<br> ***Note:** This value is mandatory*

 * **ID2** 
<br>**DataType:** Integer
<br>**Default:** -1 
<br> Defining the column index (zero-based) containing the second part 
of the identifier of the detector. 
<br> ***Note:** This value is optional and it is used in case of time series with keys 
formed by two values (e.g. link objects of a graph)*

 * **timestamp** 
<br>**DataType:** Integer
<br>**Default:** -1 
<br> Defining the column index (zero-based) containing timestamp information. 
<br> ***Note:** this value is mandatory*

 * **flow** 
<br>**DataType:** Integer
<br>**Default:** -1 
<br> Defining the column index (zero-based) containing flow information. 

 * **speed** 
<br>**DataType:** Integer
<br>**Default:** -1 
<br> Defining the column index (zero-based) containing speed information. 

 * **flowFactor** 
<br>**DataType:** Float
<br>**Default:** 1 
<br> A conversion factor in order to transform the input flow in "Vehicle/hour"  

 * **speedFactor** 
<br>**DataType:** Float
<br>**Default:** 1 
<br> A conversion factor in order to transform the input speed in "Km/hour"  

 * **keepFlowZero** 
<br>**DataType:** Boolean
<br>**Default:** True
<br> Specify if you want to trash or not flow values exactly equal to zero
 
 * **keepSpeedZero** 
<br>**DataType:** Boolean
<br>**Default:** True
<br> Specify if you want to trash or not speed values exactly equal to zero

 * **flowThreshold** 
<br>**DataType:** Float
<br>**Default:** 100.0 
<br> Define a percentage threshold for the overall cumulative distribution of the flow data
such that flow values falling into the right tail of the distribution above such 
threshold are trashed (considered outliers)

 * **speedThreshold** 
<br>**DataType:** Float
<br>**Default:** 100.0 
<br> Define a percentage threshold for the overall cumulative distribution of the speed data
such that speed values falling into the right tail of the distribution above such 
threshold are trashed (considered outliers)

 * **maximumMissingPercentageFlow** 
<br>**DataType:** Float
<br>**Default:** 100.0 
<br> A percentage threshold to set the maximum amount of missing data on flow you would like 
to handle. The higher the value the more missing data into your profiles you are 
accepting. Usually it is better to have profiles with not so many missing data. 

 * **maximumMissingPercentageSpeed** 
<br>**DataType:** Float
<br>**Default:** 100.0 
<br>  A percentage threshold to set the maximum amount of missing data on speed you would like 
to handle. The higher the value the more missing data into your profiles you are 
accepting. Usually it is better to have profiles with not so many missing data. 

 * **smoothingKernelPercentage** 
<br>**DataType:** Float
<br>**Default:** 10.0 
<br> A percentage of the maximum total data a profile could have, in order to perform
a triangular smoothing of the input profiles.  
<br>*Note: based on the experience the best value is between 10% to 12%.*

 * **enableProfileClustering** 
<br>**DataType:** Boolean
<br>**Default:** False
<br> Enable clustering over individual detectors. 

 * **enableNetworkClustering** 
<br>**DataType:** Boolean
<br>**Default:** False
<br> Enable network-wide clustering for day-type definition  

 * **KmeansNumberOfFlowCluster** 
<br>**DataType:** Integer
<br>**Default:** 12
<br> Number of day-types you want based of flow data (used K-means clustering algorithm)  

 * **KmeansNumberOfSpeedCluster** 
<br>**DataType:** Integer
<br>**Default:** 12
<br> Number of day-types you want based on speed data (K-means clustering algorithm)

## Run tests
To-Be-Done