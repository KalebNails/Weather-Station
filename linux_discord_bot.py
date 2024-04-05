#!/usr/bin/env python
#Kaleb Nails
#pip3 install metpy
#pip3 install dask
#pip3 install discord


# As a programmer I would like to admit this is not my most organized work.
# Its not awful it just could be make shorter/better by either combining booleans
# or checking for the inverse of the program. But this is a live version, and is serviced
# so the original formating was not complementary to future plans. Now armed with this experience
# the next bot I make will have a much cleaner tree.

import subprocess
import discord
import sys
import os
from datetime import datetime, timedelta
import time
import re
import json

intents = discord.Intents.all()
# This sets up a default set of intents
#reading messages is not default
client = discord.Client(intents=intents)


#this tracks how many times it has rebooted:
def load_reboot_count():
    try:
        with open('reboot_count.json', 'r+') as f:
            print("file found")
            data = json.load(f)
            print(data)
            data["reboots"] = data["reboots"] + 1
            data["reboot_dates"].append(str(datetime.now()))
            f.seek(0) #makes sure it overwrites itself
            json.dump(data,f)
            return data["reboots"]
    #this will create the file if it doesnt exist
    except FileNotFoundError:
        with open('reboot_count.json', 'w') as f:
            print("file not found, creating new file")
            data = {"reboots":1,"reboot_dates":[]}
            json.dump(data,f,indent=4)
            print("new file made")
        return 1


#this prints on bot boot up
@client.event
async def on_ready():
    print('Bot is online and ready')
    await discord.utils.get(client.get_all_channels(), name='whats-the-ip').send(f"Hello, I'm John Pheasant Kennedy on the Linux machine. This will be my #{load_reboot_count()} bootup. \n Please type 'help' if you would like a list of commands.")

# This checks for the date arguement
def contains_date(discord_message):
    # Split the message into words
    words = discord_message.split()

    # Iterate through each word to check for the date format
    date_cell = []
    for word in words:
        if len(word) == 10 and word.count('_') == 2:
            # Check if the word has the format "YYYY_MM_DD"
            try:
                print("im trying")
                year, month, day = map(int, word.split('_'))
                # You can add additional checks for valid date ranges if needed
                if 2022 <= year <= 2200 and 1 <= month <= 12 and 1 <= day <= 31:

                    date_cell.append({'year':year,'month':month,'day':day })

            except ValueError:
                # Ignore if there is a ValueError (e.g., non-integer parts)
                print("error in for word in word loop")
                pass
    print(date_cell)
    return  date_cell


#This lists all of the fast files that where saved
def fast_files(date):
    directory = "/var/tmp/wx"
    pattern = re.compile(f"^{date}.*Anemometer.csv$")
    files = os.listdir(directory)

    # Find the matching files
    matching_files = [file for file in files if pattern.match(file)]

    if matching_files:
        print("Matching files found:")
        for file in matching_files:
            print(file)
        return matching_files

    else:
        print("No matching files found.")
        return None
    
    

@client.event
async def on_message(message):

    #This is very important and keeps the bot from infinately replying to its own messages
    if message.author == client.user:
        #print('my own message')
        return

    #This checks to see if a user asks for an IP adress
    if message.channel.name == 'whats-the-ip':# and message.content == 'ip?':
        print('correct channel')
        print('the message is: {}'.format(message.content))

