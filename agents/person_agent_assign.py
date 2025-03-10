import uuid
from . import flood_agents as FA

from scipy.stats import beta
import random
import numpy as np


def create_person_agents(model):
    """
    Create person agents in the model with demographics, wealth classes, and other attributes.
    
    Steps:
    1. Define proportions of different wealth classes and ethnicities.
    2. Shuffle and assign wealth classes and ethnicity groups to agents.
    3. Initialize agents with attributes: age, wealth, education, gender, mobility, etc.
    4. Add agents to the simulation's space and schedule.
    5. Assign agents to houses, businesses, and schools.
    
    Parameters:
    - model: The simulation model containing spatial agents and parameters.
    """
    model.num_upper_class_persons = int(0.024 * model.num_persons)  # 2%
    model.num_upper_middle_class_persons = int(0.204 * model.num_persons)  # 7%
    model.num_middle_class_persons = int(0.446 * model.num_persons)  # 24.9%
    model.num_lower_class_persons = model.num_persons - model.num_upper_class_persons - model.num_upper_middle_class_persons - model.num_middle_class_persons

    model.wealth_classes = (
        ["Upper_Class"] * model.num_upper_class_persons +
        ["Upper_Middle_Class"] * model.num_upper_middle_class_persons +
        ["Middle_Class"] * model.num_middle_class_persons +
        ["Lower_Class"] * model.num_lower_class_persons
    )
    random.shuffle(model.wealth_classes)

    model.num_indigenous_persons = int(0.05 * model.num_persons)
    model.num_immigrant_persons = int(0.23 * model.num_persons)
    model.num_canadian_persons = model.num_persons - model.num_indigenous_persons - model.num_immigrant_persons

    ethnicity_groups = (
        ["Indigenous"] * model.num_indigenous_persons +
        ["Immigrant"] * model.num_immigrant_persons +
        ["Canadian"] * model.num_canadian_persons
    )
    random.shuffle(ethnicity_groups)

    model.num_working_class_persons = 0
    model.num_age_0_14_persons = 0
    model.num_age_15_64_persons = 0
    model.num_age_65_100_persons = 0
    model.num_male_persons = 0
    model.num_female_persons = 0

    model.persons_by_wealth_class = {wealth_class: [] for wealth_class in model.wealth_classes}

    for i in range(model.num_persons):
        unique_id = uuid.uuid4().int
        person = FA.Person_Agent(unique_id, model, geometry=None, crs = model.crs)
        
        assign_age(model, i, person)
        assign_wealth(model, i, person)
        assign_mobility(model, person)
        person.ethnicity = ethnicity_groups[i]
        assign_education(model, person)
        assign_gender(model, person)
        
        model.space.add_agents(person)
        model.schedule.add(person)

        assign_working_class(model, person)
        assign_SES_index(model, person)

        model.persons_by_wealth_class[person.wealth_class].append(person)

    assign_persons_to_houses(model)
    assign_persons_to_businesses(model)
    assign_persons_to_schools(model)    


def assign_working_class(model, agent):
    if 18 <= agent.age <= 64:
        agent.working_class = True
        model.num_working_class_persons += 1           


def assign_education(model, person):
    if person.age >= 18:          
        if random.uniform(0,1) <= model.perc_education_people:
            person.education = 1  # Most educated with full understanding of flood risks
        else:
            person.education = random.uniform(0.5,0.9)   # Partial education
    else:
        person.education = 0.4/18*person.age     # Education scales with age for individuals under 18


def assign_gender(model, person):           
    perc_male = 0.49
    if random.uniform(0,1) <= perc_male:            
        model.num_male_persons += 1            
        person.gender = "Male"
    else:
        model.num_female_persons += 1
        person.gender = "Female"
        
     
def assign_age(model, i, person):
    if i < int(0.16 * model.num_persons):	# Assign age for [0-14] age group
        person.age = random.randint(0, 14)
        model.num_age_0_14_persons += 1
    elif  int(0.16 * model.num_persons) <= i < int(0.81 * model.num_persons):	# [15-64] age group
        person.age = random.randint(15, 64)              
        model.num_age_15_64_persons += 1
    else:  				                # Assign age for [65-100] age group
        person.age = random.randint(65, 100)            
        model.num_age_65_100_persons += 1        


def assign_wealth(model, i, person):
    person.wealth_class = model.wealth_classes[i]  # Assign economy class based on shuffled list

    if person.wealth_class == "Upper_Class":
        person.income = random.uniform(250000, 500000)/365 * 10 #Two weeks saved income
    elif person.wealth_class == "Upper_Middle_Class":
        person.income = random.uniform(100000, 250000)/365 * 10
    elif person.wealth_class == "Middle_Class":
       person.income = random.uniform(50000, 100000)/365 * 10 
    elif person.wealth_class == "Lower_Class":
        person.income = random.uniform(0, 50000)/365 * 10 
    
    model.persons_gdp += person.income
    model.total_gdp += model.persons_gdp


