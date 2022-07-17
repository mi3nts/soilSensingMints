from collections import OrderedDict
from random import randrange, uniform
import time
import datetime
import json



while True:
    current_time = datetime.datetime.now()
    randSoilMoisture = uniform(100, 130) #resistance of soil measured in kOhms
    randN = uniform(130, 140) #nitrogen measured in mg/kg
    randP = uniform(100, 110) #phosphorus measured in mg/kg
    randK = uniform(150, 160) #potassium measured in mg/kg
    randpH = uniform(6, 7.5)

    soilSensorDictionary = OrderedDict([("dateTime", str(current_time)),
                                    ("Moisture", randSoilMoisture),
                                    ("Nitrogen", randN),
                                    ("Phosphorus", randP),
                                    ("Potassium", randK),
                                    ("pH", randpH)])

    print(soilSensorDictionary)

    time.sleep(1)
