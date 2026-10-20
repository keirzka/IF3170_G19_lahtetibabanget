import json
import os
from io_handler import load_data_from_json, state_to_json
from hill_climbing import (
    steepest_ascent, 
    sideways_move, 
    stochastic, 
    random_restart
)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "hc")

def run_experiment():
    # 1. Masukkan nama file input data JSON uji coba
    file_name = input("Masukkan nama file input (json) : ")
    
    print(f"\nMemuat data dari file {file_name}...")
    initial_data = load_data_from_json(file_name)
    truck = initial_data.truck
    packages = initial_data.packages

    os.makedirs(OUT_DIR, exist_ok=True)

    # List varian algoritma yang ingin diuji
    algorithms = [
        ("Steepest Ascent Hill-Climbing", steepest_ascent),
        ("Sideways Move Hill-Climbing", sideways_move),
        ("Stochastic Hill-Climbing", stochastic),
        ("Random Restart Hill-Climbing", lambda t, p: random_restart(t, p, max_restart=5))
    ]

    print("\n" + "="*50)
    print("HASIL EKSPERIMEN 3D BIN PACKING (LOCAL SEARCH)")
    print("="*50)

    # 2. Jalankan eksperimen untuk setiap algoritma
    for name, algo_func in algorithms:
        print(f"\nHasil Algoritma {name}...")
        
        for run in range(1, 4):
            iterations, duration, init_state, final_state, final_value, history = algo_func(truck, packages)
            
            print(f"  [Run {run}]")
            print(f"  - Nilai Objektif Awal : {objective_score(init_state)}")
            print(f"  - Nilai Objektif Akhir: {final_value}")
            print(f"  - Total Iterasi       : {iterations}")
            print(f"  - Waktu Eksekusi      : {duration:.4f} detik")
            print(f"  - Utilitas Ruang      : {final_state.space_utilization:.2f}%")
            
            file_name_clean = name.replace(" ", "_").replace("-", "_").lower()
            run_name = f"{file_name_clean}_run{run}"
            
            record = {
                "algorithm": name,
                "name": run_name,
                "run": run,
                "duration": duration,
                "iterations": iterations,
                "initial_value": objective_score(init_state),
                "final_value": final_value,
                "history": history,
                "initial_state": state_to_json(init_state),
                "final_state": state_to_json(final_state),
            }

            # Dump JSON
            with open(os.path.join(OUT_DIR, run_name + ".json"), "w") as f:
                json.dump(record, f, indent=2)
                
        print("-" * 50)
        
    print(f"\nEksperimen selesai. Output tersimpan di folder: {OUT_DIR}")

def objective_score(state):
    from objective import objective
    return objective(state)

if __name__ == "__main__":
    run_experiment()