# COD 2026 RoboMaster Balance 模型

来源：`GrassFanWang/COD-2026RoboMaster-Balance-Simulation_File`，核对提交 `089e35a97e4be832f293547d283eb6f62a22185f`。

## 文件说明

- `mjcf/COD-2026RoboMaster-Balance.xml`：作者原始 MJCF，底盘固定；
- `mjcf/COD-2026RoboMaster-Balance-free.xml`：本项目自由基座验证版本，增加自由关节、地面、重力接触和初始关键帧；
- `usd/COD-2026RoboMaster-Balance.usd`：作者原始 Isaac Sim 5.0 USD；
- 15 个 STL 和两张参考图均来自作者目录，几何未替换。

自由基座模型有 15 个刚体、14 个树关节、4 个闭链约束和 6 个执行器，MuJoCo 维度为 `nq=21`、`nv=20`、`nu=6`。原 USD 把 `base_link` 写成 `kinematicEnabled=true`；Isaac 检查脚本只在内存中改为 `false`，绝不保存覆盖作者文件。

## 动力学对齐

自由基座底盘数据直接取自作者 USD，而非网格推算：质量 11 kg，质心 `[-0.019917, -0.00040396, 0.021412] m`，主惯量 `[2.8640678, 2.8736324, 3.0472] kg·m²`。两套模型总质量均为 19 kg。

当前对齐了 15 个刚体的质量、质心与惯量，以及 14 个树关节的被动阻尼。USD 的树关节限位均未设置，Isaac 任务应显式采用 MJCF 限位；电机扭矩、速度上限和减速比仍需真实硬件资料确认。

## MuJoCo 打开方式

```bash
python3 -m mujoco.viewer --mjcf=models/cod_balance/mjcf/COD-2026RoboMaster-Balance-free.xml
```

零控制时自由基座会受重力作用，不能依靠世界固定保持站立。

## 许可边界

上游当前没有明确许可证文件。公开发布这些 USD/MJCF/STL/图片前，须获得作者书面许可或上游新增可再分发许可证。