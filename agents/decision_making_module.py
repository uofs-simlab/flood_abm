import random

############################################################### STEP (DAY) ########################################################################
def step(self):
    adjust_for_location(self)
    adjust_factors_based_on_demographics_and_identity(self)
    update_severity(self)
    update_response_efficacy(self)
    update_self_efficacy(self)
    update_perceived_costs(self)
    update_SCT(self)
    decide_on_action(self)
        
############################################################ DECISION-MAKING (NATURAL DISASTER) ####################################################
# Support Methods - Updates for every step

def adjust_for_location(self):
    # Adjust threat level and coping potential based on location
    if self.is_high_risk_area == 1:
        self.severity *= 1.2 
        #self.vulnerability *= 1.1 
    else:
        self.severity *= 0.8 
        #self.vulnerability *= 0.9 

def adjust_factors_based_on_demographics_and_identity(self):
    if self.age > 65:
        self.severity *= 1.1   
    if self.education > 0.6 :
        self.severity *= 1.05  
        self.response_efficacy *= 1.05  
    if self.wealth_class == "Lower_Class":
        self.costs *= 1.2 
    if self.gender == 'Female':
        self.costs *= 1.2 
    if self.ethnicity == 'Indigenous':
        self.costs *= 1.1 

def update_severity(self):
    base_severity = 0.5 
    past_experience_influence = 0.1 * self.past_experience 
    location_influence = 0.2 if self.is_high_risk_area == 1 else -0.1

    severity = base_severity + past_experience_influence + location_influence 
    self.severity = max(0, min(severity, 1))

def update_response_efficacy(self):
    weights = [0.5, 0.5, 0.3, 0.2] 
    self.response_efficacy = (self.trust_in_authorities * weights[0] +
                                self.media_trust * weights[1] +
                                self.self_efficacy * weights[2] +
                                self.past_experience * weights[3])
    
def update_self_efficacy(self):
    base_self_efficacy = 0.5
    # Factors influencing self-efficacy
    past_experience_influence = 0.3 * self.past_experience 
    social_support_influence = 0.2 * self.bonding_count 

    self_efficacy = base_self_efficacy + past_experience_influence + social_support_influence
    self.self_efficacy =  max(0, min(self_efficacy, 1)) 

def update_perceived_costs(self):
    base_costs = 0.5
    income_influence = -0.05 if self.wealth_class in ("Upper_Middle_Class", "Upper_Class") else 0.05
    education_influence = -0.025 if self.education > 0.7 else 0.025
    social_support = -0.05 if self.bonding_count > 0.3 else 0.05
    past_experience_influence = 0.1 if self.past_experience > 0.5 else -0.05

    influences_sum = income_influence + education_influence + social_support + past_experience_influence 
    influences_sum = max(-0.5, min(influences_sum, 0.5))

    perceived_costs = base_costs + influences_sum 
    perceived_costs = max(0, min(perceived_costs, 1))
    self.costs = perceived_costs 

def update_SCT(self):
    if self.bonding_count > 0.7 :
        self.social_capital_score += 0.2 
    else:
        self.social_capital_score -= 0.2 

    if self.bridging_count > 0.5:
        self.social_capital_score += 0.2
    else:
        self.social_capital_score -= 0.2 

    if self.linking_count  > 0.3:
        self.social_capital_score += 0.2 
    else:
        self.social_capital_score -= 0.2 

    if self.social_trust == 1:
        self.social_capital_score += 0.2
    else:
        self.social_capital_score -= 0.2
    
    # if not 0 < self.social_capital_score <1:
    #     self.social_capital_score = random.gauss(0.5,0.5/3)
        
def decide_on_action(self):
     """
     Execute the selected decision-making process to determine the agent's actions.
     """
     select_decision_making_process(self)

##### DECISION MAKING FOR - PRE, DURING AND POST FLOOD EVENTS    

