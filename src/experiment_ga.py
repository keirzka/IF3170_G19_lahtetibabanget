# Pemakaian:
#     python experiment_ga.py data/dataset_n30.json [--seed 1000] [--elitism] [--runs 3]
import argparse
import csv
import json
import os

from genetic import genetic_algorithm
from models import Package, Truck
from io_handler import state_to_json

CONTROL_POPULATION = 50
ITERATION_VARIATIONS = [50, 100, 200]   # populasi dikontrol
CONTROL_ITERATION = 100
POPULATION_VARIATIONS = [20, 50, 100]   # iterasi dikontrol
MUTATION_RATE = 0.1

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "ga")


def load_input(path):
    with open(path) as f:
        data = json.load(f)
    truck = Truck(**data["Truck"])
    packages = [Package(**p) for p in data["Package"]]
    return truck, packages


def build_configs():
    configs = [("iterasi", CONTROL_POPULATION, it) for it in ITERATION_VARIATIONS]
    configs += [("populasi", pop, CONTROL_ITERATION) for pop in POPULATION_VARIATIONS]
    return configs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--seed", type=int, default=1000, help="seed dasar; run ke-k memakai seed+k")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--elitism", action="store_true")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    truck, packages = load_input(args.input)
    os.makedirs(args.out, exist_ok=True)

    rows = []
    counter = 0
    for group, pop, gens in build_configs():
        for run in range(1, args.runs + 1):
            seed = args.seed + counter
            counter += 1
            g, duration, init_s, best_s, best_v, history = genetic_algorithm(
                truck, packages, population_size=pop, generations=gens,
                mutation_rate=MUTATION_RATE, elitism=args.elitism, seed=seed)

            name = f"{group}_pop{pop}_gen{gens}_run{run}"
            record = {
                "name": name, "group": group, "run": run, "seed": seed,
                "population_size": pop, "generations": g,
                "mutation_rate": MUTATION_RATE, "elitism": args.elitism,
                "duration": duration,
                "initial_value": init_s.total_value, "final_value": best_v,
                "history": [list(h) for h in history],
                "initial_state": state_to_json(init_s),
                "final_state": state_to_json(best_s),
            }
            with open(os.path.join(args.out, name + ".json"), "w") as f:
                json.dump(record, f, indent=2)

            rows.append([name, group, pop, g, run, seed, round(duration, 3),
                         record["initial_value"], best_v])
            print(f"{name}: awal={record['initial_value']} akhir={best_v} ({duration:.1f}s)")

    with open(os.path.join(args.out, "summary.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "group", "population", "generations", "run", "seed",
                    "duration_s", "initial_value", "final_value"])
        w.writerows(rows)


if __name__ == "__main__":
    main()