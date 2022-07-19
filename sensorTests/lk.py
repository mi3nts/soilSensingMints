import serial
import serial.tools.list_ports
import datetime
import time
#from mintsXU4 import mintsSensorReader as mSR
#from mintsXU4 import mintsDefinitions as mD
import sys
import numpy as np
import struct

def findPorts(strIn1,strIn2):
    ports = list(serial.tools.list_ports.comports())
    allPorts = []
    for p in ports:
        currentPortStr1 = str(p[1])
        currentPortStr2 = str(p[2])
        if(currentPortStr1.find(strIn1)>=0 and currentPortStr2.find(strIn2)>=0 ):
            allPorts.append(str(p[0]).split(" ")[0])
    return allPorts

#check if port is correct with for p in ports
canareePorts = findPorts("Canaree PM","PID=10C4:EA60")[0]
loRaE5MiniPorts = findPorts("CP2102N USB to UART Bridge Controller","PID=10C4:EA60")[0]
gpsPorts = findPorts("u-blox 7 - GPS/GNSS Receiver","PID=1546:01A7")[0]

def openSerial(portIn,baudRate):
    ser = serial.Serial(
            port = portIn,
            baudrate = baudRate,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0)

    return ser;
  
def readSerialLineStr(serIn, timeOutSensor, strExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime) < timeOutSensor:   
            for c in serIn.read():
                line.append(chr(c))

                if chr(c) == '\n':
                    if startFound == True:
                        dataString = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        dataStringData = dataStringPost.split(',')
                        
                        if dataStringPost.find(strExpected) > 0:
                            return dataStringData;
                        else:
                            line = []
                    else:    
                        startFound = True
                        line = []
                        
def readSerialLine(serIn, timeOutSensor, sizeExpected):
    line = []
    startTime = time.time()
    startFound = False
    while (time.time()-startTime)<timeOutSensor:   
        # try:
            for c in serIn.read():
                line.append(chr(c))
                # print((''.join(line)))

                if chr(c) == '\n':
                    if startFound == True:
                        dataString     = (''.join(line))
                        dataStringPost = dataString.replace('\r\n', '')
                        dataStringData =  dataStringPost.split(',')
                        if sizeExpected == len(dataStringData):
                            return dataStringData;
                        else:
                            line = []
                    else:
                        startFound = True
                        line = []
                        
def sendCommand(serIn, commandStrIn, timeOutIn):
    serIn.write(str.encode(commandStrIn+ '\n\r'))
    line = []
    lines = []
    startTime = time.time()
    while (time.time()-startTime)<timeOutIn:
        for c in serIn.read():
            line.append(chr(c))
            if chr(c) == '\n':
                dataString = (''.join(line)).replace("\n","").replace("\r","")
                lines.append(dataString)
                print(dataString)
                line = []
                break
                
def getMessageStringHex(dataIn, sensorIn):
    if sensorIn == "IPS7100CNR":
         strOut  = \
            np.uint32(dataIn[1]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[3]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[5]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[7]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[9]).tobytes().hex().zfill(8)+ \
            np.uint32(dataIn[11]).tobytes().hex().zfill(8) + \
            np.uint32(dataIn[13]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[15]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[17]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[19]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[21]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[23]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[25]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[27]).tobytes().hex().zfill(8)

    return strOut

    if sensorIn == "BME688CNR":
        strOut  = \
            np.float32(dataIn[29]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[31]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[33]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[35]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[37]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[39]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[41]).tobytes().hex().zfill(8)
    return strOut

def joinNetwork(numberOfTries, ser, timeOutIn):
    for currentTry in range(numberOfTries):
        print("Joining Network Trial: " + str(currentTry))
        lines = sendCommand(ser,'AT+JOIN=DR3', timeOutIn)
        
        #code below returns errors - no list is being returned by e5
        for line in lines:
            if line == '+JOIN: Network joined':
                return True
              
    return False
      
def main():
  
    appKey = "CDCC4B13264CEDF92BEA7953C4034E21"
  
    serE5Mini    = openSerial(loRaE5MiniPorts,9600)
    serCanaree   = openSerial(canareePorts,115200)
    serGPS       = openSerial(gpsPorts,9600)
    

    print(" ")
    print("Connected to: " + serE5Mini.portstr)
    print("Connected to: " + serCanaree.portstr)
    print("Connected to: " + serGPS.portstr)
    print(" ")
    
    sendCommand(serE5Mini,'AT+RESET',2)
    sendCommand(serE5Mini,'AT+FDEFAULT',1)
    sendCommand(serE5Mini,'AT+VER',1)
    sendCommand(serE5Mini,'AT+FDEFAULT',1)
    sendCommand(serE5Mini,'AT+ID',1)
    sendCommand(serE5Mini,'AT+KEY=APPKEY, "'+appKey+'"',1)
    sendCommand(serE5Mini,'AT+MODE=LWOTAA',1)
    sendCommand(serE5Mini,'AT+DR=US915',1)
    sendCommand(serE5Mini,'AT+DR=dr2',1)
    sendCommand(serE5Mini,'AT+CH=NUM, 56-63',1)
    sendCommand(serE5Mini,'AT+POWER=20',1)
    sendCommand(serE5Mini,'AT+PORT=2',2)
        
    joined = False 
    joined = joinNetwork(10, serE5Mini, 10)

    if not joined:
        time.sleep(60)
        joined = joinNetwork(10 ,serE5Mini, 10)

    if not joined:
        print("No Network Found")
    else:
        print("Network Found")
        
    message    = hex(struct.unpack('<I', struct.pack('<I', 254))[0])
    message = message.replace('0x','').zfill(2)
    sendCommand(serE5Mini,'AT+MSGHEX='+str(message),5)
    
    
    while True:
      
        #sensorData = readSerialLine(serCanaree, 2, 44)
        #print(sensorData)
            
            
        #sensorData = readSerialLineStr(serGPS, 3, "GGA")
        #print(sensorData)
        
        sensorData = readSerialLine(serCanaree,2,44)
        strOut = getMessageStringHex(sensorData, "IPS7100CNR")
        sendCommand(serE5Mini,'AT+PORT=17',2)
        sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)

if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")

    print("Monitoring E5, Canaree, GPS")
    main()
