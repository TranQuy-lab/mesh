"""Mô phỏng nâng cao cho RescueMesh-AI — WP1.

Khác biệt so với ``sim.py`` (SIM-SMOKE):

- **Cache có thời hạn** theo spec 5 phút, không phải ``set`` vô hạn.
- **Nhiều SOS đồng thời** (1/5/20/50/100) với nguồn khác nhau.
- **Hàng đợi ưu tiên** SOS > BEACON/ACK > HEARTBEAT và **luân phiên theo nguồn**
  để một nguồn không chiếm toàn bộ kênh (fairness).
- **Collision** ở tầng radio: hai nút phát chồng lấn thời gian thì gói có thể hỏng.
- **Radio busy**: một nút không thu được khi chính nó đang phát.
- **Relay suppression**: nghe thấy bản sao cùng ``tag`` trong cửa sổ jitter thì huỷ lượt phát.
- **Beacon overhead** được đếm vào chi phí phát.
- **Route expiry**: gradient hết hạn sau N chu kỳ beacon khi trạm sập.

Đây vẫn là mô hình **chưa hiệu chuẩn** (chưa có số đo PDR thực từ WP4). Mọi bảng
sinh ra từ đây phải gắn nhãn ``SIM`` và không được dùng để tuyên bố hiệu năng
thực địa. Xem ``ke-hoach-nghien-cuu-rescuemesh-ai.md`` §10.2 và cổng G3.
"""

from __future__ import annotations

import hashlib
import math
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Literal

import simpy

Strategy = Literal[
    "flood",
    "trickle",
    "managed",
    "gradient",
    "gradient_scf",
]

ALL_STRATEGIES: tuple[Strategy, ...] = (
    "flood",
    "trickle",
    "managed",
    "gradient",
    "gradient_scf",
)

# Ưu tiên: số nhỏ = phục vụ trước.
PRIO_SOS = 0
PRIO_CONTROL = 1
PRIO_HEARTBEAT = 2

# Phải khớp ``packets.HOP_UNKNOWN``: 15 = chưa biết khoảng cách tới trạm.
HOP_UNKNOWN = 0xF
HOP_INFINITY = 10**9


@dataclass(frozen=True)
class SimConfig:
    """Tham số mô hình.

    Mọi giá trị ở đây là **biến thí nghiệm**, không phải kết quả. Các mặc định
    được chọn để tái hiện đúng hành vi của ``sim.py`` cũ ở chế độ một SOS.
    """

    n_nodes: int = 50
    area_m: float = 200.0
    range_m: float = 55.0
    link_pdr: float = 0.85
    ttl: int = 15
    jitter_min_s: float = 0.010
    jitter_max_s: float = 0.220
    trickle_k: int = 3
    horizon_s: float = 10.0

    # --- v2: cache, tải, radio, beacon, hàng đợi ---
    cache_ttl_s: float = 300.0
    n_sos: int = 1
    collision_model: bool = True
    tx_duration_s: float = 0.003
    radio_busy_s: float = 0.005
    beacon_interval_s: float = 30.0
    beacon_start_offset_s: float = 0.0
    route_expiry_beacons: int = 3
    # Cho phép tắt hết hạn tuyến trong khi beacon vẫn chạy. Đây là nhánh đối
    # chứng bắt buộc của H3: cùng topology, cùng beacon, chỉ khác việc nút có
    # quên tuyến cũ sau khi trạm sập hay không.
    route_expiry_enabled: bool = True
    # Chọn relay cho beacon: nút relay khi ``hop % stride == 0``. 1 = mọi nút
    # relay (chỉ dùng cho topology nhỏ); giá trị lớn hơn giữ chi phí tuyến tính.
    beacon_relay_stride: int = 2
    station_down_after_s: float | None = None
    # Trạm hồi phục tại mốc này (beacon trở lại, trạm nhận lại). Dùng để đo
    # THỜI GIAN TÁI HỘI TỤ của H3: khi trạm sập thì không gói nào tới đích nên
    # PDR = 0 ở mọi nhánh, và PDR không phân biệt được tuyến còn hay mất.
    station_recover_after_s: float | None = None
    # Mốc thời gian bắt đầu đếm ``delivered_after_recovery``. Phải là mốc cố
    # định cho MỌI nhánh, kể cả nhánh trạm không sập, nếu không thì không so
    # sánh được giữa các nhánh.
    measure_after_s: float | None = None
    queue_capacity: int = 32
    service_interval_s: float = 0.020
    allow_duplicate_forward: bool = True
    heartbeat_interval_s: float = 60.0
    # Thời gian chờ trước khi nguồn phát SOS. 0 = cold start (beacon và SOS cùng
    # lúc, gradient chưa hội tụ). > vài chu kỳ beacon = warm start (gradient đã
    # ổn định). Phải khai báo rõ trong mọi bảng vì hai chế độ cho kết quả khác
    # nhau về bản chất, không phải khác nhau về nhiễu.
    warmup_s: float = 0.0

    def __post_init__(self) -> None:
        if self.n_nodes < 2:
            raise ValueError("n_nodes phải >= 2")
        if not 0.0 <= self.link_pdr <= 1.0:
            raise ValueError("link_pdr phải trong [0, 1]")
        if self.ttl < 0:
            raise ValueError("ttl phải >= 0")
        if self.n_sos < 1:
            raise ValueError("n_sos phải >= 1")
        if self.jitter_min_s < 0 or self.jitter_max_s < self.jitter_min_s:
            raise ValueError("cửa sổ jitter không hợp lệ")
        if self.cache_ttl_s <= 0:
            raise ValueError("cache_ttl_s phải > 0")


