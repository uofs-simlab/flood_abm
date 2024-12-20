"""
Scenario Test Batch Run Script

This script runs test scenarios of the flood model to evaluate 
and compare outcomes. 

Output:
- Data saved in 'data_collection/scenario_results.csv'.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from model.flood_model import FloodModel

from mesa.batchrunner import batch_run
import matplotlib.pyplot as plt
import seaborn as sns
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

# =============================== BatchRun ====================================

# Start the timer
start_time = time.time()

# Measure resource usage before the run
mem_before, cpu_before = get_resource_usage()
print(f"Memory usage before batch run: {mem_before:.2f} MB")
print(f"CPU usage before batch run: {cpu_before:.2f}%")

batch_run_params = {
    "N_persons": [500],
    "shelter_cap_limit": [0.5, 1, 1.5, 2 , 2.5, 3, 3.5, 4, 4.5, 5],
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
    max_steps=24 * 38,  # Total number of steps the model will run in each iteration
    number_processes=1,  # Number of processes to use for parallel execution
    data_collection_period=1,  # Collect data at every step
    display_progress=True  # Display progress of the batch run
)

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Convert "Step" from hours to days
results_df["Step"] = results_df["Step"] / 24

# List of metrics to analyze (excluding "Step")
metrics_to_analyze = [
    "evacuated_total_pop_SES_1_0_0.3", "evacuated_total_pop_SES_1_0.7_1",
    "evacuated_total_pop_SES_2_0_0.3", "evacuated_total_pop_SES_2_0.7_1",
    "stranded_total_pop_SES_1_0_0.3", "stranded_total_pop_SES_1_0.7_1",
    "stranded_total_pop_SES_2_0_0.3", "stranded_total_pop_SES_2_0.7_1",
    "injured_total_pop_SES_1_0_0.3", "injured_total_pop_SES_1_0.7_1",
    "injured_total_pop_SES_2_0_0.3", "injured_total_pop_SES_2_0.7_1",
    "hospitalized_total_pop_SES_1_0_0.3", "hospitalized_total_pop_SES_1_0.7_1",
    "hospitalized_total_pop_SES_2_0_0.3", "hospitalized_total_pop_SES_2_0.7_1",
    "sheltered_total_pop_SES_1_0_0.3", "sheltered_total_pop_SES_1_0.7_1",
    "sheltered_total_pop_SES_2_0_0.3", "sheltered_total_pop_SES_2_0.7_1",
    "dead_total_pop_SES_1_0_0.3", "dead_total_pop_SES_1_0.7_1",
    "dead_total_pop_SES_2_0_0.3", "dead_total_pop_SES_2_0.7_1",
]

avg_max_metrics = pd.DataFrame(columns=['shelter_cap_limit'])

# Calculate average maximums for each metric
for metric in metrics_to_analyze:
    max_values = results_df.groupby(['shelter_cap_limit', 'iteration'])[metric].max().reset_index()
    avg_max = max_values.groupby('shelter_cap_limit')[metric].mean().reset_index()
    avg_max.columns = ['shelter_cap_limit', f'avg_max_{metric}']

    # Merge the results into the final DataFrame
    if avg_max_metrics.empty:
        avg_max_metrics = avg_max
    else:
        avg_max_metrics = pd.merge(avg_max_metrics, avg_max, on='shelter_cap_limit', how='outer')


# Merge avg_max_metrics with the original results DataFrame if you want to keep all data
results_df = pd.merge(results_df, avg_max_metrics, on='shelter_cap_limit', how='left')

# Define the path to the 'data_collection' folder
data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_collection"))
os.makedirs(data_folder, exist_ok=True)  # Ensure the folder exists

# Define the full paths to the output files
csv_file_path = os.path.join(data_folder, "scenario_results_batchrun.csv")
# pkl_file_path = os.path.join(data_folder, "scenario_results_batchrun.pkl")

# Save the results
results_df.to_csv(csv_file_path, index=False)  # Save as CSV
# results_df.to_pickle(pkl_file_path)  # Save as Pickle

# Plot average maximum metrics for each shelter capacity limit
sns.set(style="whitegrid")  # Using seaborn style

# Iterate through each metric to create individual plots
for metric in metrics_to_analyze:
    plt.figure(figsize=(8, 6))  # Create a new figure for each metric
    sns.lineplot(data=avg_max_metrics, x='shelter_cap_limit', y=f'avg_max_{metric}', marker='o')
    plt.xlabel('Shelter Capacity Limit')
    plt.ylabel(f'Average Maximum {metric}')
    plt.title(f'Average Maximum {metric} vs Shelter Capacity Limit')
    plt.grid(True)
    plt.tight_layout()  # Ensure the layout is tight for each figure
    plt.show()  # Display each figure individually

# Measure resource usage after the run
mem_after, cpu_after = get_resource_usage()
print(f"Memory usage after batch run: {mem_after:.2f} MB")
print(f"CPU usage after batch run: {cpu_after:.2f}%")
print(f"Total memory increase during batch run: {mem_after - mem_before:.2f} MB")

# Elapsed time calculation
end_time = time.time()
elapsed_time = (end_time - start_time) / 60
print(f"Batch run completed in {elapsed_time:.2f} minutes.")