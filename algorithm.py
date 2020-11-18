import numpy as np
from itertools import permutations

class Algorithm:
    def __init__(self, params):
        self.params = params
        self.num_drone = params.num_drone
        self.drones = params.drones
        self.num_target = params.num_target
        self.targets = params.targets
        self.num_mission = params.num_mission
        self.missions = params.missions
        self.M = 150

    def payoff(self, u, p):
        ans = 0
        num_complete = self.num_drone - len(p)
        for i, v in enumerate(p):
            ans += u[i+num_complete][v]
        return ans

    def global_payoff(self, p):
        ans = 0
        for i, v in enumerate(p):
            t = v // self.num_mission
            m = v %  self.num_mission
            ans += (self.M - sum(abs(self.drones[i].position - self.targets[t].position))) * self.drones[i].capacity[m]
        return ans

    def static_GT(self):
        ans = list()
        print("[static_GT]:")
        # 每架飞机都要计算最优排列
        for d in range(self.num_drone):
            per = permutations([i for i in range(self.num_drone)], self.num_drone)
            # 计算单项收益
            u = np.zeros((self.num_drone, self.num_target*self.num_mission))
            for i in range(self.num_drone):
                for j in range(self.num_target*self.num_mission):
                    t = j // self.num_mission   # 目标编号
                    m = j %  self.num_mission   # 任务编号
                    if i == d:
                        u[i][j] = (self.M - sum(abs(self.drones[i].position - self.targets[t].position))) * self.drones[i].capacity[m]
                    else:
                        u[i][j] = (self.M - sum(abs(self.drones[i].mu - self.targets[t].position))) * self.drones[i].capacity[m]

            # 排列计算最优
            maxv = -1e10
            for p in per:
                val = self.payoff(u, p)
                if val > maxv:
                    maxv = val
                    maxp = p

            print("drone {} maxval is {}, maxp is {}".format(d, maxv, maxp))
            ans.append(maxp[d])

        gp = self.global_payoff(ans)
        print("global payoff: {}".format(gp))
        return ans

    def dynamic_GT(self):
        ans = list()
        print("[dynamic_GT]:")
        # 按编号顺序决策
        unexecuted_list = [i for i in range(self.num_drone)]
        for d in range(self.num_drone):
            per = permutations(unexecuted_list, len(unexecuted_list))
            # 计算单项收益
            u = np.zeros((self.num_drone, self.num_target*self.num_mission))
            for i in range(self.num_drone):
                for j in range(self.num_target*self.num_mission):
                    t = j // self.num_mission   # 目标编号
                    m = j %  self.num_mission   # 任务编号
                    if i == d:
                        u[i][j] = (self.M - sum(abs(self.drones[i].position - self.targets[t].position))) * self.drones[i].capacity[m]
                    else:
                        u[i][j] = (self.M - sum(abs(self.drones[i].mu - self.targets[t].position))) * self.drones[i].capacity[m]

            # 排列计算最优
            maxv = -1e10
            for p in per:
                val = self.payoff(u, p)
                if val > maxv:
                    maxv = val
                    maxp = p

            print("drone {} maxval is {}, maxp is {}".format(d, maxv, maxp))
            ans.append(maxp[0])
            unexecuted_list.remove(maxp[0])

        gp = self.global_payoff(ans)
        print("global payoff: {}".format(gp))
        return ans