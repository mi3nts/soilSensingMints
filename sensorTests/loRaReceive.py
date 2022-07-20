import serial
import datetime
import os
import csv
import time
import serial
import pynmea2
from collections import OrderedDict
import netifaces as ni
import math
import base64
import json
import struct
from traceback import print_tb
import paho.mqtt.client as mqtt
import yaml
import mintsLiveNodes as mLN
#from backports.datetime_fromisoformat import MonkeyPatch
#from datetime import date, time


dataFolder = "/home/teamlary/mnt/teamlary1/mintsData"
dataFolderMQTT = dataFolder +"rawMQTT"

mqttPort = 1883
mqttBroker = "mqtt.lora.trecis.cloud"
connected    = False  # Stores the connection status
broker       = mqttBroker  
port         = mqttPort  # Secure port
mqttUN       = "username"
mqttPW       = "password"
nodeObjects  = []
decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
nodeIDsPre = yaml.load(open("credentials/nodeIDs.yaml"),Loader=yaml.FullLoader)
nodeIDs = nodeIDsPre['nodeIDs']
#MonkeyPatch.patch_fromisoformat()
portIDsFile         = "credentials/portIDs.yaml"
portDefinitions     = yaml.load(open(portIDsFile),Loader=yaml.FullLoader)
portIDs             = portDefinitions['portIDs']

###############################################

#def getWritePathMQTT(nodeID,labelIn,dateTime):
    #Example  : MINTS_0061_OOPCN3_2019_01_04.csv
    #writePath = dataFolderMQTT+"/"+nodeID+"/"+str(dateTime.year).zfill(4)  + "/" + str(dateTime.month).zfill(2)+ "/"+str(dateTime.day).zfill(2)+"/"+ "MINTS_"+ nodeID+ "_" +labelIn + "_" + str(dateTime.year).zfill(4) + "_" +str(dateTime.month).zfill(2) + "_" +str(dateTime.day).zfill(2) +".csv"
    #return writePath;

def writeJSONLatestMQTT(sensorDictionary,nodeID,sensorID):
    directoryIn  = dataFolderMQTT+"/"+nodeID+"/"+sensorID+".json"
    # print(directoryIn)
    try:
        with open(directoryIn,'w') as fp:
            mSR.directoryCheck(directoryIn)
            json.dump(sensorDictionary, fp)
    except Exception as e:
        print("[ERROR] Could not publish data, error: {}".format(e))
        print("Json Data Not Written")
  
def loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary):
    #writePath = mSR.getWritePathMQTT(nodeID,sensorID,dateTime)
    #print(writePath)	
    #mSR.writeCSV2(writePath,sensorDictionary,exists)
    mL.writeJSONLatestMQTT(sensorDictionary,nodeID,sensorID)
    return;

def sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data):
    global sensorDictionary
    
    
    if(sensorID=="SOILMOISTURE"):
        sensorDictionary = SOILMOISTURELoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
    elif(sensorID=="NPK"):
        sensorDictionary = NPKLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data) 
    return sensorDictionary;
  
def SOILMOISTURELoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
    global sensorDictionary
    if(framePort == 17 and len(base16Data) == 8) :
        sensorDictionary =  OrderedDict([
                ("dateTime", str(dateTime)), 
        		("SoilMoisture", struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0])
        ])
        
    #loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)  
    print(sensorDictionary)
    return sensorDictionary

def NPKLoRaWrite(dateTime,nodeID,sensorID,framePort,base16Data):
    global sensorDictionary
    if(framePort == 25 and len(base16Data) == 24) :
        sensorDictionary =  OrderedDict([
                ("dateTime", str(dateTime)), 
        		("N", struct.unpack('<L',bytes.fromhex(base16Data[0:8]))[0]),
                ("P", struct.unpack('<L',bytes.fromhex(base16Data[8:16]))[0]),
                ("K", struct.unpack('<L',bytes.fromhex(base16Data[16:24]))[0])
        ])
        
    #loRaWriteFinisher(nodeID,sensorID,dateTime,sensorDictionary)  
    print(sensorDictionary)
    return sensorDictionary

