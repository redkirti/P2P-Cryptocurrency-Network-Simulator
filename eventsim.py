# random peer connections in the network
# random transaction generation by each peer with a value chosen from poisson distribution
# broadcasting the messages (transactions/blocks) in a loopless manner
# simulating network latencies based on propogation delay, message size, link speeds of nodes, and queing delay
# random block creating with arrival times chosen from a poisson distribution
# propogation of blocks on the block chain
# addition of blocks to a local blockchain of a node and resolution of forks based on block arrival time, the chain with first arrived one is extended.
# New line added


import sys
from node import Node
import random
import numpy as np
from initialize import initialize
from heapq import *
from event import Event
from transaction import Txn
from graphy import dot,longestChain
from block import Block

#No of peers
peers = int(sys.argv[1])
# Percent of slow peers
slow = int(sys.argv[2])
#Percent of peers with low CPU
lowCPU = int(sys.argv[3])

simulationTime = int(sys.argv[4])

nodes, hpower = initialize(peers, slow, lowCPU)
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
    currentTime = currentTime + np.random.exponential(scale=0.5) 
    sender = random.randint(0,peers-1)
    heappush(heap, Event(currentTime, "createTxn", sender, -1, None, None, None))

currentTime = 0
# Filling queue with block sending events

def createBlkEvent(currentTime, i, level):
    # print("Block event created - Time : %s, level : %s , Node Number: %s"%(currentTime,level,i) )
    if nodes[i].low == True:
        power = hpower
    else:
        power = hpower * 10
    stamp = np.random.exponential(scale=(10/power))
    # print(stamp)
    heappush(heap, Event(currentTime + stamp, "createBlk", i, -1, None, None, level))

for i in range(peers):
    createBlkEvent(currentTime, i, 1)
        


# Genereating random transaction information
def generateTxn(sender):
    receiver = random.randint(0,peers-1)
    while(sender == receiver):
        receiver = random.randint(0,peers-1)
    amount = random.randint(0,5) + random.random()
    txn = Txn(sender, receiver, amount)
    return txn

# # Creating a Block
# def generateBlock(sender):
#     pass

#Calculating latencies for different links
def calculateLatency(sender, receiver, type):
    if(type == "txn"):
        size = 1024
    else:
        size = 1024*1024
    if(nodes[sender].slow or nodes[receiver].slow):
        c = 5*1000000
    else:
        c = 100000000
    d = 96 * 1000 / c
    return (rho[sender][receiver] + ((size*8)/c) + np.random.exponential(scale=d))

currentTime = 0
txncreationTime = 0

# Main simulation function
while(currentTime<simulationTime):
# while len(heap)>0:
    event = heappop(heap)
    currentTime = event.timestamp
    if(event.type == "createTxn"):
        print("Random Transaction created - Time : %s, From : %s "%(currentTime,event.eventfrom) )
        txn = generateTxn(event.eventfrom)
        nodes[txn.sender].unspenttxnsarr.append(txn)
        # node[txn.sender].peersarr    : This represents nodes this node is connected to
        for i in nodes[txn.sender].peersarr:
            print("sending transactions from:%s -> to :%s"%(txn.sender,i))
            latency = calculateLatency(event.eventfrom, i, "txn")
            heappush(heap, Event(currentTime+latency, "receiveTxn", event.eventfrom, i, txn, None, None))
    elif(event.type == "receiveTxn"):
        if event.txn.txnid in nodes[event.eventto].txnvisited:
            continue
        # Adding txn to this node's list of txns
        print("Transaction Recived - Time : %s, From : %s, To : %s "%(currentTime,event.eventfrom, event.eventto) )

        nodes[event.eventto].unspenttxnsarr.append(event.txn)
        
        nodes[event.eventto].txnvisited[event.txn.txnid] = True
        ls = nodes[event.eventto].peersarr.copy()
        ls.remove(event.eventfrom)
        for i in ls:
            # print("sending transactions to :%s"%i)
            latency = calculateLatency(event.eventto, i, "txn")
            heappush(heap, Event(currentTime+latency, "receiveTxn", event.eventto, i, event.txn, None, None))
    elif (event.type == "createBlk"):

        # Check if a block exists at the same level in that node, if it exists then return null else create the blk
        # if nodes[event.eventfrom].currentHash!=event.tempCurr:
        #     Tx = currentTime + np.random.exponential(scale=0.5) 
        #     # # # if currentTime<simulationTime:
        #     createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)
        #     continue
        prevCurr = nodes[event.eventfrom].currentHash
        blk = nodes[event.eventfrom].generateBlock()
        
        print("Block created - Time : %s, Block ID : %s , Node Number: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>"%(currentTime,blk.blkid,event.eventfrom) )
        nodes[event.eventfrom].blkvisited[blk.blkid] = True
        Tx = currentTime + np.random.exponential(scale=0.5) 

        # Creating next block generation event for the same peer
        # if currentTime<simulationTime:
        # event.tempCurr = prevCurr
        createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)
        
        # Sending blocks to other nodes
        for i in nodes[event.eventfrom].peersarr:
            latency = calculateLatency(event.eventfrom, i, "blk")
            heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventfrom, i, None, blk, event.level))
    
    elif (event.type == "receiveBlk"):
        # Verify transactions
        # node[event.eventto].verify(event.block)
        # Same receive block txns can also arrive, ignore it
        blk = event.block
        Tx = currentTime + np.random.exponential(scale=0.5) 

        if event.block.blkid in nodes[event.eventto].blkvisited:
            continue
        
        print(">>>>>>>>>>>>>>>Block Recived - Time : %s, Block ID : %s , Node Number: %s"%(currentTime,blk.blkid,event.eventto) )
        # if currentTime<simulationTime:
        # event.tempCurr = blk.blkid
        # createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)        
        nodes[event.eventto].blkvisited[event.block.blkid] = True
        
        # If valid then add the block in the chain
        nodes[event.eventto].updateChain(event.block)
        
        # Creating next block generation event for the same peer
        # if currentTime<simulationTime:
        createBlkEvent(currentTime, event.eventto, event.level+1)

        nodes[event.eventto].blkvisited[event.block.blkid] = True
        ls = nodes[event.eventto].peersarr.copy()
        ls.remove(event.eventfrom)
        for i in ls:
            latency = calculateLatency(event.eventto, i, "blk")
            heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventto, i, None, event.block, event.level))

    # print(event)    


for nd in nodes:
    nd.showBlockchain()
    nd.findLongestChain()
    nd.printStats()
dot.render('doctest-output/round-table.gv', view=True)  # doctest: +SKIP
longestChain.render('doctest-output/longest-chain-table.gv', view=True)  # doctest: +SKIP
