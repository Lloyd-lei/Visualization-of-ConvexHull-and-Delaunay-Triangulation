import os
import random
import time
import matplotlib.pyplot as plt
import numpy as np
from convex_hull_api import DataCloud

def generate_points(n, x_range=(0, 1), y_range=(0, 1), distribution='uniform', seed=0):
    random.seed(seed)
    points = []
    
    for _ in range(n):
        if distribution == 'uniform':
            x = random.uniform(x_range[0], x_range[1])
            y = random.uniform(y_range[0], y_range[1])
        elif distribution == 'gaussian':
            x = random.gauss(0, 1)
            y = random.gauss(0, 1)
        else:
            raise ValueError("Invalid distribution type. Choose 'uniform' or 'gaussian'.")
        
        points.append((x, y))
    
    return points

def measure_runtime(algo_func, points):
    dc = DataCloud(points)
    start = time.perf_counter()
    algo_func(dc)
    end = time.perf_counter()
    return end - start

def run_analysis(ns, x_range, y_range, distribution, seed=0):
    algorithms = {
        "Graham Scan": DataCloud.graham_scan,
        "Jarvis March": DataCloud.jarvis_march,
        "QuickHull": DataCloud.quickhull,
        "Monotone Chain": DataCloud.monotone_chain
    }
    
    runtime_results = {name: [] for name in algorithms.keys()}
    
    for n in ns:
        points = generate_points(n, x_range, y_range, distribution, seed=seed)
        
        for algo_name, algo_method in algorithms.items():
            elapsed = measure_runtime(algo_method, points)
            runtime_results[algo_name].append(elapsed)
    
    plt.figure(figsize=(8,6))
    for algo_name in algorithms.keys():
        plt.plot(ns, runtime_results[algo_name], marker='o', label=algo_name)
    
    plt.title(f"Runtime Comparison ({distribution} distribution, range {x_range}, {y_range})")
    plt.xlabel("Number of points (n)")
    plt.ylabel("Time (seconds)")
    plt.legend()
    plt.grid(True)
    
    output_dir = "runtime_results"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{distribution}_{x_range}_{y_range}_runtime.png".replace(" ", "").replace("(", "").replace(")", "")
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath)
    plt.show()

def run_distribution_analysis(n=50, x_range=(0, 1), y_range=(0, 1), distribution='uniform', seed=0):
    algorithms = {
        "Graham Scan": DataCloud.graham_scan,
        "Jarvis March": DataCloud.jarvis_march,
        "QuickHull": DataCloud.quickhull,
        "Monotone Chain": DataCloud.monotone_chain
    }
    
    runtime_data = {name: [] for name in algorithms.keys()}
    
    for _ in range(100):
        points = generate_points(n, x_range, y_range, distribution, seed=seed)
        for algo_name, algo_method in algorithms.items():
            elapsed = measure_runtime(algo_method, points)
            runtime_data[algo_name].append(elapsed)
    
    output_dir = "runtime_results"
    os.makedirs(output_dir, exist_ok=True)
    
    results = ""
    plt.figure(figsize=(12, 8))
    for i, (algo_name, runtimes) in enumerate(runtime_data.items()):
        min_time = min(runtimes)
        max_time = max(runtimes)
        mean_time = np.mean(runtimes)
        std_dev = np.std(runtimes)
        results += f"{algo_name}: Min: {min_time:.6f}s, Max: {max_time:.6f}s, Mean: {mean_time:.6f}s, Std Dev: {std_dev:.6f}s\n"
        
        plt.subplot(2, 2, i+1)
        plt.hist(runtimes, bins=15, alpha=0.75, edgecolor='black')
        plt.title(f"{algo_name} Runtime Distribution")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Frequency")
    
    plt.tight_layout()
    hist_filepath = os.path.join(output_dir, f"{distribution}_{x_range}_{y_range}_runtime_distribution.png")
    plt.savefig(hist_filepath)
    plt.show()
    
    text_filepath = os.path.join(output_dir, "runtime_analysis.txt")
    with open(text_filepath, "w") as f:
        f.write(results)

if __name__ == "__main__":
    ns = [10, 50, 100, 200, 400, 800, 1000]
    
    run_analysis(ns, (0, 1), (0, 1), 'uniform')  
    run_analysis(ns, (-5, 5), (-5, 5), 'uniform')  
    run_analysis(ns, (-1, 1), (-1, 1), 'gaussian')  
    
    run_distribution_analysis(n=50, x_range=(0, 1), y_range=(0, 1), distribution='uniform')
