"""Load the COD free-base MJCF and run a zero-control sanity check."""

from __future__ import annotations

import argparse
from pathlib import Path

import mujoco


DEFAULT_MODEL = Path(
    "/workspace/models/cod_balance/mjcf/COD-2026RoboMaster-Balance-free.xml"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--duration", type=float, default=2.0)
    args = parser.parse_args()

    model = mujoco.MjModel.from_xml_path(str(args.model))
    data = mujoco.MjData(model)
    initial_z = float(data.qpos[2])

    steps = round(args.duration / model.opt.timestep)
    for _ in range(steps):
        data.ctrl[:] = 0.0
        mujoco.mj_step(model, data)

    print(f"model={model.names.split(bytes([0]), 1)[0].decode()}")
    print(
        f"nq={model.nq} nv={model.nv} nu={model.nu} "
        f"nbody={model.nbody} neq={model.neq}"
    )
    print(
        f"zero_control_duration={data.time:.3f}s "
        f"base_z={initial_z:.4f}->{float(data.qpos[2]):.4f} "
        f"contacts={data.ncon}"
    )

    if model.nq != 21 or model.nv != 20:
        raise RuntimeError("Expected a 7-qpos/6-DoF free base plus 14 original joints.")
    if abs(float(data.qpos[2]) - initial_z) < 0.01:
        raise RuntimeError("Base did not move under gravity; it may still be fixed.")


if __name__ == "__main__":
    main()
