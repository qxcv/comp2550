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

**TODO**

## Demonstration

**TODO**

## Challenges

**TODO**
