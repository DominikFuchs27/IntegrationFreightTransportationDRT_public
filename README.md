This is the code used in the Master Thesis “Integration of freight transporation in Demand Responsive Transport system” by Dominik Fuchs. 
Because the input data consists of .csv files with sensitive data (e.g. names of passengers) the code can be observed but does not run. 
For further information, feel free to contact me: dominikfuchs@t-online.de

---- Functions ----- 

ALNS_Sub_Parallel: Inserts a set of removed nodes into a route at the best-cost position considering time-constraints and capacity

CallMatrix: Calls the csv-files with durations and distances of the used nodes

DemandSets: All in the thesis described demand sets with origin, destination, arrival and departure times

GetMatrizes: Returns the distance (GetDistance) or duration (GetDuration) of a specific origin-destination pair

HelpingFunctions: Set of various Functions required for specific tasks

Insertion_Operations: Calls the next insertion heuristic for this iteration

  ALNS_parallel: Basic Greedy Insertion Heuristic
  
  ALNS_Regret: Regret-2-Insertion Heuristic
  
  ALNS_Regret3: Regret-3-Insertion Heurstic. Only used, if number of busses >= 3

Parameters: Set of Parameters to specify the model (e.g. input, scenario)

Removal_Operations: Calls the next removal heuristic for this iteration
   Testing_RandomRemvoval: Randomly removes a set of requests from the current route
	
   Testing_Relatedeness: Removes a related set of requests according to the Shaw Removal
	
   Testing_WorstRemoval: Removes the worst requests from the current route
	
Route: Class for inserting a new route 

Testing_DataFLEXIBUS: Transforms the input data into parameters, which can be used by the code. Calculation of time-windows for the original data

Testing_Time: Functions for defining time-windows

Testing_NewSchedule: Calculates a schedule for the inserted route

Test_Graph: Main function to run the code

----- Output --------

Printed attributes
-	IVT: list of in-vehicle time of best route of all runs
-	WT: list of waiting time of best route of all runs
-	OC: list of operational costs of best route for all runs
-	SC: list of user (service) costs of best route for all runs
-	DIST: list of distance of best route for all runs
-	CO2: list of CO2 emissions of best route for all runs
-	BS: list of overall costs of best route for all runs

Figures
-	Figure 1: Shows best costs of all runs
-	Figure 2: Shows progress of the current route for routes of all runs
-	Figure 3: Shows the operational cost of the best route for all runs
-	Figure 4: Shows the user cost of the best route for all runs
-	Figure 5: Shows comparison between operational costs and user costs as well as between best costs and progress of the current costs for the last run

CSV-File

Number of CSV files depends on the number of runs. Every csv file stores the best result for one run. Every File has information about

-	Sequence of nodes for each route
-	Schedule calculated by the model (in minutes)
-	Actual Schedule
-	Denied nodes: Nodes, which are in the sequence but time-constraints are not hold
-	Unfitting nodes: Nodes, which are not included in any route 
