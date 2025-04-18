"""
Server Run Script

This script launches an interactive visualization of the flood model, 
allowing real-time observation of agent behaviors, decisions, and flood impacts 
through a web interface.

Output:
Interactive visualization accessible via a web browser and data saved in 
  data_collection/serverrun_results.csv
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import agents.flood_agents as FA
from model.flood_model import FloodModel
from space.flood_space import FloodArea

import mesa_geo as mg
from mesa.visualization import ModularServer
from mesa.visualization.modules import ChartModule, TextElement
from mesa.visualization import Slider

import warnings
import psutil

# Suppress the specific FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning, module="seaborn")

# Function to get memory and CPU usage
def get_resource_usage():
    process = psutil.Process()
    memory_usage = process.memory_info().rss / (1024 ** 2)  # Convert to MB
    cpu_usage = process.cpu_percent(interval=None)  # CPU usage as a percentage
    return memory_usage, cpu_usage

#========================== Launch to server observe ======================

# Define portrayal dictionary for different agents
def agent_portrayal(agent):
    portrayal = {}

    # Custom portrayal for specific conditions
    if isinstance(agent, FA.Person_Agent):
        portrayal["color"] = "Green"
        portrayal["radius"] = "1"
        portrayal["fillOpacity"] = 1
        
        if agent.stranded:
            portrayal["color"] = "Red"
        elif not agent.alive:
            portrayal["color"] = "Black"
        elif agent.injured:
            portrayal["color"] = "Orange"
            
    elif isinstance(agent, FloodArea):
        portrayal["color"] = "Cyan"
        
    elif isinstance(agent, FA.Business_Agent):
        portrayal["color"] = "Purple"

    elif isinstance(agent, FA.House_Agent):
        portrayal["color"] = "Grey"
    
    elif isinstance(agent, FA.School_Agent):
        portrayal["color"] = "Yellow"
    
    elif isinstance(agent, FA.Shelter_Agent):
        portrayal["color"] = "Blue"
    
    elif isinstance(agent, FA.Healthcare_Agent):
        portrayal["color"] = "Orange"
    
    elif isinstance(agent, FA.Government_Agent):
        portrayal["color"] = "Magenta"   
    
    return portrayal


class colorLegend(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        # Define the legend content based on the agent portrayal colors and conditions
        legend = "<div style='position: absolute; right: 50px; top: 150px; font-size: 17px;'>"
        legend += "<strong>Legend:</strong><br>"
        legend += "<span style='color: green;'>&#9679; Green: Person<br>"
        legend += "<span style='color: red;'>&#9679; Red: Stranded Person<br>"
        legend += "<span style='color: orange;'>&#9679; Orange: Health-compromised<br>"
        legend += "<span style='color: black;'>&#9679; Deceased Person<br>"
        legend += "<span style='color: purple;'>&#9679; Purple: Business<br>"
        legend += "<span style='color: grey;'>&#9679; Yellow: School<br>"
        legend += "<span style='color: brown;'>&#9679; Brown: House<br>"
        legend += "<span style='color: magenta;'>&#9679; Magenta: Government<br>"
        legend += "<span style='color: blue;'>&#9679; Blue: Shelter<br>"
        legend += "<span style='color: orange;'>&#9679; Orange: Healthcare<br>"
        legend += "<span style='color: cyan;'>&#9679; Cyan: Flood Inundation<br>"
        legend += "</div>"      
        return legend

model_params = {
    "N_persons": Slider("Number of persons", 300, 10, 1500, 10), #ini,min,max,stp
    "shelter_cap_limit": Slider("Shelter Capacity(% of pop.)", 1, 0, 10, 0.3),
    "healthcare_cap_limit": Slider("Healthcare Capacity(% of pop.)", 5, 0, 10, 1),
    "shelter_funding": Slider("Shelter funds $", 50000, 5000, 200000, 5000),
    "healthcare_funding": Slider("Healthcare funds $", 100000, 50000, 500000, 10000),
    "pre_flood_days": Slider("Pre Flood Days", 8, 0, 90, 1),
    "flood_days": Slider("Flood Days", 10, 3, 30, 1),
    "post_flood_days": Slider("Post Flood Days", 14, 0, 90, 1),
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

# Create a canvas grid with given portrayal function and agent dimensions
map_element = mg.visualization.MapModule(agent_portrayal, map_height=500, map_width=860)
# map_element = MapModule(agent_portrayal, map_height=500, map_width=860)

# Add the legend to the visualization
legend = colorLegend()

#---------------------- SES index data visuals-----------------------------
# Define a function to create SES-specific chart modules for decision-making phases
def create_ses_charts(decision, ses_ranges):
    charts = []
    for ses_range in ses_ranges:
        charts.append(
            ChartModule([
                {"Label": f"PMT_{decision}_{ses_range}", "Color": "blue"},
                {"Label": f"TPB_{decision}_{ses_range}", "Color": "green"},
                {"Label": f"SCT_{decision}_{ses_range}", "Color": "orange"},
                {"Label": f"CRT_{decision}_{ses_range}", "Color": "red"}
            ])
        )
    return charts

# Define SES ranges and their corresponding colors for each index
ses_index_1_ranges = ['SES_1_0_0.3', 'SES_1_0.7_1']
ses_index_2_ranges = ['SES_2_0_0.3', 'SES_2_0.7_1']
all_ses_ranges = ses_index_1_ranges + ses_index_2_ranges
ses_index_1_colors = ['green', 'red']
ses_index_2_colors = ['blue', 'magenta']

# Create SES-specific charts for decision phases
preflood_non_evacuation_charts = create_ses_charts("preflood_non_evacuation_measure_implemented", all_ses_ranges)
evacuation_charts = create_ses_charts("evacuation", all_ses_ranges)
duringflood_coping_charts = create_ses_charts("duringflood_coping_action_implemented", all_ses_ranges)
postflood_recovery_charts = create_ses_charts("postflood_adaptation_measures_planned", all_ses_ranges)

# Define a function to create grouped SES charts for a given metric (e.g., Evacuated, Stranded)
def create_grouped_ses_charts(metric, ses_ranges, colors):
    return ChartModule([
        {"Label": f"{metric}_{ses_range}", "Color": color} for ses_range, color in zip(ses_ranges, colors)
    ])

# Create grouped charts for selected SES-based metrics for index 1 and index 2 separately
evacuated_chart_ses_1 = create_grouped_ses_charts("evacuated", ses_index_1_ranges, ses_index_1_colors)
evacuated_chart_ses_2 = create_grouped_ses_charts("evacuated", ses_index_2_ranges, ses_index_2_colors)

stranded_chart_ses_1 = create_grouped_ses_charts("stranded", ses_index_1_ranges, ses_index_1_colors)
stranded_chart_ses_2 = create_grouped_ses_charts("stranded", ses_index_2_ranges, ses_index_2_colors)

injured_chart_ses_1 = create_grouped_ses_charts("injured", ses_index_1_ranges, ses_index_1_colors)
injured_chart_ses_2 = create_grouped_ses_charts("injured", ses_index_2_ranges, ses_index_2_colors)

sheltered_chart_ses_1 = create_grouped_ses_charts("sheltered", ses_index_1_ranges, ses_index_1_colors)
sheltered_chart_ses_2 = create_grouped_ses_charts("sheltered", ses_index_2_ranges, ses_index_2_colors)

hospitalized_chart_ses_1 = create_grouped_ses_charts("hospitalized", ses_index_1_ranges, ses_index_1_colors)
hospitalized_chart_ses_2 = create_grouped_ses_charts("hospitalized", ses_index_2_ranges, ses_index_2_colors)

dead_chart_ses_1 = create_grouped_ses_charts("dead", ses_index_1_ranges, ses_index_1_colors)
dead_chart_ses_2 = create_grouped_ses_charts("dead", ses_index_2_ranges, ses_index_2_colors)

# General charts (not SES-specific)
persons_chart = ChartModule([
    {"Label": "Stranded", "Color": "red"},
    {"Label": "Health-compromised", "Color": "orange"},
    {"Label": "Sheltered", "Color": "blue"},
    {"Label": "Hospitalized", "Color": "grey"},
    {"Label": "Death", "Color": "black"}
])

decisions_chart = ChartModule([
    {"Label": "Preflood_Non_Evacuation_Measure_Implemented", "Color": "orange"},
    {"Label": "Evacuated", "Color": "green"},
    {"Label": "Duringflood_Coping_Action_Implemented", "Color": "red"},
    {"Label": "Postflood_Adaptation_Measures_Planned", "Color": "blue"}
])

entities_chart = ChartModule([
    {"Label": "Houses_Flooded", "Color": "red"},
    {"Label": "Schools_Flooded", "Color": "orange"},
    {"Label": "Businesses_Flooded", "Color": "blue"}
])

economic_chart = ChartModule([
    {"Label": "Wealth_People", "Color": "blue"},
    {"Label": "Wealth_Businesses", "Color": "green"},
    {"Label": "Wealth_Shelter", "Color": "orange"},
    {"Label": "Wealth_Healthcare", "Color": "purple"},
    {"Label": "Wealth_Government", "Color": "red"}
])

# Combine all the chart modules into a single list
all_charts = (
    [decisions_chart] + [persons_chart] + [entities_chart] + [economic_chart] + 
    preflood_non_evacuation_charts + evacuation_charts + duringflood_coping_charts + 
    postflood_recovery_charts + [evacuated_chart_ses_1, evacuated_chart_ses_2,
                                 stranded_chart_ses_1, stranded_chart_ses_2,
                                 injured_chart_ses_1, injured_chart_ses_2,
                                 sheltered_chart_ses_1, sheltered_chart_ses_2,
                                 hospitalized_chart_ses_1, hospitalized_chart_ses_2,
                                 dead_chart_ses_1, dead_chart_ses_2]
)

# Now you can pass all_charts to the server
server = ModularServer(
    FloodModel,
    [map_element, legend] + all_charts,
    "Flood Model - Vulnerabilities and Decision Making",
    model_params,
)
            
# Run the server
server.port = 8521  # The default port number
server.launch()  
    
# Measure resource usage after the run
mem_after, cpu_after = get_resource_usage()
print(f"Memory usage after batch run: {mem_after:.2f} MB")
print(f"CPU usage after batch run: {cpu_after:.2f}%")