

import nengo
import numpy as np
import matplotlib.pyplot as plt
from nengo.utils.matplotlib import rasterplot


def get_inputs(t):
    # if t < 0.5:
    #     return 0
    # else:
    #     return (2*t - 0.5)
    return t*t

model = nengo.Network()
with model:
    # sin = nengo.Node(lambda t: np.sin(8 * t))  # Input is a sine
    sin = nengo.Node(get_inputs)  # Input is a sine
    #cos = nengo.Node(lambda t: np.cos(8 * t))  # Input is a sine
    my_ensemble = nengo.Ensemble(1, dimensions=1, neuron_type=nengo.PoissonSpiking(nengo.LIF(0.01))) 
    nengo.Connection(sin, my_ensemble, synapse=0.01)
    #nengo.Connection(cos, my_ensemble[1], synapse=0.01)
    sin_probe = nengo.Probe(sin)
    #cos_probe = nengo.Probe(cos)
    En_probe = nengo.Probe(my_ensemble, synapse=0.01)  # 10ms filter
    En_spikes = nengo.Probe(my_ensemble.neurons)  # Collect the spikes

with nengo.Simulator(model) as sim:
    while sim.time < 1.0:
        sim.step()
    
# print(sim.data[probe][-10:])

# Plot the decoded output of the ensemble
plt.figure()
plt.plot(sim.trange(), sim.data[En_probe], label="Output")
plt.plot(sim.trange(), sim.data[sin_probe], "r", label="Input")
#plt.plot(sim.trange(), sim.data[cos_probe], "g", label="Input")
plt.xlim(0, 1)
plt.legend()

# Plot the spiking output of the ensemble
plt.figure()
rasterplot(sim.trange(), sim.data[En_spikes])
plt.xlim(0, 1)

plt.show()

