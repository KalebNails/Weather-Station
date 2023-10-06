#Kaleb Nails
#9/12/2023

import serial
import socket
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure

import pandas as pd

from datetime import datetime
from bokeh.io import output_file, show

#import asyncio
####import cProfile
####pr = cProfile.Profile()


#This is for hitting Ctrl C
import time
import signal
import threading
#python -m snakeviz temp_dumpfile.prof
###pr.enable()


def handle_interrupt(signal, frame):
    print("Ctrl+C pressed. Performing cleanup or other actions...")
    # Add your code to perform cleanup or other actions here
    ###pr.print_stats()
    ###pr.dump_stats("temp_dumpfile.prof") # to see the results put this in bash: python -m snakeviz temp_dumpfile.prof
    ###pr.disable()
    exit(0)  # Terminate the script gracefully

signal.signal(signal.SIGINT, handle_interrupt)

#tail -f current_weather_data_logfile.csv
#head current_weather_data_logfile.csv
#ps ax|grep pyth  shows all current python processes
#cd /var/tmp/wx
#current_weather_data_logfile.csv this is the pointer file to the most current file in the file database
global_last_value = 5
#set up your variables to be empty for first iteration
tNow = []
T_degC =[]
P_hPa = []
RH_pct = []
Wind_N_mps = []
Wind_E_mps = []
Wind_D_mps = []

Temp_source = ColumnDataSource(data={'x_values': tNow,'y_values': T_degC})
P_hPa_source = ColumnDataSource(data={'x_values': tNow,'y_values': P_hPa})
RH_source = ColumnDataSource(data={'x_values': tNow,'y_values': RH_pct})
Wind_N_source = ColumnDataSource(data={'x_values': tNow,'y_values': Wind_N_mps})
Wind_E_source  = ColumnDataSource(data={'x_values': tNow,'y_values': Wind_E_mps})
Wind_D_source  = ColumnDataSource(data={'x_values': tNow,'y_values': Wind_D_mps})


#set up your figures
T_degC_fig = figure(title = "Temp (C)", x_axis_type='datetime',output_backend="webgl")
T_degC_fig.line(x='x_values', y='y_values',source=Temp_source)

P_hPa_fig = figure(title = "P_hPa", x_axis_type='datetime',output_backend="webgl")
P_hPa_fig.line(x='x_values', y='y_values',source=P_hPa_source)

RH_fig = figure(title = "RH (%)", x_axis_type='datetime',output_backend="webgl")
RH_fig.line(x='x_values', y='y_values',source=RH_source)

Wind_N_fig = figure(title = "Wind_N", x_axis_type='datetime',output_backend="webgl")
Wind_N_fig.line(x='x_values', y='y_values',source=Wind_N_source)

Wind_E_fig = figure(title = "Wind_E", x_axis_type='datetime',output_backend="webgl")
Wind_E_fig.line(x='x_values', y='y_values',source=Wind_E_source)

Wind_D_fig = figure(title = "Wind_D", x_axis_type='datetime',output_backend="webgl")
Wind_D_fig.line(x='x_values', y='y_values',source=Wind_D_source)


#This defines the slider
N_slider = Slider(start=1, end = global_last_value, value=global_last_value, step=1, title="Values seen")

def slider_callback(attr, old, new):
    global global_last_value
    global_last_value = new

#N_slider.on_change('value',slider_callback)
N_slider.on_change('value_throttled',slider_callback)


##############################################################
def read_csv_thread():
    global data
    while True:
        new_data = pd.read_csv("/var/tmp/wx/current_weather_data_logfile.csv")
        with data_lock:
            data = new_data

data_lock = threading.Lock()
data_thread = threading.Thread(target=read_csv_thread)
data_thread.daemon = True  # Allow the thread to be killed when the main program exits
data_thread.start()



def callback_update_data():

    #data = pd.read_csv("/var/tmp/wx/current_weather_data_logfile.csv")

    global data
    with data_lock:


        #last value controls how large the window is
        global global_last_value
        #print(global_last_value)
        #> myRange = range(0,10000,n)
        #n=100 # downsample by this factor
        #ADD an idx to range below so its only a sampling
        #idx = range(0,10000,n)

        filter_condition = data.index >= len(data['tNow']) - global_last_value
        N_slider.end = len(data['tNow'])

        #This print shows the truth table from above, and proves it takes the newest values
        #print(filter_condition)


        #convert the datetime format
        data['tNow'] = pd.to_datetime(data['tNow'], format= "%Y-%m-%d %H:%M:%S.%f")

        #Grab the relevent data based on last value

        tNow= data.loc[filter_condition,"tNow"]
        T_degC = data.loc[filter_condition,"T_degC"]
        P_hPa= data.loc[filter_condition,"P_hPa"]
        RH_pct = data.loc[filter_condition,"RH_pct"]
        Wind_N_mps = data.loc[filter_condition,"Wind_N_mps"]
        Wind_E_mps = data.loc[filter_condition,"Wind_E_mps"]
        Wind_D_mps = data.loc[filter_condition,"Wind_D_mps"]

        #This updates the data
        Temp_source.data ={'x_values': tNow,'y_values': T_degC}
        P_hPa_source.data ={'x_values': tNow,'y_values': P_hPa}
        RH_source.data ={'x_values': tNow,'y_values': RH_pct}
        Wind_N_source.data ={'x_values': tNow,'y_values': Wind_N_mps}
        Wind_E_source.data ={'x_values': tNow,'y_values': Wind_E_mps}
        Wind_D_source.data ={'x_values': tNow,'y_values': Wind_D_mps}

        #Temp_source.stream({'x_values': tNow, 'y_values': T_degC})
        #P_hPa_source.stream({'x_values': tNow, 'y_values': P_hPa})
        #RH_source.stream({'x_values': tNow, 'y_values': RH_pct})
        #Wind_N_source.stream({'x_values': tNow, 'y_values': Wind_N_mps})
        #Wind_E_source.stream({'x_values': tNow, 'y_values': Wind_E_mps})
        #Wind_D_source.stream({'x_values': tNow, 'y_values': Wind_D_mps})







layout = layout([[N_slider],[T_degC_fig],[P_hPa_fig],[RH_fig],[Wind_N_fig],[Wind_E_fig],[Wind_D_fig]],sizing_mode='stretch_both')

curdoc().add_root(layout)
curdoc().theme = 'dark_minimal'






curdoc().add_periodic_callback(callback_update_data, 1000)
