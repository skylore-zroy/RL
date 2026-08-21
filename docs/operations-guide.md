# 运行与交付指南

## 1. 当前可执行内容

当前版本完成的是作者模型核对、自由基座 MuJoCo 验证和 Isaac 服务器验证容器。强化学习任务与训练策略尚未完成。

## 2. 两套镜像

| 镜像 | 用途 | 建议运行位置 |
| --- | --- | --- |
| `cod-isaac-lab:2.2.0-local` | Isaac Sim 5.0 加载 USD、解除固定、运行物理检查；后续扩展为训练镜像 | RTX 3090 Linux 服务器 |
| `cod-mujoco:3.2.6-local` | 加载自由基座 MJCF、零控制重力检查；后续用于策略验证 | 本机 WSL 2 或 Linux 服务器 |

容器已经包含相应 Python 与仿真依赖。第一次构建/拉取需要下载基础镜像层；成功后 Docker 会复用缓存，日常运行不会重新配置环境。

## 3. MuJoCo 本机验证

在项目根目录执行：

```powershell
.\scripts\build-mujoco-image.ps1
docker compose --profile mujoco run --rm mujoco-validate
```

预期报告包含 `nq=21 nv=20 nu=6 nbody=16 neq=4`，并显示底盘在零控制重力下发生移动。

直接在已安装 MuJoCo 的 WSL 中打开：

```bash
python3 -m mujoco.viewer --mjcf=/mnt/d/Users/zroy/Documents/ChatGPT/强化学习/models/cod_balance/mjcf/COD-2026RoboMaster-Balance-free.xml
```

## 4. Isaac 服务器验证

服务器要求：Linux x86_64、NVIDIA 驱动、Docker Engine、NVIDIA Container Toolkit、至少 32 GB 系统内存。当前计划使用 RTX 3090 24 GB。

将仓库复制到服务器后执行：

```bash
bash scripts/validate-on-server.sh
```

验证脚本会：

1. 打开作者原始 USD；
2. 检查 15 个刚体、18 个关节、其中 4 个闭链关节和 19 kg 总质量；
3. 只在内存中把底盘 `kinematicEnabled` 改为 `false`；
4. 加入小角速度并运行物理，写出 `validation_results/isaac_model_report.json`；
5. 关闭时不保存 USD，因此作者文件不会被覆盖。

如果 NGC 首次拉取要求身份验证，按 NVIDIA NGC 页面使用账号/API Key 登录；凭据不得写入仓库。

## 5. Windows 本机查看边界

本机 `D:\is5` 已安装 Isaac Sim 5.0 Python 包和扩展缓存，但 RTX 4060 Laptop 8 GB、约 16 GB 内存低于官方最低配置。程序在 USD 打开前的 RTX 初始化阶段崩溃，所以不再把本机作为 Isaac 运行验收平台。

`open-cod-isaac.ps1` 仅保留为诊断入口：

```powershell
.\scripts\open-cod-isaac.ps1 -FreeBase
```

它不会修改源 USD。即使 Windows 本机可运行，服务器 Docker 仍然是独立、可移植的 Linux 环境，两者不冲突。

## 6. 下一阶段

服务器模型验证通过后，依次实现 Isaac Lab 环境、观测与动作、奖励函数、地形课程、PPO 训练和 TorchScript 导出，再接入 MuJoCo 闭环指标。没有策略文件前，不执行前进/后退/转向/台阶性能宣称。

## 7. 发布限制

作者模型仓库当前未发现许可证。公开提交模型资产或发布包含模型的镜像前，必须取得作者许可；否则采用构建时从上游固定提交获取并校验哈希的方式。