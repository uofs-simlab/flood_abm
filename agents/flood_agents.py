"""
The flood_agents module contains classes representing different entities within the flood simulation environment. 
These classes encapsulate the behaviors, attributes, and interactions of various agents present in the 
simulation environment.

- Person_Agent: Represents individuals within the simulation, each with unique attributes, behaviors, and responses to flooding events.
- House_Agent: Models residential units, managing residents and their reactions to flood risk and distress situations.
- Business_Agent: Represents commercial entities offering services, employing individuals, and interacting with the economy.
- School_Agent: Represents educational institutions providing services to students and interacting with the population.
- Shelter_Agent: Represents infrastructure responsible for rescuing stranded agents and providing support during flood events.
- Healthcare_Agent: Represents healthcare facilities supporting injured individuals during flood disasters.
- Government_Agent: Models the governing body responsible for managing taxes, supporting infrastructure, and public finances within the simulation environment.
"""

import sys
import os

# Add the parent directory of 'agents' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mesa_geo import GeoAgent
import random
from . import decision_making_module as decision
import numpy as np
from shapely.geometry import Point

import uuid

class Person_Agent(GeoAgent):
    """
    Person Agents represent individuals within the simulation. Each person possesses demographic attributes such as age, ethnicity,
    and income, alongside a measure of flood risk perception and preparedness. They engage in diverse behaviors including daily 
    activities, responses to flood-induced distress, tax payment, and interaction with businesses for services.
    """
    
    def __init__(self, unique_id, model, geometry, crs) -> None:
        """
        Initialize a Person Agent with demographic, behavioral, and state-based attributes.

        Parameters:
        - unique_id: Unique identifier for the agent.
        - model: Reference to the simulation model.
        - geometry: Geographical location of the person (Shapely geometry).
        - crs: Coordinate Reference System for spatial data.
        """
        super().__init__(unique_id=unique_id, model=model, geometry=geometry, crs=crs)
        self.name = str(uuid.uuid4()) # Generate a unique name for the agent
        
        # Basic attributes
        self.age = None
        self.ethnicity = None
        self.income = None
        self.wealth_class = None
        self.education = None
        self.gender = None
        
        # Location and employment attributes
        self.household = None  
        self.homeless = True             
        self.workplace = None
        self.working_class = False
        self.employed = False
        self.student = False
        self.schoolplace = None
        
        # Flood and evacuation attributes
        self.mobility = None
        self.last_evacuation_time = None
        self.flood_data_prediction = None
        self.evacuated = False
        self.injured = False
        
        # Time and state attributes
        self.current_hour = 0            
        self.resilience = random.uniform(5, 15)  # Flood risk perception
        self.stranded = False
        self.time_stranded = 0
        self.time_injured = 0
        self.time_in_shelter = 0
        
        # Survival thresholds
        self.injury_duration = random.randint(12, 60)        
        self.survivability_duration = self.injury_duration + random.randint(70, 120)
        self.recovery_rate = random.uniform(0, 1)       # in hours
        self.alive = True
        
        # Decision-making components
        self.worldview = self.random.choice(['hierarchist', 'egalitarian', 'individualist', 'fatalist']) # Based on Cultural theory of risk
        self.past_experience = random.random()  # 0 to 1, where 1 is a high impact past flood experience # Att with flood map
        self.is_high_risk_area = random.choice([0, 1]) # 0 or 1, where 1 is high risk area # Att with region map
        self.trust_in_authorities = random.choice([0, 1]) # 0 or 1, where 1 is high trust
        self.media_trust = random.choice([0, 1]) # 0 or 1, where 1 is high trust
        self.social_trust = random.choice([0, 1]) # 0 or 1, where 1 is high trust

        # Social Network
        self.bonding_count = random.random() # 1 = higher values
        self.bridging_count = random.random() # 1 = higher values
        self.linking_count = random.random() # 1 = higher values
        self.social_capital_score = 0
        
        # Initializing Decision-Making Behaviour components (for disaster)
        self.self_efficacy = random.random() 
        self.intention = random.random() 
        self.preflood_decision_now = None
        self.preduringflood_decision_now = None
        self.postflood_decision_now = None
        self.preflood_non_evacuation_measure_implemented = None
        self.duringflood_coping_action_implemented = None
        self.postflood_adaptation_measures_planned = None
        
        self.severity = random.random() 
        self.response_efficacy = random.random() 
        self.costs = random.random()         
        
        #----------------------------------------------------------------------        

    def step(self):
        """
        Execute one step of the agent's actions in the simulation model.

        Behavior:
        - Determines daily activities based on time of day.
        - Reacts to flood conditions during pre-flood, during-flood, and post-flood phases.
        - Handles taxation every 30 days.
        """       
        if self.alive:
            self.time_of_day = self.current_hour % 24  # Assuming a 24-hour model
            
            if not (self.evacuated or self in self.model.shelter.sheltered_agents or self in self.model.healthcare.hospitalized_agents):
                if not self.stranded:                    
                    # Different actions based on time of day
                    if 0 <= self.time_of_day < 8:     # Resting at home
                        if not self.homeless :
                            self.rest_at_home()
                        else:
                            self.random_movement()        
                    elif 8 <= self.time_of_day < 12:  # Working or Schooling or Working Randomly 
                        if self.employed:               
                            self.work_at_business()
                        elif self.student:              
                            self.go_to_school()
                        else:
                            self.random_movement()
                    elif 12 <= self.time_of_day < 14:  # Lunchtime - random movement
                        self.random_movement()
            
                    elif 14 <= self.time_of_day < 18:  # Working or Schooling or Working Randomly
                        if self.employed:
                            self.work_at_business()
                        elif self.student:
                            self.go_to_school()
                        else:
                            self.random_movement()
                           
                    else:                              # Random movement - recreation time
                        self.random_movement() 
                else:                                  # Alive but stranded in its location and can't go home, work or school
                    self.random_movement()
        
            if self.current_hour / 24 == 30:
                self.pay_taxes()    
            
            # Pre Flood            
            if self.model.disaster_period == 'pre_flood_evac_period':
                
                if not self.evacuated:
                    if random.gauss(0.5,0.5/3) < 0.25:
                        decision.step(self)
                        
                    if self.evacuated:
                        self.model.space.remove_agent(self)
            
            # During Flood
            if self.model.disaster_period == 'during_flood':
                
                self.preflood_non_evacuation_measure_implemented = False
                self.preflood_decision_now = None
                
                if not self.evacuated: # and not self.in_shelter and not self.in_healthcare:
                    decision.step(self)
                    
                    if self.evacuated:
                        self.model.space.remove_agent(self)
                    
            # Post flood
            if self.model.disaster_period == 'post_flood':
                
                self.duringflood_coping_action_implemented = False
                self.preduringflood_decision_now = None
                
                self.stranded = False
                
                decision.step(self)
                
                    
                if self.evacuated:
                    if random.random() < 0.5:
                        self.evacuated = False                            
                        self.model.space.add_agents(self)
                            
                if self in self.model.shelter.sheltered_agents:
                    if random.random() < 0.7:
                        self.model.shelter.sheltered_agents.remove(self)
                        
                if self.injured:
                    self.model.receive_healthcare(self)  
                    
            # Everyday life       
            else:
                if self.model.disaster_period == 'during_flood':
                    self.preflood_non_evacuation_measure_implemented = False
                if self.model.disaster_period == 'during_flood':                    
                    self.preflood_non_evacuation_measure_implemented = False
                    
            
        else:
            self.preflood_decision_now = None
            self.preduringflood_decision_now = None
            self.postflood_decision_now = None
            
            self.duringflood_coping_action_implemented = False
            self.preflood_non_evacuation_measure_implemented = False
            
            
        self.current_hour += 1
    
    def rest_at_home(self):
        """Simulates resting behavior if the agent's home is not flooded."""
        # Function for resting at home if not stranded
        if self.household.flooded:
            self.random_movement()
        else:
            house_polygon = self.household.geometry
            house_position = self.get_random_point_in_polygon(house_polygon)
            # Move the agent to a random position within the household geometry
            if self.time_of_day == 0:
                self.model.space.move_agent(self, house_position)
    
    def get_random_point_in_polygon(self, polygon):
        """Generate a random point within a given polygon."""
        min_x, min_y, max_x, max_y = polygon.bounds
        while True:
            random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if polygon.contains(random_point):
                return random_point

    def work_at_business(self):
        """Simulates working behavior if the agent's workplace is not flooded."""
        if self.workplace.flooded:
            self.random_movement()
        else:
            workplace_polygon = self.workplace.geometry
            workplace_position = self.get_random_point_in_polygon(workplace_polygon)
            # print("job position", workplace_position)
            self.model.space.move_agent(self, workplace_position)
            
            employee_hourly_pay = self.get_hourly_wage()
            self.income += employee_hourly_pay  
            
            if isinstance(self.workplace, Business_Agent):
                self.workplace.wealth -= employee_hourly_pay  # Deduct payment from business wealth
            
    def get_hourly_wage(self):
        """Determine hourly wage based on wealth class."""
        if self.wealth_class == "Upper_Class":
            hourly_wage = random.uniform(250000, 500000)/(365*24)
        elif self.wealth_class == "Upper_Middle_Class":
            hourly_wage = random.uniform(100000, 250000)/(365*24)
        elif self.wealth_class == "Middle_Class":
            hourly_wage = random.uniform(50000, 100000)/(365*24)
        elif self.wealth_class == "Lower_Class":
            hourly_wage = random.uniform(0, 50000)/(365*24)
        
        return hourly_wage

    def go_to_school(self):
        """Simulates attending school if the school is not flooded."""
        # Function for going to school if not flooded
        if self.schoolplace.flooded:
            self.random_movement()
        else:
            schoolplace_polygon = self.schoolplace.geometry
            school_position = self.get_random_point_in_polygon(schoolplace_polygon)
            # print("school_position", school_position)            
            self.model.space.move_agent(self, school_position)

    def random_movement(self):
        """Simulates random movement while considering flood risk."""
        current_position = self.geometry
    
        # Generate possible moves within the mobility range
        num_moves = 10  # Number of potential moves to consider
        possible_moves = []
    
        for _ in range(num_moves):
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(0, self.mobility * 20)
            dx = distance * np.cos(angle)
            dy = distance * np.sin(angle)
            new_x = current_position.x + dx
            new_y = current_position.y + dy
            possible_move = Point(new_x, new_y)
    
            possible_moves.append(possible_move)
    
        # Filter out unsafe moves based on flood resilience
        safe_moves = [move for move in possible_moves
                      if self.resilience > self.model.space.get_flood_height_at_position(move)]
    
        if not safe_moves:
            self.stranded_behavior()
        else:
            self.stranded = False
            self.time_stranded = 0
    
            chosen_spot = random.choice(safe_moves)
            # print("random_spot", chosen_spot)
            self.model.space.move_agent(self, chosen_spot)
    
            # Check if the agent comes in contact with a business
            for business in self.model.space.businesses:
                if business.geometry.contains(chosen_spot):
                    service_cost = self.get_hourly_wage() * random.uniform(0.5, 1.5)
                    
                    if not business.flooded:
                        self.income -= service_cost  # Deduct service cost from agent's income
                        business.wealth += service_cost * random.uniform(1,5) 
                    else:
                        business.wealth -= service_cost * random.uniform(10,40) 
                    return
        
    def stranded_behavior(self):
        """Handles agent behavior when stranded in a flood."""
        self.stranded = True
        self.time_stranded += 1
        
        if self.time_stranded > self.injury_duration:
            self.injured = True
            self.time_injured += 1 
        
        self.model.notify_shelter(self)  # Notify the support system agent
        
        if self not in self.model.shelter.sheltered_agents:
            if self.time_stranded > self.survivability_duration:
                self.alive = False
                self.stranded = False
                self.injured = False 
                self.duringflood_coping_action_implemented = False
        
            
    def pay_taxes(self):
        """Calculates and pays taxes to the government."""
        tax_rate = random.uniform(0, 0.07)  # Set the tax rate (adjust as needed)
        tax_amount = self.income * tax_rate
        self.model.government.wealth += tax_amount
        self.income -= tax_amount      
        


