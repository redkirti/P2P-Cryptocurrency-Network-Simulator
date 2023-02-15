# P2P-Cryptocurrency-Network-Simulator
A simple blockchain event simulator that mimics the working of an actual blockchain and allows to observe its behaviour under different parameters by creating events for:
- Transaction Creation
- Transaction Receiving
- Block Creation
- Block Receiving

Requirements:
- Python
- Graphviz for visualization of blockchain tree
- Numpy

Steps to Run:
In the project directory run:
```sh
python eventsim.py [arg1] [arg2] [arg3] [arg4] [arg5] [arg6] > output.txt
```
Replace the argumens with the following:
- [arg1] : The number of peers
- [arg2] : The percent of slow nodes
- [arg3] : The percent of low CPU nodes
- [arg4] : Interarrival time of transactions
- [arg5] : Interarrival time of blocks
- [arg6] : Simulation Time

output.txt contains the results of the simulation  
doctest-output folder contains the blockchains of the nodes along with their longest chains.

Changing the above parameters produces different block trees which are used for analysis.
