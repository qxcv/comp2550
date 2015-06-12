#!/usr/bin/env python3

import sys

from itertools import cycle, islice

"""Scrape output of bench_times.sh to produce a nice LaTeX table"""

if __name__ == '__main__':
    current_traj = None
    current_particles = None
    is_map_aided = None
    # Maps trace -> num particles
    fixes = {}
    # Maps (trace, particles, map_aided?) -> runtime
    times = {}
    particle_counts = set()
    trajectories = set()

    for line in sys.stdin:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("# Attempting times for trajectory"):
            current_traj = int(stripped.split()[-1])
            trajectories.add(current_traj)
            assert 0 <= current_traj <= 10
        elif stripped.startswith("## With "):
            current_particles = int(stripped.split()[2])
            particle_counts.add(current_particles)
            assert current_particles > 0
        elif stripped.startswith("### Spawning "):
            ft = stripped.split()[2]
            assert ft == 'map' or ft == 'plain'
            is_map_aided = ft == 'map'
        elif stripped.startswith("Runtime: "):
            rt = float(stripped.split()[1])
            key = (current_traj, current_particles, is_map_aided)
            assert None not in key
            times[key] = rt
        elif stripped.startswith("Fixes: "):
            n = int(stripped.split()[1])
            if current_traj in fixes:
                assert fixes[current_traj] == n, n
            else:
                fixes[current_traj] = n
        else:
            raise Exception("Invalid line: '{}'".format(stripped))

    # Sweet! Now we just have to make our table :D
    traj_names = sorted(trajectories)
    pcs = sorted(particle_counts)

    # Trace number
    format_str = r"\multicolumn{{{}}}{{c}}{{{}}}"
    print(
        "Trace no. &", " & ".join(
            format_str.format(len(pcs), n) for n in traj_names
        ), r"\\"
    )

    # No. of samples
    print(
        "Samples &", " & ".join(
            format_str.format(len(pcs), fixes[t]) for t in traj_names
        ), r"\\"
    )

    # hline
    print(r'\hline', r"\\")

    # Number of particles
    sc_iter = map(str, islice(cycle(pcs), len(traj_names) * len(pcs)))
    print("Particles &", " & ".join(sc_iter), r"\\")

    # Times
    map_aided_times = []
    non_map_aided_times = []
    for trajectory in traj_names:
        for pcount in pcs:
            map_aided_times.append(times[(trajectory, pcount, True)])
            non_map_aided_times.append(times[(trajectory, pcount, False)])

    format_str = "{:.2f}"
    print(
        "Map-aided time (s) &",
        " & ".join(format_str.format(t) for t in map_aided_times),
        r"\\"
    )
    print(
        "Non-map-aided time (s) &",
        " & ".join(format_str.format(t) for t in non_map_aided_times),
        r"\\"
    )
