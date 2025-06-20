"""
Batch Run Results Visualization Script

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
import matplotlib.pylab as plb
import seaborn as sns

def plot_graphs(file_path,output_dir, group_num, columns_to_include,  x_label, y_label, legend_labels=None, legend_fontsize=None, line_thickness=1.5, 
                x_range=None, y_range=None, x_interval=None, y_interval=None, axis_label_size=12, tick_label_size=None, colors=None, plot_average=False, 
                include_std=False, plot_title=None, show_title=False, save_as=True):

    # Load data from the specified file
    df = pd.read_csv(file_path)

    # Select the columns associated with the specified group number
    if group_num < 0 or group_num >= len(columns_to_include):
        raise ValueError("Invalid group number. Please choose a valid group number.")
    
    selected_columns = columns_to_include[group_num]

    # Set plot style
    sns.set(style="white")
    plt.figure(figsize=(10, 6))

    # Melt the DataFrame for easier plotting with seaborn
    melted_df = df[selected_columns].melt(id_vars=[selected_columns[0]], var_name="Variable", value_name="Value")
    
    # Plotting the average and std (fill between)
    if plot_average:
        ax = sns.lineplot(
            data=melted_df, 
            x=selected_columns[0], 
            y="Value", 
            hue="Variable", 
            ci="sd" if include_std else None,  # Confidence interval (can use 'sd' for standard deviation) 
            linewidth=line_thickness,
            palette=colors[:len(selected_columns[1:])]  # Limit colors to number of lines being plotted
        )    
        sns.move_legend(ax, 'best', labels=legend_labels, title=None, frameon=True)
        plb.setp(ax.get_legend().get_texts(), fontsize=legend_fontsize) # for legend text
        
    # Set axis labels
    plt.xlabel(x_label, fontsize=axis_label_size)
    plt.ylabel(y_label, fontsize=axis_label_size)
    
    # Set title if enabled
    if show_title and plot_title:
        plt.title(plot_title, fontsize=axis_label_size + 2)  # Title font size can be slightly larger than axis label size

    # Set axis ranges if specified
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    # Set axis intervals if specified
    if x_interval:
        plt.xticks(range(int(x_range[0]), int(x_range[1]) + 1, x_interval), fontsize=tick_label_size)
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

file_path = "batchrun_results.csv"  
output_dir = "./graphs"  # Graphs will be saved here

columns_to_include = [
    ["Step", "Preflood_Non_Evacuation_Measure_Implemented", "Evacuated", "Duringflood_Coping_Action_Implemented", "Postflood_Adaptation_Measures_Planned"],
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


#=============================================================================#
"""
Use graph_options_for_batchrun.txt to plot the rest of graphs by replacing
line 119 to 134 
"""
#=============================================================================#

group_num = 0
x_label = "Days"
y_label = "Pecentage of population"
legend_labels = ["Pre-flood non-evacuation measures","Evacuations",  "During-flood coping actions", "Post-flood adaptation measures"]
legend_fontsize = '18'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.65)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = True
plot_title = "."
show_title = False
save_filename = "all_phases"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


group_num = 1
x_label = "Days"
y_label = "Pecentage of population"
legend_labels = ["Stranded", "Health-compromised", "Sheltered", "Hospitalized", "Deceased"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.3)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = True
plot_title = "."
show_title = False
save_filename = "persons_effects"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


group_num = 14
x_label = "Days"
y_label = "Proportion of flooded structures"
legend_labels = ["Homes", "Businesses", "Schools"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.8)
x_interval = 7
y_interval = 0.2
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = True
plot_title = "."
show_title = False
save_filename = "entity_effects"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


group_num = 15
x_label = "Days"
y_label = "Relative wealth growth"
legend_labels = ["Persons", "Businesses", "Shelter", "Healthcare", "Government"]
legend_fontsize = '17'
line_thickness = 4
x_range = (0, 38)
y_range = (-0.5, 0.5)
x_interval = 7
y_interval = 0.2
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = True
plot_title = "."
show_title = False
save_filename = "wealth_effects"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 2
x_label = "Days"
y_label = "Evacuated persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (high-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.5)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "evacuation_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 4
x_label = "Days"
y_label = "Stranded persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (high-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.3)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "stranded_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 6
x_label = "Days"
y_label = "Health-compromised persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (high-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.5)
x_interval = 7
y_interval = 0.1
axis_label_size = 20
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "injured_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 8
x_label = "Days"
y_label = "Hospitalized persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (high-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.5)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "hospitalized_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 10
x_label = "Days"
y_label = "Sheltered persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (High-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.5)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "sheltered_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 12
x_label = "Days"
y_label = "Deceased persons proportions"
legend_labels = ["High SES (low-vunerability)", "Low SES (High-vulnerability)"]
legend_fontsize = '22'
line_thickness = 4
x_range = (0, 38)
y_range = (0, 0.5)
x_interval = 7
y_interval = 0.1
axis_label_size = 22
tick_label_size = 18  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "deceased_vul"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 17
x_label = "Days"
y_label = "Proportion of high-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (7, 14.1)
y_range = (0, 0.2)
x_interval = 7
y_interval = 0.05
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "nonevac_high_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 16
x_label = "Days"
y_label = "Proportion of low-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (7, 14.1)
y_range = (0, 0.04)
x_interval = 7
y_interval = 0.025
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "nonevac_low_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 20                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of low-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (7, 24.1)
y_range = (0, 0.21)
x_interval = 7
y_interval = 0.07
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "evac_low_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 21                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of high-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (7, 24.1)
y_range = (0, 0.21)
x_interval = 7
y_interval = 0.07
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "evac_high_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 24                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of low-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (14, 24.1)
y_range = (0, 0.04)
x_interval = 7
y_interval = 0.01
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "during_low_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 25                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of high-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (14, 24.1)
y_range = (0, 0.08)
x_interval = 7
y_interval = 0.02
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "during_High_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 28                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of low-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (24, 38.2)
y_range = (0, 0.05)
x_interval = 7
y_interval = 0.01
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "post_low_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


#SES1
group_num = 29                       # Select the group number from columns_to_include
x_label = "Days"
y_label = "Proportion of high-vulnerability agents"
legend_labels = ["PMT",	"TPB", "SCT", "CRT"]
legend_fontsize = '22'
line_thickness = 4
x_range = (24, 38.2)
y_range = (0, 0.15)
x_interval = 7
y_interval = 0.05
axis_label_size = 22
tick_label_size = 22  # Set the tick label size here
colors = sns.color_palette("deep")  # Seaborn’s default color palette
plt_std = False
plot_title = "."
show_title = False
save_filename = "post_High_dec"  # Filename for the saved graph
# To plot the average with standard deviation fill
plot_graphs(file_path, output_dir, group_num, columns_to_include, x_label, y_label, legend_labels, legend_fontsize, 
            line_thickness, x_range, y_range, x_interval, y_interval, axis_label_size, tick_label_size, colors, 
            plot_average=True, include_std=plt_std, plot_title=plot_title, show_title=show_title, save_as=save_filename)


