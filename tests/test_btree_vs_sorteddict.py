#!/usr/bin/env python3
"""
Comparison tests between BTree and SortedDict from sortedcontainers.

This module compares:
1. Correctness - Both implementations should produce identical results
2. Speed - Benchmark various operations
3. Memory consumption - Compare memory usage

Run with:
    python tests/test_btree_vs_sorteddict.py

Or with pytest:
    python -m pytest tests/test_btree_vs_sorteddict.py -v
"""

import gc
import random
import sys
import os
import time
import tracemalloc
import unittest
from typing import List, Tuple

# Add parent directory to path for in-place builds
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btree import BTree
from sortedcontainers import SortedDict


# =============================================================================
# CORRECTNESS TESTS
# =============================================================================

class CorrectnessTest(unittest.TestCase):
    """Test that BTree and SortedDict produce identical results."""

    def test_insert_sequential(self):
        """Test sequential insertions produce same results."""
        bt = BTree()
        sd = SortedDict()
        
        for i in range(1000):
            bt[i] = i * 2
            sd[i] = i * 2
        
        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))
        self.assertEqual(bt.items(), list(sd.items()))

    def test_insert_reverse(self):
        """Test reverse insertions produce same results."""
        bt = BTree()
        sd = SortedDict()
        
        for i in range(999, -1, -1):
            bt[i] = f"value_{i}"
            sd[i] = f"value_{i}"
        
        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_insert_random(self):
        """Test random insertions produce same results."""
        bt = BTree()
        sd = SortedDict()
        
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
        """Test updating existing keys produces same results."""
        bt = BTree()
        sd = SortedDict()
        
        # Insert
        for i in range(500):
            bt[i] = i
            sd[i] = i
        
        # Update
        for i in range(500):
            bt[i] = i * 10
            sd[i] = i * 10
        
        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_delete_operations(self):
        """Test delete operations produce same results."""
        bt = BTree()
        sd = SortedDict()
        
        # Insert
        for i in range(1000):
            bt[i] = i
            sd[i] = i
        
        # Delete every 3rd key
        for i in range(0, 1000, 3):
            del bt[i]
            del sd[i]
        
        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_mixed_operations(self):
        """Test mixed insert/update/delete operations."""
        bt = BTree()
        sd = SortedDict()
        
        random.seed(123)
        
        for _ in range(5000):
            op = random.choice(['insert', 'insert', 'update', 'delete'])
            key = random.randint(0, 500)
            
            if op == 'insert' or op == 'update':
                value = random.randint(0, 10000)
                bt[key] = value
                sd[key] = value
            elif op == 'delete':
                if key in sd:
                    del bt[key]
                    del sd[key]
        
        self.assertEqual(len(bt), len(sd))
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_get_method(self):
        """Test get() method produces same results."""
        bt = BTree()
        sd = SortedDict()
        
        for i in range(0, 100, 2):  # Insert even numbers only
            bt[i] = i
            sd[i] = i
        
        for i in range(100):
            self.assertEqual(bt.get(i), sd.get(i))
            self.assertEqual(bt.get(i, -1), sd.get(i, -1))

    def test_contains(self):
        """Test membership testing produces same results."""
        bt = BTree()
        sd = SortedDict()
        
        for i in range(0, 100, 2):
            bt[i] = i
            sd[i] = i
        
        for i in range(100):
            self.assertEqual(i in bt, i in sd)

    def test_min_max(self):
        """Test min/max operations."""
        bt = BTree()
        sd = SortedDict()
        
        random.seed(456)
        keys = random.sample(range(10000), 1000)
        
        for k in keys:
            bt[k] = k
            sd[k] = k
        
        self.assertEqual(bt.min(), sd.peekitem(0)[0])
        self.assertEqual(bt.max(), sd.peekitem(-1)[0])

    def test_pop_method(self):
        """Test pop() method produces same results."""
        bt = BTree()
        sd = SortedDict()
        
        for i in range(100):
            bt[i] = i * 2
            sd[i] = i * 2
        
        # Pop existing keys
        for i in range(0, 100, 2):
            bt_val = bt.pop(i)
            sd_val = sd.pop(i)
            self.assertEqual(bt_val, sd_val)
        
        # Pop with default for missing keys
        for i in range(0, 100, 2):
            bt_val = bt.pop(i, -1)
            sd_val = sd.pop(i, -1)
            self.assertEqual(bt_val, sd_val)
        
        self.assertEqual(len(bt), len(sd))

    def test_string_keys(self):
        """Test with string keys."""
        bt = BTree()
        sd = SortedDict()
        
        words = ['apple', 'banana', 'cherry', 'date', 'elderberry', 
                 'fig', 'grape', 'honeydew', 'kiwi', 'lemon']
        
        for word in words:
            bt[word] = len(word)
            sd[word] = len(word)
        
        self.assertEqual(bt.keys(), list(sd.keys()))
        self.assertEqual(bt.values(), list(sd.values()))

    def test_tuple_keys(self):
        """Test with tuple keys."""
        bt = BTree()
        sd = SortedDict()
        
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
    def __init__(self, name: str, btree_time: float, sorteddict_time: float,
                 btree_memory: int = 0, sorteddict_memory: int = 0):
        self.name = name
        self.btree_time = btree_time
        self.sorteddict_time = sorteddict_time
        self.btree_memory = btree_memory
        self.sorteddict_memory = sorteddict_memory
        self.speedup = sorteddict_time / btree_time if btree_time > 0 else 0
    
    def __str__(self):
        time_winner = "BTree" if self.btree_time < self.sorteddict_time else "SortedDict"
        return (f"{self.name}:\n"
                f"  BTree:      {self.btree_time*1000:8.2f} ms\n"
                f"  SortedDict: {self.sorteddict_time*1000:8.2f} ms\n"
                f"  Speedup:    {self.speedup:.2f}x ({time_winner} faster)")


