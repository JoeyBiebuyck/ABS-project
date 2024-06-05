# Grid Packing

**This project contains a simulation of the grid packing puzzle. It was build by J. Biebuyck, C. Monderen, O. Nolf.
 As their project for the course Agent Based Systems at VUB.**

Grid packing is a puzzel where agents have to collaborate to retrieve items, from an order, from a grid and bring them to a loading dock.
The goal for these agents is to fulfill these orders as quickly as possible.

We used two types of methods to make the collaboration happen.
- A _decentralised agent_, which communicates with the other agents to decide who retrieves which item.
- A _centralised agent_, that does all the decision-making and then sends commands to the following agents.
These agent classes can be found in the /agents/ directory.

In the directory grids there is a logic grid, which is used as the grid where information is stored, and a
visual grid, which makes a graphical representation of everything that goes on in the logic grid.
Lastly the file grid_classes.py can be found in grids. this file contains classes like: an item, a loading dock
and a position.

In the directory /utilities/ you can find some files containing all tools we implemented to run the simulations.
- _Util.py_ contains all our helper functions and classes which are not strictly a method of a class.
Some examples are: a priority queue class, the A* path-finding algorithm, an order generator and some functions needed
for our analysis.
- _test_items.py_ contains 30 fixed orders, this way we could have the same orders for the tests in OV1.
- _globals.py_ contains some variables that should be accessible between multiple files for our data collection.

### How to run a simulation:

The file _required_packages.py_ contains a script that installs al the necessary packages the run the simulations.

To do a simulation you should run one of the demo files:
- _decentralised_demo.py_ will run a simulation using the decentralised agents
- _centralised_demo.py_ will run a simulation using the decentralised agents

There are two files, OV1.py and OV2.py, and two directories, /Data OV1/ and /Data OV2/, left. These were used to collect the data for our research questions.
_OV1.py_ contains a loop that tests the efficiency of the centralised and decentralised agents. Data OV 1 contains the gathered data.
_OV2.py_ contains a loop that runs the decentralised implementation with different combinations of parameters. Data OV 2 contains the gathered data.
