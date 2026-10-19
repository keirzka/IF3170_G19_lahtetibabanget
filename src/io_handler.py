import json
from models import Package, Truck, State

# Loader + parser
def load_data_from_json(file_path : str) : 
    # Data input disimpan di dalam src/data
    with open('./data/' + file_path, 'r') as file:
        data = json.load(file)

    truck = Truck(**data["Truck"])
    packages = [Package(**p) for p in data["Package"]]

    state = State(truck=truck, packages=packages)

    return state

def state_to_json(state):
    t = state.truck
    return {
        "truck": {"width": t.width, "length": t.length, "height": t.height,
                  "max_capacity": t.max_capacity},
        "value": state.total_value,
        "weight": state.current_weight,
        "packages": [
            {
                "id": p.id, "width": p.width, "length": p.length, "height": p.height,
                "value": p.value, "weight": p.weight, "eta": p.eta,
                "is_fragile": p.is_fragile,
                "position": list(p.position) if p.position is not None else None,
                "orientation": list(p.orientation),
            }
            for p in state.packages
        ],
    }

def state_from_json(data):
    truck = Truck(**data["truck"])
    packages = []
    for d in data["packages"]:
        d = dict(d)
        pos = d.pop("position")
        ori = d.pop("orientation")
        packages.append(Package(**d,
                                position=tuple(pos) if pos is not None else None,
                                orientation=tuple(ori)))
    return State(truck, packages)