def getPortIndex(portIDIn,portIDs):
    indexOut = 0
    for portID in portIDs:
        if (portIDIn == portID['portID']):
            return indexOut; 
        indexOut = indexOut +1
    return -1;
  
def getNodeIndex(nodeIDIn):
    indexOut = 0
    for node in nodeIDs:
        nodeID = node['nodeID']
        if (nodeID == nodeIDIn):
            return indexOut; 
        indexOut = indexOut +1
    return -1;

def loRaSummaryReceive(message,portIDs):
    nodeID = message.topic.split('/')[5]
    sensorPackage       =  decoder.decode(message.payload.decode("utf-8","ignore"))
    rxInfo              =  sensorPackage['rxInfo'][0]
    txInfo              =  sensorPackage['txInfo']
    loRaModulationInfo  =  txInfo['loRaModulationInfo']
    sensorID            = portIDs[getPortIndex(sensorPackage['fPort'],portIDs)]['sensor']
    inputDate           = sensorPackage['publishedAt'][0:26]
    dateTime            = inputDate.replace("T", " ") #edited with monkeypatch
    base16Data          = base64.b64decode(sensorPackage['data'].encode()).hex()
    gatewayID           = base64.b64decode(rxInfo['gatewayID']).hex()
    framePort           = sensorPackage['fPort']
    sensorDictionary =  OrderedDict([
            ("dateTime"        , str(dateTime)),
            ("nodeID"          , nodeID),
            ("sensorID"        , sensorID),
            ("gatewayID"       , gatewayID),
            ("rssi"            , rxInfo["rssi"]),
            ("loRaSNR"         , rxInfo["loRaSNR"]),
            ("channel"         , rxInfo["channel"] ),
            ("rfChain"         , rxInfo["rfChain"] ),
            ("frequency"       , txInfo["frequency"]),
            ("bandwidth"       , loRaModulationInfo["bandwidth"]),
            ("spreadingFactor" , loRaModulationInfo["spreadingFactor"] ),
            ("codeRate"        , loRaModulationInfo["codeRate"] ),
            ("dataRate"        , sensorPackage['dr']),
            ("frameCounters"   , sensorPackage['fCnt']),
            ("framePort"       , framePort),
            ("base64Data"      , sensorPackage['data']),
            ("base16Data"      , base16Data),
            ("devAddr"         , sensorPackage['devAddr']),
            ("deviceAddDecoded", base64.b64decode(sensorPackage['devAddr'].encode()).hex())
        ])
    # loRaWriteFinisher("LoRaNodes","Summary",dateTime,sensorDictionary)
    # loRaWriteFinisher(gatewayID,"Summary",dateTime,sensorDictionary)
    return dateTime,gatewayID,nodeID,sensorID,framePort,base16Data;
  
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    topic = "utd/lora/app/2/device/+/event/up"
    client.subscribe(topic)
    print("Subscrbing to Topic: "+ topic)
    for node in nodeIDs:
        print("Appending  Node")
        nodeID = node['nodeID']
        print(nodeID)
        nodeObjects.append(mLN.node(nodeID))
    
def on_message(client, userdata, msg):
        dateTime,gatewayID,nodeID,sensorID,framePort,base16Data = \
        loRaSummaryReceive(msg, portIDs)
        # print(msg.payload)
        if nodeID == "2cf7f12032304cc3":
            print(" - - - MINTS DATA RECEIVED - - - ")
            print("Node ID         : " + nodeID)
            nodeIndex = getNodeIndex(nodeID)
            if nodeIndex >= 0 :
                print("============")
                sensorDictionary = sensorReceiveLoRa(dateTime,nodeID,sensorID,framePort,base16Data)
                dateTime = datetime.datetime.strptime(sensorDictionary["dateTime"], '%Y-%m-%d %H:%M:%S.%f')
                print("Node ID         : " + nodeID)
                print("Gateway ID      : " + gatewayID)
                print("Sensor ID       : " + sensorID)
                print("Date Time       : " + str(dateTime))
                print("Port ID         : " + str(framePort))
                print("Base 16 Data    : " + base16Data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqttUN,mqttPW)
client.connect(broker, port, 60)
client.loop_forever()
