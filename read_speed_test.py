#Kaleb Nails
#modified from: https://unidata.github.io/MetPy/latest/examples/meteogram_metpy.html
#This is for plotting weather data using the MetPy library, which I in fact have no strong opinions on

import datetime as dt

import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

from metpy.calc import dewpoint_from_relative_humidity
from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo
from metpy.units import units
import pandas as pd

import code #code.interact(local=dict(globals(), **locals()))
import dask.dataframe as dd



# I just stole this code from: https://www.freecodecamp.org/news/python-decorators-explained-with-examples/
#I added some modifications

from functools import wraps
import tracemalloc
from time import perf_counter

def measure_performance(func):
    '''Measure performance of a function'''

    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        start_time = perf_counter()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        finish_time = perf_counter()
        print(f'Function: {func.__name__}')
        #print(f'Method: {func.__doc__}')
        print(f'Memory usage:\t\t {current / 10**6:.6f} MB \n'
              f'Peak memory usage:\t {peak / 10**6:.6f} MB ')
        print(f'Time elapsed is seconds: {finish_time - start_time:.6f}')
        print(f'{"-"*40}')
        tracemalloc.stop()
        return result
    return wrapper

def calc_mslp(t, p, h):
    return p * (1 - (0.0065 * h) / (t + 0.0065 * h + 273.15)) ** (-5.257)




