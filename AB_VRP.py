from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
# from mesa.batchrunner import BatchRunner

import csv

# Define the required Parameters

PROD_DC = 100         # Initial quantity of products for DC
PROD_SH = 5         # Initial quantity of products for SH
ID_DC = 0           # First ID number for DC
ID_SH = 1000        # First ID number for SH

# Define the required Classes

class DCAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.products = PROD_DC
        self.type = "DC"

    def in_items (self):
        self.products += round(self.random.gauss(10, 5), 0)
        
    def out_items (self):
        self.products -= round(self.random.gauss(20, 5), 0)
        
    # def step(self):
        # print ("DC ID " + str(self.unique_id) +"- Products: " + str(self.products))
        
        
class ShopAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.products = PROD_SH
        self.type = "SH"
        
    def in_items (self):
        self.products += round(self.random.gauss(5, 2), 0)
        
    def out_items (self):
        self.products -= round(self.random.gauss(5, 2), 0) 

    # def step(self):
        # print ("Shop ID " + str(self.unique_id) +"- Products: " + str(self.products))
        

class MDVRPModel(Model):
    def __init__(self, N_DC, N_SH, width, height):
        self.num_DC = N_DC
        self.num_Shops = N_SH
        self.width = width
        self.height = height
        self.schedule = RandomActivation(self)
        self.space = ContinuousSpace(width, height, True)
        self.running = True
        self.step_counter = 0
        
        self.datacollector = DataCollector(
            model_reporters={"Stock": calculate_stock},
            agent_reporters={"Products": "products"})
        
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
        for i in range(self.num_DC):
            a = DCAgent(i, self)
            self.schedule.add(a)

            # Add the DCs to a random space point
            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
            
        # Create Shops
        for i in range(self.num_Shops):
            a = ShopAgent(1000+i, self)
            self.schedule.add(a)

            # Add the Shops to a random space point
            x = self.random.randrange(self.space.width)
            y = self.random.randrange(self.space.height)
            self.space.place_agent(a, (x, y))
            
        print ("Agents in model:")
        for agent in self.schedule.agents:
            print(agent.unique_id)
                
    def step(self):
        self.step_counter += 1
        for agent in self.schedule.agents:
            agent.in_items()
            agent.out_items()
        self.datacollector.collect(self)
        self.schedule.step()
        self.generate_problem()
        self.generate_network()
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
                        demand = agent.products - PROD_SH
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

model = MDVRPModel(2, 2, 250, 250)
model.initiate()
# model.step()
