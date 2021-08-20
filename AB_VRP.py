from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner

import csv
import matplotlib.pyplot as plt

from hsolver import HSolver


# Define the required Parameters

PROD_DC = 100       # Initial quantity of products for DC
PROD_SP = 5         # Initial quantity of products for SP
ID_DC = 0           # First ID number for DC
ID_SP = 1000        # First ID number for SP

DEM_AV = 5          # Demand average in SP
DEM_SD = 2          # Demand st dev in SP

# Define the required Classes

class DCAgent(Agent):
    """Depot Center Agent"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.model = model
        self.products = PROD_DC
        self.type = "DC"
        self.sup_av = self.calc_supply()[0]
        self.sup_sd = self.calc_supply()[1]

    def in_items (self):
        self.products += round(self.random.gauss(self.sup_av, self.sup_sd), 0)
        
    def out_items (self):
        self.products -= round(self.random.gauss(10, 5), 0)
        
    def calc_supply (self):
        """
        The maximum demand in SP equates to the minimum supply in DC:
        N_SP*(DEM_AV+DEM_SD) = N_DC*(SUP_AV-SUP_SD)
        The average supply equates the minimum demand:
        N_SP*(DEM_AV-DEM_SD) = N_DC*SUP_AV
        """
        sup_av = (self.model.N_SP/self.model.N_DC)*(DEM_AV-DEM_SD)
        # print("supply average: " + str(sup_av))
        sup_sd = (self.model.N_SP/self.model.N_DC)*2*DEM_SD
        # print("supply std dev: " + str(sup_sd))
        return (sup_av, sup_sd)
        
    # def step(self):
        # print ("DC ID " + str(self.unique_id) +"- Products: " + str(self.products))
        
        
class SPAgent(Agent):
    """Shop Agent"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.products = PROD_SP
        self.type = "SP"
        
    def in_items (self):
        self.products += round(self.random.gauss(5, 2), 0)
        
    def out_items (self):
        self.products -= round(self.random.gauss(DEM_AV, DEM_SD), 0) 

    # def step(self):
        # print ("Shop ID " + str(self.unique_id) +"- Products: " + str(self.products))
        

class MDVRPModel(Model):
    def __init__(self, N_DC, N_SP, width, height):
        self.N_DC = N_DC
        self.N_SP = N_SP
        self.width = width
        self.height = height
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.running = True
        self.step_counter = 0
        
        self.datacollector = DataCollector(
            model_reporters={"Stock": calculate_stock},
            agent_reporters={"Products": "products"})
        
        self.solver = HSolver()
        self.routes = None
        
    def initiate(self):
        
        # Delete existing agents from schedule
        for agent in self.schedule.agents:
            self.schedule.remove(agent)
            
        # Restart counter (MESA's first step is 0)
        self.step_counter = -1
        
        # Clean input.csv, network.csv files
        self.generate_problem()
        self.generate_network()
        
        # Create DC
        for i in range(self.N_DC):
            a = DCAgent(i, self)
            self.schedule.add(a)

            # Add the DCs to a random space point
            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
            
        # Create Shops
        for i in range(self.N_SP):
            a = SPAgent(1000+i, self)
            self.schedule.add(a)

            # Add the Shops to a random space point
            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
            
        print ("Agents in model:")
        for agent in self.schedule.agents:
            print(agent.unique_id)
            
        # self.calc_supply()
                
    def step(self):
        self.step_counter += 1
        for agent in self.schedule.agents:
            agent.in_items()
            agent.out_items()
        self.datacollector.collect(self)
        self.schedule.step()
        self.generate_problem()
        self.generate_network()
        dc_sp, dc_sp_pos, outfiles = self.solver.solve_MD_short()
        self.routes = self.solver.aggregate_VRP(*outfiles)
        print("---- Step: " + str (self.step_counter))
        
    def generate_problem (self):
        agent_demand = self.datacollector.get_agent_vars_dataframe()
        with open('input.csv', 'w', newline='') as csvinput:
            writer = csv.writer(csvinput)
            header = ["ID","Type","Xpos","Ypos","Products","Demand"]
            writer.writerow(header)
            prev_step = self.step_counter - 1
            if prev_step > 0:
                for agent in self.schedule.agents:
                    demand = agent.products - agent_demand.loc[(prev_step, agent.unique_id),"Products"]
                    row = [agent.unique_id, agent.type, agent.pos[0], agent.pos[1], agent.products, demand]
                    writer.writerow(row)
            else: # control for step 0 which is not considered in MESA
                for agent in self.schedule.agents:
                    if agent.type == "DC":
                        demand = agent.products - PROD_DC
                    else:
                        demand = agent.products - PROD_SP
                    row = [agent.unique_id, agent.type, agent.pos[0], agent.pos[1], agent.products, demand]
                    writer.writerow(row)
                    
    def generate_network (self):
        with open('network.csv', 'w', newline='') as csvnetwork:
            writer = csv.writer(csvnetwork)
            header = ["Orig","Dest","Cost","Active"]
            writer.writerow(header)
            for orig in self.schedule.agents:
                for dest in self.schedule.agents:
                    if orig != dest:
                        dist = self.space.get_distance(orig.pos, dest.pos)
                        row = [orig.unique_id, dest.unique_id, dist, "Y"]
                        writer.writerow(row)
    



# Define the required Functions

def calculate_stock (model):
    stock = 0
    for agent in model.schedule.agents:
        stock += agent.products
    return stock
        

# Main program execution
if __name__ == "__main__":

    
    # Single step Run (comment if not used):
    model = MDVRPModel(2, 10, 250, 250)
    model.initiate()
    model.step()   
    
    # Complete Run (comment if not used):
    # model = MDVRPModel(3, 10, 250, 250)
    # model.initiate()
    # for i in range(100):
    #     model.step()
    # Stock_all = model.datacollector.get_model_vars_dataframe()
    # Stock_all.plot()
    
    # Batch Run (comment if not used):
    # fixed_params = {"N_SP": 10,
    #                 "width": 250,
    #                 "height": 250}
    # variable_params = {"N_DC": (1,3,5,7)}

    # batch_run = BatchRunner(MDVRPModel,
    #                         variable_params,
    #                         fixed_params,
    #                         iterations=5,
    #                         max_steps=100,
    #                         model_reporters={"Stock": calculate_stock})
    # batch_run.run_all()
    # run_data = batch_run.get_model_vars_dataframe()
    # plt.scatter(run_data.N_DC, run_data.Stock)
