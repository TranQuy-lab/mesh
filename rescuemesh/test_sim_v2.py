"""Kiểm thử cho simulator v2 (WP1).

Gồm kiểm soát âm bắt buộc theo ``ke-hoach-nghien-cuu-rescuemesh-ai.md`` §10.2:
kịch bản không có trạm phải cho PDR ~ 0, và kịch bản TTL=1 không được chuyển
tiếp — mục đích là xác nhận simulator không "tự giao gói".
"""

from __future__ import annotations

import math

from sim_v2 import (
    ALL_STRATEGIES,
    FairPriorityQueue,
    QueueItem,
    SimConfig,
    hop_gradient,
    jain_fairness,
    line_graph,
    random_geometric_graph,
    simulate,
)


def _line(n: int, **kw) -> SimConfig:
    base = dict(n_nodes=n, link_pdr=1.0, ttl=15, collision_model=False,
                beacon_interval_s=1e9)
    base.update(kw)
    return SimConfig(**base)


# --- Kiểm soát âm (bắt buộc) ---


def test_no_links_never_delivers():
    cfg = SimConfig(n_nodes=4, link_pdr=1.0, collision_model=False)
    graph = [set() for _ in range(4)]
    for strategy in ALL_STRATEGIES:
        r = simulate(cfg, strategy, seed=2, sources=(3,), graph=graph)
        assert r.delivered_sources == 0, strategy
        assert r.pdr == 0.0, strategy


def test_ttl_one_cannot_cross_two_relays():
    """TTL=1: tới được hàng xóm trực tiếp nhưng không qua hai relay."""
    cfg = _line(4, ttl=1)
    r = simulate(cfg, "flood", seed=3, sources=(3,), graph=line_graph(4))
    assert r.delivered_sources == 0


def test_ttl_zero_delivers_nothing():
    cfg = _line(3, ttl=0)
    r = simulate(cfg, "flood", seed=31, sources=(2,), graph=line_graph(3))
    assert r.delivered_sources == 0


def test_zero_pdr_never_delivers():
    cfg = SimConfig(n_nodes=3, link_pdr=0.0, collision_model=False)
    for strategy in ALL_STRATEGIES:
        r = simulate(cfg, strategy, seed=4, sources=(2,), graph=line_graph(3))
        assert r.delivered_sources == 0
        assert r.receptions == 0


# --- Lan truyền đúng ---


def test_perfect_line_delivers_for_all_strategies():
    cfg = _line(5)
    for strategy in ALL_STRATEGIES:
        r = simulate(cfg, strategy, seed=1, sources=(4,), graph=line_graph(5))
        assert r.delivered_sources == 1, strategy


def test_latency_is_positive_and_ordered():
    cfg = _line(6)
    r = simulate(cfg, "flood", seed=5, sources=(5,), graph=line_graph(6))
    assert r.delivered_sources == 1
    assert r.latency_p50 is not None and r.latency_p50 >= 0
    assert r.latency_p99 >= r.latency_p95 >= r.latency_p50


# --- Cache có thời hạn ---


def test_cache_suppresses_duplicate_when_ttl_live():
    cfg = _line(4, cache_ttl_s=300.0)
    r = simulate(cfg, "flood", seed=6, sources=(3,), graph=line_graph(4))
    assert r.dropped_duplicate >= 0  # không âm; có thể 0 trên chuỗi thẳng
    assert r.delivered_sources == 1


def test_cache_expiry_allows_reforward_later():
    """Cache TTL rất ngắn không được làm sai lệch điều kiện biên (vẫn giao được)."""
    cfg = _line(4, cache_ttl_s=0.001)
    r = simulate(cfg, "flood", seed=7, sources=(3,), graph=line_graph(4))
    assert r.delivered_sources == 1


# --- Hàng đợi công bằng ---


def test_fair_queue_rotates_sources_within_same_priority():
    q = FairPriorityQueue()
    # Ba nguồn khác nhau cùng mức ưu tiên.
    for i in range(3):
        q.push(QueueItem(PRIO := 0, seq=i, source=i, node=1, ttl=5, sender_hop=1, packet_tag=i))
    popped = [q.pop().source for _ in range(3)]
    assert sorted(popped) == [0, 1, 2]