@dataclass
class SimResult:
    strategy: Strategy
    seed: int
    n_nodes: int
    n_sos: int
    sources: tuple[int, ...]

    # Giao nhận
    delivered_sources: int
    pdr: float
    # Số SOS tới trạm SAU khi trạm hồi phục. Chỉ số chính cho H3: khi trạm sập
    # thì PDR = 0 ở mọi nhánh, nên PDR không phân biệt được tuyến còn hay mất.
    delivered_after_recovery: int
    latency_p50: float | None
    latency_p95: float | None
    latency_p99: float | None

    # Chi phí
    transmissions: int
    receptions: int
    collisions: int
    dropped_queue_full: int
    dropped_ttl: int
    dropped_duplicate: int
    dropped_no_route: int
    tx_per_delivered_sos: float
    beacon_transmissions: int

    # Cấu trúc
    jain_fairness: float
    max_queue_occupancy: int
    queue_drain_s: float | None
    copies_per_sos: float


# --------------------------------------------------------------------------
# Topology
# --------------------------------------------------------------------------


def random_geometric_graph(
    cfg: SimConfig, seed: int
) -> tuple[list[tuple[float, float]], list[set[int]]]:
    """Trạm ở tâm; các nút phân bố đều. Cạnh khi khoảng cách <= range_m."""
    rng = random.Random(seed)
    points = [(cfg.area_m / 2, cfg.area_m / 2)]
    points += [
        (rng.uniform(0, cfg.area_m), rng.uniform(0, cfg.area_m))
        for _ in range(cfg.n_nodes - 1)
    ]
    graph = [set() for _ in points]
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if math.dist(points[i], points[j]) <= cfg.range_m:
                graph[i].add(j)
                graph[j].add(i)
    return points, graph


def line_graph(n: int) -> list[set[int]]:
    graph = [set() for _ in range(n)]
    for i in range(n - 1):
        graph[i].add(i + 1)
        graph[i + 1].add(i)
    return graph


def hop_gradient(graph: list[set[int]], station: int = 0) -> list[int]:
    """BFS từ trạm. ``10**9`` nghĩa là không có đường tới trạm."""
    hops = [10**9] * len(graph)
    if not graph:
        return hops
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


# --------------------------------------------------------------------------
# Hàng đợi ưu tiên có luân phiên theo nguồn
# --------------------------------------------------------------------------


@dataclass(order=True)
class QueueItem:
    priority: int
    seq: int
    source: int = field(compare=False)
    node: int = field(compare=False)
    ttl: int = field(compare=False)
    sender_hop: int = field(compare=False)
    packet_tag: int = field(compare=False)


