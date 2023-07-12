import gc
from kongduino import hexdump
from time import sleep as delay

def Fletcher(blob):
    CK_A = 0
    CK_B = 0
    size = len(blob) - 2
    # last 2 bytes is the checksum
    for i in range(2, size):
        CK_A += blob[i]
        CK_B += CK_A
    blob[size] = CK_A
    blob[size + 1] = CK_B
    return blob

def toRad(x):
  return x * 3.141592653 / 180

def haversine(lat1, lon1, lat2, lon2):
  R = 6371
  x1 = lat2-lat1
  dLat = toRad(x1)
  x2 = lon2-lon1
  dLon = toRad(x2)
  a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(toRad(lat1)) * math.cos(toRad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = R * c
  return round((d + 2.220446049250313e-16) * 100) / 100

class NMEAParser():
    def __init__(self, uart):
        self._uart = uart
        self.UTCTime = "??:??:??"
        self.TXT = []
        self.hasTXT = False
        self.hasFix = False
        self.hasSIV = False
        self.SIV = -1
        self.fixMode = ''
        self.fixType = ''
        self.latitude = None
        self.longitude = None
        self.fixQuality = -1
        self.hasFixQuality = False
        self.textFixQuality = []
        self.textFixQuality.append("GPS fix")
        self.textFixQuality.append("Diff. GPS Fix")
        self.TTMG = False
        self.MTMG = False
        self.knots = False
        self.kpm = False
        buf = uart.read() # flush
        self.remainder = b''
        self.CFGNMEA = bytearray([0x06, 0x17])

    def SendCmd0B(self, myClassID, cmd):
        mb = bytearray([0xB5, 0x62, myClassID[0], myClassID[1], 0, 0, 0, 0])
        # Sync Char 1
        # Sync Char 2
        # Payload Length, Little Endian, 16-bit
        mb = Fletcher(mb)
        print("Sending: `{}`".format(cmd))
        hexdump(mb)
        self._uart.write(mb)
        delay(0.1)

    def sendCFGNMEA(self):
        self.SendCmd0B(self.CFGNMEA, "CFG-NMEA")

    def parseDegrees(self, term):
        try:
            value = float(term) / 100.0
            left = int(value)
            value = (value - left) * 1.66666666666666
            value += left
            return value
        except:
            return False

    def setGPS(self, result, start):
        self.hasFix = True
        signLat = 1
        signLong = 1
        if result[start+1] == b'W':
            signLat = -1
        if result[start+3] == b'S':
            signLong = -1
        deg = self.parseDegrees(result[start])
        if deg == False:
            return
        newLatitude = signLat * deg
        deg = self.parseDegrees(result[start+2])
        if deg == False:
            return
        newLongitude = signLong * deg
        if self.longitude != newLongitude or self.latitude != newLatitude:
            self.latitude = newLatitude
            self.longitude = newLongitude

    def feed(self, buffer):
        self.hasTXT = (len(self.TXT) > 0)
        buf = (self.remainder+buffer).split(b'\r\n')
        self.remainder = buf.pop()
        for line in buf:
            if line.startswith(b'\xb5\x62'):
                #is this a UBX message?
                payloadLen = line[4] * 256 + line[5]
                totalLen = payloadLen + 6
                print("payloadLen: {}, totalLen: {}".format(payloadLen, totalLen))
                payload = line[2:totalLen+2]
                line = line[totalLen+2:]
                hexdump(payload)
            if line.startswith(b'$'):
                if line.find(b'*') > -1:
                    temp = line.split(b'*')
                    line = temp[0]
                    crc = temp[1]
                    temp = None
                    chunks=line.split(b',')
                    verb = chunks[0][3:]
                    if verb == b'TXT':
                        self.parseGPTXT(chunks)
                    elif verb == b'RMC':
                        self.parseGPRMC(chunks)
                    elif verb == b'GSV':
                        self.parseGPGSV(chunks)
                    elif verb == b'GGA':
                        self.parseGPGGA(chunks)
                    elif verb == b'GSA':
                        self.parseGPGSA(chunks)
                    elif verb == b'GLL':
                        self.parseGPGLL(chunks)
                    elif verb == b'VTG':
                        self.parseGPVTG(chunks)
                    elif verb!=b'':
                        print(line)
    gc.collect()

    def setTime(self, result):
        hh = result[0:2].decode()
        mm = result[2:4].decode()
        ss = result[4:6].decode()
        self.UTCTime = "{}:{}:{} UTC".format(hh, mm, ss)

    def parseGPVTG(self, result):
        if(len(result)<8):
            self.TTMG = False
            self.MTMG = False
            self.knots = False
            self.kpm = False
            return
        if result[1] != b'':
            try:
                self.TTMG = float(result[1])
            except:
                self.TTMG = False
        else:
            self.TTMG = False
        if result[3] != b'':
            try:
                self.MTMG = float(result[3])
            except:
                self.MTMG = False
        else:
            self.MTMG = False
        if result[5] != b'':
            try:
                self.knots = float(result[5])
            except:
                self.knots = False
        else:
            self.knots = False
        if result[7] != b'':
            try:
                self.kpm = float(result[7])
            except:
                self.kpm = False
        else:
            self.kpm = False

    def parseGPRMC(self, result):
        if result[1] != b'':
            #print("RMC set time to {}".format(result[1]))
            self.setTime(result[1])
        if result[2] != b'A' or result[3] == b'':
            self.hasFix = False
            return
        self.setGPS(result, 3)

    def parseGPGLL(self, result):
        if result[1] != b'':
            self.setGPS(result, 1)
            if len(result) > 5:
                if result[5] != b'':
                    #print("GLL set time to {}".format(result[5][0:6]))
                    self.setTime(result[5][0:6])

    def displayFixQuality(self):
        if self.hasFixQuality == False:
            return
        self.hasFixQuality = False
        #print("Fix quality: {}".format(self.textFixQuality[self.fixQuality]))


    def parseGPGGA(self, result):
        if result[1] != b'':
            #print("GGA set time to {}".format(result[1]))
            self.setTime(result[1])
        try:
            quality = int(result[6])
        except:
            quality = 0
        if quality == 0:
            self.hasFix == False
            return
        self.hasFix = True
        self.fixQuality = quality
        self.hasFixQuality = True
        self.setGPS(result, 2)

    def parseGPGSA(self, result):
        if result[1] != b'':
            if result[1] == b'A':
                self.fixType = "Automatic"
            elif result[1] == b'M':
                self.fixType = "Manual"
            if result[2] == b'1':
                self.fixMode = "Fix not available."
                self.hasFix = False
            else:
                self.fixMode = result[2].decode() + "D fix."
                self.hasFix = True

    def parseGPGSV(self, result):
        if len(result) < 3:
            self.hasSIV = False
            return
        if result[1] != b'':
            try:
                newSIV = int(result[3])
                if self.SIV != newSIV:
                    self.SIV = newSIV
                    self.hasSIV = True
                else:
                    self.hasSIV = False
            except:
                pass

    def parseGPTXT(self, result):
        if result[1] != b'':
            self.TXT.append(result[4])
            self.hasTXT = True
    
    def showTexts(self):
        if self.hasTXT == False:
            return
        ln = len(self.TXT)
        for i in range(0, ln):
            print("Message {} of {}: {}".format(i+1, ln, self.TXT[i]))
        self.TXT = []
        self.hasTXT = False
