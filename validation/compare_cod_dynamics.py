#!/usr/bin/env python3
"""Compare COD rigid-body and damping data between USD report and MuJoCo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mujoco
import numpy as np


def quaternion_matrix(quaternion: np.ndarray) -> np.ndarray:
    w, x, y, z = quaternion / np.linalg.norm(quaternion)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ]
    )


def inertia_tensor(diagonal: np.ndarray, quaternion: np.ndarray) -> np.ndarray:
    rotation = quaternion_matrix(quaternion)
    return rotation @ np.diag(diagonal) @ rotation.T


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--usd-report", type=Path, required=True)
    parser.add_argument("--mjcf", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.usd_report.read_text(encoding="utf-8"))
    model = mujoco.MjModel.from_xml_path(str(args.mjcf.resolve()))

    mass_errors: list[float] = []
    com_errors: list[float] = []
    inertia_errors: list[float] = []
    damping_errors: list[float] = []
    body_count = 0
    joint_count = 0

    for prim in report["prims"]:
        mass_data = prim.get("mass_api")
        if mass_data:
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, prim["name"])
            if body_id < 0:
                raise AssertionError(f"USD body missing in MJCF: {prim['name']}")
            body_count += 1
            mass_errors.append(abs(float(mass_data["mass"]) - model.body_mass[body_id]))
            com_errors.append(
                float(
                    np.max(
                        np.abs(
                            np.asarray(mass_data["center_of_mass"], dtype=float)
                            - model.body_ipos[body_id]
                        )
                    )
                )
            )
            usd_inertia = inertia_tensor(
                np.asarray(mass_data["diagonal_inertia"], dtype=float),
                np.asarray(mass_data["principal_axes"], dtype=float),
            )
            mjcf_inertia = inertia_tensor(
                model.body_inertia[body_id], model.body_iquat[body_id]
            )
            inertia_errors.append(float(np.max(np.abs(usd_inertia - mjcf_inertia))))

        if prim["type"] == "PhysicsRevoluteJoint":
            attributes = prim["attributes"]
            if attributes.get("physics:excludeFromArticulation"):
                continue
            joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, prim["name"])
            if joint_id < 0:
                raise AssertionError(f"USD joint missing in MJCF: {prim['name']}")
            joint_count += 1
            dof_id = model.jnt_dofadr[joint_id]
            usd_damping = float(attributes["drive:angular:physics:damping"])
            damping_errors.append(abs(usd_damping - model.dof_damping[dof_id]))

    maximum_mass_error = max(mass_errors, default=0.0)
    maximum_com_error = max(com_errors, default=0.0)
    maximum_inertia_error = max(inertia_errors, default=0.0)
    maximum_damping_error = max(damping_errors, default=0.0)

    print(f"bodies_compared={body_count} joints_compared={joint_count}")
    print(f"usd_mass={sum(float(item['mass_api']['mass']) for item in report['prims'] if item.get('mass_api')):.6f}kg")
    print(f"mjcf_mass={model.body_mass.sum():.6f}kg")
    print(f"max_mass_error={maximum_mass_error:.3e}kg")
    print(f"max_com_error={maximum_com_error:.3e}m")
    print(f"max_inertia_tensor_error={maximum_inertia_error:.3e}kg*m^2")
    print(f"max_joint_damping_error={maximum_damping_error:.3e}")

    if body_count != 15 or joint_count != 14:
        raise AssertionError("Unexpected COD body or tree-joint count")
    if maximum_mass_error > 2e-6:
        raise AssertionError("Mass mismatch exceeds tolerance")
    if maximum_com_error > 2e-6:
        raise AssertionError("Center-of-mass mismatch exceeds tolerance")
    if maximum_inertia_error > 1e-6:
        raise AssertionError("Inertia tensor mismatch exceeds tolerance")
    if maximum_damping_error > 2e-6:
        raise AssertionError("Joint damping mismatch exceeds tolerance")


if __name__ == "__main__":
    main()
