"""Parse Kaggle kernel logs (lerobot-train / lerobot-eval) into a loss CSV and eval summary.

Kaggle log format: each line is `,{"stream_name":"stdout","time":...,"data":"..."}`.

Usage:
    python results/parse_metaworld_logs.py <logfile> [output_prefix]
"""
import json
import re
import sys
from pathlib import Path

STEP_RE = re.compile(r"step:(\d+).*?loss:([\d.]+)")
EVAL_RE = re.compile(r"(success|Success).*?([\d.]+)%?")
TASK_RE = re.compile(r"task[=:]\s*([\w\-]+)")


def iter_data(log_path: str):
    with open(log_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith(",{"):
                continue
            try:
                obj = json.loads(line[1:])
            except json.JSONDecodeError:
                continue
            yield obj.get("stream_name"), obj.get("data", "")


def main() -> None:
    log_path = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else Path(log_path).stem

    losses = []  # (step, loss)
    eval_lines = []
    for stream, data in iter_data(log_path):
        m = STEP_RE.search(data)
        if m:
            losses.append((int(m.group(1)), float(m.group(2))))
        if "success" in data.lower() and "%" in data:
            eval_lines.append(data.strip())

    if losses:
        csv_path = Path(prefix + "_loss.csv")
        with csv_path.open("w", encoding="utf-8") as f:
            f.write("step,loss\n")
            for step, loss in losses:
                f.write(f"{step},{loss}\n")
        first, last = losses[0], losses[-1]
        print(f"[loss] {len(losses)} points | first {first[1]:.4f} (step {first[0]}) | last {last[1]:.4f} (step {last[0]}) -> {csv_path}")

    if eval_lines:
        print("[eval] success lines:")
        for l in eval_lines[-20:]:
            print("   ", l[:160])
    else:
        print("[eval] no success-rate lines found")


if __name__ == "__main__":
    main()
