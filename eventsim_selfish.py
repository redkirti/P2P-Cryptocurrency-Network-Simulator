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
import gc

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

# Fraction of honest nodes an attacker is connected do.
zeta = int(sys.argv[6])
print("Hello" + str(zeta))
# Hashing power of attacker
hashpower = float(sys.argv[7])

# Simulation Time
simulationTime = int(sys.argv[8])

nodes, hpower = initialize(peers, slow, lowCPU, zeta, hashpower)
heap = []
currentTime = 0
txncount = 0
rho = []  #positive minimum value corresponding to speed of light propagation delay

for i in range(peers+1):
    rho.append(list(range(peers+1)))

for i in range(peers+1):
    for j in range(peers+1):
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

# Function to create block genereation event considering hashing power of the node
def createBlkEvent(currentTime, i, level):
    if currentTime>simulationTime:
        return
    # print("Block event created - Time : %s, level : %s , Node Number: %s"%(currentTime,level,i) )

    if i == peers:
        power = hashpower
    elif nodes[i].low == True:
        power = hpower
    else:
        power = hpower * 10
    stamp = np.random.exponential(scale=(I/power))
    # print(stamp)
    e = Event(currentTime + stamp, "createBlk", i, -1, None, None, level)
    e.tempCurr = nodes[i].currentHash
    heappush(heap, e)

# Pushing intitial block generation events
for i in range(peers+1):
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

