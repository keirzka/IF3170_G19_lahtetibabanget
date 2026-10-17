
# Fungsi utama:
#   draw_state(state, ...)              -> truk 3D + paket di dalam, panel paket di luar, value state
#   plot_history(history, ...)          -> nilai objective terhadap iterasi
#                                          history = list angka        -> satu garis (HC / SA)
#                                          history = list (best, avg)  -> dua garis (GA)
#   visualize_run(record_json, ...)     -> state awal, state akhir, dan plot history satu run
#   plot_experiment_summary(records)    -> perbandingan nilai akhir dan durasi antar konfigurasi GA

# Pemakaian CLI:
#   python visualization.py demo                         # contoh dengan data buatan
#   python visualization.py run output/ga/<run>.json     # visualisasi satu run hasil experiment_ga.py
#   python visualization.py summary output/ga            # ringkasan seluruh run di satu folder

# Koordinat: x = lebar, y = panjang, z = tinggi

import argparse
import glob
import json
import os

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from state_serializer import state_from_dict

# palet 
ORANGE = "#E85D04"
ORANGE_LIGHT = "#FAA307"
ORANGE_PALE = "#FFE8CC"
ORANGE_DARK = "#9D3B00"
BROWN = "#3D1A00"
GRAY = "#6B6B6B"
CMAP = LinearSegmentedColormap.from_list("oranye", [ORANGE_PALE, ORANGE_LIGHT, ORANGE, ORANGE_DARK])

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "viz")
MAX_OUTSIDE_ROWS = 22

# Util
def _finish(fig, save_path, show):
    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)
    return save_path

def _box_faces(x, y, z, dx, dy, dz):
    p = [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z),
         (x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)]
    idx = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]
    return [[p[i] for i in face] for face in idx]

# State 3D
def draw_state(state, title="State", save_path=None, labels=True, show=False):
    truck = state.truck
    W, L, H = truck.width, truck.length, truck.height

    fig = plt.figure(figsize=(13, 6.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[2.3, 0.07, 1.1], wspace=0.28)
    ax = fig.add_subplot(gs[0], projection="3d")
    ax.computed_zorder = False  # urutan gambar mengikuti lantai < rangka < balok < label
    cax = fig.add_subplot(gs[1])
    side = fig.add_subplot(gs[2])
    side.axis("off")

    # lantai tipis + kerangka
    ax.add_collection3d(Poly3DCollection([[(0, 0, 0), (W, 0, 0), (W, L, 0), (0, L, 0)]],
                                         facecolors="#EEEEEE", alpha=0.5, edgecolors="none", zorder=0))
    ax.add_collection3d(Poly3DCollection(_box_faces(0, 0, 0, W, L, H), facecolors=(0, 0, 0, 0),
                                         edgecolors=GRAY, linewidths=1.4, zorder=1))

    vmax = max([p.value for p in state.packages] + [1])
    norm = Normalize(0, vmax)
    # semua sisi balok dikumpulkan dalam satu grup agar diurutkan per sisi 
    faces, face_colors, edge_colors, widths, styles = [], [], [], [], []
    for p in state.placed_packages:
        x, y, z = p.position
        dx, dy, dz = p.dimension
        box = _box_faces(x, y, z, dx, dy, dz)
        faces += box
        face_colors += [CMAP(norm(p.value))] * len(box)
        edge_colors += [BROWN if p.is_fragile else ORANGE_DARK] * len(box)
        widths += [1.8 if p.is_fragile else 0.8] * len(box)
        styles += ["--" if p.is_fragile else "-"] * len(box)
    if faces:
        ax.add_collection3d(Poly3DCollection(faces, facecolors=face_colors, edgecolors=edge_colors,
                                             linewidths=widths, linestyles=styles, alpha=0.95, zorder=2))
    if labels:
        for p in state.placed_packages:
            x, y, z = p.position
            dx, dy, dz = p.dimension
            ax.text(x + dx / 2, y + dy / 2, z + dz, p.id + ("*" if p.is_fragile else ""),
                    ha="center", va="bottom", fontsize=6.5, color=BROWN,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
                    zorder=10)

    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    ax.set_zlim(0, H)
    ax.set_box_aspect((W, L, H), zoom=1.15)
    ax.set_xlabel("x (lebar)", labelpad=10)
    ax.set_ylabel("y (panjang)", labelpad=16)
    ax.set_zlabel("z (tinggi)", labelpad=6)
    ax.tick_params(axis="both", labelsize=8, pad=2)
    ax.view_init(elev=28, azim=-55)
    fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), cax=cax, label="Value paket")

    # panel di luar truk
    outside = [p for p in state.packages if not p.is_placed]
    rows = [f"Di luar truk: {len(outside)} paket", f"{'id':<8}{'w x l x h':<11}{'val':>5}{'wt':>5}  F"]
    for p in outside[:MAX_OUTSIDE_ROWS]:
        rows.append(f"{p.id:<8}{f'{p.width}x{p.length}x{p.height}':<11}{p.value:>5}{p.weight:>5}  "
                    f"{'Y' if p.is_fragile else '-'}")
    if len(outside) > MAX_OUTSIDE_ROWS:
        rows.append(f"... +{len(outside) - MAX_OUTSIDE_ROWS} paket lainnya")
    side.text(0, 1, "\n".join(rows), va="top", family="monospace", fontsize=8, color=BROWN)
    side.text(0, 0, "* dan garis putus-putus = pecah-belah\nwarna lebih gelap = value lebih besar",
              va="bottom", fontsize=8, color=GRAY)

    fig.suptitle(
        f"{title}\nValue {state.total_value} | berat {state.current_weight}/{truck.max_capacity} | "
        f"utilisasi ruang {state.space_utilization:.1f}% | "
        f"{len(state.placed_packages)}/{len(state.packages)} paket di dalam",
        fontsize=11, color=BROWN)
    return _finish(fig, save_path, show)

