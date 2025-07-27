# program written in June 2025 by Bhavani Onkar, and modified by Madhu Belur from 15 July 2025
# the python program takes schedule (supply of trips) and demand-OD data and boards/alights passengers

# required modules
import csv
import heapq 
import random
import sys
import os

os.makedirs("log", exist_ok=True)

# input files

supServices='supply-schedule.csv' # first four rows/columns are not yet the main data (but could contain headers, etc)
demODpass='demand-od.csv' # first four rows/columns are not yet the main data (but could contain headers, etc)

stnList = []

class Service:
    def __init__(self, servNum):
        self.servNum = servNum
        self.stnTimings = []
        self.stnTimingsDict = {}
        self.buckets = {}
    
    def printData(self):
        print(self.servNum,stnList,self.stnTimings)
        
    def __repr__(self):
        return f"Station({self.servNum}, timings={self.stnTimings})"

servicesDict = {}
servicesLst = []

# Read timetable
with open(supServices, newline='') as file:
    reader = csv.reader(file)
    header = next(reader) # contains service ids
    servNums = header[4:5] # first four rows/columns are not yet the main data
    for colIndx, servId in enumerate(servNums):
        servObj = Service(servId)
        servicesDict[servId] = servObj
        servicesLst.append(servObj)

    for row_num, row in enumerate(reader):
        if row_num < 3: continue
        if row_num >= 3:
             station = row[1]
             stnList.append(station)
        timings = row[4:5]
        indx = 0
        for serv, timing in zip(servicesLst, timings):
             serv.stnTimingsDict[station] = int(timing)
             serv.stnTimings.append(int(timing))
             indx += 1
             for stn in stnList: 
                serv.buckets[stn] = 0

print(servicesDict)
print(stnList)

EventsList = []


for ke,val in servicesDict.items():
   print(val.servNum)

class Event :
    def __init__(self, timing, stn, servNum, etype, destn, bucket , vanishEvent):
        self.timing = timing
        self.stn = stn
        self.servNum = servNum
        self.etype = etype
        self.destn = destn ### vanish and OD uses it 
        self.bucket = bucket ### only OD event uses this 
        self.vanishEvent = vanishEvent ### links to vanish event only arrival event uses it 

    def __lt__(self, other): #need this for heap comparision
        return self.timing < other.timing

def updateBuckets(ev):
   if ev.etype == 'servArrival': # do some bucket transfer only for those stations with event time
       # in services MORE than event-time
       # alight from the service
       stnObjDict[ev.stn].buckets[ev.stn] += servicesDict[ev.servNum].buckets[ev.stn] # added
       ### adding de-boarding people to vanish bucket 
       VanEvent = ev.vanishEvent
       VanEvent.bucket = servicesDict[ev.servNum].buckets[ev.stn]
       servicesDict[ev.servNum].buckets[ev.stn] = 0 # emptied

       for stn in stnList: # at the stn corresponding to event, update for *EACH* station to/from service
          if servicesDict[ev.servNum].stnTimingsDict[stn] > ev.timing:
             # board: station's that
             servicesDict[ev.servNum].buckets[stn] += stnObjDict[ev.stn].buckets[stn] 
             stnObjDict[ev.stn].buckets[stn] = 0
             print('yes boarded', ev.stn, ev.timing)
          else: print('not boarded', ev.stn, ev.timing)
   elif ev.etype == 'passVanish':
       print('came into passVanish')
       ### subtracting no of people from station bucket
       stnObjDict[ev.stn].buckets[ev.stn] -= ev.bucket # at station stn, empty its own bucket (exitting passengers)
   elif ev.etype == 'passAppear':
       print('came into passAppear')
       stnObjDict[ev.stn].buckets[ev.destn] += ev.bucket

# Read passenger demand data
with open(demODpass, newline='') as file:
    reader = csv.reader(file)
    header = next(reader) # contains service ids
    for row_num, row in enumerate(reader):
      if row_num >=3:
        timing = int(row[1])
        orig = row[4]
        dest = row[5] #passenger count
        pcount = int(row[6]) # destination
        EventsList.append(Event(timing, orig, 0, 'passAppear', dest, pcount, None))


stnNums = len(stnList)

class Station:
    def __init__(self, stnName):
        self.stnName = stnName
        self.buckets = {}
        for stn in stnList:
             self.buckets[stn] = 0 # stn is key to a dictionary called buckets

stnObjDict = {}

for stnName in stnList:
   stnObjDict[stnName] = Station(stnName)

for serv in servicesLst:
    stnIndx = 0
    for timing in serv.stnTimings:
        stn = stnList[stnIndx]
        EventsList.append(Event(timing, stn, serv.servNum, 'servArrival', 0, 0, None))
        EventsList.append(Event(timing+50, stn, serv.servNum, 'passVanish', 0, 0, None))
        ### linking arrival event to its corresponding vanish event
        EventsList[-2].vanishEvent = EventsList[-1]
        stnIndx += 1

EventsList.sort(key = lambda x: x.timing)

for ev in EventsList:
   updateBuckets(ev)

#sys.exit()

#print(len(EventsList))

#for stn in stnList:
   #print(stn, stnObjDict[stn].buckets)

#sys.exit()


with open("log/event_log.csv", "w", newline= "") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Station", "Service", "Event", "Destination", "People count"])
    for event in EventsList:
        writer.writerow([event.timing, event.stn, event.servNum, event.etype, event.destn, event.bucket])


print("Done. Event log saved to log/event_log.csv. ")

