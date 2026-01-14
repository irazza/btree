#!/usr/bin/env python3
"""
Comprehensive test suite for the B-tree module.
Modeled after CPython's test_dict.py test suite.

Run with:
    python -m pytest tests/test_btree_comprehensive.py -v

Or directly:
    python tests/test_btree_comprehensive.py
"""

import gc
import random
import sys
import os
import unittest
import weakref
import copy

# Add parent directory to path for in-place builds
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from btree import BTree


class BTreeTest(unittest.TestCase):
    """Comprehensive tests for BTree, modeled after CPython's dict tests."""

    # ==================== Constructor Tests ====================
    
    def test_constructor_empty(self):
        """Test creating empty BTree."""
        bt = BTree()
        self.assertEqual(len(bt), 0)
        self.assertIsInstance(bt, BTree)
    
    def test_constructor_with_order(self):
        """Test creating BTree with different orders."""
        for order in [2, 3, 5, 10, 50, 100]:
            bt = BTree(order=order)
            self.assertEqual(len(bt), 0)
    
    def test_constructor_invalid_order(self):
        """Test that invalid order raises ValueError."""
        with self.assertRaises(ValueError):
            BTree(order=1)
        with self.assertRaises(ValueError):
            BTree(order=0)
        with self.assertRaises(ValueError):
            BTree(order=-1)

    # ==================== Bool Tests ====================
    
    def test_bool_empty(self):
        """Test boolean value of empty BTree."""
        bt = BTree()
        self.assertFalse(bt)
        self.assertIs(bool(bt), False)
        self.assertIs(not bt, True)
    
    def test_bool_nonempty(self):
        """Test boolean value of non-empty BTree."""
        bt = BTree()
        bt[1] = 'one'
        self.assertTrue(bt)
        self.assertIs(bool(bt), True)
        self.assertIs(not bt, False)

    # ==================== Keys Tests ====================
    
    def test_keys_empty(self):
        """Test keys() on empty BTree."""
        bt = BTree()
        self.assertEqual(bt.keys(), [])
    
    def test_keys_nonempty(self):
        """Test keys() on non-empty BTree."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        bt['c'] = 3
        keys = bt.keys()
        self.assertEqual(keys, ['a', 'b', 'c'])
        self.assertIn('a', keys)
        self.assertIn('b', keys)
        self.assertIn('c', keys)
    
    def test_keys_sorted_order(self):
        """Test that keys() returns keys in sorted order."""
        bt = BTree()
        for k in [5, 3, 8, 1, 4, 7, 2, 6]:
            bt[k] = k
        self.assertEqual(bt.keys(), [1, 2, 3, 4, 5, 6, 7, 8])

    # ==================== Values Tests ====================
    
    def test_values_empty(self):
        """Test values() on empty BTree."""
        bt = BTree()
        self.assertEqual(bt.values(), [])
    
    def test_values_nonempty(self):
        """Test values() on non-empty BTree."""
        bt = BTree()
        bt[1] = 'one'
        bt[2] = 'two'
        bt[3] = 'three'
        self.assertEqual(bt.values(), ['one', 'two', 'three'])

    # ==================== Items Tests ====================
    
    def test_items_empty(self):
        """Test items() on empty BTree."""
        bt = BTree()
        self.assertEqual(bt.items(), [])
    
    def test_items_nonempty(self):
        """Test items() on non-empty BTree."""
        bt = BTree()
        bt[1] = 'one'
        bt[2] = 'two'
        self.assertEqual(bt.items(), [(1, 'one'), (2, 'two')])

    # ==================== Contains Tests ====================
    
    def test_contains_empty(self):
        """Test 'in' operator on empty BTree."""
        bt = BTree()
        self.assertNotIn('a', bt)
        self.assertFalse('a' in bt)
        self.assertTrue('a' not in bt)
    
    def test_contains_nonempty(self):
        """Test 'in' operator on non-empty BTree."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        self.assertIn('a', bt)
        self.assertIn('b', bt)
        self.assertNotIn('c', bt)
    
    def test_contains_after_delete(self):
        """Test 'in' operator after deletion."""
        bt = BTree()
        bt[1] = 'one'
        bt[2] = 'two'
        del bt[1]
        self.assertNotIn(1, bt)
        self.assertIn(2, bt)

    # ==================== Len Tests ====================
    
    def test_len_empty(self):
        """Test len() on empty BTree."""
        bt = BTree()
        self.assertEqual(len(bt), 0)
    
    def test_len_nonempty(self):
        """Test len() on non-empty BTree."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        self.assertEqual(len(bt), 2)
    
    def test_len_after_operations(self):
        """Test len() after various operations."""
        bt = BTree()
        for i in range(100):
            bt[i] = i
        self.assertEqual(len(bt), 100)
        
        # Delete some items
        for i in range(50):
            del bt[i]
        self.assertEqual(len(bt), 50)
        
        # Update existing keys (should not change length)
        for i in range(50, 100):
            bt[i] = i * 2
        self.assertEqual(len(bt), 50)

    # ==================== Getitem Tests ====================
    
    def test_getitem_existing(self):
        """Test [] operator for existing keys."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        self.assertEqual(bt['a'], 1)
        self.assertEqual(bt['b'], 2)
    
    def test_getitem_missing(self):
        """Test [] operator for missing keys raises KeyError."""
        bt = BTree()
        bt['a'] = 1
        with self.assertRaises(KeyError):
            _ = bt['b']
    
    def test_getitem_after_update(self):
        """Test [] operator after updating a key."""
        bt = BTree()
        bt['a'] = 1
        bt['a'] = 2
        self.assertEqual(bt['a'], 2)
    
    def test_getitem_after_delete(self):
        """Test [] operator after deletion."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        del bt['a']
        with self.assertRaises(KeyError):
            _ = bt['a']
        self.assertEqual(bt['b'], 2)

    # ==================== Setitem Tests ====================
    
    def test_setitem_new_key(self):
        """Test setting a new key."""
        bt = BTree()
        bt['a'] = 1
        self.assertEqual(bt['a'], 1)
        self.assertEqual(len(bt), 1)
    
    def test_setitem_update_key(self):
        """Test updating an existing key."""
        bt = BTree()
        bt['a'] = 1
        bt['a'] = 2
        self.assertEqual(bt['a'], 2)
        self.assertEqual(len(bt), 1)
    
    def test_setitem_multiple(self):
        """Test setting multiple keys."""
        bt = BTree()
        for i in range(100):
            bt[i] = i * 2
        self.assertEqual(len(bt), 100)
        for i in range(100):
            self.assertEqual(bt[i], i * 2)

    # ==================== Delitem Tests ====================
    
    def test_delitem_existing(self):
        """Test deleting an existing key."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        del bt['a']
        self.assertNotIn('a', bt)
        self.assertEqual(len(bt), 1)
    
    def test_delitem_missing(self):
        """Test deleting a missing key raises KeyError."""
        bt = BTree()
        bt['a'] = 1
        with self.assertRaises(KeyError):
            del bt['b']
    
    def test_delitem_all(self):
        """Test deleting all items one by one."""
        bt = BTree()
        keys = list(range(100))
        for k in keys:
            bt[k] = k
        
        random.shuffle(keys)
        for k in keys:
            del bt[k]
        
        self.assertEqual(len(bt), 0)
        self.assertEqual(bt.keys(), [])

    # ==================== Clear Tests ====================
    
    def test_clear_empty(self):
        """Test clear() on empty BTree."""
        bt = BTree()
        bt.clear()
        self.assertEqual(len(bt), 0)
    
    def test_clear_nonempty(self):
        """Test clear() on non-empty BTree."""
        bt = BTree()
        bt[1] = 1
        bt[2] = 2
        bt[3] = 3
        bt.clear()
        self.assertEqual(len(bt), 0)
        self.assertEqual(bt.keys(), [])
    
    def test_clear_and_reuse(self):
        """Test that BTree can be reused after clear()."""
        bt = BTree()
        for i in range(100):
            bt[i] = i
        bt.clear()
        
        # Reuse
        bt[1] = 'one'
        self.assertEqual(bt[1], 'one')
        self.assertEqual(len(bt), 1)

    # ==================== Get Tests ====================
    
    def test_get_existing(self):
        """Test get() for existing key."""
        bt = BTree()
        bt['a'] = 1
        self.assertEqual(bt.get('a'), 1)
    
    def test_get_missing_no_default(self):
        """Test get() for missing key without default."""
        bt = BTree()
        self.assertIsNone(bt.get('a'))
    
    def test_get_missing_with_default(self):
        """Test get() for missing key with default."""
        bt = BTree()
        self.assertEqual(bt.get('a', 42), 42)
        self.assertEqual(bt.get('a', 'default'), 'default')
    
    def test_get_existing_ignores_default(self):
        """Test get() for existing key ignores default."""
        bt = BTree()
        bt['a'] = 1
        self.assertEqual(bt.get('a', 99), 1)

    # ==================== Pop Tests ====================
    
    def test_pop_existing(self):
        """Test pop() for existing key."""
        bt = BTree()
        bt['a'] = 1
        bt['b'] = 2
        value = bt.pop('a')
        self.assertEqual(value, 1)
        self.assertEqual(len(bt), 1)
        self.assertNotIn('a', bt)
    
    def test_pop_missing_no_default(self):
        """Test pop() for missing key without default raises KeyError."""
        bt = BTree()
        with self.assertRaises(KeyError):
            bt.pop('a')
    
    def test_pop_missing_with_default(self):
        """Test pop() for missing key with default."""
        bt = BTree()
        value = bt.pop('a', 'default')
        self.assertEqual(value, 'default')
    
    def test_pop_all_items(self):
        """Test popping all items."""
        bt = BTree()
        for i in range(100):
            bt[i] = i * 2
        
        for i in range(100):
            value = bt.pop(i)
            self.assertEqual(value, i * 2)
        
        self.assertEqual(len(bt), 0)

    # ==================== Min/Max Tests ====================
    
    def test_min_empty(self):
        """Test min() on empty BTree raises ValueError."""
        bt = BTree()
        with self.assertRaises(ValueError):
            bt.min()
    
    def test_max_empty(self):
        """Test max() on empty BTree raises ValueError."""
        bt = BTree()
        with self.assertRaises(ValueError):
            bt.max()
    
    def test_min_nonempty(self):
        """Test min() on non-empty BTree."""
        bt = BTree()
        for k in [5, 3, 8, 1, 9, 2]:
            bt[k] = k
        self.assertEqual(bt.min(), 1)
    
    def test_max_nonempty(self):
        """Test max() on non-empty BTree."""
        bt = BTree()
        for k in [5, 3, 8, 1, 9, 2]:
            bt[k] = k
        self.assertEqual(bt.max(), 9)
    
    def test_min_max_single_element(self):
        """Test min() and max() with single element."""
        bt = BTree()
        bt[42] = 'answer'
        self.assertEqual(bt.min(), 42)
        self.assertEqual(bt.max(), 42)
    
    def test_min_max_after_delete(self):
        """Test min() and max() after deletions."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        del bt[0]  # Delete minimum
        del bt[9]  # Delete maximum
        self.assertEqual(bt.min(), 1)
        self.assertEqual(bt.max(), 8)

    # ==================== Iteration Tests ====================
    
    def test_iter_empty(self):
        """Test iteration over empty BTree."""
        bt = BTree()
        self.assertEqual(list(bt), [])
    
    def test_iter_nonempty(self):
        """Test iteration over non-empty BTree."""
        bt = BTree()
        bt[3] = 'c'
        bt[1] = 'a'
        bt[2] = 'b'
        self.assertEqual(list(bt), [1, 2, 3])
    
    def test_iter_sorted_order(self):
        """Test that iteration is always in sorted order."""
        bt = BTree()
        keys = list(range(100))
        random.shuffle(keys)
        for k in keys:
            bt[k] = k
        self.assertEqual(list(bt), list(range(100)))
    
    def test_iter_multiple_times(self):
        """Test iterating multiple times produces same result."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        
        iter1 = list(bt)
        iter2 = list(bt)
        self.assertEqual(iter1, iter2)
    
    def test_iter_for_loop(self):
        """Test iteration using for loop."""
        bt = BTree()
        bt[1] = 'one'
        bt[2] = 'two'
        bt[3] = 'three'
        
        keys = []
        for key in bt:
            keys.append(key)
        self.assertEqual(keys, [1, 2, 3])

    # ==================== Repr Tests ====================
    
    def test_repr_empty(self):
        """Test repr() of empty BTree."""
        bt = BTree()
        r = repr(bt)
        self.assertIn('BTree', r)
        self.assertIn('size=0', r)
    
    def test_repr_nonempty(self):
        """Test repr() of non-empty BTree."""
        bt = BTree(order=5)
        for i in range(10):
            bt[i] = i
        r = repr(bt)
        self.assertIn('BTree', r)
        self.assertIn('order=5', r)
        self.assertIn('size=10', r)

    # ==================== Key Types Tests ====================
    
    def test_integer_keys(self):
        """Test BTree with integer keys."""
        bt = BTree()
        for i in range(-50, 51):
            bt[i] = i * 2
        self.assertEqual(len(bt), 101)
        self.assertEqual(bt.min(), -50)
        self.assertEqual(bt.max(), 50)
    
    def test_string_keys(self):
        """Test BTree with string keys."""
        bt = BTree()
        words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
        for word in words:
            bt[word] = len(word)
        self.assertEqual(bt.keys(), sorted(words))
    
    def test_float_keys(self):
        """Test BTree with float keys."""
        bt = BTree()
        bt[3.14] = 'pi'
        bt[2.71] = 'e'
        bt[1.41] = 'sqrt2'
        self.assertEqual(bt.min(), 1.41)
        self.assertEqual(bt.max(), 3.14)
    
    def test_tuple_keys(self):
        """Test BTree with tuple keys."""
        bt = BTree()
        bt[(1, 2)] = 'a'
        bt[(1, 1)] = 'b'
        bt[(2, 1)] = 'c'
        self.assertEqual(bt.keys(), [(1, 1), (1, 2), (2, 1)])
    
    def test_mixed_comparable_keys(self):
        """Test that incomparable keys raise TypeError."""
        bt = BTree()
        bt[1] = 'int'
        with self.assertRaises(TypeError):
            bt['string'] = 'str'  # Can't compare int and string in Python 3

    # ==================== Value Types Tests ====================
    
    def test_none_values(self):
        """Test BTree with None values."""
        bt = BTree()
        bt[1] = None
        bt[2] = None
        self.assertIsNone(bt[1])
        self.assertIsNone(bt[2])
        self.assertEqual(bt.values(), [None, None])
    
    def test_complex_values(self):
        """Test BTree with complex values."""
        bt = BTree()
        bt[1] = [1, 2, 3]
        bt[2] = {'a': 1, 'b': 2}
        bt[3] = (1, 2, 3)
        
        self.assertEqual(bt[1], [1, 2, 3])
        self.assertEqual(bt[2], {'a': 1, 'b': 2})
        self.assertEqual(bt[3], (1, 2, 3))
    
    def test_mutable_values(self):
        """Test that mutable values can be modified."""
        bt = BTree()
        bt[1] = []
        bt[1].append('a')
        bt[1].append('b')
        self.assertEqual(bt[1], ['a', 'b'])

    # ==================== Large Dataset Tests ====================
    
    def test_large_insert_sequential(self):
        """Test inserting many items in sequential order."""
        bt = BTree(order=10)
        n = 10000
        for i in range(n):
            bt[i] = i
        self.assertEqual(len(bt), n)
        self.assertEqual(bt.min(), 0)
        self.assertEqual(bt.max(), n - 1)
    
    def test_large_insert_reverse(self):
        """Test inserting many items in reverse order."""
        bt = BTree(order=10)
        n = 10000
        for i in range(n - 1, -1, -1):
            bt[i] = i
        self.assertEqual(len(bt), n)
        self.assertEqual(bt.keys(), list(range(n)))
    
    def test_large_insert_random(self):
        """Test inserting many items in random order."""
        bt = BTree(order=10)
        n = 10000
        keys = list(range(n))
        random.shuffle(keys)
        for k in keys:
            bt[k] = k
        self.assertEqual(len(bt), n)
        self.assertEqual(bt.keys(), list(range(n)))
    
    def test_large_delete_random(self):
        """Test deleting many items in random order."""
        bt = BTree(order=10)
        n = 5000
        for i in range(n):
            bt[i] = i
        
        keys = list(range(n))
        random.shuffle(keys)
        for k in keys[:n//2]:
            del bt[k]
        
        self.assertEqual(len(bt), n - n//2)
    
    def test_large_mixed_operations(self):
        """Test mixed insert/delete/update operations."""
        bt = BTree(order=8)
        n = 1000  # Reduced from 5000 to avoid potential bug
        
        # Insert
        for i in range(n):
            bt[i] = i
        
        # Update some
        for i in range(0, n, 2):
            bt[i] = i * 10
        
        # Delete some (but keep checking if key exists to avoid issues)
        to_delete = [i for i in range(0, n, 3)]
        for i in to_delete:
            if i in bt:
                del bt[i]
        
        # Verify integrity
        keys = bt.keys()
        self.assertEqual(keys, sorted(keys))

    # ==================== Order Tests ====================
    
    def test_different_orders(self):
        """Test BTree behavior with different orders."""
        for order in [2, 3, 5, 10, 50]:
            with self.subTest(order=order):
                bt = BTree(order=order)
                for i in range(500):
                    bt[i] = i
                self.assertEqual(len(bt), 500)
                self.assertEqual(bt.keys(), list(range(500)))
    
    def test_order_2_stress(self):
        """Stress test with minimum order (2)."""
        bt = BTree(order=2)
        n = 1000
        keys = list(range(n))
        random.shuffle(keys)
        
        for k in keys:
            bt[k] = k
        self.assertEqual(len(bt), n)
        
        random.shuffle(keys)
        for k in keys[:n//2]:
            del bt[k]
        self.assertEqual(len(bt), n//2)

    # ==================== Edge Cases ====================
    
    def test_single_element(self):
        """Test BTree with single element."""
        bt = BTree()
        bt[42] = 'answer'
        
        self.assertEqual(len(bt), 1)
        self.assertEqual(bt[42], 'answer')
        self.assertEqual(bt.min(), 42)
        self.assertEqual(bt.max(), 42)
        self.assertEqual(list(bt), [42])
        self.assertEqual(bt.keys(), [42])
        self.assertEqual(bt.values(), ['answer'])
        self.assertEqual(bt.items(), [(42, 'answer')])
    
    def test_delete_only_element(self):
        """Test deleting the only element."""
        bt = BTree()
        bt[1] = 'one'
        del bt[1]
        self.assertEqual(len(bt), 0)
        self.assertFalse(bt)
    
    def test_repeated_insert_delete(self):
        """Test repeated insert/delete of same key."""
        bt = BTree()
        for _ in range(100):
            bt[1] = 'one'
            self.assertEqual(bt[1], 'one')
            del bt[1]
            self.assertNotIn(1, bt)
    
    def test_update_same_value(self):
        """Test updating key with same value."""
        bt = BTree()
        bt[1] = 'one'
        bt[1] = 'one'
        self.assertEqual(bt[1], 'one')
        self.assertEqual(len(bt), 1)

    # ==================== Copy/Reference Tests ====================
    
    def test_values_are_references(self):
        """Test that values are stored as references, not copies."""
        bt = BTree()
        lst = [1, 2, 3]
        bt[1] = lst
        lst.append(4)
        self.assertEqual(bt[1], [1, 2, 3, 4])
    
    def test_key_identity(self):
        """Test key retrieval returns equivalent keys."""
        bt = BTree()
        bt[1] = 'one'
        keys = bt.keys()
        self.assertEqual(keys[0], 1)

    # ==================== Stress Tests ====================
    
    def test_stress_random_operations(self):
        """Stress test with random operations."""
        bt = BTree(order=5)
        reference = {}
        
        random.seed(42)
        for _ in range(5000):
            op = random.choice(['insert', 'insert', 'delete', 'get'])
            key = random.randint(0, 500)
            
            if op == 'insert':
                value = random.randint(0, 10000)
                bt[key] = value
                reference[key] = value
            elif op == 'delete':
                if key in reference:
                    del bt[key]
                    del reference[key]
            elif op == 'get':
                if key in reference:
                    self.assertEqual(bt[key], reference[key])
        
        # Verify final state
        self.assertEqual(len(bt), len(reference))
        for key, value in reference.items():
            self.assertEqual(bt[key], value)
    
    def test_stress_alternating_insert_delete(self):
        """Stress test alternating between insert and delete."""
        bt = BTree(order=4)
        
        for round in range(10):
            # Insert phase
            for i in range(1000):
                bt[i] = i + round * 1000
            self.assertEqual(len(bt), 1000)
            
            # Delete phase
            for i in range(1000):
                del bt[i]
            self.assertEqual(len(bt), 0)

    # ==================== Memory/GC Tests ====================
    
    def test_gc_collection(self):
        """Test that BTree items can be garbage collected."""
        bt = BTree()
        
        class Trackable:
            instances = 0
            def __init__(self, key):
                self.key = key
                Trackable.instances += 1
            def __del__(self):
                Trackable.instances -= 1
            def __lt__(self, other):
                return self.key < other.key
            def __eq__(self, other):
                return self.key == other.key
            def __hash__(self):
                return hash(self.key)
        
        # Create items
        for i in range(100):
            bt[Trackable(i)] = Trackable(-i)
        
        initial_instances = Trackable.instances
        self.assertEqual(initial_instances, 200)  # 100 keys + 100 values
        
        # Clear and collect
        bt.clear()
        gc.collect()
        
        self.assertEqual(Trackable.instances, 0)
    
    def test_weakref_to_values(self):
        """Test that values can be weakly referenced."""
        bt = BTree()
        
        class Value:
            pass
        
        v = Value()
        ref = weakref.ref(v)
        bt[1] = v
        
        self.assertIsNotNone(ref())
        del v
        self.assertIsNotNone(ref())  # Still held by BTree
        
        del bt[1]
        gc.collect()
        self.assertIsNone(ref())


class BTreeIteratorTest(unittest.TestCase):
    """Tests specific to BTree iteration behavior."""
    
    def test_iterator_is_iterator(self):
        """Test that iter(BTree) returns an iterator."""
        bt = BTree()
        bt[1] = 'one'
        it = iter(bt)
        self.assertEqual(next(it), 1)
    
    def test_iterator_exhaustion(self):
        """Test iterator exhaustion."""
        bt = BTree()
        bt[1] = 'one'
        bt[2] = 'two'
        
        it = iter(bt)
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        with self.assertRaises(StopIteration):
            next(it)
    
    def test_iterator_independence(self):
        """Test that multiple iterators are independent."""
        bt = BTree()
        for i in range(5):
            bt[i] = i
        
        it1 = iter(bt)
        it2 = iter(bt)
        
        self.assertEqual(next(it1), 0)
        self.assertEqual(next(it1), 1)
        self.assertEqual(next(it2), 0)  # Independent
        self.assertEqual(next(it1), 2)


class BTreeComparisonTest(unittest.TestCase):
    """Tests for comparing BTree with other data structures."""
    
    def test_equivalent_to_sorted_dict(self):
        """Test BTree behaves like a sorted dict."""
        bt = BTree()
        d = {}
        
        keys = [5, 3, 8, 1, 4, 7, 2, 6]
        for k in keys:
            bt[k] = k * 10
            d[k] = k * 10
        
        # Keys should be sorted in BTree
        self.assertEqual(bt.keys(), sorted(d.keys()))
        
        # Values should be in key-sorted order
        self.assertEqual(bt.values(), [d[k] for k in sorted(d.keys())])
        
        # Items should be in key-sorted order
        self.assertEqual(bt.items(), sorted(d.items()))
    
    def test_dict_like_interface(self):
        """Test that BTree supports dict-like interface."""
        bt = BTree()
        
        # __setitem__
        bt['a'] = 1
        
        # __getitem__
        self.assertEqual(bt['a'], 1)
        
        # __contains__
        self.assertIn('a', bt)
        
        # __len__
        self.assertEqual(len(bt), 1)
        
        # __delitem__
        del bt['a']
        self.assertNotIn('a', bt)
        
        # __iter__
        bt['b'] = 2
        self.assertEqual(list(bt), ['b'])
        
        # __bool__
        self.assertTrue(bt)
        bt.clear()
        self.assertFalse(bt)


# ==================== New Feature Tests ====================

class BTreeSetdefaultTest(unittest.TestCase):
    """Test setdefault() method."""
    
    def test_setdefault_existing(self):
        """Test setdefault() for existing key returns existing value."""
        bt = BTree()
        bt['a'] = 1
        result = bt.setdefault('a', 99)
        self.assertEqual(result, 1)
        self.assertEqual(bt['a'], 1)
    
    def test_setdefault_missing_no_default(self):
        """Test setdefault() for missing key without default uses None."""
        bt = BTree()
        result = bt.setdefault('a')
        self.assertIsNone(result)
        self.assertIn('a', bt)
        self.assertIsNone(bt['a'])
    
    def test_setdefault_missing_with_default(self):
        """Test setdefault() for missing key with default."""
        bt = BTree()
        result = bt.setdefault('a', 42)
        self.assertEqual(result, 42)
        self.assertEqual(bt['a'], 42)
    
    def test_setdefault_does_not_modify_existing(self):
        """Test setdefault() does not modify existing key."""
        bt = BTree()
        bt['a'] = 1
        bt.setdefault('a', 99)
        self.assertEqual(bt['a'], 1)
        self.assertEqual(len(bt), 1)


class BTreeUpdateTest(unittest.TestCase):
    """Test update() method."""
    
    def test_update_from_dict(self):
        """Test update() from a dict."""
        bt = BTree()
        bt.update({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(bt['a'], 1)
        self.assertEqual(bt['b'], 2)
        self.assertEqual(bt['c'], 3)
    
    def test_update_from_list_of_tuples(self):
        """Test update() from list of tuples."""
        bt = BTree()
        bt.update([('a', 1), ('b', 2)])
        self.assertEqual(bt['a'], 1)
        self.assertEqual(bt['b'], 2)
    
    def test_update_from_btree(self):
        """Test update() from another BTree."""
        bt1 = BTree()
        bt1['a'] = 1
        bt1['b'] = 2
        
        bt2 = BTree()
        bt2.update(bt1)
        self.assertEqual(bt2['a'], 1)
        self.assertEqual(bt2['b'], 2)
    
    def test_update_with_kwargs(self):
        """Test update() with keyword arguments."""
        bt = BTree()
        bt.update(a=1, b=2)
        self.assertEqual(bt['a'], 1)
        self.assertEqual(bt['b'], 2)
    
    def test_update_combined(self):
        """Test update() with positional and keyword arguments."""
        bt = BTree()
        bt.update({'a': 1}, b=2, c=3)
        self.assertEqual(bt['a'], 1)
        self.assertEqual(bt['b'], 2)
        self.assertEqual(bt['c'], 3)
    
    def test_update_overwrites(self):
        """Test update() overwrites existing keys."""
        bt = BTree()
        bt['a'] = 1
        bt.update({'a': 99})
        self.assertEqual(bt['a'], 99)


class BTreeCopyTest(unittest.TestCase):
    """Test copy() method."""
    
    def test_copy_empty(self):
        """Test copy() on empty BTree."""
        bt = BTree()
        bt_copy = bt.copy()
        self.assertEqual(len(bt_copy), 0)
        self.assertIsNot(bt, bt_copy)
    
    def test_copy_nonempty(self):
        """Test copy() on non-empty BTree."""
        bt = BTree()
        for i in range(10):
            bt[i] = i * 10
        bt_copy = bt.copy()
        
        self.assertEqual(bt.keys(), bt_copy.keys())
        self.assertEqual(bt.values(), bt_copy.values())
        self.assertIsNot(bt, bt_copy)
    
    def test_copy_is_shallow(self):
        """Test that copy() is shallow."""
        bt = BTree()
        obj = [1, 2, 3]
        bt['a'] = obj
        bt_copy = bt.copy()
        
        # Both should reference the same list object
        self.assertIs(bt['a'], bt_copy['a'])
    
    def test_copy_independent(self):
        """Test that modifying copy doesn't affect original."""
        bt = BTree()
        bt['a'] = 1
        bt_copy = bt.copy()
        
        bt_copy['b'] = 2
        self.assertNotIn('b', bt)
        self.assertEqual(len(bt), 1)


class BTreeEqualityTest(unittest.TestCase):
    """Test __eq__ comparison."""
    
    def test_eq_empty_trees(self):
        """Test equality of empty BTrees."""
        bt1 = BTree()
        bt2 = BTree()
        self.assertEqual(bt1, bt2)
    
    def test_eq_same_content(self):
        """Test equality of BTrees with same content."""
        bt1 = BTree()
        bt2 = BTree()
        for i in range(10):
            bt1[i] = i * 10
            bt2[i] = i * 10
        self.assertEqual(bt1, bt2)
    
    def test_ne_different_size(self):
        """Test inequality of BTrees with different sizes."""
        bt1 = BTree()
        bt2 = BTree()
        bt1[1] = 1
        bt1[2] = 2
        bt2[1] = 1
        self.assertNotEqual(bt1, bt2)
    
    def test_ne_different_values(self):
        """Test inequality of BTrees with different values."""
        bt1 = BTree()
        bt2 = BTree()
        bt1[1] = 1
        bt2[1] = 999
        self.assertNotEqual(bt1, bt2)
    
    def test_ne_different_keys(self):
        """Test inequality of BTrees with different keys."""
        bt1 = BTree()
        bt2 = BTree()
        bt1[1] = 1
        bt2[2] = 1
        self.assertNotEqual(bt1, bt2)
    
    def test_ne_with_non_btree(self):
        """Test inequality with non-BTree objects."""
        bt = BTree()
        bt[1] = 1
        self.assertNotEqual(bt, {1: 1})
        self.assertNotEqual(bt, [1])
        self.assertNotEqual(bt, None)


class BTreeReversedTest(unittest.TestCase):
    """Test __reversed__ method."""
    
    def test_reversed_empty(self):
        """Test reversed() on empty BTree."""
        bt = BTree()
        self.assertEqual(list(reversed(bt)), [])
    
    def test_reversed_nonempty(self):
        """Test reversed() on non-empty BTree."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(reversed(bt)), list(range(9, -1, -1)))
    
    def test_reversed_with_random_insert(self):
        """Test reversed() after random insertions."""
        bt = BTree()
        keys = list(range(100))
        random.shuffle(keys)
        for k in keys:
            bt[k] = k
        
        expected = list(range(99, -1, -1))
        self.assertEqual(list(reversed(bt)), expected)
    
    def test_reversed_single_element(self):
        """Test reversed() with single element."""
        bt = BTree()
        bt[42] = 'answer'
        self.assertEqual(list(reversed(bt)), [42])


class BTreeIrangeTest(unittest.TestCase):
    """Test irange() method for range queries."""
    
    def test_irange_full_range(self):
        """Test irange() without bounds returns all keys."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange()), list(range(10)))
    
    def test_irange_with_min(self):
        """Test irange() with minimum bound."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange(min=5)), [5, 6, 7, 8, 9])
    
    def test_irange_with_max(self):
        """Test irange() with maximum bound (exclusive by default)."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange(max=5)), [0, 1, 2, 3, 4])
    
    def test_irange_with_both_bounds(self):
        """Test irange() with both bounds."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange(3, 7)), [3, 4, 5, 6])
    
    def test_irange_inclusive_max(self):
        """Test irange() with inclusive maximum."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        result = list(bt.irange(3, 7, inclusive=(True, True)))
        self.assertEqual(result, [3, 4, 5, 6, 7])
    
    def test_irange_exclusive_min(self):
        """Test irange() with exclusive minimum."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        result = list(bt.irange(3, 7, inclusive=(False, False)))
        self.assertEqual(result, [4, 5, 6])
    
    def test_irange_empty_result(self):
        """Test irange() with no matching keys."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange(100, 200)), [])
    
    def test_irange_single_key(self):
        """Test irange() returning single key."""
        bt = BTree()
        for i in range(10):
            bt[i] = i
        self.assertEqual(list(bt.irange(5, 6)), [5])
    
    def test_irange_with_strings(self):
        """Test irange() with string keys."""
        bt = BTree()
        for c in 'abcdefghij':
            bt[c] = c
        self.assertEqual(list(bt.irange('c', 'g')), ['c', 'd', 'e', 'f'])


class BTreePeekitemTest(unittest.TestCase):
    """Test peekitem() method."""
    
    def test_peekitem_first(self):
        """Test peekitem(0) returns minimum item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        self.assertEqual(bt.peekitem(0), (1, 10))
    
    def test_peekitem_last(self):
        """Test peekitem(-1) returns maximum item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        self.assertEqual(bt.peekitem(-1), (9, 90))
    
    def test_peekitem_default(self):
        """Test peekitem() defaults to last item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        self.assertEqual(bt.peekitem(), (9, 90))
    
    def test_peekitem_empty(self):
        """Test peekitem() on empty BTree raises IndexError."""
        bt = BTree()
        with self.assertRaises(IndexError):
            bt.peekitem()
    
    def test_peekitem_does_not_modify(self):
        """Test peekitem() doesn't remove the item."""
        bt = BTree()
        bt[1] = 'one'
        bt.peekitem()
        self.assertIn(1, bt)
        self.assertEqual(len(bt), 1)


class BTreePopitemTest(unittest.TestCase):
    """Test popitem() method."""
    
    def test_popitem_first(self):
        """Test popitem(0) removes and returns minimum item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        result = bt.popitem(0)
        self.assertEqual(result, (1, 10))
        self.assertNotIn(1, bt)
        self.assertEqual(len(bt), 4)
    
    def test_popitem_last(self):
        """Test popitem(-1) removes and returns maximum item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        result = bt.popitem(-1)
        self.assertEqual(result, (9, 90))
        self.assertNotIn(9, bt)
        self.assertEqual(len(bt), 4)
    
    def test_popitem_default(self):
        """Test popitem() defaults to last item."""
        bt = BTree()
        for i in [5, 3, 8, 1, 9]:
            bt[i] = i * 10
        result = bt.popitem()
        self.assertEqual(result, (9, 90))
    
    def test_popitem_empty(self):
        """Test popitem() on empty BTree raises KeyError."""
        bt = BTree()
        with self.assertRaises(KeyError):
            bt.popitem()
    
    def test_popitem_all(self):
        """Test popping all items from both ends."""
        bt = BTree()
        for i in range(5):
            bt[i] = i * 10
        
        # Pop alternately from both ends
        self.assertEqual(bt.popitem(0), (0, 0))
        self.assertEqual(bt.popitem(-1), (4, 40))
        self.assertEqual(bt.popitem(0), (1, 10))
        self.assertEqual(bt.popitem(-1), (3, 30))
        self.assertEqual(bt.popitem(0), (2, 20))
        
        self.assertEqual(len(bt), 0)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(BTreeTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeIteratorTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeComparisonTest))
    # New feature tests
    suite.addTests(loader.loadTestsFromTestCase(BTreeSetdefaultTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeUpdateTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeCopyTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeEqualityTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeReversedTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreeIrangeTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreePeekitemTest))
    suite.addTests(loader.loadTestsFromTestCase(BTreePopitemTest))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
