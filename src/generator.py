import random
from typing import List, Union
from models import AXIS, Package, State, Truck
from neighbor import drop_z
from validator import is_valid

def _as_trucks(trucks: Union[Truck, List[Truck]]):
    return [trucks] if isinstance(trucks, Truck) else list(trucks)

def generate(trucks: Union[Truck, List[Truck]], packages: List[Package], limit: int = 100):
    trucks = _as_trucks(trucks)
    for _ in range(limit):
        packages_copy = [p.copy() for p in packages]

        for i, p in enumerate(packages_copy):
            p.position = None
            p.truck_id = 0

            if not random.choice([True, False]):
                continue

            for _ in range(random.randint(0, 3)):
                p.rotate(random.choice(AXIS))

            truck_id = 0 if len(trucks) == 1 else random.randrange(len(trucks))
            truck = trucks[truck_id]
            w, l, h = p.dimension

            if w > truck.width or l > truck.length or h > truck.height:
                continue

            x = random.randint(0, truck.width - w)
            y = random.randint(0, truck.length - l)
            z = drop_z(State(trucks, packages_copy), i, truck_id, x, y, w, l)

            if z + h <= truck.height:
                p.position = (x, y, z)
                p.truck_id = truck_id

        state = State(trucks, packages_copy)
        if is_valid(state):
            return state

    packages_outside = [p.copy() for p in packages]
    for p in packages_outside:
        p.position = None
        p.truck_id = 0
    return State(trucks, packages_outside)