def select_decision_making_process(self):
    """
    Select the decision-making process based on the agent's attributes

    -Protection Motivation Theory (PMT)
    -Social Capital Theory (SCT)
    -Cultural Risk Theory (CRT)
    -Theory of Planned Behavior (TPB)
    """
    # Define the mapping for decision-making functions
    decision_making_functions = {
        'pre_flood_evac_period': {
            'evacuation': {
                'CRT': lambda: CRT_decide_on_evacuation(self),
                'SCT': lambda: SCT_decide_on_evacuation(self),
                'TPB': lambda: TPB_decide_on_evacuation(self),
                'PMT': lambda: PMT_decide_on_evacuation(self)
            },
            'mitigation_preparedness': {
                'CRT': lambda: CRT_decide_on_mitigation_and_preparedness(self),
                'SCT': lambda: SCT_decide_on_mitigation_and_preparedness(self),
                'TPB': lambda: TPB_decide_on_mitigation_and_preparedness(self),
                'PMT': lambda: PMT_decide_on_mitigation_and_preparedness(self)
            }
        },
        'during_flood': {
            'evacuation': {
                'CRT': lambda: CRT_decide_on_evacuation(self),
                'SCT': lambda: SCT_decide_on_evacuation(self),
                'TPB': lambda: TPB_decide_on_evacuation(self),
                'PMT': lambda: PMT_decide_on_evacuation(self)
            },
            'coping': {
                'CRT': lambda: CRT_decide_on_coping_during_flood(self),
                'SCT': lambda: SCT_decide_on_coping_during_flood(self),
                'TPB': lambda: TPB_decide_on_coping_during_flood(self),
                'PMT': lambda: PMT_decide_on_coping_during_flood(self)
            }
        },
        'post_flood': {
            'CRT': lambda: CRT_decide_on_recovery_and_adaptation(self),
            'SCT': lambda: SCT_decide_on_recovery_and_adaptation(self),
            'TPB': lambda: TPB_decide_on_recovery_and_adaptation(self),
            'PMT': lambda: PMT_decide_on_recovery_and_adaptation(self)
        }
    }

    # Decide the action type based on perceived severity for each disaster period
    if not 0 < self.severity < 1:
        self.severity = random.gauss(0.5, 0.5 / 3)  # Normally distribute around 0.5
    else:
        # Add some controlled variation to severity using a scaling factor
        scaling_factor = random.uniform(6, 10)  # Control how much to scale the random adjustment
        self.severity += random.gauss(self.severity, self.severity / 3) / scaling_factor
        
    action_mapping = {
        'pre_flood_evac_period': 'evacuation' if self.severity > 0.92  else 'mitigation_preparedness',
        'during_flood': 'evacuation' if self.severity > 0.94  else 'coping'
    }
    
    if self.model.disaster_period in ['pre_flood_evac_period', 'during_flood']:
        action_type = action_mapping[self.model.disaster_period]
        functions = decision_making_functions[self.model.disaster_period][action_type]
    else:
        functions = decision_making_functions[self.model.disaster_period]
    
    decision_options = [
        # CRT (Cultural Risk Theory)
        ((self.worldview in ['hierarchist', 'fatalist'] and self.bonding_count < 0.5), functions['CRT']),
        ((self.is_high_risk_area == 1 and self.trust_in_authorities == 0), functions['CRT']),
        ((self.bridging_count < 0.5 and self.media_trust == 0), functions['CRT']),
        ((self.self_efficacy < 0.5 and self.wealth_class == "Lower_Class"), functions['CRT']),
        ((self.worldview in ['individualist', 'egalitarian'] and self.bridging_count > 0.5), functions['CRT']),
        
        # PMT (Protection Motivation Theory)
        ((self.past_experience > 0.5) or (self.wealth_class in ("Upper_Middle_Class", "Upper_Class") and self.ethnicity in ['Canadian', 'Immigrant']), functions['PMT']),
        ((self.response_efficacy > 0.7 and self.severity > 0.6), functions['PMT']),
        ((self.is_high_risk_area == 1 and self.vulnerability > 0.6), functions['PMT']),
        ((self.trust_in_authorities == 1 and self.media_trust == 1 and self.severity > 0.4), functions['PMT']),
    
        # SCT (Social Capital Theory)
        ((self.social_trust > 0.7 and self.bonding_count > 0.2) or self.wealth_class == "Lower_Class" or self.ethnicity == 'Indigenous', functions['SCT']),
        ((self.bridging_count > 0.5 or self.linking_count > 0.4), functions['SCT']),
        ((self.social_trust == 1 and self.bonding_count > 0.5 and self.linking_count > 0.4), functions['SCT']),
        ((self.bonding_count > 0.6), functions['SCT']),
        
        # TPB (Theory of Planned Behavior)
        ((self.self_efficacy > 0.6 and self.social_trust > 0.6), functions['TPB']),
        ((self.wealth_class in ("Upper_Middle_Class", "Upper_Class") or self.education > 0.7), functions['TPB']),
        ((self.intention > 0.5 and self.self_efficacy > 0.5), functions['TPB']),
        ((self.media_trust == 1 and self.trust_in_authorities == 1 and self.intention > 0.4), functions['TPB'])
    ]


    # Filter out conditions that are not met and randomly select from valid options
    valid_options = [func for condition, func in decision_options if condition]
    if not valid_options:
        valid_options = [functions.get('CRT')]
    
    # Randomly select one of the valid options (you can adjust weights if needed)
    selected_function = random.choice(valid_options)
    
    # Call the selected function
    return selected_function()

