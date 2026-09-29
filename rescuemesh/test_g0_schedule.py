"""Kiểm tra lịch G0-S cân bằng và tái lập."""

from __future__ import annotations

from collections import Counter

from generate_g0_schedule import FACTORS, generate


def test_default_schedule_size_and_blocks():
    rows = generate()
    assert len(rows) == 3 * 3 * 16
    blocks = Counter((row["pair_id"], row["replicate"]) for row in rows)
    assert set(blocks.values()) == {16}


def test_every_factor_is_balanced():
    rows = generate()
    for factor, levels in FACTORS.items():
        counts = Counter(row[factor] for row in rows)
        assert set(counts) == set(levels)
        assert set(counts.values()) == {len(rows) // 2}


def test_each_block_contains_full_factorial_once():
    rows = generate(pairs=2, replicates=2)
    keys = tuple(FACTORS)
    for pair_id in ("PAIR_01", "PAIR_02"):
        for replicate in (1, 2):
            conditions = [tuple(row[key] for key in keys) for row in rows
                          if row["pair_id"] == pair_id and row["replicate"] == replicate]
            assert len(conditions) == 16
            assert len(set(conditions)) == 16


def test_seed_is_reproducible_and_changes_order():
    assert generate(seed=42) == generate(seed=42)
    order_a = [(row["pair_id"], row["replicate"], row["advertise_mode"],
                row["scan_mode"], row["distance_m"], row["wifi_load"])
               for row in generate(seed=42)]
    order_b = [(row["pair_id"], row["replicate"], row["advertise_mode"],
                row["scan_mode"], row["distance_m"], row["wifi_load"])
               for row in generate(seed=43)]
    assert order_a != order_b


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\n{len(tests)}/{len(tests)} test qua")
