"""
Accepts only csv files
N path/to/tfl_stations.csv path/to/tfl_connections.csv

"""


import random
import time
import sys
import math

if sys.version_info < (3, 0):
    raise Exception("You should use Python3")

if len(sys.argv) != 4:
    raise Exception("You should introduce the following arguments: N path/to/tfl_stations.csv "
                    "path/to/tfl_connections.csv")

TURNS = 100000
N = int(sys.argv[1])
stations_file = sys.argv[2]
station_connections_file = sys.argv[3]


class UnderGround:
    """
    Underground main class
    Underground may have various networks, or Graphs, that are not connected with each other
    """
    def __init__(self):
        self.stations = {}
        self.networks = []
        self.cats = {}
        self.humans = {}
        self.N = 0
        self.cats_found = 0
        self.founders = []

    def build_stations(self, stations_file, station_connections_file):
        """
        builds the stations, and adds the connections to each station
        """
        with open(stations_file, 'rt') as tube_stations:
            for row in tube_stations:
                id_number, station_name = row.replace("\n", "").split(",")
                self.stations[id_number] = Station(id_number, station_name)

        # after creating the stations set the connections and mark to which Underground they belong to
        with open(station_connections_file, 'rt') as tube_connections:
            for row in tube_connections:
                station_id, connection_id = row.replace("\n", "").split(",")
                station = self.stations[station_id]
                connection_station = self.stations[connection_id]
                station.ug = ug
                connection_station.ug = ug
                station.add_connection(connection_station)
                connection_station.add_connection(station)

    def construct_networks(self):
        """
        We create networks that are connected to each other.
         for instance a-b-c-d-e are initially connected to each other,
         but when c closes, only a-b & d-e are now connected

        Every time a station closes, we construct the networks again:
         We go through the all the stations, and create the graphs
        """
        self.networks = []
        mapped_stations = []

        for station in self.stations.values():
            if not station.closed and station not in mapped_stations:
                g = Graph()
                mapped_stations.extend(g.create_network(station))
                self.networks.append(g)

    def create_humans_and_lost_cats(self, N):
        self.N = N
        for e in range(N):
            cat = Cat(e)
            human = Human(e)
            cat.owner = human
            human.cat = cat
            cat.set_random_start_station(self.stations)
            human.set_random_start_station(self.stations)
            self.cats[cat.cat_id] = cat
            self.humans[human.human_id] = human

    def find_the_cats(self):
        t = 0
        while t < TURNS and self.humans:
            for e in range(self.N):
                if e in self.humans:
                    c = self.cats[e]
                    h = self.humans[e]
                    cat_able_to_move = c.move()
                    human_able_to_move = h.move()
                    if h.cat_found():
                        # remove from the search list
                        del self.humans[e]
                        self.cats_found += 1
                        self.founders.append(h)
                    # if not found, check if the cat and the human are even in the same network
                    elif h.cat_in_different_network():
                        del self.humans[e]
                    elif not cat_able_to_move or not human_able_to_move:
                        del self.humans[e]
            t += 1


class Graph:
    """
    A Graph represents a network of connected stations (all of them must be open)
     a-b-c-d-e is a network; if the c closes, then we have two networks that are not connected: a-b & d-e

    """
    def __init__(self):
        self.stations = []

    def create_network(self, start_station):
        """
        take a station, and follow its connections to create a list of the stations in the network
        """
        start_station.set_graph(self)
        self.stations.append(start_station)
        stations = [start_station]
        while stations:
            for connected_station in stations.pop().get_connections():
                if connected_station not in self.stations and not connected_station.closed:
                    self.stations.append(connected_station)
                    stations.append(connected_station)
                    # the station must also know to which network it belongs to
                    connected_station.set_graph(self)
        return self.stations


class Station:
    def __init__(self, id_number, name):
        self.id_number = id_number
        self.name = name
        self.connections = set()
        self.closed = False
        self.graph = None
        self.number_of_visits = 0

    def add_connection(self, connection):
        self.connections.add(connection)

    def get_connections(self):
        return list(self.connections)

    def close_station(self, n):
        self.closed = True
        sys.stdout.write("Owner {} found cat {} - {} is now closed\n".format(n, n, self.name))
        # construct lines again to see if the cats are humnans are in the same networks
        self.ug.construct_networks()

    def set_graph(self, graph):
        self.graph = graph


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
        self.station.number_of_visits += 1
        self.moves += 1
        return True


class Human:
    def __init__(self, human_id):
        self.human_id = human_id
        self.visited_stations = set()
        self.moves = 0
        self.cat_missing = True

    def set_random_start_station(self, stations):
        # stations is a dict
        self.station = stations[random.choice(list(stations.keys()))]
        while self.station == self.cat.station:
            self.station = stations[random.choice(list(stations.keys()))]
        self.visited_stations.add(self.station)

    def cat_in_different_network(self):
        return self.station.graph != self.cat.station.graph

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
        self.visited_stations.add(self.station)
        self.station.number_of_visits += 1
        return True

    def cat_found(self):
        if self.station == self.cat.station:
            self.cat_missing = False
            self.station.close_station(self.human_id)
        return not self.cat_missing


# we initialize the underground and create the stations
ug = UnderGround()
ug.build_stations(stations_file, station_connections_file)
# construct the initial tubenetwork
ug.construct_networks()
ug.create_humans_and_lost_cats(N)
ug.find_the_cats()

sys.stdout.write("Total number of cats: {}\n".format(N))
sys.stdout.write("Number of cats found: {}\n".format(ug.cats_found))
avg_moves = sum([f.moves for f in ug.founders])/ug.cats_found if ug.cats_found else 0
sys.stdout.write("Average number of movements required to find a cat: {}\n".format(math.ceil(avg_moves)))
most_visited_station = max(list(ug.stations.values()), key=lambda x: x.number_of_visits)
sys.stdout.write("Most visited station was {} with {} visists".format(most_visited_station.name,
                                                                      most_visited_station.number_of_visits))