def plot_history(history, title="Nilai objective terhadap iterasi", save_path=None,
                 xlabel="Iterasi", ylabel="Nilai objective",
                 labels=("Maksimum populasi", "Rata-rata populasi"), show=False):

    fig, ax = plt.subplots(figsize=(8, 4.5))
    if history and isinstance(history[0], (tuple, list)):
        ax.plot(range(len(history)), [h[0] for h in history], color=ORANGE, lw=2, label=labels[0])
        ax.plot(range(len(history)), [h[1] for h in history], color=ORANGE_LIGHT, lw=2, ls="--",
                label=labels[1])
        ax.legend(frameon=False)
    else:
        ax.plot(range(len(history)), history, color=ORANGE, lw=2)
    ax.set_title(title, color=BROWN, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return _finish(fig, save_path, show)

def visualize_run(record_path, out_dir=DEFAULT_OUT, show=False):
    with open(record_path) as f:
        rec = json.load(f)
    name = rec.get("name", os.path.splitext(os.path.basename(record_path))[0])

    info = []
    if "population_size" in rec:
        info.append(f"populasi {rec['population_size']}")
    if "generations" in rec:
        info.append(f"{rec['generations']} generasi")
    if "duration" in rec:
        info.append(f"{rec['duration']:.2f} s")
    if "seed" in rec:
        info.append(f"seed {rec['seed']}")
    is_ga = "population_size" in rec

    paths = [
        draw_state(state_from_dict(rec["initial_state"]), f"{name} - state awal",
                   os.path.join(out_dir, f"{name}_awal.png"), show=show),
        draw_state(state_from_dict(rec["final_state"]), f"{name} - state akhir",
                   os.path.join(out_dir, f"{name}_akhir.png"), show=show),
        plot_history(rec["history"], f"{name}\n{' | '.join(info)}",
                     os.path.join(out_dir, f"{name}_history.png"),
                     xlabel="Generasi" if is_ga else "Iterasi", show=show),
    ]
    return paths


def load_records(directory):
    records = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict) and "final_value" in data and "history" in data:
            records.append(data)
    return records


