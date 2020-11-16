import argparse
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from new_recursive_hungarian import RHA2, gen_task_lists

class SimParams:
    def __init__(self, settings, sim_mode, loss_probability, success_rate, min_energy, arrive_threshold):
        self.settings = settings
        self.sim_mode = sim_mode
        self.loss_probability = loss_probability
        self.success_rate = success_rate
        self.min_energy = min_energy
        self.arrive_threshold = arrive_threshold


class Drone:
    def __init__(self, name, position, velocity, energy, sim_params):
        self.name = name
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.energy = energy
        self.sim_params = sim_params
        self.task_list = list()

        if sim_params.sim_mode == "Clash":
            sim_params.loss_probability = 1

    def __str__(self):
        return "name: {}; position: {}; energy: {}".format(self.name, self.position, self.energy)

    def update(self, interval, task_list, intruders_position):
        """
        function: 更新无人机状态，判断是否完成任务、是否毁坏
        :param interval: 一帧时间间隔
        :param task_list: 该飞机的任务列表
        :param intruders_position: 任务坐标
        :return: distroy_task: 完成的任务代号，没有为-1: int
        :return: is_sacrificed: 任务完成后自身是否损坏了，或者自身是不是没电了: bool
        :return: is_reallocate: 是否需要重规划: bool
        """
        self.task_list = task_list
        target = intruders_position[task_list[0]]
        direction = target - self.position
        direction /= np.linalg.norm(direction)
        displacement = interval * self.velocity * direction

        distroy_task, is_sacrificed, is_reallocate = -1, False, False
        if self.arrive_task(self.position, target, displacement):
            if np.random.uniform() < self.sim_params.success_rate:
                distroy_task = task_list[0]
                is_reallocate = True
                if np.random.uniform() < self.sim_params.loss_probability:
                    is_sacrificed = True
        self.position += displacement
        self.energy -= np.linalg.norm(displacement)
        if self.energy < self.sim_params.min_energy:
            is_sacrificed = True
            is_reallocate = True
        return distroy_task, is_sacrificed, is_reallocate

    def arrive_task(self, position, target, displacement):
        """判断是否到达任务点"""
        pt = target - position
        r = pt.dot(displacement) / displacement.dot(displacement)
        if r > 1 or r < 0:
            return False
        else:
            return True


class Intruder:
    def __init__(self, name, intrude_tactics, position, motion_model, motion, velocity, importance, entry_time=0):
        self.name = name
        self.intrude_tactics = intrude_tactics
        self.position = np.array(position, dtype=np.float64)
        self.motion_model = motion_model
        self.motion = motion
        self.velocity = velocity
        self.importance = importance
        self.entry_time = entry_time
        self.direction = np.array([0,0,0], dtype=np.float64)

        if self.intrude_tactics.intrude_mode == "Respective":
            if self.motion_model == "Linear":
                self.direction = self.motion.direction
            elif self.motion_model == "WPs":
                self.direction = self.motion.WPs[(self.motion.cnt_wp+1)%self.motion.num_wp] - self.motion.WPs[self.motion.cnt_wp]
                self.direction /= np.linalg.norm(self.direction)
        elif self.intrude_tactics.intrude_mode == "Assemble":
            if self.intrude_tactics.velocity > 0:
                self.velocity = self.intrude_tactics.velocity
            self.motion_model = "Linear"
            self.direction = self.intrude_tactics.assembly_point - self.position
            self.direction /= np.linalg.norm(self.direction)
        elif self.intrude_tactics.intrude_mode == "Parallel":
            if self.intrude_tactics.velocity > 0:
                self.velocity = self.intrude_tactics.velocity
            self.motion_model = "Linear"
            self.direction = self.intrude_tactics.direction
        else:
            raise TypeError("Invalid intrude mode: {}".format(self.intrude_tactics.intrude_mode))

    def __str__(self):
        return "name: {}, position: {}, motion_model: {}, motion: {}, velocity: {}, importance: {}, entry_time: {}".format(self.name, self.position, self.motion_model, self.motion.name, self.velocity, self.importance, self.entry_time)

    def update(self, interval):
        if self.motion_model == "Linear":
            self.position += interval * self.velocity * self.direction
        elif self.motion_model == "RandomWalk":
            self.position += interval * self.motion.step * np.random.uniform(-1, 1, 3)
        elif self.motion_model == "WayPoint":
            self.position += interval * self.velocity * self.direction
        else:
            raise TypeError("Invalid motion mode: {}".format(self.motion_model))


