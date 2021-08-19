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

if __name__ == "__main__":
    model = MDVRPModel(3, 10, 250, 250)
    model.initiate()
    model.step()
    solver = HSolver()
    dc_sp, dc_sp_pos = solver.solve_MD_short()
    dwg = draw_MD_sol(model,dc_sp_pos)
    dwg.save()


# DRAWING

# dwg.add(dwg.circle((100, 200), AGENT_R, fill='red'))
# dwg.add(dwg.text('Test', insert=(100, 200)))
# dwg.add(dwg.line((10, 10), (100, 200), stroke='#000000', stroke_width=2))