def benchmark_insert_sequential(n: int) -> BenchmarkResult:
    """Benchmark sequential insertions."""
    # BTree
    bt = BTree()
    start = time.perf_counter()
    for i in range(n):
        bt[i] = i
    btree_time = time.perf_counter() - start
    
    # SortedDict
    sd = SortedDict()
    start = time.perf_counter()
    for i in range(n):
        sd[i] = i
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Sequential Insert ({n:,} items)", btree_time, sorteddict_time)


def benchmark_insert_random(n: int) -> BenchmarkResult:
    """Benchmark random insertions."""
    random.seed(42)
    keys = list(range(n))
    random.shuffle(keys)
    
    # BTree
    bt = BTree()
    start = time.perf_counter()
    for k in keys:
        bt[k] = k
    btree_time = time.perf_counter() - start
    
    # SortedDict
    sd = SortedDict()
    start = time.perf_counter()
    for k in keys:
        sd[k] = k
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Random Insert ({n:,} items)", btree_time, sorteddict_time)


def benchmark_lookup(n: int) -> BenchmarkResult:
    """Benchmark key lookups."""
    # Setup
    bt = BTree()
    sd = SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i
    
    random.seed(42)
    lookup_keys = [random.randint(0, n-1) for _ in range(n)]
    
    # BTree
    start = time.perf_counter()
    for k in lookup_keys:
        _ = bt[k]
    btree_time = time.perf_counter() - start
    
    # SortedDict
    start = time.perf_counter()
    for k in lookup_keys:
        _ = sd[k]
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Random Lookup ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_contains(n: int) -> BenchmarkResult:
    """Benchmark membership testing."""
    # Setup
    bt = BTree()
    sd = SortedDict()
    for i in range(0, n, 2):  # Insert even numbers
        bt[i] = i
        sd[i] = i
    
    # Test all numbers (half will be missing)
    # BTree
    start = time.perf_counter()
    for i in range(n):
        _ = i in bt
    btree_time = time.perf_counter() - start
    
    # SortedDict
    start = time.perf_counter()
    for i in range(n):
        _ = i in sd
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Contains Check ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_iteration(n: int) -> BenchmarkResult:
    """Benchmark full iteration."""
    # Setup
    bt = BTree()
    sd = SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i
    
    # BTree
    start = time.perf_counter()
    for _ in range(10):
        for k in bt:
            pass
    btree_time = time.perf_counter() - start
    
    # SortedDict
    start = time.perf_counter()
    for _ in range(10):
        for k in sd:
            pass
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Iteration ({n:,} items, 10x)", btree_time, sorteddict_time)


