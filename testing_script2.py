from pycoalescence import Simulation

for seed in range(10):
	s = Simulation(logging_level=40)
	s.set_simulation_parameters(seed, 4, "/Users/samthompson/Temp", 0.001, spatial=False, deme=100000)
	s.run()
	print(s.get_species_richness())