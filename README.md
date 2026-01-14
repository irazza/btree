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
from btree import BTree

# Create a B-tree (default order=3)
bt = BTree()

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

### `BTree(order=3)`

Create a new B-tree with the specified order (minimum degree).

- **order**: The minimum degree of the B-tree (default: 3)
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
| `bt == other` | Test equality with another BTree |

### Range Queries with `irange()`

The `irange()` method provides efficient iteration over a range of keys:

```python
bt = BTree()
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
- **Default (3)**: Good general-purpose choice

```python
# For in-memory use with many items
bt = BTree(order=16)

# For small datasets
bt = BTree(order=3)
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

## Project Structure

```
btree/
├── include/
│   └── btreeobject.h    # Public C API header
├── src/
│   └── btreemodule.c    # Main implementation
├── tests/
│   └── test_btree.py    # Test suite
├── setup.py             # Build configuration
├── pyproject.toml       # Modern Python packaging
└── README.md            # This file
```

## License

MIT License
