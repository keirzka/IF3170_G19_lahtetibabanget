import sys
from experiment_runner import run_experiment
from generator import generate
from io_handler import load_data_from_json
from simulated_annealing import simulated_annealing

SEEDS = [1, 2, 3]

def run_sa_experiment(file_name, n_runs=3, seeds=SEEDS, output_dir="../output"):
    data = load_data_from_json(file_name)
    def initial_state_factory():
        return generate(data.truck, data.packages)
    return run_experiment(
        name="SA",
        algorithm=simulated_annealing,
        initial_state_factory=initial_state_factory,
        n_runs=n_runs,
        output_dir=output_dir,
        seeds=seeds,
        config={"input_file": file_name},
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Masukkan nama file input (json) : ")
    run_sa_experiment(input_file)