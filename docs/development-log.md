# 开发日志

| 项目 | 内容 |
| --- | --- |
| 项目 | COD RoboMaster Balance Sim-to-Sim RL |
| 维护规则 | 每次开发结束后更新，记录事实、验证证据、失败原因和下一步。 |

## 2026-08-20 — 需求确认

### 已确认

- 第一版使用开源项目中现有机器人，验证成功后才制作自研机器人；
- 第一版只做一台机器人，但最终要实现该机器人强化学习工程的完整训练、导出和 sim-to-sim 验证能力；
- 目标行为为前进、后退、转向与跨台阶，速度误差和跌倒率需达到可接受范围；
- 代码与文档目标仓库为 `git@github.com:skylore-zroy/RL.git`；用户已授权旧内容清空并覆盖；
- 环境必须容器化，目标是支持的硬件拉取后即可运行，不反复手工安装依赖；
- 本机为 Lenovo R9000P 2023 / RTX 4060 Laptop 8 GB；服务器暂定 RTX 3090 24 GB，可按需增加资源；
- 需要正式《需求规格说明》和持续更新的《开发日志》。

### 更正

最初把 E 盘中的目标误认成 b2w/Isaac Gym 项目。该判断经用户截图和重新读取源目录后撤回，旧 b2w 代码、模型和文档不再作为项目基线。

## 2026-08-21 — 正确上游与模型确认

### 已完成

- 重新读取 `E:\RL\COD-2026RoboMaster-Balance-Simulation_File\COD-2026RoboMaster-Balance-Simulation_File`；
- 确认目标为辽宁科技大学 COD 战队 RM2026 串联腿闭链平衡机器人；
- 核对源提交 `089e35a97e4be832f293547d283eb6f62a22185f`；
- 确认作者提供原始 MJCF、Isaac Sim 5.0 USD、15 个 STL 和两张参考图；
- 确认上游只提供模型资产，没有 Isaac Gym/Isaac Lab 训练代码或训练策略；
- 删除错误制作的简化几何模型，改为直接使用作者原始网格和模型文件。

### 许可发现

上游目录未发现 LICENSE、COPYING 或 NOTICE。模型可以本地继续验证，但在公开 GitHub/容器镜像再分发前需要作者明确许可或许可证。

## 2026-08-21 — MuJoCo 自由基座与动力学对齐

### 已完成

- 保留作者固定 MJCF 作为原件，另建 `COD-2026RoboMaster-Balance-free.xml`；
- 增加 6 自由度底盘、地面、重力接触和初始关键帧；
- 从作者 USD 提取底盘质量、质心、主惯量和主轴方向，替换早期错误的网格惯量推算；
- 对齐 15 个刚体的质量、质心和惯量，以及 14 个树关节的阻尼；
- 保留 4 个闭链约束和 6 个主动执行器。

### 验证证据

- MuJoCo：`nq=21`、`nv=20`、`nu=6`、`nbody=16`、`neq=4`；
- USD 与 MJCF 总质量均为 19 kg，底盘质量 11 kg；
- 最大质量误差 `2.384e-08 kg`；
- 最大质心误差 `3.458e-09 m`；
- 最大惯量张量误差 `3.548e-08 kg·m²`；
- 最大关节阻尼误差 `1.490e-09`；
- 零控制 2 s 后底盘高度由 `0.4500 m` 变化为约 `0.2360 m`，出现 5 个接触点，证明底盘没有固定。

### 遗留参数

USD 的 14 个树关节没有有限上下限，Isaac 任务需采用作者 MJCF 限位。真实电机扭矩、速度、减速比、碰撞简化和轮地接触仍待硬件资料或标定。

## 2026-08-21 — Isaac Sim 5.0 本机环境检查

### 已完成

- 在 Windows 短路径 `D:\is5` 安装 Python 3.11 与官方 `isaacsim[all]==5.0.0`；
- 下载并安装官方 Kit、Kit SDK 和 Physics 扩展缓存；三份 wheel 均通过 NVIDIA 索引 SHA-256 校验；
- Isaac Sim 能加载完整扩展、识别 RTX 4060 Laptop 并到达应用就绪阶段；
- 使用英文短路径复测，排除中文项目路径导致崩溃；
- 延后 USD 打开复测后，程序仍在模型加载前崩溃，排除作者 USD 是直接原因。

### 失败证据与结论

- 日志中的致命位置为 `rtx.scenedb.plugin.dll` / `carb.scenerenderer-rtx.plugin.dll`；
- Warp 同时报告 CUDA 驱动入口/API 不支持；
- 本机只有 8 GB 显存和约 16 GB 内存，低于 Isaac Sim 5.0 官方最低 16 GB 显存和 32 GB 内存；
- 因此本机不作为 Isaac Sim 5.0 运行验收平台。静态 USD 检查与 MuJoCo 可继续在本机完成，真实 Isaac 验证转移到 3090 服务器。

## 2026-08-21 — 容器路线纠正与仓库清理

### 已完成

- 训练/Isaac 验证路线由错误的 Isaac Gym Preview 4 改为作者模型对应的 Isaac Sim 5.0 + Isaac Lab 2.2；
- Isaac Docker 基础镜像改为 NVIDIA 官方 `nvcr.io/nvidia/isaac-lab:2.2.0`；
- MuJoCo Docker 改为只复制 COD 自由基座 MJCF 与对应网格；
- Compose 建立 `isaac-validate` 与 `mujoco-validate` 两个服务；
- Isaac 验证脚本检查刚体、关节、闭链和质量，只在内存解除底盘固定并可运行物理；
- 删除旧 `src`、`third_party/isaacgym`、`docker/isaacgym`、b2w 查看器/渲染器、旧构建脚本和下载日志；
- 重写项目 README、需求规格、运行指南和模型说明。

### 当前状态

- MuJoCo 动力学与模型结构已经在本机通过；
- Isaac Sim 5.0 Docker 定义已完成，但尚未在目标 RTX 3090 Linux 服务器实际构建运行；
- 本机 MuJoCo Docker 构建已通过配置检查，但 Docker Hub 认证端点网络超时，基础镜像未拉取；同一模型已在独立 WSL 环境完成等价回归；
- 强化学习环境、奖励、PPO、地形课程和策略导出尚未开始；
- 公开推送模型资产受上游许可证缺失阻塞。

### 下一步

1. 在 RTX 3090 Linux 服务器构建 Isaac 镜像并生成模型运行报告；
2. 检查解除固定后的闭链稳定性、关节方向、接触和视觉是否与作者参考图一致；
3. 获取电机和传动参数；
4. 实现 Isaac Lab 训练环境和最小站立/平衡任务；
5. 逐步加入速度跟踪、转向、地形课程、策略导出和 MuJoCo 闭环评测。