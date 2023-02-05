import random
import hashlib
from block import Block
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
        self.register={}

    # Still have to add coinbase txn in the block generation function....

    def generateBlock(self):
        txns = random.sample(self.unspenttxnsarr, 2)
        msg = ""
        for i in txns:
            msg += i.txnstr
        # balance = self.register[self.currentHash].balance
        # for txn in txns:
        #     if txn.sender not in balance:
        #         balance[txn.sender] = 1000
        #     if txn.receiver not in self.balance:
        #         balance[txn.receiver] = 1000
        #     balance[txn.sender] -= txn.amount
        #     balance[txn.receiver] += txn.amount

        # Add some extra random values to the string --later
        hash = str(hashlib.sha256(msg.encode()).hexdigest())
        blk = Block(hash, txns, self.currentHash)
        self.updateChain(blk)
        self.register[hash]=blk
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


    
        

    # def verify(self, block):
