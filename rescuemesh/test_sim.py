"""Kiểm soát âm và kiểm thử tái lập cho mô phỏng."""

from __future__ import annotations

from sim import SimConfig, line_graph, simulate_once


def test_perfect_line_delivers_for_all_strategies():
    cfg = SimConfig(n_nodes=5, link_pdr=1.0, ttl=15)
    graph = line_graph(5)
    for strategy in ("flood", "trickle", "gradient"):
        result = simulate_once(cfg, strategy, seed=1, source=4, graph=graph)
        assert result.delivered and result.transmissions == 4


def test_no_links_never_delivers():
    cfg = SimConfig(n_nodes=4, link_pdr=1.0)
    graph = [set() for _ in range(4)]
    for strategy in ("flood", "trickle", "gradient"):
        result = simulate_once(cfg, strategy, seed=2, source=3, graph=graph)
        assert not result.delivered and result.transmissions == 1


def test_ttl_one_cannot_cross_two_relays():
    cfg = SimConfig(n_nodes=4, link_pdr=1.0, ttl=1)
    graph = line_graph(4)
    result = simulate_once(cfg, "flood", seed=3, source=3, graph=graph)
    assert not result.delivered


def test_zero_pdr_never_delivers():
    cfg = SimConfig(n_nodes=3, link_pdr=0.0)
    result = simulate_once(cfg, "gradient", seed=4, source=2, graph=line_graph(3))
    assert not result.delivered and result.receptions == 0


def test_same_seed_is_reproducible():
    cfg = SimConfig(n_nodes=30)
    a = simulate_once(cfg, "gradient", seed=99)
    b = simulate_once(cfg, "gradient", seed=99)
    assert a == b


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(tests)}/{len(tests)} test qua")
