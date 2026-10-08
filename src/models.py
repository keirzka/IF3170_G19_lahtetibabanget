from dataclasses import dataclass
from typing import List, Optional, Tuple
import copy

# Sumbu Koordinat Package
AXIS = ('x', 'y', 'z')

# Swap untuk rotasi terhadap sumbu tertentu
SWAP_AXIS = {'x': {'y': 'z', 'z': 'y'},
            'y': {'x': 'z', 'z': 'x'},
            'z': {'x': 'y', 'y': 'x'}}

@dataclass
class Package :
    id : str    # id paket
    width : int 
    length : int
    height : int
    value : int
    weight : int
    eta : int   # Estimate Time of Arrival
    is_fragile : bool  # benda pecah belah 

    position : Optional[Tuple[int, int, int]] = None # posisi paket saat ini berdasarkan titik sudut kiri-bawah-belakang (None : di luar truk)
    orientation : Tuple[str, str, str] = AXIS   # orientasi posisi paket terhadap ukuran posisinya pada w, l, h

    @property 
    def dimension(self) : # tuple ukuran paket sesuai dimensi pada sumbu x, y, z
        sizes = (self.width, self.length, self.height)

        dx = sizes[self.orientation.index('x')]
        dy = sizes[self.orientation.index('y')]
        dz = sizes[self.orientation.index('z')]

        return dx, dy, dz

    @property
    def volume(self) :
        return self.length * self.width * self.height

    @property
    def is_placed(self):
        return self.position != None

    def rotate(self, axis : str): # 1 kali rotate adalah untuk 90 derajat terhadap sumbu axis
       swap = SWAP_AXIS[axis.lower()]
       self.orientation = tuple(swap.get(a, a) for a in self.orientation)

    def copy(self) : 
        return copy.deepcopy(self)
    
@dataclass
class Truck : 
    width : int
    length : int
    height : int
    max_capacity : int
    
    @property
    def volume(self) :
        return self.length * self.width * self.height

@dataclass
class State : 
    truck : Truck
    packages : List[Package] 

    def __init__(self, truck : Truck, package : Package) : 
        self.truck = truck
        self.packages = package

    @property
    def total_value(self):
        return sum(pack.value for pack in self.packages if pack.is_placed)
    
    @property
    def current_weight(self): 
        return sum(pack.weight for pack in self.packages if pack.is_placed)

    @property
    def remaining_weight(self):
        return self.truck.max_capacity - self.current_weight

    @property
    def current_volume(self):
        return sum(pack.volume for pack in self.packages if pack.is_placed)

    @property
    def space_utilization(self) :
        if self.truck.volume == 0:
            return 0
        return (self.current_volume / self.truck.volume) * 100

    @property
    def placed_packages(self) :
        return [p for p in self.packages if p.is_placed]

    def get_package_by_id(self, idPackage : str) : 
        for pack in self.packages :
            if(pack.id == idPackage) : return pack
        return None
    
    def place_package(self, idPackage : str, position : Tuple[int, int, int]) :
        pack = self.get_package_by_id(idPackage)
        if (pack) : pack.position = position

    def unplace_package(self, idPackage : str) : 
        pack = self.get_package_by_id(idPackage)
        if (pack) : pack.position = None
