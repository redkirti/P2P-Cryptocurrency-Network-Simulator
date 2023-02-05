import random
import hashlib
from block import Block
from graphy import dot
# import graphviz  # doctest: +NO_EXE

class Node:
    def __init__(self, nodeid, peersarr, blockchain, unspenttxnsarr, alltxnsarr, slow, low, peers):
        self.nodeid = nodeid
        self.peersarr = peersarr
        self.blockchain = {}
        self.unspenttxnsarr = unspenttxnsarr
        self.alltxnsarr = alltxnsarr
        self.slow = slow
        self.low = low
        self.txnvisited = {}
        self.blkvisited = {}
        self.balance = [1000]*peers
        self.level = 0
        self.currentHash = str(hashlib.sha256("0".encode()).hexdigest())


    def generateBlock(self):
        txns = random.sample(self.unspenttxnsarr, 2)
        msg = ""
        for i in txns:
            msg += i.txnstr

        # Add some extra random values to the string ---later
        hash = str(hashlib.sha256(msg.encode()).hexdigest())
        blk = Block(hash, txns, self.currentHash)
        self.updateChain(blk)
        return blk

    def updateChain(self, block):
        self.level += 1
        if self.currentHash not in self.blockchain:
            self.blockchain[self.currentHash] = []
        self.blockchain[self.currentHash].append(block)
        self.currentHash = block.blkid
        for i in block.txnsarr:
            # Updating balance of nodes
            self.balance[i.sender] -= i.amount
            # Removing used txns from unspent transactions 
            if i in self.unspenttxnsarr:
                self.unspenttxnsarr.remove(i)
    
    def showBlockchain(self):
        visited = []
        for key,val in self.blockchain.items():
            if len(val)>1:
                print("FICCCCCLLLLLLKKKKK")
                print(key,val)
                for xx in val:
                    print(xx.blkid)
        # dot = graphviz.Graph(comment='Block Chain')
        # graphviz.Graph

        for nds in self.blockchain.keys():
            dot.node(str(self.nodeid)+"_Node_"+nds)
        # self.blockchain["5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"].append(Block("98989","8989","5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9"))
        # dot.edge(str(self.nodeid)+"_Node_"+"5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9",str(self.nodeid)+"new fork")
        def dfs(currId):
            if (currId) not in self.blockchain.keys():
                return 
            for next in self.blockchain[currId]:
                nextId = next.blkid
                if (str(self.nodeid)+"_Node_"+nextId) not in visited:
                    print("connecting curr   "+currId," ---->",nextId)
                    dot.edge((str(self.nodeid)+"_Node_"+currId),(str(self.nodeid)+"_Node_"+nextId))
                    visited.append((str(self.nodeid)+"_Node_"+nextId))
                    dfs(nextId)
        for currNode in self.blockchain.keys():
            if currNode not in visited:
                visited.append(str(self.nodeid)+"_Node_"+currNode)
                dfs(currNode)
        # doctest_mark_exe()
        print("--------------------_X------------------------")

        # dot.render('doctest-output/round-table.gv', view=True)  # doctest: +SKIP
        

