"""Mô phỏng rời rạc tối thiểu cho RescueMesh-AI.

Đây là mô hình kiểm tra logic (SIM-SMOKE), chưa được hiệu chuẩn với điện thoại.
Nó mô hình hóa broadcast, mất gói độc lập, jitter, TTL, dedup và ba chiến lược
forwarding. Chưa có collision, queue radio, mobility, beacon overhead hay pin.
"""

from __future__ import annotations

import hashlib
import math
import random
from collections import deque
from dataclasses import dataclass
from typing import Literal

import simpy

Strategy = Literal["flood", "trickle", "gradient"]


@dataclass(frozen=True)
class SimConfig:
    n_nodes: int = 50
    area_m: float = 200.0
    range_m: float = 55.0
    link_pdr: float = 0.85
    ttl: int = 15
    jitter_min_s: float = 0.010
    jitter_max_s: float = 0.220
    trickle_k: int = 3
    horizon_s: float = 10.0


@dataclass(frozen=True)
class SimResult:
    strategy: Strategy
    seed: int
    source: int
    delivered: bool
    latency_s: float | None
    transmissions: int
    receptions: int
    connected_source: bool


def random_geometric_graph(cfg: SimConfig, seed: int) -> tuple[list[tuple[float, float]], list[set[int]]]:
    rng = random.Random(seed)
    points = [(cfg.area_m / 2, cfg.area_m / 2)]
    points += [(rng.uniform(0, cfg.area_m), rng.uniform(0, cfg.area_m)) for _ in range(cfg.n_nodes - 1)]
    graph = [set() for _ in points]
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if math.dist(points[i], points[j]) <= cfg.range_m:
                graph[i].add(j)
                graph[j].add(i)
    return points, graph


def hop_gradient(graph: list[set[int]], station: int = 0) -> list[int]:
    hops = [10**9] * len(graph)
    hops[station] = 0
    queue = deque([station])
    while queue:
        node = queue.popleft()
        for nbr in graph[node]:
            if hops[nbr] > hops[node] + 1:
                hops[nbr] = hops[node] + 1
                queue.append(nbr)
    return hops


def _uniform(seed: int, *parts: object) -> float:
    raw = "|".join(map(str, (seed,) + parts)).encode()
    value = int.from_bytes(hashlib.blake2s(raw, digest_size=8).digest(), "big")
    return value / 2**64


def simulate_once(cfg: SimConfig, strategy: Strategy, seed: int, source: int | None = None,
                  graph: list[set[int]] | None = None) -> SimResult:
    """Chạy một replication kết thúc ở ``horizon_s``; đơn vị thời gian là giây."""
    if cfg.n_nodes < 2 or cfg.n_nodes > 500:
        raise ValueError("n_nodes phải trong [2, 500]")
    if not 0 <= cfg.link_pdr <= 1:
        raise ValueError("link_pdr phải trong [0, 1]")
    if strategy not in ("flood", "trickle", "gradient"):
        raise ValueError("strategy không hợp lệ")

    if graph is None:
        _, graph = random_geometric_graph(cfg, seed)
    if len(graph) != cfg.n_nodes:
        raise ValueError("graph không khớp n_nodes")
    hops = hop_gradient(graph)
    if source is None:
        source = 1 + int(_uniform(seed, "source") * (cfg.n_nodes - 1))
    if not 1 <= source < cfg.n_nodes:
        raise ValueError("source phải là nút khác trạm")

    env = simpy.Environment()
    seen: list[set[int]] = [set() for _ in graph]
    duplicate_count = [0] * len(graph)
    tx_attempt = [0] * len(graph)
    scheduled = [False] * len(graph)
    delivered_at: list[float] = []
    transmissions = 0
    receptions = 0
    packet_id = 1

    def link_success(sender: int, receiver: int, attempt: int) -> bool:
        return _uniform(seed, "link", sender, receiver, packet_id, attempt) < cfg.link_pdr

    def jitter(node: int) -> float:
        u = _uniform(seed, "jitter", node, packet_id)
        return cfg.jitter_min_s + u * (cfg.jitter_max_s - cfg.jitter_min_s)

    def broadcast(sender: int, ttl: int, sender_hop: int):
        nonlocal transmissions, receptions
        if ttl < 0:
            return
        attempt = tx_attempt[sender]
        tx_attempt[sender] += 1
        transmissions += 1
        for receiver in sorted(graph[sender]):
            if link_success(sender, receiver, attempt):
                receptions += 1
                env.process(receive(receiver, sender, ttl, sender_hop))
        yield env.timeout(0)

    def scheduled_forward(node: int, ttl: int):
        yield env.timeout(jitter(node))
        if strategy == "trickle" and duplicate_count[node] >= cfg.trickle_k:
            return
        yield env.process(broadcast(node, ttl - 1, hops[node]))

    def receive(node: int, sender: int, ttl: int, sender_hop: int):
        if packet_id in seen[node]:
            duplicate_count[node] += 1
            return
        seen[node].add(packet_id)
        if node == 0:
            if not delivered_at:
                delivered_at.append(env.now)
            return
        if ttl <= 0:
            return
        if strategy == "gradient" and not (hops[node] < sender_hop):
            return
        if not scheduled[node]:
            scheduled[node] = True
            env.process(scheduled_forward(node, ttl))
        yield env.timeout(0)

    seen[source].add(packet_id)
    env.process(broadcast(source, cfg.ttl, hops[source]))
    env.run(until=cfg.horizon_s)
    return SimResult(strategy, seed, source, bool(delivered_at),
                     delivered_at[0] if delivered_at else None,
                     transmissions, receptions, hops[source] < 10**9)


def line_graph(n: int) -> list[set[int]]:
    graph = [set() for _ in range(n)]
    for i in range(n - 1):
        graph[i].add(i + 1)
        graph[i + 1].add(i)
    return graph
