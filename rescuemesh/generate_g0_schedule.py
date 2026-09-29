"""Sinh lịch screening G0 có block và random hóa tái lập.

Đơn vị độc lập là một phiên đo ba phút. Packet trong cùng phiên là quan sát lồng
nhau, không phải replication độc lập. Mỗi block pair × replicate chứa đủ 16 tổ
hợp 2^4 đúng một lần, nhưng thứ tự chạy được xáo bằng seed cố định.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import random
from pathlib import Path


FACTORS = {
    "advertise_mode": ("low_latency_100ms", "balanced_250ms"),
    "scan_mode": ("low_latency", "balanced"),
    "distance_m": (1, 5),
    "wifi_load": ("off", "udp_active"),
}


def block_seed(seed: int, pair_id: str, replicate: int) -> int:
    raw = f"{seed}|{pair_id}|{replicate}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def generate(pairs: int = 3, replicates: int = 3, seed: int = 20260929):
    keys = tuple(FACTORS)
    combinations = [dict(zip(keys, values)) for values in itertools.product(
        *(FACTORS[key] for key in keys)
    )]
    rows = []
    run_id = 0
    for pair_index in range(1, pairs + 1):
        pair_id = f"PAIR_{pair_index:02d}"
        for replicate in range(1, replicates + 1):
            block = combinations.copy()
            random.Random(block_seed(seed, pair_id, replicate)).shuffle(block)
            for order, condition in enumerate(block, 1):
                run_id += 1
                rows.append({
                    "run_id": f"G0S-{run_id:04d}",
                    "pair_id": pair_id,
                    "replicate": replicate,
                    "order_in_block": order,
                    **condition,
                    "duration_s": 180,
                    "screen": "off",
                    "scan_filter": "manufacturer_and_protocol_prefix",
                    "traffic": "bidirectional_sos",
                })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--output", type=Path,
                        default=Path("results/g0-screening-schedule.csv"))
    args = parser.parse_args()
    if args.pairs < 1 or args.replicates < 1:
        raise SystemExit("pairs và replicates phải >= 1")
    rows = generate(args.pairs, args.replicates, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} runs to {args.output}")


if __name__ == "__main__":
    main()
