import serial
import serial.tools.list_ports
import datetime
import time
#from mintsXU4 import mintsSensorReader as mSR
#from mintsXU4 import mintsDefinitions as mD
import sys
import numpy as np
from random import randrange, uniform
from collections import OrderedDict
import json
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
    if sensorIn == "SOILMOISTURE":
         strOut  = \
            np.float32(dataIn[1]).tobytes().hex().zfill(8)

    return strOut
  
    if sensorIn == "NPK":
         strOut  = \
            np.float32(dataIn[1]).tobytes().hex().zfill(8)+ \
            np.float32(dataIn[3]).tobytes().hex().zfill(8) + \
            np.float32(dataIn[5]).tobytes().hex().zfill(8)

    return strOut
  
    if sensorIn == "PH":
         strOut  = \
            np.float32(dataIn[1]).tobytes().hex().zfill(8)

    return strOut

def joinNetwork(numberOfTries, ser, timeOutIn):
    for currentTry in range(numberOfTries):
        print("Joining Network Trial: " + str(currentTry))
        lines = sendCommand(ser,'AT+JOIN', timeOutIn)
        
        #code below returns errors - no list is being returned by e5
        #for line in lines:
            #if line == '+JOIN: Network joined':
                #return True
              
    return True
      
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
    joined = joinNetwork(1, serE5Mini, 10)

    if not joined:
        time.sleep(60)
        joined = joinNetwork(1 ,serE5Mini, 10)

    if not joined:
        print("No Network Found")
    else:
        print("Network Found")
        
    message    = hex(struct.unpack('<I', struct.pack('<I', 254))[0])
    message = message.replace('0x','').zfill(2)
    sendCommand(serE5Mini,'AT+MSGHEX='+str(message),5)
    
    
    while True:
      
        current_time = datetime.datetime.now()
        randSoilMoisture = uniform(100, 130) #resistance of soil measured in kOhms
        randN = uniform(130, 140) #nitrogen measured in mg/kg
        randP = uniform(100, 110) #phosphorus measured in mg/kg
        randK = uniform(150, 160) #potassium measured in mg/kg
        randpH = uniform(6, 7.5)
        soilMoistureList = ["soilMoisture", randSoilMoisture]
        NPKList = ["Nitrogen", str(randN), "Phosphorus", str(randP), "Potassium", str(randK)]
        pHList = ["pH", str(randpH)]
        
        
      
        #sensorData = readSerialLine(serCanaree, 2, 44)
        #print(sensorData)
            
            
        #sensorData = readSerialLineStr(serGPS, 3, "GGA")
        #print(sensorData)
        
        #sensorData = readSerialLine(serCanaree,2,44)
        strOut = getMessageStringHex(soilMoistureList, "SOILMOISTURE")
        sendCommand(serE5Mini,'AT+PORT=17',2)
        sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)
        
        strOut = getMessageStringHex(NPKList, "NPK")
        sendCommand(serE5Mini,'AT+PORT=25',2)
        sendCommand(serE5Mini,'AT+MSGHEX='+str(strOut),5)
 
        #third AT port?
        #reception of data?


if __name__ == "__main__":
    print("=============")
    print("    MINTS    ")
    print("=============")

    print("Monitoring E5, Canaree, GPS")
    main()