# Creating queue for attacker private blocks
attacker_queue = []
# Creating a set for only releasing one block per level by attacker
released = set()
startlevel = 1
zerodash = False
timeStore = 0
# Main simulation function
# while(currentTime<simulationTime):
while len(heap)!=0 or len(attacker_queue)!=0:
    if len(heap)==0:
        print("Timestore: " + str(timeStore))
        attacker_block = attacker_queue.pop(0)
        for i in nodes[peers].peersarr:
            latency = calculateLatency(peers, i, "blk")
            blk = nodes[peers].register[attacker_block]
            heappush(heap, Event(timeStore+latency, "receiveBlk", peers, i, None, blk, blk.level-1))
    event = heappop(heap)
    currentTime = event.timestamp
    if currentTime>simulationTime and event.type == "createBlk":
        continue
    if(event.type == "createTxn"):
        # print("Random Transaction created - Time : %s, From : %s "%(currentTime,event.eventfrom) )
        txn = generateTxn(event.eventfrom)
        nodes[txn.sender].unspenttxnsarr.append(txn)
        # node[txn.sender].peersarr    : This represents nodes this node is connected to
        for i in nodes[txn.sender].peersarr:
            # print("sending transactions from:%s -> to :%s"%(txn.sender,i))
            latency = calculateLatency(event.eventfrom, i, "txn")
            heappush(heap, Event(currentTime+latency, "receiveTxn", event.eventfrom, i, txn, None, None))

    elif(event.type == "receiveTxn"):
        if event.txn.txnid in nodes[event.eventto].txnvisited:
            continue
        # Adding txn to this node's list of txns
        # print("Transaction Recived - Time : %s, From : %s, To : %s "%(currentTime,event.eventfrom, event.eventto) )

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
            continue

        blk = nodes[event.eventfrom].generateBlock()
        blk.level = event.level+1
        # nodes[event.eventfrom].level += 1
        nodes[event.eventfrom].currentHash = blk.blkid
        
        print("Block created - Time : %s, Block ID : %s , Node Number: %s, Level: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>"%(currentTime,blk.blkid,event.eventfrom, blk.level) )
        nodes[event.eventfrom].blkvisited[blk.blkid] = True
        # time_ = currentTime + np.random.exponential(scale=Tb) 

        # Creating next block generation event for the same peer
        createBlkEvent(currentTime, event.eventfrom, event.level+1)
        
        
        # Check for attacker , attacker doesn't publish blocks
        if(event.eventfrom != peers):
            # Sending blocks to other nodes
            for i in nodes[event.eventfrom].peersarr:
                latency = calculateLatency(event.eventfrom, i, "blk")
                heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventfrom, i, None, blk, event.level))
        else:
            if(zerodash == True):
                for i in nodes[event.eventfrom].peersarr:
                    latency = calculateLatency(event.eventfrom, i, "blk")
                    heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventfrom, i, None, blk, event.level))
                startlevel = blk.level
                zerodash = False
                attacker_queue = []
                released = set()
            else:
                attacker_queue.append(blk.blkid)
    
    elif (event.type == "receiveBlk"):
        if event.block.blkid in nodes[event.eventto].blkvisited:
            continue
        nodes[event.eventto].blkvisited[event.block.blkid] = True
        # Verify transactions
        flag = nodes[event.eventto].verify(event.block)
        if flag == 0:
            print("Invalid Block")
            continue
        # If it is a cached block just send to others
        if flag == 2 and event.eventto != peers:
            print("Block Cached by honest")
            ls = nodes[event.eventto].peersarr.copy()
            ls.remove(event.eventfrom)
            for i in ls:
                latency = calculateLatency(event.eventto, i, "blk")
                heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventto, i, None, event.block, event.level))
            print(">>>>>>>>>>>>>>>Block Recived - Time : %s, Block ID : %s , From Node: %s, To Node Number: %s, Block level: %s"%(currentTime,event.block.blkid, event.block.creatorid,event.eventto, event.block.level) )
            continue
        
        # For attacker if future block is received
        if flag == 2:
            print("Cached block by attacker")
            continue

        # If valid then add the block in the chain
        nodes[event.eventto].updateChain(event.block)

        # Same receive block txns can also arrive, ignore it
        blk = event.block        
        print(">>>>>>>>>>>>>>>Block Recived - Time : %s, Block ID : %s , From Node: %s, To Node Number: %s, Block level: %s"%(currentTime,blk.blkid, event.block.creatorid,event.eventto, blk.level) )
        # createBlkEvent(currentTime+Tx, event.eventfrom, event.level+1)        

        # Honest peers code
        if(event.eventto != peers):
            mx, blkhash = nodes[event.eventto].cache_function(event.block.blkid)
            print("Mx: " + str(mx) + ", blkhash: " + str(blkhash))
            print("node level: %s, event level: %s"%(nodes[event.eventto].level, event.level))
            if nodes[event.eventto].level == event.level:
                # Update current hash and create a new create block event
                nodes[event.eventto].currentHash = blk.blkid
                nodes[event.eventto].level += 1
                if mx > nodes[event.eventto].level:
                    nodes[event.eventto].currentHash = blkhash
                    createBlkEvent(currentTime, event.eventto, mx)
                else:
                    # Creating next block generation event for the same peer
                    createBlkEvent(currentTime, event.eventto, event.level+1)

            ls = nodes[event.eventto].peersarr.copy()
            ls.remove(event.eventfrom)
            for i in ls:
                latency = calculateLatency(event.eventto, i, "blk")
                heappush(heap, Event(currentTime+latency, "receiveBlk", event.eventto, i, None, event.block, event.level))
        # Attacker Code
        else:
            print("This is current start level: " + str(startlevel))
            ls = nodes[peers].peersarr.copy()
            zerodash = False
            mx, blkhash = nodes[event.eventto].cache_function(event.block.blkid)
            noofblocks = 1
            if mx>event.block.level:
                noofblocks = mx-event.block.level+1
                print("Max : " + str(mx) + " and  event.block.level: " + str(event.block.level))
            for i in range(noofblocks):
                if event.block.level in released or event.block.level<=startlevel:
                    print("Start level: %s, Block level: %s" %(startlevel, event.block.level))
                    continue
                attacker_level = len(attacker_queue)
                print("Attacker level: %s"%(attacker_level))
                if(attacker_level > 2):
                    print("Case: >2")
                    released.add(event.block.level)
                    blocktorelease = attacker_queue.pop(0)
                    blk = nodes[peers].register[blocktorelease]
                    for i in ls:
                        latency = calculateLatency(peers, i, "blk")
                        heappush(heap, Event(currentTime+latency, "receiveBlk", peers, i, None, blk, blk.level-1))
                elif(attacker_level == 2):
                    print("Case: =2")
                    released.add(event.block.level)
                    released.add(event.block.level+1)
                    blocktorelease = attacker_queue.pop(0)
                    blk = nodes[peers].register[blocktorelease]
                    for i in ls:
                        latency = calculateLatency(peers, i, "blk")
                        heappush(heap, Event(currentTime+latency, "receiveBlk", peers, i, None, blk, blk.level-1))
                    blocktorelease = attacker_queue.pop(0)
                    blk = nodes[peers].register[blocktorelease]
                    for i in ls:
                        latency = calculateLatency(peers, i, "blk")
                        heappush(heap, Event(currentTime+latency, "receiveBlk", peers, i, None, blk, blk.level-1))
                    released = set()
                    attacker_queue = []
                    startlevel = nodes[event.eventto].level
                    print("This is new start level" + str(startlevel))

                elif(attacker_level == 1):
                    print("Case: =1")
                    released.add(event.block.level)
                    blocktorelease = attacker_queue.pop(0)
                    blk = nodes[peers].register[blocktorelease]
                    for i in ls:
                        latency = calculateLatency(peers, i, "blk")
                        heappush(heap, Event(currentTime+latency, "receiveBlk", peers, i, None, blk, blk.level-1))
                    zerodash = True
                else:
                    print("Case: No lead")
                    released = set()
                    attacker_queue = []
                    nodes[peers].currentHash = event.block.blkid
                    createBlkEvent(currentTime, peers, event.block.level)
                    nodes[peers].level = event.block.level
                    startlevel = event.block.level
                    print("This is new start level" + str(startlevel))

        timeStore = currentTime
        # print(event)    


# Printing details of each node
for nd in nodes:
    print("Dumped by " + str(nd.nodeid) + ": ", end="")
    print(nd.dumped_blocks)
    nd.showBlockchain()
    nd.findLongestChain()
    nd.printStats(hashpower)

dot.render('doctest-output/round-table.gv', view=True)  # doctest: +SKIP
longestChain.render('doctest-output/longest-chain-table.gv', view=True)  # doctest: +SKIP

del heap
del nodes
gc.collect()

