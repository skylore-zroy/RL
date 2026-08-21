# COD RoboMaster Balance Sim-to-Sim RL

本项目面向辽宁科技大学 COD 战队公开的 **RM2026 串联腿闭链平衡机器人**，使用作者同一套 USD/MJCF 资产建立强化学习与 sim-to-sim 验证工程。

当前阶段先验证作者现有机器人，不设计自研机器人。训练侧采用 **Isaac Sim 5.0 + Isaac Lab 2.2**，验证侧采用 **MuJoCo 3.2.6**；第一版目标行为为前进、后退、转向和跨台阶。

## 当前状态

- 已核对作者原始 USD、MJCF 和 15 个 STL 网格；
- 已建立自由基座 MuJoCo 版本，底盘不再固定；
- 已将 USD 中的质量、质心、惯量和关节阻尼对齐到 MuJoCo，总质量均为 19 kg；
- 已准备 Isaac Lab 2.2 / Isaac Sim 5.0 与 MuJoCo 两套 Docker；
- 本机 RTX 4060 Laptop（8 GB）低于 Isaac Sim 5.0 官方最低 16 GB 显存，Isaac 运行验证转移到 RTX 3090 服务器；
- 强化学习任务、策略和训练结果尚未实现，不能把当前模型检查误称为训练完成。

详细范围见 [需求规格说明](docs/requirements-specification.md)，操作步骤见 [运行与交付指南](docs/operations-guide.md)，每次开发记录见 [开发日志](docs/development-log.md)。

## 上游来源与许可提醒

模型来源：`GrassFanWang/COD-2026RoboMaster-Balance-Simulation_File`，核对提交 `089e35a97e4be832f293547d283eb6f62a22185f`。

截至 2026-08-21，上游仓库未发现 LICENSE/COPYING 文件。“仓库可公开访问”不自动等于允许再分发。模型资产在公开推送前必须获得作者许可或由作者补充明确许可证。