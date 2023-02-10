from matplotlib import pyplot as plt
import numpy as np
import convex_hull as convex_hull
import random
import time

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


n_values_to_test = [10, 100, 1000, 10000, 100000, 500000, 1000000]


def newPoints(num_points):

    random.seed(time.time())

    ptlist = []
    unique_xvals = {}
    max_r = 0.98
    WIDTH = 1.0
    HEIGHT = 1.0

    while len(ptlist) < num_points:
        x = random.uniform(-1.0, 1.0)
        y = random.uniform(-1.0, 1.0)
        if x ** 2 + y ** 2 <= max_r ** 2:
            xval = WIDTH * x
            yval = HEIGHT * y
            if xval not in unique_xvals:
                ptlist.append(QPointF(xval, yval))
                unique_xvals[xval] = 1

    return ptlist


if __name__ == "__main__":
    test_results = {n_value: [] for n_value in n_values_to_test}

    for n_value in n_values_to_test:
        print(f"Testing with n = {n_value}")
        for i in range(5):
            # Generate random points
            print(f" Test {i + 1}")
            points = newPoints(n_value)
            points.sort(key=lambda p: p.x())
            t1 = time.time()
            solver = convex_hull.ConvexHullSolver()
            hull = solver.divide_conquer(points)  # Replace this function with your own
            t2 = time.time()

            elapsed_time = t2 - t1
            print(f"  Elapsed time: {elapsed_time:3.3f} seconds")
            test_results[n_value].append(elapsed_time)

    finalResults = {}
    for n_value, results in test_results.items():
        finalResults[n_value] = sum(results) / len(results)

    # Write test results to a file
    with open("convex_hull_benchmark_results.txt", "w") as f:
        for n_value in n_values_to_test:
            f.write(f"n = {n_value}\n")
            f.write(f"Average time: {finalResults[n_value]} seconds\n")
            f.write("\n")
    
    # x = np.arange()
    plt.plot(n_values_to_test, [finalResults[n_value] for n_value in n_values_to_test])
    plt.xscale("log", base=2)
    plt.xlabel("Number of points")
    plt.ylabel("Time elapsed")
    plt.show()