#PRE-EVENT

def PMT_decide_on_mitigation_and_preparedness(self):    
    threat_level = self.severity * self.vulnerability  # Adjusted based on threat perception
    coping_potential = self.response_efficacy * self.self_efficacy - self.costs  # Based on coping ability

    # Modify the decision threshold using a scaling factor
    decision_threshold = coping_potential + random.gauss(
        (threat_level - coping_potential) * scaling_factor1(),  # Increase control over the difference
        (threat_level - coping_potential) / scaling_factor1()  # A fixed variance for randomness, tweak as necessary
    )

    # Make decision based on adjusted threshold
    if threat_level > decision_threshold:
        self.preflood_non_evacuation_measure_implemented = False
        self.preflood_decision_now = "PMT_preflood_mitigation_non_evac_False"
    else:
        self.preflood_non_evacuation_measure_implemented = True
        self.preflood_decision_now = "PMT_preflood_non_evacuation_measure_implemented"
 
def TPB_decide_on_mitigation_and_preparedness(self):
    intention = (self.self_efficacy + self.social_trust) / 2

    # Modify the decision threshold using a scaling factor
    decision_threshold = random.gauss(
        intention * scaling_factor1(),  # Control how much we scale the intention
        intention / scaling_factor1()   # Control randomness through variance
    )

    # Make decision based on adjusted threshold
    if intention > decision_threshold:
        self.preflood_non_evacuation_measure_implemented = True
        self.preflood_decision_now = "TPB_preflood_non_evacuation_measure_implemented"
    else:
        self.preflood_non_evacuation_measure_implemented = False
        self.preflood_decision_now = "TPB_preflood_mitigation_non_evac_False"

def SCT_decide_on_mitigation_and_preparedness(self):
    decision_threshold = random.gauss(
        self.social_capital_score * scaling_factor1(),  # Control how much we scale the social capital score
        self.social_capital_score / scaling_factor1()   # Control randomness through variance
    )

    # Make decision based on adjusted threshold
    if self.social_capital_score > decision_threshold:
        self.preflood_non_evacuation_measure_implemented = True
        self.preflood_decision_now = "SCT_preflood_non_evacuation_measure_implemented"
    else:
        self.preflood_non_evacuation_measure_implemented = False
        self.preflood_decision_now = "SCT_preflood_mitigation_non_evac_False"

def CRT_decide_on_mitigation_and_preparedness(self):
    # Calculate the influence score based on worldview
    if self.worldview == 'hierarchist':
        influence_score = min(max(self.income * 0.00001 + 0.5, 0), 1)
    elif self.worldview == 'egalitarian':
        influence_score = 0.7 if self.bonding_count > 0.8 else 0.4
    elif self.worldview == 'individualist':
        influence_score = 0.9 if self.wealth_class == "Upper_Class" else 0.3
    else:
        influence_score = 0.2

    # Random decision threshold using Gaussian distribution
    decision_threshold = random.gauss(
        influence_score * scaling_factor1(),  # Control how much we scale the influence score
        influence_score / scaling_factor1()    # Control randomness through variance
    )

    # Make decision based on adjusted threshold
    if influence_score > decision_threshold:
        self.preflood_non_evacuation_measure_implemented = True
        self.preflood_decision_now = "CRT_preflood_non_evacuation_measure_implemented"        
    else:
        self.preflood_non_evacuation_measure_implemented = False
        self.preflood_decision_now = "CRT_preflood_mitigation_non_evac_False"

         
