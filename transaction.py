class Txn:
    counter = 0
    def __init__(self, sender, receiver, amount ) -> None:
        self.txnid = Txn.counter
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.txnstr = str(Txn.counter) + ": " + str(sender) + "pays" + str(receiver) + "coins"
        Txn.counter = Txn.counter + 1