class IntrudeTactics:
    def __init__(self, intrude_mode, assembly_point, direction, velocity):
        if intrude_mode not in ["Respective", "Assemble", "Parallel"]:
            raise TypeError("Invalid intrude mode: {}".format(intrude_mode))
        self.intrude_mode = intrude_mode
        self.assembly_point = np.array(assembly_point, dtype=np.float64)
        self.direction = np.array(direction, dtype=np.float64) / np.linalg.norm(direction)
        self.velocity = velocity


class Motions:
    def __init__(self, name, direction=[1,0,0], step=0, WPs=[]):
        self.name = name
        self.direction = np.array(direction, dtype=np.float64) / np.linalg.norm(direction)
        self.step = step
        self.WPs = np.array(WPs, dtype=np.float64)
        self.num_wp = len(self.WPs)
        self.cnt_wp = 0


class Visualizer:
    def __init__(self, importance_scale, energy_scale):
        self.importance_scale = importance_scale
        self.energy_scale = energy_scale


class Theater:
    def __init__(self, drones, intruders, visualizer, sim_params, intrude_tactics, motions):
        self.num_drone = len(drones)
        self.num_intruder = len(intruders)
        self.drones = drones
        self.intruders = intruders
        self.task_lists = list()
        self.is_reallocate = True
        self.visualizer = visualizer
        self.sim_params = sim_params
        self.intrude_tactics = intrude_tactics
        self.motions = motions
        self.count = 0
        self.ax = plt.axes(projection='3d')
        self.is_finished = False

    def __str__(self):
        prt = "[drones]:\n"
        prt += "\n".join([d.__str__() for d in self.drones])
        prt += "\n[intruders]:\n"
        prt += "\n".join([d.__str__() for d in self.intruders])
        prt += "\n[task_lists]:\n"
        prt += self.task_lists.__str__()
        return prt

    def step(self, fps=10):
        """
        function: 每一帧调用该函数一次
        :param fps: 帧率
        :return: None
        """
        # 迭代时间
        start_time = time.time()
        self.interval = 1 / fps
        self.count += 1
        # 需要再分配时计算
        if self.is_reallocate:
            agent_pos = self.get_agent_pos()
            agent_energy = self.get_agent_energy()
            task_pos = self.get_task_pos()
            task_importance = self.get_task_importance()
            allocator = RHA2(agent_pos, agent_energy, task_pos, task_importance)
            uavs_pos_record = allocator.deal()
            self.task_lists = gen_task_lists(task_pos, uavs_pos_record)
            print("[task_lists]: {}".format(self.task_lists))
            self.is_reallocate = False
        # 更新敌我位置
        self.update()
        # 画图
        self.render()
        # 维持帧率
        sleep_time = start_time + self.interval - time.time()
        if sleep_time > 0 and not self.is_reallocate: plt.pause(sleep_time)

    def update(self):
        """
        function: 更新敌人位置和我方位置
        :return: None
        """
        # 是否有新目标
        pop_keys = []
        for key, value in self.sim_params.settings["Intruders"].items():
            if value["EntryTime"] <= self.count * self.interval:
                self.intruders.append(Intruder(key, self.intrude_tactics, value["Position"], value["MotionModel"], 
                    self.motions[value["MotionParams"]], value.get("Velocity", 0), value["Importance"], value["EntryTime"]))
                self.is_reallocate = True
                self.num_intruder += 1
                pop_keys.append(key)
        for k in pop_keys:
            self.sim_params.settings["Intruders"].pop(k)
        # 更新敌人位置
        for i in range(self.num_intruder):
            self.intruders[i].update(self.interval)
        # 更新我方位置
        del_task = list()
        del_drone = list()
        for i in range(self.num_drone):
            distroy_task, is_sacrificed, is_reallocate = self.drones[i].update(
                self.interval, self.task_lists[i], self.get_task_pos())
            if distroy_task >= 0:
                del_task.append(distroy_task)
                del self.task_lists[i][0]
                for t in self.task_lists[i]:
                    if t > distroy_task:
                        t -= 1
            if is_sacrificed:
                del_drone.append(i)
            if is_reallocate:
                self.is_reallocate = True
        if del_task:
            self.intruders = np.delete(self.intruders, del_task, axis=0)
            self.num_intruder = len(self.intruders)
            if self.num_intruder == 0:
                self.is_finished = True
                print("All intruders are intercepted!!!")
        if del_drone:
            self.drones = np.delete(self.drones, del_drone, axis=0)
            self.num_drone = len(self.drones)
            del self.task_lists[del_drone[0]]
            if self.num_drone == 0:
                self.is_finished = True
                if self.num_intruder == 0:
                    print("We won by a nose.")
                else:
                    print("Failure is also we need.")

    def render(self):
        """
        function: 画图
        :return: None
        """
        if self.is_reallocate or self.is_finished: return
        print(self)
        print("="*10)
        # 清楚上一帧，设置画布参数
        self.ax.cla()
        self.ax.set_xlim(-20, 110)
        self.ax.set_ylim(0, 100)
        self.ax.set_zlim(-10, 20)
        self.ax.set_xlabel('x', size=15)
        self.ax.set_ylabel('y', size=15)
        self.ax.set_zlabel('z', size=15)
        # 画task
        task_pos = self.get_task_pos()
        task_importance = self.get_task_importance()
        self.ax.scatter(task_pos[:,0], task_pos[:,1], task_pos[:,2], linewidths = self.visualizer.importance_scale * task_importance)
        # 画agent
        agent_pos = self.get_agent_pos()
        agent_energy = self.get_agent_energy()
        self.ax.scatter(agent_pos[:,0], agent_pos[:,1], agent_pos[:,2], linewidths = self.visualizer.energy_scale * agent_energy)
        # 画任务连线
        # self.ax.plot(agent_pos[:,0], agent_pos[:,1], agent_pos[:,2])
        plot_data = [[[] for j in range(self.num_drone)] for k in range(3)]
        for k in range(3):      # 第k个轴，第j个飞机，第i个数据
            for j in range(self.num_drone):
                plot_data[k][j].append(agent_pos[j][k])
                for i in range(len(self.task_lists[j])):
                    plot_data[k][j].append(task_pos[self.task_lists[j][i]][k])
        for j in range(self.num_drone):
            self.ax.plot(plot_data[0][j], plot_data[1][j], plot_data[2][j])


    def get_agent_pos(self):
        """
        function: 聚合我方位置信息，供RHA2使用
        :return: agent_pos: np.array()
        """
        agent_pos = []
        for i in range(self.num_drone):
            agent_pos.append(self.drones[i].position)
        return np.array(agent_pos)

    def get_agent_energy(self):
        """
        function: 聚合我方能量信息，供RHA2使用
        :return: agent_energy: np.array()
        """
        agent_energy = []
        for i in range(self.num_drone):
            agent_energy.append(self.drones[i].energy)
        return np.array(agent_energy)

    def get_task_pos(self):
        """
        function: 聚合敌方位置信息，供RHA2使用
        :return: task_pos: np.array()
        """
        task_pos = []
        for i in range(self.num_intruder):
            task_pos.append(self.intruders[i].position)
        return np.array(task_pos)

    def get_task_importance(self):
        """
        function: 聚合敌方重要度信息，供RHA2使用
        :return: task_importance: np.array()
        """
        task_importance = []
        for i in range(self.num_intruder):
            task_importance.append(self.intruders[i].importance)
        return np.array(task_importance)