class Shelter_Agent(GeoAgent):
    """
    Shelter Agent represents the infrastructure responsible for rescuing stranded agents, 
    providing shelter, and administering support within the simulation. 
    It has a limited capacity to rescue and support agents, allocating resources for rescue operations and care, 
    while receiving funds from the government and potentially redistributing them to other entities.
    """
    
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        """
        Initialize a Shelter Agent with the provided unique identifier, model, capacity limit, and support GDP share.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - capacity_limit: maximum capacity of the shelter system
        - support_gdp_share: the share of the GDP attributed to support operations
        - geometry: the geographical location of the shelter (Shapely geometry)
        - crs: the coordinate reference system of the geometry
        """

        self.wealth = None  # Share of the GDP attributed to support operations
        self.capacity_limit = None  # Maximum capacity of the shelter system
        self.sheltered_agents = []  # List to store sheltered agents
        self.num_sheltered_agents = 0  # Count of sheltered agents
        self.current_hour = 0  # Initialize the current hour

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        Shelters manage resources, care for agents, and attempt to help them during floods.
        """
        # During Flood and Post Flood
        if self.model.last_evacuation_time < self.current_hour :        
            
            self.num_sheltered_agents = len(self.sheltered_agents)  # Update the count of rescued agents
            
            shelter_cost_per_person = random.uniform(0, 50)  # Cost for the support system
            shelter_cost = shelter_cost_per_person * self.num_sheltered_agents
            self.wealth -= shelter_cost  # Deduct funds for rescue and sheltering
            
            # Redistribute support funds to a randomly chosen business, if available
            businesses = [agent for agent in self.model.schedule.agents if isinstance(agent, Business_Agent)]
            if businesses:
                chosen_business = random.choice(businesses)
                if not chosen_business.flooded:
                    chosen_business.wealth += shelter_cost * random.uniform(0, 0.1)  # Allocate support funds to the chosen business
                else:
                    chosen_business.wealth -= shelter_cost * random.uniform(1, 20)
            
            for agent in self.sheltered_agents:  # if agent is injured and in shelter get him healthcare
                agent.time_in_shelter += 1
                
                if agent.injured:
                    if len(self.model.healthcare.hospitalized_agents) < self.model.healthcare.capacity_limit and agent.time_injured >= self.model.hours_before_healthcare:
                        self.model.receive_healthcare(agent)
                        self.sheltered_agents.remove(agent)
                        agent.time_in_shelter = 0
                    
                    if agent not in self.model.healthcare.hospitalized_agents:  # update time of injury if healthcare is full
                        self.time_injured += 1
            
            for agent in self.sheltered_agents:
                if agent.time_in_shelter >= 12: # Agent attempts to go home after 12 hours in shelter
                    if not agent.household.flooded:
                        self.sheltered_agents.remove(agent)
        
        self.current_hour += 1  # Increment the current hour

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, Shelter_Agent):
            return self.unique_id == other.unique_id
        return False


class Healthcare_Agent(GeoAgent):
    """
    Healthcare Agent represents healthcare facilities within the simulation. 
    These agents provide medical support and care for injured individuals. 
    They have a capacity limit for patient care and operate with allocated healthcare GDP.
    """
    
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        """
        Initialize a Healthcare Agent with the provided unique identifier, model, capacity limit, and healthcare GDP.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - capacity_limit: maximum capacity of the healthcare facility
        - healthcare_gdp: the healthcare GDP allocated to the facility
        - geometry: the geographical location of the healthcare facility (Shapely geometry)
        - crs: the coordinate reference system of the geometry
        """

        self.wealth = None  # Share of the GDP allocated to healthcare
        self.capacity_limit = None  # Maximum capacity of the healthcare facility
        self.hospitalized_agents = []  # List to store injured patients
        self.current_hour = 0  # Initialize the current hour

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        """
        
        # During Flood
        if self.model.last_evacuation_time < self.current_hour:
               
            self.num_hospitalized_patients = len(self.hospitalized_agents)  # Update the count of injured patients          
            
            for agent in self.hospitalized_agents:
                healthcare_cost_per_person = random.uniform(0,100)  # Cost for the support system
                if isinstance(agent, Person_Agent):
                    agent.income -= healthcare_cost_per_person  # Agent spends some money for their care
                    self.wealth -= healthcare_cost_per_person * random.uniform(0,0.3)   # healthcare gets some profit from agen  
                    
                    businesses = [bizagent for bizagent in self.model.schedule.agents if isinstance(bizagent, Business_Agent)]                    
                    chosen_business = random.choice(businesses)
                    
                    if not chosen_business.flooded:
                        chosen_business.wealth += healthcare_cost_per_person * random.uniform(0.0,0.1)  # Allocate support funds to the chosen business
                    else:
                        chosen_business.wealth -= healthcare_cost_per_person * random.gauss(10,3)
                    
            for patient in  self.hospitalized_agents:
                self.continued_healthcare(patient)
        
        self.current_hour += 1  # Increment the current hour
        
        if self.current_hour / 24 == 30:
            # self.pay_taxes()    
            pass

    def continued_healthcare(self, patient):
            average_recovery_rate = 0.9
            
            if patient.recovery_rate <= average_recovery_rate:
                self.hospitalized_agents.remove(patient)
                patient.injured = False
                patient.time_injured = 0
            else:
                patient.time_injured += 1
            
            if patient.time_injured >= patient.survivability_duration:
                patient.alive = False
                patient.injured = False
                self.hospitalized_agents.remove(patient)    
                patient.preflood_non_evacuation_measure_implemented = False
                patient.postflood_adaptation_measures_planned = False
    
    def pay_taxes(self):
        # Function for paying taxes
        tax_rate = random.uniform(0, 0.05)  # Set the tax rate (adjust as needed)
        tax_amount = self.wealth * tax_rate
        self.model.government.wealth += tax_amount
        self.wealth -= tax_amount
            
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, Healthcare_Agent):
            return self.unique_id == other.unique_id
        return False



