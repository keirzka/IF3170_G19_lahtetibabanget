# Pemakaian:
#     python generate_dataset.py --n 30 --seed 2026 

import argparse
import json
import os
import random

TRUCK = {"width": 10, "length": 20, "height": 5, "max_capacity": 500}


def build(n, seed):
    rng = random.Random(seed)
    packages = []
    for k in range(1, n + 1):
        w, l, h = rng.randint(1, 5), rng.randint(2, 8), rng.randint(1, 4)
        volume = w * l * h
        packages.append({
            "id": f"Pkg{k:02d}",
            "width": w, "length": l, "height": h,
            "value": max(10, round(volume * rng.uniform(3, 8))),
            "weight": max(1, round(volume * rng.uniform(0.3, 1.2))),
            "is_fragile": rng.random() < 0.2,
            "eta": rng.randint(1, 7),
        })
    return {"Package": packages, "Truck": dict(TRUCK)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    data = build(args.n, args.seed)
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   f"dataset_n{args.n}.json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2)

    pk = data["Package"]
    vol = sum(p["width"] * p["length"] * p["height"] for p in pk)
    wt = sum(p["weight"] for p in pk)
    print(f"{out}: {len(pk)} paket | volume {vol} (truk 1000) | berat {wt} (kapasitas 500) "
          f"| fragile {sum(p['is_fragile'] for p in pk)} | total value {sum(p['value'] for p in pk)}")


if __name__ == "__main__":
    main()