#!/usr/bin/env python3
"""Extract authored physics data from the COD Isaac Sim USD asset.

The script intentionally records generic authored attributes in addition to
UsdPhysics schema values.  That keeps PhysX-specific data visible even when
the standalone USD runtime does not have NVIDIA's PhysX schema plugin.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pxr import Usd, UsdGeom, UsdPhysics


PHYSICS_TERMS = (
    "physics",
    "physx",
    "mass",
    "inertia",
    "joint",
    "drive",
    "limit",
    "damping",
    "stiffness",
    "velocity",
    "effort",
    "friction",
    "collision",
    "articulation",
)


def serialise(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "pathString"):
        return value.pathString
    if hasattr(value, "GetReal") and hasattr(value, "GetImaginary"):
        imaginary = value.GetImaginary()
        return [float(value.GetReal()), *(float(item) for item in imaginary)]
    if isinstance(value, dict):
        return {str(key): serialise(item) for key, item in value.items()}
    try:
        return [serialise(item) for item in value]
    except TypeError:
        return str(value)


def authored_value(attribute: Usd.Attribute) -> Any:
    if not attribute.HasAuthoredValueOpinion():
        return None
    try:
        return serialise(attribute.Get())
    except Exception as error:  # A missing schema plugin can reject typed reads.
        return {"read_error": str(error)}


def relation_targets(prim: Usd.Prim) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for relation in prim.GetRelationships():
        targets = [str(path) for path in relation.GetTargets()]
        if targets or relation.HasAuthoredTargets():
            result[relation.GetName()] = targets
    return result


def filtered_attributes(prim: Usd.Prim) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for attribute in prim.GetAttributes():
        name = attribute.GetName()
        lowered = name.lower()
        if attribute.HasAuthoredValueOpinion() and any(term in lowered for term in PHYSICS_TERMS):
            result[name] = authored_value(attribute)
    return result


def api_names(prim: Usd.Prim) -> list[str]:
    return sorted(str(name) for name in prim.GetAppliedSchemas())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("usd", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    stage = Usd.Stage.Open(str(args.usd))
    if stage is None:
        raise RuntimeError(f"Unable to open USD stage: {args.usd}")

    report: dict[str, Any] = {
        "source": str(args.usd.resolve()),
        "stage": {
            "default_prim": str(stage.GetDefaultPrim().GetPath()) if stage.GetDefaultPrim() else None,
            "up_axis": UsdGeom.GetStageUpAxis(stage),
            "meters_per_unit": UsdGeom.GetStageMetersPerUnit(stage),
            "time_codes_per_second": stage.GetTimeCodesPerSecond(),
            "frames_per_second": stage.GetFramesPerSecond(),
        },
        "prims": [],
    }

    for prim in stage.TraverseAll():
        attributes = filtered_attributes(prim)
        relations = relation_targets(prim)
        schemas = api_names(prim)
        type_name = prim.GetTypeName()
        is_physics_type = any(
            token in type_name.lower()
            for token in ("joint", "physics", "collision", "material")
        )
        is_physics_schema = any(
            any(term in schema.lower() for term in PHYSICS_TERMS)
            for schema in schemas
        )
        if not (attributes or relations or is_physics_type or is_physics_schema):
            continue

        entry: dict[str, Any] = {
            "path": str(prim.GetPath()),
            "name": prim.GetName(),
            "type": type_name,
            "applied_schemas": schemas,
            "attributes": attributes,
            "relationships": relations,
        }

        if prim.HasAPI(UsdPhysics.MassAPI):
            mass = UsdPhysics.MassAPI(prim)
            entry["mass_api"] = {
                "mass": serialise(mass.GetMassAttr().Get()),
                "center_of_mass": serialise(mass.GetCenterOfMassAttr().Get()),
                "diagonal_inertia": serialise(mass.GetDiagonalInertiaAttr().Get()),
                "principal_axes": serialise(mass.GetPrincipalAxesAttr().Get()),
                "density": serialise(mass.GetDensityAttr().Get()),
            }

        report["prims"].append(entry)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    joint_count = sum("joint" in item["type"].lower() for item in report["prims"])
    mass_count = sum("mass_api" in item for item in report["prims"])
    print(f"stage={report['stage']}")
    print(f"physics_prims={len(report['prims'])} joints={joint_count} mass_apis={mass_count}")
    print(f"report={args.output}")


if __name__ == "__main__":
    main()
