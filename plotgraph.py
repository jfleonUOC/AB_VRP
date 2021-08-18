from mesa import Agent, Model

def plot_Model_values (Model):
    index = Model.step_counter
    Stock_all = Model.datacollector.get_model_vars_dataframe()
    Stock_current = Stock_all.tail(index)
    return Stock_current