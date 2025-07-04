import csv
import heapq 
import random

STATION_NAMES = ['Kanjurmarg', 'Vikhroli', 'Ghatkopar', 'Kurla', 'Andheri', 'Santacruz', 'Vileparle']
NUM_STATION = len(STATION_NAMES)
OD_EVENT = 'OD'
ARRIVAL_EVENT = 'ARRIVAL'
VANISH_EVENT = 'VANISH'

station_index = {name: idx for idx, name in enumerate(STATION_NAMES)} #need this because station index and stop indices are not one to one

class Station : 
    def __init__(self, name):
        self.name = name
        self.buckets = [0 for _ in range (NUM_STATION)]
        
    def __repr__(self):
        return f"Station({self.name}, Buckets={self.buckets})"

class Service:
    def __init__(self, service_id, route, schedule):
        self.service_id = service_id
        self.route = route
        self.schedule = schedule
        self.buckets = [0 for _ in route]
        self.current_stop = 0 #pointer that points where serivce is ... easier for index like access
        self.crossed = [0 for _ in route]

    def current_station(self):
        if self.current_stop < len(self.route):
            return self.route[self.current_stop]
        return None

    def current_time(self):
        if self.current_stop < len(self.route):
            return self.schedule[self.current_stop]
        return None
    
    def mark_crossed(self):
        if self.current_stop < len(self.route):
            self.crossed[self.current_stop] = -1

    def move_next(self):
        self.current_stop +=1

class Event :
    def __init__(self, timestamp, event_type, data):
        self.timestamp = timestamp
        self.event_type = event_type
        self.data = data

    def __lt__(self, other): #need this for heap comparision
        return self.timestamp < other.timestamp

stations = {name: Station(name) for name in STATION_NAMES} #station object dictionary

services = { 
    "S1": Service("S1", ['Kanjurmarg', 'Santacruz','Vileparle','Ghatkopar'], [1,3,5,7]),
    "S2": Service("S2", ['Vikhroli', 'Ghatkopar', 'Andheri', 'Kurla'], [2,4,6,8]),
    "S3": Service("S3", ['Andheri', 'Kanjurmarg','Vileparle', 'Santacruz'], [1,4,7,10])
}

event_queue = []
event_log = []

def generate_od_matrix():
    matrix = [[0]*NUM_STATION for _ in range(NUM_STATION)]
    for i in range(NUM_STATION):
        for j in range(NUM_STATION):
            if i !=j :
                matrix[i][j] = random.randint(10,50)
    return matrix

#using heap becuase ... in this implementation events are added dynamically 
#only OD matrix
for t in range (0, 20, 5):
    heapq.heappush(event_queue, Event(t, OD_EVENT, generate_od_matrix()))

#only first stop
for s in services.values():
    heapq.heappush(event_queue, Event(s.schedule[0],ARRIVAL_EVENT, s.service_id))

while event_queue:
    event = heapq.heappop(event_queue)
    CURRENT_TIME = event.timestamp
    etype = event.event_type
    edata = event.data

    if etype == OD_EVENT :
        od_matrix = edata # here edata is the OD_matrix
        for i in range (NUM_STATION):
            for j in range (NUM_STATION):
                if i != j:
                    stations[STATION_NAMES[i]].buckets[j] += od_matrix[i][j]
        event_log.append((CURRENT_TIME,"OD_FEED","","INCOMING PASSENGERS"))

    elif etype == ARRIVAL_EVENT :
        service = services[edata] # here edata is the service_id

        if service.current_stop >= len(service.route):
            continue #service terminated 
        
        current_station = service.current_station()
        s_idx = station_index[current_station] #station index needed as station and service indices are not one to one

        deboard = service.buckets[service.current_stop]
        stations[current_station].buckets[s_idx] += deboard
        service.buckets[service.current_stop] = 0

        #vanish event addition 
        heapq.heappush(event_queue, Event(CURRENT_TIME +3, VANISH_EVENT, (current_station, deboard)))
        service.mark_crossed()

        #taking in those passengers for stations marked as 0 for service.crossed

        downstream_indices = range(service.current_stop+1, len(service.route))
        for dest in downstream_indices:
            dest_station = service.route[dest]
            d_idx = station_index[dest_station]
            num_boarding = stations[current_station].buckets[d_idx]
            if num_boarding > 0:
                service.buckets[dest] += num_boarding
                stations[current_station].buckets[d_idx] = 0

        event_log.append((CURRENT_TIME,"ARRIVAL",service.service_id, f"at {current_station}, boarded passengers updated"))

        service.move_next()

        #adding next stop to the event queue
        if service.current_stop < len(service.route):
            next_time = service.schedule[service.current_stop]
            heapq.heappush(event_queue,Event(next_time, ARRIVAL_EVENT, service.service_id))
    
    elif etype == VANISH_EVENT :
        station_name, count = edata
        idx = station_index [station_name]
        stations[station_name].buckets[idx] = max(0, stations[station_name].buckets[idx] - count)

        event_log.append((CURRENT_TIME,"ARRIVAL",service.service_id, f"Removed {count} passengers at {station_name}"))

with open("event_log.csv", "w", newline= "") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Event", "Service", "Details"])
    for row in event_log:
        writer.writerow(row)

print("Done. Event log saved to event_log.csv. ")