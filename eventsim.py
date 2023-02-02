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

#No of peers
peers = int(sys.argv[1])
# Percent of slow peers
slow = int(sys.argv[2])
#Percent of peers with low CPU
lowCPU = int(sys.argv[3])


# Choosing slow and lowCPU nodes randomly
slowNodes = random.sample(range(0, peers-1), int(slow*peers/100))
lowNodes = random.sample(range(0, peers-1), int(lowCPU*peers/100))

# print(slowNodes)
# print(lowNodes)

# adj = np.random.rand(peers, peers)
# adj[adj > 0.5] = 1
# adj[adj <= 0.5] = 0
# print(adj)

# Creating peers
# for i in range(1, peers):

#     # s and l are two flags for slow and low CPU nodes
#     Node(i, [], [], [], [], s, l)



connectednodes = []

fullnodes = []

for i in range(0, peers-1):
    connectednodes.append([])

for i in range(0, peers-1):
    connections = random.randint(4, 8)
    if(connections<=len(connectednodes[i])):
        continue
    ls = list(range(0,peers-1))
    ls.remove(i)
    for j in connectednodes[i]:
        ls.remove(j)
    ls = list(set(ls) - set(fullnodes))
    if(len(ls)<(connections-len(connectednodes[i]))):
        continue
    connectednodes[i] += random.sample(ls, connections-len(connectednodes[i]))

    for k in connectednodes[i]:
        if i not in connectednodes[k]:
            connectednodes[k].append(i)
        if(len(connectednodes[k]) == 8) :
            fullnodes.append(k)
            # print("Welcome" + str(k))


for i in connectednodes:
    for j in i:
        print(str(j) + " ", end="")
    print("")
