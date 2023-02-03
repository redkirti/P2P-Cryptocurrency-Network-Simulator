class Event:
    def __init__(self, timestamp, type, eventfor):
        self.timestamp = timestamp
        self.type = type
        self.eventfor = eventfor
    
    def __repr__(self):
        return f'Node value: {self.timestamp} {self.type} {self.eventfor}'
    
    def __lt__(self, other):
        return self.timestamp<other.timestamp