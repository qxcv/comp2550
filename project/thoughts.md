# Thoughts on map matching and its applications to computer vision

## The current state of map matching

I've just completed a [literature survey](../submitted/literature-survey.pdf) on
map matching techniques, so I'll try to summarise what I learnt from writing
that survey in a few bullet points:

* The most prominent map matching algorithms follow the same "three step"
  structure. First, they try to figure out the segment of the road network the
  vehicle is on by taking a few GPS fixes and finding the nearest road segment
  to these fixes. Then, they execute the following loop:

  1. Get the most recent GPS fix (in some cases this is first passed through an
     EKF) and project it onto the selected road segment, then output the
     coordinates of the projection.
  2. If, since the last time step, the vehicle has made a turn (as indicated by
     change in heading, or difference in heading relative to the orientation of
     the selected road segment) or approached a junction, then re-run the road
     segment selection routine to get a new segment for the next iteration.
     Otherwise, keep the old segment.

  The second part of the loop is where the complexity lies. At the moment, the
  best (plausible) reported results using an algorithm like this come from
  [Quddus et al.
  (2006)](http://www.tandfonline.com/doi/abs/10.1080/15472450600793560), who
  report 99.2% road segment selection accuracy on a nontrivial data set. Their
  algorithm used a complex fuzzy logic-based system to select links, which took
  into account GPS signal strength, vehicle heading, vehicle speed, link length,
  etc. However, there are other approaches mentioned (and benchmarked) in that
  paper which are much simpler, albeit with lower accuracy.
* There are also a few probabilistic map matching algorithms, although these
  don't seem to be as popular. The most common approach is the [particle
  filter](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=5290369&tag=1),
  but it's hard to find anyone using particle filters with low resolution maps
  like those from OpenStreetMap; rather, they tend to use highly detailed maps
  with known lane widths, road curvature, etc., at sub-metre accuracy. It's not
  clear that particle filters would still work well without these details. There
  are also a few other approaches probabilistic approaches to map matching, like
  the one outlined by [Brubaker et al.
  (2013)](http://www.cs.toronto.edu/~mbrubake/projects/CVPR13.pdf), but these
  are rare.
* Probabilistic algorithms have two advantages: firstly, they are capable of
  representing uncertainty in a vehicle's position, which is especially useful
  at Y-junctions and highway off-ramps where traditional map matching algorithms
  often select he incorrect fork. Secondly, some probabilistic algorithms are
  capable of functioning without GPS. Particle filters [can be
  used](http://ieeexplore.ieee.org/xpls/abs_all.jsp?arnumber=978396) in this
  way, as can the model proposed by Brubaker et al. However, probabilistic
  approaches seem less mature on the whole than simple heuristic approaches.

## Opportunities for improvement

My understanding (which may be incorrect) is that the initial goal of this
project was to improve the algorithm presented in ["Combining Priors,
Appearance, and Context for Road
Detection"](http://ieeexplore.ieee.org/xpl/articleDetails.jsp?reload=true&arnumber=6719504)
by improving localisation relative to the road. After looking into map matching
algorithms, I think that this is perfectly feasible, but with some caveats:

* It may be difficult to produce a meaningful road prior on multi-lane roads,
  since it's quite difficult to determine which lane a vehicle is in from
  positioning data alone. Most roads are bidirectional and have only two lanes,
  though, so this will not be a huge issue initially.
* Using a basic heuristic algorithm would likely improve performance over just
  using GPS fixes, although particle filtering or some other probabilistic
  method would be preferable as it would provide a meaningful vehicle position
  and heading distribution to sample from when constructing masks for the road
  prior. However, going the probabilistic route will be more challenging as most
  probabilistic algorithms seem to be designed for use with high accuracy maps
  or positioning systems, as mentioned in the previous section.
