
# akorghebin@gmail.com
# 44R-XiU-m4b-F7S

# Authorization Key
# Access ID/Client ID: 48c7cxsg5fe38v4hf8kq
# Access Secret/Client Secret: 8e66a4bbfc7348c98f8a12b76c9c685d
# Project Code: p1679682100215rmx4cg

import tinytuya

# Connect to Device
# d = tinytuya.OutletDevice(
#     dev_id='bf1c4d57e0d6a25b4am9r3',
#     address='192.168.1.41',
#     local_key='54b6d5a683b5cab5', 
#     version=3.3)


# # Turn Off
# d.turn_off()

import time

d = tinytuya.BulbDevice('bf1c4d57e0d6a25b4am9r3', '192.168.1.41', '54b6d5a683b5cab5')
d.set_version(3.3)  # IMPORTANT to set this regardless of version
d.set_socketPersistent(True)  # Optional: Keep socket open for multiple commands
#data = d.status()

# Get Status
# data = d.status() 
# print('set_status() result %r' % data)

# start_time = time.time()

# Turn On
# d.turn_on()
# # Show status of first controlled switch on device
# print('Dictionary %r' % data)

# # Set to RED Color - set_colour(r, g, b):
# d.set_colour(0,0,255)  

# # Cycle through the Rainbow
# rainbow = {"red": [255, 0, 0], "orange": [255, 127, 0], "yellow": [255, 200, 0],
#           "green": [0, 255, 0], "blue": [0, 0, 255], "indigo": [46, 43, 95],
#           "violet": [139, 0, 255]}

# a = 1
# while a == 1:
#     for color in rainbow:
#         [r, g, b] = rainbow[color]
#         d.set_colour(r, g, b, nowait=True)  # nowait = Go fast don't wait for response
#         time.sleep(0.5)



# # Brightness: Type A devices range = 25-255 and Type B = 10-1000
# d.set_brightness(1000)

# # Set to White - set_white(brightness, colourtemp):
# #    colourtemp: Type A devices range = 0-255 and Type B = 0-1000
# d.set_white(1000,10)

# end_time = time.time()
# execution_time = end_time - start_time
# print(f'Время выполнения программы: {execution_time} секунд')


# # Set Bulb to Scene Mode
# d.set_mode('scene')

# Scene Example: Set Color Rotation Scene
#d.set_value(25, '07464602000003e803e800000000464602007803e803e80000000046460200f003e803e800000000464602003d03e803e80000000046460200ae03e803e800000000464602011303e803e800000000')

# time.sleep(10)
# # Turn Off
# d.turn_off()

# start_time = time.time()
# scan  = tinytuya.deviceScan()
# print(f'Время выполнения программы: {time.time() - start_time} секунд')


# print(scan)

d.set_brightness_percentage(100)
time.sleep(1.5)
d.set_brightness_percentage(0)
time.sleep(1.5)
d.set_brightness_percentage(50)