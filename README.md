# Grid Packing

**This project contains a simulation of the grid packing puzzle. It was build by J. Biebuyck, C. Monderen, O. Nolf.
As there project for the course Agent Based Systems at VUB.**

Grid packing is a puzzel where agents have to collaborate to retrieve, items in an order, from a grid and bring them to a loading dock.
The goal is for these agents is the fulfill these orders as efficiently as possible.

We have used two types of methods to make the collaboration happen.
A _decentralised agent_, which communicates with the other agents to decide who retrieves witch item and
a _centralised agent_, that does al the decision-making and then sends commands to a few following agents.
These agent classes can be found in the directory agents.

In the directory grids, one can find a logic grid, which we use as our grid we need to retrieve the items from and a
visual grid, which makes a graphical representation of everything that goes on in the logic grid.
Lastly the file grid_classes.py can be found in grids. this file contains classes like: an item, a loading dock
and a position.

In the directory utilities, you can find some files contain extra tools we implemented to run the simulations.
_Util.py_ contains al our helper functions and class which are not strictly a method of a class.
Some examples are: a priority queue class, the A* pathfinding algorithm, an order generator, some functions needed
for statistics.
_test_items.py_ contains 30 fixed orders, this way we could have the same orders for every test.
_strategies.py_ contains some strategies agents can use to divide the items between themselves.
_globals.py_ contains some variables that should be accessible between multiple files for our data collection.

### How to run a simulation:

The file _required_packages.py_ contains a script that installs al the necessary packages the run the simulations.

To do a simulation you should run 1 of the two demo files:
- _decentralised_demo.py_ wil run a simulation using the decentralised agents
- _centralised_demo.py_ wil run a simulation using the decentralised agents

There are two files and two directory left. These were used to collect the data for our research questions.
_OV 1.py_ contains a loop that tests the efficiency of the centralised and decentralised agents. Data OV 1 contains the gathered data.
_OV2 1.py_ contains a loop that runs the simulation with different parameters. Data OV 2 contains the gathered data.
