import time
import board
import busio
import digitalio
import adafruit_rfm9x
import statistics
import math

# Define radio parameters.
RADIO_FREQ_MHZ = 900.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip.
# set GPIO pins as necessary - this example is for Raspberry Pi
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23
# enable CRC checking
rfm9x.enable_crc = True
# set delay before transmitting ACK (seconds)
rfm9x.ack_delay = 0.05
# set node addresses
rfm9x.node = 4
rfm9x.destination = 1
# initialize counter
counter = 0
ack_failed_counter = 0

def handlePacket(rawPacket):
    packetIndex = rawPacket.split(",")
    mode = ""
    print(packetIndex)
    nodeAData = []
    nodeBData = []
    nodeCData = []

    for index in packetIndex:
        if("NodeA" in index):
            mode = "A"
        elif ("NodeB" in index):
            mode = "B"
        elif("NodeC" in index):
            mode = "C"
        elif("EOF" in index):
            break
        if(index.lstrip("-").isdigit()):
            if(mode is "A"):
                nodeAData.append(int(index))
            elif(mode is "B"):
                nodeBData.append(int(index))
            elif(mode is "C"):
                nodeCData.append(int(index))
          
    print("Node C Data" + str(nodeCData))
    return nodeAData, nodeBData, nodeCData

def calcDistance(nodeA, nodeB, nodeC):
    # print(nodeA)
    avgNodeA = 1.1
    avgNodeB = 1.1 
    avgNodeC = 1.1

    if(bool(nodeA)):
        avgNodeA = statistics.mean(nodeA)
    if(bool(nodeB)):
        avgNodeB = statistics.mean(nodeB)
    if(bool(nodeC)):
        avgNodeC = statistics.mean(nodeC)


    x = 0.0
    AC = -38
    n = 2
    aDist = 0.0
    bDist = 0.0
    cDist = 0.0

    if(avgNodeC is not 1.1):
        cDist = math.pow(10, ((AC - avgNodeC) / (10 * n)))
    print("DISTANCE:" + str(cDist))





# Wait to receive packets.
print("Waiting for packets...")

while True:
    packet = rfm9x.receive(with_ack=True, with_header=True)

    if packet is not None:
       
        
        packetData = ""
        packetData = packet.decode('UTF-8', 'backslashreplace')
        nodeA = []
        nodeB = []
        nodeC = []


        if("Ping" not in packetData):
            nodeA, nodeB, nodeC = handlePacket(packetData)
            calcDistance(nodeA, nodeB, nodeC)
        
        print(packetData)
        if not rfm9x.send_with_ack(bytes("I don't know why but this is necessary", "UTF-8")):
            print("No Ack")
     

    # else:
    #     print("none packet")
