# sumber heuristik drop_z dari Baker dkk. (1980) dan Karabulut & Inceoglu (2004)
import copy
import random
from models import State, AXIS
from validator import is_valid

MOVE_NAMES = ("swap", "move", "rotate")

def _clone(state):
    return State(state.truck, [copy.copy(p) for p in state.packages])

def _xy_overlap(ax, ay, aw, al, bx, by, bw, bl):
    return ax < bx + bw and bx < ax + aw and ay < by + bl and by < ay + al

def drop_z(state, idx, x, y, dx, dy):
    z = 0
    for j, other in enumerate(state.packages):
        if j == idx or not other.is_placed:
            continue
        ox, oy, oz = other.position
        ow, ol, oh = other.dimension
        if _xy_overlap(x, y, dx, dy, ox, oy, ow, ol):
            z = max(z, oz + oh)
    return z

def move_swap(state, rng=random):
    packages = state.packages
    inside = [i for i, p in enumerate(packages) if p.is_placed]
    if not inside or len(packages) < 2:
        return None
    i = rng.choice(inside)
    j = rng.randrange(len(packages) - 1)
    if j >= i:
        j += 1
    new_state = _clone(state)
    a, b = new_state.packages[i], new_state.packages[j]
    a.position, b.position = b.position, a.position
    return new_state

def move_relocate(state, rng=random):
    packages = state.packages
    if not packages:
        return None
    truck = state.truck
    i = rng.randrange(len(packages))
    pkg = packages[i]
    dx, dy, dz = pkg.dimension
    variants = ("take_out", "shift", "relocate") if pkg.is_placed else ("relocate",)
    variant = rng.choice(variants)
    if variant == "take_out":
        new_pos = None
    elif variant == "shift":
        x, y, _ = pkg.position
        delta = rng.choice((-1, 1))
        if rng.choice(("x", "y")) == "x":
            x += delta
        else:
            y += delta
        if x < 0 or y < 0 or x + dx > truck.width or y + dy > truck.length:
            return None
        new_pos = (x, y, drop_z(state, i, x, y, dx, dy))
    else:
        if dx > truck.width or dy > truck.length:
            return None
        x = rng.randint(0, truck.width - dx)
        y = rng.randint(0, truck.length - dy)
        new_pos = (x, y, drop_z(state, i, x, y, dx, dy))
    if new_pos is not None and new_pos[2] + dz > truck.height:
        return None
    if new_pos == pkg.position:
        return None
    new_state = _clone(state)
    new_state.packages[i].position = new_pos
    return new_state

def move_rotate(state, rng=random, axis=None):
    packages = state.packages
    if not packages:
        return None
    i = rng.randrange(len(packages))
    pkg = packages[i]
    rotated = copy.copy(pkg)
    rotated.rotate(axis or rng.choice(AXIS))
    if rotated.dimension == pkg.dimension:
        return None
    if pkg.is_placed:
        truck = state.truck
        x, y, _ = pkg.position
        dx, dy, dz = rotated.dimension
        if x + dx > truck.width or y + dy > truck.length:
            return None
        z = drop_z(state, i, x, y, dx, dy)
        if z + dz > truck.height:
            return None
        rotated.position = (x, y, z)
    new_state = _clone(state)
    new_state.packages[i] = rotated
    return new_state

MOVES = {"swap": move_swap, "move": move_relocate, "rotate": move_rotate}

def get_neighbor_with_info(state, rng=random, is_valid_fn=is_valid, max_tries=100):
    for _ in range(max_tries):
        name = rng.choice(MOVE_NAMES)
        candidate = MOVES[name](state, rng)
        if candidate is None:
            continue
        if is_valid_fn is None or is_valid_fn(candidate):
            return candidate, name
    return state, None

def get_neighbor(state, rng=random, is_valid_fn=is_valid, max_tries=100):
    return get_neighbor_with_info(state, rng, is_valid_fn, max_tries)[0]

def get_neighbor_sample(state, n, rng=random, is_valid_fn=is_valid):
    result = []
    for _ in range(n):
        candidate, name = get_neighbor_with_info(state, rng, is_valid_fn)
        if name is not None:
            result.append(candidate)
    return result