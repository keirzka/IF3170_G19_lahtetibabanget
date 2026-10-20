import sys
from experiment_runner import DEFAULT_SEEDS, log_group_statistics, run_experiment, write_summary
from simulated_annealing import simulated_annealing

def sa_search(initial_state):
    result = simulated_annealing(initial_state)
    result.pop("temp_history", None)
    result.pop("last_state", None)
    result.pop("last_value", None)
    result.pop("stuck_iterations", None)
    result["prob_history"] = [round(p, 6) for p in result["prob_history"]]
    result["acceptance_rate_history"] = [round(a, 4) for a in result["acceptance_rate_history"]]
    params = result.pop("params")
    result["T0"] = params["T0"]
    result["temp_factor"] = params["temp_factor"]
    result["temp_length"] = params["temp_length"]
    result["init_prob"] = params["init_prob"]
    result["min_percent"] = params["min_percent"]
    return result

def run_sa_experiment(file_name, seeds=DEFAULT_SEEDS):
    rows, out_dir, logger = run_experiment("Simulated Annealing", "sa", file_name, sa_search, seeds, algorithm_key="sa")
    write_summary(out_dir, rows)
    log_group_statistics(logger, rows)
    logger.info(f"Output tersimpan di {out_dir}")
    return rows, out_dir

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else input("Masukkan nama file input (json) : ")
    run_sa_experiment(input_file)