#METO COMMAND
        directory_location = "/var/tmp/wx/"

        if 'meto' in message.content.lower():#'ip?':
            try:
                print('its true')
                python_script_path = 'discord_meteogram.py'

                #argnum dictates how many arguements have as an input and sort the dates in order
                date_cell = contains_date(message.content.lower())
                print(f"the date cell is outside function {date_cell}")

                #sort the data by date
                print(f"the unsorted date_cell: \n {date_cell}")
                date_cell = sorted(date_cell, key=lambda x: (x['year'], x['month'], x['day']))
                print(f"the sorted date_cell: \n {date_cell}")

                #Runs from yesterdays data
                if 'previous' in message.content.lower():
                    await message.channel.send('''Hello, I am John Pheasent Kennedy.
                        As a bot perfection is the final goal, unfortunately, my programer does not have this goal.
                        Thus this feature has been delayed until further notice, as there is a compatability issue with this specific
                        command that will be fixed in a future patch.''')

                        #previous_weather_data_logfile.csv
                        # subprocess.run(['python',python_script_path]) #######################


                #checks for the propper amounts of dates
                elif  0<= len(date_cell) <= 2:

                    #THINK I CAN DELETE THE NEXT 3 lines
                    #for i in date_cell:
                        #python_script_path += f" {i['year']}_{str(i['month']).zfill(2)}_{str(i['day']).zfill(2)}"
                        #print(python_script_path)

                    if len(date_cell) == 0:
                        python_script_path = 'discord_meteogram.py'
                        print(python_script_path)
                        await message.channel.send("Generating todays data from the linux machine")
                        subprocess.run(['python',python_script_path]) #######################
                        await message.channel.send( file=discord.File('meteogram_image.png'))

                    #double check file exists
                    elif len(date_cell)==1:
                        print('using one provided date')
                        file_path = f"{directory_location}{date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}_weather_station_data.csv"

                        if os.path.exists(file_path):
                                print("File exists.")

                                #python_script_path = f"discord_meteogram.py {date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}"
                                python_script_path = f"{date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}"

                                print(python_script_path)
                                await message.channel.send(f"Date exists. Generating linux from {file_path}")
                                #subprocess.run(['python',python_script_path]) #######################
                                subprocess.run(['python','discord_meteogram.py',python_script_path]) #######################

                                await message.channel.send( file=discord.File('meteogram_image.png'))
                        else:
                            print(f"File {file_path} does not exist. defaulting to current date")
                            await message.channel.send(f" {file_path} {date_end} does not exist ")



                    #This is for a range of 2 dates
                    elif len(date_cell)==2:
                        print('using two provided date')
                        date_start = f"{date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}"
                        date_end =  f"{date_cell[1]['year']}_{str(date_cell[1]['month']).zfill(2)}_{str(date_cell[1]['day']).zfill(2)}"
                        print(date_start)
                        print(date_end)

                        #Convert date format
                        start_date = datetime.strptime(date_start, '%Y_%m_%d')
                        end_date = datetime.strptime(date_end, '%Y_%m_%d')

                        # Generate a list of strings of all the dates in between start and end dates
                        date_list = []
                        current_date = start_date
                        while current_date <= end_date:
                            date_list.append(current_date.strftime('%Y_%m_%d'))
                            current_date += timedelta(days=1)

                        # Print the list of dates
                        print(date_list)
                        #Check if all the files exist
                        file_path_list = [f"{directory_location}{date_temp}_weather_station_data.csv" for date_temp in date_list]
                        print(file_path_list)
                        all_exist = all(os.path.exists(file_path_tmp) for file_path_tmp in file_path_list)

                        if all_exist:
                            # Run the subprocess
                            print(f"Date exist between {date_start} {date_end}.")

                            print(python_script_path)
                            await message.channel.send(f"Date exist between {date_start} {date_end}. Generating from linux")
                            #subprocess.run(['python',python_script_path]) #######################
                            subprocess.run(['python','discord_meteogram.py',date_start,date_end])
                            await message.channel.send( file=discord.File('meteogram_image.png'))

                        else:
                            print("Not all files exist.")
                            await message.channel.send(f"not all dates exist between {date_start} and {date_end}.")

                else:
                    error_message = '''invalid amount of dates sent please enter following the example inputs below:
                        current date: meto
                        specific date: meto 2024_08_01
                        date range: meto 2023_06_05 2024_08_01'''

                    print(error_message)
                    await message.channel.send(error_message)

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")