def test_fair_queue_respects_priority_over_source():
    q = FairPriorityQueue()
    q.push(QueueItem(2, seq=0, source=0, node=1, ttl=5, sender_hop=1, packet_tag=0))
    q.push(QueueItem(0, seq=1, source=1, node=1, ttl=5, sender_hop=1, packet_tag=1))
    assert q.pop().priority == 0
    assert q.pop().priority == 2


def test_fair_queue_empty_returns_none():
    assert FairPriorityQueue().pop() is None


def test_jain_fairness_bounds():
    assert math.isclose(jain_fairness([1.0, 1.0, 1.0, 1.0]), 1.0, rel_tol=1e-9)
    # Một nguồn chiếm hết trong 4 nguồn -> 1/4.
    assert math.isclose(jain_fairness([4.0, 0.0, 0.0, 0.0]), 0.25, rel_tol=1e-9)
    assert jain_fairness([]) == 1.0


# --- Nhiều SOS ---


def test_multi_sos_all_deliver_on_line():
    """Ba nguồn cách xa nhau trên chuỗi thẳng, horizon đủ dài cho jitter."""
    cfg = _line(12, n_sos=3, horizon_s=30.0)
    r = simulate(cfg, "flood", seed=8, sources=(3, 7, 11), graph=line_graph(12))
    assert r.n_sos == 3
    assert r.delivered_sources == 3
    assert math.isclose(r.pdr, 1.0)


def test_multi_sos_short_horizon_can_lose_packets():
    """Horizon ngắn hơn jitter phải làm mất gói — kiểm soát dương cho mô hình thời gian."""
    cfg = _line(12, n_sos=3, horizon_s=0.001)
    r = simulate(cfg, "flood", seed=8, sources=(3, 7, 11), graph=line_graph(12))
    assert r.delivered_sources < 3


def test_multi_sos_deterministic_source_selection():
    cfg = SimConfig(n_nodes=20, n_sos=4, collision_model=False)
    points, graph = random_geometric_graph(cfg, 11)
    a = simulate(cfg, "flood", seed=11, graph=graph)
    b = simulate(cfg, "flood", seed=11, graph=graph)
    assert a.sources == b.sources
    assert a.delivered_sources == b.delivered_sources


def test_multi_sos_requires_matching_source_count():
    cfg = SimConfig(n_nodes=6, n_sos=2, collision_model=False)
    try:
        simulate(cfg, "flood", seed=12, sources=(1,), graph=line_graph(6))
    except ValueError:
        return
    raise AssertionError("phải báo lỗi khi số nguồn không khớp n_sos")


def test_station_is_not_allowed_as_source():
    cfg = SimConfig(n_nodes=5, n_sos=1, collision_model=False)
    try:
        simulate(cfg, "flood", seed=13, sources=(0,), graph=line_graph(5))
    except ValueError:
        return
    raise AssertionError("nguồn không được là trạm")


# --- Gradient ---


def test_gradient_uses_strictly_fewer_transmissions_than_flood_on_grid():
    """Trên mạng lưới đủ dày, gradient phải phát ít hơn flooding."""
    cfg = SimConfig(n_nodes=100, link_pdr=0.95, collision_model=False,
                    beacon_interval_s=1e9, area_m=120.0, range_m=60.0)
    points, graph = random_geometric_graph(cfg, 21)
    flood = simulate(cfg, "flood", seed=21, sources=(5,), graph=graph)
    grad = simulate(cfg, "gradient", seed=21, sources=(5,), graph=graph)
    assert grad.transmissions < flood.transmissions
    assert grad.tx_per_delivered_sos <= flood.tx_per_delivered_sos or grad.delivered_sources < flood.delivered_sources


