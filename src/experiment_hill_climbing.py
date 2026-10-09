from io_handler import load_data_from_json
from hill_climbing import (
    steepest_ascent, 
    sideways_move, 
    stochastic, 
    random_restart
)

def run_experiment():
    # 1. Masukkan nama file input data JSON uji coba
    file_name = input("Masukkan nama file input (json) : ")
    
    print(f"\nMemuat data dari file {file_name}...")
    initial_data = load_data_from_json(file_name)
    truck = initial_data.truck
    packages = initial_data.packages

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
        
        # Panggil fungsi algoritma (mengembalikan: iterations, duration, initial_state, final_state, final_value)
        iterations, duration, init_state, final_state, final_value = algo_func(truck, packages)
        
        # Tampilkan hasil metrik untuk keperluan laporan
        print(f"  - Nilai Objektif Awal : {objective_score(init_state)}") # Atau hitung total_value
        print(f"  - Nilai Objektif Akhir: {final_value}")
        print(f"  - Total Iterasi       : {iterations}")
        print(f"  - Waktu Eksekusi      : {duration:.4f} detik")
        print(f"  - Utilitas Ruang      : {final_state.space_utilization:.2f}%")
        print("-" * 50)

def objective_score(state):
    from objective import objective
    return objective(state)

if __name__ == "__main__":
    run_experiment()