def plot_experiment_summary(records, save_path=None, title="Hasil eksperimen Genetic Algorithm",
                            show=False):
    groups = [g for g in ("iterasi", "populasi") if any(r.get("group") == g for r in records)]
    if not groups:
        raise ValueError("tidak ada record dengan group 'iterasi' atau 'populasi'")

    fig, axes = plt.subplots(2, len(groups), figsize=(6.4 * len(groups), 8), squeeze=False)
    for col, g in enumerate(groups):
        recs = [r for r in records if r.get("group") == g]
        order = (lambda c: c[1]) if g == "iterasi" else (lambda c: c[0])
        configs = sorted({(r["population_size"], r["generations"]) for r in recs}, key=order)
        labels = [f"{c[1]} generasi\n(pop {c[0]})" if g == "iterasi"
                  else f"populasi {c[0]}\n({c[1]} generasi)" for c in configs]

        for row, (key, ylabel) in enumerate((("final_value", "Nilai objective akhir"),
                                             ("duration", "Durasi (detik)"))):
            ax = axes[row][col]
            for k, c in enumerate(configs):
                vals = [r[key] for r in recs if (r["population_size"], r["generations"]) == c]
                ax.bar(k, sum(vals) / len(vals), color=ORANGE_LIGHT, alpha=0.55, width=0.55)
                xs = [k + (i - (len(vals) - 1) / 2) * 0.09 for i in range(len(vals))]
                ax.scatter(xs, vals, color=ORANGE, edgecolor=ORANGE_DARK, zorder=3, s=36)
            ax.set_xticks(range(len(configs)))
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_ylabel(ylabel)
            ax.grid(axis="y", alpha=0.25)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            if row == 0:
                ax.set_title("Variasi banyak iterasi (populasi dikontrol)" if g == "iterasi"
                             else "Variasi jumlah populasi (iterasi dikontrol)",
                             color=BROWN, fontsize=10)
    fig.suptitle(title, color=BROWN, fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return _finish(fig, save_path, show)

# Demo
def demo(out_dir, show=False):
    import random
    from gen_dataset import build
    from generator import generate
    from genetic_algorithm import genetic_algorithm
    from models import Package, Truck

    data = build(30, 2026)
    truck = Truck(**data["Truck"])
    packages = [Package(**p) for p in data["Package"]]

    random.seed(3)
    out = []
    out.append(draw_state(generate(truck, packages), "Demo - state dari generator",
                          os.path.join(out_dir, "demo_state.png"), show=show))

    _, dur, init_s, best_s, _, hist = genetic_algorithm(truck, packages, 30, 40, seed=3)
    out.append(draw_state(init_s, "Demo GA - state awal", os.path.join(out_dir, "demo_ga_awal.png"), show=show))
    out.append(draw_state(best_s, "Demo GA - state akhir", os.path.join(out_dir, "demo_ga_akhir.png"), show=show))
    out.append(plot_history(hist, f"Demo GA (populasi 30, 40 generasi, {dur:.2f} s)",
                            os.path.join(out_dir, "demo_ga_history.png"), xlabel="Generasi", show=show))

    mock, v = [], 0
    for _ in range(60):
        v += random.choice([0, 0, 0, 40, 70, 120])
        mock.append(v)
    out.append(plot_history(mock, "[DATA TIRUAN] contoh history hill-climbing (list angka)",
                            os.path.join(out_dir, "demo_hc_history.png"), show=show))

    records = []
    for group, configs in (("iterasi", [(20, 10), (20, 20), (20, 40)]),
                           ("populasi", [(10, 20), (20, 20), (40, 20)])):
        for pop, gens in configs:
            for run in range(3):
                _, d, _, _, bv, _ = genetic_algorithm(truck, packages, pop, gens, seed=100 + run)
                records.append({"group": group, "population_size": pop, "generations": gens,
                                "final_value": bv, "duration": d})
    out.append(plot_experiment_summary(records, os.path.join(out_dir, "demo_ringkasan.png"),
                                       title="[DEMO KECIL] Ringkasan eksperimen GA", show=show))
    return out


def main():
    ap = argparse.ArgumentParser(description="Visualisasi Tubes 1 IF3170")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run", help="visualisasi satu record JSON")
    p_run.add_argument("record")
    p_sum = sub.add_parser("summary", help="ringkasan semua record JSON dalam satu folder")
    p_sum.add_argument("directory")
    p_demo = sub.add_parser("demo", help="contoh dengan data tiruan dan GA kecil")
    for p in (p_run, p_sum, p_demo):
        p.add_argument("--out", default=DEFAULT_OUT)
        p.add_argument("--show", action="store_true", help="tampilkan jendela (default: simpan PNG saja)")
    args = ap.parse_args()

    if not args.show:
        plt.switch_backend("Agg")

    if args.cmd == "run":
        paths = visualize_run(args.record, args.out, args.show)
    elif args.cmd == "summary":
        paths = [plot_experiment_summary(load_records(args.directory),
                                         os.path.join(args.out, "ringkasan_ga.png"), show=args.show)]
    else:
        paths = demo(args.out, args.show)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()