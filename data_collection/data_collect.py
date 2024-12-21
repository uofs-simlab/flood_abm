import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from mesa import DataCollector
import agents.flood_agents as FA

#-------------- Data Collection based on SES index --------------------

def data_collection(model):
    model.datacollector = DataCollector(
        model_reporters={
            **generate_ses_reporters("preflood_non_evacuation_measure_implemented", "SES_1", compute_preflood_non_evacuation_measure_implemented),
            **generate_ses_reporters("preflood_non_evacuation_measure_implemented", "SES_2", compute_preflood_non_evacuation_measure_implemented),
            **generate_ses_reporters("evacuation", "SES_1", compute_evacuated),
            **generate_ses_reporters("evacuation", "SES_2", compute_evacuated),
            **generate_ses_reporters("duringflood_coping_action_implemented", "SES_1", compute_duringflood_coping_action_implemented),
            **generate_ses_reporters("duringflood_coping_action_implemented", "SES_2", compute_duringflood_coping_action_implemented),
            **generate_ses_reporters("postflood_adaptation_measures_planned", "SES_1", compute_postflood_adaptation_measures_planned),
            **generate_ses_reporters("postflood_adaptation_measures_planned", "SES_2", compute_postflood_adaptation_measures_planned),

            # Aggregate metrics
            "Stranded": lambda model: safe_divide(compute_stranded(model), model.num_persons),
            "Injured": lambda model: safe_divide(compute_injured(model), model.num_persons),
            "Sheltered": lambda model: safe_divide(compute_sheltered(model), model.num_persons),
            "Hospitalized": lambda model: safe_divide(compute_hospitalized(model), model.num_persons),
            "Death": lambda model: safe_divide(compute_death(model), model.num_persons),
            "Evacuated": lambda model: safe_divide(compute_evacuated(model), model.num_persons),

            "Preflood_Non_Evacuation_Measure_Implemented": lambda model: safe_divide(compute_preflood_non_evacuation_measure_implemented(model), model.num_persons),
            "Duringflood_Coping_Action_Implemented": lambda model: safe_divide(compute_duringflood_coping_action_implemented(model), model.num_persons),
            "Postflood_Adaptation_Measures_Planned": lambda model: safe_divide(compute_postflood_adaptation_measures_planned(model), model.num_persons),

            # Flooded buildings
            "Houses_Flooded": lambda model: safe_divide(sum(1 for agent in model.schedule.agents if isinstance(agent, FA.House_Agent) and agent.flooded), model.num_houses),
            "Businesses_Flooded": lambda model: safe_divide(sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Business_Agent) and agent.flooded), model.num_businesses),
            "Schools_Flooded": lambda model: safe_divide(sum(1 for agent in model.schedule.agents if isinstance(agent, FA.School_Agent) and agent.flooded), model.num_schools),

            # Wealth
            "Wealth_People": lambda model: sum(agent.income for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and not agent.evacuated) / model.persons_gdp - 1,
            "Wealth_Businesses": lambda model: sum(agent.wealth for agent in model.schedule.agents if isinstance(agent, FA.Business_Agent))/ model.business_gdp - 1,
            "Wealth_Shelter": lambda model: sum(agent.wealth for agent in model.schedule.agents if isinstance(agent, FA.Shelter_Agent)) / model.shelter_gdp - 1,
            "Wealth_Healthcare": lambda model: sum(agent.wealth for agent in model.schedule.agents if isinstance(agent, FA.Healthcare_Agent)) / model.healthcare_gdp - 1,
            "Wealth_Government": lambda model: sum(agent.wealth for agent in model.schedule.agents if isinstance(agent, FA.Government_Agent)) / model.government_gdp - 1,

            # SES-specific metrics using compute functions
            **create_ses_category_reporters("evacuated", ['SES_1', 'SES_2'], compute_evacuated),
            **create_ses_category_reporters("stranded", ['SES_1', 'SES_2'], compute_stranded),
            **create_ses_category_reporters("sheltered", ['SES_1', 'SES_2'], compute_sheltered),
            **create_ses_category_reporters("dead", ['SES_1', 'SES_2'], compute_death),
            **create_ses_category_reporters("hospitalized", ['SES_1', 'SES_2'], compute_hospitalized),
            **create_ses_category_reporters("injured", ['SES_1', 'SES_2'], compute_injured),
            **create_ses_category_reporters_total_population("stranded", ['SES_1', 'SES_2']),  # New SES stranded metrics
            **create_ses_category_reporters_total_population("injured", ['SES_1', 'SES_2']),  # New SES stranded metrics
            **create_ses_category_reporters_total_population("sheltered", ['SES_1', 'SES_2']),  # New SES stranded metrics
            **create_ses_category_reporters_total_population("hospitalized", ['SES_1', 'SES_2']),  # New SES stranded metrics
            **create_ses_category_reporters_total_population("dead", ['SES_1', 'SES_2']),  # New SES stranded metrics
            **create_ses_category_reporters_total_population("evacuated", ['SES_1', 'SES_2']),  # New SES stranded metrics
        }
    )

