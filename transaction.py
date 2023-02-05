class Txn:
    counter = 0
    def __init__(self, sender, receiver, amount,  txnstr ) -> None:
        self.txnid = Txn.counter
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        Txn.counter = Txn.counter + 1
        self.txnstr = txnstr