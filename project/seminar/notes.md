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

> So, I've been talking about particle filters a bit, but I haven't explained
> what they are! Intuitively, a particle filter represents the position of a
> vehicle using a whole bunch of "particles", each of which has a position, a
> heading, maybe even a velocity or an acceleration depending on the type of
> particle filter. These are actually samples from a probability distribution
> which we'll talk about later, but it might help to think of them as being like
> hypotheses for where the vehicle is. When the vehicle moves, and we get
> readings from the steering wheel and the speedometer, we can update the
> positions of the particles accordingly, and then we can introduce "weights"
> which tells us how much the particles' new positions agree with, say, laser
> scan data or GPS fixes. Finally, we can use a technique called resampling to
> make sure that we focus most of our effort on tracking high-weight particles,
> and ignore the less important ones.

> So here's an example of what this looks like for a robot which has an
> odometer, a map of its environment, and a bunch of sonar sensors which can
> tell it how far it is from walls.

> At first, we start out with all of our particles scattered throughout the map,
> since we really have no idea where we are.

> After we've moved for a while, a lot of the particles have ended up in weird
> places which don't reflect the data we're getting from our laser sensors, so
> we've replaced them with new particles that seem more reasonable. You
> can see that we've travelled forward a few metres and ended up a
> doorway---which our laser sensors will be able to tell us---and there are two
> locations where we could expect that to be the case: down here, where we might
> have gone from the right-hand side of the corridor down to the bottom edge,
> and up here, where we might have gone from the left-hand side to the top. The
> particle ends up keeping both of these "hypotheses", since it hasn't seen any
> strong evidence which would suggest that one is more likely that the other.

> Once we move forward a little more, though, we find ourselves in a long,
> narrow corridor, so we can throw away the other particles down in the bottom
> right of the map and we get our actual position.

## Particle filter details

## Incorporating map data

## Full setup

## Demonstration

## Conclusion
