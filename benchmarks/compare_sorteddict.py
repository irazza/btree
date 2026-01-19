#!/usr/bin/env python3
"""
SortedDict (B-tree) vs sortedcontainers.SortedDict comparison suite.

Includes:
- Correctness checks
- Micro-benchmarks
- Memory usage
- Optional Hypothesis property checks
- Optional pyperf benchmarks

Examples:
  python benchmarks/compare_sorteddict.py --test
  python benchmarks/compare_sorteddict.py --benchmark
  python benchmarks/compare_sorteddict.py --hypothesis
  python benchmarks/compare_sorteddict.py --pyperf --impl btree --size 10000
"""

from __future__ import annotations

import argparse
import gc
import os
import random
import sys
import time
import tracemalloc
import unittest
from typing import List, Tuple

# Add parent directory to path for in-place builds
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btreedict import SortedDict

try:
    import sortedcontainers
except Exception as exc:  # pragma: no cover - optional dependency
    sortedcontainers = None
    _sortedcontainers_import_error = exc
else:
    _sortedcontainers_import_error = None


def require_sortedcontainers() -> None:
    if sortedcontainers is None:
        raise RuntimeError(
            "sortedcontainers is required for this comparison. "
            "Install it with: pip install sortedcontainers"
        ) from _sortedcontainers_import_error


# =============================================================================
# CORRECTNESS TESTS
# =============================================================================

