import random
from node import Node
def initialize(peers, slow, lowCPU, zeta=0):
    print("Hello again" + str(zeta))
    # Choosing slow and lowCPU nodes randomly
    slowNodes = random.sample(range(peers), int(slow*peers/100))
    lowNodes = random.sample(range(peers), int(lowCPU*peers/100))
    hpower = (1 / ((10*peers)- (9*len(lowNodes))))

    print("Total Nodes: " + str(peers))
    print("Slow Nodes: ", end="")
    print(slowNodes)
    print("Low CPU Nodes: ", end="")
    print(lowNodes)

    visited = []

    def dfs(startNode): 
        visited[startNode] = True
        for neighbour in connectednodes[startNode]:
            if(neighbour == peers):
                continue
            if (visited[neighbour] == False):
                dfs(neighbour)

    def check():
        for i in range(peers):
            visited.append(False)
        dfs(0)
        flag = True
        for i in range(peers):
            if (visited[i] == False):
                flag = False
                break
        return flag


    connectednodes = []

    fullnodes = set()

    def create_graph():
        for i in range(peers):
            connectednodes.append([])
        if zeta!=0:
            connectednodes.append([])
            # Adding attacker node in graph
            fraction = int((int(zeta)/100)*peers)    #Fraction of honest nodes connected with attacker
            print("Here it comes: "+str(fraction))
            connectednodes[peers].extend(random.sample(range(peers), fraction))
            for i in connectednodes[peers]:
                connectednodes[i].append(peers)
            print("This is the list")
            print(connectednodes[peers])

        for i in range(peers):
            connections = random.randint(4, 8)
            if(connections<=len(connectednodes[i])):
                continue
            st = set(range(peers))
            st.remove(i)
            for j in connectednodes[i]:
                if j in st:
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




    print("Adjacency list of nodes: ")
    for i in connectednodes:
        print(i)

    node = []
    # Creating peers
    for i in range(peers):
        # s and l are two flags for slow and low CPU nodes
        isSlow = False
        isLowCPU = False
        if i in slowNodes:
            isSlow = True
        if i in lowNodes:
            isLowCPU = True
        node.append(Node(i, connectednodes[i], {}, [], [], isSlow, isLowCPU, peers))

    # Initializing the attacker node
    if zeta!=0:
        print("Hello")
        node.append(Node(peers, connectednodes[peers], {}, [], [], False, False, peers))
    else:
        print("Zero")

    return node, hpower