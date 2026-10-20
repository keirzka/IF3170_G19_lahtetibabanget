import argparse
import os

from experiment_runner import (input_name, log_group_statistics, output_dir_for, save_record, setup_logger, summary_row, write_summary)
from genetic import genetic_algorithm
from io_handler import load_data_from_json
from objective import get_objective_mode, objective

CONTROL_POPULATION = 100
ITERATION_VARIATIONS = [100, 300, 500]
CONTROL_ITERATION = 300
POPULATION_VARIATIONS = [50, 100, 200]
MUTATION_RATE = 0.1
BASE_SEED = 1000


def build_configs():
    configs = [("iterasi", CONTROL_POPULATION, it) for it in ITERATION_VARIATIONS]
    configs += [("populasi", pop, CONTROL_ITERATION) for pop in POPULATION_VARIATIONS]
    return configs


def run_ga_experiment(file_name, runs=3, base_seed=BASE_SEED, elitism=False):
    data = load_data_from_json(file_name)
    out_dir = output_dir_for("ga", file_name)
    logger = setup_logger(out_dir, f"ga_{input_name(file_name)}")
    logger.info(f"Genetic Algorithm | input={os.path.basename(file_name)} | "
                f"{len(data.trucks)} truk | {len(data.packages)} paket | "
                f"mutation_rate={MUTATION_RATE} | elitism={elitism} | "
                f"objective={get_objective_mode()}")

    rows = []
    counter = 0
    for group, population, generations in build_configs():
        variant = f"{group}_pop{population}_gen{generations}"
        for run in range(1, runs + 1):
            seed = base_seed + counter
            counter += 1
            iterations, duration, initial_state, best_state, best_value, history = genetic_algorithm(
                data.trucks, data.packages, population_size=population,
                generations=generations, mutation_rate=MUTATION_RATE,
                elitism=elitism, seed=seed)

            record = {
                "algorithm": "Genetic Algorithm",
                "name": f"{variant}_run{run}",
                "variant": variant,
                "input_file": os.path.basename(file_name),
                "objective": get_objective_mode(),
                "group": group,
                "run": run,
                "seed": seed,
                "duration": duration,
                "iterations": iterations,
                "initial_value": max(0, objective(initial_state)),
                "final_value": best_value,
                "initial_total_value": initial_state.total_value,
                "final_total_value": best_state.total_value,
                "population_size": population,
                "generations": generations,
                "mutation_rate": MUTATION_RATE,
                "elitism": elitism,
                "history": [list(h) for h in history],
                "initial_state": initial_state,
                "final_state": best_state,
            }
            save_record(out_dir, record)
            rows.append(summary_row(record))
            logger.info(f"{record['name']}: awal={record['initial_value']} akhir={best_value} "
                        f"(total value {record['initial_total_value']} -> {record['final_total_value']}) "
                        f"durasi={duration:.3f}s")
    write_summary(out_dir, rows)
    log_group_statistics(logger, rows)
    logger.info(f"Output tersimpan di {out_dir}")
    return rows, out_dir

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("--seed", type=int, default=BASE_SEED)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--elitism", action="store_true")
    args = ap.parse_args()
    input_file = args.input or input("Masukkan nama file input (json) : ")
    run_ga_experiment(input_file, args.runs, args.seed, args.elitism)


if __name__ == "__main__":
    main()