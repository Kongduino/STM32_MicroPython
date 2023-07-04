import lzw, random, json, binascii
from machine import Pin, ADC
from kongduino import *

rnd = ADC(0)
x = rnd.read_u16()
x = rnd.read_u16()
x = rnd.read_u16()
x = rnd.read_u16()
random.seed(x)

def getRandomByte():
    x = 0
    for j in range (0, 8):
        b = random.randint(0, 255) & 0b00000001
        while (b == random.randint(0, 255) & 0b00000001):
            # von Neumann extractor.
            z = random.randint(0, 255)
        x = (x << 1) | b
    return x

def getRandomWord():
    return getRandomByte() << 8 | getRandomByte()

temp = (getRandomByte() % 130) / 10.0 + 12
hum = (getRandomByte() /10.0) + 30
press = getRandomWord() % 120 + 900
a=bytearray(4)
for i in range(0, 4):
    a[i] = getRandomByte()
UUID = binascii.hexlify(a).decode() 
packet = {}
packet['temp'] = temp
packet['hum'] = hum
packet['press'] = press
packet['msgID'] = UUID

msg = json.dumps(packet).replace(' ','')
print(msg)
pkt = lzw.compress(msg)
print(pkt)
s1 = len(pkt)
s0 = len(msg)
ratio = (1 - (s1 / s0))*100
print("Compression: {} vs {} bytes, ie {:.2f}%".format(s1, s0, ratio))

pIV = bytearray(16)
for i in range(0, 16):
    pIV[i] = getRandomByte()
pKey = bytearray(32)
for i in range(0, 32):
    pKey[i] = getRandomByte()
print("> Key")
hexdump(pKey)
print("> IV")
hexdump(pIV)
print("> Plaintext")
hexdump(pkt)
result = encryptAES_CBC(msg, pKey, pIV)
print("> Ciphertext")
hexdump(msg)
result = decryptAES_CBC(msg, pKey, pIV)
print("> Deciphered")
print(msg)