class Business_Agent(GeoAgent):
    """
    Business Agent represents commercial entities within the simulation. 
    These agents manage wealth, provide employment opportunities, and offer services to Person Agents. 
    They interact with Person Agents by offering services and contributing taxes to the government.
    """

    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        """
        Initialize a Business Agent with the provided unique identifier, model, business type, and GDP share.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - business_type: type of business represented by the agent
        - business_gdp_share: the share of the GDP attributed to the business
        - geometry: the geographical location of the business (Shapely geometry)
        - crs: the coordinate reference system of the geometry
        """
        self.wealth = None  # Share of the GDP attributed to the business
        self.type = None  # Type of business
        self.employees = []  # List to store employed individuals
        self.resilience = random.uniform(15, 25)  # Measure of the business's resilience to flooding
        self.current_hour = 0  # Initialize the current hour
        self.flooded = False  # Flag indicating if the business is flooded due to flooding
        self.time_flooded = 0  # Time since the business became flooded
        # Evacuation information
        self.last_evacuation_time = None
        self.flood_data_prediction = None

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        """
        # Get flood height for the business's geographic position
        business_flood_height = self.model.space.get_flood_height_at_position(self.geometry)

        # Check if the business is flooded based on its resilience compared to flood height
        if self.resilience < business_flood_height:
            self.flooded = True
            self.time_flooded += 1
        else:
            self.flooded = False
            self.time_flooded = 0

        # Pay taxes every 30 days
        if self.current_hour / 24 == 30:
            self.pay_taxes()
            pass

        self.current_hour += 1  # Increment the current hour

    def pay_taxes(self):
        """
        Calculate and pay taxes to the government.
        """
        
        tax_rate = random.uniform(0, 0.05)
        tax_amount = self.wealth * tax_rate
        self.model.government.wealth += tax_amount
        self.wealth -= tax_amount

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, Business_Agent):
            return self.unique_id == other.unique_id
        return False


class House_Agent(GeoAgent):
    """
    House Agent represents residential units within the simulation. Each house tracks the economic class of its residents and 
    their measures of risk perception and preparation for flooding. House Agents facilitate the resting behavior of Person Agents 
    during specific hours and manage distress situations caused by flooding.
    """

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id=unique_id, model=model, geometry=geometry, crs=crs)
        self.name = str(uuid.uuid4())
        """
        Initialize a House Agent with the provided unique identifier, model, and wealth class.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - wealth_class: the economic class of the house
        - resilience: the house's resilience to flooding
        - geometry: the geographical location of the house (Shapely geometry)
        - crs: the coordinate reference system of the geometry
        """
        # self.wealth_class = wealth_class  # Adding economy_class attribute
        self.residents = []  # List to store residents
        self.resilience = random.uniform(10, 30)  # Measure of the house's resilience to flooding
        self.current_hour = 0  # Initialize the current hour
        self.flooded = False  # Flag indicating if the house is flooded due to flooding
        self.time_flooded = 0  # Time since the house became flooded
        self.wealth = 0  # Total wealth of residents in the house

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        """
        # Get flood height for the house's geographic position
        flood_height = self.model.space.get_flood_height_at_position(self.geometry)
        # print(flood_height)

        # Check if the house is flooded based on its resilience compared to flood height
        if self.resilience < flood_height:
            self.flooded = True
            self.time_flooded += 1
        else:
            self.flooded = False
            self.time_flooded = 0

        # Calculate the total wealth of residents in the house
        self.wealth = sum(resident.income for resident in self.residents)
        self.current_hour += 1  # Increment the current hour

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, House_Agent):
            return self.unique_id == other.unique_id
        return False



