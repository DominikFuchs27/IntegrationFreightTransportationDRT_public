route = 'KruFahrten_20200124_10_17.csv'
package_insertion = True        # Insert Packages [True/False]
scenario_load = "10M2"          # Demand Set
scenario_number = 1             # Desired Scenario (1,2,3)
number_runs = 10                # number of runs
number_iterations = 100         # number of iterations
predefined_no_busses = 3
degree_of_deconstruction = 0.15


separation = False              # Van carrying only packages (True) or DRT combining both (False)
weighing_operational = 5
weighing_service = 1
weighing_denied_requests = 500
VoT = 5/60                      # Value of time (5 Euro per h)
consumption_per_100_km = 11
cost_per_l = 1.3                # Cost per liter fuel
cost_driver = 200
CO2_emission_Bus = 200
CO2_emissions_Car = 150
Boarding_time_passenger = 1
Boarding_time_package = 2
Delivery_time_package = 3

