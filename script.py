import os
from decimal import Decimal

def func(cmd):
    os.system(cmd)

i = Decimal('0.1')
while i<=Decimal('0.5'):
    zeta = str(i)
    cmd = "python3 eventsim_selfish.py 100 50 50 1 10 25 " + zeta +  " 1000 > output.txt"
    for j in range(5):
        func(cmd)
    i+=Decimal('0.1')
# func('python eventsim_selfish.py 100 50 50 1 10 25 0.3 1000')
