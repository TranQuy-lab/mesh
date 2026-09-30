"""Bộ mô phỏng mạng LoRa đa chặng cho RescueMesh-LoRa (chỉ thư viện chuẩn).

Vai trò: sinh số liệu **mô phỏng** (nhãn `SIM`) cho năm chiến lược phát tán tin
SOS trên MỘT kênh LoRa dùng chung. Tệp này KHÔNG tạo ra số `ĐO`; mọi giá trị
phụ thuộc mô hình vật lý trong `lora.py` và các tham số `GIẢ ĐỊNH` trong
`LoraSimConfig`. Kết luận về hiệu năng thực địa bắt buộc phải hiệu chuẩn lại.

Mô hình
-------
- Thời gian liên tục (giây), sự kiện rời rạc, hàng đợi sự kiện theo thời gian.
- Mỗi lần phát chiếm kênh trong `[t, t + airtime]`. Va chạm xét ở mức kênh toàn
  cục: khung chồng lấn mất với mọi nút thu, trừ khi capture cứu được khung đến
  trước (xem `_resolve_channel`).
- PDR cặp nút: dùng `link_pdr` nếu được đặt, nếu không thì tính biên dự trữ
  bằng `lora.link_margin_db` rồi qua hàm logistic.
- Duty cycle: ngân sách airtime trượt trong cửa sổ 1 giờ cho từng nút.

Nhãn nguồn gốc: `SUY` = suy ra từ công thức/mô hình chuẩn; `GIẢ ĐỊNH` = giá trị
kỹ thuật chưa đối chiếu datasheet/văn bản pháp quy.

Chạy::

    python3 sim_lora.py                # ma trận đầy đủ, ghi ../results/sim-lora-*.csv
    python3 sim_lora.py --seeds 5      # chạy nhanh để kiểm tra
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import math
import os
import random
import statistics
from dataclasses import dataclass, field
from typing import Iterable

from lora import (
    BAND_VN_920_923_HZ,
    PATH_LOSS_EXPONENT,
    SF_MAX,
    SF_MIN,
    LoraProfile,
    link_margin_db,
    path_loss_log_distance_db,
)

EVIDENCE = "SIM"  #: Nhãn bằng chứng trên mọi dòng CSV và bảng in.
STRATEGIES = ("flood", "managed_flood", "gradient", "trickle", "store_carry_forward")
DUTY_WINDOW_S = 3600.0  #: Cửa sổ duty cycle theo quy ước băng ISM (giây).


@dataclass
class LoraSimConfig:
    """Cấu hình một lần mô phỏng mạng đơn kênh (mọi trường là tham số mô hình)."""

    n_nodes: int = 50
    area_m: float = 1000.0
    sf: int = 9
    bw_hz: float = 125_000.0
    cr: int = 1
    # GIẢ ĐỊNH: payload đủ chứa định danh, toạ độ thô và cờ ưu tiên.
    sos_payload_bytes: int = 36
    beacon_payload_bytes: int = 18
    link_pdr: float | None = None  # None = tính PDR từ vật lý
    # GIẢ ĐỊNH logistic: biên 0 dB ⇒ PDR 0,5; độ dốc 6 dB.
    margin_50_db: float = 0.0
    margin_slope_db: float = 6.0
    tx_dbm: float = 14.0  # GIẢ ĐỊNH
    # GIẢ ĐỊNH: kịch bản rừng/núi (cứu hộ) nên dùng suy hao mạnh n = 4,0.
    path_loss_exponent: float = PATH_LOSS_EXPONENT["dense_urban_or_forest"]  # SUY
    duty_cycle: float = 0.01  # GIẢ ĐỊNH theo thông lệ ISM, chưa đối chiếu luật
    duty_cycle_enabled: bool = True
    ttl: int = 4
    beacon_interval_s: float | None = 60.0
    cache_ttl_s: float = 120.0
    n_sos: int = 5
    sos_interval_s: float = 10.0
    n_gateways: int = 1
    gateway_outage: tuple[float, float] | None = None
    # warm_start=True: SOS phát sau khi beacon lan một vòng.
    # warm_start=False: cold start, SOS phát ngay ở t=0 (trước khi có tuyến).
    warm_start: bool = True
    warmup_s: float = 60.0  # GIẢ ĐỊNH: đủ để beacon lan một vòng
    n_couriers: int = 0
    courier_speed_m_s: float = 1.4  # GIẢ ĐỊNH: tốc độ đi bộ
    courier_step_s: float = 5.0
    duration_s: float = 240.0
    # GIẢ ĐỊNH capture: cần chênh 6 dB và đến trước (guard mặc định 0).
    capture_enabled: bool = True
    capture_db: float = 6.0
    capture_guard_s: float = 0.0
    relay_fraction: float = 0.5  # GIẢ ĐỊNH cho managed_flood
    trickle_i_min_s: float = 1.0
    trickle_i_max_s: float = 32.0
    trickle_k: int = 2
    # GIẢ ĐỊNH: cửa sổ backoff cỡ vài lần airtime để tránh đồng bộ tuyệt đối.
    flood_jitter_s: float = 2.0
    relay_jitter_s: float = 4.0
    seed: int = 0

    def __post_init__(self) -> None:
        """Kiểm tra tham số; ném ValueError với giá trị không hợp lệ."""
        if not (SF_MIN <= self.sf <= SF_MAX):
            raise ValueError(f"sf phải trong {SF_MIN}..{SF_MAX}, nhận {self.sf}")
        LoraProfile(sf=self.sf, bw_hz=self.bw_hz, cr=self.cr)  # kiểm tra bw, cr
        if self.n_nodes <= 0:
            raise ValueError(f"n_nodes phải dương, nhận {self.n_nodes}")
        if self.ttl <= 0:
            raise ValueError(f"ttl phải dương, nhận {self.ttl}")
        if self.area_m <= 0 or self.duration_s <= 0:
            raise ValueError("area_m và duration_s phải dương")
        if self.n_sos < 0 or self.sos_interval_s < 0 or self.cache_ttl_s < 0:
            raise ValueError("n_sos, sos_interval_s, cache_ttl_s không âm")
        if not (0.0 <= self.duty_cycle <= 1.0):
            raise ValueError("duty_cycle phải trong [0, 1]")
        if not (0 <= self.n_gateways <= 2):
            raise ValueError("n_gateways chỉ nhận 0, 1 hoặc 2")
        if self.n_couriers < 0:
            raise ValueError("n_couriers không âm")
        if self.link_pdr is not None and not (0.0 <= self.link_pdr <= 1.0):
            raise ValueError("link_pdr phải trong [0, 1] hoặc None")
        if self.margin_slope_db <= 0 or self.path_loss_exponent <= 0:
            raise ValueError("margin_slope_db và path_loss_exponent phải dương")
        if not (0.0 <= self.relay_fraction <= 1.0):
            raise ValueError("relay_fraction phải trong [0, 1]")
        if self.beacon_interval_s is not None and self.beacon_interval_s <= 0:
            raise ValueError("beacon_interval_s phải dương hoặc None")
        if self.gateway_outage is not None:
            t0, t1 = self.gateway_outage
            if t0 < 0 or t1 <= t0:
                raise ValueError("gateway_outage phải là (bắt đầu, kết thúc) hợp lệ")


#: Bộ cột số của kết quả, dùng chung cho `as_row` và thống kê summary.
RESULT_FIELDS = (
    "delivered", "pdr", "latency_p50", "latency_p95",
    "transmissions_per_delivered", "airtime_total_s", "airtime_control_s",
    "airtime_data_s", "control_airtime_ratio", "duplicate_ratio", "jain_fairness",
    "deferred_count", "collisions", "reconvergence_s", "total_transmissions",
    "data_transmissions", "control_transmissions", "total_sos", "n_nodes",
    "strategy", "seed", "duration_s",
)


@dataclass
class LoraSimResult:
    """Chỉ số một lần mô phỏng. Nhãn `SIM`, chưa hiệu chuẩn."""

    delivered: int
    pdr: float
    latency_p50: float
    latency_p95: float
    transmissions_per_delivered: float
    airtime_total_s: float
    airtime_control_s: float
    airtime_data_s: float
    control_airtime_ratio: float
    duplicate_ratio: float
    jain_fairness: float
    deferred_count: int
    collisions: int
    reconvergence_s: float
    per_source_delivered: dict
    total_transmissions: int
    data_transmissions: int
    control_transmissions: int
    total_sos: int
    n_nodes: int
    strategy: str
    seed: int
    duration_s: float

    def as_row(self) -> dict:
        """Bản phẳng để ghi CSV (đã kèm nhãn bằng chứng)."""
        row = {name: getattr(self, name) for name in RESULT_FIELDS}
        row["per_source_delivered"] = ";".join(
            f"{k}:{v}" for k, v in sorted(self.per_source_delivered.items())
        )
        row["evidence"] = EVIDENCE
        return row


def _logistic(x: float) -> float:
    """Hàm logistic chống tràn số cho đối số lớn."""
    if x < -700.0:
        return 0.0
    if x > 700.0:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def _percentile(values: list[float], q: float) -> float:
    """Phân vị nội suy tuyến tính; trả 0.0 khi rỗng (tránh NaN)."""
    if not values:
        return 0.0
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1.0 - (pos - lo)) + xs[hi] * (pos - lo)


def _jain_fairness(counts: list[int]) -> float:
    """Chỉ số Jain trong [0, 1]; quy ước 1.0 khi mọi giá trị bằng 0."""
    total = sum(counts)
    sq = sum(c * c for c in counts)
    if not counts or sq == 0:
        return 1.0
    return (total * total) / (len(counts) * sq)


def _stable_rank(*parts: object) -> float:
    """Rank tất định trong [0, 1) — không phụ thuộc PYTHONHASHSEED."""
    raw = "|".join(repr(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha1(raw).digest()[:4], "big") / 2 ** 32


@dataclass
class _Node:
    """Trạng thái một nút (thường, gateway hoặc courier)."""

    idx: int
    x: float
    y: float
    is_gateway: bool = False
    is_courier: bool = False
    hop_to_gateway: float = math.inf
    waypoint_x: float = 0.0
    waypoint_y: float = 0.0


@dataclass
class _Frame:
    """Một khung đang chiếm kênh trong `[t_start, t_end]`."""

    msg_id: tuple
    kind: str  # "sos" hoặc "beacon"
    source: int
    sender: int
    t_start: float
    t_end: float
    ttl_left: int
    hop_count: int
    sender_hop: float
    lost: bool = False


@dataclass
class _NodeState:
    """Bộ nhớ khử trùng lặp và trạng thái trickle của một nút."""

    cache: dict = field(default_factory=dict)  # msg_id -> thời điểm nhận lần đầu
    trickle_interval_s: float = 1.0
    trickle_count: int = 0


class _AirtimeLedger:
    """Ngân sách airtime trượt trong cửa sổ 1 giờ cho từng nút."""

    def __init__(self, window_s: float, cap_s: float) -> None:
        self.window_s = window_s
        self.cap_s = cap_s
        self._spent: dict[int, list[list[float]]] = {}

    def _prune(self, node: int, t: float) -> list[list[float]]:
        entries = self._spent.setdefault(node, [])
        cutoff = t - self.window_s
        drop = 0
        for entry in entries:
            if entry[0] > cutoff:
                break
            drop += 1
        if drop:
            del entries[:drop]
        return entries

    def can_spend(self, node: int, t: float, airtime_s: float) -> bool:
        """True nếu còn ngân sách cho khung này tại thời điểm t."""
        return sum(e[1] for e in self._prune(node, t)) + airtime_s <= self.cap_s + 1e-12

    def spend(self, node: int, t: float, airtime_s: float) -> None:
        """Ghi nhận airtime đã dùng (chỉ gọi sau khi `can_spend` đồng ý)."""
        self._prune(node, t).append([t, airtime_s])


class _Simulation:
    """Một lần chạy mô phỏng với cấu hình, chiến lược và seed cho trước."""

    def __init__(self, cfg: LoraSimConfig, strategy: str, seed: int) -> None:
        self.cfg = cfg
        self.strategy = strategy
        self.seed = seed
        self.rng = random.Random(seed)
        self.profile = LoraProfile(sf=cfg.sf, bw_hz=cfg.bw_hz, cr=cfg.cr)
        self.freq_hz = BAND_VN_920_923_HZ
        self.airtime_sos = self.profile.airtime_s(cfg.sos_payload_bytes)
        self.airtime_beacon = self.profile.airtime_s(cfg.beacon_payload_bytes)
        self._heap: list = []
        self._seq = 0
        self.airborne: list[_Frame] = []
        # Bộ đếm kết quả.
        self.transmissions = self.data_transmissions = self.control_transmissions = 0
        self.airtime_data = self.airtime_control = 0.0
        self.deferred = self.collisions = 0
        self.duplicate_receptions = self.data_receptions = self.suppressed = 0
        self.deliveries: list[tuple[float, int, tuple]] = []
        self.delivered_msgs: set = set()
        self.msg_gen: dict[tuple, float] = {}
        self.msg_source: dict[tuple, int] = {}
        self.sources: list[int] = []
        self._build_nodes()
        self._build_links()
        cap = cfg.duty_cycle * DUTY_WINDOW_S if cfg.duty_cycle_enabled else math.inf
        self.ledger = _AirtimeLedger(DUTY_WINDOW_S, cap)

    def _build_nodes(self) -> None:
        """Sinh vị trí: nút thường, rồi gateway, rồi courier (thứ tự cố định)."""
        cfg = self.cfg
        self.nodes: list[_Node] = [
            _Node(i, self.rng.uniform(0, cfg.area_m), self.rng.uniform(0, cfg.area_m))
            for i in range(cfg.n_nodes)
        ]
        for _ in range(cfg.n_gateways):
            self.nodes.append(_Node(
                len(self.nodes), self.rng.uniform(0, cfg.area_m),
                self.rng.uniform(0, cfg.area_m), is_gateway=True, hop_to_gateway=0.0,
            ))
        for _ in range(cfg.n_couriers):
            self.nodes.append(_Node(
                len(self.nodes), self.rng.uniform(0, cfg.area_m),
                self.rng.uniform(0, cfg.area_m), is_courier=True,
            ))
        self.n_total = len(self.nodes)
        for node in self.nodes:
            if node.is_courier:
                node.waypoint_x = self.rng.uniform(0, cfg.area_m)
                node.waypoint_y = self.rng.uniform(0, cfg.area_m)
        self.states = [_NodeState(trickle_interval_s=cfg.trickle_i_min_s) for _ in self.nodes]
        self.gateways = [n.idx for n in self.nodes if n.is_gateway]
        self.couriers = [n.idx for n in self.nodes if n.is_courier]

    def _build_links(self) -> None:
        """Ma trận khoảng cách, ma trận PDR và cường độ tham chiếu cho capture."""
        cfg = self.cfg
        n = self.n_total
        self.dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = math.hypot(self.nodes[i].x - self.nodes[j].x,
                               self.nodes[i].y - self.nodes[j].y)
                self.dist[i][j] = self.dist[j][i] = d
        self.pdr = [[0.0] * n for _ in range(n)]
        if cfg.link_pdr is not None:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        self.pdr[i][j] = cfg.link_pdr
        else:
            sens = self.profile.sensitivity_dbm()
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    margin = link_margin_db(max(self.dist[i][j], 1.0), self.freq_hz,
                                            cfg.path_loss_exponent, cfg.tx_dbm, sens)
                    self.pdr[i][j] = _logistic(
                        (margin - cfg.margin_50_db) / cfg.margin_slope_db)
        self.neighbors = [[j for j in range(n) if j != i and self.pdr[i][j] > 0.0]
                          for i in range(n)]
        # GIẢ ĐỊNH: đo cường độ capture tại gateway đầu tiên, hoặc tâm vùng.
        if self.gateways:
            rx, ry = self.nodes[self.gateways[0]].x, self.nodes[self.gateways[0]].y
        else:
            rx = ry = cfg.area_m / 2.0
        self.signal_ref = []
        for i in range(n):
            d = max(math.hypot(self.nodes[i].x - rx, self.nodes[i].y - ry), 1.0)
            pl = path_loss_log_distance_db(d, self.freq_hz, cfg.path_loss_exponent)
            self.signal_ref.append(cfg.tx_dbm - pl)

    def _schedule(self, t: float, kind: str, payload: object) -> None:
        self._seq += 1
        heapq.heappush(self._heap, (t, self._seq, kind, payload))

    def _in_outage(self, t: float) -> bool:
        """True nếu gateway đang trong khoảng sập."""
        outage = self.cfg.gateway_outage
        return outage is not None and outage[0] <= t <= outage[1]

    def _seed_events(self) -> None:
        """Xếp lịch beacon, SOS, courier cho cả kịch bản."""
        cfg = self.cfg
        if cfg.beacon_interval_s is not None:
            # GIẢ ĐỊNH: lệch pha ngẫu nhiên ban đầu để tránh bão beacon ở t=0.
            for node in self.nodes:
                t = self.rng.uniform(0.0, cfg.beacon_interval_s)
                while t <= cfg.duration_s:
                    self._schedule(t, "beacon", node.idx)
                    t += cfg.beacon_interval_s
        k = cfg.n_sos
        if k > 0:
            self.sources = (sorted(self.rng.sample(range(cfg.n_nodes), k)) if k <= cfg.n_nodes
                            else [i % cfg.n_nodes for i in range(k)])
        t0 = cfg.warmup_s if cfg.warm_start else 0.0
        for i, src in enumerate(self.sources):
            gen_t = t0 + i * cfg.sos_interval_s
            msg_id = ("sos", src, i)
            self.msg_gen[msg_id] = gen_t
            self.msg_source[msg_id] = src
            if gen_t <= cfg.duration_s:
                self._schedule(gen_t, "sos_gen", msg_id)
        for idx in self.couriers:
            t = 0.0
            while t <= cfg.duration_s:
                self._schedule(t, "courier_step", idx)
                t += cfg.courier_step_s

    def _mark_lost(self, frame: _Frame) -> None:
        if not frame.lost:
            frame.lost = True
            self.collisions += 1

    def _resolve_channel(self, new_frame: _Frame, t: float) -> None:
        """Giải va chạm khi khung mới bắt đầu chiếm kênh.

        Mọi khung đang hoạt động (`t_end > t`) đều chồng lấn với khung mới.
        Không capture ⇒ tất cả cùng mất. Có capture ⇒ khung đến trước đủ
        `capture_guard_s` và mạnh hơn mọi khung còn lại ≥ `capture_db` được giữ.
        """
        active = [f for f in self.airborne if f.t_end > t]
        if not active:
            return
        cfg = self.cfg
        if cfg.capture_enabled:
            guards = [f for f in active if (t - f.t_start) >= cfg.capture_guard_s]
            if guards:
                best = max(guards, key=lambda f: self.signal_ref[f.sender])
                best_sig = self.signal_ref[best.sender]
                others = [f for f in active if f is not best] + [new_frame]
                if all(best_sig - self.signal_ref[o.sender] >= cfg.capture_db
                       for o in others):
                    for f in active:
                        if f is not best:
                            self._mark_lost(f)
                    self._mark_lost(new_frame)
                    return
        for f in active:
            self._mark_lost(f)
        self._mark_lost(new_frame)

    def _start_tx(self, node_idx: int, msg_id: tuple, kind: str, t: float,
                  ttl_left: int, hop_count: int, sender_hop: float) -> bool:
        """Thử phát một khung; False nếu bị chặn bởi duty cycle hoặc thời gian."""
        cfg = self.cfg
        if t > cfg.duration_s:
            return False
        node = self.nodes[node_idx]
        if node.is_gateway and (kind == "sos" or self._in_outage(t)):
            return False  # gateway là điểm thu, không chuyển tiếp dữ liệu
        airtime = self.airtime_beacon if kind == "beacon" else self.airtime_sos
        if cfg.duty_cycle_enabled and not self.ledger.can_spend(node_idx, t, airtime):
            # GIẢ ĐỊNH: khung vượt ngân sách bị bỏ (không có hàng đợi bền)
            # nhưng vẫn được đếm vào `deferred_count`.
            self.deferred += 1
            return False
        self.ledger.spend(node_idx, t, airtime)
        # Dọn khung đã kết thúc: chúng không thể chồng lấn với tương lai.
        self.airborne = [f for f in self.airborne if f.t_end > t]
        frame = _Frame(msg_id, kind, node_idx if kind == "beacon" else msg_id[1],
                       node_idx, t, t + airtime, ttl_left, hop_count, sender_hop)
        self._resolve_channel(frame, t)
        self._schedule(frame.t_end, "rx", frame)
        self.airborne.append(frame)
        self.transmissions += 1
        if kind == "beacon":
            self.control_transmissions += 1
            self.airtime_control += airtime
        else:
            self.data_transmissions += 1
            self.airtime_data += airtime
        return True

    def _on_rx(self, frame: _Frame, t: float) -> None:
        """Xử lý khung đã phát xong: mất do va chạm hoặc giao cho từng nút thu."""
        if frame.lost:
            return
        for r in self.neighbors[frame.sender]:
            if self.nodes[r].is_gateway and self._in_outage(t):
                continue
            p = self.pdr[frame.sender][r]
            if p < 1.0 and self.rng.random() >= p:
                continue
            self._deliver(frame, r, t)

    def _deliver(self, frame: _Frame, r: int, t: float) -> None:
        """Giao khung cho nút thu r, hoặc ghi nhận nếu r là gateway."""
        if frame.kind == "beacon":
            cand = frame.sender_hop + 1.0
            if cand < self.nodes[r].hop_to_gateway:
                self.nodes[r].hop_to_gateway = cand
            return
        if self.nodes[r].is_gateway:
            if frame.msg_id not in self.delivered_msgs:
                self.delivered_msgs.add(frame.msg_id)
                self.deliveries.append((t, self.msg_source[frame.msg_id], frame.msg_id))
            return
        self.data_receptions += 1
        state = self.states[r]
        seen_at = state.cache.get(frame.msg_id)
        if seen_at is not None and (t - seen_at) <= self.cfg.cache_ttl_s:
            self.duplicate_receptions += 1
            if self.strategy == "trickle":
                self._trickle_note(r, relay=False)
            return
        state.cache[frame.msg_id] = t
        self._maybe_relay(r, frame, t)

    def _maybe_relay(self, node_idx: int, frame: _Frame, t: float) -> None:
        """Quyết định chuyển tiếp theo chiến lược đang chọn."""
        cfg = self.cfg
        if frame.ttl_left <= 1 or self.nodes[node_idx].is_gateway:
            return
        node = self.nodes[node_idx]
        if self.strategy == "flood":
            delay = self.rng.uniform(0.0, cfg.flood_jitter_s)
        elif self.strategy in ("managed_flood", "store_carry_forward"):
            if _stable_rank(node_idx, frame.msg_id, self.seed) >= cfg.relay_fraction:
                self.suppressed += 1
                return
            delay = self.rng.uniform(0.0, cfg.relay_jitter_s)
        elif self.strategy == "gradient":
            # GIẢ ĐỊNH: không chuyển tiếp khi chưa biết hướng (hop vô cực).
            if not (node.hop_to_gateway < frame.sender_hop):
                self.suppressed += 1
                return
            delay = self.rng.uniform(0.0, cfg.relay_jitter_s)
        else:  # trickle
            if not self._trickle_note(node_idx, relay=True):
                return
            delay = self.rng.uniform(0.0, self.states[node_idx].trickle_interval_s / 2.0)
        self._schedule(t + delay, "relay",
                       (node_idx, frame.msg_id, frame.ttl_left - 1,
                        frame.hop_count + 1, node.hop_to_gateway))

    def _trickle_note(self, node_idx: int, relay: bool) -> bool:
        """Cập nhật trickle; True nếu được phép xếp lịch phát lại."""
        cfg = self.cfg
        state = self.states[node_idx]
        state.trickle_count += 1
        if state.trickle_count >= cfg.trickle_k:
            # Đủ số lần nghe trùng ⇒ tăng khoảng trickle (doubling) và im lặng.
            state.trickle_count = 0
            state.trickle_interval_s = min(cfg.trickle_i_max_s,
                                           state.trickle_interval_s * 2.0)
            if relay:
                self.suppressed += 1
            return False
        return relay

    def _on_courier_step(self, idx: int, t: float) -> None:
        """Di chuyển courier và giao hàng đã mang khi vào tầm gateway."""
        cfg = self.cfg
        node = self.nodes[idx]
        step = cfg.courier_speed_m_s * cfg.courier_step_s
        dx, dy = node.waypoint_x - node.x, node.waypoint_y - node.y
        d = math.hypot(dx, dy)
        if d <= step or d == 0.0:
            node.x, node.y = node.waypoint_x, node.waypoint_y
            node.waypoint_x = self.rng.uniform(0, cfg.area_m)
            node.waypoint_y = self.rng.uniform(0, cfg.area_m)
        else:
            node.x, node.y = node.x + dx / d * step, node.y + dy / d * step
        for other in self.nodes:  # cập nhật khoảng cách sau khi di chuyển
            dd = math.hypot(node.x - other.x, node.y - other.y)
            self.dist[idx][other.idx] = self.dist[other.idx][idx] = dd
        for gw in self.gateways:
            if self._in_outage(t) or self.pdr[idx][gw] < 0.5:
                continue
            for msg_id, seen_at in list(self.states[idx].cache.items()):
                if msg_id in self.delivered_msgs or (t - seen_at) > cfg.cache_ttl_s:
                    continue
                self.delivered_msgs.add(msg_id)
                self.deliveries.append((t, self.msg_source[msg_id], msg_id))
        if t + cfg.courier_step_s <= cfg.duration_s:
            self._schedule(t + cfg.courier_step_s, "courier_step", idx)

    def run(self) -> LoraSimResult:
        """Chạy tới hết thời lượng mô phỏng rồi tổng hợp chỉ số."""
        cfg = self.cfg
        self._seed_events()
        horizon = cfg.duration_s + self.airtime_sos
        while self._heap:
            t, _, kind, payload = heapq.heappop(self._heap)
            if t > horizon:
                break
            if kind == "sos_gen":
                msg_id = payload
                self._start_tx(msg_id[1], msg_id, "sos", t, cfg.ttl, 0,
                               self.nodes[msg_id[1]].hop_to_gateway)
            elif kind == "beacon":
                self._start_tx(payload, ("beacon", payload, 0), "beacon", t, 1, 0,
                               self.nodes[payload].hop_to_gateway)
            elif kind == "relay":
                node_idx, msg_id, ttl_left, hop_count, sender_hop = payload
                self._start_tx(node_idx, msg_id, "sos", t, ttl_left, hop_count, sender_hop)
            elif kind == "rx":
                self._on_rx(payload, t)
            else:  # courier_step
                self._on_courier_step(payload, t)
        return self._summarise()

    def _summarise(self) -> LoraSimResult:
        """Tổng hợp chỉ số từ bộ đếm và danh sách giao hàng."""
        cfg = self.cfg
        delivered = len(self.delivered_msgs)
        per_source: dict[int, int] = {s: 0 for s in self.sources}
        for _t, src, _mid in self.deliveries:
            per_source[src] = per_source.get(src, 0) + 1
        latencies = [t - self.msg_gen[mid] for (t, _s, mid) in self.deliveries]
        airtime_total = self.airtime_control + self.airtime_data
        outage = cfg.gateway_outage
        reconvergence = 0.0
        if outage is not None:
            oend = outage[1]
            after = [t for (t, _s, _m) in self.deliveries if t >= oend]
            if after:
                reconvergence = min(after) - oend
            elif oend < cfg.duration_s:
                reconvergence = cfg.duration_s - oend
        return LoraSimResult(
            delivered=delivered,
            pdr=delivered / cfg.n_sos if cfg.n_sos else 0.0,
            latency_p50=_percentile(latencies, 0.50),
            latency_p95=_percentile(latencies, 0.95),
            transmissions_per_delivered=(self.data_transmissions / delivered
                                         if delivered else 0.0),
            airtime_total_s=airtime_total,
            airtime_control_s=self.airtime_control,
            airtime_data_s=self.airtime_data,
            control_airtime_ratio=(self.airtime_control / airtime_total
                                   if airtime_total > 0 else 0.0),
            duplicate_ratio=(self.duplicate_receptions / self.data_receptions
                             if self.data_receptions else 0.0),
            jain_fairness=_jain_fairness([per_source[s] for s in self.sources]),
            deferred_count=self.deferred,
            collisions=self.collisions,
            reconvergence_s=reconvergence,
            per_source_delivered={str(s): per_source[s] for s in self.sources},
            total_transmissions=self.transmissions,
            data_transmissions=self.data_transmissions,
            control_transmissions=self.control_transmissions,
            total_sos=cfg.n_sos,
            n_nodes=cfg.n_nodes,
            strategy=self.strategy,
            seed=self.seed,
            duration_s=cfg.duration_s,
        )


def simulate_once(cfg: LoraSimConfig, strategy: str, seed: int | None = None) -> LoraSimResult:
    """Mô phỏng một lần; cùng seed + cùng cfg cho kết quả bằng nhau từng trường."""
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy phải thuộc {STRATEGIES}, nhận {strategy!r}")
    return _Simulation(cfg, strategy, cfg.seed if seed is None else int(seed)).run()


#: Cấu hình nền cho ma trận CLI (mọi giá trị đều là tham số mô hình).
BASE_CELL: dict = {
    "area_m": 1000.0, "bw_hz": 125_000.0, "cr": 1, "beacon_interval_s": 60.0,
    "n_gateways": 1, "duration_s": 240.0, "sos_interval_s": 6.0, "warmup_s": 60.0,
    "capture_enabled": True, "capture_db": 6.0, "capture_guard_s": 0.0,
    "duty_cycle": 0.01, "duty_cycle_enabled": True, "ttl": 4,
}
CELL_KEYS = ("strategy", "n_nodes", "n_sos", "sf", "start_mode")
SUMMARY_METRICS = ("delivered", "pdr", "latency_p50", "latency_p95",
                   "transmissions_per_delivered", "airtime_total_s",
                   "airtime_control_s", "airtime_data_s", "control_airtime_ratio",
                   "duplicate_ratio", "jain_fairness", "deferred_count",
                   "collisions", "reconvergence_s", "total_transmissions",
                   "data_transmissions", "control_transmissions")


def _default_cells() -> list[dict]:
    """Ma trận 5 thuật toán × 3 mật độ × 2 tải × 2 SF × cold/warm = 120 ô."""
    return [
        {"strategy": strategy, "n_nodes": density, "n_sos": load, "sf": sf,
         "warm_start": warm}
        for strategy in STRATEGIES
        for density in (25, 50, 100)
        for load in (5, 20)
        for sf in (7, 9)
        for warm in (True, False)
    ]


def _cell_config(cell: dict) -> tuple[LoraSimConfig, str]:
    """Dựng `LoraSimConfig` từ một ô ma trận."""
    params = dict(BASE_CELL)
    params.update(cell)
    strategy = params.pop("strategy")
    params.setdefault("n_couriers",
                      3 if strategy == "store_carry_forward" else 0)
    return LoraSimConfig(**params), strategy


def run_matrix(seeds: Iterable[int] = range(20), cells: list[dict] | None = None,
               progress: bool = False) -> tuple[list[dict], list[dict]]:
    """Chạy ma trận mô phỏng, trả về `(raw, summary)`.

    `raw`: một dòng cho mỗi (ô, seed), đã kèm nhãn `evidence=SIM`.
    `summary`: một dòng cho mỗi ô, gồm trung bình và độ lệch chuẩn theo seed.
    """
    seed_list = [int(s) for s in seeds]
    raw_rows: list[dict] = []
    summary_rows: list[dict] = []
    for cell in (_default_cells() if cells is None else list(cells)):
        cfg, strategy = _cell_config(cell)
        label = {"strategy": strategy, "n_nodes": cfg.n_nodes, "n_sos": cfg.n_sos,
                 "sf": cfg.sf, "start_mode": "warm" if cfg.warm_start else "cold"}
        results = [simulate_once(cfg, strategy, seed=seed) for seed in seed_list]
        for seed, res in zip(seed_list, results):
            row = dict(label)
            row["seed"] = seed
            row.update(res.as_row())
            raw_rows.append(row)
        summary = dict(label)
        summary["n_seeds"] = len(seed_list)
        for metric in SUMMARY_METRICS:
            vals = [getattr(r, metric) for r in results]
            summary[f"mean_{metric}"] = statistics.fmean(vals)
            summary[f"std_{metric}"] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        summary["evidence"] = EVIDENCE
        summary_rows.append(summary)
        if progress:
            print(f"  [SIM] {label} × {len(seed_list)} seed")
    return raw_rows, summary_rows


def _write_csv(path: str, rows: list[dict]) -> None:
    """Ghi CSV với đúng bộ cột của dòng đầu (mọi dòng đều có `evidence`)."""
    if not rows:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _print_summary_table(summary_rows: list[dict]) -> None:
    """In bảng 5 thuật toán × cold/warm, mọi dòng đều ghi `evidence=SIM`."""
    print("=" * 100)
    print("BẢNG TÓM TẮT MÔ PHỎNG MẠNG LoRa — evidence=SIM, CHƯA HIỆU CHUẨN")
    print("Trung bình trên mọi mật độ/tải/SF và mọi seed trong ma trận.")
    print("=" * 100)
    header = (f"{'thuật toán':<20} | {'start':<5} | {'PDR':>6} | {'p50 ms':>8} | "
              f"{'p95 ms':>8} | {'tx/giao':>8} | {'ctl%':>6} | {'trùng%':>7} | "
              f"{'coll':>8} | {'hoãn':>7} | {'evidence':>8}")
    print(header)
    print("-" * len(header))
    for strategy in STRATEGIES:
        for mode in ("cold", "warm"):
            rows = [r for r in summary_rows
                    if r["strategy"] == strategy and r["start_mode"] == mode]
            if not rows:
                continue
            mean = lambda key: statistics.fmean(r[key] for r in rows)  # noqa: E731
            print(f"{strategy:<20} | {mode:<5} | {mean('mean_pdr'):6.3f} | "
                  f"{mean('mean_latency_p50') * 1000:8.1f} | "
                  f"{mean('mean_latency_p95') * 1000:8.1f} | "
                  f"{mean('mean_transmissions_per_delivered'):8.2f} | "
                  f"{mean('mean_control_airtime_ratio') * 100:6.2f} | "
                  f"{mean('mean_duplicate_ratio') * 100:7.2f} | "
                  f"{mean('mean_collisions'):8.1f} | "
                  f"{mean('mean_deferred_count'):7.1f} | {EVIDENCE:>8}")
    print("-" * len(header))
    print("GHI CHÚ: số liệu mô hình (SIM), phụ thuộc tham số GIẢ ĐỊNH; không phải ĐO.")
    print("=" * 100)


def main(argv: list[str] | None = None) -> int:
    """Điểm vào CLI: chạy ma trận, ghi CSV, in bảng tóm tắt."""
    parser = argparse.ArgumentParser(description="Mô phỏng mạng LoRa (SIM).")
    parser.add_argument("--seeds", type=int, default=20, help="số seed mỗi ô (mặc định 20)")
    parser.add_argument("--out-dir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "results"),
        help="thư mục ghi CSV (mặc định ../results)")
    parser.add_argument("--progress", action="store_true", help="in tiến độ từng ô")
    args = parser.parse_args(argv)
    print(f"[{EVIDENCE}] chạy ma trận 120 ô × {args.seeds} seed ...")
    raw_rows, summary_rows = run_matrix(seeds=range(args.seeds), progress=args.progress)
    raw_path = os.path.join(args.out_dir, "sim-lora-raw.csv")
    summary_path = os.path.join(args.out_dir, "sim-lora-summary.csv")
    _write_csv(raw_path, raw_rows)
    _write_csv(summary_path, summary_rows)
    print()
    _print_summary_table(summary_rows)
    print()
    print(f"[{EVIDENCE}] raw     : {os.path.abspath(raw_path)} ({len(raw_rows)} dòng)")
    print(f"[{EVIDENCE}] summary : {os.path.abspath(summary_path)} ({len(summary_rows)} dòng)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
