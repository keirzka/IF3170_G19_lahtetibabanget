import csv
import json
import logging
import os
import random
import statistics
import time

from generator import generate
from io_handler import load_data_from_json, state_to_json
from models import State

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")
DEFAULT_SEEDS = [1, 2, 3]
SUMMARY_FIELDS = ["name", "variant", "run", "seed", "initial_value", "final_value", "iterations", "duration"]

def input_name(file_name):
    return os.path.splitext(os.path.basename(file_name))[0]

def output_dir_for(algorithm_key, file_name):
    path = os.path.join(OUTPUT_DIR, algorithm_key, input_name(file_name))
    os.makedirs(path, exist_ok=True)
    return path

def seed_everything(seed):
    random.seed(seed)

def setup_logger(out_dir, name):
    logger = logging.getLogger(f"{name}:{out_dir}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s | %(message)s", "%H:%M:%S")
    for handler in (logging.FileHandler(os.path.join(out_dir, "experiment.log"), "w", "utf-8"),
                    logging.StreamHandler()):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger

def to_record_value(value):
    if isinstance(value, State):
        return state_to_json(value)
    if isinstance(value, tuple):
        return list(value)
    return value

def save_record(out_dir, record):
    path = os.path.join(out_dir, record["name"] + ".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({k: to_record_value(v) for k, v in record.items()}, f)
    return path

def summary_row(record):
    row = {k: record.get(k) for k in SUMMARY_FIELDS}
    for k, v in record.items():
        if k not in row and isinstance(v, (int, float, str, bool)):
            row[k] = v
    return row

def write_summary(out_dir, rows):
    fields = list(SUMMARY_FIELDS)
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with open(os.path.join(out_dir, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def log_group_statistics(logger, rows, key="variant"):
    groups = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row)
    for group, items in groups.items():
        finals = [r["final_value"] for r in items]
        durations = [r["duration"] for r in items]
        std = statistics.pstdev(finals) if len(finals) > 1 else 0.0
        logger.info(f"{group}: rata-rata nilai akhir={statistics.mean(finals):.2f} "
                    f"std={std:.2f} rata-rata durasi={statistics.mean(durations):.3f}s")

def run_experiment(algorithm, variant, file_name, search_fn, seeds=DEFAULT_SEEDS,
                   algorithm_key=None, logger=None):
    data = load_data_from_json(file_name)
    out_dir = output_dir_for(algorithm_key or variant, file_name)
    logger = logger or setup_logger(out_dir, variant)
    logger.info(f"{algorithm} | input={os.path.basename(file_name)} | "
                f"{len(data.trucks)} truk | {len(data.packages)} paket | seed={list(seeds)}")
    rows = []
    for run, seed in enumerate(seeds, 1):
        seed_everything(seed)
        initial_state = generate(data.trucks, data.packages)
        start = time.perf_counter()
        result = search_fn(initial_state)
        duration = result.pop("duration", time.perf_counter() - start)
        record = {
            "algorithm": algorithm,
            "name": f"{variant}_run{run}",
            "variant": variant,
            "input_file": os.path.basename(file_name),
            "run": run,
            "seed": seed,
            "duration": duration,
            "iterations": result.pop("iterations"),
            "initial_value": result.pop("initial_value"),
            "final_value": result.pop("final_value"),
        }
        result.pop("initial_state", None)
        final_state = result.pop("final_state")
        history = result.pop("history")
        record.update(result)
        record["history"] = history
        record["initial_state"] = initial_state
        record["final_state"] = final_state
        save_record(out_dir, record)
        row = summary_row(record)
        rows.append(row)
        logger.info(f"{record['name']}: awal={record['initial_value']} "
                    f"akhir={record['final_value']} iterasi={record['iterations']} "
                    f"durasi={duration:.3f}s")
    return rows, out_dir, logger