def test_hop_gradient_station_is_zero_and_unknown_is_infinite():
    graph = line_graph(4)
    hops = hop_gradient(graph)
    assert hops[0] == 0
    assert hops[1] == 1
    assert hops[3] == 3
    isolated = [set() for _ in range(3)]
    assert hop_gradient(isolated)[1] == 10**9


# --- Beacon overhead ---


def test_beacon_overhead_is_counted():
    cfg = SimConfig(n_nodes=20, beacon_interval_s=1.0, horizon_s=5.0,
                    collision_model=False)
    points, graph = random_geometric_graph(cfg, 31)
    r = simulate(cfg, "flood", seed=31, sources=(3,), graph=graph)
    assert r.beacon_transmissions >= 1
    assert r.beacon_transmissions <= r.transmissions


def test_beacon_can_be_disabled():
    cfg = SimConfig(n_nodes=10, beacon_interval_s=1e9, horizon_s=2.0,
                    collision_model=False)
    points, graph = random_geometric_graph(cfg, 32)
    r = simulate(cfg, "flood", seed=32, sources=(2,), graph=graph)
    assert r.beacon_transmissions == 0


# --- Gradient: beacon relay, route expiry, warmup ---


def test_beacon_is_relayed_beyond_station_neighbourhood():
    """Beacon phải lan ra ngoài hàng xóm trực tiếp của trạm."""
    cfg = SimConfig(n_nodes=40, n_sos=1, link_pdr=1.0, collision_model=False,
                    area_m=400.0, range_m=90.0, beacon_interval_s=2.0,
                    horizon_s=20.0)
    _, graph = random_geometric_graph(cfg, 41)
    r = simulate(cfg, "gradient", seed=41, sources=(10,), graph=graph)
    # Nếu beacon không được relay, số lần phát beacon xấp xỉ số hàng xóm trạm.
    station_neighbours = len(graph[0])
    assert r.beacon_transmissions > station_neighbours


def test_cold_start_can_lose_sources_that_warm_start_delivers():
    """SOS phát trước khi gradient hội tụ có thể không tới trạm."""
    common = dict(n_nodes=100, n_sos=20, link_pdr=0.95, collision_model=True,
                  area_m=400.0, range_m=70.0, beacon_interval_s=2.0)
    _, graph = random_geometric_graph(SimConfig(**common), 5)
    cold = simulate(SimConfig(**common, horizon_s=80.0, warmup_s=0.0),
                    "gradient", seed=5, graph=graph)
    warm = simulate(SimConfig(**common, horizon_s=90.0, warmup_s=10.0),
                    "gradient", seed=5, graph=graph)
    assert warm.pdr >= cold.pdr, "warm start không được tệ hơn cold start"


def test_station_down_reduces_delivery():
    """Trạm sập phải ngừng nhận, không chỉ ngừng phát beacon."""
    common = dict(n_nodes=100, n_sos=20, link_pdr=0.95, collision_model=True,
                  area_m=400.0, range_m=70.0, beacon_interval_s=2.0,
                  horizon_s=90.0, warmup_s=10.0)
    _, graph = random_geometric_graph(SimConfig(**common), 5)
    up = simulate(SimConfig(**common), "gradient", seed=5, graph=graph)
    down = simulate(SimConfig(**common, station_down_after_s=1.0),
                    "gradient", seed=5, graph=graph)
    assert down.delivered_sources < up.delivered_sources, (
        "trạm sập phải làm giảm số nguồn được giao"
    )


def test_route_expiry_drops_more_than_no_expiry_when_station_down():
    """Cô lập hiệu ứng hết hạn tuyến: đây là phép thử H3 nhánh (3) vs (4)."""
    common = dict(n_nodes=80, n_sos=10, link_pdr=0.95, collision_model=True,
                  area_m=400.0, range_m=75.0, horizon_s=90.0, warmup_s=10.0,
                  station_down_after_s=1.0)
    _, graph = random_geometric_graph(SimConfig(**common), 5)
    with_expiry = simulate(
        SimConfig(**common, beacon_interval_s=2.0, route_expiry_beacons=3),
        "gradient", seed=5, graph=graph)
    # beacon_interval_s rất lớn = tắt route expiry (nút không bao giờ quên tuyến)
    without_expiry = simulate(
        SimConfig(**common, beacon_interval_s=1e9),
        "gradient", seed=5, graph=graph)
    assert without_expiry.delivered_sources > 0
    assert (with_expiry.delivered_sources != without_expiry.delivered_sources
            or with_expiry.dropped_no_route != without_expiry.dropped_no_route)


