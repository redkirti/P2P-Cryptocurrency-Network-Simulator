class Node:
    def __init__(self, nodeid, peersarr, unspenttxnsarr, alltxnsarr, slow, low):
        self.nodeid = nodeid
        self.peersarr = peersarr
        self.blockchain = {}
        self.unspenttxnsarr = unspenttxnsarr
        self.alltxnsarr = alltxnsarr
        self.slow = slow
        self.low = low