#HELP COMMAND
        if 'help' in message.content.lower():#'ip?':
            try:
                await message.channel.send(
                    "______\n **LIST OF COMMANDS** (case insensitive):\n \n"
                    "meto: \n *Produces a meteogram graph of today*\n \n"
                    "meto YYYY_MM_DD: \n *Will return the data at a specific date*\n \n"
                    "meto YYYY_MM_DD YYYY_MM_DD: \n *Creates a graph of the fusion between all of the dates*\n \n"
                    "ifconfig: \n *Prints out the contents of ifconfig from the Linux terminal*\n \n"
                    "traceroute: \n *Will traceroute and give the bubble IP, no longer functional needs to be troubleshot*\n \n"
                    "upload: \n *Uploads todays data as csv* \n \n"
                    "upload YYYY_MM_DD: \n *Uploads that days data as csv* \n \n"
                    " who: \n *tells you about me and my creator* \n \n"
                    "stop_data: \n*This stops the high frequency data recording*\n \n"
                    "fast_data: \n*This will start fast data collection, this will only default run for 30 minutes due to storage limitations*\n \n"
                    "fast_data ##: \n*This will run the fast data for ## minutes before automatically stopping it*\n \n"
                    "fast_download YYYY_MM_DD: \n*This will download the high frequency CSV's frmo the correct date and upload them to discord* \n __________"

                )

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")



        #THIS IS TO UPLOAD DATA
        if 'upload' in message.content.lower():
            try:
                print('its true')
                python_script_path = 'discord_meteogram.py'

                #argnum dictates how many arguements have as an input and sort the dates in order
                date_cell = contains_date(message.content.lower())
                print(f"the date cell is outside function {date_cell}")

                #sort the data by date
                print(f"the unsorted date_cell: \n {date_cell}")
                date_cell = sorted(date_cell, key=lambda x: (x['year'], x['month'], x['day']))
                print(f"the sorted date_cell: \n {date_cell}")

                #checks for the propper amounts of dates
                if  0<= len(date_cell) <= 1:

                    #THINK I CAN DELETE THE NEXT 3 lines
                    #for i in date_cell:
                        #python_script_path += f" {i['year']}_{str(i['month']).zfill(2)}_{str(i['day']).zfill(2)}"
                        #print(python_script_path)

                    if len(date_cell) == 0:
                        python_script_path = 'discord_meteogram.py'
                        print(python_script_path)
                        await message.channel.send("pulling todays data from the linux machine")
                        await message.channel.send( file=discord.File('current_weather_data_logfile.csv'))

                    #double check file exists
                    elif len(date_cell)==1:
                        print('using provided date')
                        file_path = f"{directory_location}{date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}_weather_station_data.csv"

                        if os.path.exists(file_path):
                                print("File exists.")

                                #python_script_path = f"discord_meteogram.py {date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}"
                                python_script_path = f"{date_cell[0]['year']}_{str(date_cell[0]['month']).zfill(2)}_{str(date_cell[0]['day']).zfill(2)}"

                                print(python_script_path)
                                await message.channel.send(f"Date exists. uploading {file_path}")
                                await message.channel.send( file=discord.File(file_path))
                        else:
                            print(f"File {file_path} does not exist. defaulting to current date")
                            await message.channel.send(f" {file_path} {date_end} does not exist ")


                else:
                    error_message = '''invalid amount of dates sent please enter following the example inputs below:
                        current date: upload
                        specific date: upload 2024_08_01'''

                    print(error_message)
                    await message.channel.send(error_message)

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")

        #This is to download the high frequency files
        if 'fast_download' in message.content.lower():#'ip?':
                    try:
                        #extract the date
                        user_date = contains_date(message.content.lower())
                        user_date = (f"{user_date[0]['year']}_{str(user_date[0]['month']).zfill(2)}_{str(user_date[0]['day']).zfill(2)}")
                        print(user_date)

                        #check for matching files with that date
                        matching_files = fast_files(user_date)

                        #Indicate if they dont exist if they do then go through and upload them
                        if not matching_files:
                            await message.channel.send(f"No high frequency files on {user_date} exist")

                        if matching_files:
                            #loop through each file and upload them
                            for file in matching_files:
                                file_path = f"{directory_location}{file}"
                                await message.channel.send(f"Date exists. uploading {file_path}")
                                await message.channel.send( file=discord.File(file_path))
                            await message.channel.send("Uploading Complete")

                    except Exception as e:
                        await message.channel.send(f"An error has occurred: {str(e)}")
                        await message.channel.send(f"Make you your format is fast_download YYYY_MM_DD or you will get errors")

        #Credit
        if 'who' in message.content.lower():#'ip?':
            try:
                await message.channel.send(
                    "Hello, I was created by Kaleb Nails originally as a way to report an IP address of a remote raspberry pi that could have a new address asigned to it. This was to run a \n"
                    "weather station that was mounted ~60ft up on a light pole. This weather station has a 3D sonic anonometer, RH sensor, and a temp sensor."
                    "This was orignally done with traceroute and ifconfig, but I eventually grew to have more purposes. Now I have 2 instances, one on a linux desktop which is the bot you are"
                    "talking to, but also on the pi mounted outside. The JPK outside has limited responsibilities, but I can create custom meteogram graphs at your request, as well as upload"
                    "csv's at your request. Hopefully, after I have a security update, I will avaiable to the general public to use and enjoy."
                    " \nKaleb Nails is an AE major who likes programming. My code can be found in the github link below, as well as Kaleb's linkedin. \n"
                    "**GitHub**: \n https://github.com/KalebNails/Example_Code/blob/main/Python/discord_bots/linux_discord.py \n"
                    "**LinkedIn**: \n https://www.linkedin.com/in/kaleb-nails \n"
                )
            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")



client.run('YOUR AUTH')