#PRE-EVENT and DURING-EVENT EVACUATIONS

def PMT_decide_on_evacuation(self):
    immediate_threat = self.severity * 1.2  
    utility_of_evacuation = immediate_threat - (self.costs * 1.1) 

    if utility_of_evacuation > random.gauss(utility_of_evacuation, utility_of_evacuation):
        self.evacuated = True
        self.preduringflood_decision_now = "PMT_evacuation"
        self.preflood_decision_now = None
        
        evac_cost = evac_costs()
        self.income -= evac_cost
        
        business = random.choice(self.model.space.businesses)
        business.wealth += evac_cost/3
        
    else:
        self.evacuated = False
        self.preduringflood_decision_now = "PMT_evac_False"
        self.preflood_decision_now = None
        
def TPB_decide_on_evacuation(self):
    intention = (self.self_efficacy + self.social_trust) / 2 
    
    if intention > random.gauss(intention, intention):
        self.evacuated = True
        self.preduringflood_decision_now = "TPB_evacuation"
        self.preflood_decision_now = None
        
        evac_cost = evac_costs()
        self.income -= evac_cost
        
        business = random.choice(self.model.space.businesses)
        business.wealth += evac_cost/3
        
    else:
        self.evacuated = False
        self.preduringflood_decision_now = "TPB_evac_False"
        self.preflood_decision_now = None
    
def SCT_decide_on_evacuation(self):
    if  self.social_capital_score > random.gauss(self.social_capital_score, self.social_capital_score):
        self.evacuated = True
        self.preduringflood_decision_now = "SCT_evacuation"
        self.preflood_decision_now = None
        
        evac_cost = evac_costs()
        self.income -= evac_cost
        
        business = random.choice(self.model.space.businesses)
        business.wealth += evac_cost/3
        
    else:
        self.evacuated = False
        self.preduringflood_decision_now = "SCT_evac_False"
        self.preflood_decision_now = None
    
def CRT_decide_on_evacuation(self):

    if self.worldview == 'hierarchist':
        influence_score = min(max(self.income * 0.00001 + 0.5, 0), 1)
    elif self.worldview == 'egalitarian':
        influence_score = 0.7 if self.bonding_count > 0.8 else 0.4
    elif self.worldview == 'individualist':
        influence_score = 0.9 if self.wealth_class == "Upper_Class" else 0.3
    else:
        influence_score = 0.2
    
    if  influence_score > random.gauss(influence_score, influence_score):
        self.evacuated = True
        self.preduringflood_decision_now = "CRT_evacuation"
        self.preflood_decision_now = None
        
        evac_cost = evac_costs()
        self.income -= evac_cost
        
        business = random.choice(self.model.space.businesses)
        business.wealth += evac_cost/3
            
    else:
        self.evacuated = False
        self.preduringflood_decision_now = "CRT_evac_False"
        self.preflood_decision_now = None

#DURING EVENT

def PMT_decide_on_coping_during_flood(self):
    # Calculate threat level and coping potential
    threat_level = self.severity * self.vulnerability
    coping_potential = self.response_efficacy * self.self_efficacy - self.costs
    
    # Consider the impact of previously implemented mitigation/preparedness measures
    mitigation_effectiveness = 0.8 if self.preflood_non_evacuation_measure_implemented else 0.0

    # Adjust current threat level and coping potential based on mitigation effectiveness
    current_threat_level = threat_level * (1 - mitigation_effectiveness)
    current_coping_potential = coping_potential + (mitigation_effectiveness * 0.5)

    # Set decision threshold using Gaussian distribution with scaling factor
    decision_threshold = random.gauss(
        (current_threat_level - current_coping_potential) * scaling_factor2(),  # Mean adjusted for decision making
        (current_threat_level - current_coping_potential) / scaling_factor2()  # Variance controlled by scaling factor
    )

    # Make decision based on adjusted threshold
    if current_threat_level < decision_threshold:
        self.duringflood_coping_action_implemented = True
        self.preduringflood_decision_now = "PMT_duringflood_coping_action_implemented"
    else:
        self.duringflood_coping_action_implemented = False
        self.preduringflood_decision_now = "PMT_duringflood_coping_action_implemented_False"


