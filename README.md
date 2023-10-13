# Weather-Station #
This is the supporting code to the remote weather station

## Meeting Questions 10/12/2023 ##
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/5571e9c8-c885-41e3-819d-9fc379b9b20b)


I had a couple questions about the image above. 
1. Does the realtive humidity and temp scales and measurements seem reasonable?
2. The mean sea level pressure is a solid block, and idea what its supposed to look like?
3. I removed the wind graph because if you look at the image below this is what its supposed to look like is below:
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/849fd789-8018-46e4-8ce7-f4996577e647)


Wind Max is over 3 seconds is that a correct time frame for our puposes over 24 hours? Also it says direction, I looked this up and it says its in degrees from some fixed lattitude or long, since we are recording 3d wind should I just remove the vertical component when dislpaying this?


Also I hit the none fatal error below:
![image](https://github.com/KalebNails/Weather-Station/assets/102830532/a2bdbc23-e5f7-4805-bef9-1500e2828820)

does the equation: deg_C + 243.5 *value / (17.67 - value)
immediately mean anything to you? I don't exactly know where this takes place in the code and is a little hard to find, but I was wondering if you could possibly point me in a direction in if its reltated to RH or temp or etc.
