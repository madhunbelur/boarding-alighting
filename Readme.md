What's there in ?
- M station buckets for each of M stations 
- Services have N buckets : one for each stop in the route 
- heapq is used to store and sort the events, the __lt__() in the event class aids in time sorting 
- three events - od_matrix (random generated at timed intervals), arrival , vanish
- time is just a integer right now 
- upon a service arrival at a station : bucket for that station from service is offloaded into that station and then vanish event is created. Bucket from that station(od matrix row) is also offloaded in to that serivce (only after checking that service.crossed is 0)
