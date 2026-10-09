import copy
import csv
import dataclasses
import json
import logging
import os
import random
import time
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from models import Package, State, Truck

OBJECTIVE_KEYS = ["history", "best_history", "history_max", "history_avg"]
LABELS = {
    "history": "Current value",
    "best_history": "Best value",
    "history_max": "Max populasi",
    "history_avg": "Rata-rata populasi",
}
STATE_KEYS = {"initial_state", "final_state", "best_state"}
SUMMARY_SKIP = {"history", "best_history", "history_max", "history_avg", "prob_history", "temp_history", "stuck_iterations", "acceptance_rate_history"}

def state_to_dict(state):
    return {
        "summary": {
            "total_value": state.total_value,
            "current_weight": state.current_weight,
            "max_capacity": state.truck.max_capacity,
            "placed_count": len(state.placed_packages),
            "total_packages": len(state.packages),
            "space_utilization_percent": round(state.space_utilization, 2),
        },
        "truck": dataclasses.asdict(state.truck),
        "packages": [
            {
                **{k: v for k, v in dataclasses.asdict(p).items()
                   if k not in ("position", "orientation")},
                "orientation": list(p.orientation),
                "position": list(p.position) if p.is_placed else None,
                "dimension": list(p.dimension),
                "inside": p.is_placed,
            }
            for p in state.packages
        ],
    }

def state_from_dict(data):
    truck = Truck(**data["truck"])
    fields = {f.name for f in dataclasses.fields(Package)}
    packages = []
    for p in data["packages"]:
        kwargs = {k: v for k, v in p.items() if k in fields}
        kwargs["orientation"] = tuple(p["orientation"])
        kwargs["position"] = tuple(p["position"]) if p["position"] is not None else None
        packages.append(Package(**kwargs))
    return State(truck, packages)

def to_jsonable(obj):
    if isinstance(obj, State):
        return state_to_dict(obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return to_jsonable(dataclasses.asdict(obj))
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    if hasattr(obj, "tolist"):
        return obj.tolist()
    return obj

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_jsonable(data), f, indent=2, ensure_ascii=False)

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_state(path):
    return state_from_dict(load_json(path))