class CorrectnessTest(unittest.TestCase):
    """Test that SortedDict (btree) and sortedcontainers.SortedDict match."""

    def test_insert_sequential(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(1000):
            bt[i] = i * 2
            sd[i] = i * 2

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))
        self.assertEqual(bt.items(), list(sd.items()))

    def test_insert_reverse(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(999, -1, -1):
            bt[i] = f"value_{i}"
            sd[i] = f"value_{i}"

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_insert_random(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        random.seed(42)
        keys = list(range(1000))
        random.shuffle(keys)

        for k in keys:
            bt[k] = k * 3
            sd[k] = k * 3

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_update_existing_keys(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(500):
            bt[i] = i
            sd[i] = i

        for i in range(500):
            bt[i] = i * 10
            sd[i] = i * 10

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_delete_operations(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(1000):
            bt[i] = i
            sd[i] = i

        for i in range(0, 1000, 3):
            del bt[i]
            del sd[i]

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_mixed_operations(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        random.seed(123)

        for _ in range(5000):
            op = random.choice(["insert", "insert", "update", "delete"])
            key = random.randint(0, 500)

            if op in {"insert", "update"}:
                value = random.randint(0, 10000)
                bt[key] = value
                sd[key] = value
            elif op == "delete":
                if key in sd:
                    del bt[key]
                    del sd[key]

        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_get_method(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(0, 100, 2):
            bt[i] = i
            sd[i] = i

        for i in range(100):
            self.assertEqual(bt.get(i), sd.get(i))
            self.assertEqual(bt.get(i, -1), sd.get(i, -1))

    def test_contains(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(0, 100, 2):
            bt[i] = i
            sd[i] = i

        for i in range(100):
            self.assertEqual(i in bt, i in sd)

    def test_min_max(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        random.seed(456)
        keys = random.sample(range(10000), 1000)

        for k in keys:
            bt[k] = k
            sd[k] = k

        self.assertEqual(bt.min(), sd.peekitem(0)[0])
        self.assertEqual(bt.max(), sd.peekitem(-1)[0])

    def test_pop_method(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(100):
            bt[i] = i * 2
            sd[i] = i * 2

        for i in range(0, 100, 2):
            bt_val = bt.pop(i)
            sd_val = sd.pop(i)
            self.assertEqual(bt_val, sd_val)

        for i in range(0, 100, 2):
            bt_val = bt.pop(i, -1)
            sd_val = sd.pop(i, -1)
            self.assertEqual(bt_val, sd_val)

        self.assertEqual(len(bt), len(sd))

    def test_string_keys(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        words = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elderberry",
            "fig",
            "grape",
            "honeydew",
            "kiwi",
            "lemon",
        ]

        for word in words:
            bt[word] = len(word)
            sd[word] = len(word)

        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_tuple_keys(self):
        require_sortedcontainers()
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for i in range(10):
            for j in range(10):
                bt[(i, j)] = i * 10 + j
                sd[(i, j)] = i * 10 + j

        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))


# =============================================================================
# PERFORMANCE BENCHMARKS
# =============================================================================

class BenchmarkResult:
    """Store benchmark results."""

    def __init__(
        self,
        name: str,
        btree_time: float,
        sorteddict_time: float,
        btree_memory: int = 0,
        sorteddict_memory: int = 0,
    ):
        self.name = name
        self.btree_time = btree_time
        self.sorteddict_time = sorteddict_time
        self.btree_memory = btree_memory
        self.sorteddict_memory = sorteddict_memory
        self.speedup = sorteddict_time / btree_time if btree_time > 0 else 0

    def __str__(self):
        time_winner = "SortedDict (btree)" if self.btree_time < self.sorteddict_time else "SortedDict (sortedcontainers)"
        return (
            f"{self.name}:\n"
            f"  SortedDict (btree):         {self.btree_time*1000:8.2f} ms\n"
            f"  SortedDict (sortedcontainers): {self.sorteddict_time*1000:8.2f} ms\n"
            f"  Speedup:    {self.speedup:.2f}x ({time_winner} faster)"
        )


def benchmark_insert_sequential(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    start = time.perf_counter()
    for i in range(n):
        bt[i] = i
    btree_time = time.perf_counter() - start

    sd = sortedcontainers.SortedDict()
    start = time.perf_counter()
    for i in range(n):
        sd[i] = i
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Sequential Insert ({n:,} items)", btree_time, sorteddict_time)


def benchmark_insert_random(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    random.seed(42)
    keys = list(range(n))
    random.shuffle(keys)

    bt = SortedDict()
    start = time.perf_counter()
    for k in keys:
        bt[k] = k
    btree_time = time.perf_counter() - start

    sd = sortedcontainers.SortedDict()
    start = time.perf_counter()
    for k in keys:
        sd[k] = k
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Random Insert ({n:,} items)", btree_time, sorteddict_time)


def benchmark_lookup(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i

    random.seed(42)
    lookup_keys = [random.randint(0, n - 1) for _ in range(n)]

    start = time.perf_counter()
    for k in lookup_keys:
        _ = bt[k]
    btree_time = time.perf_counter() - start

    start = time.perf_counter()
    for k in lookup_keys:
        _ = sd[k]
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Random Lookup ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_contains(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(0, n, 2):
        bt[i] = i
        sd[i] = i

    start = time.perf_counter()
    for i in range(n):
        _ = i in bt
    btree_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(n):
        _ = i in sd
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Contains Check ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_iteration(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i

    start = time.perf_counter()
    for _ in range(10):
        for _ in bt:
            pass
    btree_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(10):
        for _ in sd:
            pass
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Iteration ({n:,} items, 10x)", btree_time, sorteddict_time)


def benchmark_delete_random(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    random.seed(42)
    delete_order = list(range(n))
    random.shuffle(delete_order)

    bt = SortedDict()
    for i in range(n):
        bt[i] = i

    start = time.perf_counter()
    for k in delete_order:
        del bt[k]
    btree_time = time.perf_counter() - start

    sd = sortedcontainers.SortedDict()
    for i in range(n):
        sd[i] = i

    start = time.perf_counter()
    for k in delete_order:
        del sd[k]
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Random Delete ({n:,} items)", btree_time, sorteddict_time)


def benchmark_mixed_operations(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    random.seed(42)
    operations = []
    for _ in range(n):
        op = random.choice(["insert", "insert", "lookup", "delete"])
        key = random.randint(0, n // 2)
        value = random.randint(0, 10000)
        operations.append((op, key, value))

    bt = SortedDict()
    start = time.perf_counter()
    for op, key, value in operations:
        if op == "insert":
            bt[key] = value
        elif op == "lookup":
            _ = bt.get(key)
        elif op == "delete":
            if key in bt:
                del bt[key]
    btree_time = time.perf_counter() - start

    sd = sortedcontainers.SortedDict()
    start = time.perf_counter()
    for op, key, value in operations:
        if op == "insert":
            sd[key] = value
        elif op == "lookup":
            _ = sd.get(key)
        elif op == "delete":
            if key in sd:
                del sd[key]
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Mixed Operations ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_update(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i

    start = time.perf_counter()
    for i in range(n):
        bt[i] = i * 2
    btree_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(n):
        sd[i] = i * 2
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(f"Update Existing ({n:,} items)", btree_time, sorteddict_time)


def benchmark_keys_values_items(n: int) -> BenchmarkResult:
    require_sortedcontainers()
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i

    start = time.perf_counter()
    for _ in range(100):
        _ = bt.keys()
        _ = bt.values()
        _ = bt.items()
    btree_time = time.perf_counter() - start

    start = time.perf_counter()
    for _ in range(100):
        _ = list(sd.keys())
        _ = list(sd.values())
        _ = list(sd.items())
    sorteddict_time = time.perf_counter() - start

    return BenchmarkResult(
        f"keys/values/items ({n:,} items, 100x)", btree_time, sorteddict_time
    )


# =============================================================================
# MEMORY BENCHMARKS
# =============================================================================

def benchmark_memory(n: int) -> Tuple[int, int]:
    require_sortedcontainers()
    gc.collect()

    tracemalloc.start()
    bt = SortedDict()
    for i in range(n):
        bt[i] = i
    btree_current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    del bt
    gc.collect()

    tracemalloc.start()
    sd = sortedcontainers.SortedDict()
    for i in range(n):
        sd[i] = i
    sorteddict_current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return btree_current, sorteddict_current


def format_bytes(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(b) < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"


# =============================================================================
# MAIN BENCHMARK RUNNER
# =============================================================================

def run_benchmarks() -> None:
    require_sortedcontainers()
    print("=" * 70)
    print("SortedDict (btree) vs sortedcontainers.SortedDict Comparison")
    print("=" * 70)

    print("\nWarming up...")
    bt = SortedDict()
    sd = sortedcontainers.SortedDict()
    for i in range(1000):
        bt[i] = i
        sd[i] = i
    del bt, sd
    gc.collect()

    print("\n" + "=" * 70)
    print("SPEED BENCHMARKS")
    print("=" * 70)

    sizes = [10_000, 100_000]
    benchmarks = [
        benchmark_insert_sequential,
        benchmark_insert_random,
        benchmark_lookup,
        benchmark_contains,
        benchmark_iteration,
        benchmark_delete_random,
        benchmark_mixed_operations,
        benchmark_update,
        benchmark_keys_values_items,
    ]

    results: List[BenchmarkResult] = []

    for size in sizes:
        print(f"\n--- Size: {size:,} ---")
        for bench_func in benchmarks:
            try:
                result = bench_func(size)
                results.append(result)
                print(f"\n{result}")
            except Exception as exc:
                print(f"\n{bench_func.__name__}: ERROR - {exc}")
            gc.collect()

    print("\n" + "=" * 70)
    print("MEMORY BENCHMARKS")
    print("=" * 70)

    for size in [10_000, 100_000, 500_000]:
        btree_mem, sorteddict_mem = benchmark_memory(size)
        ratio = sorteddict_mem / btree_mem if btree_mem > 0 else 0
        winner = "SortedDict (btree)" if btree_mem < sorteddict_mem else "SortedDict (sortedcontainers)"

        print(f"\nMemory for {size:,} items:")
        print(f"  SortedDict (btree):         {format_bytes(btree_mem)}")
        print(f"  SortedDict (sortedcontainers): {format_bytes(sorteddict_mem)}")
        print(f"  Ratio:      {ratio:.2f}x ({winner} more efficient)")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    btree_wins = sum(1 for r in results if r.btree_time < r.sorteddict_time)
    sorteddict_wins = len(results) - btree_wins
    avg_speedup = sum(r.speedup for r in results) / len(results) if results else 0

    print(f"\nTotal benchmarks: {len(results)}")
    print(f"SortedDict (btree) wins:       {btree_wins}")
    print(f"SortedDict wins:  {sorteddict_wins}")
    print(f"Average speedup:  {avg_speedup:.2f}x")

    if avg_speedup > 1:
        print("\nOverall: SortedDict (btree) is faster on average")
    else:
        print("\nOverall: SortedDict is faster on average")


# =============================================================================
# OPTIONAL HYPOTHESIS CHECKS
# =============================================================================

def run_hypothesis_tests() -> None:
    require_sortedcontainers()
    try:
        from hypothesis import given, settings, strategies as st
    except Exception as exc:
        raise RuntimeError(
            "hypothesis is required for --hypothesis. Install it with: pip install hypothesis"
        ) from exc

    @settings(max_examples=200, deadline=None)
    @given(
        st.lists(
            st.tuples(
                st.sampled_from(["insert", "delete", "get", "contains"]),
                st.integers(min_value=0, max_value=100),
                st.integers(min_value=-1000, max_value=1000),
            ),
            min_size=1,
            max_size=200,
        )
    )
    def random_ops_match_sorteddict(ops):
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()

        for op, key, value in ops:
            if op == "insert":
                bt[key] = value
                sd[key] = value
            elif op == "delete":
                if key in sd:
                    del bt[key]
                    del sd[key]
                else:
                    try:
                        del bt[key]
                        raise AssertionError("Expected KeyError")
                    except KeyError:
                        pass
            elif op == "get":
                if bt.get(key) != sd.get(key):
                    raise AssertionError("get() mismatch")
            elif op == "contains":
                if (key in bt) != (key in sd):
                    raise AssertionError("contains mismatch")

            if len(bt) != len(sd):
                raise AssertionError("length mismatch")
            if bt.keys() != list(sd.keys()):
                raise AssertionError("keys mismatch")
            if bt.values() != list(sd.values()):
                raise AssertionError("values mismatch")
            if bt.items() != list(sd.items()):
                raise AssertionError("items mismatch")

    @settings(max_examples=200, deadline=None)
    @given(
        st.lists(st.integers(min_value=-50, max_value=50), min_size=0, max_size=200),
        st.one_of(st.none(), st.integers(min_value=-60, max_value=60)),
        st.one_of(st.none(), st.integers(min_value=-60, max_value=60)),
        st.tuples(st.booleans(), st.booleans()),
    )
    def irange_matches_sorteddict(keys, min_v, max_v, inclusive):
        bt = SortedDict()
        sd = sortedcontainers.SortedDict()
        for k in keys:
            bt[k] = k
            sd[k] = k

        bt_result = list(bt.irange(min_v, max_v, inclusive=inclusive))
        sd_result = list(sd.irange(min_v, max_v, inclusive=inclusive))
        if bt_result != sd_result:
            raise AssertionError("irange mismatch")

    random_ops_match_sorteddict()
    irange_matches_sorteddict()


# =============================================================================
# OPTIONAL PYPERF BENCHMARKS
# =============================================================================

def run_pyperf(size: int, impl: str, remaining_argv: List[str]) -> None:
    require_sortedcontainers()
    try:
        import pyperf
    except Exception as exc:
        raise RuntimeError(
            "pyperf is required for --pyperf. Install it with: pip install pyperf"
        ) from exc

    def build_sorted(n):
        bt = SortedDict()
        for i in range(n):
            bt[i] = i
        return bt

    def build_random(n, seed=42):
        keys = list(range(n))
        random.Random(seed).shuffle(keys)
        bt = SortedDict()
        for k in keys:
            bt[k] = k
        return bt

    def build_sorted_sd(n):
        sd = sortedcontainers.SortedDict()
        for i in range(n):
            sd[i] = i
        return sd

    def build_random_sd(n, seed=42):
        keys = list(range(n))
        random.Random(seed).shuffle(keys)
        sd = sortedcontainers.SortedDict()
        for k in keys:
            sd[k] = k
        return sd

    def bench_bulk_build_sorted(n, impl_name):
        if impl_name == "btree":
            def fn():
                bt = SortedDict()
                for i in range(n):
                    bt[i] = i
            return fn
        def fn():
            sd = sortedcontainers.SortedDict()
            for i in range(n):
                sd[i] = i
        return fn

    def bench_bulk_build_random(n, impl_name):
        keys = list(range(n))
        random.Random(42).shuffle(keys)
        if impl_name == "btree":
            def fn():
                bt = SortedDict()
                for k in keys:
                    bt[k] = k
            return fn
        def fn():
            sd = sortedcontainers.SortedDict()
            for k in keys:
                sd[k] = k
        return fn

    def bench_lookup(n, impl_name):
        if impl_name == "btree":
            bt = build_sorted(n)
            keys = [random.randint(0, n - 1) for _ in range(n)]
            def fn():
                for k in keys:
                    _ = bt[k]
            return fn
        sd = build_sorted_sd(n)
        keys = [random.randint(0, n - 1) for _ in range(n)]
        def fn():
            for k in keys:
                _ = sd[k]
        return fn

    def bench_contains(n, impl_name):
        if impl_name == "btree":
            bt = SortedDict()
            for i in range(0, n, 2):
                bt[i] = i
            def fn():
                for k in range(n):
                    _ = k in bt
            return fn
        sd = sortedcontainers.SortedDict()
        for i in range(0, n, 2):
            sd[i] = i
        def fn():
            for k in range(n):
                _ = k in sd
        return fn

    def bench_range_iter(n, impl_name):
        if impl_name == "btree":
            bt = build_sorted(n)
            def fn():
                for _ in bt.irange(n // 4, 3 * n // 4):
                    pass
            return fn
        sd = build_sorted_sd(n)
        def fn():
            for _ in sd.irange(n // 4, 3 * n // 4):
                pass
        return fn

    def bench_delete_random(n, impl_name):
        keys = list(range(n))
        random.Random(42).shuffle(keys)
        if impl_name == "btree":
            def fn():
                bt = build_sorted(n)
                for k in keys:
                    del bt[k]
            return fn
        def fn():
            sd = build_sorted_sd(n)
            for k in keys:
                del sd[k]
        return fn

    def bench_mixed(n, impl_name):
        rng = random.Random(42)
        ops = []
        for _ in range(n):
            op = rng.choice(["insert", "insert", "lookup", "delete"])
            key = rng.randint(0, n // 2)
            value = rng.randint(0, 10000)
            ops.append((op, key, value))

        if impl_name == "btree":
            def fn():
                bt = SortedDict()
                for op, key, value in ops:
                    if op == "insert":
                        bt[key] = value
                    elif op == "lookup":
                        _ = bt.get(key)
                    else:
                        if key in bt:
                            del bt[key]
            return fn
        def fn():
            sd = sortedcontainers.SortedDict()
            for op, key, value in ops:
                if op == "insert":
                    sd[key] = value
                elif op == "lookup":
                    _ = sd.get(key)
                else:
                    if key in sd:
                        del sd[key]
        return fn

    sys.argv = [sys.argv[0]] + remaining_argv
    runner = pyperf.Runner()
    runner.metadata["impl"] = impl
    runner.metadata["size"] = size

    runner.bench_func("bulk_build_sorted", bench_bulk_build_sorted(size, impl))
    runner.bench_func("bulk_build_random", bench_bulk_build_random(size, impl))
    runner.bench_func("lookup", bench_lookup(size, impl))
    runner.bench_func("contains", bench_contains(size, impl))
    runner.bench_func("range_iter", bench_range_iter(size, impl))
    runner.bench_func("delete_random", bench_delete_random(size, impl))
    runner.bench_func("mixed", bench_mixed(size, impl))


def main() -> None:
    parser = argparse.ArgumentParser(description="SortedDict (btree) vs sortedcontainers.SortedDict comparison")
    parser.add_argument("--test", action="store_true", help="Run correctness tests")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarks")
    parser.add_argument("--hypothesis", action="store_true", help="Run Hypothesis checks")
    parser.add_argument("--pyperf", action="store_true", help="Run pyperf benchmarks")
    parser.add_argument("--size", type=int, default=10000, help="Pyperf size")
    parser.add_argument("--impl", choices=["btree", "sorteddict"], default="btree")
    args, remaining = parser.parse_known_args()

    if args.hypothesis:
        run_hypothesis_tests()
        return

    if args.pyperf:
        run_pyperf(args.size, args.impl, remaining)
        return

    if args.test:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(CorrectnessTest)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
        return

    if args.benchmark:
        run_benchmarks()
        return

    print("No mode selected. Use --test, --benchmark, --hypothesis, or --pyperf.")
    sys.exit(2)


if __name__ == "__main__":
    main()
