class Event:
    def __init__(self, timestamp, type, eventfrom, eventto, txn, block, level):
        self.timestamp = timestamp
        self.type = type
        self.eventfrom = eventfrom
        self.eventto = eventto
        self.txn = txn
        self.block = block
        self.level = level
    
    def __repr__(self):
        return f'Node value: {self.timestamp} {self.type} {self.eventfrom} {self.eventto}'
    
    def __lt__(self, other):
        return self.timestamp<other.timestamp