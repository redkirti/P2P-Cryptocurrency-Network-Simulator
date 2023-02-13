import random
import hashlib
from block import Block
from graphy import dot,longestChain
from transaction import Txn

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
        self.level = 1
        # self.currentHash = str(hashlib.sha256("0".encode()).hexdigest())
        self.currentHash = "0"
        self.register={}
        self.genesis=self.getGenesis()
        self.hashMapping = {}
        self.currNo = {}
        self.stats = {
                "totalTransactions" : 0 ,
                "totalBlocksTree" : 0,
                "invalidBlocks" : 0,
                "totalBlockLongestChain" : 0,
                "longestChainLen":0
        }

        self.dumped_blocks = []
        

    def getGenesis(self):
        blk=Block("0",[],None)
        blk.balance=[10]*self.peers
        self.blockchain["0"]=[blk]
        self.register["0"]=blk
    

    def verify(self, block):
        temp_balance = self.register[block.prevblkid].balance.copy()
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
            self.dumped_blocks.append(block)
            return False
        return True




    # Still have to add coinbase txn in the block generation function....

    def generateBlock(self):
        txns = random.sample(self.unspenttxnsarr, 2)
        msg = ""
        current_block = self.register[self.currentHash]
        temp_balances = current_block.balance.copy()
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
        self.level += 1
        self.updateChain(blk)
        self.register[hash]=blk

        return blk

    def updateChain(self, blk):
        blkChain = self.blockchain
        prevBlkId = blk.prevblkid
        
        # # if block hash not key blockchain dictionary
        # if self.currentHash not in blkChain:
        #     blkChain[self.currentHash] = []

        # if  Previous block hash not key blockchain dictionary
        if prevBlkId not in blkChain.keys() :
            blkChain[prevBlkId] = []

        self.register[blk.blkid]=blk
        blkChain[prevBlkId].append(blk)
        
        # self.currentHash = blk.blkid
        # self.register[blk.blkid] = blk

        # for txn in blk.txnsarr:
        #     # Updating balance of nodes
        #     # self.balance[txn.sender] -= txn.amount
        #     # Removing used txns from unspent transactions 
        #     if txn in self.unspenttxnsarr:
        #         self.unspenttxnsarr.remove(txn)
    
    
    def showBlockchain(self):
        visited = []
       
        self.currNo = 1
        # create Nodes for the graph
        for node in self.blockchain.keys():
            self.hashMapping[str(self.nodeid)+"_Node_"+node]="_Node_"+str(self.nodeid)+"__"+str(self.currNo)
            self.currNo+=1
            dot.node(self.hashMapping[str(self.nodeid)+"_Node_"+node])

        def dfs(currId):
            if currId != "0":
                currBlock = self.register[currId]
                self.stats["totalTransactions"]+= len(currBlock.txnsarr)

            if (currId) not in self.blockchain.keys():
                return 
            
            for next in self.blockchain[currId]:
                nextId = next.blkid
 
                if (str(self.nodeid)+"_Node_"+nextId) not in self.hashMapping:
                    self.hashMapping[str(self.nodeid)+"_Node_"+nextId]="_Node_"+str(self.nodeid)+"__"+str(self.currNo)
                    self.currNo+=1

                if  (self.hashMapping[str(self.nodeid)+"_Node_"+nextId]) not in visited:
                    dot.edge(self.hashMapping[(str(self.nodeid)+"_Node_"+currId)],self.hashMapping[(str(self.nodeid)+"_Node_"+nextId)])
                    visited.append(self.hashMapping[(str(self.nodeid)+"_Node_"+nextId)])
                    dfs(nextId)

        for currNode in self.blockchain.keys():
            if currNode not in visited:
                visited.append(self.hashMapping[str(self.nodeid)+"_Node_"+currNode])
                dfs(currNode)

        
    def findLongestChain(self):
        self.longestChain = []
        visited = []
        def dfs(temp,currId):
            if currId in visited:
                return
            visited.append(currId)
            temp.append(currId)

            if currId not in self.blockchain:
                self.blockchain[currId] = []

            for next in self.blockchain[currId]:
                nextId = next.blkid
                if (nextId) not in visited:
                    dfs(temp,nextId)
            
            if len(temp)>len(self.longestChain):
                self.longestChain = temp.copy()
            temp.pop()
        dfs([],"0")
        self.stats["longestChainLen"] = len(self.longestChain)
        # print(self.longestChain)
        lastNode = None
        for nodeVal in self.longestChain:
            currNode = self.hashMapping[str(self.nodeid)+"_Node_"+nodeVal]
            longestChain.node(currNode)
            if lastNode:
                longestChain.edge(lastNode, currNode)
            lastNode = currNode
        
    def printStats(self):
        print("------------------Node Statistics %s-------------------"%self.nodeid)
        totalTransactions = self.stats["totalTransactions"]
        totalBlocksTree = 0
        
        invalidBlocks = len(self.dumped_blocks)

        totalBlockLongestChain = self.stats["longestChainLen"]

        totalBlocksInBlockChain = list(self.blockchain.keys())
        for block in self.blockchain.values():
            for crrBlock in block:
                totalBlocksInBlockChain.append(crrBlock.blkid)
        
        totalBlocksTree = len(set(totalBlocksInBlockChain))
        print("Total Blocks in Longest Chain:",totalBlockLongestChain)
        print("Total Transactions:",totalTransactions)
        print("Total Blocks in Tree:",totalBlocksTree)
        print("Total Invalid Blocks Dumped By node:",invalidBlocks)
        # print("Total Transactions:",totalTransactions)
        # self.stats["longestChainLen"] =

        # for nodes in self.block:

        print("-------------------------x--------------------------")
