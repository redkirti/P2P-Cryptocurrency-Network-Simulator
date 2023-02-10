import random
import hashlib
from block import Block
from graphy import dot
from transaction import Txn
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
        self.peers=peers
        # self.balance = [1000]*peers
        self.level = 0
        # self.currentHash = str(hashlib.sha256("0".encode()).hexdigest())
        self.currentHash = "0"
        self.register={}
        self.genesis=self.getGenesis()
        

    def getGenesis(self):
        blk=Block("0",None,None)
        blk.balance=[1000]*self.peers
        self.blockchain["0"]=[blk]
    

    def verify(self, block):
        temp_balance = self.register[self.currentHash].balance.copy()
        incoming_txns = block.txnsarr
        for txn in incoming_txns:
            if txn.sender == -1:
                temp_balance[txn.receiver] += txn.amount
                continue
            if temp_balance[txn.sender]<txn.amount:
                return False
            temp_balance[txn.sender] -= txn.amount
            temp_balance[txn.receiver] += txn.amount
        if temp_balance != block.balance:
            return False
        return True




    # Still have to add coinbase txn in the block generation function....

    def generateBlock(self):
        txns = random.sample(self.unspenttxnsarr, 2)
        msg = ""
        current_block = self.register[self.currentHash]
        temp_balances = current_block.txnsarr.copy()
        for i in txns:
            temp_balances[i.sender] -= i.amount
            temp_balances[i.receiver] += i.amount
            msg += i.txnstr

        coinbase_txn = Txn(-1, self.nodeid, 50)
        temp_balances[self.nodeid] += 50
        coinbase_txn.txnstr = str(coinbase_txn.txnid)+ ": " + str(self.nodeid) + " mines 50 coins"
        txns.append(coinbase_txn)
        # Add some extra random values to the string --later
        msg += coinbase_txn.txnstr
        hash = str(hashlib.sha256(msg.encode()).hexdigest())
        blk = Block(hash, txns, self.currentHash)
        blk.balance = temp_balances
        blk.creatorid = self.nodeid
        self.updateChain(blk)
        self.register[hash]=blk

        return blk

    def updateChain(self, blk):
        blkChain = self.blockchain
        prevBlkId = blk.prevblkid
        
        self.level += 1
        # if block hash not key blockchain dictionary
        if self.currentHash not in blkChain:
            blkChain[self.currentHash] = []

        # if  Previous block hash not key blockchain dictionary
        if prevBlkId not in blkChain.keys() :
            blkChain[prevBlkId] = []

        blkChain[prevBlkId].append(blk)
        
        self.currentHash = blk.blkid

        for txn in blk.txnsarr:
            # Updating balance of nodes
            self.balance[txn.sender] -= txn.amount
            # Removing used txns from unspent transactions 
            if txn in self.unspenttxnsarr:
                self.unspenttxnsarr.remove(txn)
    
    def showBlockchain(self):
        visited = []

        # create Nodes for the graph
        for node in self.blockchain.keys():
            dot.node(str(self.nodeid)+"_Node_"+node)
       
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
        