def assign_SES_index(model, agent):   # High value represents high vulnerability
    # Age vulnerability
    if agent.age in [0,14]:
        age_vul = 1
    elif agent.age in [15-64]:
        age_vul = 0.1
    else:
        age_vul = 0.8
        
    # Education vulnerability 
    edu_vul = (1-0.9*agent.education)
    
    # Gender vulnerability
    if agent.gender == "Male":
        gen_vul = 0.1
    else:
        gen_vul = 1

    # Ethnicity vulnerability
    if agent.ethnicity == "Canadian":
        eth_vul = 0.1
    elif agent.ethnicity == "Immigrant":
        eth_vul = 0.8
    else:
        eth_vul = 1
    
    # Wealth status vulnerability
    if agent.wealth_class == "Upper_Class":
        wth_vul = 0.01
    elif agent.wealth_class == "Upper_Middle_Class":
        wth_vul = 0.1
    elif agent.wealth_class == "Middle_Class":
        wth_vul = 0.8
    else: 
        wth_vul = 1

    agent.SES_1 = (age_vul + edu_vul + gen_vul + eth_vul + wth_vul )/5
    agent.SES_2 = (age_vul * edu_vul * gen_vul * eth_vul * wth_vul )**(1/5) 
    agent.vulnerability = (agent.SES_1 + agent.SES_2) / 2
    

def assign_mobility(model, person):
    # Define parameters for the beta function of age
    a_age, b_age = 2, 5
    
    # Define parameters for the logistic function of wealth
    k_wealth, x0_wealth = 0.1, 50
    
    # Normalize age between 0 and 1
    x_age = person.age / 100
    
    # Compute mobility based on age using the beta function
    age_mobility = beta.pdf(x_age, a_age, b_age)
    
    # Compute mobility based on wealth using the logistic function
    wealth_mobility = 1 / (1 + np.exp(-k_wealth * (person.income - x0_wealth)))
    
    # Combine mobility from age and wealth
    person.mobility = age_mobility + wealth_mobility


def assign_persons_to_houses(model):
    for economy, persons in model.persons_by_wealth_class.items():
        persons_copy = persons[:]  # Make a copy of the list because pop functions removes agents from original list - person_by_economy
        houses = model.space.houses
        num_houses = len(houses)
        residents_per_house = len(persons_copy) // num_houses

        # Keep track of persons and their availability
        adults_available = [person for person in persons_copy if person.age >= 18]

        # Assign residents to houses
        for idx, house in enumerate(houses):
            # Determine the number of residents for this house
            if idx < num_houses * residents_per_house:
                num_residents = residents_per_house
            else:
                num_residents = residents_per_house + 1

            # Assign one adult resident to the house if available
            if adults_available:
                adult_resident = adults_available.pop(0)
                house.residents.append(adult_resident)
                adult_resident.household = house
                adult_resident.homeless = False
                # print(adult_resident.household.geometry)
                model.space.move_agent(adult_resident, adult_resident.household.geometry)
                num_residents -= 1

            # Assign remaining residents to the house
            for _ in range(num_residents):
                if persons_copy:
                    resident = persons_copy.pop(0)  # Take the next resident from the copied list
                    house.residents.append(resident)
                    resident.household = house
                    resident.homeless = False
                    model.space.move_agent(resident, resident.household.geometry)

        # Handle any remaining persons
        while persons_copy:
            resident = persons_copy.pop()
            house = random.choice(houses)
            house.residents.append(resident)
            resident.household = house
            resident.homeless = False
            model.space.move_agent(resident, resident.household.geometry)


def assign_persons_to_businesses(model):
    # Ensure there are businesses available
    if not model.space.businesses:
        print("No businesses available for assignment.")
        return
    
    for economy, persons in model.persons_by_wealth_class.items():
        for person in persons:
            # Assign only if the person is working class and not already employed
            if person.working_class and not person.employed:
                business = random.choice(model.space.businesses)
                business.employees.append(person)
                person.employed = True
                person.workplace = business


def assign_persons_to_schools(model):
    # Ensure there are schools available
    if not model.space.schools:
        print("No schools available for assignment.")
        return
    
    for economy, persons in model.persons_by_wealth_class.items():
        for person in persons:
            # Check if the person is within the school age range and not already assigned to a school
            if 5 <= person.age < 18 and not person.schoolplace:
                school = random.choice(model.space.schools)
                school.students.append(person)
                person.student = True
                person.schoolplace = school