from dataclasses import dataclass
from typing import List, Optional, Tuple
import copy

AXIS = ('x', 'y', 'z')

SWAP_AXIS = {'x': {'y': 'z', 'z': 'y'},
             'y': {'x': 'z', 'z': 'x'},
             'z': {'x': 'y', 'y': 'x'}}

@dataclass
class Package:
    id: str
    width: int
    length: int
    height: int
    value: int
    weight: int
    eta: int
    is_fragile: bool

    position: Optional[Tuple[int, int, int]] = None
    orientation: Tuple[str, str, str] = AXIS
    truck_id: int = 0

    @property
    def dimension(self):
        sizes = (self.width, self.length, self.height)
        dx = sizes[self.orientation.index('x')]
        dy = sizes[self.orientation.index('y')]
        dz = sizes[self.orientation.index('z')]
        return dx, dy, dz

    @property
    def volume(self):
        return self.length * self.width * self.height

    @property
    def is_placed(self):
        return self.position is not None

    def rotate(self, axis: str):
        swap = SWAP_AXIS[axis.lower()]
        self.orientation = tuple(swap.get(a, a) for a in self.orientation)

    def copy(self):
        return copy.deepcopy(self)


@dataclass
class Truck:
    width: int
    length: int
    height: int
    max_capacity: int

    @property
    def volume(self):
        return self.length * self.width * self.height

@dataclass
class State:
    trucks: List[Truck]
    packages: List[Package]

    @property
    def truck(self):
        return self.trucks[0]

    @property
    def placed_packages(self):
        return [p for p in self.packages if p.is_placed]

    def packages_in(self, truck_id: int):
        return [p for p in self.packages if p.is_placed and p.truck_id == truck_id]

    def weight_in(self, truck_id: int):
        return sum(p.weight for p in self.packages_in(truck_id))

    def value_in(self, truck_id: int):
        return sum(p.value for p in self.packages_in(truck_id))

    def remaining_weight_in(self, truck_id: int):
        return self.trucks[truck_id].max_capacity - self.weight_in(truck_id)

    @property
    def total_value(self):
        return sum(p.value for p in self.placed_packages)

    @property
    def current_weight(self):
        return sum(p.weight for p in self.placed_packages)

    @property
    def total_capacity(self):
        return sum(t.max_capacity for t in self.trucks)

    @property
    def remaining_weight(self):
        return self.total_capacity - self.current_weight

    @property
    def current_volume(self):
        return sum(p.volume for p in self.placed_packages)

    @property
    def total_volume(self):
        return sum(t.volume for t in self.trucks)

    @property
    def space_utilization(self):
        if self.total_volume == 0:
            return 0
        return self.current_volume / self.total_volume * 100

    def get_package_by_id(self, package_id: str):
        for p in self.packages:
            if p.id == package_id:
                return p
        return None