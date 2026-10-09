from models import State, Truck, Package, AXIS
from validator import is_valid
from neighbor import drop_z
from typing import List
import random

def generate(truck : Truck, packages : List[Package], limit : int = 100) : 
    for i in range(limit) :
        packages_copy = [p.copy() for p in packages]

        for p in packages_copy : 
            # Random paket yg masuk dan di luar
            package_inside = random.choice([True, False])

            if(package_inside) : 
                # Rotasi paket secara random sejauh kelipatan 90 derajat
                num_rotation = random.randint(0,3)

                for j in range(num_rotation) : 
                    p.rotate(random.choice(AXIS))

                w, l, h = p.dimension

                if(w <= truck.width and l <= truck.length and h <= truck.height) : # Ukuran paket yang masih muat di truk dimasukkan ke truk

                    # Posisikan paket secara random
                    max_x = truck.width - w
                    max_y = truck.length - l
                    
                    x = random.randint(0, max_x)
                    y = random.randint(0, max_y)
                    z = drop_z(State(truck, packages_copy), i, x, y, w, l)

                    # Pastikan tidak melebihi tinggi truk
                    if(z + h < truck.height) :
                        p.position = (x, y, z)

                    else : 
                        p.position = None

                else : # Ukuran paket sudah tidak muat, ditaro di luar
                    p.position = None


        # Buat objek state
        state = State(truck, packages_copy)

        # Pastikan penempatan paket valid
        if (is_valid(state)) :  return state


    # Tidak ada paket yang berhasil dimasukkan ke truck
    packages_outside = [p.copy() for p in packages]

    for p in packages_outside : 
        p.position = None

    return State(truck, packages_outside)
