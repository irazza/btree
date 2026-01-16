# B-Tree: A Self-Balancing Tree Data Structure for Python

A high-performance B-Tree implementation written in C as a Python extension module.

## Features

- **Fast O(log n)** operations: insert, search, delete
- **Sorted iteration**: keys are always returned in sorted order
- **Dictionary-like interface**: supports `[]`, `in`, `len()`, iteration
- **Customizable order**: control the branching factor
- **Memory efficient**: implemented in C with proper garbage collection support

## Installation

### From source

```bash
cd /home/irazza/projects/btree
pip install .
```

### For development (editable install)

```bash
pip install -e .
```

### Build extension in-place

```bash
python setup.py build_ext --inplace
```

## Quick Start

```python
from btree import BTreeDict

# Create a B-tree (default order=64)
bt = BTreeDict()

# Insert key-value pairs
bt[5] = "five"
bt[3] = "three"
bt[7] = "seven"
bt[1] = "one"

# Lookup
print(bt[5])        # "five"
print(bt.get(10))   # None (default)
print(bt.get(10, "not found"))  # "not found"

# Check membership
print(3 in bt)      # True
print(10 in bt)     # False

# Get size
print(len(bt))      # 4

# Iterate (sorted order)
for key in bt:
    print(key, bt[key])
# Output:
# 1 one
# 3 three
# 5 five
# 7 seven

# Get all keys/values/items
print(bt.keys())    # [1, 3, 5, 7]
print(bt.values())  # ['one', 'three', 'five', 'seven']
print(bt.items())   # [(1, 'one'), (3, 'three'), (5, 'five'), (7, 'seven')]

# Min/Max
print(bt.min())     # 1
print(bt.max())     # 7

# Delete
del bt[3]
print(bt.keys())    # [1, 5, 7]

# Pop (delete and return value)
value = bt.pop(5)
print(value)        # "five"

# Clear all items
bt.clear()
print(len(bt))      # 0
```

## API Reference

### `BTreeDict(order=64)`

Create a new B-tree with the specified order (minimum degree).

- **order**: The minimum degree of the B-tree (default: 64)
  - Each node has at most `2*order - 1` keys
  - Each node (except root) has at least `order - 1` keys
  - Must be >= 2

### Methods

| Method | Description |
|--------|-------------|
| `bt[key]` | Get value for key (raises `KeyError` if not found) |
| `bt[key] = value` | Insert or update key-value pair |
| `del bt[key]` | Delete key (raises `KeyError` if not found) |
| `key in bt` | Check if key exists |
| `len(bt)` | Get number of items |
| `iter(bt)` | Iterate over keys in sorted order |
| `reversed(bt)` | Iterate over keys in reverse order |
| `bt.get(key, default=None)` | Get value or default if not found |
| `bt.setdefault(key, default=None)` | Insert default if key missing, return value |
| `bt.insert(key, value)` | Insert key-value pair |
| `bt.pop(key, default)` | Remove and return value |
| `bt.popitem(index=-1)` | Remove and return (key, value) at index (0=first, -1=last) |
| `bt.peekitem(index=-1)` | Return (key, value) at index without removing |
| `bt.update(other, **kwargs)` | Update with items from mapping/iterable |
| `bt.copy()` | Return a shallow copy |
| `bt.keys()` | Return list of all keys (sorted) |
| `bt.values()` | Return list of all values (key-sorted) |
| `bt.items()` | Return list of (key, value) tuples (sorted) |
| `bt.irange(min, max, inclusive)` | Iterate over keys in range |
| `bt.min()` | Return minimum key |
| `bt.max()` | Return maximum key |
| `bt.clear()` | Remove all items |
| `bt == other` | Test equality with another BTreeDict |

### Range Queries with `irange()`

The `irange()` method provides efficient iteration over a range of keys:

