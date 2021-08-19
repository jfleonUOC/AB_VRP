import csv
import numpy as np
from itertools import tee


class HSolver ():
    """Solver with multiple heuristics for the VRP variants"""
    
    # def __init__(self):
    
    def solve_MD_short (self):
        """Solve Multi-Depot part of the problem by shortest path"""
        #TODO: delete all vrp*.csv files in folder
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
                    
            # print(dc_sp)
            # print(dc_sp_pos)
            # print(max(dc_sp)[0])
            # print(int(max(dc_sp)[0]))
            for dc in range(int(max(dc_sp)[0])+1):
                f_id = "vrp_"+str(dc)+".csv"
                # print(dc)
                with open(f_id, 'w', newline='') as csvoutput:
                    writer = csv.writer(csvoutput)
                    for sol in dc_sp:
                        if int(sol[0]) == dc:
                            # print (sol[1])
                            for dict_line in read:
                                if dict_line["ID"] == sol[1]:
                                    # print(dict_line)
                                    sp_x = dict_line["Xpos"]
                                    sp_y = dict_line["Ypos"]
                                    sp_demand = dict_line["Demand"]
                                    row = [sp_x, sp_y, sp_demand]
                                    # print(row)
                                    writer.writerow(row)
        return dc_sp, dc_sp_pos

    
    def solve_VRP_greedy (self):
        """Solve single VRP by using simple greedy behaviour"""
        pass
    
    def calc_dist (self, pos1, pos2):
        """Calculate distance between 2 positions"""
        x1, y1 = pos1
        x2, y2 = pos2
        dx = np.abs(x1 - x2)
        dy = np.abs(y1 - y2)
        return np.sqrt(dx * dx + dy * dy)
    
# Main program execution
if __name__ == "__main__":
    solver = HSolver()
    solver.solve_MD_short()
    