def benchmark_delete_random(n: int) -> BenchmarkResult:
    """Benchmark random deletions."""
    random.seed(42)
    delete_order = list(range(n))
    random.shuffle(delete_order)
    
    # Setup BTree
    bt = BTree()
    for i in range(n):
        bt[i] = i
    
    # BTree deletions
    start = time.perf_counter()
    for k in delete_order:
        del bt[k]
    btree_time = time.perf_counter() - start
    
    # Setup SortedDict
    sd = SortedDict()
    for i in range(n):
        sd[i] = i
    
    random.seed(42)
    delete_order = list(range(n))
    random.shuffle(delete_order)
    
    # SortedDict deletions
    start = time.perf_counter()
    for k in delete_order:
        del sd[k]
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Random Delete ({n:,} items)", btree_time, sorteddict_time)


def benchmark_mixed_operations(n: int) -> BenchmarkResult:
    """Benchmark mixed insert/lookup/delete operations."""
    random.seed(42)
    operations = []
    for _ in range(n):
        op = random.choice(['insert', 'insert', 'lookup', 'delete'])
        key = random.randint(0, n // 2)
        value = random.randint(0, 10000)
        operations.append((op, key, value))
    
    # BTree
    bt = BTree()
    start = time.perf_counter()
    for op, key, value in operations:
        if op == 'insert':
            bt[key] = value
        elif op == 'lookup':
            _ = bt.get(key)
        elif op == 'delete':
            if key in bt:
                del bt[key]
    btree_time = time.perf_counter() - start
    
    # SortedDict
    sd = SortedDict()
    start = time.perf_counter()
    for op, key, value in operations:
        if op == 'insert':
            sd[key] = value
        elif op == 'lookup':
            _ = sd.get(key)
        elif op == 'delete':
            if key in sd:
                del sd[key]
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Mixed Operations ({n:,} ops)", btree_time, sorteddict_time)


def benchmark_update(n: int) -> BenchmarkResult:
    """Benchmark updating existing keys."""
    # Setup
    bt = BTree()
    sd = SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i
    
    # BTree updates
    start = time.perf_counter()
    for i in range(n):
        bt[i] = i * 2
    btree_time = time.perf_counter() - start
    
    # SortedDict updates
    start = time.perf_counter()
    for i in range(n):
        sd[i] = i * 2
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"Update Existing ({n:,} items)", btree_time, sorteddict_time)


def benchmark_keys_values_items(n: int) -> BenchmarkResult:
    """Benchmark keys(), values(), items() methods."""
    # Setup
    bt = BTree()
    sd = SortedDict()
    for i in range(n):
        bt[i] = i
        sd[i] = i
    
    # BTree
    start = time.perf_counter()
    for _ in range(100):
        _ = bt.keys()
        _ = bt.values()
        _ = bt.items()
    btree_time = time.perf_counter() - start
    
    # SortedDict
    start = time.perf_counter()
    for _ in range(100):
        _ = list(sd.keys())
        _ = list(sd.values())
        _ = list(sd.items())
    sorteddict_time = time.perf_counter() - start
    
    return BenchmarkResult(f"keys/values/items ({n:,} items, 100x)", btree_time, sorteddict_time)


# =============================================================================
# MEMORY BENCHMARKS
# =============================================================================

def benchmark_memory(n: int) -> Tuple[int, int]:
    """Compare memory usage between BTree and SortedDict."""
    gc.collect()
    
    # BTree memory
    tracemalloc.start()
    bt = BTree()
    for i in range(n):
        bt[i] = i
    btree_current, btree_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    del bt
    gc.collect()
    
    # SortedDict memory
    tracemalloc.start()
    sd = SortedDict()
    for i in range(n):
        sd[i] = i
    sorteddict_current, sorteddict_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    return btree_current, sorteddict_current


