from datetime import datetime, timedelta
from os import name
import time
import random
import pandas as pd
#import pyqtgraph as pg
from collections import deque
#from pyqtgraph.Qt import QtGui, QtCore
# from mintsXU4 import mintsProcessing as mP
import yaml

# from dateutil import tz
import numpy as np
#from pyqtgraph import AxisItem
from time import mktime
import statistics
from collections import OrderedDict
# import pytz
import sys

nodeIDsPre = yaml.load(open('credentials/nodeIDs.yaml'),Loader=yaml.FullLoader)
nodeIDs = nodeIDsPre['nodeIDs']

# class TimeAxisItem(pg.AxisItem):
#     def tickStrings(self, values, scale, spacing):
#         return [datetime.fromtimestamp(value) for value in values]

class node:
    def __init__(self,nodeID):
        self.nodeID = nodeID
        print("============MINTS============")
        print("NODEID: " +nodeID)
        
