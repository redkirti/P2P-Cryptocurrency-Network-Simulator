import random
import hashlib
from block iport Block
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
        self.currentHash = hashlib.sha256("0").hexdigest()


    def generateBlock(self):
        txns = random.sample(self.unspenttxnsarr, 5)
        msg = ""
        for i in txns:
            msg += i.txnstr

        # Add some extra random values to the string ---later
        hash = hashlib.sha256(msg).hexdigest()
        self.level += 1
        blk = Block(hash, txns, self.currhash)
        blockchain[currentHash].append(blk)
        return blk

    def updateChain(block):
        self.level += 1
        self.blockchain[self.currentHash].append(block)
        self.currentHash = block.blkid
        for i in block.txnsarr:
            # Updating balance of nodes
            self.balance[i.sender] -= i.amount
            # Removing used txns from unspent transactions 
            if i in unspenttxnsarr:
                unspenttxnsarr.remove(i)
        