def setup_logger(log_path, name="experiment"):
    logger = logging.getLogger(f"{name}_{log_path}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%H:%M:%S")
    for handler in (logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger

def plot_objective(result, path, title):
    keys = [k for k in OBJECTIVE_KEYS if result.get(k)]
    if not keys:
        return
    plt.figure(figsize=(10, 5))
    for k in keys:
        plt.plot(result[k], label=LABELS[k], linewidth=1)
    plt.xlabel("Iterasi")
    plt.ylabel("Nilai objective function")
    plt.title(title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()

def plot_acceptance_prob(result, path, title):
    probs = result.get("prob_history")
    if not probs:
        return
    plt.figure(figsize=(10, 5))
    plt.scatter(range(1, len(probs) + 1), probs, s=2, alpha=0.5)
    plt.xlabel("Iterasi")
    plt.ylabel(r"$e^{\Delta E / T}$")
    plt.ylim(-0.05, 1.05)
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()

def plot_comparison(results, path, title, key=None):
    if key is None:
        key = next((k for k in ("history_max", "history") if results and results[0].get(k)), None)
    if key is None:
        return
    plt.figure(figsize=(10, 5))
    for i, r in enumerate(results, 1):
        plt.plot(r.get(key, []), label=f"Run {i} (final={r.get('final_value')})", linewidth=1)
    plt.xlabel("Iterasi")
    plt.ylabel("Nilai objective function")
    plt.title(title)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()

def _seed_everything(seed):
    if seed is None:
        return
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass

def run_experiment(name, algorithm, initial_state_factory, n_runs=3, output_dir="../output", seeds=None, config=None):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exp_dir = os.path.join(output_dir, f"{name}_{stamp}")
    os.makedirs(exp_dir, exist_ok=True)
    logger = setup_logger(os.path.join(exp_dir, "experiment.log"))
    logger.info(f"Mulai eksperimen '{name}' ({n_runs} run), config={config}")
    results, summary_rows = [], []
    for run in range(1, n_runs + 1):
        seed = seeds[run - 1] if seeds else None
        _seed_everything(seed)
        run_dir = os.path.join(exp_dir, f"run_{run}")
        os.makedirs(run_dir, exist_ok=True)
        initial_state = initial_state_factory()
        saved_initial = copy.deepcopy(initial_state)
        save_json(saved_initial, os.path.join(run_dir, "initial_state.json"))
        logger.info(f"Run {run}: mulai (seed={seed})")
        wall_start = time.perf_counter()
        result = algorithm(initial_state)
        wall = time.perf_counter() - wall_start
        result.setdefault("duration", wall)
        result.setdefault("initial_state", saved_initial)
        save_json(result["final_state"], os.path.join(run_dir, "final_state.json"))
        save_json({k: v for k, v in result.items() if k not in STATE_KEYS}, os.path.join(run_dir, "result.json"))
        title = f"{name} - Run {run}"
        plot_objective(result, os.path.join(run_dir, "objective_plot.png"), f"{title}: Objective function vs iterasi")
        plot_acceptance_prob(result, os.path.join(run_dir, "acceptance_prob_plot.png"), f"{title}: " + r"$e^{\Delta E/T}$ vs iterasi")
        row = {"run": run, "seed": seed}
        row.update({k: v for k, v in result.items() if k not in STATE_KEYS | SUMMARY_SKIP and not isinstance(v, (dict, list))})
        params = result.get("params")
        if isinstance(params, dict):
            row.update({f"param_{k}": v for k, v in params.items() if not isinstance(v, (dict, list))})
        if config:
            row.update({f"cfg_{k}": v for k, v in config.items()})
        summary_rows.append(row)
        results.append(result)
        logger.info(f"Run {run}: selesai | initial={result.get('initial_value')} "
                    f"final={result['final_value']} durasi={result['duration']:.3f}s "
                    + (f"iterasi={result['iterations']} " if "iterations" in result else "")
                    + (f"stuck={result['stuck_count']}" if "stuck_count" in result else ""))
    plot_comparison(results, os.path.join(exp_dir, "comparison_plot.png"), f"{name}: perbandingan {n_runs} run")
    finals = [r["final_value"] for r in results]
    durations = [r["duration"] for r in results]
    mean_final = sum(finals) / len(finals)
    aggregate = {
        "name": name,
        "config": config,
        "n_runs": n_runs,
        "final_values": finals,
        "best_final": max(finals),
        "worst_final": min(finals),
        "mean_final": mean_final,
        "std_final": (sum((v - mean_final) ** 2 for v in finals) / len(finals)) ** 0.5,
        "mean_duration": sum(durations) / len(durations),
        "runs": summary_rows,
    }
    save_json(aggregate, os.path.join(exp_dir, "summary.json"))
    fieldnames = sorted({k for row in summary_rows for k in row}, key=lambda k: (k != "run", k))
    with open(os.path.join(exp_dir, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    logger.info(f"Selesai. mean_final={aggregate['mean_final']:.2f} "
                f"std={aggregate['std_final']:.2f} mean_durasi={aggregate['mean_duration']:.3f}s")
    logger.info(f"Output tersimpan di {exp_dir}")
    return results, exp_dir

def compare_algorithms(summary_paths, output_path="../output/algorithm_comparison.png"):
    data = [load_json(p) for p in summary_paths]
    names = [d["name"] for d in data]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(names, [d["mean_final"] for d in data], yerr=[d["std_final"] for d in data], capsize=5)
    axes[0].set_title("Rata-rata nilai objective akhir (± std)")
    axes[1].bar(names, [d["mean_duration"] for d in data])
    axes[1].set_title("Rata-rata durasi (detik)")
    for ax in axes:
        ax.tick_params(axis="x", rotation=30)
        ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=120)
    plt.close()
    return output_path