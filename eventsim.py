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

#interarrival time for Transactions
Tx=int(sys.argv[4])

# interarrival time for Blocks
I=int(sys.argv[5])

simulationTime = int(sys.argv[6])

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




# Filling queue with transaction sending events
while(currentTime<simulationTime):
    #Scale is the mean of the exponential distribution
    currentTime = currentTime + np.random.exponential(scale=Tx) 
    sender = random.randint(0,peers-1)
    heappush(heap, Event(currentTime, "createTxn", sender, -1, None, None, None))

currentTime = 5
# Filling queue with block sending events

def createBlkEvent(currentTime, i, level):
    # print("Block event created - Time : %s, level : %s , Node Number: %s"%(currentTime,level,i) )
    if nodes[i].low == True:
        power = hpower
    else:
        power = hpower * 10
    stamp = np.random.exponential(scale=(I/power))
    print(stamp)
    e = Event(currentTime + stamp, "createBlk", i, -1, None, None, level)
    e.tempCurr = nodes[i].currentHash
    heappush(heap, e)

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
# while(currentTime<simulationTime):
while currentTime<simulationTime:
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

        prevCurr = nodes[event.eventfrom].currentHash
        if prevCurr!=event.tempCurr:
            # Tx = currentTime + np.random.exponential(scale=0.5)
            # createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)
            continue

        blk = nodes[event.eventfrom].generateBlock()
        blk.level = event.level+1
        nodes[event.eventfrom].level += 1
        nodes[event.eventfrom].currentHash = blk.blkid
        
        print("Block created - Time : %s, Block ID : %s , Node Number: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>"%(currentTime,blk.blkid,event.eventfrom) )
        nodes[event.eventfrom].blkvisited[blk.blkid] = True
        # time_ = currentTime + np.random.exponential(scale=Tb) 

        # Creating next block generation event for the same peer
        createBlkEvent(currentTime, event.eventfrom, event.level+1)
        
        # Sending blocks to other nodes
        for i in nodes[event.eventfrom].peersarr:
            latency = calculateLatency(event.eventfrom, i, "blk")
            heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventfrom, i, None, blk, event.level))
    
    elif (event.type == "receiveBlk"):
        if event.block.blkid in nodes[event.eventto].blkvisited:
            continue
        nodes[event.eventto].blkvisited[event.block.blkid] = True
        # Verify transactions
        flag = nodes[event.eventto].verify(event.block)
        if flag == False:
            continue

        # If valid then add the block in the chain
        nodes[event.eventto].updateChain(event.block)
        # node[event.eventto].verify(event.block)
        # Same receive block txns can also arrive, ignore it
        blk = event.block
        # time_ = currentTime + np.random.exponential(scale=Tb) 

        
        print(">>>>>>>>>>>>>>>Block Recived - Time : %s, Block ID : %s , Node Number: %s"%(currentTime,blk.blkid,event.eventto) )
        # createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)        

        mx, blkhash = nodes[event.eventto].cache_function(event.block.blkid)

        if nodes[event.eventto].level == event.level:
            # Update current hash and create a new create block event
            nodes[event.eventto].currentHash = blk.blkid
            nodes[event.eventto].level += 1
            if mx > nodes[event.eventto].level:
                nodes[event.eventto].currentHash = blkhash
                createBlkEvent(currentTime, event.eventto, mx+1)
            else:
                # Creating next block generation event for the same peer
                createBlkEvent(currentTime, event.eventto, event.level+1)

        ls = nodes[event.eventto].peersarr.copy()
        ls.remove(event.eventfrom)
        for i in ls:
            latency = calculateLatency(event.eventto, i, "blk")
            heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventto, i, None, event.block, event.level))

    # print(event)    

slow=[]
for nd in nodes:
    print("Dumped by " + str(nd.nodeid) + ": ", end="")
    print(nd.dumped_blocks)
    nd.showBlockchain()
    nd.findLongestChain()
    nd.printStats()
    if nd.slow==True :
        slow.append(nd.nodeid)
    print(slow)
dot.render('doctest-output/round-table.gv', view=True)  # doctest: +SKIP
longestChain.render('doctest-output/longest-chain-table.gv', view=True)  # doctest: +SKIP
