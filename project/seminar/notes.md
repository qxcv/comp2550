# Notes for COMP2550 presentation

## Intro slide

> Hi everyone! This semester, I've been working on a system for performing
> localisation in road vehicles---cars, trucks whatever.

## Localisation slide

- Phone analogy (if you've used a map on your phone, you've performed
  localisation)
- Easy for pedestrians, but harder when you have to do it continually, or with
  very high precision
- Important that it's reliable; can cause frustration (navigation systems) or
  safety hazards (self-driving cars) otherwise

## "Localisation is messy"

- We have lots of sensors to use for this
- They're not always reliable
- GPS is a good example
- Picture is from paper on classifying accuracy of GPS fixes. Trace taken from
  driving around with SiRFstarIII chip in a car. Goes off road frequently, which
  doesn't make sense.

## Using map data

- Vehicles are on the road most of the time, so why not use our knowledge of the
  road network to only localise on road?
- Becoming much easier with OpenStreetMap

## Past work

- Lots of people have tried this in the past with varying degrees of success.
- Field called "map matching": assume car is on road, snap to road
- Couple of approaches, most common is heuristic

**NOTE:** Skip the next few slides and just talk if you're running short on
time here.

- Start with "best guess" for previous position
- Write a bunch of rules which score road segments in the map as "likely" or
  "unlikely" based on previous position and new data
- Pick best segment and snap to it
- Good performance; fuzzy logic paper reported 99.2% accuracy on data set of
  several kilometers
- Has a few problems:
  1. Hard to come up with useful rules; less complicated algorithms get anywhere
     between 70% and 90% segment classification accuracy. Would like more
     principled approach
  2. Can have problems with mismatches, especially if it mismatches the initial
     location, since it might rule out matching to roads not adjacent to the
     first one during subsequent steps.

- Fix this using probability distribution over positions rather than just one
  "best guess"
- Figure on screen is of Gaussian mixture model. Shows how some regions have
  high probability initially and some low, and this narrows down over time until
  you get the right location.
- Common approach is particle filtering, which I will explain soon
- Particle filtering is flexible and fast, but not many people using it
- Ones who were using particle filtering also used emaps, augmented GPS, etc.

## Project goals

- For this project, I wanted to produce a reliable localisation system, but also
  wanted to investigate how particle filters could be applied to localisation in
  a more practical way, without the onerous requirements of other research.

## Particle filters

- Idea if that we have a large number of "particles" which represent possible
  vehicle states. Include position, heading, etc.
- Start out with particles spread around the environment in some reasonable
  pattern
- When we take an action (wheels say we've moved), move the particles
- Add weights to particles representing how likely a particle is to be the state
  which generated an observation
- Focus on high-weight particles, since that's where the vehicle is likely to be

- Particles are actually distributed according to distribution on screen
- Aim of each step of particle filtering is to take particles which are
  distributed according to that distribution at time $t$, and produce a new step
  of particles sampled from the distribution at time $t + 1$

- Graphical example:
  1. Start with particles initialises around where the robot probably is
  2. Robot moves, like taking action
  3. Move particles according to transition distribution (stratified sampling).
     Accounts for movement sensor noise (odom, gyro, etc.)
  4. Get an observation (GPS-like), represent particle likelihood using
     Gaussian. Weights are given by Gaussian.
  5. Resample according to weights. Will trim off low weight particles and
     duplicate high-weight ones.

## Incorporating map data

- We just use function of distance to nearest lane in the road map
- Very fast to compute; put all the lanes in a k-d tree and find the distance to
  the nearest one.
- Specific form here still results in acceptable behaviour when mixed with
  Gaussian GPS pseudo-likelihoods
- Only a *pseudo*-likelihood; believing that there is a likelihood function like
  this over the road network is probabilistically flawed.
- Form is Cauchy-like

## Demonstration

- Both filters are fed gyroscope data, forward speed data and positioning data.
  All three of these have noise, and all three are likely to be found in a real
  localisation setup.
- Positioning data is not GPS-like, since I couldn't find any data sets with
  both labelled ground truth and noisy GPS information. Instead, it's white,
  Gaussian noise.
- Slightly ridiculous setup, but does a good job of illustrating what the map
  likelihood measurements are actually doing.
- Jumping is to be expected, since we're calculating the most likely position
  at a given time, rather than a smooth trajectory over past positions.
- For performance reasons, I'm only resampling once the weights become
  sufficiently imbalanced.
- Maps result in significant decrease in lateral movement of particles due to
  incorrect GPS fixes.
- Source code available on GitHub

## Challenges

- If we don't know how fast the wheels are moving, we need to add extra
  dimensions to state representation to figure out how our transitions should
  work.
- I'm adding velocity, and updating it using some simple Gaussian noise added at
  each step, since that's what I found that the transition noise looked like in
  the actual data set.
- Other approaches to particle filtering for incorporating map information
  associated each particle with a road in the map, which potentially allowed
  them to use an update equation which reflects our intuitive understanding of
  where a car is likely to move from a given position on a road. This is more
  expensive, but could improve performance on corner cases like L-bends, where
  particles tend to disappear easily.
- Sometimes the particle distribution becomes bimodal, which causes the
  expectation formula used to output a nonsensical result (estimate in a region
  of zero or near-zero probability mass). Not sure how to fix this in a
  probabilistically reasonable way.

## Likely questions

**Q:** Is your use of GPS and map likelihoods as independent multiplicative
factors justified?

**A:** Absolutely. If you assume independence of the map likelihood and the GPS
likelihood given the true state---which is totally reasonable---then just
multiplying the two likelihoods together works fine.

**Q:** Are particle filters suitable for map-aided localisation, in your view?
This is an important question, since finding the answer was one of the goals of
your research.

**A:** There's enough evidence to indicate that particle filtering is a viable
approach to map-based localisation. However, the approach which I took---namely,
attempting to track the "true" position of the vehicle (rather than clamping the
vehicle's position to the road)---is not, in my view, a very good approach,
since it results in the particles being decimated at bends in the road.
Intuitively, we would prefer the particles to continue along the same road,
which they would do if we clamped each particle to a specific segment.

**Q:** Did you succeed in your second goal of producing a localisation algorithm
which is robust to noise? Robust compared to what?

**A:** Yes, the resultant algorithm is reasonably robust compared to both the
plain particle filter and the raw GPS fixes. Having additional map matching
algorithms for comparison would be nice, but I ran out of time to implement
these.

**Q:** How do self-driving cars (e.g. Junior) localise?

**A:** Post-Urban Grand Challenge, Junior was localising using custom infrared
maps of the ground plane, combined with a histogram filter (grid-based
localisation). This achieved around 10cm accuracy, but required a vehicle with
the appropriate infrared sensors to cove the route beforehand (not to mention
much more processing!). For the challenge itself, they used road reflectivity
maps and detection of curb-like obstacles plugged into a 1D (road-lateral)
histogram filter to provide GPS/IMU corrections. Other systems (KIT and CMU
entries to DARPA Urban Grand Challenge) just used their expensive GPS/INS units
(AFAICT, not certain).
