import os
import random
from experiment_ga import run_ga_experiment
from experiment_hill_climbing import run_hc_experiment
from experiment_runner import OUTPUT_DIR, input_name
from experiment_sa import run_sa_experiment
from generator import generate
from io_handler import load_data_from_json
from objective import objective
from validator import is_valid
from visualisasi import draw_state, plot_algorithm_comparison, visualize_folder

MENU = """
Optimasi Pengisian Paket ke Truk (Local Search)
1. Tampilkan initial state acak
2. Eksperimen Hill-Climbing (4 varian x 3 run)
3. Eksperimen Simulated Annealing (3 run)
4. Eksperimen Genetic Algorithm (18 run)
5. Jalankan semua eksperimen + visualisasi
6. Buat visualisasi dan grafik perbandingan dari output yang ada
0. Keluar
"""

def show_initial_state(file_name):
    data = load_data_from_json(file_name)
    random.seed(1)
    state = generate(data.trucks, data.packages)
    print(f"Status valid         : {is_valid(state)}")
    print(f"Objective value      : {objective(state)}")
    print(f"Paket di dalam truk  : {len(state.placed_packages)} dari {len(state.packages)}")
    for t, truck in enumerate(state.trucks):
        print(f"Truk {t + 1}               : berat {state.weight_in(t)}/{truck.max_capacity}, "
              f"value {state.value_in(t)}")
    print(f"Utilisasi ruang      : {state.space_utilization:.2f}%")
    path = os.path.join(OUTPUT_DIR, f"initial_state_{input_name(file_name)}.png")
    print(f"Gambar               : {draw_state(state, 'Initial state acak (seed 1)', path)}")

def visualize_all(file_name):
    name = input_name(file_name)
    for algo in ("hc", "sa", "ga"):
        directory = os.path.join(OUTPUT_DIR, algo, name)
        if os.path.isdir(directory):
            print(f"Visualisasi {directory} ...")
            visualize_folder(directory)
    print(f"Grafik perbandingan  : {plot_algorithm_comparison(name)}")

def main():
    file_name = input("Masukkan nama file input (json) [dataset_n30.json] : ").strip() or "dataset_n30.json"
    actions = {
        "1": lambda: show_initial_state(file_name),
        "2": lambda: run_hc_experiment(file_name),
        "3": lambda: run_sa_experiment(file_name),
        "4": lambda: run_ga_experiment(file_name),
        "5": lambda: (run_hc_experiment(file_name), run_sa_experiment(file_name),
                      run_ga_experiment(file_name), visualize_all(file_name)),
        "6": lambda: visualize_all(file_name),
    }
    while True:
        choice = input(MENU + "Pilih menu: ").strip()
        if choice == "0":
            break
        if choice in actions:
            actions[choice]()
        else:
            print("Pilihan tidak dikenal.")

if __name__ == "__main__":
    main()