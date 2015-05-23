# To-do list

1. Make sure that my implementation complies with the SIR formalism. This
   probably means resampling at every step, but it also means finding
   probabilistic justification for my choice of (movement-dependent) transition
   distribution.
2. When resampling, pick some particles and scatter them uniformly in some
   region around the robot. If you have a GPS coordinate, pick some particles
   and scatter them uniformly around that.
3. Look into "leapfrog" edges between roads. A nicely curved edge to reflect the
   path of the vehicle at an intersection could make the filter more responsive
   during sharp turns.
4. Make sure that GPS fixes in Jose's data are ignored when 'signal' is 0.
5. Speed up movie writing :P
6. Look into increasing variance of Gaussian for GPS measurement likelihoods. At
   the moment, the particles are getting annihilated during GPS updates. I might
   also want to look into using less noise, since the plain map filter is seriously
   suffering for the amount of noise in its transition equations.
