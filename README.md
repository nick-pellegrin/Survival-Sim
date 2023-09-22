# Survival-Sim
animationTest.py is the main simulation file.  In this file, autonomous agents are simulated in an environment as either prey (white) or predator (red).  The predators eat the prey, and the prey eat the food (green) which spawns in randomly around the map over time. If a prey eats enough food, or if a predator eats enough prey, another prey or predator is spawned into the environment.  This simulates reproduction when resource availability reaches a certain threshold.  This simulation models population size in a simple environment, and given enough time the populations of predator and prey stabalize and reach an equilibrium solution.  

# Survival-Sim Demo
![](https://github.com/nick-pellegrin/Survival-Sim/blob/main/sim_demoGIF.gif)  

# Future Progress
model.py outlines a possible architecture for a spiking neural network using Nengo.  Future progress for this project includes training this biologically plausible network to hopefull autonomously drive decision making for the predators and prey, taking energy required to perform a task and weighing that against the perceived utility value of a particular action.
