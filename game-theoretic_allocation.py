import argparse
import json
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from ellipse import plot_ellopse

class Params:
    """
    docstring
    """
    def __init__(self, config):
        self.config = config
        self.random_seed = config["RandomSeed"]
        if self.random_seed >= 0:
            np.random.seed(self.random_seed)

        self.num_drone = len(config["Vehicles"])
        self.drones = list()
        for key, value in config["Vehicles"].items():
            self.drones.append(Drone(key, np.array(value.get("mu",[0.,0.,0.])), np.array(value.get("sigma",[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])), np.array(value.get("Capacity", [0.,0.,0.])) ))

        self.num_target = len(config["Targets"])
        self.targets = list()
        for key, value in config["Targets"].items():
            self.targets.append(Target(key, np.array(value.get("Position",[0.,0.,0.]))))

        self.num_mission = len(config["Missions"])
        self.missions = list()
        for key, value in config["Missions"].items():
            self.missions.append(Mission(key, value.get("Demand", 0)))

        if not self.check_validity():
            sys.exit(1)

    def check_validity(self):
        return True

class Drone:
    def __init__(self, name, mu, sigma, capacity):
        self.name = name
        self.mu = mu
        self.sigma = sigma
        self.position = np.random.multivariate_normal(self.mu, self.sigma)
        self.capacity = capacity
    def __str__(self):
        return "name: {}; position: {};".format(self.name, self.position)

class Target:
    def __init__(self, name, position):
        self.name = name
        self.position = position
    def __str__(self):
        return "name: {}; position: {};".format(self.name, self.position)

class Mission:
    def __init__(self, name, demand):
        self.name = name
        self.demand = demand
    def __str__(self):
        return "name: {}; demand: {};".format(self.name, self.demand)

class Theater:
    def __init__(self, params):
        self.params = params
        self.ax = plt.axes(projection='3d')
    def __str__(self):
        prt = "[drones]:\n"
        prt += "\n".join([d.__str__() for d in self.params.drones])
        prt += "\n[targets]:\n"
        prt += "\n".join([d.__str__() for d in self.params.targets])
        prt += "\n[missions]:\n"
        prt += "\n".join([d.__str__() for d in self.params.missions])
        return prt
    def render(self):
        for d in self.params.drones:
            plot_ellopse(self.ax, d.mu, d.sigma.diagonal(), d.position)
        for t in self.params.targets:
            self.ax.scatter(t.position[0], t.position[1], t.position[2], marker="*")
        
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        plt.show()

def main(args):
    # 读配置文件
    config_file = open(args.config_file)
    config = json.load(config_file)
    print(json.dumps(config, indent=4))
    # 生成舞台
    params = Params(config)
    theater = Theater(params)
    print(theater)
    # Game-Theoretic Allocation

    # 表演开始
    theater.render()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="config_file", default="./config.json")
    args = parser.parse_args()
    print(args)
    main(args)
