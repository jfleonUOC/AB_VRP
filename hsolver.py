import csv
import numpy as np
from itertools import tee
import os
import re

class Node():
    """Node class to easily retrieve info."""
    def __init__(self, ID, xpos, ypos, demand):
        self.ID = ID
        self.xpos = xpos
        self.ypos = ypos
        self.demand = demand
        
    # def node_pos(self, ID):
    #     if ID = self.ID
    #     return self.xpos, self.ypos
        
    def print_node_info(self):
        info = [self.ID,self.xpos, self.ypos,self.demand]
        print("Node ID {0} at ({1}, {2}) with demand: {3}".format(*info))

class HSolver ():
    """Solver with multiple heuristics for the VRP variants"""
    
    # def __init__(self):
    
    def solve_MD_short (self):
        """Solve Multi-Depot part of the problem by shortest path"""
        # Delete all vrp*.csv files in folder
        dir_curr = os.getcwd()
        for file in os.listdir(dir_curr):
            if re.search(r"(vrp_\d{1,2}).csv$", file):
                # print("removing: {0}".format(file))
                os.remove(os.path.join(dir_curr, file))
                
        # Solve the MD problem
        with open("input.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            read = list(reader)
            dc_sp = []
            dc_sp_pos = []
            for row_sp in read:
                dist_min = np.inf
                if row_sp["Type"] == "SP":
                    dist_min = np.inf
                    for row_dc in read:
                        if row_dc["Type"] == "DC":
                            pos1 = (int(row_sp["Xpos"]),int(row_sp["Ypos"]))
                            pos2 = (int(row_dc["Xpos"]),int(row_dc["Ypos"]))
                            dist = self.calc_dist(pos1, pos2)
                            if dist < dist_min:
                                dist_min = dist
                                dc_min = row_dc["ID"]
                                dc_min_pos = (row_dc["Xpos"],row_dc["Ypos"])
                    dc_sp.append((dc_min,row_sp["ID"]))
                    sp_pos = (row_sp["Xpos"],row_sp["Ypos"])
                    dc_sp_pos.append((dc_min_pos,sp_pos))
                    
            # Output the vrp*.csv files
            outfiles = []
            for dc in range(int(max(dc_sp)[0])+1):
                f_name = "vrp_"+str(dc)+".csv"
                outfiles.append(f_name)
                with open(f_name, 'w', newline='') as csvoutput:
                    writer = csv.writer(csvoutput)
                    # write depot coordinates with demand = 0
                    for dict_line in read:
                        if dict_line["ID"] == str(dc):
                            writer.writerow([dict_line["Xpos"],dict_line["Ypos"],0])
                    # write shop coordinates with demand
                    for sol in dc_sp:
                        if int(sol[0]) == dc:
                            for dict_line in read:
                                if dict_line["ID"] == sol[1]:
                                    sp_x = dict_line["Xpos"]
                                    sp_y = dict_line["Ypos"]
                                    sp_demand = dict_line["Demand"]
                                    row = [sp_x, sp_y, sp_demand]
                                    writer.writerow(row)
                
        return dc_sp, dc_sp_pos, outfiles

    
    def solve_VRP_greedy (self, vrp_f, input_f="input.csv"):
        """
        Solve single VRP by using simple greedy behaviour
        Demand not considered
        """
        # Create candidate list
        with open(vrp_f, newline='') as vrpfile:
            vrp_reader = csv.reader(vrpfile)
            dc_line = next(vrp_reader)
            # vrp_read = list(vrp_reader)
            with open(input_f, newline='') as inputfile:
                input_reader = csv.DictReader(inputfile)
                input_read = list(input_reader)
                dc_x, dc_y = (int(dc_line[0]),int(dc_line[1]))
                dc_id = self.map_coord_to_id ((dc_x, dc_y))
                dc = Node (dc_id, dc_x, dc_y, 0)
                # dc.print_node_info()
                candidates = [dc]
                for node in vrp_reader:
                    n_x, n_y = (int(node[0]),int(node[1]))
                    n_id = self.map_coord_to_id ((n_x, n_y))
                    n_demand = float(node[2])
                    n = Node(n_id, n_x, n_y, n_demand)
                    # n.print_node_info()
                    candidates.append(n)
        # print("There are {0} nodes in vrp.".format(len(candidates)))
        # Iterate inside candidate list to generate route order
        route = [candidates[0].ID]
        while len(candidates) > 1:
            dist_min = np.inf
            pos1 = (candidates[0].xpos,candidates[0].ypos)
            candidates.pop(0)
            next_n = []
            for node in candidates:
                pos2 = (node.xpos,node.ypos)
                dist = self.calc_dist(pos1, pos2)
                if dist < dist_min:
                    dist_min = dist
                    next_n = node
            i = candidates.index(next_n)
            candidates.pop(i)
            candidates.insert(0, next_n)
            route.append(next_n.ID)
        # print("greedy route for {0}: {1}".format(vrp_f, route))

        #TODO: write output
        return route
    
    def aggregate_VRP (self, *args):
        routes = []
        for file in args:
            route = self.solve_VRP_greedy(file)
            routes.append(route)
        return routes
        
    
    def calc_dist (self, pos1, pos2):
        """Calculate distance between 2 positions"""
        x1, y1 = pos1
        x2, y2 = pos2
        dx = np.abs(x1 - x2)
        dy = np.abs(y1 - y2)
        return np.sqrt(dx * dx + dy * dy)
    
    def map_coord_to_id (self, pos):
        with open("input.csv", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            read = list(reader)
            x, y = pos
            agent_id = "not"
            for line in read:
                if line["Xpos"] == str(x) and line ["Ypos"] == str(y):
                    agent_id = line["ID"]
            message = "Agent {0} found at ({1}, {2})".format(agent_id,x,y)
        # print(message)
        if agent_id != "not":
            return agent_id
        
    #TODO: create "node_from_coord" function: from coordinates create node object with info from input.csv
        
    
# Main program execution
if __name__ == "__main__":
    solver = HSolver()
    # solver.solve_MD_short()
    solver.solve_VRP_greedy("vrp_1.csv")
   