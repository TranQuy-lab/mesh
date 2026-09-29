"""Chạy thí nghiệm SIM-SMOKE; không dùng để kết luận về hệ thống thật."""

from __future__ import annotations

import csv
from pathlib import Path

from sim import SimConfig, random_geometric_graph, simulate_once


def main() -> None:
    output = Path(__file__).resolve().parent.parent / "results" / "sim-smoke.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for n_nodes in (20, 50, 100):
        cfg = SimConfig(n_nodes=n_nodes)
        for seed in range(30):
            _, graph = random_geometric_graph(cfg, seed)
            source = 1 + seed % (n_nodes - 1)
            for strategy in ("flood", "trickle", "gradient"):
                r = simulate_once(cfg, strategy, seed, source=source, graph=graph)
                rows.append({
                    "label": "SIM-SMOKE-UNCALIBRATED",
                    "n_nodes": n_nodes,
                    "seed": seed,
                    "source": source,
                    "strategy": strategy,
                    "connected_source": int(r.connected_source),
                    "delivered": int(r.delivered),
                    "latency_s": "" if r.latency_s is None else f"{r.latency_s:.6f}",
                    "transmissions": r.transmissions,
                    "receptions": r.receptions,
                })
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {output}")


if __name__ == "__main__":
    main()