class FairPriorityQueue:
    """Hàng đợi ưu tiên + round-robin theo nguồn bên trong cùng mức ưu tiên.

    Spec yêu cầu (``thiet-ke-he-thong-chi-tiet.md`` §6.4 điểm 5) rằng hàng đợi
    phải phục vụ lần lượt các nguồn khác nhau. Nếu chỉ sắp theo ``priority``,
    100 SOS cùng mức sẽ tranh nhau và một nguồn phát dày có thể đè các nguồn
    khác. Round-robin theo ``source`` trong từng mức ưu tiên sửa điểm đó.
    """

    def __init__(self) -> None:
        self._buckets: dict[int, deque[QueueItem]] = {}
        self._order: deque[int] = deque()
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def push(self, item: QueueItem) -> None:
        bucket = self._buckets.setdefault(item.priority, deque())
        already = any(existing.source == item.source for existing in bucket)
        bucket.append(item)
        self._size += 1
        if not already:
            # Chèn nguồn mới vào sau các nguồn đang chờ ở cùng mức ưu tiên.
            self._order.append(item.priority)

    def pop(self) -> QueueItem | None:
        """Lấy item ưu tiên cao nhất, luân phiên nguồn trong cùng mức."""
        if self._size == 0:
            return None
        for priority in sorted(self._buckets):
            bucket = self._buckets[priority]
            while bucket:
                item = bucket.popleft()
                self._size -= 1
                if not any(x.source == item.source for x in bucket):
                    try:
                        self._order.remove(priority)
                    except ValueError:
                        pass
                return item
        return None


def jain_fairness(values: list[float]) -> float:
    """Chỉ số Jain. 1.0 = công bằng hoàn hảo; 1/n = một nguồn chiếm hết."""
    if not values:
        return 1.0
    total = sum(values)
    if total <= 0:
        return 1.0
    squared = sum(v * v for v in values)
    return (total * total) / (len(values) * squared)


# --------------------------------------------------------------------------
# Mô phỏng chính
# --------------------------------------------------------------------------


