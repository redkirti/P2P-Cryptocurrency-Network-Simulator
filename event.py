class Event:
    def __init__(self, timestamp, type, eventfrom, eventto, txn, block):
        self.timestamp = timestamp
        self.type = type
        self.eventfrom = eventfrom
        self.eventto = eventto
        self.txn = txn
        self.block = block
    
    def __repr__(self):
        return f'Node value: {self.timestamp} {self.type} {self.eventfrom} {self.eventto} {self.txn.txnid}'
    
    def __lt__(self, other):
        return self.timestamp<other.timestamp