from typing import List
from models import Package, State, Truck

def is_valid(state: State):
    for p in state.placed_packages:
        if not 0 <= p.truck_id < len(state.trucks):
            return False

    for truck_id, truck in enumerate(state.trucks):
        placed = state.packages_in(truck_id)

        if sum(p.weight for p in placed) > truck.max_capacity:
            return False

        for i, p in enumerate(placed):
            if not is_fit_in_truck(p, truck):
                return False
            if is_melayang(p, placed):
                return False
            if p.is_fragile and is_support(p, placed):
                return False
            for p2 in placed[i + 1:]:
                if is_overlap(p, p2):
                    return False

    return True

def is_fit_in_truck(package: Package, truck: Truck):
    x, y, z = package.position
    w, l, h = package.dimension
    return (x >= 0 and x + w <= truck.width and
            y >= 0 and y + l <= truck.length and
            z >= 0 and z + h <= truck.height)

def is_melayang(package: Package, placed_packages: List[Package]):
    x, y, z = package.position
    w, l, h = package.dimension

    if z == 0:
        return False

    for p in placed_packages:
        if p is package:
            continue
        px, py, pz = p.position
        pw, pl, ph = p.dimension
        if pz + ph == z:
            bersisian_x = x < px + pw and x + w > px
            bersisian_y = y < py + pl and y + l > py
            if bersisian_x and bersisian_y:
                return False

    return True

def is_overlap(p1: Package, p2: Package):
    x1, y1, z1 = p1.position
    w1, l1, h1 = p1.dimension
    x2, y2, z2 = p2.position
    w2, l2, h2 = p2.dimension

    overlap_x = x1 < x2 + w2 and x1 + w1 > x2
    overlap_y = y1 < y2 + l2 and y1 + l1 > y2
    overlap_z = z1 < z2 + h2 and z1 + h1 > z2
    return overlap_x and overlap_y and overlap_z

def is_support(package: Package, placed_packages: List[Package]):
    x, y, z = package.position
    w, l, h = package.dimension
    top_z = z + h

    for p in placed_packages:
        if p is package:
            continue
        px, py, pz = p.position
        pw, pl, ph = p.dimension
        if pz == top_z:
            bersisian_x = x < px + pw and x + w > px
            bersisian_y = y < py + pl and y + l > py
            if bersisian_x and bersisian_y:
                return True

    return False