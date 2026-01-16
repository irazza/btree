#!/usr/bin/env python3
import argparse
import random
import os
import sys

import pyperf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btreedict import BTreeDict
from sortedcontainers import SortedDict


def build_sorted(n):
    bt = BTreeDict()
    for i in range(n):
        bt[i] = i
    return bt


def build_random(n, seed=42):
    keys = list(range(n))
    random.Random(seed).shuffle(keys)
    bt = BTreeDict()
    for k in keys:
        bt[k] = k
    return bt


def build_sorted_sd(n):
    sd = SortedDict()
    for i in range(n):
        sd[i] = i
    return sd


def build_random_sd(n, seed=42):
    keys = list(range(n))
    random.Random(seed).shuffle(keys)
    sd = SortedDict()
    for k in keys:
        sd[k] = k
    return sd


def bench_bulk_build_sorted(n, impl):
    if impl == "btree":
        def fn():
            bt = BTreeDict()
            for i in range(n):
                bt[i] = i
        return fn
    else:
        def fn():
            sd = SortedDict()
            for i in range(n):
                sd[i] = i
        return fn


def bench_bulk_build_random(n, impl):
    keys = list(range(n))
    random.Random(42).shuffle(keys)
    if impl == "btree":
        def fn():
            bt = BTreeDict()
            for k in keys:
                bt[k] = k
        return fn
    else:
        def fn():
            sd = SortedDict()
            for k in keys:
                sd[k] = k
        return fn


def bench_lookup(n, impl):
    if impl == "btree":
        bt = build_sorted(n)
        keys = [random.randint(0, n - 1) for _ in range(n)]
        def fn():
            for k in keys:
                _ = bt[k]
        return fn
    else:
        sd = build_sorted_sd(n)
        keys = [random.randint(0, n - 1) for _ in range(n)]
        def fn():
            for k in keys:
                _ = sd[k]
        return fn


def bench_contains(n, impl):
    if impl == "btree":
        bt = BTreeDict()
        for i in range(0, n, 2):
            bt[i] = i
        def fn():
            for k in range(n):
                _ = k in bt
        return fn
    else:
        sd = SortedDict()
        for i in range(0, n, 2):
            sd[i] = i
        def fn():
            for k in range(n):
                _ = k in sd
        return fn


def bench_range_iter(n, impl):
    if impl == "btree":
        bt = build_sorted(n)
        def fn():
            for _ in bt.irange(n // 4, 3 * n // 4):
                pass
        return fn
    else:
        sd = build_sorted_sd(n)
        def fn():
            for _ in sd.irange(n // 4, 3 * n // 4):
                pass
        return fn


def bench_delete_random(n, impl):
    keys = list(range(n))
    random.Random(42).shuffle(keys)
    if impl == "btree":
        def fn():
            bt = build_sorted(n)
            for k in keys:
                del bt[k]
        return fn
    else:
        def fn():
            sd = build_sorted_sd(n)
            for k in keys:
                del sd[k]
        return fn


def bench_mixed(n, impl):
    rng = random.Random(42)
    ops = []
    for _ in range(n):
        op = rng.choice(["insert", "insert", "lookup", "delete"])
        key = rng.randint(0, n // 2)
        value = rng.randint(0, 10000)
        ops.append((op, key, value))

    if impl == "btree":
        def fn():
            bt = BTreeDict()
            for op, key, value in ops:
                if op == "insert":
                    bt[key] = value
                elif op == "lookup":
                    _ = bt.get(key)
                else:
                    if key in bt:
                        del bt[key]
        return fn
    else:
        def fn():
            sd = SortedDict()
            for op, key, value in ops:
                if op == "insert":
                    sd[key] = value
                elif op == "lookup":
                    _ = sd.get(key)
                else:
                    if key in sd:
                        del sd[key]
        return fn


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--size", type=int, default=10000, help="Number of items")
    parser.add_argument("--impl", choices=["btree", "sorteddict"], default="btree")
    args, remaining = parser.parse_known_args()

    n = args.size
    impl = args.impl

    sys.argv = [sys.argv[0]] + remaining
    runner = pyperf.Runner()
    runner.metadata["impl"] = impl
    runner.metadata["size"] = n

    runner.bench_func("bulk_build_sorted", bench_bulk_build_sorted(n, impl))
    runner.bench_func("bulk_build_random", bench_bulk_build_random(n, impl))
    runner.bench_func("lookup", bench_lookup(n, impl))
    runner.bench_func("contains", bench_contains(n, impl))
    runner.bench_func("range_iter", bench_range_iter(n, impl))
    runner.bench_func("delete_random", bench_delete_random(n, impl))
    runner.bench_func("mixed", bench_mixed(n, impl))


if __name__ == "__main__":
    main()
