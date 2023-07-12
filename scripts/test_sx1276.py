from machine import Pin, SoftSPI, UART
import time
from sx127x import SX127x
from nmea import *

gps = UART(1, 9600)
gps.init(9600, bits=8, parity=None, stop=1)
cs = Pin("D10", Pin.OUT)
sck = Pin("D13", Pin.OUT)
mosi = Pin("D11", Pin.OUT)
miso = Pin("D12", Pin.IN)
spiBus = SoftSPI(baudrate=1666666, sck=sck, mosi=mosi, miso=miso)
nmea = NMEAParser(gps)

lora = SX127x(spi = spiBus, pin_ss=cs)
message = ''
pingCounter = 0
DELAY = const(5000)
lastCheck = time.ticks_ms() - DELAY + 1000
nmea.sendCFGNMEA()

def Version():
    global message
    return lora.readRegister(0x42)

def PING():
    global pingCounter
    payload = 'PING #{0}'.format(pingCounter)
    print("Sending packet: {}".format(payload))
    message = "Sent "+payload
    lora.print(bytearray(payload.encode()))
    pingCounter += 1
    print("Sent\n")

v = Version()
message = "Version: "+hex(v)
if v == 0x12:
    message += " [o]"
else:
    message += " [x]"
print(message)
lora.init({'frequency' : 145000000, 'tx_power_level': 20, 'signal_bandwidth': 7,
           'spreading_factor': 12, 'coding_rate': 8, 'preamble_length': 8,
           'implicitHeader'  : False, 'sync_word': 0x12, 'enable_CRC': False})

PING()
target = time.ticks_ms() + 15000

while True:
    if time.ticks_ms() >= target:
        PING()
        target = time.ticks_ms() + 15000
    buf = gps.read()
    if buf != None:
        nmea.feed(buf)
    if time.ticks_ms() - lastCheck > DELAY:
        print("-----------------------------------------")
        if nmea.hasTXT:
            nmea.showTexts()
        lastCheck = time.ticks_ms()
        if nmea.hasSIV == True:
            print("SIV: {}".format(nmea.SIV))
        if nmea.fixMode != "":
            print("Fix type: {}".format(nmea.fixType))
            print("Fix mode: {}".format(nmea.fixMode))
        print(nmea.UTCTime)
        if nmea.hasFix == True:
            print("Location: {}, {}".format(nmea.latitude, nmea.longitude))
        if nmea.hasFixQuality:
            nmea.displayFixQuality()
        if nmea.knots != False:
            print("Speed: {} knots".format(nmea.knots))
        if nmea.kpm != False:
            print("Speed: {} km/h".format(nmea.kpm))
        lastCheck = time.ticks_ms()