def TPB_decide_on_coping_during_flood(self):
    # Calculate intention based on self-efficacy and social trust
    intention = (self.self_efficacy + self.social_trust) / 2
    
    # Consider the effectiveness of previously implemented measures on current intentions
    measure_effectiveness_boost = 0.1 if self.preflood_non_evacuation_measure_implemented else 0.0
    current_intention = intention + measure_effectiveness_boost
    
    # Set decision threshold using Gaussian distribution with scaling factor
    decision_threshold = random.gauss(
        current_intention * scaling_factor2(),  # Mean adjusted for decision making
        current_intention / scaling_factor2()  # Variance controlled by scaling factor
    )

    # Make decision based on adjusted threshold
    if current_intention > decision_threshold:
        self.duringflood_coping_action_implemented = True
        self.preduringflood_decision_now = "TPB_duringflood_coping_action_implemented"
    else:
        self.duringflood_coping_action_implemented = False
        self.preduringflood_decision_now = "TPB_duringflood_coping_action_implemented_False"


def SCT_decide_on_coping_during_flood(self):
    # Adjust the influence of social capital based on previously implemented measures
    mitigation_adjustment = 0.9 if self.preflood_non_evacuation_measure_implemented else -0.1
    score = self.social_capital_score + mitigation_adjustment

    # Set decision threshold using Gaussian distribution with scaling factor
    decision_threshold = random.gauss(
        score * scaling_factor2(),  # Mean adjusted for decision making
        score / scaling_factor2()    # Variance controlled by scaling factor
    )

    # Make decision based on adjusted threshold
    if score > decision_threshold:
        self.duringflood_coping_action_implemented = True
        self.preduringflood_decision_now = "SCT_duringflood_coping_action_implemented"
    else:
        self.duringflood_coping_action_implemented = False
        self.preduringflood_decision_now = "SCT_duringflood_coping_action_implemented_False"

 
def CRT_decide_on_coping_during_flood(self):
    # Determine the influence score based on worldview
    if self.worldview == 'hierarchist':
        influence_score = min(max(self.income * 0.00001 + 0.5, 0), 1)
    elif self.worldview == 'egalitarian':
        influence_score = 0.7 if self.bonding_count > 0.8 else 0.4
    elif self.worldview == 'individualist':
        influence_score = 0.9 if self.wealth_class == "Upper_Class" else 0.3
    else:
        influence_score = 0.2
    
    # Set decision threshold using Gaussian distribution with scaling factor
    decision_threshold = random.gauss(
        influence_score * scaling_factor2(),  # Mean adjusted for decision making
        influence_score / scaling_factor2()     # Variance controlled by scaling factor
    )

    # Make decision based on adjusted threshold
    if influence_score > decision_threshold:
        self.duringflood_coping_action_implemented = True
        self.preduringflood_decision_now = "CRT_duringflood_coping_action_implemented"
    else:
        self.duringflood_coping_action_implemented = False
        self.preduringflood_decision_now = "CRT_duringflood_coping_action_implemented_False"


#POS-EVENT

