import svgwrite
from mesa import Agent, Model
from AB_VRP import *
from hsolver import HSolver


SPC_PAD = 20    # Padding around model space (for visualization only)
AGENT_R = 5     # Agent Display Radius

def draw_Agents_simple (Model):
    dwg = svgwrite.Drawing('img.svg', profile='tiny')
    dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
    for agent in Model.schedule.agents:
        dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
    return dwg

def draw_Agents_products (Model):
    dwg = svgwrite.Drawing('img.svg', profile='tiny')
    dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
    for agent in Model.schedule.agents:
        if agent.unique_id < 1000:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='red'))
        else:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
        dwg.add(dwg.text(agent.products, insert=agent.pos))
    return dwg

def draw_Agents_positions (Model):
    dwg = svgwrite.Drawing('img.svg', profile='tiny')
    dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
    for agent in Model.schedule.agents:
        if agent.unique_id < 1000:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='red'))
        else:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
        dwg.add(dwg.text(agent.pos, insert=agent.pos))
    return dwg

def draw_Agents_id (Model):
    dwg = svgwrite.Drawing('img.svg', profile='tiny')
    dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
    for agent in Model.schedule.agents:
        if agent.unique_id < 1000:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='red'))
        else:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
        dwg.add(dwg.text(agent.unique_id, insert=agent.pos))
        dwg.add(dwg.text(agent.products, fill="green", insert=(agent.pos[0],agent.pos[1]+10)))
    return dwg

def draw_MD_sol (Model,dc_sp_pos):
    dwg = svgwrite.Drawing('img.svg', profile='tiny')
    dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
    for arc in dc_sp_pos:
        dwg.add(dwg.line(arc[0], arc[1], stroke='#000000', stroke_width=2))
    for agent in Model.schedule.agents:
        if agent.unique_id < 1000:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='red'))
        else:
            dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
        dwg.add(dwg.text(agent.unique_id, insert=agent.pos))
    return dwg

def draw_VRP_sol (Model, routes=None):
    if routes == None:
        dwg = draw_Agents_id(Model)
    else:
        dwg = svgwrite.Drawing('img.svg', profile='tiny')
        dwg.viewbox(-SPC_PAD, -SPC_PAD, Model.width+2*SPC_PAD, Model.height+2*SPC_PAD)
        
        map_trip = []
        for dc in range(len(routes)):
            trip = []
            for sp in range(len(routes[dc])):
                # print (type(routes[dc][sp]))
                for agent in Model.schedule.agents:
                    # print(type(agent.unique_id))
                    if int(agent.unique_id) == int(routes[dc][sp]):
                        if agent.unique_id < 1000:
                            dc_pos = agent.pos
                        # print("found {0} and {1}".format(agent.unique_id, routes[dc][sp]))
                        trip.append(agent.pos)
            trip.append(dc_pos)
            map_trip.append(trip)
        
        # Convert in arcs instead of positions:
        map_trip_arcs = []
        for trip in map_trip:
            trip_arcs = []
            count = 0
            for pos in trip:
                if count == 0:
                    prev_pos = pos
                    count +=1
                else:
                    trip_arcs.append((prev_pos,pos))
                    prev_pos = pos
            map_trip_arcs.append(trip_arcs)
        
        # Draw the trip arcs:        
        for trip in map_trip_arcs:
            for arc in trip:
                dwg.add(dwg.line(arc[0], arc[1], stroke='#C0C0C0', stroke_width=2))
        for agent in Model.schedule.agents:
            if agent.unique_id < 1000:
                dwg.add(dwg.circle(agent.pos, AGENT_R, fill='red'))
            else:
                dwg.add(dwg.circle(agent.pos, AGENT_R, fill='blue'))
            dwg.add(dwg.text(agent.unique_id, insert=agent.pos))
            if agent.products > 0:
                dwg.add(dwg.text(agent.products, fill="green", insert=(agent.pos[0],agent.pos[1]+10)))
            else:
                dwg.add(dwg.text(agent.products, fill="red", insert=(agent.pos[0],agent.pos[1]+10)))
    return dwg

if __name__ == "__main__":
    model = MDVRPModel(3, 10, 250, 250)
    model.initiate()
    model.step()
    solver = HSolver()
    dc_sp, dc_sp_pos, outfiles = solver.solve_MD_short()
    routes = solver.aggregate_VRP(*outfiles)
    dwg = draw_VRP_sol(model, routes)
    # dwg = draw_MD_sol(model,dc_sp_pos)
    dwg.save()


# DRAWING

# dwg.add(dwg.circle((100, 200), AGENT_R, fill='red'))
# dwg.add(dwg.text('Test', insert=(100, 200)))
# dwg.add(dwg.line((10, 10), (100, 200), stroke='#000000', stroke_width=2))
