# Flood Effects on Vulnerable Groups and Decision-Making Processes

This repository contains an **Agent-Based Model (ABM)** that simulates the effects of flooding on vulnerable groups, their decision-making processes, and community-level responses. Using **Mesa** for agent-based modeling and **Mesa-Geo** for GIS integration, the model captures interactions between individuals, households, businesses, shelters, healthcare systems, and government entities under pre-flood, flood, and post-flood conditions. The ABM evaluates vulnerability, resilience, and decisions made during disasters based on socio-economic factors, demographics, and spatial characteristics.

---

## Folder Structure

- **agents/**
  - `flood_agents.py` – Defines core agents like Person, Business, House, Shelter, Healthcare, and Government agents.
  - `person_agent_assign.py` – Assigns demographics, wealth, education, and mobility attributes to person agents.
  - `decision_making_module.py` – Implements decision-making logic for agents (e.g., evacuation, adaptation measures).

- **model/**
  - `flood_model.py` – Core model logic that initializes the environment, agents, and simulation steps.

- **space/**
  - `flood_space.py` – Handles the GIS environment and spatial interactions using Mesa-Geo.

- **run/**
  - `flood_serverrun.py` – Runs an interactive server-based visualization of the simulation.
  - `flood_batchrun.py` – Runs batch simulations to collect and analyze large-scale results.
  - `scenario_test_batchrun.py` – Tests specific flood scenarios and outputs results.

- **calgary_map_data/**
  - Contains spatial data such as building layouts and flood maps used for GIS integration.

- **data_collection/**
  - `data_collect.py` – Handles data collection during model runs.
  - Includes scripts for graph generation and post-simulation analysis.

- **data_for_paper/**
  - Contains simulation results and generated graphs used for research papers.

---

## How to Run the Model

1. **Clone the Repository**  
   Open a terminal and run the following command:  
   ```bash
   git clone https://github.com/your-username/repo-name.git
   cd repo-name
   ```

2. **Install Dependencies**  
   Install the required libraries using the `requirements.txt` file:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Interactive Server**  
   To launch the interactive server-based visualization:  
   ```bash
   cd run
   python flood_serverrun.py
   ```
   - Open the browser and go to `http://localhost:8521` to view the simulation.

4. **Run Batch Simulations**  
   To execute multiple simulations and save results:  
   ```bash
   python flood_batchrun.py
   ```

5. **Test Specific Scenarios**  
   For scenario-based batch runs, use:  
   ```bash
   python scenario_test_batchrun.py
   ```

---

## Installation

Ensure Python 3.8+ is installed on your machine. Use the following command to install the required libraries:  
```bash
pip install -r requirements.txt
```

### Key Libraries:
- Mesa 2.1.2
- Mesa-Geo 0.7.1
- Pandas
- NumPy
- Shapely
- Matplotlib
- Seaborn
- Psutil

---

## Further Reading

1. **Mesa**: [Mesa Documentation](https://mesa.readthedocs.io/)
2. **Mesa-Geo**: [Mesa-Geo Documentation](https://mesa-geo.readthedocs.io/)
3. **Literature**: *(Pending Submission)* – Title: "Flood Effects on Vulnerable Groups and Decision-Making Processes" *(to be updated upon publication)*.

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for feedback.

---

## License

This project is licensed under the **MIT License**. See the `license` file for details.

---
