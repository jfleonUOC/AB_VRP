from tkinter import Tk, Button, Menu, Label, StringVar, messagebox
from PIL import ImageTk, Image

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from agentgraph import *
from plotgraph import *
from AB_VRP import *

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

from threading import Thread
from time import sleep


# Define the required Parameters
PLTSIZE = (3, 2)    # Plot Size (width, height)
DPI = 100           # Plot Dots Per Inch (default = 100)
IMG_X = 1           # Space (agents) Image X position (column)
IMG_Y = 2           # Space (agents) Image Y position (row)
PLT_X = 2           # Plot X position (column)
PLT_Y = 2           # Plot Y position (row)
FRQ_STP = 0.2       # Step frequency

N_DC = 3            # Number of DC Agents (Depot Center)
N_SP = 10           # Number of SP Agents (Shops)
MDL_X = 250         # Model Width
MDL_Y = 250         # Model Height


# Define the required Classes


# Define the required Functions

def dummy_message ():
    print("dummy message")
    
def create_img (Model, routes=None):
    # dwg = draw_Agents_products(Model)
    # dwg = draw_Agents_positions(Model)
    dwg = draw_VRP_sol(Model, routes)
    dwg.save()
    drawing = svg2rlg("img.svg") 
    renderPM.drawToFile(drawing, "img.png", fmt="PNG")
    image_out = "img.png"
    return image_out
    
def display_img (image_in, tk_column, tk_row):
    img = ImageTk.PhotoImage(Image.open(image_in))
    img_panel = Label(root, image = img)
    img_panel.image = img
    img_panel.grid(column=tk_column, row=tk_row)
    return img_panel

def update_plot (model, tk_column, tk_row):
    fig = Figure(figsize=PLTSIZE, dpi=DPI)
    stock = plot_Model_values(model)
    fig.add_subplot().plot(stock)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(column=tk_column, row=tk_row)

def reset_model (model):
    model.initiate()
    img = create_img(model, model.routes)
    display_img(img, IMG_X, IMG_Y)
    update_plot(model, PLT_X, PLT_Y)
    step_counter.set("Step: " + str(model.step_counter))
    print("Model reset. Running: " + str(running))
    return model
    
def step_model ():
    model.step()
    img = create_img(model, model.routes)
    display_img(img, IMG_X, IMG_Y)
    update_plot(model, PLT_X, PLT_Y)
    step_counter.set("Step: " + str(model.step_counter))

def running_model():
    global running
    while True:
        model.step()
        img = create_img(model, model.routes)
        display_img(img, IMG_X, IMG_Y)
        update_plot(model, PLT_X, PLT_Y)
        step_counter.set("Step: " + str(model.step_counter))
        sleep(FRQ_STP)
        if running == False:
            break

def play_stop_model ():
    global running
    running = not running
    if running:
        print("Running Model. Running: " + str(running))
        B1["text"] = "Stop"
        B2["state"] = "disabled"
        run_thread=Thread(target=running_model, daemon=True)
        run_thread.start()
        running = True
        return running
    else:
        print ("Model Stopped. Running: " + str(running))
        B1["text"] = "Play"
        B2["state"] = "normal"
        running = False
        return running
    
def on_closing():
    global running
    running = False
    B1["text"] = "Play"
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        

# Main program execution

if __name__ == "__main__":
    
    model = MDVRPModel(N_DC, N_SP, MDL_X, MDL_Y)
    model.initiate()
    
    global running
    running = False
    
    print("Model started. Running: " + str(running))

    #GUI
    root = Tk()
    root.title("Agent Based Tkinter")
    
    play_text = StringVar(root)
    if running == False:
        play_text.set("Play")
    else:
        play_text.set("Stop")
    
    #Create buttons
    B1 = Button(root, text ="Play", width=10, command = play_stop_model)
    B1.grid(column=1, row=3)
    B2 = Button(root, text ="Step", width=10, command = step_model)
    B2.grid(column=1, row=4)
    B3 = Button(root, text ="Reset", width=10, command = lambda: reset_model(model))
    B3.grid(column=1, row=5)

    #Create Menu
    MenuBar=Menu(root)
    root.config(menu=MenuBar)
    DBMenu=Menu(MenuBar, tearoff=0)
    DBMenu.add_command(label="Dummy Message", command=dummy_message)
    MenuBar.add_cascade(label="Actions", menu=DBMenu)
    TemplateMenu=Menu(MenuBar, tearoff=0)
    TemplateMenu.add_command(label="Help", command=dummy_message)
    TemplateMenu.add_command(label="About", command=dummy_message)
    MenuBar.add_cascade(label="Info", menu=TemplateMenu)
    
    #Insert Image
    image_agents = create_img(model, model.routes)
    img_panel = display_img(image_agents, IMG_X, IMG_Y)
    
    #Insert Plot
    update_plot(model, PLT_X, PLT_Y)

    #Insert Step Counter
    step_counter = StringVar(root)
    Stp_ctr = Label(root, textvariable=step_counter)
    step_counter.set("Step: -")
    Stp_ctr.grid(column=1, row=1)

    #End
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
