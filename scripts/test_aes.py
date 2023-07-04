from kongduino import *
import time, random

randomBuff = bytearray(112)
for i in range(0, 112):
    randomBuff[i] = random.randint(0, 255)

print("> randomBuff")
hexdump(randomBuff)
pKey = randomBuff[0:16]
pIV = randomBuff[16:32]
plaintext = randomBuff[32:96]
print("> Key")
hexdump(pKey)
print("> IV")
hexdump(pIV)
print("> Plaintext")
hexdump(plaintext)

buffer = plaintext
goal = time.ticks_ms() + 1000
count = 0
while time.ticks_ms() < goal:
    result = encryptAES_CBC(buffer, pKey, pIV)
    count += 1
print("Encryption: {} rounds / second".format(count))

goal = time.ticks_ms() + 1000
count = 0
while time.ticks_ms() < goal:
    result = decryptAES_CBC(buffer, pKey, pIV)
    count += 1
print("Decryption: {} rounds / second".format(count))

plaintext = randomBuff[32:96]
buffer = plaintext
result = encryptAES_CBC(buffer, pKey, pIV)
print("> Ciphertext")
hexdump(buffer)
result = decryptAES_CBC(buffer, pKey, pIV)
print("> Deciphered")
hexdump(buffer)

if buffer[0:64] == plaintext[0:64]:
    print("[√] Test successful")
else:
    print("[X] Test failed")

