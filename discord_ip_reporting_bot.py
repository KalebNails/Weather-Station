# Kaleb Nails, nailsk@my.erau.edu
# Marc Compere, comperem@erau.edu
#
# simple command-response discord bot configured to report 'traceroute' output to Mac Daddy Weather Studs discord chat
#
# pip install discord.py
# created : 10/19/2023
# modified: 11/24/2023

import subprocess
import discord
import asyncio
import re

intents = discord.Intents.all()  # This sets up a default set of intents
#reading messages is not default
client = discord.Client(intents=intents)


#this prints on bot boot up
@client.event
async def on_ready():
    print('Bot is online and ready')
    await discord.utils.get(client.get_all_channels(), name='whats-the-ip').send("Hello, I'm John Pheasant Kennedy on the Weather Station. I have just woken up.")



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


        if message.content.lower() == 'ifconfig':#'ip?':
            try:
                ipconfig_txt = str(subprocess.getstatusoutput(f'ifconfig'))
                #I am so very dyslexic, it took me like 10 minutes to figure out i swapped / for \ and i even specifically checked if i did
                ipconfig_txt = ipconfig_txt.replace(r'\n','\n')
                await message.channel.send(ipconfig_txt)

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")



        if message.content.lower() == 'traceroute':#'ip?':
            try:
                #ipconfig_txt = str(subprocess.getstatusoutput(f'traceroute 10.33.166.1')) # works from M.131 lab location
                ipconfig_txt = str(subprocess.getstatusoutput(f'traceroute 10.33.228.1')) # works from ACE lab location, discovery by ssh login, then 'w' or 'who' to report originating login ip
                #I am so very dyslexic, it took me like 10 minutes to figure out i swapped / for \ and i even specifically checked if i did
                ipconfig_txt = ipconfig_txt.replace(r'\n','\n')
                await message.channel.send(ipconfig_txt)

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")


        #Start the fast data collection and add a safety measure to it
        if 'fast_data' in message.content.lower():#'ip?':
            try:
                #check that it provides times in minutes
                match = re.search(r'fast_data\s*(\d+)', message.content.lower())

                #set how long the bot sleeps for
                if match:
                    run_time = int(match.group(1))
                    await message.channel.send(f"Starting fast data collection for {run_time} minutes")
                    subprocess.run(['python3','/home/pi/SDL_Starter.py'])
                    await asyncio.sleep(run_time*60) #DONT FORGET TO MULTILY BY 60

                #Defaults to 30 minute runtimes
                else:
                    await message.channel.send("Starting fast data collection with default time of 30 minutes")
                    subprocess.run(['python3','/home/pi/SDL_Starter.py'])
                    await asyncio.sleep(30*60) #DONT FORGET TO MULTIPLY BY 60
                
                await message.channel.send("Maximium time reached. Stopping high frequency data collection")
                subprocess.run(['python3','/home/pi/SDL_Stopper.py'])
                await message.channel.send("Stopped Sucessfully")

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")

         #Stop the fast data collection
        if 'stop_data' in message.content.lower():
            try:
                await message.channel.send("Stopping fast data collection")
                subprocess.run(['python3','/home/pi/SDL_Stopper.py'])
                await message.channel.send("Stopped Sucessfully")

            except Exception as e:
                await message.channel.send(f"An error has occurred: {str(e)}")               


client.run('YOUR AUTH')



