import sys
from experiment_runner import (DEFAULT_SEEDS, input_name, log_group_statistics, output_dir_for,
                               run_experiment, setup_logger, write_summary)
from hill_climbing import random_restart, sideways_move, steepest_ascent, stochastic

VARIANTS = [
    ("Steepest Ascent Hill-Climbing", "steepest_ascent", steepest_ascent),
    ("Hill-Climbing with Sideways Move", "sideways_move", sideways_move),
    ("Stochastic Hill-Climbing", "stochastic", stochastic),
    ("Random Restart Hill-Climbing", "random_restart", random_restart),
]

def run_hc_experiment(file_name, seeds=DEFAULT_SEEDS):
    out_dir = output_dir_for("hc", file_name)
    logger = setup_logger(out_dir, f"hc_{input_name(file_name)}")
    all_rows = []
    for algorithm, variant, search_fn in VARIANTS:
        rows, _, _ = run_experiment(algorithm, variant, file_name, search_fn, seeds,
                                    algorithm_key="hc", logger=logger)
        all_rows.extend(rows)
    write_summary(out_dir, all_rows)
    log_group_statistics(logger, all_rows)
    logger.info(f"Output tersimpan di {out_dir}")
    return all_rows, out_dir

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else input("Masukkan nama file input (json) : ")
    run_hc_experiment(input_file)