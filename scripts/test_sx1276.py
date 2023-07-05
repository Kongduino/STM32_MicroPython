from machine import Pin, SPI, SoftSPI
from sx127x import SX127x

cs = Pin("D10", Pin.OUT)
sck = Pin("D13", Pin.OUT)
mosi = Pin("D11", Pin.OUT)
miso = Pin("D12", Pin.IN)
#spi = SoftSPI(1)
spi2 = SoftSPI(sck=sck, mosi=mosi, miso=miso)

lora = SX127x(spi=spi2, pin_ss=cs)
message = ''
pingCounter = 0

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
    print("Sent")

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
