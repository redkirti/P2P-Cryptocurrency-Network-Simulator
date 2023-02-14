class Block:
    def __init__(self, blkid, txnsarr, prevblkid):
        self.blkid = blkid
        self.txnsarr = txnsarr
        self.prevblkid = prevblkid
        self.creatorid = None
        self.balance = []
        self.level = 1