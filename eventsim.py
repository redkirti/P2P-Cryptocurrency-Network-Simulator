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



visited = []

def dfs(startNode): 
	visited[startNode] = True
	for neighbour in connectednodes[startNode]: 
		if (visited[neighbour] == False):
			dfs(neighbour)

def check():
    for i in range(0, peers-1):
        visited.append(False)
    dfs(0)
    flag = True
    for i in range(0, peers-1):
        if (visited[i] == False):
            flag = False
            break
    return flag


connectednodes = []

fullnodes = set()

def create_graph():
    for i in range(0, peers-1):
        connectednodes.append([])

    for i in range(0, peers-1):
        connections = random.randint(4, 8)
        if(connections<=len(connectednodes[i])):
            continue
        st = set(range(0,peers-1))
        st.remove(i)
        for j in connectednodes[i]:
            st.remove(j)
        st = st - fullnodes
        # print(st)
        if(len(st)<(connections-len(connectednodes[i]))):
            continue
        connectednodes[i] += random.sample(list(st), connections-len(connectednodes[i]))
        if (len(connectednodes[i])==8):
            fullnodes.add(i)
        for k in connectednodes[i]:
            if i not in connectednodes[k]:
                connectednodes[k].append(i)
            if(len(connectednodes[k]) == 8) :
                fullnodes.add(k)
                # print("Welcome" + str(k))

create_graph()
while (check() == False):
    visited = []
    connectednodes = []
    fullnodes = set()
    create_graph()

for i in connectednodes:
    for j in i:
        print(str(j) + " ", end="")
    print("")


# Creating peers
for i in range(1, peers):
    # s and l are two flags for slow and low CPU nodes
    Node(i, connectednodes[i], [], [], [], s, l)


