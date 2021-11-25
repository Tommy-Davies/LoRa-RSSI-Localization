import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
matplotlib.use('TKAgg')
# import _tkinter

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import random

import paho.mqtt.client as mqtt
# import graph
# import main

XData = []
YData = []
fallStatus = False
tempStatus = 0

fig = plt.figure()
# assert 'QTAgg' in fig.canvas.__class__.__name__

ax1 = fig.add_subplot(1,1,1)

# def draw_figure(canvas, figure):
#     figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
#     figure_canvas_agg.draw()
#     figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
#     return figure_canvas_agg

def windowSetup():
    # Define the window layout
    layout = [
        [sg.Text("Current Location")],
        [sg.Canvas(key="-CANVAS-")],
        [sg.Button("Ok")],
        [sg.Button("Close")],
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
im = plt.imread("map1.png")
#implot = plt.imshow(im)

def animate(x, y):
    #populating thr arrays with get_data func
    # get_data(xar,yar)
    #clearing previous line
    ax1.clear()
    #drawing line again wiht new data
    ax1.scatter(x,y)
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

    for i in range(len(packetIndex)):
        if(i + 1 <= len(packetIndex)):
            if("X:" in packetIndex[i]):
                XData.append(packetIndex[i+1])

            elif("Y:" in packetIndex[i]):
                YData.append(packetIndex[i+1])
            
            elif("Fall" in packetIndex[i]):
                fallStatus = str2bool(packetIndex[i+1])
            
            elif("Temp" in packetIndex[i]):
                tempStatus = packetIndex[i+1]
            

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # subscribe, which need to put into on_connect
    # if reconnect after losing the connection with the broker, it will continue to subscribe to the raspberry/topic topic
    client.subscribe("rssi")

# the callback function, it will be triggered when receiving messages
def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload}")
    packetData = msg.payload.decode('UTF-8', 'backslashreplace') #might not be needed
    handlePacket(packetData)
    ani = animation.FuncAnimation(fig, animate(XData, YData), interval=1000)
    # draw_figure(window["-CANVAS-"].TKCanvas, fig)

window = windowSetup()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# set the will message, when the Raspberry Pi is powered off, or the network is interrupted abnormally, it will send the will message to other clients
client.will_set('rssi', b'{"status": "Off"}')

# create connection, the three parameters are broker address, broker port number, and keep-alive time respectively
client.connect("broker.emqx.io", 1883, 60)

event, values = window.read()
window.close()

# set the network loop blocking, it will not actively end the program before calling disconnect() or the program crash
client.loop_forever()