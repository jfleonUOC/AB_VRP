from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
# from mesa.batchrunner import BatchRunner


# Define the required Classes

class DCAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.products = 100

    def in_items (self):
        self.products += round(self.random.gauss(10, 5), 0)
        
    def out_items (self):
        self.products -= round(self.random.gauss(20, 5), 0)
        
    # def step(self):
        # print ("DC ID " + str(self.unique_id) +"- Products: " + str(self.products))
        
        
class ShopAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.products = 5
        
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
            
        # Restart counter
        self.step_counter = 0
        
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
        for agent in self.schedule.agents:
            agent.in_items()
            agent.out_items()
        self.datacollector.collect(self)
        self.schedule.step()
        self.step_counter += 1
        print("---- Step: " + str (self.step_counter))
        
       
# Define the required Functions

def calculate_stock (model):
    stock = 0
    for agent in model.schedule.agents:
        stock += agent.products
    return stock
        

# Main program execution

