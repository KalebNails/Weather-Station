# Weather-Station #
This is the supporting code to the remote weather station

## discord_meteogram.py ## 
This is the final version of the meteograph designed to be executed by the Discord bot (as seen in my examples/python/discord repositories). Aside from occasional bugs, it is ready for production deployment. There are a few peculiarities in this code. Firstly, it saves the image of the meteogram without displaying it when run, as the Discord bot should handle the execution and doesn't require popups. Additionally, there are some unconventional steps in the 'wind3D_to_graphable' function. You'll notice that I resample the dataframe, clear the contents of 'windmax' in the original dataframe, combine it with the original dataframe, sort by time, fill forward to ensure erased slots have sampled values, and then erase any data points with a time value with nanoseconds of 0000 ns. I do this because realistically, only the sampled data will have a time exactly at a nanosecond interval. If this happens, the program might encounter issues, and it would be challenging to identify why. However, for our smaller use case, this is an acceptable bug. I adopted this approach due to the constraints of the meteogram library, which only plots values with the same dimensional length. Therefore, I couldn't just resample and superimpose it over the graph. While there may be a better way to achieve this, the presented solution is the most straightforward one I could develop independently without modifying the meteogram library itself.

## Bokeh_weather_station.py ##
this is an earlier version of read_speed_test that uses a different method to plot 10M data points. This has some threading in it that just constantly rereads the CSV, not an incredible method to hand this issue.

## read_speed_test.py ##
This uses bokeh to display data points one multiple graphs with a window that the user can control. This can work with roughly up to 10M points of data and still have pretty reliable loading speeds and times. 
The most important things to save time I learned was:
1. not reading the entire file, there is a way with pandas to only read certain rows, and there is also a way using the terminal to get how many rows are in a csv without opening it
2. using Webgl setting in some of the bokeh functions, it is just a empirically faster way to graph
3. throttlelock the slider so it doesn't try to make a new plot for each point you pass over while moving the slider itself
4. pandas resample, this helps the bokeh graph faster, but this is not that fast itself, and there is a sweet spot between bokeh plotting speed and resample speed


## Meeting Questions 10/12/2023 ##
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/5571e9c8-c885-41e3-819d-9fc379b9b20b)


I had a couple questions about the image above. 
1. Does the realtive humidity and temp scales and measurements seem reasonable?
2. The mean sea level pressure is a solid block, and idea what its supposed to look like?
3. I removed the wind graph because if you look at the image below this is what its supposed to look like is below:
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/849fd789-8018-46e4-8ce7-f4996577e647)


Wind Max is over 3 seconds is that a correct time frame for our puposes over 24 hours? Also it says direction, I looked this up and it says its in degrees from some fixed lattitude or long, since we are recording 3d wind should I just remove the vertical component when dislpaying this?


Also I hit the none fatal error below:
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/5fc9831b-59e9-4d2c-96f5-51b3159eba2c)

does the equation: deg_C + 243.5 *value / (17.67 - value)
immediately mean anything to you? I don't exactly know where this takes place in the code and is a little hard to find, but I was wondering if you could possibly point me in a direction in if its reltated to RH or temp or etc.