# Safe divide helper function to avoid division by zero
def safe_divide(numerator, denominator):
    return numerator / denominator if denominator != 0 else 0

def create_reporter(decision, ses_index, min_value, max_value, compute_func): 
    def reporter(model):
        total_matching_agents = 0
        total_agents_in_ses = 0
        
        for agent in model.schedule.agents:
            if isinstance(agent, FA.Person_Agent):
                ses_value = getattr(agent, ses_index, None)  # Get the SES value for the agent
                decision_value = False  # Initialize with a default value
                
                # Check which disaster period is active
                if model.disaster_period == 'pre_flood_evac_period':
                    if agent.preflood_decision_now is not None:
                        decision_value = agent.preflood_decision_now == decision  # Preflood decision
                    else:
                        decision_value = agent.preduringflood_decision_now == decision
                        
                elif model.disaster_period == 'during_flood':
                    decision_value = agent.preduringflood_decision_now == decision  # During-flood decision
                
                elif model.disaster_period == 'post_flood':
                    decision_value = agent.postflood_decision_now == decision  # Post-flood decision

                if ses_value is not None and min_value <= ses_value <= max_value:
                    total_agents_in_ses += 1  # Count total agents within the SES range
                    
                    if decision_value:
                        total_matching_agents += 1  # Count agents that match the decision
        
        # Return the fraction of matching agents over total agents in SES
        return total_matching_agents / compute_func(model) if compute_func(model) > 0 else 0

    return reporter


# Helper function to create SES-based reporters for decisions
def generate_ses_reporters(phase, ses_index, compute_func):
    decisions = ["PMT", "TPB", "SCT", "CRT"]
    ses_ranges = [(0, 0.3), (0.7, 1)]
    reporters = {}
    
    for decision in decisions:
        for min_val, max_val in ses_ranges:
            key = f"{decision}_{phase}_{ses_index}_{min_val}_{max_val}"
            reporters[key] = create_reporter(f"{decision}_{phase}", ses_index, min_val, max_val, compute_func)
    
    return reporters


# Refactored count_agents_by_category to mimic create_reporter logic
def count_agents_by_category(model, category, prefix, compute_func):
    ses_ranges = {
        'SES_1': {'0_0.3': (0, 0.3), '0.7_1': (0.7, 1)},
        'SES_2': {'0_0.3': (0, 0.3), '0.7_1': (0.7, 1)}
    }

    # Extract SES index and SES range from category
    category_parts = category.split('_')
    ses_index = '_'.join(category_parts[:2])  # Extract SES index (e.g., 'SES_1')
    ses_range = '_'.join(category_parts[2:])  # Extract SES range (e.g., '0_0.3')

    # Check if the SES index and range are valid
    if ses_index in ses_ranges and ses_range in ses_ranges[ses_index]:
        min_val, max_val = ses_ranges[ses_index][ses_range]

        # Get the total number of agents matching the condition (evacuated, stranded, etc.)
        total_matching_agents = compute_func(model)

        # Initialize counters for agents within SES and matching condition
        matching_agents_in_ses = 0
        total_agents_in_ses = 0

        # Loop through agents in the model and check their SES value and condition
        for agent in model.schedule.agents:
            if isinstance(agent, FA.Person_Agent):
                ses_value = getattr(agent, ses_index, None)

                # Determine condition_matched based on prefix
                if prefix.lower() == "dead":
                    condition_matched = not agent.alive  # For dead, check if the agent is not alive
                elif prefix.lower() == "sheltered":
                    condition_matched = agent in model.shelter.sheltered_agents  # Check if sheltered
                elif prefix.lower() == "hospitalized":
                    condition_matched = agent in model.healthcare.hospitalized_agents  # Check if hospitalized
                else:
                    condition_matched = getattr(agent, f"{prefix.lower()}", False)  # Other conditions like evacuated, injured

                # Count agents in SES range
                if ses_value is not None and min_val <= ses_value <= max_val:
                    total_agents_in_ses += 1

                    if condition_matched:
                        matching_agents_in_ses += 1

        # Return the ratio of matching agents to total matching agents
        return matching_agents_in_ses / total_matching_agents if total_matching_agents > 0 else 0

    return 0