def main(args):
    # 读配置文件
    config_file = open(args.config_file)
    config = json.load(config_file)
    print(json.dumps(config, indent=4))
    # 生成舞台
    sim_params = SimParams(config, config["SimMode"], config["LossProbability"], config["SuccessRate"], config["MinEnergy"], config["ArriveThreshold"])

    drones = list()
    for key, value in config["Vehicles"].items():
        drones.append(Drone(key, value["Position"], value["Velocity"], value["Energy"], sim_params))

    config_tactics = config["IntrudeTactics"]
    intrude_tactics = IntrudeTactics(config_tactics["IntrudeMode"], config_tactics.get("AssemblyPoint", [0,0,0]),
        config_tactics.get("Direction", [1,0,0]), config_tactics.get("Velocity", 0))

    motions = dict()
    for key, value in config["Motions"].items():
        motions[key] = Motions(key, value.get("Direction", [1,0,0]), value.get("Step", 0), value.get("WPs", []))

    intruders = list()
    pop_keys = []
    for key, value in config["Intruders"].items():
        if value.get("EntryTime", 0) <= 0:
            intruders.append(Intruder(key, intrude_tactics, value["Position"], value["MotionModel"], 
                motions[value["MotionParams"]], value.get("Velocity", 0), value["Importance"], value.get("EntryTime", 0)))
            pop_keys.append(key)
    for k in pop_keys:
        sim_params.settings["Intruders"].pop(k)
    
    visualizer = Visualizer(config["Visualizer"]["ImportanceScale"], config["Visualizer"]["EnergyScale"])
    theater = Theater(drones, intruders, visualizer, sim_params, intrude_tactics, motions)
    print(theater)
    # 表演开始
    while not theater.is_finished:
        theater.step()
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", dest="config_file", default="./config.json")
    args = parser.parse_args()
    print(args)
    main(args)