def PMT_decide_on_recovery_and_adaptation(self):
    # Reflect on the past actions' effectiveness
    mitigation_reflection = 1.0 if self.preflood_non_evacuation_measure_implemented else 0.5
    coping_reflection = 1.0 if self.duringflood_coping_action_implemented else 0.5

    # Calculate adjusted perceived threat level and coping potential for future events
    future_threat_level = self.severity * self.vulnerability * (1 - mitigation_reflection)
    future_coping_potential = self.response_efficacy * self.self_efficacy + coping_reflection - self.costs

    # Set decision threshold using Gaussian distribution with scaling factor
    decision_threshold = future_coping_potential + random.gauss(
        (future_threat_level - future_coping_potential) * scaling_factor3(),  # Control over the difference
        (future_threat_level - future_coping_potential) / scaling_factor3()     # Variance controlled by scaling factor
    )

    # Make decision based on adjusted threshold
    if future_threat_level < decision_threshold:
        self.postflood_adaptation_measures_planned = True
        self.postflood_decision_now = "PMT_postflood_adaptation_measures_planned"
    else:
        self.postflood_adaptation_measures_planned = False
        self.postflood_decision_now = "PMT_postflood_adaptation_measures_planned_False"


def TPB_decide_on_recovery_and_adaptation(self):
    base_intention = (self.self_efficacy + self.social_trust) / 2
    
    # Adjust intention based on effectiveness of past mitigation/preparedness and coping measures
    past_measures_effectiveness = 0.2 if self.preflood_non_evacuation_measure_implemented else -0.1  
    past_coping_effectiveness = 0.2 if self.duringflood_coping_action_implemented else -0.1  

    recovery_intention = base_intention + past_measures_effectiveness + past_coping_effectiveness

    # Decision threshold influenced by scaling factor for variability
    decision_threshold = random.gauss(
        recovery_intention * scaling_factor3(),    # Scale based on intention
        recovery_intention / scaling_factor3()     # Introduce variability
    )

    # Make decision based on adjusted intention threshold
    if recovery_intention > decision_threshold:
        self.postflood_adaptation_measures_planned = True
        self.postflood_decision_now = "TPB_postflood_adaptation_measures_planned"
    else:
        self.postflood_adaptation_measures_planned = False
        self.postflood_decision_now = "TPB_postflood_adaptation_measures_planned_False"

    
def SCT_decide_on_recovery_and_adaptation(self):
    # Adjust intention based on effectiveness of past mitigation/preparedness and coping measures
    past_measures_effectiveness = 0.2 if self.preflood_non_evacuation_measure_implemented else -0.1
    past_coping_effectiveness = 0.2 if self.duringflood_coping_action_implemented else -0.1
    
    # Calculate adjusted score
    score = self.social_capital_score + past_measures_effectiveness + past_coping_effectiveness

    # Decision threshold influenced by scaling factor for variability
    decision_threshold = random.gauss(
        score * scaling_factor3(),  # Scale based on score
        score / scaling_factor3()    # Introduce variability
    )

    # Make decision based on adjusted score and threshold
    if score > decision_threshold:
        self.postflood_adaptation_measures_planned = True
        self.postflood_decision_now = "SCT_postflood_adaptation_measures_planned"
    else:
        self.postflood_adaptation_measures_planned = False
        self.postflood_decision_now = "SCT_postflood_adaptation_measures_planned_False"

            
def CRT_decide_on_recovery_and_adaptation(self):
    # Calculate influence score based on worldview
    if self.worldview == 'hierarchist':
        influence_score = min(max(self.income * 0.00001 + 0.5, 0), 1)
    elif self.worldview == 'egalitarian':
        influence_score = 0.7 if self.bonding_count > 0.8 else 0.4
    elif self.worldview == 'individualist':
        influence_score = 0.9 if self.wealth_class == "Upper_Class" else 0.3
    else:
        influence_score = 0.2

    # Decision threshold influenced by scaling factor for variability
    decision_threshold = random.gauss(
        influence_score * scaling_factor3(),  # Scale based on influence score
        influence_score / scaling_factor3()     # Introduce variability
    )

    # Make decision based on adjusted score and threshold
    if influence_score > decision_threshold:
        self.postflood_adaptation_measures_planned = True
        self.postflood_decision_now = "CRT_postflood_adaptation_measures_planned"
    else:
        self.postflood_adaptation_measures_planned = False
        self.postflood_decision_now = "CRT_postflood_adaptation_measures_planned_False"
   
    
def scaling_factor1():
    return random.uniform(0.2, 10)

def scaling_factor2():
    return random.uniform(0.01, 1)

def scaling_factor3():
    return random.uniform(0.7, 2)
    
def evac_costs():
    return random.uniform(0, 1500)