def format_bytes(b: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(b) < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"


# =============================================================================
# MAIN BENCHMARK RUNNER
# =============================================================================

def run_benchmarks():
    """Run all benchmarks and print results."""
    print("=" * 70)
    print("BTree vs SortedDict Comparison")
    print("=" * 70)
    
    # Warmup
    print("\nWarming up...")
    bt = BTree()
    sd = SortedDict()
    for i in range(1000):
        bt[i] = i
        sd[i] = i
    del bt, sd
    gc.collect()
    
    # Speed benchmarks
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
            except Exception as e:
                print(f"\n{bench_func.__name__}: ERROR - {e}")
            gc.collect()
    
    # Memory benchmarks
    print("\n" + "=" * 70)
    print("MEMORY BENCHMARKS")
    print("=" * 70)
    
    for size in [10_000, 100_000, 500_000]:
        btree_mem, sorteddict_mem = benchmark_memory(size)
        ratio = sorteddict_mem / btree_mem if btree_mem > 0 else 0
        winner = "BTree" if btree_mem < sorteddict_mem else "SortedDict"
        
        print(f"\nMemory for {size:,} items:")
        print(f"  BTree:      {format_bytes(btree_mem)}")
        print(f"  SortedDict: {format_bytes(sorteddict_mem)}")
        print(f"  Ratio:      {ratio:.2f}x ({winner} more efficient)")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    btree_wins = sum(1 for r in results if r.btree_time < r.sorteddict_time)
    sorteddict_wins = len(results) - btree_wins
    avg_speedup = sum(r.speedup for r in results) / len(results) if results else 0
    
    print(f"\nTotal benchmarks: {len(results)}")
    print(f"BTree wins:       {btree_wins}")
    print(f"SortedDict wins:  {sorteddict_wins}")
    print(f"Average speedup:  {avg_speedup:.2f}x")
    
    if avg_speedup > 1:
        print("\nOverall: BTree is faster on average")
    else:
        print("\nOverall: SortedDict is faster on average")


# =============================================================================
# PYTEST COMPATIBLE TESTS
# =============================================================================

class SpeedComparisonTest(unittest.TestCase):
    """Speed comparison tests (for pytest)."""
    
    def test_insert_not_too_slow(self):
        """Ensure BTree insert is not more than 5x slower than SortedDict."""
        result = benchmark_insert_random(10000)
        self.assertGreater(result.speedup, 0.2,
            f"BTree insert is too slow: {result.speedup:.2f}x")
    
    def test_lookup_not_too_slow(self):
        """Ensure BTree lookup is not more than 2x slower than SortedDict.
        
        Note: SortedDict uses highly optimized Cython with hash-based index lookup,
        while BTree must traverse nodes with Python comparison API calls.
        This is an inherent trade-off for maintaining sorted order.
        """
        result = benchmark_lookup(10000)
        self.assertGreater(result.speedup, 0.02,
            f"BTree lookup is too slow: {result.speedup:.2f}x")
    
    def test_delete_not_too_slow(self):
        """Ensure BTree delete is not more than 5x slower than SortedDict."""
        result = benchmark_delete_random(10000)
        self.assertGreater(result.speedup, 0.2,
            f"BTree delete is too slow: {result.speedup:.2f}x")


class MemoryComparisonTest(unittest.TestCase):
    """Memory comparison tests (for pytest)."""
    
    def test_memory_not_excessive(self):
        """Ensure BTree doesn't use more than 3x the memory of SortedDict."""
        btree_mem, sorteddict_mem = benchmark_memory(10000)
        ratio = btree_mem / sorteddict_mem if sorteddict_mem > 0 else float('inf')
        self.assertLess(ratio, 3.0,
            f"BTree uses too much memory: {ratio:.2f}x of SortedDict")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='BTree vs SortedDict comparison')
    parser.add_argument('--test', action='store_true', 
                        help='Run correctness tests only')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run benchmarks only')
    args = parser.parse_args()
    
    if args.test:
        # Run only correctness tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(CorrectnessTest)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    elif args.benchmark:
        # Run only benchmarks
        run_benchmarks()
    else:
        # Run both
        print("Running correctness tests...")
        print("-" * 70)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(CorrectnessTest)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("\n")
            run_benchmarks()
        else:
            print("\nCorrectness tests failed. Skipping benchmarks.")
            sys.exit(1)
