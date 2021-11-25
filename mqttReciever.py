# subscriber.py
# from locServer import handlePacket
import paho.mqtt.client as mqtt
# import graph
import main

XData = []
YData = []
sensorData = []

def handlePacket(rawPacket):
    packetIndex = rawPacket.split(",")
    global XData
    global YData
    global sensorData

    for i in range(len(packetIndex)):
        if(i + 1 <= len(packetIndex)):
            if("X:" in packetIndex[i]):
                XData.append(packetIndex[i+1])

            elif("Y:" in packetIndex[i]):
                YData.append(packetIndex[i+1])
            
            elif("S:" in packetIndex[i]):
                sensorData.append(packetIndex[i+1])
            

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

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# set the will message, when the Raspberry Pi is powered off, or the network is interrupted abnormally, it will send the will message to other clients
client.will_set('rssi', b'{"status": "Off"}')

# create connection, the three parameters are broker address, broker port number, and keep-alive time respectively
client.connect("broker.emqx.io", 1883, 60)

# set the network loop blocking, it will not actively end the program before calling disconnect() or the program crash
client.loop_forever()