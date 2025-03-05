"""
Batch Run Results Visualization Script for scenario testing.

This script generates line plots from simulation data stored in a CSV file. 
It allows users to analyze trends in agent behaviors, decisions, and states 
over simulation time steps. The script supports customization of plot appearance, 
including axis labels, legends, and color schemes.

Images are saved in graphs directory
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_graphs(file_path, metric, x_label, y_label, legend_labels=None, legend_fontsize=None, line_thickness=1.5, 
                x_range=None, y_range=None, x_interval=None, y_interval=None, axis_label_size=12, tick_label_size=None, colors=None, 
                plot_average=False, include_std=False, plot_title=None, show_title=False, show_legend=True, save_as=True):

    # Load data from the specified file
    df = pd.read_csv(file_path)

    # Ensure the required columns are present in the dataframe
    selected_columns = ['shelter_cap_limit', metric]
    if not all(col in df.columns for col in selected_columns):
        raise ValueError(f"Required columns {selected_columns} not found in the dataset.")

    # Set plot style
    sns.set(style="white")
    plt.figure(figsize=(10, 6))

    # If plot_average is True, group by 'shelter_cap_limit' and calculate the mean and std
    if plot_average:
        # Group data by 'shelter_cap_limit' and calculate mean and std
        grouped_data = df.groupby('shelter_cap_limit')[metric].agg(['mean', 'std']).reset_index()

        # Plot the mean
        ax = sns.lineplot(
            x=grouped_data['shelter_cap_limit'], 
            y=grouped_data['mean'], 
            linewidth=line_thickness, 
            palette=colors[:1]
        )

        # Optionally include standard deviation as shading
        if include_std:
            plt.fill_between(grouped_data['shelter_cap_limit'], 
                             grouped_data['mean'] - grouped_data['std'], 
                             grouped_data['mean'] + grouped_data['std'], 
                             color=colors[0], alpha=0.3)

    # Set legend if provided and show_legend is True
    if legend_labels and show_legend:
        ax.legend(labels=legend_labels, fontsize=legend_fontsize)

    # Set axis labels
    plt.xlabel(x_label, fontsize=axis_label_size)
    plt.ylabel(y_label, fontsize=axis_label_size)

    # Set title if enabled
    if show_title and plot_title:
        plt.title(plot_title, fontsize=axis_label_size + 1)

    # Set axis ranges if specified
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    # Set x-axis intervals if specified
    if x_interval:
        plt.xticks(np.arange(x_range[0], x_range[1] + x_interval, x_interval), fontsize=tick_label_size)

    # Set y-axis intervals using np.arange similar to x-axis
    if y_interval:
        plt.yticks(np.arange(y_range[0], y_range[1] + y_interval, y_interval), fontsize=tick_label_size)

    plt.grid(False)
    plt.tight_layout()
    # Save the plot
    if save_as:
        os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
        save_path = os.path.join(output_dir, save_as)
        plt.savefig(save_path)
        print(f"Graph saved to: {save_path}")
        
    plt.show()


results_df = pd.read_csv("scenario_results_batchrun.csv")

# List of metrics to analyze (from your original code)
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
    "dead_total_pop_SES_2_0_0.3", "dead_total_pop_SES_2_0.7_1"
]

# Initialize avg_max_metrics DataFrame
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
        
avg_max_metrics.to_csv("scenario_shelter_vs_categories.csv", index=False)

# Example usage with avg_max_metrics file
file_path = "scenario_shelter_vs_categories.csv"  
output_dir = "./graphs"  # Graphs will be saved here

# ======================  Define plot parameters ==============================

# hospitalized
metric = "avg_max_hospitalized_total_pop_SES_1_0.7_1"  # Specify the metric you want to plot
x_label = "Shelter capacity limit"
y_label = "Population proportions"
legend_labels = ["Stranded SES 1"]
legend_fontsize = 22
line_thickness = 4
x_range = (0.5, 5)  # Adjust based on your data
y_range = (0.002, 0.012)  # Adjust based on your data
x_interval = 0.5
y_interval = 0.002
axis_label_size = 22
tick_label_size = 22
colors = sns.color_palette("deep")
plot_title = "Hospitalized persons (high-vulnerability) vs shelter capacity"
show_title = False
show_legend = False  # Change to True to show legend
save_filename = "hospitalized_shelcap"

# Call the function
plot_graphs(file_path, metric, x_label, y_label, legend_labels, legend_fontsize, line_thickness, 
            x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=False, plot_title=plot_title, show_title=show_title, show_legend=show_legend, save_as=save_filename)


# Injured
metric = "avg_max_injured_total_pop_SES_1_0.7_1"  # Specify the metric you want to plot
x_label = "Shelter capacity limit"
y_label = "Population proportions"
legend_labels = ["Stranded SES 1"]
legend_fontsize = 22
line_thickness = 4
x_range = (0.5, 5)  # Adjust based on your data
y_range = (0.005, 0.03)  # Adjust based on your data
x_interval = 0.5
y_interval = 0.005
axis_label_size = 22
tick_label_size = 22
colors = sns.color_palette("deep")
plot_title = "Health-compromised (high-vulnerability) vs shelter capacity"
show_title = False
show_legend = False  # Change to True to show legend
save_filename = "injured_shelcap"

plot_graphs(file_path, metric, x_label, y_label, legend_labels, legend_fontsize, line_thickness, 
            x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=False, plot_title=plot_title, show_title=show_title, show_legend=show_legend, save_as=save_filename)

# Sheltered
metric = "avg_max_sheltered_total_pop_SES_1_0.7_1"  # Specify the metric you want to plot
x_label = "Shelter capacity limit"
y_label = "Population proportions"
legend_labels = ["Stranded SES 1"]
legend_fontsize = 22
line_thickness = 4
x_range = (0.5, 5)  # Adjust based on your data
y_range = (0.0, 0.02)  # Adjust based on your data
x_interval = 0.5
y_interval = 0.004
axis_label_size = 22
tick_label_size = 22
colors = sns.color_palette("deep")
plot_title = "Sheltered persons (high-vulnerability) vs shelter capacity"
show_title = False
show_legend = False  # Change to True to show legend
save_filename = "sheltered_shelcap"

plot_graphs(file_path, metric, x_label, y_label, legend_labels, legend_fontsize, line_thickness, 
            x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=False, plot_title=plot_title, show_title=show_title, show_legend=show_legend, save_as=save_filename)

# stranded
metric = "avg_max_stranded_total_pop_SES_1_0.7_1"  # Specify the metric you want to plot
x_label = "Shelter capacity limit"
y_label = "Population proportions"
legend_labels = ["Stranded SES 1"]
legend_fontsize = 22
line_thickness = 4
x_range = (0.5, 5)  # Adjust based on your data
y_range = (0.035, 0.055)  # Adjust based on your data
x_interval = 0.5
y_interval = 0.005
axis_label_size = 22
tick_label_size = 22
colors = sns.color_palette("deep")
plot_title = "Stranded persons (high-vulnerability) vs shelter capacity"
show_title = False
show_legend = False  # Change to True to show legend
save_filename = "stranded_shelcap"

plot_graphs(file_path, metric, x_label, y_label, legend_labels, legend_fontsize, line_thickness, 
            x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=False, plot_title=plot_title, show_title=show_title, show_legend=show_legend, save_as=save_filename)