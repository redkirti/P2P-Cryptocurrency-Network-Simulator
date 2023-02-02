class Event:
    def __init__(self, timestamp, name):
        self.timestamp = timestamp
        self.name = name
    def __cmp__(self, other):
        return (self.timestamp>other.timestamp) - (self.timestamp<other.timestamp)