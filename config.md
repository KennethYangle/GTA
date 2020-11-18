主程序需要指定配置文件路径，默认为`./config.json`

## RandomSeed
随机数种子.
指定int范围内的正数表示使用这个种子；指定负数表示随机生成种子，输出日志里会写有种子数值。

## Method
包括`0`和`1`两种模式. 分别表示`static_GT`和`dynamic_GT`方法
* `static_GT`: 静态博弈，所有智能体同时决策;
* `dynamic_GT`: 动态博弈，按照飞机编号依次博弈，后决策的飞机可以知道先决策飞机的选择.

## Vehicles
每个无人机有自己的属性
* `mu`: 卡尔曼滤波均值;
* `sigma`: 卡尔曼滤波方差矩阵;
* `Capacity`: 执行任务的能力，长度应与下面的`Missions`数量相同.

## Targets
可以设置多个目标
* `Position`: 位置向量.

## Missions
每个目标包含的任务。任务名应有明确的含义
* `Demand`: 该任务需求量;
* `Color`: 可视化时的颜色表示.
