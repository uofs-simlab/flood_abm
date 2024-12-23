"""
Batch Run Script

This script runs multiple simulations of the flood model with varying parameters 
to analyze the effects of different scenarios. It collects results and saves 
them to a CSV  file for further analysis.

Output:
Data saved in 'data_collection/batchrun_results.csv'.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.flood_model import FloodModel

from mesa.batchrunner import batch_run
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

import warnings
import time  # Import the time module
import psutil

# Suppress the specific FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")


    # Function to get memory and CPU usage
def get_resource_usage():
    process = psutil.Process()
    memory_usage = process.memory_info().rss / (1024 ** 2)  # Convert to MB
    cpu_usage = process.cpu_percent(interval=None)  # CPU usage as a percentage
    return memory_usage, cpu_usage


# =============================== BatchRun ================================

# Start the timer
start_time = time.time()

# Measure resource usage before the run
mem_before, cpu_before = get_resource_usage()
print(f"Memory usage before batch run: {mem_before:.2f} MB")
print(f"CPU usage before batch run: {cpu_before:.2f}%")

batch_run_params = {
    "N_persons": [500],
    "shelter_cap_limit": [1],
    "healthcare_cap_limit": [5],
    "shelter_funding": [50000],
    "healthcare_funding": [100000],
    "pre_flood_days": [14],
    "flood_days": [10],
    "post_flood_days": [14],
    "houses_file": "../calgary_map_data/houses.zip",
    "businesses_file": "../calgary_map_data/businesses.zip",
    "schools_file": "../calgary_map_data/schools.zip",
    "shelter_file": "../calgary_map_data/shelter.zip",
    "healthcare_file": "../calgary_map_data/healthcare.zip",
    "government_file": "../calgary_map_data/government.zip",
    "flood_file_1": "../calgary_map_data/flood1.zip",
    "flood_file_2": "../calgary_map_data/flood2.zip",
    "flood_file_3": "../calgary_map_data/flood3.zip",
    "model_crs": "EPSG:5070"
    }

num_iterations = 5

# Create and run the batch
results = batch_run(
    FloodModel, 
    batch_run_params, 
    iterations=num_iterations, 
    max_steps=24*38,  # Total number of steps the model will run in each iteration
    number_processes=1,  # Number of processes to use for parallel execution
    data_collection_period=1,  # Collect data at every step
    display_progress=True  # Display progress of the batch run
)
results_df = pd.DataFrame(results)

# Convert "Step" from hours to days
results_df["Step"] = results_df["Step"] / 24

# Define the path to the 'data_collection' folder
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_collection"))
os.makedirs(data_folder, exist_ok=True)  # Ensure the folder exists

# Define the full paths to the output files
csv_file_path = os.path.join(data_folder, "batchrun_results.csv")

# Save the results
results_df.to_csv(csv_file_path, index=False)  

# Specify the columns you want to include in the analysis
columns_to_include = [
    ["Step", "Evacuated", "Preflood_Non_Evacuation_Measure_Implemented", "Duringflood_Coping_Action_Implemented", "Postflood_Adaptation_Measures_Planned"],
    ["Step", "Stranded", "Injured", "Sheltered", "Hospitalized", "Death"],
    ["Step", "evacuated_SES_1_0_0.3", "evacuated_SES_1_0.7_1"],
    ["Step", "evacuated_SES_2_0_0.3", "evacuated_SES_2_0.7_1"],
    ["Step", "stranded_SES_1_0_0.3", "stranded_SES_1_0.7_1"],
    ["Step", "stranded_SES_2_0_0.3", "stranded_SES_2_0.7_1"],
    ["Step", "injured_SES_1_0_0.3", "injured_SES_1_0.7_1"],
    ["Step", "injured_SES_2_0_0.3", "injured_SES_2_0.7_1"],
    ["Step", "hospitalized_SES_1_0_0.3", "hospitalized_SES_1_0.7_1"],
    ["Step", "hospitalized_SES_2_0_0.3", "hospitalized_SES_2_0.7_1"],
    ["Step", "sheltered_SES_1_0_0.3", "sheltered_SES_1_0.7_1"],
    ["Step", "sheltered_SES_2_0_0.3", "sheltered_SES_2_0.7_1"],
    ["Step", "dead_SES_1_0_0.3", "dead_SES_1_0.7_1"],
    ["Step", "dead_SES_2_0_0.3", "dead_SES_2_0.7_1"],
    ["Step", "Houses_Flooded", "Businesses_Flooded", "Schools_Flooded"],
    ["Step", "Wealth_People", "Wealth_Businesses", "Wealth_Shelter", "Wealth_Healthcare", "Wealth_Government"],
    ["Step", "PMT_preflood_non_evacuation_measure_implemented_SES_1_0_0.3",	"TPB_preflood_non_evacuation_measure_implemented_SES_1_0_0.3", "SCT_preflood_non_evacuation_measure_implemented_SES_1_0_0.3",	"CRT_preflood_non_evacuation_measure_implemented_SES_1_0_0.3"],
    ["Step", "PMT_preflood_non_evacuation_measure_implemented_SES_1_0.7_1", "TPB_preflood_non_evacuation_measure_implemented_SES_1_0.7_1", "SCT_preflood_non_evacuation_measure_implemented_SES_1_0.7_1",	"CRT_preflood_non_evacuation_measure_implemented_SES_1_0.7_1"],
    ["Step", "PMT_preflood_non_evacuation_measure_implemented_SES_2_0_0.3",	"TPB_preflood_non_evacuation_measure_implemented_SES_2_0_0.3", "SCT_preflood_non_evacuation_measure_implemented_SES_2_0_0.3",	"CRT_preflood_non_evacuation_measure_implemented_SES_2_0_0.3"],
    ["Step", "PMT_preflood_non_evacuation_measure_implemented_SES_2_0.7_1", "TPB_preflood_non_evacuation_measure_implemented_SES_2_0.7_1", "SCT_preflood_non_evacuation_measure_implemented_SES_2_0.7_1",	"CRT_preflood_non_evacuation_measure_implemented_SES_2_0.7_1"],
    ["Step", "PMT_evacuation_SES_1_0_0.3", "TPB_evacuation_SES_1_0_0.3", "SCT_evacuation_SES_1_0_0.3",	"CRT_evacuation_SES_1_0_0.3"],
    ["Step", "PMT_evacuation_SES_1_0.7_1", "TPB_evacuation_SES_1_0.7_1", "SCT_evacuation_SES_1_0.7_1",	"CRT_evacuation_SES_1_0.7_1"],
    ["Step", "PMT_evacuation_SES_2_0_0.3", "TPB_evacuation_SES_2_0_0.3", "SCT_evacuation_SES_2_0_0.3",	"CRT_evacuation_SES_2_0_0.3"],
    ["Step", "PMT_evacuation_SES_2_0.7_1", "TPB_evacuation_SES_2_0.7_1", "SCT_evacuation_SES_2_0.7_1",	"CRT_evacuation_SES_2_0.7_1"],
    ["Step", "PMT_duringflood_coping_action_implemented_SES_1_0_0.3", "TPB_duringflood_coping_action_implemented_SES_1_0_0.3", "SCT_duringflood_coping_action_implemented_SES_1_0_0.3",	"CRT_duringflood_coping_action_implemented_SES_1_0_0.3"],
    ["Step", "PMT_duringflood_coping_action_implemented_SES_1_0.7_1", "TPB_duringflood_coping_action_implemented_SES_1_0.7_1", "SCT_duringflood_coping_action_implemented_SES_1_0.7_1",	"CRT_duringflood_coping_action_implemented_SES_1_0.7_1"],
    ["Step", "PMT_duringflood_coping_action_implemented_SES_2_0_0.3", "TPB_duringflood_coping_action_implemented_SES_2_0_0.3", "SCT_duringflood_coping_action_implemented_SES_2_0_0.3",	"CRT_duringflood_coping_action_implemented_SES_2_0_0.3"],
    ["Step", "PMT_duringflood_coping_action_implemented_SES_2_0.7_1", "TPB_duringflood_coping_action_implemented_SES_2_0.7_1", "SCT_duringflood_coping_action_implemented_SES_2_0.7_1",	"CRT_duringflood_coping_action_implemented_SES_2_0.7_1"],
    ["Step", "PMT_postflood_adaptation_measures_planned_SES_1_0_0.3", "TPB_postflood_adaptation_measures_planned_SES_1_0_0.3", "SCT_postflood_adaptation_measures_planned_SES_1_0_0.3",	"CRT_postflood_adaptation_measures_planned_SES_1_0_0.3"],
    ["Step", "PMT_postflood_adaptation_measures_planned_SES_1_0.7_1", "TPB_postflood_adaptation_measures_planned_SES_1_0.7_1", "SCT_postflood_adaptation_measures_planned_SES_1_0.7_1",	"CRT_postflood_adaptation_measures_planned_SES_1_0.7_1"],
    ["Step", "PMT_postflood_adaptation_measures_planned_SES_2_0_0.3", "TPB_postflood_adaptation_measures_planned_SES_2_0_0.3", "SCT_postflood_adaptation_measures_planned_SES_2_0_0.3",	"CRT_postflood_adaptation_measures_planned_SES_2_0_0.3"],
    ["Step", "PMT_postflood_adaptation_measures_planned_SES_2_0.7_1", "TPB_postflood_adaptation_measures_planned_SES_2_0.7_1", "SCT_postflood_adaptation_measures_planned_SES_2_0.7_1",	"CRT_postflood_adaptation_measures_planned_SES_2_0.7_1"]
]

#======================== Plot batch run results =========================#
# Filter only the numeric columns and group by the "Step" column
for i, group_columns in enumerate(columns_to_include):
    numeric_data = results_df[group_columns].select_dtypes(include='number')

    # Replace infinite values with NaN
    numeric_data.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Group by the "Step" column
    grouped_data = numeric_data.groupby("Step")
    
    # Calculate the mean, minimum, and maximum for each group
    average_data = grouped_data.mean()
    std_data = grouped_data.std()
    
    # Define the x-tick intervals (every 7 days)
    xticks = np.arange(0, max(average_data.index) + 1, 7)
    
    # Create a lineplot with error bars for each column in the group
    plt.figure(figsize=(10, 6))
    for column in group_columns[1:]:
        g = sns.lineplot(
            data=average_data,
            x="Step",
            y=column,
            label=column,
        )
        # Fill between the mean +/- standard deviation
        plt.fill_between(average_data.index, average_data[column] - std_data[column], average_data[column] + std_data[column], alpha=0.2)
                
    # plt.title(f"Group {i+1}")
    plt.xlabel("Days")
    plt.xticks(xticks)  # Set x-axis to display ticks every 7 days
    plt.legend()
    plt.show()  
    
    # Create a lineplot without error bars for each column in the group
    plt.figure(figsize=(10, 6))
    for column in group_columns[1:]:
        g = sns.lineplot(
            data=average_data,
            x="Step",
            y=column,
            label=column,
        )
                    
    # plt.title(f"Group {i+1}")
    plt.xlabel("Days")
    plt.xticks(xticks)  # Set x-axis to display ticks every 7 days
    plt.legend()
    plt.show()   
    
# Measure resource usage after the run
mem_after, cpu_after = get_resource_usage()
print(f"Memory usage after batch run: {mem_after:.2f} MB")
print(f"CPU usage after batch run: {cpu_after:.2f}%")
  
# Elapsed time calculation
end_time = time.time()
elapsed_time = (end_time - start_time) / 60
print(f"Batch run completed in {elapsed_time:.2f} minutes.")
print(f"Total memory used: {mem_after - mem_before:.2f} MB")   