#!/usr/bin/env python3
"""
Test suite for the B-tree module.

Run with:
    python -m pytest tests/test_btree.py -v

Or directly:
    python tests/test_btree.py
"""

import sys
import os

# Add parent directory to path for in-place builds
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_operations():
    """Test basic insert, search, delete operations."""
    from btree import BTree
    
    bt = BTree()
    
    # Test empty tree
    assert len(bt) == 0
    assert 1 not in bt
    
    # Test insert
    bt[1] = "one"
    assert len(bt) == 1
    assert bt[1] == "one"
    assert 1 in bt
    
    # Test multiple inserts
    bt[5] = "five"
    bt[3] = "three"
    bt[7] = "seven"
    bt[2] = "two"
    
    assert len(bt) == 5
    assert bt[3] == "three"
    assert bt[7] == "seven"
    
    # Test update existing key
    bt[3] = "THREE"
    assert len(bt) == 5  # Size unchanged
    assert bt[3] == "THREE"
    
    # Test delete
    del bt[3]
    assert len(bt) == 4
    assert 3 not in bt


def test_sorted_iteration():
    """Test that keys are iterated in sorted order."""
    from btree import BTree
    
    bt = BTree()
    keys = [5, 3, 8, 1, 4, 7, 2, 6]
    
    for k in keys:
        bt[k] = k * 10
    
    # Test iteration order
    result = list(bt)
    assert result == sorted(keys)
    
    # Test keys()
    assert bt.keys() == sorted(keys)
    
    # Test values()
    assert bt.values() == [k * 10 for k in sorted(keys)]
    
    # Test items()
    assert bt.items() == [(k, k * 10) for k in sorted(keys)]


def test_min_max():
    """Test min() and max() methods."""
    from btree import BTree
    
    bt = BTree()
    
    # Test empty tree
    try:
        bt.min()
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    try:
        bt.max()
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    # Test with data
    for k in [5, 3, 8, 1, 9, 2]:
        bt[k] = str(k)
    
    assert bt.min() == 1
    assert bt.max() == 9


def test_get_method():
    """Test get() method with default values."""
    from btree import BTree
    
    bt = BTree()
    bt[1] = "one"
    bt[2] = "two"
    
    assert bt.get(1) == "one"
    assert bt.get(3) is None
    assert bt.get(3, "default") == "default"
    assert bt.get(3, 42) == 42


def test_pop_method():
    """Test pop() method."""
    from btree import BTree
    
    bt = BTree()
    bt[1] = "one"
    bt[2] = "two"
    bt[3] = "three"
    
    # Pop existing key
    value = bt.pop(2)
    assert value == "two"
    assert len(bt) == 2
    assert 2 not in bt
    
    # Pop with default
    value = bt.pop(10, "not found")
    assert value == "not found"
    
    # Pop non-existing without default
    try:
        bt.pop(10)
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_clear():
    """Test clear() method."""
    from btree import BTree
    
    bt = BTree()
    for i in range(100):
        bt[i] = i
    
    assert len(bt) == 100
    
    bt.clear()
    assert len(bt) == 0
    assert list(bt) == []
    
    # Can still use after clear
    bt[1] = "one"
    assert bt[1] == "one"


def test_different_orders():
    """Test B-trees with different orders."""
    from btree import BTree
    
    for order in [2, 3, 5, 10, 50]:
        bt = BTree(order=order)
        
        # Insert many items
        for i in range(1000):
            bt[i] = i * 2
        
        # Verify
        assert len(bt) == 1000
        assert bt.keys() == list(range(1000))
        assert bt[500] == 1000


def test_invalid_order():
    """Test that invalid order raises ValueError."""
    from btree import BTree
    
    try:
        bt = BTree(order=1)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
    
    try:
        bt = BTree(order=0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass


def test_key_error():
    """Test KeyError for missing keys."""
    from btree import BTree
    
    bt = BTree()
    bt[1] = "one"
    
    try:
        _ = bt[2]
        assert False, "Should raise KeyError"
    except KeyError:
        pass
    
    try:
        del bt[2]
        assert False, "Should raise KeyError"
    except KeyError:
        pass


def test_various_key_types():
    """Test with different key types."""
    from btree import BTree
    
    # String keys
    bt = BTree()
    bt["apple"] = 1
    bt["banana"] = 2
    bt["cherry"] = 3
    assert bt.keys() == ["apple", "banana", "cherry"]
    
    # Float keys
    bt2 = BTree()
    bt2[3.14] = "pi"
    bt2[2.71] = "e"
    bt2[1.41] = "sqrt2"
    assert bt2.min() == 1.41
    assert bt2.max() == 3.14


def test_large_dataset():
    """Test with a large number of items."""
    from btree import BTree
    import random
    
    bt = BTree(order=16)
    n = 10000
    
    # Insert in random order
    keys = list(range(n))
    random.shuffle(keys)
    
    for k in keys:
        bt[k] = k * 2
    
    assert len(bt) == n
    
    # Verify all keys present and sorted
    assert bt.keys() == list(range(n))
    
    # Verify values
    for k in keys[:100]:  # Spot check
        assert bt[k] == k * 2
    
    # Delete half
    random.shuffle(keys)
    for k in keys[:n//2]:
        del bt[k]
    
    assert len(bt) == n // 2


def test_repr():
    """Test string representation."""
    from btree import BTree
    
    bt = BTree(order=5)
    for i in range(10):
        bt[i] = i
    
    r = repr(bt)
    assert "BTree" in r
    assert "order=5" in r
    assert "size=10" in r


def run_all_tests():
    """Run all tests."""
    tests = [
        test_basic_operations,
        test_sorted_iteration,
        test_min_max,
        test_get_method,
        test_pop_method,
        test_clear,
        test_different_orders,
        test_invalid_order,
        test_key_error,
        test_various_key_types,
        test_large_dataset,
        test_repr,
    ]
    
    print("Running B-tree tests...\n")
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"  ✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    try:
        from btree import BTree
    except ImportError:
        print("Error: btree module not found.")
        print("Build it first with:")
        print("  cd /home/irazza/projects/btree")
        print("  pip install -e .")
        print("  # or: python setup.py build_ext --inplace")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
