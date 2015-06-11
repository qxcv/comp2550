# Report-specific TODO list

1. Benchmark the performance of particle filtering with and without map
   filtering enabled.
2. Benchmark performance of algorithm with varying number of particles.
3. Perform an experiment of some sort (doesn't have to be a rigorous benchmark;
   probably *can't* be a rigorous benchmark) to demonstrate how the algorithm
   copes with the vehicle travelling off-road. I think it might be sensible to
   achieve this by taking one of the maps which Brubaker et al. produced and
   removing a couple of roads from it, then re-running localisation with the
   roads missing :D
