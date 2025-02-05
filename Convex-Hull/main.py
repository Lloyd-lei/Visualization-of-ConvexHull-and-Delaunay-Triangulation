import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from convex_hull_api import DataCloud

def main():
    # read external file, skip first two rows
    file_path = "mesh.dat"
    data = pd.read_csv(file_path, sep='\s+', skiprows=1, header=None, names=["x", "y"])
    points = list(zip(data["x"], data["y"]))

    dc = DataCloud(points)
    steps_graham = dc.graham_scan(return_steps=True)
    steps_jarvis = dc.jarvis_march(return_steps=True)
    steps_quickhull = dc.quickhull(return_steps=True)
    steps_monotone = dc.monotone_chain(return_steps=True)

    steps_list = [
        ("Graham Scan", steps_graham),
        ("Jarvis March", steps_jarvis),
        ("QuickHull", steps_quickhull),
        ("Monotone Chain", steps_monotone)
    ]

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes = axes.flatten()

    lines = []  # stores all possible line nections for each algorithm
    for ax, (algo_name, algo_steps) in zip(axes, steps_list):
        # initial datacloud
        ax.scatter(*zip(*points), s=10, c='blue')
        
        # create a red line
        line, = ax.plot([], [], 'r-', linewidth=1.5)
        lines.append(line)

        ax.set_title(algo_name)
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        ax.grid(True)

        all_x = data["x"].values
        all_y = data["y"].values
        ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
        ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    # set up for the animation
    # take the max steps as the animation frame, quicker algorithms just stay the final status
    max_frames = max(len(s[1]) for s in steps_list)

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def update(frame):
        """frame update, from 0 to max_frames-1。"""
        for line, (algo_name, algo_steps) in zip(lines, steps_list):
            # if steps <= frame，continue
            idx = min(frame, len(algo_steps) - 1)
            hull_points = algo_steps[idx]

            # if closured, check head and tail in the stack
            if len(hull_points) > 1 and hull_points[0] != hull_points[-1]:
                hull_points = hull_points + [hull_points[0]]

            xdata = [p[0] for p in hull_points]
            ydata = [p[1] for p in hull_points]
            line.set_data(xdata, ydata)

        return lines

    # generate animation
    ani = animation.FuncAnimation(
        fig, update, frames=max_frames, init_func=init,
        interval=100,  # frame interval, /millesecond
        blit=True
    )

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
