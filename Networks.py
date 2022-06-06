# Foundation code for a network-based computational model of
#systemic risk in banking networks

__author__="Vaishnav Puri"


class Node:
    neighbours = []
    name = "not set"

    def __init__(self, nodeName):
        self.neighbours = []
        self.name = nodeName

    def printNeighbours(self):
        print("\nNeighbours of ", self.name, ": ")
        for neighbour in self.neighbours:
            print(neighbour.name, ",")
        return

    def addNeighbour(self, newNode):
        self.neighbours.append(newNode)
        return

class Graph:
    Nodes = []

    def __init__(self, nodes):
        self.Nodes = []
        for node in nodes:
            self.Nodes.append(node)
        return

    def addLink(self, nodeA, nodeB):
        nodeA.addNeighbour(nodeB)
        return

    def addTwoWayLink(self, A, B):
        nodeA = self.get(A)
        nodeB = self.get(B)
        self.addLink(nodeA, nodeB)
        self.addLink(nodeB, nodeA)
        return

    def addOneWayLink(self, A, B):
        intersectionA = self.get(A)
        intersectionB = self.get(B)
        self.addLink(intersectionA, intersectionB)
        return

    def get(self, name):
        #Check if any nodes exist
        if(len(self.Nodes) == 0):
            self.Nodes.append(Node(name))
        else:
            fetched = self.Nodes[0]
        #Check if node already exists
        found = 0
        for node in self.Nodes:
            if node.name == name:
                fetched = node
                found = 1
                break
        #If not found append new node and return
        if found == 0:
            fetched = Node(name)
            self.Nodes.append(fetched)
        #Return the found / new node
        return fetched

    def printNodes(self):
        print ("\nList of all Nodes: ")
        for node in self.Nodes:
            print(node.name, ",")
        return




# This contains the actual implementation of a simple systemic risk modeller.
# It is essentially a network based computational model of systemic risk. 


import csv
import random
import math

class User(Node):
    assets = 0
    deposits = 0
    totalShock = 0

    def __init__(self, n, a, d):
        Node.__init__(self, n)
        self.assets = a
        self.deposits = d
        self.totalShock = 0
        return

    def getShock(self, shock):
        if shock >= 0.025:
            networkEffect = len(self.neighbours) + 1
            self.totalShock = self.totalShock + shock / networkEffect
            for neighbour in self.neighbours:
                neighbour.getShock(shock / networkEffect)
            return
        else:
            self.totalShock = self.totalShock + shock

class InterNetwork(Graph):

    numLinks = 0

    def __init__(self, banks):
        Graph.__init__(self, banks)

    def constructNetwork(self):
        numUser = len(self.Nodes)
        self.numLinks = int(numUser + random.random() * (numUser * numUser))
        for i in range(self.numLinks):
            x = int(random.random() * numUser)
            y = int(random.random() * numUser)
            if x == y:
                y = y - 1
            self.addTwoWayLink(self.Nodes[x].name, self.Nodes[y].name)
        return

    def printNetwork(self):
        for user in self.Nodes:
            user.printNeighbours()

    def analyzeNetwork(self):
        totalShocked = 1
        maxShock = 0.0
        minShock = 1.0

        for user in self.Nodes:
            if user.totalShock > 0.0:
                totalShocked = totalShocked + 1
            if user.totalShock > maxShock:
                maxShock = user.totalShock
            if user.totalShock < minShock:
                minShock = user.totalShock

        return Result(self.numLinks, totalShocked, maxShock, minShock)

    def startShock(self, impacts):
        numUser = len(self.Nodes)
        for i in range(impacts):
            x = int(random.random() * numBanks)
            self.Nodes[x].getShock(1.0)

    def resetNetwork(self):
        for user in self.Nodes:
            user.totalShock = 0.0
            user.neighbours = []

class Result:
    numLinks = 0
    totalShocked = 1
    maxShock = 0.0
    minShock = 1.0

    def __init__(self, nl, ts, max, min):
        self.numLinks = nl
        self.totalShocked = ts
        self.maxShock = max
        self.minShock = min


#inspired from https://gist.github.com/StuartGordonReid/9deb4ce312138e78debc#file-interbanknetworkmainmethod-py

if __name__ == "__main__":
    sys = []
    with open('#Data','rb') as data:
        reader = csv.reader(data)
        for datum in reader:
            # Datum = ['Bank name', 'Assets', 'Deposits']
            user = User(datum[0], datum[1], datum[2])
            sys.append(user)
    interNetwork = InterNetwork(sys)

    Results = []
    for i in range(1000000):
        interNetwork.constructNetwork()
        interNetwork.startShock(10)
        Results.append(interNetwork.analyzeNetwork())
        interNetwork.resetNetwork()

    print("Links, Avg links per node, #Results, Avg Node Shocked, Avg Max Shock, Avg Min Shock, Max Max Shock, Max Min Shock, Stdev Nodes Shocked, Stdev Max Shock, Stdev Min Shock")
    for links in range(2700):
        totalResults = 0

        # Once off count metrics
        avgTotalShocked = 0.0
        avgMaxShock = 0.0
        avgMinShock = 0.0
        maxMaxShock = 0.0
        maxMinShock = 1.0

        for result in Results:
            if result.numLinks == links:
                totalResults = totalResults + 1
                avgTotalShocked = avgTotalShocked + result.totalShocked
                avgMaxShock = avgMaxShock + result.maxShock
                avgMinShock = avgMinShock + result.minShock
                if result.maxShock > maxMaxShock:
                    maxMaxShock = result.maxShock
                if result.minShock < maxMinShock:
                    maxMinShock = result.minShock                  
                if totalResults > 0: 
                    avgTotalShocked = avgTotalShocked / totalResults
                    avgMaxShock = avgMaxShock / totalResults
                    avgMinShock = avgMinShock / totalResults

            # Standard deviations
            stdevTotalShocked = 0.0
            stdevMaxShock = 0.0
            stdevMinShock = 0.0

            for result in Results:
                if result.numLinks == links:
                    stdevTotalShocked = stdevTotalShocked + math.pow((result.totalShocked - avgTotalShocked),2.0)
                    stdevMaxShock = stdevMaxShock + math.pow((result.maxShock - avgMaxShock),2.0)
                    stdevMinShock = stdevMinShock + math.pow((result.minShock - avgMinShock),2.0)

            stdevTotalShocked = math.sqrt(stdevTotalShocked/totalResults)
            stdevMaxShock = math.sqrt(stdevMaxShock/totalResults)
            stdevMinShock = math.sqrt(stdevMinShock/totalResults)

            print(links, ",",(links / 50),",", totalResults,",", avgTotalShocked, 
            ",", avgMaxShock,",", avgMinShock,",", maxMaxShock,",", maxMinShock,
            ",",stdevTotalShocked,",",stdevMaxShock,",",stdevMinShock)
