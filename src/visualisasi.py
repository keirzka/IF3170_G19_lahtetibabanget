import argparse
import csv
import glob
import json
import math
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from io_handler import state_from_json

ORANGE = "#E85D04"
ORANGE_LIGHT = "#FAA307"
ORANGE_PALE = "#FFE8CC"
ORANGE_DARK = "#9D3B00"
BROWN = "#3D1A00"
GRAY = "#6B6B6B"
BLACK = "#000000"
CMAP = LinearSegmentedColormap.from_list("oranye", [ORANGE_PALE, ORANGE_LIGHT, ORANGE, ORANGE_DARK])

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
MAX_OUTSIDE_ROWS = 22
ELEV, AZIM = 28, -55

def _finish(fig, save_path, show=False):
    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return save_path

def _style(ax, title, xlabel, ylabel):
    ax.set_title(title, color=BROWN, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.25)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
def _box_faces(x, y, z, dx, dy, dz):
    p = [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z),
         (x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)]
    idx = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (1, 2, 6, 5), (0, 3, 7, 4)]
    return [[p[i] for i in face] for face in idx]

def _depth_key():
    elev, azim = math.radians(ELEV), math.radians(AZIM)
    cam = (math.cos(elev) * math.cos(azim), math.cos(elev) * math.sin(azim), math.sin(elev))
    def depth(p):
        dx, dy, dz = p.dimension
        x, y, z = p.position
        return (x + dx / 2) * cam[0] + (y + dy / 2) * cam[1] + (z + dz / 2) * cam[2]
    return depth
def _draw_truck(ax, state, truck_id, norm, labels):
    truck = state.trucks[truck_id]
    W, L, H = truck.width, truck.length, truck.height
    ax.computed_zorder = False
    ax.add_collection3d(Poly3DCollection([[(0, 0, 0), (W, 0, 0), (W, L, 0), (0, L, 0)]],
                                         facecolors="#EEEEEE", alpha=0.5, edgecolors="none", zorder=0))
    ax.add_collection3d(Poly3DCollection(_box_faces(0, 0, 0, W, L, H), facecolors=(0, 0, 0, 0),
                                         edgecolors=GRAY, linewidths=1.4, zorder=1))

    zorder = 2
    for p in sorted(state.packages_in(truck_id), key=_depth_key()):
        x, y, z = p.position
        dx, dy, dz = p.dimension
        box = _box_faces(x, y, z, dx, dy, dz)
        ax.add_collection3d(Poly3DCollection(box, facecolors=[CMAP(norm(p.value))] * len(box),
                                             edgecolors=BLACK, linewidths=0.8,
                                             linestyles="--" if p.is_fragile else "-",
                                             alpha=0.95, zorder=zorder))
        if labels:
            ax.text(x + dx / 2, y + dy / 2, z + dz, p.id + ("*" if p.is_fragile else ""),
                    ha="center", va="bottom", fontsize=6.5, color=BROWN,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75),
                    zorder=zorder + 1000)
        zorder += 1

    ax.set_xlim(0, W)
    ax.set_ylim(0, L)
    ax.set_zlim(0, H)
    ax.set_box_aspect((W, L, H), zoom=1.1)
    ax.set_xlabel("x (lebar)", labelpad=8)
    ax.set_ylabel("y (panjang)", labelpad=12)
    ax.set_zlabel("z (tinggi)", labelpad=4)
    ax.tick_params(axis="both", labelsize=7, pad=1)
    ax.view_init(elev=ELEV, azim=AZIM)
    if len(state.trucks) > 1:
        ax.set_title(f"Truk {truck_id + 1}: value {state.value_in(truck_id)} | "
                     f"berat {state.weight_in(truck_id)}/{truck.max_capacity}",
                     color=BROWN, fontsize=9)

def draw_state(state, title="State", save_path=None, labels=True, show=False):
    n = len(state.trucks)
    fig = plt.figure(figsize=(6.5 * n + 5.5, 6.2))
    gs = fig.add_gridspec(1, n + 2, width_ratios=[2.3] * n + [0.07, 1.1], wspace=0.28)
    norm = Normalize(0, max([p.value for p in state.packages] + [1]))

    for t in range(n):
        _draw_truck(fig.add_subplot(gs[t], projection="3d"), state, t, norm, labels)

    fig.colorbar(ScalarMappable(norm=norm, cmap=CMAP), cax=fig.add_subplot(gs[n]), label="Value paket")

    side = fig.add_subplot(gs[n + 1])
    side.axis("off")
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
        f"{title}\nValue {state.total_value} | berat {state.current_weight}/{state.total_capacity} | "
        f"utilisasi ruang {state.space_utilization:.1f}% | "
        f"{len(state.placed_packages)}/{len(state.packages)} paket di dalam {n} truk",
        fontsize=11, color=BROWN)
    return _finish(fig, save_path, show)