def simulate(
    cfg: SimConfig,
    strategy: Strategy,
    seed: int,
    sources: tuple[int, ...] | None = None,
    graph: list[set[int]] | None = None,
) -> SimResult:
    """Chạy một replication nhiều SOS trên một topology.

    Đơn vị thời gian là giây. Kết thúc ở ``cfg.horizon_s``.
    """
    if strategy not in ALL_STRATEGIES:
        raise ValueError(f"strategy không hợp lệ: {strategy}")

    if graph is None:
        _, graph = random_geometric_graph(cfg, seed)
    if len(graph) != cfg.n_nodes:
        raise ValueError("graph không khớp n_nodes")

    hops = hop_gradient(graph)

    rng = random.Random(seed * 7919 + 13)
    if sources is None:
        # Ưu tiên nút CÓ đường tới trạm (kịch bản quan tâm), nhưng nếu không đủ
        # thì lấy thêm nút bị cô lập: trong thực tế nút cô lập vẫn phát SOS vì nó
        # không biết mình không có tuyến. Đây là hành vi đúng, không phải lỗi.
        reachable = [n for n in range(1, cfg.n_nodes) if hops[n] < 10**9]
        isolated = [n for n in range(1, cfg.n_nodes) if hops[n] >= 10**9]
        candidates = reachable + isolated
        take = min(cfg.n_sos, len(candidates))
        sources = tuple(sorted(rng.sample(candidates, take)))
    if len(sources) != cfg.n_sos:
        raise ValueError(
            f"số nguồn không khớp n_sos: cần {cfg.n_sos}, nhận {len(sources)}"
        )
    if any(s == 0 for s in sources):
        raise ValueError("nguồn không được là trạm")

    env = simpy.Environment()

    # --- Trạng thái ---
    # Cache có thời hạn: tag -> thời điểm hết hạn.
    cache: list[dict[int, float]] = [dict() for _ in graph]
    queue = FairPriorityQueue()
    queue_seq = 0
    max_queue_occupancy = 0
    queue_left_at: float | None = None

    tx_attempt = [0] * len(graph)
    node_busy_until = [0.0] * len(graph)
    scheduled_tags: list[set[int]] = [set() for _ in graph]

    transmissions = 0
    receptions = 0
    collisions = 0
    beacon_transmissions = 0
    dropped_queue_full = 0
    dropped_ttl = 0
    dropped_duplicate = 0
    dropped_no_route = 0

    copies: dict[int, int] = {s: 0 for s in sources}
    delivered: dict[int, float] = {}
    delivered_after_recovery = 0
    # Mốc đo "sau hồi phục" là một mốc THỜI GIAN cố định, không phụ thuộc việc
    # trạm có sập hay không. Nếu gắn nó vào ``station_recover_after_s`` thì nhánh
    # đối chứng (trạm không sập) sẽ không bao giờ đếm được gì, và phép so sánh
    # A/B với C/D trở nên vô nghĩa.
    recovery_time = cfg.measure_after_s
    service_busy = {"value": False}

    station_up = {"value": True}

    # --- Cache ---
    def cache_has(node: int, tag: int) -> bool:
        expiry = cache[node].get(tag)
        if expiry is None:
            return False
        if env.now >= expiry:
            del cache[node][tag]
            return False
        return True

    def cache_put(node: int, tag: int) -> None:
        cache[node][tag] = env.now + cfg.cache_ttl_s

    # --- Gradient có hết hạn tuyến (route expiry) ---
    # ``hops`` tĩnh ở trên là chân lý topology; ``route_hop`` là cái nút THỰC SỰ
    # biết, chỉ được cập nhật khi nghe beacon. Nếu beacon ngừng tới quá
    # ``route_expiry_s``, nút quên tuyến -> mô phỏng "bóng ma đường" của H3.
    route_hop = [10**9] * len(graph)
    route_updated_at = [float("-inf")] * len(graph)
    last_beacon_relay = [float("-inf")] * len(graph)
    route_expiry_s = max(cfg.beacon_interval_s, 1e-9) * cfg.route_expiry_beacons
    # Bật/tắt hết hạn tuyến ĐỘC LẬP với việc có beacon hay không. Nhánh đối
    # chứng của H3 cần beacon chạy bình thường (để gradient hội tụ) nhưng nút
    # KHÔNG quên tuyến khi beacon ngừng tới.
    route_expiry_enabled = cfg.route_expiry_enabled and cfg.beacon_interval_s < 1e8

    def known_hop(node: int) -> int:
        if not route_expiry_enabled:
            return hops[node]
        if env.now - route_updated_at[node] > route_expiry_s:
            return 10**9
        return route_hop[node]

    def beacon_heard(node: int, beacon_hop: int) -> None:
        candidate = beacon_hop + 1
        if candidate < route_hop[node]:
            route_hop[node] = candidate
        route_updated_at[node] = env.now

    # Trạm luôn biết mình là gốc.
    route_hop[0] = 0
    route_updated_at[0] = float("inf")

    # --- Radio ---
    def link_ok(sender: int, receiver: int, attempt: int, tag: int) -> bool:
        return _uniform(seed, "link", sender, receiver, tag, attempt) < cfg.link_pdr

    def jitter(node: int, tag: int) -> float:
        u = _uniform(seed, "jitter", node, tag)
        return cfg.jitter_min_s + u * (cfg.jitter_max_s - cfg.jitter_min_s)

    def broadcast(sender: int, tag: int, packet_ttl: int, sender_hop: int, is_beacon: bool = False):
        """Phát một gói. Trả về generator để simpy lên lịch."""
        nonlocal transmissions, receptions, collisions, beacon_transmissions

        if node_busy_until[sender] > env.now:
            # Radio đang bận: mô hình hoá như mất lượt phát này.
            return
        attempt = tx_attempt[sender]
        tx_attempt[sender] += 1
        transmissions += 1
        if is_beacon:
            beacon_transmissions += 1

        start = env.now
        node_busy_until[sender] = start + cfg.tx_duration_s

        # Radio busy: nút đang phát thì không thu.
        for receiver in sorted(graph[sender]):
            if cfg.collision_model and node_busy_until[receiver] > start:
                collisions += 1
                continue
            if link_ok(sender, receiver, attempt, tag):
                receptions += 1
                env.process(receive(receiver, sender, tag, packet_ttl, sender_hop, is_beacon))
        yield env.timeout(0)

    # --- Giao nhận ---
    def receive(node: int, sender: int, tag: int, packet_ttl: int, sender_hop: int, is_beacon: bool):
        nonlocal dropped_duplicate, dropped_ttl, dropped_no_route
        nonlocal delivered_after_recovery

        if node_busy_until[node] > env.now - cfg.tx_duration_s and node_busy_until[node] > env.now:
            return  # đang phát, không thu

        if is_beacon:
            # Beacon cập nhật gradient rồi được relay tiếp ra ngoài.
            #
            # Relay theo CHU KỲ, không chỉ lần đầu: nếu chỉ relay khi hop được
            # cải thiện thì mỗi nút chỉ phát beacon đúng một lần trong đời, và
            # các nút ở xa (hoặc vào mạng muộn) vĩnh viễn không có tuyến. Beacon
            # trong thiết kế §4.4 được phát định kỳ; ở đây ta relay mỗi khi nhận
            # một beacon mới, dùng ``bseq`` để tránh relay lại cùng một beacon.
            beacon_heard(node, sender_hop)
            if node != 0:
                env.process(beacon_relay(node, sender_hop))
            yield env.timeout(0)
            return

        if cache_has(node, tag):
            dropped_duplicate += 1
            return
        cache_put(node, tag)

        if node == 0:
            # Trạm sập nghĩa là KHÔNG nhận được nữa, không chỉ ngừng phát beacon.
            if station_up["value"] and tag not in delivered:
                delivered[tag] = env.now
                if recovery_time is not None and env.now >= recovery_time:
                    delivered_after_recovery += 1
            return

        if packet_ttl <= 0:
            dropped_ttl += 1
            return

        if strategy in ("gradient", "gradient_scf"):
            my_hop = known_hop(node)
            if my_hop >= 10**9:
                dropped_no_route += 1
                if strategy == "gradient_scf":
                    schedule(node, tag, packet_ttl, sender_hop)
                return
            if not my_hop < sender_hop:
                # Không tốt hơn người gửi: chỉ store-carry-forward mới giữ lại.
                if strategy == "gradient_scf":
                    dropped_no_route += 1
                    schedule(node, tag, packet_ttl, sender_hop)
                return

        schedule(node, tag, packet_ttl, sender_hop)
        yield env.timeout(0)

    def schedule(node: int, tag: int, packet_ttl: int, sender_hop: int) -> None:
        nonlocal queue_seq, max_queue_occupancy, queue_left_at, dropped_queue_full
        if len(queue) >= cfg.queue_capacity:
            dropped_queue_full += 1
            return
        queue_seq += 1
        item = QueueItem(
            priority=PRIO_SOS,
            seq=queue_seq,
            source=tag,
            node=node,
            ttl=packet_ttl,
            sender_hop=sender_hop,
            packet_tag=tag,
        )
        queue.push(item)
        if len(queue) > max_queue_occupancy:
            max_queue_occupancy = len(queue)
        queue_left_at = None

    # --- Jitter + suppression ---
    def forward_after_jitter(node: int, tag: int, packet_ttl: int, sender_hop: int):
        """Đợi jitter; nếu nghe bản sao cùng tag thì huỷ lượt phát."""
        yield env.timeout(jitter(node, tag))

        if strategy == "trickle":
            # Trickle: đủ k bản sao thì im lặng.
            pass

        if tag in scheduled_tags[node]:
            return
        scheduled_tags[node].add(tag)
        copies[tag] = copies.get(tag, 0) + 1
        relay_hop = known_hop(node)
        yield env.process(broadcast(node, tag, packet_ttl - 1,
                                    relay_hop if relay_hop < 10**9 else sender_hop))

    # --- Beacon ---
    def beacon_loop() -> None:
        if cfg.beacon_interval_s >= 1e8:
            return  # beacon tắt cho thí nghiệm đối chứng không có control plane
        yield env.timeout(cfg.beacon_start_offset_s)
        while True:
            if cfg.station_down_after_s is not None and env.now >= cfg.station_down_after_s:
                station_up["value"] = False
            if (cfg.station_recover_after_s is not None
                    and env.now >= cfg.station_recover_after_s):
                station_up["value"] = True
            if station_up["value"]:
                yield env.process(broadcast(0, -1, cfg.ttl, 0, is_beacon=True))
            yield env.timeout(cfg.beacon_interval_s)

    def beacon_relay(node: int, sender_hop: int) -> None:
        """Relay phát lại beacon để gradient lan ra ngoài tầm trạm.

        Chỉ một tập relay **được chọn** phát lại, đúng như thiết kế §6.4 điểm 1
        ("chỉ cho các relay được chọn phát lại", "relay được chọn theo
        rank/khả năng pin"). Nếu mọi nút đều relay mỗi chu kỳ thì chi phí beacon
        là O(n²) và mô phỏng không còn phản ánh thiết kế.

        Luật chọn ở đây: nút relay khi **chỉ số nút** chia hết cho
        ``beacon_relay_stride``. Không được chọn theo ``hop``: nếu chọn theo hop
        thì các hop lẻ bị bỏ qua và beacon đứt ngay từ tầng đầu (đã kiểm chứng —
        stride=2 theo hop làm PDR về 0 vì nút hop 1 không relay).
        """
        yield env.timeout(jitter(node, -1))
        my_hop = known_hop(node)
        if my_hop >= 10**9:
            return
        if cfg.beacon_relay_stride > 1 and (node % cfg.beacon_relay_stride) != 0:
            return
        # Cửa sổ chống trùng: mỗi nút relay tối đa một lần mỗi chu kỳ beacon.
        if env.now - last_beacon_relay[node] < cfg.beacon_interval_s * 0.5:
            return
        last_beacon_relay[node] = env.now
        yield env.process(broadcast(node, -1, cfg.ttl, my_hop, is_beacon=True))

    # --- Nguồn phát SOS ---
    def source_emit(source: int, tag: int) -> None:
        cache_put(source, tag)
        if cfg.warmup_s > 0:
            yield env.timeout(cfg.warmup_s)
        # Nguồn phát với hop CHƯA BIẾT (HOP_UNKNOWN=15) để mọi hàng xóm gần trạm
        # hơn đều thoả ``my_hop < packet_hop`` và được phép relay.
        #
        # LƯU Ý THIẾT KẾ (phát hiện WP3): nếu nguồn CHƯA có tuyến (beacon chưa
        # lan tới, ``known_hop`` = inf), thì bản thân nguồn không cần tuyến để
        # phát — nó phát broadcast. Nhưng các hàng xóm cũng phải đã biết tuyến
        # thì mới relay được. Vì vậy ``beacon_start_offset_s`` và thời điểm phát
        # SOS quyết định mạng có "ấm" hay không. Thí nghiệm phải chạy cả hai chế
        # độ: cold start (SOS ở t=0, beacon đồng thời) và warm start (SOS sau khi
        # gradient đã hội tụ). Đây chính là nội dung H2/H3 cần phân biệt.
        yield env.process(broadcast(source, tag, cfg.ttl, HOP_UNKNOWN))

    env.process(beacon_loop())
    for tag, source in enumerate(sources, start=1):
        env.process(source_emit(source, tag))

    # Bộ phục vụ hàng đợi: lấy item ra và chuyển tiếp.
    def server() -> None:
        while True:
            item = queue.pop()
            if item is None:
                yield env.timeout(cfg.service_interval_s)
                continue
            env.process(forward_after_jitter(item.node, item.packet_tag, item.ttl, item.sender_hop))
            yield env.timeout(cfg.service_interval_s)

    env.process(server())
    env.run(until=cfg.horizon_s)

    # --- Tổng hợp ---
    latencies = sorted(delivered.values())
    n_delivered = len(latencies)
    pdr = n_delivered / cfg.n_sos if cfg.n_sos else 0.0

    def percentile(values: list[float], q: float) -> float | None:
        if not values:
            return None
        idx = min(len(values) - 1, max(0, math.ceil(q * len(values)) - 1))
        return values[idx]

    copies_list = [copies.get(t, 0) for t in range(1, cfg.n_sos + 1)]
    total_copies = sum(copies_list)
    fairness = jain_fairness([float(c) for c in copies_list]) if copies_list else 1.0

    tx_per_sos = transmissions / n_delivered if n_delivered else float("inf")

    return SimResult(
        strategy=strategy,
        seed=seed,
        n_nodes=cfg.n_nodes,
        n_sos=cfg.n_sos,
        sources=sources,
        delivered_sources=n_delivered,
        pdr=pdr,
        delivered_after_recovery=delivered_after_recovery,
        latency_p50=percentile(latencies, 0.50),
        latency_p95=percentile(latencies, 0.95),
        latency_p99=percentile(latencies, 0.99),
        transmissions=transmissions,
        receptions=receptions,
        collisions=collisions,
        dropped_queue_full=dropped_queue_full,
        dropped_ttl=dropped_ttl,
        dropped_duplicate=dropped_duplicate,
        dropped_no_route=dropped_no_route,
        tx_per_delivered_sos=tx_per_sos,
        beacon_transmissions=beacon_transmissions,
        jain_fairness=fairness,
        max_queue_occupancy=max_queue_occupancy,
        queue_drain_s=queue_left_at,
        copies_per_sos=(total_copies / cfg.n_sos) if cfg.n_sos else 0.0,
    )


def simulate_once(
    cfg: SimConfig,
    strategy: Strategy,
    seed: int,
    source: int | None = None,
    graph: list[set[int]] | None = None,
) -> SimResult:
    """Tương thích ngược với ``sim.simulate_once`` cho trường hợp một SOS."""
    sources = None if source is None else (source,)
    return simulate(cfg, strategy, seed, sources=sources, graph=graph)


__all__ = [
    "ALL_STRATEGIES",
    "FairPriorityQueue",
    "QueueItem",
    "SimConfig",
    "SimResult",
    "hop_gradient",
    "jain_fairness",
    "line_graph",
    "random_geometric_graph",
    "simulate",
    "simulate_once",
]
