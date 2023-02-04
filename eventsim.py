# random peer connections in the network
# random transaction generation by each peer with a value chosen from poisson distribution
# broadcasting the messages (transactions/blocks) in a loopless manner
# simulating network latencies based on propogation delay, message size, link speeds of nodes, and queing delay
# random block creating with arrival times chosen from a poisson distribution
# propogation of blocks on the block chain
# addition of blocks to a local blockchain of a node and resolution of forks based on block arrival time, the chain with first arrived one is extended.

import sys
from node import Node
import random
import numpy as np
from initialize import initialize
from heapq import *
from event import Event
from transaction import Txn
from block import Block

#No of peers
peers = int(sys.argv[1])
# Percent of slow peers
slow = int(sys.argv[2])
#Percent of peers with low CPU
lowCPU = int(sys.argv[3])

simulationTime = int(sys.argv[4])

node, hpower = initialize(peers, slow, lowCPU)
heap = []
currentTime = 0
txncount = 0
rho = []  #positive minimum value corresponding to speed of light propagation delay

for i in range(peers):
    rho.append(list(range(0,peers)))

for i in range(peers):
    for j in range(peers):
        if(j>i):
            rho[i][j] = random.uniform(0.01,0.5)
        elif(j<i):
            rho[i][j] = rho[j][i]
        else:
            rho[i][j] = 0

# for i in rho:
#     print(i)




# Filling queue with transaction sending events
while(currentTime<simulationTime):
    #Scale is the mean of the exponential distribution
    currentTime = currentTime + np.random.exponential(scale=2) 
    sender = random.randint(0,peers-1)
    heappush(heap, Event(currentTime, "sendTxn", sender, -1, Txn(0,0,0), Block(0,[],0)))

currentTime = 0
# Filling queue with block sending events
while(currentTime<simulationTime):
    #Scale is the mean of the exponential distribution
    currentTime = currentTime + np.random.exponential(scale=2) 
    sender = random.randint(0,peers-1)
    heappush(heap, Event(currentTime, "sendTxn", sender, -1, Txn(0,0,0), Block(0,[],0)))


# Genereating random transaction information
def generateTxn(sender):
    receiver = random.randint(0,peers-1)
    while(sender == receiver):
        receiver = random.randint(0,peers-1)
    amount = random.randint(0,5) + random.random()
    txn = Txn(sender, receiver, amount)
    txnstr = str(txn.txnid) + ": " + str(sender) + "pays" + str(receiver) + "coins"
    return txn

# Creating a Block
def createBlock():
    pass

#Calculating latencies for different links
def calculateLatency(sender, receiver, type):
    if(type == "txn"):
        size = 1024
    else:
        size = 1024*1024
    if(node[sender].slow or node[receiver].slow):
        c = 5*1000000
    else:
        c = 100000000
    d = 96 * 1000 / c
    return (rho[sender][receiver] + ((size*8)/c) + np.random.exponential(scale=d))

currentTime = 0
txncreationTime = 0

# Main simulation function
while(currentTime<simulationTime):
    event = heappop(heap)
    currentTime = event.timestamp
    if(event.type == "sendTxn"):
        txn = generateTxn(event.eventfrom)
        # node[txn.sender].peersarr    : This represents nodes this node is connected to
        for i in node[txn.sender].peersarr:
            latency = calculateLatency(txn.sender, i, "txn")
            heappush(heap, Event(currentTime+latency, "receiveTxn", event.eventfrom, i, txn, Block(0,[],0)))
    elif(event.type == "receiveTxn"):
        if event.txn.txnid in node[event.eventto].visited:
            continue
        # Adding txn to this node's list if txns
        node[event.eventto].unspenttxnsarr.append(event.txn)
        
        node[event.eventto].visited[event.txn.txnid] = True
        ls = node[event.eventto].peersarr.copy()
        ls.remove(event.eventfrom)
        for i in ls:
            latency = calculateLatency(event.eventto, i, "txn")
            heappush(heap, Event(currentTime+latency, "receiveTxn", event.eventto, i, event.txn, Block(0,[],0)))
    print(event)