# Refactor create_ses_category_reporters
def create_ses_category_reporters(prefix, ses_indexes, compute_func):
    categories = ['0_0.3', '0.7_1']
    reporters = {}

    for ses_index in ses_indexes:
        for category in categories:
            key = f"{prefix}_{ses_index}_{category}"
            
            # Create reporter using count_agents_by_category
            reporters[key] = lambda model, cat=f"{ses_index}_{category}": count_agents_by_category(
                model, cat, prefix, compute_func
            )
    
    return reporters

def create_ses_category_reporters_total_population(prefix, ses_indexes):
    categories = ['0_0.3', '0.7_1']
    reporters = {}

    for ses_index in ses_indexes:
        for category in categories:
            key = f"{prefix}_total_pop_{ses_index}_{category}"
            
            # Create reporter using count_agents_by_total_population
            reporters[key] = lambda model, cat=f"{ses_index}_{category}": count_agents_by_total_population(
                model, cat, prefix
            )
    
    return reporters


def count_agents_by_total_population(model, category, prefix):
    ses_ranges = {
        'SES_1': {'0_0.3': (0, 0.3), '0.7_1': (0.7, 1)},
        'SES_2': {'0_0.3': (0, 0.3), '0.7_1': (0.7, 1)}
    }

    # Extract SES index and SES range from category
    category_parts = category.split('_')
    ses_index = '_'.join(category_parts[:2])  # Extract SES index (e.g., 'SES_1')
    ses_range = '_'.join(category_parts[2:])  # Extract SES range (e.g., '0_0.3')

    # Check if the SES index and range are valid
    if ses_index in ses_ranges and ses_range in ses_ranges[ses_index]:
        min_val, max_val = ses_ranges[ses_index][ses_range]

        # Initialize counters for agents within SES and matching condition
        matching_agents_in_ses = 0
        total_agents_in_ses = 0

        # Loop through agents in the model and check their SES value and condition
        for agent in model.schedule.agents:
            if isinstance(agent, FA.Person_Agent):
                ses_value = getattr(agent, ses_index, None)

                # Determine condition_matched based on prefix
                if prefix.lower() == "stranded":
                    condition_matched = agent.stranded
                elif prefix.lower() == "injured":
                    condition_matched = agent.injured
                elif prefix.lower() == "sheltered":
                    condition_matched = agent in model.shelter.sheltered_agents
                elif prefix.lower() == "hospitalized":
                    condition_matched = agent in model.healthcare.hospitalized_agents
                elif prefix.lower() == "dead":
                    condition_matched = not agent.alive
                elif prefix.lower() == "evacuated":
                    condition_matched = agent.evacuated
                else:
                    # Default to False if the condition doesn't match known prefixes
                    condition_matched = False

                # Count agents in SES range
                if ses_value is not None and min_val <= ses_value <= max_val:
                    total_agents_in_ses += 1
                    if condition_matched:
                        matching_agents_in_ses += 1

        # Return the ratio of matching agents to total population
        return matching_agents_in_ses / model.num_persons if model.num_persons > 0 else 0

    return 0




def compute_preflood_non_evacuation_measure_implemented(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.preflood_non_evacuation_measure_implemented)

def compute_duringflood_coping_action_implemented(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.duringflood_coping_action_implemented)

def compute_postflood_adaptation_measures_planned(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.postflood_adaptation_measures_planned)

def compute_evacuated(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.evacuated)

def compute_hospitalized(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent in 
               [hospitalized_agent for hc_agent in model.schedule.agents if isinstance(hc_agent, FA.Healthcare_Agent) for hospitalized_agent in hc_agent.hospitalized_agents])

def compute_sheltered(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent in 
               [sheltered_agent for ss_agent in model.schedule.agents if isinstance(ss_agent, FA.Shelter_Agent) for sheltered_agent in ss_agent.sheltered_agents])

def compute_stranded(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.stranded)

def compute_injured(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and agent.injured)

def compute_death(model):
    return sum(1 for agent in model.schedule.agents if isinstance(agent, FA.Person_Agent) and not agent.alive)

