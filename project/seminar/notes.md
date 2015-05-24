# Notes for COMP2550 presentation

## Intro slide

> Hi everyone! This semester, I've been working on a system for performing
> localisation in road vehicles---cars, trucks whatever.

## Localisation slide

> If you've ever gotten lost and pulled up a map on your phone to figure out
> where you are, then you've performed localisation. That's just a roboticist's
> way of saying that you figured out where you were. For pedestrians, this is a
> pretty easy problem; even if you didn't have your phone with you, you could
> probably have figured out where you were just by walking around for a while
> until you found a building you recognised or something like that. For
> machines, though, this is often a lot harder, because you need to know where
> you are with enough precision to, say, figure out which lane you're in (if
> you're a navigation system), or even to make sure you don't run off the edge
> of the road (if you're an autonomous vehicle), and you need to have this
> information constantly available and up-to-date.

## "Localisation is messy"

> So this is important, but surely it's a solved problem, right? I mean, we have
> GPS receivers everywhere, we have inertial measurement units which can figure
> out roughly where you are just by integrating your positional and angular
> acceleration over time, so we should be able to do this task really well.

> Well, we can do it well when we need to, but there are some things that still
> make it hard. For instance, GPS is not a panacea: this figure down here is
> from a paper about trying to classify the accuracy of GPS fixes. The to make
> that plot, the researchers grabbed a GPS receiver drove around a built-up area
> with it. So you can see the road network which they travelled along, and you
> can also see how the GPS fixes they got---the coloured dots---are way out in
> places. This is due to stuff like multipath interference, where GPS signals
> reflect off buildings. It's definitely not something you want to use if your
> system needs to have high accuracy.

## Using map data

> As you might have guessed by looking at the road network there, it turns out
> that there's a readily available source of data that we can use to correct
> inaccurate sensor data, and that's road maps! This is an especially promising
> approach now that we have things like the OpenStreetMap project, where you
> can download high accuracy street map data---and we'll see an example of that
> at the end of the presentation---for free.

## Past work

> The fact that you can use map data like this is something that researchers
> have known for a while, so there are already a bunch of algorithms out there
> to do what's called "map matching", where you take your GPS observations, your
> gyroscope data, whatever you have available, and you try to find a position on
> the road network which seems most likely given that data.

> The most common way of doing this is pretty hacky: you just write a whole
> bunch of heuristics to rule out unlikely roads in the map---call them road
> segments---and use that to figure out which road segment you're probably on.
> Then you take your GPS fix, and you pretend that your vehicle is on the part
> of that most likely road segment. This actually works pretty well---the
> authors in the paper I've listed there claimed that their algorithm correctly
> identified which road segment the vehicle was on 99% of the time---but there
> are a lot of common problems with these approaches. For example, a lot of
> these algorithms can really be messed up if they localise the vehicle on the
> wrong road, because they'll only let the vehicle move to adjacent roads in
> subsequent steps, and sometimes it takes a lot of steps to do that.

> Probabilistic approaches to map matching avoid that issue by reasoning about
> the vehicle's position as a probability distribution over possible locations,
> rather than just a single "best guess". Up on the slide there I have a diagram
> from a paper where they did that using something called a Gaussian mixture
> model, and you see that all of the positions on the road have an assigned
> probability---red is really high probability---and the vehicle manages to
> narrow down it's position over time. In fact, that image is from a computer
> vision paper, since they didn't even use GPS or IMUs---they just used a street
> map and a bunch of frames from a stereo video camera! So probabilistic
> approaches can be really robust, and they're also good at incorporating
> unusual data---like video frames, or street maps.

> One of the most common probabilistic approaches is called particle filtering.
> It's quite effective for a lot of tasks, and the basic idea is ridiculously
> simple, but when I was researching this area, I found that there weren't a lot
> of people using it, and the ones who were using it were also making use of all
> sorts of difficult-to-come-by information, like extremely high accuracy maps,
> GPS augmentation systems, and so on.

## Project goals

> So, for this project, I ended up with two goals: firstly, I wanted to build a
> localisation algorithm which, like map-matching algorithms, was robust to
> sensor noise. Secondly, though, I wanted to figure out why other people
> weren't using particle filters, and how particle filters could be adapted to
> work without all of these onerous requirements like "enhanced maps" and
> augmented GPS.

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
