"""
SPIKING NEURAL NETOWRK MODEL FOR INDEPENDENT/HERD AGENT CONTROLLER
Author: Nick Pellegrin
Development Start Date: 08/11/2023

"""

import nengo
import numpy as np
import matplotlib.pyplot as plt
from nengo.utils.matplotlib import rasterplot

#Global Variables
NUM_INPUTS = 6
NUM_ACTIONS = 4
DEFAULT_ENSEMBLE_NEURONS = 100
BASALGANGLIA_NEURONS = 100 #default = 100
THALAMUS_NEURONS = 50 #default = 50




def get_inputs(i):
    inputs = np.array([0.43, 0.33, 0.72, 0.002, 0.13, 0.94])
    return inputs[i]




model = nengo.Network()
with model:
    
    #Define model ensembles
    input_1 = nengo.Node(output=get_inputs(0))
    input_2 = nengo.Node(output=get_inputs(1))
    input_3 = nengo.Node(output=get_inputs(2))
    input_4 = nengo.Node(output=get_inputs(3))
    input_5 = nengo.Node(output=get_inputs(4))
    input_6 = nengo.Node(output=get_inputs(5))
    

    input_ensemble = nengo.Ensemble(n_neurons=DEFAULT_ENSEMBLE_NEURONS * NUM_INPUTS, dimensions=NUM_INPUTS)
    utility_ensemble = nengo.Ensemble(n_neurons=DEFAULT_ENSEMBLE_NEURONS * NUM_ACTIONS, dimensions=NUM_ACTIONS)
    basal_ganglia = nengo.networks.BasalGanglia(n_neurons_per_ensemble=BASALGANGLIA_NEURONS, dimensions=NUM_ACTIONS)
    thalamus = nengo.networks.Thalamus(n_neurons_per_ensemble=THALAMUS_NEURONS, dimensions=NUM_ACTIONS)
    action_ensemble = nengo.Ensemble(n_neurons=DEFAULT_ENSEMBLE_NEURONS * NUM_ACTIONS, dimensions=NUM_ACTIONS)
    
    #Define connections between ensembles
    nengo.Connection(input_1, input_ensemble[0], synapse=None)
    nengo.Connection(input_2, input_ensemble[1], synapse=None)
    nengo.Connection(input_3, input_ensemble[2], synapse=None)
    nengo.Connection(input_4, input_ensemble[3], synapse=None)
    nengo.Connection(input_5, input_ensemble[4], synapse=None)
    nengo.Connection(input_6, input_ensemble[5], synapse=None)

    nengo.Connection(input_ensemble, utility_ensemble, function=lambda x: np.dot(x, np.random.rand(NUM_INPUTS, NUM_ACTIONS)))
    nengo.Connection(utility_ensemble, basal_ganglia.input, synapse=None)
    nengo.Connection(basal_ganglia.output, thalamus.input, synapse=0.01)
    nengo.Connection(thalamus.output, action_ensemble, synapse=0.01)

    #Define model probes
    utility_probe = nengo.Probe(utility_ensemble, synapse=0.2)
    output_probe = nengo.Probe(thalamus.output, synapse=0.01)
    bas_probe = nengo.Probe(basal_ganglia.output, synapse=0.01)
    



with nengo.Simulator(model) as sim:
    sim.run(1)

#Plot utility value
plt.figure()
plt.plot(sim.trange(), sim.data[utility_probe])
plt.legend([f"Action {action_id} Utility" for action_id in range(NUM_ACTIONS)])
plt.title("Action Utility")

#Plot BG-TH output value
plt.figure()
plt.plot(sim.trange(), sim.data[output_probe])
plt.legend([f"Action {action_id}" for action_id in range(NUM_ACTIONS)])
plt.title("Thalamus Output")

plt.show()



