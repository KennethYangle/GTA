# coding=utf-8

import numpy as np
from numpy.linalg import cholesky
import matplotlib.pyplot as plt

sampleNo = 5000
np.random.seed(10)

# 二维正态分布
mu = np.array([1, 5])
Sigma = np.array([[5, 0], [0, 3]])
s = np.random.multivariate_normal(mu, Sigma, sampleNo)
plt.plot()
# 注意绘制的是散点图，而不是直方图
plt.plot(s[:,0],s[:,1],'+')
plt.show()