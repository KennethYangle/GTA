可视化程序需要指定配置文件路径，默认为`./config.json`
## SimMode
包括`NetGun`和`Clash`两种模式.
* `NetGun`: 无人机发射网炮拦截目标，损耗率为`LossProbability`，成功率为`SuccessRate`;
* `Clash`: 无人机撞击目标，损耗率为100%，成功率为`SuccessRate`.

`MinEnergy`表示执行任务时最少保留的能量，缺省为0.

## Vehicles
每个无人机有自己的属性
* `Position`: 初始位置;
* `Energy`: 初始能量.

## IntrudeTactics
`IntrudeMode`为敌人入侵的行为，包括
* "各自为战": `Respective`，按照下面各入侵者配置运作;
* "同一目标": `Assemble`，敌人攻击同一目标，目标位置为`AssemblyPoint`，速度都指向目标，速度大小`Velocity`若指定则一致;
* "平行推进": `Parallel`，敌人沿同一方向`Direction`行进，速度大小`Velocity`若指定则一致，否则按照各自属性.

## Intruders
只有"各自为战"会参考运动模式，否则均沿直线运动。每个任务的属性包括
* `Position`: 初始位置;
* `MotionModel`: 运动模式，可取值["Linear", "RandomWalk", "WayPoint"];
* `MotionParams`: 运动参数，对应关系见`Motions`;
* `Velocity`: 运动速度;
* `Importance`: 重要度;
* `EntryTime`: 进入场景时间，默认为0.

## Motions
运动模式的相关属性
#### 1. `Linear`沿直线运动
* `Direction`: 速度方向，程序里会转换为单位向量.
#### 2. `RandomWalk`随机游走
* `Step`: 步长。在半径为步长的圆上生成下一个点.
#### 3. `WayPoint`路径点
* `WPs`: 二维列表，表示依次经过的路径点.

## Visualizer
可视化相关的一些参数
* `ImportanceScale`: 重要性在图上表示为圆的大小，该参数为比例系数