class School_Agent(GeoAgent):
    """
    School Agent represents educational institutions within the simulation. 
    These agents manage resources, provide educational services, and interact with Person Agents. 
    They play a vital role in shaping the educational landscape and contribute to the economy through taxes.
    """

    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        """
        Initialize a School Agent with the provided unique identifier, model, school type, and GDP share.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - school_type: type of school represented by the agent
        - school_gdp_share: the share of the GDP attributed to the school
        - geometry: the geographical location of the school (Shapely geometry)
        - crs: the coordinate reference system of the geometry
        """

        self.wealth = None  # Share of the GDP attributed to the school
        self.types = None  # Type of school
        self.students = []  # List to store enrolled students
        self.resilience = random.uniform(15, 25)  # Measure of the school's resilience to flooding
        self.current_hour = 0  # Initialize the current hour
        self.flooded = False  # Flag indicating if the school is flooded due to flooding
        self.time_flooded = 0  # Time since the school became flooded
        # Evacuation information
        self.last_evacuation_time = None
        self.flood_data_prediction = None

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        """
        # Get flood height for the school's geographic position
        school_flood_height = self.model.space.get_flood_height_at_position(self.geometry)

        # Check if the school is flooded based on its resilience compared to flood height
        if self.resilience < school_flood_height:
            self.flooded = True
            self.time_flooded += 1
        else:
            self.flooded = False
            self.time_flooded = 0

        school_cost_rate = random.uniform(0.001, 0.01)  # Cost rate for each student
        self.num_students = len(self.students)  # Update the number of students
        
        school_cost = self.wealth * school_cost_rate * self.num_students
        self.wealth -= school_cost  # Deduct funds for rescue and shelter
        
        # Redistribute support funds to a randomly chosen business, if available
        businesses = [agent for agent in self.model.schedule.agents if isinstance(agent, Business_Agent)]
        if businesses:
            chosen_business = random.choice(businesses)
            chosen_business.wealth += school_cost  # Allocate support funds to the chosen business

        self.current_hour += 1  # Increment the current hour


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, School_Agent):
            return self.unique_id == other.unique_id
        return False    


    
class Government_Agent(GeoAgent):
    """
    Government Agent represents the governing body overseeing the simulation. 
    It collects taxes from Person and Business Agents, contributes to the support system, 
    and manages public finances, experiencing fluctuations in wealth based on taxation and support allocations.
    """
    
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        """
        Initialize a Government Agent with the provided unique identifier, model, and government GDP.

        Parameters:
        - unique_id: unique identifier for the agent
        - model: the simulation model containing this agent
        - government_gdp: the initial GDP allocated to the government
        - geometry: the geographical location of the government agent (Shapely geometry) 
        - crs: the coordinate reference system of the geometry
        """
        self.wealth = None
        self.shelter_contribution = None
        self.school_contribution = None
        self.current_hour = 0  # Initialize the current hour

    def step(self):
        """
        Execute one step of the agent's actions within the simulation model.
        """
        if self.current_hour / 24 == 30:
           self.redistribute_wealth()
        
        self.current_hour += 1  # Increment the current hour
    
    def redistribute_wealth(self):
        """
        Redistribute wealth to support systems and schools.
        """        
        
        self.shelter_contribution = random.uniform(0.01, 0.2) * self.model.shelter_gdp
        self.healthcare_contribution = random.uniform(0.01, 0.2) * self.model.healthcare_gdp
        self.school_contribution = random.uniform(0.01, 0.2) * self.model.school_gdp
        
        #healthcare_amount = self.wealth * self.healthcare_contribution
        
        # Distribute wealth to the shelter system
        self.model.shelter.wealth += self.shelter_contribution
        self.wealth -= self.shelter_contribution
        
        # Distribute wealth to the healthcare system
        self.model.healthcare.wealth += self.healthcare_contribution
        self.wealth -= self.healthcare_contribution
               
        # Distribute wealth to schools
        amount = self.school_contribution / self.model.num_schools
        for school in self.model.space.schools:
            school.wealth += amount
            self.wealth -= amount # Deduct the allocated amount from government wealth


    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, "
            f"function={self.function}, centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, Government_Agent):
            return self.unique_id == other.unique_id
        return False
        