```python
bt = BTreeDict()
for i in range(100):
    bt[i] = i * 10

# Iterate over keys 20-30 (exclusive upper bound by default)
for key in bt.irange(20, 30):
    print(key)  # 20, 21, 22, ..., 29

# Include upper bound
list(bt.irange(20, 30, inclusive=(True, True)))  # [20, 21, ..., 30]

# No lower bound
list(bt.irange(max=5))  # [0, 1, 2, 3, 4]

# No upper bound
list(bt.irange(min=95))  # [95, 96, 97, 98, 99]
```

## B-Tree Properties

A B-tree of order `t` has the following properties:

1. Every node has at most `2t - 1` keys
2. Every node (except root) has at least `t - 1` keys
3. The root has at least 1 key (unless tree is empty)
4. All leaves appear at the same level
5. A non-leaf node with `k` keys has `k + 1` children
6. Keys within each node are sorted

### Choosing the Order

- **Small order (2-4)**: More balanced, more memory overhead per item
- **Large order (16-64)**: Better cache locality, good for disk-based storage
- **Default (64)**: Optimized for in-memory workloads with fewer node traversals

```python
# For in-memory use with many items (default)
bt = BTreeDict()

# For smaller datasets or tight memory constraints
bt = BTreeDict(order=3)
```

## Performance

| Operation | Time Complexity |
|-----------|-----------------|
| Search | O(log n) |
| Insert | O(log n) |
| Delete | O(log n) |
| Min/Max | O(log n) |
| Iteration | O(n) |

## When to Use B-Tree vs Dict

Use **B-Tree** when you need:
- Sorted iteration
- Range queries (min, max)
- Ordered key access

Use **dict** when you need:
- Fastest possible O(1) average lookup
- No ordering requirements

## BTreeDict vs SortedDict

Benchmark command: `python benchmarks/compare_sorteddict.py --benchmark`
(Python 3.14.2, default order=64, cache_i64=True, AMD Ryzen AI 7 PRO 350 w/ Radeon 860M, Jan 16, 2026).

### Speed (10,000 items)

| Operation | BTreeDict | SortedDict |
|-----------|-----------|------------|
| Sequential insert | 0.66 ms | 2.92 ms |
| Random insert | 0.99 ms | 4.73 ms |
| Random lookup | 1.10 ms | 0.26 ms |
| Contains check | 0.44 ms | 0.25 ms |
| Iteration (10x) | 0.35 ms | 0.45 ms |
| Random delete | 1.18 ms | 4.30 ms |
| Mixed ops | 1.57 ms | 2.76 ms |
| Update existing | 0.70 ms | 1.32 ms |
| keys/values/items (100x) | 14.79 ms | 67.30 ms |

### Speed (100,000 items)

| Operation | BTreeDict | SortedDict |
|-----------|-----------|------------|
| Sequential insert | 6.32 ms | 30.79 ms |
| Random insert | 16.64 ms | 62.05 ms |
| Random lookup | 17.64 ms | 7.92 ms |
| Contains check | 6.32 ms | 2.28 ms |
| Iteration (10x) | 5.53 ms | 4.04 ms |
| Random delete | 29.53 ms | 77.95 ms |
| Mixed ops | 23.81 ms | 53.31 ms |
| Update existing | 9.97 ms | 15.02 ms |
| keys/values/items (100x) | 289.52 ms | 876.95 ms |

### Memory (tracemalloc)

| Items | BTreeDict | SortedDict |
|-------|-----------|------------|
| 10,000 | 815.51 KB | 682.38 KB |
| 100,000 | 8.02 MB | 8.91 MB |
| 500,000 | 40.12 MB | 39.59 MB |

Summary: BTreeDict wins 13/18 benchmarks (average speedup 2.37x). SortedDict remains faster for read‑heavy workloads (lookup/contains/iteration), while BTreeDict is faster for inserts, deletes, updates, and bulk materialization.

## Project Structure

```
btree/
├── include/
│   └── btreeobject.h    # Public C API header
├── src/
│   └── btreemodule.c    # Main implementation
├── tests/
│   └── test_btree_comprehensive.py    # Comprehensive test suite
├── setup.py             # Build configuration
├── pyproject.toml       # Modern Python packaging
└── README.md            # This file
```

## License

MIT License