def plot_history(history, title="Nilai objective terhadap iterasi", save_path=None,
                 xlabel="Iterasi", ylabel="Nilai objective", best_history=None, show=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    if history and isinstance(history[0], (list, tuple)):
        ax.plot(range(len(history)), [h[0] for h in history], color=ORANGE, lw=2,
                label="Maksimum populasi")
        ax.plot(range(len(history)), [h[1] for h in history], color=ORANGE_LIGHT, lw=2, ls="--",
                label="Rata-rata populasi")
        ax.legend(frameon=False)
    elif history:
        ax.plot(range(len(history)), history, color=ORANGE, lw=1.2, label="Nilai current")
        if best_history:
            ax.plot(range(len(best_history)), best_history, color=ORANGE_DARK, lw=1.2, ls="--",
                    label="Nilai terbaik")
            ax.legend(frameon=False)
    _style(ax, title, xlabel, ylabel)
    return _finish(fig, save_path, show)

def plot_sa_probability(prob_history, title="e^(ΔE/T) terhadap iterasi", save_path=None, show=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.scatter(range(1, len(prob_history) + 1), prob_history, s=2, alpha=0.5, color=ORANGE)
    ax.set_ylim(-0.05, 1.05)
    _style(ax, title, "Iterasi", r"$e^{\Delta E / T}$")
    return _finish(fig, save_path, show)

def _info(rec):
    info = [f"durasi {rec.get('duration', 0):.2f} s", f"seed {rec.get('seed')}"]
    if "population_size" in rec:
        info = [f"populasi {rec['population_size']}", f"{rec['generations']} generasi"] + info
    else:
        info = [f"{rec.get('iterations', 0)} iterasi"] + info
    if "stuck_count" in rec:
        info.append(f"stuck {rec['stuck_count']} kali")
    if "restarts" in rec:
        info.append(f"{rec['restarts']} restart")
    if "sideways_moves" in rec:
        info.append(f"{rec['sideways_moves']} sideways move")
    return " | ".join(info)

def visualize_run(record_path, out_dir=None, show=False):
    with open(record_path, encoding="utf-8") as f:
        rec = json.load(f)
    name = rec.get("name", os.path.splitext(os.path.basename(record_path))[0])
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(record_path)), "gambar")
    algorithm = rec.get("algorithm", "")
    title = f"{name} ({algorithm})" if algorithm else name

    paths = [
        draw_state(state_from_json(rec["initial_state"]), f"{title} - state awal",
                   os.path.join(out_dir, f"{name}_awal.png"), show=show),
        draw_state(state_from_json(rec["final_state"]), f"{title} - state akhir",
                   os.path.join(out_dir, f"{name}_akhir.png"), show=show),
        plot_history(rec["history"], f"{title}\n{_info(rec)}",
                     os.path.join(out_dir, f"{name}_objective.png"),
                     xlabel="Generasi" if "population_size" in rec else "Iterasi",
                     best_history=rec.get("best_history"), show=show),
    ]
    if "prob_history" in rec:
        paths.append(plot_sa_probability(rec["prob_history"], f"{title}: e^(ΔE/T) terhadap iterasi",
                                         os.path.join(out_dir, f"{name}_probabilitas.png"), show=show))
    return paths


def load_records(directory):
    records = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "final_value" in data and "history" in data:
            records.append(data)
    return records


def plot_ga_summary(records, save_path=None, title="Hasil eksperimen Genetic Algorithm", show=False):
    groups = [g for g in ("iterasi", "populasi") if any(r.get("group") == g for r in records)]
    if not groups:
        return None

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

def visualize_folder(directory):
    records = load_records(directory)
    out_dir = os.path.join(directory, "gambar")
    paths = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "final_value" in data and "history" in data:
            paths += visualize_run(path, out_dir)
    if any("population_size" in r for r in records):
        paths.append(plot_ga_summary(records, os.path.join(out_dir, "ringkasan_ga.png")))
    return paths

def _read_summary(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def plot_algorithm_comparison(input_name, output_dir=OUTPUT_DIR, save_path=None, show=False):
    labels, means, stds, durations = [], [], [], []
    for algo_key, algo_label in (("hc", "HC"), ("sa", "SA"), ("ga", "GA")):
        path = os.path.join(output_dir, algo_key, input_name, "summary.csv")
        if not os.path.isfile(path):
            continue
        groups = {}
        for row in _read_summary(path):
            groups.setdefault(row["variant"], []).append(row)
        for variant, rows in groups.items():
            finals = [float(r["final_value"]) for r in rows]
            labels.append(f"{algo_label}\n{variant}")
            means.append(statistics.mean(finals))
            stds.append(statistics.pstdev(finals) if len(finals) > 1 else 0.0)
            durations.append(statistics.mean(float(r["duration"]) for r in rows))

    if not labels:
        return None

    fig, axes = plt.subplots(2, 1, figsize=(max(10, 1.1 * len(labels)), 9))
    xs = range(len(labels))
    axes[0].bar(xs, means, yerr=stds, capsize=4, color=ORANGE_LIGHT, edgecolor=ORANGE_DARK)
    axes[1].bar(xs, durations, color=ORANGE, edgecolor=ORANGE_DARK)
    _style(axes[0], f"Rata-rata nilai objective akhir (± simpangan baku) - {input_name}", "", "Nilai akhir")
    _style(axes[1], f"Rata-rata durasi - {input_name}", "", "Durasi (detik)")
    axes[1].set_yscale("log")
    for ax in axes:
        ax.set_xticks(list(xs))
        ax.set_xticklabels(labels, fontsize=7.5, rotation=45, ha="right")
    fig.tight_layout()
    save_path = save_path or os.path.join(output_dir, f"perbandingan_{input_name}.png")
    return _finish(fig, save_path, show)

def main():
    ap = argparse.ArgumentParser(description="Visualisasi hasil eksperimen")
    ap.add_argument("paths", nargs="*", default=[OUTPUT_DIR],
                    help="folder hasil eksperimen (default: seluruh folder output)")
    ap.add_argument("--compare", metavar="NAMA_INPUT",
                    help="buat grafik perbandingan HC, SA, dan GA untuk input tersebut")
    args = ap.parse_args()

    if args.compare:
        print(plot_algorithm_comparison(args.compare))
        return
    for root_path in args.paths:
        for directory, _, files in os.walk(root_path):
            if os.path.basename(directory) == "gambar" or "summary.csv" not in files:
                continue
            print(f"Memproses {directory} ...")
            visualize_folder(directory)
            print(f"-> gambar tersimpan di {os.path.join(directory, 'gambar')}")

if __name__ == "__main__":
    main()