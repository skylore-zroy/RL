#!/usr/bin/env python3
"""Inspect and optionally simulate the author's COD USD in Isaac Sim 5.0.

All physics changes are session-only. The source USD is never saved.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

BASE_PATH = "/COD_2026_Balance_2_0/base_link"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("usd", type=Path)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--free-base",
        action="store_true",
        help="Disable the authored kinematic flag in memory; never saves the USD.",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run physics after inspection. With --free-base, add a small angular velocity.",
    )
    parser.add_argument("--updates", type=int, default=240)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--low-resource",
        action="store_true",
        help="Reduce viewport settings for local viewing; does not waive hardware requirements.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    usd_path = args.usd.resolve()
    if not usd_path.is_file():
        raise FileNotFoundError(usd_path)

    os.environ.setdefault("OMNI_KIT_ACCEPT_EULA", "YES")
    from isaacsim import SimulationApp

    launch_config: dict[str, object] = {
        "headless": args.headless,
        "multi_gpu": False,
        "active_gpu": 0,
        "max_gpu_count": 1,
        "create_new_stage": False,
    }
    if args.low_resource:
        launch_config.update(
            {
                "width": 960,
                "height": 540,
                "anti_aliasing": 0,
                "renderer": "RaytracedLighting",
            }
        )

    app = SimulationApp(launch_config)

    import omni.timeline
    import omni.usd
    from pxr import Gf, Usd, UsdPhysics

    context = omni.usd.get_context()
    if not context.open_stage(str(usd_path)):
        app.close()
        raise RuntimeError(f"Isaac Sim could not open {usd_path}")
    for _ in range(30):
        app.update()

    stage = context.get_stage()
    base = stage.GetPrimAtPath(BASE_PATH)
    if not base.IsValid():
        app.close()
        raise RuntimeError(f"Missing expected base prim: {BASE_PATH}")

    rigid_bodies: list[str] = []
    joints: list[str] = []
    closures: list[str] = []
    masses: list[float] = []
    for prim in stage.TraverseAll():
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            rigid_bodies.append(str(prim.GetPath()))
        if prim.IsA(UsdPhysics.Joint):
            joints.append(str(prim.GetPath()))
            if prim.GetAttribute("physics:excludeFromArticulation").Get():
                closures.append(str(prim.GetPath()))
        if prim.HasAPI(UsdPhysics.MassAPI):
            mass = UsdPhysics.MassAPI(prim).GetMassAttr().Get()
            if mass is not None:
                masses.append(float(mass))

    rigid_api = UsdPhysics.RigidBodyAPI(base)
    authored_kinematic = bool(rigid_api.GetKinematicEnabledAttr().Get())
    if args.free_base:
        rigid_api.GetKinematicEnabledAttr().Set(False)
        if args.simulate:
            rigid_api.GetAngularVelocityAttr().Set(Gf.Vec3f(0.0, 0.4, 0.0))

    report: dict[str, object] = {
        "usd": str(usd_path),
        "default_prim": str(stage.GetDefaultPrim().GetPath()),
        "rigid_bodies": len(rigid_bodies),
        "joints": len(joints),
        "closure_joints": len(closures),
        "total_mass_kg": sum(masses),
        "base_kinematic_authored": authored_kinematic,
        "base_kinematic_runtime": bool(rigid_api.GetKinematicEnabledAttr().Get()),
    }

    if (len(rigid_bodies), len(joints), len(closures)) != (15, 18, 4):
        app.close()
        raise AssertionError("Unexpected COD rigid-body or joint topology")
    if abs(sum(masses) - 19.0) > 1e-5:
        app.close()
        raise AssertionError("Unexpected COD total mass")
    if args.free_base and report["base_kinematic_runtime"]:
        app.close()
        raise AssertionError("Runtime base is still kinematic")

    if args.simulate:
        matrix_before = omni.usd.utils.get_world_transform_matrix(base, Usd.TimeCode.Default())
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        for _ in range(max(args.updates, 1)):
            app.update()
        current_time = timeline.get_current_time() * timeline.get_time_codes_per_seconds()
        matrix_after = omni.usd.utils.get_world_transform_matrix(base, current_time)
        timeline.stop()

        before = matrix_before.ExtractTranslation()
        after = matrix_after.ExtractTranslation()
        report["base_position_before_m"] = [float(value) for value in before]
        report["base_position_after_m"] = [float(value) for value in after]
        report["simulation_updates"] = max(args.updates, 1)

    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")

    if not args.headless:
        try:
            from isaacsim.core.utils.viewports import set_camera_view

            set_camera_view(
                eye=[1.15, 1.15, 0.75],
                target=[0.0, 0.0, 0.20],
                camera_prim_path="/OmniverseKit_Persp",
            )
        except Exception as error:
            print(f"camera_setup_warning={error}")
        while app.is_running():
            app.update()

    app.close()


if __name__ == "__main__":
    main()