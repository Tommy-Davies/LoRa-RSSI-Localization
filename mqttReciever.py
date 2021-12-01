import numpy as np
import tkinter

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TKAgg')

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import random

import paho.mqtt.client as mqtt
sg.theme('Topanga')

# import graph
# import main
XScale = 100
YScale = 120
XOffset = 60
YOffset = 20

XData = []
YData = []
XAlerts = []
YAlerts = []

anchorX = [0, 4.3, 3]
anchorY = [0, 0, 2]


fallStatus = False
tempStatus = 0
soundStatus = False

fig = plt.figure()
# assert 'QTAgg' in fig.canvas.__class__.__name__

ax1 = fig.add_subplot(1,1,1)

def draw_figure(canvas, fig):
    figure_canvas_agg = FigureCanvasTkAgg(fig, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def windowSetup():
    # Define the window layout
    layout = [
        [sg.Text("Current Location")],
        [sg.Canvas(key="-CANVAS-"),sg.Output(size=(30,10), key='-OUTPUT-')],
        [sg.OK(), sg.Cancel()]

    ]

    # Create the form and show it without the plot
    window = sg.Window(
        "Matplotlib Single Graph",
        layout,
        location=(0, 0),
        finalize=True,
        element_justification="center",
        font="Helvetica 18",
    )
    return window

#overlay a picture over the plot
im = plt.imread("floorplanfinal.png")
#implot = plt.imshow(im)

def animate(i):

    #clearing previous line
    ax1.clear()
    #drawing line again wiht new data
    ax1.scatter(XData,YData)
    ax1.scatter(anchorX,anchorY, color="g")
    ax1.scatter(XAlerts, YAlerts, color="r")

    #making the overlay visible
    implot = plt.imshow(im)
    
def str2bool(str):
    return str.lower() in ("true", "t", "1", "yes")
def handlePacket(rawPacket):
    packetIndex = rawPacket.split(",")
    global XData
    global YData
    global fallStatus
    global tempStatus
    global soundStatus

    for i in range(len(packetIndex)):
        if(i + 1 <= len(packetIndex)):
            if("X:" in packetIndex[i]):
                x = (float(packetIndex[i+1]) * XScale) + XOffset
                XData.append(x)

            elif("Y:" in packetIndex[i]):
                y = height - ((float(packetIndex[i + 1]) * YScale) + YOffset)
                YData.append(y)
            
            elif("Fall" in packetIndex[i]):
                fallStatus = str2bool(packetIndex[i+1])
            elif("Temp" in packetIndex[i]):
                tempStatus = packetIndex[i+1]
            elif("High Noise" in packetIndex[i]):
                soundStatus = str2bool(packetIndex[i+1])
    
    if fallStatus or tempStatus != 0 or soundStatus:
        XAlerts.append(x)
        YAlerts.append(y)

    if fallStatus:
        print("Fall at " + str(x) + ", " + str(y) + "!")
    if tempStatus == 1:
        print("Low temperature at " + str(x) + ", " + str(y) + "!")
    elif tempStatus == 2:
        print("High temperature at " + str(x) + ", " + str(y) + "!")
    if soundStatus:
        print("Dangerous noise levels at " + str(x) + ", " + str(y) + "!")
    
    # print(XData)
def on_connect(client, userdata, flags, rc):
    # print(f"Connected with result code {rc}")
    # subscribe, which need to put into on_connect
    # if reconnect after losing the connection with the broker, it will continue to subscribe to the raspberry/topic topic
    client.subscribe("rssi")

# the callback function, it will be triggered when receiving messages
def on_message(client, userdata, msg):
    # print(f"{msg.topic} {msg.payload}")
    packetData = msg.payload.decode('UTF-8', 'backslashreplace') #might not be needed
    handlePacket(packetData)
    # 

# 

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.loop_start()


# set the will message, when the Raspberry Pi is powered off, or the network is interrupted abnormally, it will send the will message to other clients
client.will_set('rssi', b'{"status": "Off"}')

# create connection, the three parameters are broker address, broker port number, and keep-alive time respectively
client.connect("broker.emqx.io", 1883, 60)

window = windowSetup()
bbox = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
width, height = bbox.width*fig.dpi, bbox.height*fig.dpi

anchorX = [ (x*XScale)+XOffset for x in anchorX]
anchorY = [height - ((x*YScale)+YOffset) for x in anchorY]

ani = animation.FuncAnimation(fig, animate, interval=1000)
draw_figure(window["-CANVAS-"].TKCanvas, fig)



# set the network loop blocking, it will not actively end the program before calling disconnect() or the program crash
# client.loop_forever()

event, values = window.read()
window.close()