import dataclasses
import json
import os

from models import Package, State, Truck

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

PACKAGE_FIELDS = {f.name for f in dataclasses.fields(Package)}


def resolve_input_path(file_path: str):
    if os.path.isfile(file_path):
        return file_path
    return os.path.join(DATA_DIR, os.path.basename(file_path))


def parse_trucks(data):
    raw = data.get("Trucks", data.get("Truck"))
    if raw is None:
        raise ValueError("input harus memiliki key 'Truck' atau 'Trucks'")
    if isinstance(raw, dict):
        raw = [raw]
    if not raw:
        raise ValueError("minimal harus ada satu truk")
    return [Truck(**t) for t in raw]


def load_data_from_json(file_path: str):
    with open(resolve_input_path(file_path), "r") as file:
        data = json.load(file)
    trucks = parse_trucks(data)
    packages = [Package(**p) for p in data["Package"]]
    return State(trucks, packages)


def state_to_json(state: State):
    return {
        "trucks": [dataclasses.asdict(t) for t in state.trucks],
        "value": state.total_value,
        "weight": state.current_weight,
        "packages": [
            {
                "id": p.id, "width": p.width, "length": p.length, "height": p.height,
                "value": p.value, "weight": p.weight, "eta": p.eta,
                "is_fragile": p.is_fragile,
                "position": list(p.position) if p.position is not None else None,
                "orientation": list(p.orientation),
                "truck_id": p.truck_id,
            }
            for p in state.packages
        ],
    }


def state_from_json(data):
    raw = data.get("trucks", data.get("truck"))
    if isinstance(raw, dict):
        raw = [raw]
    trucks = [Truck(**t) for t in raw]
    packages = []
    for d in data["packages"]:
        kwargs = {k: v for k, v in d.items() if k in PACKAGE_FIELDS}
        kwargs["position"] = tuple(d["position"]) if d.get("position") is not None else None
        kwargs["orientation"] = tuple(d.get("orientation", ("x", "y", "z")))
        packages.append(Package(**kwargs))
    return State(trucks, packages)