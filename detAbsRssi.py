import time
import board
import busio
import digitalio
import adafruit_rfm9x
import statistics
import math
import matplotlib
import random

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
rfm9x.ack_delay = 0
rfm9x.ack_retries = 1
rfm9x.ack_wait = 0.1

rfm9x.node = 4 #self address
rfm9x.destination = 3 #TODO change this

while True:
    if not rfm9x.send_with_ack(bytes("Ping", "UTF-8")):
        print("no ack")
    else:
        print("rssi: " + str(rfm9x.last_rssi))
        rfm9x.receive(with_ack=True, with_header=True)
        # rfm9x.send_with_ack(bytes("ack", "UTF-8"))