#!/usr/bin/env python3

import sys

from itertools import cycle, islice

"""Scrape output of bench_times.sh to produce a nice LaTeX table"""


def sorted_values(dict):
    yield from (v for k, v in sorted(dict.items()))

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

    total_fixes = sum(fixes.values())
    print("% Total fixes: ", total_fixes)
    print("% Total time at 10Hz: ", total_fixes * 10)

    # Number of particles
    sc_iter = map(str, pcs)
    print("Particles &", " & ".join(sc_iter), r"\\")
    print(r'\hline')

    # Times
    map_aided_dict = {pc: 0 for pc in pcs}
    non_map_aided_dict = {pc: 0 for pc in pcs}
    for trajectory in traj_names:
        for pcount in pcs:
            map_aided_dict[pcount] += times[(trajectory, pcount, True)]
            non_map_aided_dict[pcount] += times[(trajectory, pcount, False)]

    format_str = "{:.2f}"
    map_aided_times = map(
        format_str.format, sorted_values(map_aided_dict)
    )
    non_map_aided_times = map(
        format_str.format, sorted_values(non_map_aided_dict)
    )

    print(
        "Map-aided time (s) &",
        " & ".join(map_aided_times),
        r"\\"
    )
    print(
        "Non-map-aided time (s) &",
        " & ".join(non_map_aided_times),
        r"\\"
    )