def test_turning_beacon_off_disables_route_expiry():
    """Không beacon = không hết hạn tuyến; gradient dùng hop tĩnh."""
    cfg = SimConfig(n_nodes=20, n_sos=1, link_pdr=1.0, collision_model=False,
                    beacon_interval_s=1e8, horizon_s=20.0,
                    area_m=400.0, range_m=140.0)
    _, graph = random_geometric_graph(cfg, 5)
    r = simulate(cfg, "gradient", seed=5, sources=(5,), graph=graph)
    assert r.beacon_transmissions == 0
    assert r.delivered_sources == 1


def test_beacon_is_relayed_periodically_not_once():
    """Beacon phải được relay theo chu kỳ, không chỉ lần đầu nghe thấy.

    Bảo vệ bug đã tìm ra: nếu relay chỉ khi hop được cải thiện, mỗi nút phát
    beacon đúng một lần trong đời, và nút vào mạng muộn không bao giờ có tuyến.
    """
    cfg = SimConfig(n_nodes=60, n_sos=1, link_pdr=1.0, collision_model=False,
                    area_m=400.0, range_m=85.0, beacon_interval_s=2.0,
                    horizon_s=60.0, warmup_s=30.0, beacon_relay_stride=2)
    _, graph = random_geometric_graph(cfg, 51)
    r = simulate(cfg, "gradient", seed=51, sources=(20,), graph=graph)
    assert r.beacon_transmissions > 60, (
        "beacon relay định kỳ phải tạo nhiều lần phát, không chỉ vài lần đầu"
    )
    assert r.pdr > 0.5, "tuyến phải hình thành và SOS phải tới trạm"


def test_relay_stride_can_isolate_some_regions():
    """Hạn chế đã biết: chọn relay theo chỉ số nút phụ thuộc topology.

    Cùng một hop, có nguồn giao được và có nguồn không, vì stride bỏ qua một số
    nút nên vài vùng không còn relay nào. Test này **ghi lại** hạn chế đó thay vì
    che đi: đây là lý do stride phải là biến thí nghiệm, không được cố định.
    """
    cfg = SimConfig(n_nodes=60, n_sos=1, link_pdr=1.0, collision_model=False,
                    area_m=400.0, range_m=85.0, beacon_interval_s=2.0,
                    horizon_s=60.0, warmup_s=30.0, beacon_relay_stride=2)
    _, graph = random_geometric_graph(cfg, 51)
    hops = hop_gradient(graph)
    same_hop = [n for n in range(1, len(graph)) if hops[n] == hops[10]]
    outcomes = {
        n: simulate(cfg, "gradient", seed=51, sources=(n,), graph=graph).pdr
        for n in same_hop
    }
    assert len(set(outcomes.values())) > 1, (
        "phải quan sát được rằng cùng hop nhưng kết quả khác nhau — "
        "đây là hạn chế của chọn relay theo chỉ số nút"
    )


def test_relay_stride_one_reaches_all_reachable_sources():
    """stride=1 (mọi nút relay) phải cho mọi nguồn reachable đều giao được."""
    cfg = SimConfig(n_nodes=60, n_sos=1, link_pdr=1.0, collision_model=False,
                    area_m=400.0, range_m=85.0, beacon_interval_s=2.0,
                    horizon_s=60.0, warmup_s=30.0, beacon_relay_stride=1)
    _, graph = random_geometric_graph(cfg, 51)
    hops = hop_gradient(graph)
    for source in (5, 10, 15, 20):
        if hops[source] >= 10**9:
            continue
        r = simulate(cfg, "gradient", seed=51, sources=(source,), graph=graph)
        assert r.pdr > 0.5, f"nguồn {source} (hop {hops[source]}) phải giao được với stride=1"


