from collections import OrderedDict
from random import randrange, uniform
import time
import datetime
import json
import struct



while True:
    current_time = datetime.datetime.now()
    randSoilMoisture = uniform(100, 130) #resistance of soil measured in kOhms
    randN = uniform(130, 140) #nitrogen measured in mg/kg
    randP = uniform(100, 110) #phosphorus measured in mg/kg
    randK = uniform(150, 160) #potassium measured in mg/kg
    randpH = uniform(6, 7.5)

    soilSensorDictionary = OrderedDict([("dateTime", str(current_time)),
                                    ("Moisture", struct.pack("f", randSoilMoisture)),
                                    ("Nitrogen", struct.pack("f", randN)),
                                    ("Phosphorus", struct.pack("f", randP)),
                                    ("Potassium", struct.pack("f", randK)),
                                    ("pH", struct.pack("f", randpH))])

    print(soilSensorDictionary)

    time.sleep(1)
