"""
Accepts only csv files
first argument: N path/to/tfl_stations.csv path/to/tfl_connections.csv

"""


import random
import time
import sys

start = time.time()

TURNS = 100000

N = int(sys.argv[1])
stations_file = sys.argv[2]
station_connections_file = sys.argv[3]


class Station:
    def __init__(self, id_number, name):
        self.id_number = id_number
        self.name = name
        self.connections = set()
        self.closed = False

    def add_connection(self, connection):
        self.connections.add(connection)

    def get_connections(self):
        return list(self.connections)

    def close_station(self, n):
        self.closed = True
        sys.stdout.write("Owner {} found cat {} - {} is now closed\n".format(n, n, self.name))


class Cat:
    def __init__(self, cat_id):
        self.cat_id = cat_id
        self.moves = 0

    def set_random_start_station(self, stations):
        # stations is a dict
        self.station = stations[random.choice(list(stations.keys()))]

    def move(self):
        # do nothing if all neighboring stations are closed
        available_stations = [s for s in self.station.get_connections() if s.closed is False]
        if not available_stations:
            return None
        self.station = random.choice(available_stations)
        self.moves += 1
        return True

    def infinite_loop(self):
        if len(self.station.get_connections()) == 1 and self.station.get_connections()[0] == self.station:
            print("cat in infinite loop")
            return True
        return False


class Human:
    def __init__(self, human_id):
        self.human_id = human_id
        self.visited_stations = []
        self.moves = 0
        self.cat_missing = True

    def set_random_start_station(self, stations):
        # stations is a dict
        self.station = stations[random.choice(list(stations.keys()))]
        while self.station == self.cat.station:
            self.station = stations[random.choice(list(stations.keys()))]
        self.visited_stations.append(self.station)

    def infinite_loop(self):
        if len(self.station.get_connections()) == 1 and self.station.get_connections()[0] == self.station:
            print("human infinite loop")
            return True
        return False

    def move(self):
        # do nothing if all neighboring stations are closed
        available_stations = [s for s in self.station.get_connections() if s.closed is False]
        if not available_stations:
            return None

        new_station = False
        # try to go to a station where the person has not been before
        for station in available_stations:
            if station not in self.visited_stations:
                self.station = station
                new_station = True
                break
        if not new_station:
            self.station = random.choice(available_stations)
        self.moves += 1
        self.visited_stations.append(self.station)
        return True

    def cat_found(self):
        if self.station == self.cat.station:
            self.cat_missing = False
            self.station.close_station(self.human_id)
        return not self.cat_missing


stations = {}

with open(stations_file, 'rt') as tube_stations:
    for row in tube_stations:
        id_number, station_name = row.replace("\n", "").split(",")
        stations[id_number] = Station(id_number, station_name)

with open(station_connections_file, 'rt') as tube_connections:
    for row in tube_connections:
        station_id, connection_id = row.replace("\n", "").split(",")
        station = stations[station_id]
        connection_station = stations[connection_id]
        station.add_connection(connection_station)
        connection_station.add_connection(station)

cats = {}
humans = {}

for e in range(N):
    cat = Cat(e)
    human = Human(e)
    cat.owner = human
    human.cat = cat
    cat.set_random_start_station(stations)
    human.set_random_start_station(stations)
    cats[cat.cat_id] = cat
    humans[human.human_id] = human


lucky_founder = []
while humans:
    for i in range(TURNS):
        for e in range(N):
            if e in humans:
                cat = cats[e]
                human = humans[e]
                if not human.cat_found():
                    cat_able_to_move = cat.move()
                    able_to_move = human.move()
                    if not able_to_move or not cat_able_to_move:
                        del humans[e]
                    if human.infinite_loop():
                        del humans[e]
                    if cat.infinite_loop():
                        del humans[e]
                else:
                    lucky_founder.append(human)
                    del humans[e]
    humans = None

print("lucky founder ", len(lucky_founder))

sys.stdout.write("Total number of cats: {}\n".format(N))
sys.stdout.write("Number of cats found: {}\n".format(len(lucky_founder)))
avg_moves = sum([f.moves for f in lucky_founder])/len(lucky_founder) if len(lucky_founder) else 0
sys.stdout.write("Average number of movements required to find a cat: {}\n".format(avg_moves))

print("Duration:", time.time()-start)