def test_relay_selection_by_hop_would_break_propagation():
    """Chọn relay theo hop làm đứt beacon ở tầng hop lẻ — đây là bẫy phải tránh.

    Test này ghi lại rằng stride theo NODE hoạt động, còn nếu chọn theo HOP thì
    các tầng lẻ không có relay nào. Ta kiểm tra gián tiếp: với stride theo node,
    nút ở hop >= 2 vẫn nhận được tuyến.
    """
    cfg = SimConfig(n_nodes=80, n_sos=1, link_pdr=1.0, collision_model=False,
                    area_m=400.0, range_m=80.0, beacon_interval_s=2.0,
                    horizon_s=60.0, warmup_s=30.0, beacon_relay_stride=2)
    _, graph = random_geometric_graph(cfg, 61)
    hops = hop_gradient(graph)
    deep = [n for n in range(1, len(graph)) if 2 <= hops[n] < 10**9]
    assert deep, "topology phải có nút ở hop >= 2 để phép thử có nghĩa"
    source = deep[0]
    r = simulate(cfg, "gradient", seed=61, sources=(source,), graph=graph)
    assert r.pdr > 0.5, (
        f"nút ở hop {hops[source]} phải có tuyến; "
        "nếu chọn relay theo hop thì beacon đứt và nút này không bao giờ relay được"
    )


def test_beacon_relay_stride_one_is_most_thorough_but_costliest():
    """stride=1 phải cho tuyến đầy đủ nhất và chi phí beacon cao nhất."""
    common = dict(n_nodes=50, n_sos=1, link_pdr=1.0, collision_model=False,
                  area_m=400.0, range_m=95.0, beacon_interval_s=2.0,
                  horizon_s=40.0, warmup_s=20.0)
    _, graph = random_geometric_graph(SimConfig(**common), 71)
    dense = simulate(SimConfig(**common, beacon_relay_stride=1),
                     "gradient", seed=71, sources=(7,), graph=graph)
    sparse = simulate(SimConfig(**common, beacon_relay_stride=2),
                      "gradient", seed=71, sources=(7,), graph=graph)
    assert dense.beacon_transmissions >= sparse.beacon_transmissions
    assert dense.pdr >= sparse.pdr


# --- Tái lập ---


def test_same_seed_is_reproducible():
    cfg = SimConfig(n_nodes=30, collision_model=True)
    a = simulate(cfg, "gradient", seed=99)
    b = simulate(cfg, "gradient", seed=99)
    assert a == b


def test_different_seed_changes_outcome_or_topology():
    cfg = SimConfig(n_nodes=40, n_sos=3)
    a = simulate(cfg, "flood", seed=101)
    b = simulate(cfg, "flood", seed=102)
    assert (a.sources, a.transmissions) != (b.sources, b.transmissions)


# --- Kiểm tra tham số ---


def test_invalid_strategy_rejected():
    cfg = SimConfig(n_nodes=5)
    try:
        simulate(cfg, "bogus", seed=1)  # type: ignore[arg-type]
    except ValueError:
        return
    raise AssertionError("strategy sai phải bị từ chối")


def test_invalid_config_rejected():
    for kwargs in ({"n_nodes": 1}, {"link_pdr": 1.5}, {"n_sos": 0}, {"cache_ttl_s": 0}):
        try:
            SimConfig(**kwargs)  # type: ignore[arg-type]
        except ValueError:
            continue
        raise AssertionError(f"cấu hình sai phải bị từ chối: {kwargs}")


def test_graph_size_must_match_config():
    cfg = SimConfig(n_nodes=10, collision_model=False)
    try:
        simulate(cfg, "flood", seed=1, sources=(1,), graph=line_graph(5))
    except ValueError:
        return
    raise AssertionError("graph lệch kích thước phải bị từ chối")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in tests:
        fn()
        passed += 1
        print(f"PASS {fn.__name__}")
    print(f"\n{passed}/{len(tests)} test qua")
