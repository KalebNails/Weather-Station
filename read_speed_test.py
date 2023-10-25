#Kaleb Nails
#9/12/2023
#Updated: 10/6/2023

import serial
import socket
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Slider,RangeSlider
from bokeh.plotting import figure
import pandas as pd
import subprocess
from datetime import datetime
from bokeh.io import output_file, show

#THIS GIVE LENGTH OF THE LINE num_lines = int(subprocess.check_output("wc -l test.csv", shell=True).split()[0]) -1
#This is for hitting Ctrl C
import time
import signal
import subprocess

#bokeh serve --show read_speed_test.py port=5001
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
global_last_value = 2
global_start_value = 1

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
N_slider = RangeSlider(start=1, end = 100, value=(global_start_value ,global_last_value), step=1, title="Values seen")

def slider_callback(attr, old, new):
    global global_start_value
    global global_last_value


    global_start_value = int(new[0])
    global_last_value = int(new[1])
    #print(global_last_value)
    #print(global_start_value)

#N_slider.on_change('value',slider_callback)
N_slider.on_change('value_throttled',slider_callback)


def callback_update_data():

    global global_last_value
    global global_start_value       #print(global_last_value)

    #print(global_last_value)
    #print(global_start_value)
    #N_slider.end = int(subprocess.check_output("wc -l /var/tmp/wx/current_weather_data_logfile.csv", shell=True).split()[0]) -1
    N_slider.end = int(subprocess.check_output("wc -l ~/Downloads/2023_09_26_weather_station_data.csv", shell=True).split()[0]) -1



    #SET AN IF STATEMENT DEPENDING ON A BOX. if the box is checked then just use the second one
    #also then just take the global_last_value and change it to the length of the sliders
    #maybe add distance lock for live_read 1 so it turns into a scrolling window
    live_read = 0
    if live_read == 0:
        #data = pd.read_csv("/var/tmp/wx/current_weather_data_logfile.csv",header=0, skiprows=range(1,1+global_start_value),nrows=int(abs(global_last_value-global_start_value)))
        data = pd.read_csv("~/Downloads/2023_09_26_weather_station_data.csv",header=0, skiprows=range(1,1+global_start_value),nrows=int(abs(global_last_value-global_start_value)))


    elif live_read == 1:
        data = pd.read_csv("/var/tmp/wx/current_weather_data_logfile.csv",header=0, skiprows=range(1,1+global_start_value))
        N_slider.value = (N_slider.value[0],int(subprocess.check_output("wc -l /var/tmp/wx/current_weather_data_logfile.csv", shell=True).split()[0]) -1)


        #convert the datetime format
    data['tNow'] = pd.to_datetime(data['tNow'], format= "%Y-%m-%d %H:%M:%S.%f")


    #This resamples the data, change to S when the real data comes in
    data = data.resample('40S', on='tNow').mean()

    #After resampling tnow is often shiften down one row, which messes up all the keys, so this fixes it
    data.reset_index(inplace=True)
    #print(data)

    #This updates the data
    Temp_source.data = ({'x_values': data['tNow'], 'y_values': data['T_degC']})
    P_hPa_source.data = ({'x_values': data['tNow'], 'y_values': data['P_hPa']})
    RH_source.data = ({'x_values': data['tNow'], 'y_values': data['RH_pct']})
    Wind_N_source.data = ({'x_values': data['tNow'], 'y_values': data['Wind_N_mps']})
    Wind_E_source.data = ({'x_values': data['tNow'], 'y_values': data['Wind_E_mps']})
    Wind_D_source.data = ({'x_values': data['tNow'], 'y_values': data['Wind_D_mps']})





layout = layout([[N_slider],[T_degC_fig],[P_hPa_fig],[RH_fig],[Wind_N_fig],[Wind_E_fig],[Wind_D_fig]],sizing_mode='stretch_both')

curdoc().add_root(layout)
curdoc().theme = 'dark_minimal'



curdoc().add_periodic_callback(callback_update_data, 2000)
