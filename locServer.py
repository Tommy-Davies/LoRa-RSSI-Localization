import time
import board
import busio
import digitalio
import adafruit_rfm9x
import statistics
import math

RADIO_FREQ_MHZ = 900.0 #set radio frequency
#digital io pins
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)
#initialize spi bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
#initialize radio driver
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

#radio parameters
rfm9x.tx_power = 23
rfm9x.enable_crc = True
rfm9x.ack_delay = 0.05

rfm9x.node = 4 #self address
rfm9x.destination = 1 #localized node address


def handlePacket(rawPacket:'string')->'list, list, list':
#   Takes a recieved packet string and splits the information along delimeters.
#   Returns 3 lists for each set of node data.
    packetIndex = rawPacket.split(",")
    mode = ""
    # print(packetIndex)
    nodeAData = []
    nodeBData = []
    nodeCData = []

    for index in packetIndex:
        #Changes read mode when a new dataset is detected
        if("NodeA" in index):
            mode = "A"
        elif ("NodeB" in index):
            mode = "B"
        elif("NodeC" in index):
            mode = "C"
        elif("EOF" in index): #stops reading at EOF to prevent reading from invalid data
            break

        #add data points to the correct lists
        if(index.lstrip("-").isdigit()): #minus sign is problematic with isdigit
            if(mode is "A"):
                nodeAData.append(int(index))
            elif(mode is "B"):
                nodeBData.append(int(index))
            elif(mode is "C"):
                nodeCData.append(int(index))
          
    #return lists
    return nodeAData, nodeBData, nodeCData

def calcDistance(nodeA: 'list', nodeB: 'list', nodeC: 'list'):
    #set averages to arbitrary unreachable values for error checking
    avgNodeA = 1.1
    avgNodeB = 1.1 
    avgNodeC = 1.1

    if(bool(nodeA)):
        avgNodeA = statistics.mean(nodeA)
    if(bool(nodeB)):
        avgNodeB = statistics.mean(nodeB)
    if(bool(nodeC)):
        avgNodeC = statistics.mean(nodeC)

    #rssi parameters
    x = 0.0
    AC = -38
    n = 2
    aDist = 0.0 #force floats
    bDist = 0.0
    cDist = 0.0

    if(avgNodeC is not 1.1): #check if average was populated
        cDist = math.pow(10, ((AC - avgNodeC) / (10 * n))) #calculate distance with rssi
    print("DISTANCE:" + str(cDist))





print("Waiting for messages...")
while True:
    packet = rfm9x.receive(with_ack=True, with_header=True) #attempt to recieve message

    if packet is not None:    
        packetData = ""
        packetData = packet.decode('UTF-8', 'backslashreplace') #utf-8 decoding can cause problems with lossy comms like LoRa
        
        #reset packet lists
        nodeA = [] 
        nodeB = []
        nodeC = []

        if("Ping" not in packetData): #if packet is not a simple ping it should be a data packet
            #process and parse packet string along delimeters, return into lists
            nodeA, nodeB, nodeC = handlePacket(packetData) 
            #calculate distances from rssi data, requires the most fine tuning for accuracy
            calcDistance(nodeA, nodeB, nodeC)
        
        # print(packetData)
        if not rfm9x.send_with_ack(bytes("I don't know why but this is necessary", "UTF-8")):
            print("No Ack")

