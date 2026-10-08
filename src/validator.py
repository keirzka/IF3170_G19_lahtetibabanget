from models import Package, Truck, State
from typing import List

def is_valid(state : State) :
    # Valid : 
    # - Tidak melayang
    # - Tidak overlap
    # - Pecah belah tidak boleh sebagai support
    # - Tidak melebihi kapasitas berat truk
    # - Tidak melebihi batas dinnding truk

    # -----------------------------------------
    # Cek kapasitas total truk
    if (state.remaining_weight < 0) : return False

    placed_packages = [p for p in state.packages if p.position != None]

    for i, p in enumerate(placed_packages) : 
        # Cek batasan ruang truk
        if (not is_fit_in_truck(p, state.truck)) : return False

        # Cek paket melayang
        if (is_melayang(p, placed_packages)) : return False

        # Cek barang pecah belah sebagai support
        if (p.is_fragile and is_support(p, placed_packages)) : return False
    
        # Cek paket overlap
        for j, p2 in enumerate(placed_packages) : 
            if (i != j and is_overlap(p, p2)) : return False
    
    return True

def is_fit_in_truck(package : Package, truck : Truck):
    x, y, z = package.position
    w, l, h = package.dimension

    return (x >= 0 and x + w <= truck.width and
            y >= 0 and y + l <= truck.length and
            z >= 0 and z + h <= truck.height)

def is_melayang(package : Package, placed_packages : List) :
    x, y, z = package.position
    w, l, h = package.dimension

    # Di lantai truk
    if (z == 0) : return False

    for p in placed_packages : 
        # Skip paket saat ini
        if (p.id == package.id) : 
            continue

        px, py, pz = p.position
        pw, pl, ph = p.dimension

        # Cek paket yang tepat di bawah paket saat ini
        if (pz + ph == z) :
            bersisian_x = (x < px + pw) and (x + w > px)
            bersisian_y = (y < py + pl) and (y + l > py)

            if (bersisian_x and bersisian_y) : return False
    
    return True

def is_overlap(p1 : Package, p2 : Package) :
    x1, y1, z1 = p1.position
    w1, l1, h1 = p1.dimension
    
    x2, y2, z2 = p2.position
    w2, l2, h2 = p2.dimension

    overlap_x = (x1 < x2 + w2) and (x1 + w1 > x2)
    overlap_y = (y1 < y2 + l2) and (y1 + l1 > y2)
    overlap_z = (z1 < z2 + h2) and (z1 + h1 > z2)

    return overlap_x and overlap_y and overlap_z

def is_support(package : Package, placed_packages : List):
    x, y, z = package.position
    w, l, h = package.dimension
    
    topZ = z + h

    for p in placed_packages:
        if p.id == package.id:
            continue
            
        px, py, pz = p.position
        pw, pl, ph = p.dimension

        if (pz == topZ):
            bersisian_x = (x < px + pw) and (x + w > px)
            bersisian_y = (y < py + pl) and (y + l > py)

            if (bersisian_x and bersisian_y) : return True # Paket fragile ini menopang paket lain
                
    return False