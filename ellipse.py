# -*- coding: utf-8 -*-
'''椭球面'''
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

def plot_ellopse(ax, centre, axises, position):
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x = centre[0] + axises[0] * np.outer(np.cos(u), np.sin(v))
    y = centre[1] + axises[1] * np.outer(np.sin(u), np.sin(v))
    z = centre[2] + axises[2] * np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_surface(x, y, z, alpha=0.5)
    ax.scatter(position[0], position[1], position[2])


if __name__ == "__main__":
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    plot_ellopse(ax, [0,0,0], [4,3,1], [1,0,0])
    plot_ellopse(ax, [10,5,5], [2,6,3], [8,5,5])

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()