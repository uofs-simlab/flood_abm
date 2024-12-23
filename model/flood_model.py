"""
Flood Model Simulation

This model simulates a flood scenario where agents (persons, homes, businesses, shelter system, healthcare, and government) 
interact within a grid-based environment. Each agent has specific attributes and behaviors, such as risk perception, 
movement, distress reactions, and financial transactions. The simulation tracks the effects of flooding on agent behavior, 
economic activities, rescue operations, and shelter systems.

"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
from shapely.geometry import Point

from space.flood_space import StudyArea
from mesa import Model
from agents import person_agent_assign as psn_agnt

from mesa.time import RandomActivation

from data_collection import data_collect

class FloodModel(Model):
    """
    The Model Class defines the environment and interaction rules for the flood simulation. 
    It manages the grid-based environment, schedules agent actions, tracks time progression, 
    and monitors the effects of flooding on agents, their behaviors, and economic activities.
    """
    def __init__(self, N_persons,
                 shelter_cap_limit, healthcare_cap_limit, shelter_funding, healthcare_funding, pre_flood_days, flood_days, post_flood_days, 
                 houses_file, businesses_file, schools_file, shelter_file, healthcare_file, government_file,
                 flood_file_1, flood_file_2, flood_file_3, model_crs):
        super().__init__()
        
        self.crs = model_crs
    
        self.space = StudyArea(self, houses_file, businesses_file, schools_file, shelter_file, healthcare_file, government_file, model_crs)
        
        self.total_days = pre_flood_days + flood_days + post_flood_days
        self.pre_flood_days = pre_flood_days
        self.flood_days = flood_days
        self.flood_file_1 = flood_file_1
        self.flood_file_2 = flood_file_2
        self.flood_file_3 = flood_file_3
        
        # Calculate times for flood maps
        self.disaster_period = None
        
        self.evacuation_time = (self.pre_flood_days - 7) * 24
        self.last_evacuation_time = self.pre_flood_days * 24
        
        self.hours_before_rescue = 2
        self.hours_before_healthcare = 0
        
        flood_interval = (self.flood_days * 24) // 6
        self.flood_map_add_times = [
            self.last_evacuation_time + 1,
            self.last_evacuation_time + 1 + flood_interval,
            self.last_evacuation_time + 1 + 2 * flood_interval
        ]
        self.flood_map_remove_times = [
            self.flood_map_add_times[0] + 3 * flood_interval,
            self.flood_map_add_times[1] + 3 * flood_interval,
            self.flood_map_add_times[2] + 3 * flood_interval
        ]
        
        self.perc_education_people = 0.89     
        self.schedule = RandomActivation(self)
        
        self.num_persons = N_persons
        
        self.num_houses = len(self.space.houses)
        self.num_businesses = len(self.space.businesses)
        self.num_schools = len(self.space.schools)
        
        self.shelter_cap_limit = shelter_cap_limit/100 * self.num_persons
        self.healthcare_cap_limit = healthcare_cap_limit/100 * self.num_persons
        
        # Share total gdp among population, businesses and government
        self.business_gdp = (self.num_persons * 22000)/365 * 14 #* self.total_days
        self.school_gdp = (self.num_persons * 1200)/365 * 14 #* self.total_days
        self.shelter_gdp = (self.num_persons * 4200)/365 * 14 #* self.total_days
        self.healthcare_gdp = (self.num_persons * 4200)/365 * 14 #* self.total_days
        self.government_gdp = (self.num_persons * 7000)/365 * 14 #* self.total_days
        self.persons_gdp = 0
        self.total_gdp = self.business_gdp + self.school_gdp  + self.shelter_gdp + self.healthcare_gdp + self.government_gdp      
        
    #------------Initialize government agent-----------------------------------
        self.government = self.space.government[0]
        self.government.wealth = self.government_gdp
        self.schedule.add(self.government)
            
    #------------Initialize shelter system agent------------------------------
        self.shelter = self.space.shelter[0]
        self.shelter.wealth = self.shelter_gdp 
        self.shelter.capacity_limit = self.shelter_cap_limit
        self.schedule.add(self.shelter)
                      
    #------------Initialize healthcare system agent------------------------------
        self.healthcare = self.space.healthcare[0]
        self.healthcare.wealth = self.healthcare_gdp 
        self.healthcare.capacity_limit = self.healthcare_cap_limit
        self.schedule.add(self.healthcare) 
    
    #---------Initialize businesses, schools and houses--------------------
        self._initialize_businesses()

        # Initialize schools
        self._initialize_schools()
        
        # Initialize houses
        self._initialize_houses()
        
    #-----------------Initialize person agents--------------------------------
        psn_agnt.create_person_agents(self)
        
        data_collect.data_collection(self)      
        
    #-------------------------------Step function------------------------------
    def step(self):
        # Baseline, Pre, During. Post flood periods        
        if self.evacuation_time <= self.schedule.time <= self.last_evacuation_time:
            self.disaster_period = 'pre_flood_evac_period'
        if self.last_evacuation_time < self.schedule.time < (self.pre_flood_days + self.flood_days) * 24:
            self.disaster_period = 'during_flood'
        if self.schedule.time >= (self.pre_flood_days + self.flood_days) * 24:                
            self.disaster_period = 'post_flood'
        
        # Handle flood map addition
        if self.schedule.time == self.flood_map_add_times[0]:
            self.add_flood_maps(self.flood_file_1)
        elif self.schedule.time == self.flood_map_add_times[1]:
            self.add_flood_maps(self.flood_file_2)
        elif self.schedule.time == self.flood_map_add_times[2]:
            self.add_flood_maps(self.flood_file_3)
        
        # Handle flood map removal
        if self.schedule.time == self.flood_map_remove_times[0]:
            self.remove_flood_maps(self.flood_file_3)         
        elif self.schedule.time == self.flood_map_remove_times[1]:
            self.remove_flood_maps(self.flood_file_2)
        elif self.schedule.time == self.flood_map_remove_times[2]:
            self.remove_flood_maps(self.flood_file_1)
    
        self.datacollector.collect(self)
        self.schedule.step()
    
        # Define the path to the 'data_collection' folder
        data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_collection"))
        os.makedirs(data_folder, exist_ok=True)  # Ensure the folder exists
        
        # Define the full path to the output file
        file_path = os.path.join(data_folder, "serverrun_results.csv")
        
        # Save the data to 'data_collection/model_data.csv'
        data = self.datacollector.get_model_vars_dataframe()
        data.to_csv(file_path, index=False)
        
    
    def add_flood_maps(self, flood_file):
        self.space._load_flood_maps_from_file(self, flood_file, self.crs)

    def remove_flood_maps(self, flood_file):  # remove flood areas as were added
        self.space.remove_flood_maps(flood_file)

    #-------------------------Initialize businesses----------------------------
    
    def _initialize_businesses(self):
        avg_business_wealth = self.business_gdp / self.num_businesses    
        
        for business in self.space.businesses:
            business.wealth = avg_business_wealth
        
            self.schedule.add(business)

    #---------------------------Initialize schools-----------------------------
    
    def _initialize_schools(self):
        # School GDP share
        avg_school_wealth = self.school_gdp / self.num_schools
        
        # Assign all types to each school and distribute GDP
        for school in self.space.schools:
            school.wealth = avg_school_wealth
            
            # Add school agent to the schedule
            self.schedule.add(school)

    def _initialize_houses(self):
        # Assign random resilience to houses
        for house in self.space.houses:
            self.schedule.add(house)    
    
    #-------------Notify Shelter and get healthcare----------------------------
                       
    def notify_shelter(self, agent):
        "Get sheltered"
        if agent not in self.shelter.sheltered_agents and agent.time_stranded >= self.hours_before_rescue:
            
            if len(self.shelter.sheltered_agents) < self.shelter.capacity_limit:
                self.shelter.sheltered_agents.append(agent)
                                
                shelter_position = self.get_random_point_in_polygon(self.shelter.geometry)
                self.space.move_agent(agent, shelter_position)
                
                agent.stranded = False
                agent.time_stranded = 0                               
    
    def get_random_point_in_polygon(self, polygon):
        """Generate a random point within a given polygon."""
        min_x, min_y, max_x, max_y = polygon.bounds
        while True:
            random_point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if polygon.contains(random_point):
                return random_point
                 
    def receive_healthcare(self, patient):
        if len(self.healthcare.hospitalized_agents) < self.healthcare.capacity_limit:
            if patient not in self.healthcare.hospitalized_agents:
                self.healthcare.hospitalized_agents.append(patient)
                
                healthcare_position = self.get_random_point_in_polygon(self.healthcare.geometry)
                self.space.move_agent(patient, healthcare_position)