# Make meteogram plot
class Meteogram:
    """ Plot a time series of meteorological data from a particular station as a
    meteogram with standard variables to visualize, including thermodynamic,
    kinematic, and pressure. The functions below control the plotting of each
    variable.
    TO DO: Make the subplot creation dynamic so the number of rows is not
    static as it is currently. """
    @measure_performance
    def __init__(self, fig, dates, probeid, time=None, axis=0):
        """
        Required input:
            fig: figure object
            dates: array of dates corresponding to the data
            probeid: ID of the station
        Optional Input:
            time: Time the data is to be plotted
            axis: number that controls the new axis to be plotted (FOR FUTURE)
        """
        if not time:
            time = dt.datetime.utcnow()
        self.start = dates[0]
        self.fig = fig
        self.end = dates[-1]
        self.axis_num = 0
        self.dates = mpl.dates.date2num(dates)
        self.time = time.strftime('%Y-%m-%d %H:%M UTC')
        self.title = f'Latest Ob Time: {self.time}\nProbe ID: {probeid}'

    @measure_performance
    def plot_winds(self, ws, wd, wsmax, plot_range=None):
        """
        Required input:
            ws: Wind speeds (knots)
            wd: Wind direction (degrees)
            wsmax: Wind gust (knots)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT WIND SPEED AND WIND DIRECTION
        self.ax1 = fig.add_subplot(4, 1, 1)
        ln1 = self.ax1.plot(self.dates, ws, label='Wind Speed')
        self.ax1.fill_between(self.dates, ws, 0)
        self.ax1.set_xlim(self.start, self.end)
        ymin, ymax, ystep = plot_range if plot_range else (0, 8, 2)
        self.ax1.set_ylabel('Wind Speed (knots)', multialignment='center')
        self.ax1.set_ylim(ymin, ymax)
        self.ax1.yaxis.set_major_locator(MultipleLocator(ystep))
        self.ax1.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)

        #I did this in an odd way and matched the times, it was a bad way to do it, so i have to pull every 3rd value here, i can do this because we already sample at 1 herze
        ln2 = self.ax1.plot(self.dates[::3], wsmax[::3], '.r', label='3-sec Wind Speed Max',markersize=3.5)

        ax7 = self.ax1.twinx()
        ln3 = ax7.plot(self.dates, wd, '.k', linewidth=0.5, label='Wind Direction')
        ax7.set_ylabel('Wind\nDirection\n(degrees)', multialignment='center')
        ax7.set_ylim(0, 360)
        ax7.set_yticks(np.arange(45, 405, 90))
        ax7.set_yticklabels(['NE', 'SE', 'SW', 'NW'])
        lines = ln1 + ln2 + ln3
        labs = [line.get_label() for line in lines]
        ax7.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
        ax7.legend(lines, labs, loc='upper center',
                   bbox_to_anchor=(0.5, 1.2), ncol=3, prop={'size': 12})
    @measure_performance
    def plot_thermo(self, t, td, plot_range=None):
        """
        Required input:
            T: Temperature (deg F)
            TD: Dewpoint (deg F)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT TEMPERATURE AND DEWPOINT
        ymin, ymax, ystep = plot_range if plot_range else (10, 90, 5)
        self.ax2 = fig.add_subplot(4, 1, 2, sharex=self.ax1)
        ln4 = self.ax2.plot(self.dates, t, 'r-', label='Temperature')
        self.ax2.fill_between(self.dates, t, td, color='r')

        self.ax2.set_ylabel('Temperature\n(F)', multialignment='center')
        self.ax2.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        self.ax2.set_ylim(ymin, ymax)
        self.ax2.yaxis.set_major_locator(MultipleLocator(ystep))

        ln5 = self.ax2.plot(self.dates, td, 'g-', label='Dewpoint')
        self.ax2.fill_between(self.dates, td, self.ax2.get_ylim()[0], color='g')

        ax_twin = self.ax2.twinx()
        ax_twin.set_ylim(ymin, ymax)
        ax_twin.yaxis.set_major_locator(MultipleLocator(ystep))
        lines = ln4 + ln5
        labs = [line.get_label() for line in lines]
        ax_twin.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))

        self.ax2.legend(lines, labs, loc='upper center',
                        bbox_to_anchor=(0.5, 1.2), ncol=2, prop={'size': 12})

    @measure_performance
    def plot_rh(self, rh, plot_range=None):
        """
        Required input:
            RH: Relative humidity (%)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT RELATIVE HUMIDITY
        ymin, ymax, ystep = plot_range if plot_range else (0, 100, 5)
        self.ax3 = fig.add_subplot(4, 1, 3, sharex=self.ax1)
        self.ax3.plot(self.dates, rh, 'g-', label='Relative Humidity')
        self.ax3.legend(loc='upper center', bbox_to_anchor=(0.5, 1.22), prop={'size': 12})
        self.ax3.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        self.ax3.set_ylim(ymin, ymax)
        self.ax3.yaxis.set_major_locator(MultipleLocator(ystep))

        self.ax3.fill_between(self.dates, rh, self.ax3.get_ylim()[0], color='g')
        self.ax3.set_ylabel('Relative Humidity\n(%)', multialignment='center')
        self.ax3.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))
        axtwin = self.ax3.twinx()
        axtwin.set_ylim(ymin, ymax)
        axtwin.yaxis.set_major_locator(MultipleLocator(ystep))

    @measure_performance
    def plot_pressure(self, p, plot_range=None):
        """
        Required input:
            P: Mean Sea Level Pressure (hPa)
        Optional Input:
            plot_range: Data range for making figure (list of (min,max,step))
        """
        # PLOT PRESSURE
        ymin, ymax, ystep = plot_range if plot_range else (970, 1080, 4)
        self.ax4 = fig.add_subplot(4, 1, 4, sharex=self.ax1)
        self.ax4.plot(self.dates, p, 'm', label='Mean Sea Level Pressure')
        self.ax4.set_ylabel('Mean Sea\nLevel Pressure\n(mb)', multialignment='center')
        self.ax4.set_ylim(ymin, ymax)
        self.ax4.yaxis.set_major_locator(MultipleLocator(ystep))

        axtwin = self.ax4.twinx()
        axtwin.set_ylim(ymin, ymax)
        axtwin.yaxis.set_major_locator(MultipleLocator(ystep))
        axtwin.fill_between(self.dates, p, axtwin.get_ylim()[0], color='m')
        axtwin.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d/%H UTC'))

        self.ax4.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2), prop={'size': 12})
        self.ax4.grid(which='major', axis='y', color='k', linestyle='--', linewidth=0.5)
        # OTHER OPTIONAL AXES TO PLOT
        # plot_irradiance
        # plot_precipitation

# set the starttime and endtime for plotting, 24 hour range
endtime = dt.datetime(2016, 3, 31, 22, 0, 0, 0)
starttime = endtime - dt.timedelta(hours=24)

# Height of the station to calculate MSLP
hgt_example = 292.

# Parse dates from .csv file, knowing their format as a string and convert to datetime
def parse_date(date):
    return dt.datetime.strptime(date.decode('ascii'), '%Y-%m-%d %H:%M:%S')

#Converts 3D components to windspeed, wind gust, and wind direction
def wind3D_to_graphable(windE, windN, windD, times):
    print(f"windE: {windE}")
    ws = np.sqrt(windE**2 + windN**2 + windD**2) #calculate the wind speed

    print("WIND SPEED:")
    print(ws)

    #resample down to 3 seconds
    wind_max_3s = pd.DataFrame({ 'Times': times,'WindSpeed': ws})
    print(f"original \n {wind_max_3s}" )

    wind_max_3s.set_index('Times', inplace=True)

    wind_max_3s_sampled = wind_max_3s.resample('3S').max().ffill()
    wind_max_3s_sampled['origin'] = 'new'



    #Reset the values and then merge the dataframes, then fill foward, and remove the uneeded times which I am assuming is at 0000 ms
    wind_max_3s['WindSpeed'] = np.nan
    wind_max_3s['origin'] = 'old'
    combined_df = pd.concat([wind_max_3s, wind_max_3s_sampled], ignore_index=False)
    combined_df = combined_df.sort_values(by='Times').reset_index(drop=False)
    #print(f"prefilter \n {combined_df}" )


    combined_df['WindSpeed'] = combined_df['WindSpeed'].ffill()
    print(len(combined_df))


    #This removes the times generated by resmaple
    #wsmax = combined_df[combined_df['Times'].isin(times)]
    wsmax = combined_df.loc[combined_df['origin'] == 'old', 'WindSpeed']
    #print(f"aftfilter \n {combined_df}" )

    #wsmax = combined_df[~(combined_df['Times'].dt.microsecond == 0)]

    #this is temporary filler of just zero values
    wd = pd.Series(np.zeros(len(windN)))

    print(len(wsmax))
    print(len(windN))

    #code.interact(local=dict(globals(), **locals()))

    return [ws, wd, wsmax]




    # Now, wind_max_3s has rows for all original_times, and missing values are filled with NaN
    # You can fill NaN values with your preferred method, for example, forward filling (ffill)
    #wind_max_3s = wind_max_3s.ffill()
    #print(f"fill foward:\n {wind_max_3s}" )


#This function reads the data and saves it to a dict
@measure_performance
def read_data_csv_custom():
    #declare your sample factor:
    sample_factor = 15
    #testdata = pd.read_csv("~/Downloads/2023_09_26_weather_station_data.csv")
    testdata = pd.read_csv("~/Downloads/2023_12_03_weather_station_data.csv")

    #print(testdata.dtypes)
    #print(testdata.keys())\

    #resample your data based on your sample factor
    testdata = testdata.iloc[::sample_factor]

    #NOTE: this is to fix a unit error in the incomming data
    testdata['Press_Pa'] = testdata['Press_Pa']/100
    #testdata['tNow'] = pd.to_datetime(testdata['tNow'], format= "%Y-%m-%d %H:%M:%S.%f")
    testdata['tNow'] = pd.to_datetime(testdata['tNow'], format="%Y-%m-%d %H:%M:%S")

    total_rows = len(testdata)
    #gets rid of a device by zero error, double check later on
    subset_columns = ['Press_Pa', 'Temp_C', 'Hum_RH']

    # Create a boolean mask to identify rows with any zero values in the specified columns
    mask = (testdata[subset_columns] == 0).any(axis=1)

    #FIX unit convserstions for the preasure
    # Filter the DataFrame to keep rows without any zero values in the specified columns
    testdata = testdata[~mask]
    removed_rows = total_rows - len(testdata)
    print(f"{removed_rows} out of {total_rows} rows were removed.")

    #convert the wind units
    [ws, wd,wsmax] = wind3D_to_graphable(testdata['u_m_s'],testdata['w_m_s'],testdata['w_m_s'],testdata['tNow'])

    testdata = testdata.to_dict('list')




    # Temporary variables for ease
    temp = testdata['Temp_C']
    print(type(temp))
    print(type(ws))


    pressure = testdata['Press_Pa']
    rh = testdata['Hum_RH']
    ws = ws.tolist()
    wsmax = wsmax.tolist()
    wd = wd.tolist()
    date = testdata['tNow']




    # data = {
    #     'dewpoint': dewpoint_from_relative_humidity((np.array(temp) * units.degC).to(units.K), np.array(rh) / 100.).to(units('degF')),
    #     'air_temperature': (np.array(temp) * units('degC')).to(units('degF')),
    #     'mean_slp': calc_mslp(np.array(temp), np.array(pressure), hgt_example) * units('hPa'),
    #     'relative_humidity': np.array(rh),
    #     'times': np.array(date)
    # }

    data = {'wind_speed': (np.array(ws) * units('m/s')).to(units('knots')),
            'wind_speed_max': (np.array(wsmax) * units('m/s')).to(units('knots')),
            'wind_direction': np.array(wd) * units('degrees'),
            'dewpoint': dewpoint_from_relative_humidity((np.array(temp) * units.degC).to(units.K),
                                                        np.array(rh) / 100.).to(units('degF')),
            'air_temperature': (np.array(temp) * units('degC')).to(units('degF')),
            'mean_slp': calc_mslp(np.array(temp), np.array(pressure), hgt_example) * units('hPa'),
            'relative_humidity': np.array(rh), 'times': np.array(date)}

    return data

print("start reading file")
data= read_data_csv_custom()
print("done returning data dictionary")


# ID For Plotting on Meteogram
probe_id = '0102A'

#This plots all your figures
fig = plt.figure(figsize=(20, 16))
meteogram = Meteogram(fig, data['times'], probe_id)
meteogram.plot_winds(data['wind_speed'], data['wind_direction'], data['wind_speed_max'])
meteogram.plot_thermo(data['air_temperature'], data['dewpoint'])
meteogram.plot_rh(data['relative_humidity'])
print(data['mean_slp'])
meteogram.plot_pressure(data['mean_slp'])
fig.subplots_adjust(hspace=0.5)

#Saves the figures to png
print("saving")
plt.savefig("deleteme.png",dpi=600)
print("saved")
plt.show()
