/* B-Tree object implementation
 *
 * A B-tree is a self-balancing tree data structure that maintains sorted data
 * and allows searches, sequential access, insertions, and deletions in
 * logarithmic time. This implementation follows CPython's object model.
 *
 * Properties of B-tree of order t (minimum degree):
 * - Every node has at most 2t-1 keys
 * - Every node (except root) has at least t-1 keys
 * - Root has at least 1 key (unless tree is empty)
 * - All leaves appear at same level
 * - A non-leaf node with k keys has k+1 children
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* Default minimum degree (order) of the B-tree */
#define BTREE_DEFAULT_ORDER 8
#define BTREE_MIN_ORDER 2

/* ==================== BTreeNode Implementation ==================== */

typedef struct _PyBTreeNode {
    PyObject_HEAD
    Py_ssize_t n_keys;           /* Number of keys currently in node */
    int is_leaf;                  /* True if node is a leaf */
    PyObject **keys;              /* Array of keys (Python objects) */
    PyObject **values;            /* Array of values (Python objects) */
    struct _PyBTreeNode **children; /* Array of child pointers */
    int order;                    /* Order (t) - needed for node operations */
} PyBTreeNode;

/* Forward declarations */
static PyTypeObject PyBTreeNode_Type;
static PyObject *btreenode_new(int order, int is_leaf);
static void btreenode_dealloc(PyObject *self);
static int btreenode_traverse(PyObject *self, visitproc visit, void *arg);
static int btreenode_clear(PyObject *self);

/* Create a new B-tree node */
static PyObject *
btreenode_new(int order, int is_leaf)
{
    PyBTreeNode *node;
    Py_ssize_t max_keys = 2 * order - 1;
    Py_ssize_t max_children = 2 * order;
    size_t keys_size, values_size, children_size;
    char *block;

    node = PyObject_GC_New(PyBTreeNode, &PyBTreeNode_Type);
    if (node == NULL) {
        return NULL;
    }

    node->n_keys = 0;
    node->is_leaf = is_leaf;
    node->order = order;

    /* Allocate arrays for keys, values, and children in one block */
    keys_size = max_keys * sizeof(PyObject *);
    values_size = max_keys * sizeof(PyObject *);
    children_size = is_leaf ? 0 : max_children * sizeof(PyBTreeNode *);

    block = (char *)PyMem_Calloc(1, keys_size + values_size + children_size);
    if (block == NULL) {
        Py_DECREF(node);
        return PyErr_NoMemory();
    }

    node->keys = (PyObject **)block;
    node->values = (PyObject **)(block + keys_size);
    
    if (!is_leaf) {
        node->children = (PyBTreeNode **)(block + keys_size + values_size);
    } else {
        node->children = NULL;
    }

    PyObject_GC_Track((PyObject *)node);
    return (PyObject *)node;
}

static void
btreenode_dealloc(PyObject *self)
{
    PyBTreeNode *node = (PyBTreeNode *)self;
    Py_ssize_t i;

    PyObject_GC_UnTrack(self);

    /* Decref all keys */
    if (node->keys) {
        for (i = 0; i < node->n_keys; i++) {
            Py_XDECREF(node->keys[i]);
        }
        /* node->keys points to the start of the allocated block */
        /* keys, values, children are in one block, so freeing keys frees all */
        /* But we must loop over values/children to decref them first */
    }

    /* Decref all values */
    if (node->values) {
        for (i = 0; i < node->n_keys; i++) {
            Py_XDECREF(node->values[i]);
        }
    }

    /* Decref all children */
    if (node->children) {
        Py_ssize_t max_children = 2 * node->order;
        for (i = 0; i <= node->n_keys && i < max_children; i++) {
            Py_XDECREF(node->children[i]);
        }
    }

    if (node->keys) {
        PyMem_Free(node->keys);
    }

    Py_TYPE(self)->tp_free(self);
}

static int
btreenode_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyBTreeNode *node = (PyBTreeNode *)self;
    Py_ssize_t i;

    for (i = 0; i < node->n_keys; i++) {
        Py_VISIT(node->keys[i]);
        Py_VISIT(node->values[i]);
    }

    if (node->children) {
        for (i = 0; i <= node->n_keys; i++) {
            Py_VISIT(node->children[i]);
        }
    }

    return 0;
}

static int
btreenode_clear(PyObject *self)
{
    PyBTreeNode *node = (PyBTreeNode *)self;
    Py_ssize_t i;

    for (i = 0; i < node->n_keys; i++) {
        Py_CLEAR(node->keys[i]);
        Py_CLEAR(node->values[i]);
    }

    if (node->children) {
        for (i = 0; i <= node->n_keys; i++) {
            Py_CLEAR(node->children[i]);
        }
    }

    node->n_keys = 0;
    return 0;
}

static PyTypeObject PyBTreeNode_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_btree.BTreeNode",                         /* tp_name */
    sizeof(PyBTreeNode),                        /* tp_basicsize */
    0,                                          /* tp_itemsize */
    btreenode_dealloc,                          /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    btreenode_traverse,                         /* tp_traverse */
    btreenode_clear,                            /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    0,                                          /* tp_new */
    PyObject_GC_Del,                            /* tp_free */
};

/* ==================== BTree Implementation ==================== */

typedef struct _PyBTreeObject {
    PyObject_HEAD
    PyBTreeNode *root;           /* Root node of the tree */
    Py_ssize_t size;             /* Total number of key-value pairs */
    int order;                    /* Order (minimum degree) of the B-tree */
} PyBTreeObject;

/* Forward declarations */
static PyTypeObject PyBTree_Type;

/* Type check macro */
#define PyBTree_Check(op) PyObject_TypeCheck((op), &PyBTree_Type)

static void btree_dealloc(PyObject *self);
static int btree_traverse(PyObject *self, visitproc visit, void *arg);
static int btree_clear_internal(PyBTreeObject *self);
static PyObject *btree_repr(PyObject *self);
static Py_ssize_t btree_length(PyObject *self);
static int btree_contains(PyObject *self, PyObject *key);
static PyObject *btree_subscript(PyObject *self, PyObject *key);
static int btree_ass_subscript(PyObject *self, PyObject *key, PyObject *value);
static PyObject *btree_iter(PyObject *self);

/* ==================== B-Tree Core Operations ==================== */

/* Compare two Python objects. Returns:
 *  -1 if a < b
 *   0 if a == b
 *   1 if a > b
 *  -2 on error
 *
 * Optimized to minimize Python API calls by trying equality first
 * (common in updates) then doing a single < comparison.
 */
static int
compare_keys(PyObject *a, PyObject *b)
{
    /* Fast path: check pointer equality first */
    if (a == b) {
        return 0;
    }
    
    /* For integers, use rich comparison (avoid accessing internal ob_digit for Python 3.12+ compatibility) */
    if (PyLong_CheckExact(a) && PyLong_CheckExact(b)) {
        int result = PyObject_RichCompareBool(a, b, Py_LT);
        if (result < 0) {
            return 0;  /* Error in comparison, treat as equal */
        }
        if (result) {
            return -1;  /* a < b */
        }
        
        result = PyObject_RichCompareBool(a, b, Py_EQ);
        if (result < 0) {
            return 0;  /* Error in comparison, treat as equal */
        }
        if (result) {
            return 0;   /* a == b */
        }
        return 1;       /* a > b */
    }

    /* For floats, use direct double comparison when not NaN */
    if (PyFloat_CheckExact(a) && PyFloat_CheckExact(b)) {
        double a_val = PyFloat_AS_DOUBLE(a);
        double b_val = PyFloat_AS_DOUBLE(b);
        if (!Py_IS_NAN(a_val) && !Py_IS_NAN(b_val)) {
            if (a_val < b_val) return -1;
            if (a_val > b_val) return 1;
            return 0;
        }
        /* If NaN encountered, fall back to Python semantics below */
    }
    
    /* For strings, use optimized comparison */
    if (PyUnicode_CheckExact(a) && PyUnicode_CheckExact(b)) {
        int cmp = PyUnicode_Compare(a, b);
        if (cmp < 0) {
            if (PyErr_Occurred()) return -2;
            return -1;
        }
        if (cmp > 0) return 1;
        return 0;
    }
    
    /* General case: use rich comparison */
    int result = PyObject_RichCompareBool(a, b, Py_EQ);
    if (result < 0) {
        return -2;  /* Error */
    }
    if (result) {
        return 0;   /* a == b */
    }

    result = PyObject_RichCompareBool(a, b, Py_LT);
    if (result < 0) {
        return -2;  /* Error */
    }
    if (result) {
        return -1;  /* a < b */
    }

    return 1;       /* a > b */
}

/* Search for a key in a node using binary search, returning the index 
 * where the key is found or should be inserted. 
 * Sets *found to 1 if key is found, 0 otherwise.
 * Returns -1 on error.
 */
static Py_ssize_t
node_search_key(PyBTreeNode *node, PyObject *key, int *found)
{
    Py_ssize_t low = 0;
    Py_ssize_t high = node->n_keys - 1;
    *found = 0;

    while (low <= high) {
        Py_ssize_t mid = low + (high - low) / 2;
        int cmp = compare_keys(key, node->keys[mid]);
        
        if (cmp == -2) {
            return -1;  /* Error */
        }
        if (cmp == 0) {
            *found = 1;
            return mid;
        }
        if (cmp < 0) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return low;  /* Insert position */
}

/* Search for a key starting from a node. Returns the value if found,
 * NULL if not found (does not set exception).
 */
static PyObject *
node_search(PyBTreeNode *node, PyObject *key)
{
    int found;
    Py_ssize_t i;

    while (node != NULL) {
        i = node_search_key(node, key, &found);
        if (i < 0) {
            return NULL;  /* Error already set */
        }

        if (found) {
            Py_INCREF(node->values[i]);
            return node->values[i];
        }

        if (node->is_leaf) {
            return NULL;  /* Not found */
        }

        node = node->children[i];
    }

    return NULL;
}

/* Split a full child node. The parent must have room for one more key. */
static int
split_child(PyBTreeNode *parent, Py_ssize_t child_index)
{
    PyBTreeNode *full_child = parent->children[child_index];
    int order = full_child->order;
    Py_ssize_t t = order;

    /* Create a new node that will hold the right half */
    PyBTreeNode *new_node = (PyBTreeNode *)btreenode_new(order, full_child->is_leaf);
    if (new_node == NULL) {
        return -1;
    }

    /* Copy the right half of keys and values to new_node */
    new_node->n_keys = t - 1;
    memcpy(new_node->keys, &full_child->keys[t], (t - 1) * sizeof(PyObject *));
    memcpy(new_node->values, &full_child->values[t], (t - 1) * sizeof(PyObject *));
    
    /* Clear moved pointers in full_child to avoid double-free/decref issues */
    memset(&full_child->keys[t], 0, (t - 1) * sizeof(PyObject *));
    memset(&full_child->values[t], 0, (t - 1) * sizeof(PyObject *));

    /* Copy children if not a leaf */
    if (!full_child->is_leaf) {
        memcpy(new_node->children, &full_child->children[t], t * sizeof(PyBTreeNode *));
        memset(&full_child->children[t], 0, t * sizeof(PyBTreeNode *));
    }

    /* Move parent's keys and children to make room */
    if (parent->n_keys > child_index) {
        memmove(&parent->keys[child_index + 1], &parent->keys[child_index], (parent->n_keys - child_index) * sizeof(PyObject *));
        memmove(&parent->values[child_index + 1], &parent->values[child_index], (parent->n_keys - child_index) * sizeof(PyObject *));
    }
    
    if (parent->n_keys + 1 > child_index + 1) {
        memmove(&parent->children[child_index + 2], &parent->children[child_index + 1], (parent->n_keys - child_index) * sizeof(PyBTreeNode *));
    }

    /* Insert the middle key into parent */
    parent->keys[child_index] = full_child->keys[t - 1];
    parent->values[child_index] = full_child->values[t - 1];
    full_child->keys[t - 1] = NULL;
    full_child->values[t - 1] = NULL;

    parent->children[child_index + 1] = new_node;
    full_child->n_keys = t - 1;
    parent->n_keys++;

    return 0;
}

/* Insert a key-value pair into a non-full node - optimized with binary search */
static int
insert_non_full(PyBTreeNode *node, PyObject *key, PyObject *value)
{
    int order = node->order;
    int found;
    Py_ssize_t i;

    if (node->is_leaf) {
        /* Use binary search to find insert position */
        i = node_search_key(node, key, &found);
        if (i < 0) {
            return -1;  /* Error */
        }
        
        if (found) {
            /* Key exists, update value */
            Py_INCREF(value);
            Py_SETREF(node->values[i], value);
            return 1;  /* Updated existing key */
        }

        /* Key not found, need to insert at position i */
        /* Shift keys from the end to make room */
        if (node->n_keys > i) {
            memmove(&node->keys[i + 1], &node->keys[i], (node->n_keys - i) * sizeof(PyObject *));
            memmove(&node->values[i + 1], &node->values[i], (node->n_keys - i) * sizeof(PyObject *));
        }

        /* Insert new key-value */
        Py_INCREF(key);
        Py_INCREF(value);
        node->keys[i] = key;
        node->values[i] = value;
        node->n_keys++;
        return 0;  /* Inserted new key */
    }

    /* Use binary search to find child to descend into */
    i = node_search_key(node, key, &found);
    if (i < 0) {
        return -1;  /* Error */
    }
    
    if (found) {
        /* Key exists in internal node, update value */
        Py_INCREF(value);
        Py_SETREF(node->values[i], value);
        return 1;  /* Updated existing key */
    }

    /* Check if child is full */
    if (node->children[i]->n_keys == 2 * order - 1) {
        if (split_child(node, i) < 0) {
            return -1;
        }
        int cmp = compare_keys(key, node->keys[i]);
        if (cmp == -2) {
            return -1;
        }
        if (cmp == 0) {
            Py_INCREF(value);
            Py_SETREF(node->values[i], value);
            return 1;
        }
        if (cmp > 0) {
            i++;
        }
    }

    return insert_non_full(node->children[i], key, value);
}

/* ==================== B-Tree Delete Operations ==================== */

/* Get predecessor key-value (rightmost in left subtree) */
static int
get_predecessor(PyBTreeNode *node, Py_ssize_t idx, PyObject **pred_key, PyObject **pred_value)
{
    PyBTreeNode *current = node->children[idx];
    while (!current->is_leaf) {
        current = current->children[current->n_keys];
    }
    *pred_key = current->keys[current->n_keys - 1];
    *pred_value = current->values[current->n_keys - 1];
    return 0;
}

/* Get successor key-value (leftmost in right subtree) */
static int
get_successor(PyBTreeNode *node, Py_ssize_t idx, PyObject **succ_key, PyObject **succ_value)
{
    PyBTreeNode *current = node->children[idx + 1];
    while (!current->is_leaf) {
        current = current->children[0];
    }
    *succ_key = current->keys[0];
    *succ_value = current->values[0];
    return 0;
}

/* Merge children[idx] with children[idx+1] */
static void
merge_children(PyBTreeNode *node, Py_ssize_t idx)
{
    PyBTreeNode *child = node->children[idx];
    PyBTreeNode *sibling = node->children[idx + 1];
    Py_ssize_t t = node->order;

    /* Move key from parent to child */
    child->keys[t - 1] = node->keys[idx];
    child->values[t - 1] = node->values[idx];

    /* Copy keys from sibling */
    memcpy(&child->keys[t], sibling->keys, sibling->n_keys * sizeof(PyObject *));
    memcpy(&child->values[t], sibling->values, sibling->n_keys * sizeof(PyObject *));
    memset(sibling->keys, 0, sibling->n_keys * sizeof(PyObject *));
    memset(sibling->values, 0, sibling->n_keys * sizeof(PyObject *));

    /* Copy children if not leaf */
    if (!child->is_leaf) {
        memcpy(&child->children[t], sibling->children, (sibling->n_keys + 1) * sizeof(PyBTreeNode *));
        memset(sibling->children, 0, (sibling->n_keys + 1) * sizeof(PyBTreeNode *));
    }

    /* Shift parent's keys */
    if (node->n_keys - 1 > idx) {
        memmove(&node->keys[idx], &node->keys[idx + 1], (node->n_keys - 1 - idx) * sizeof(PyObject *));
        memmove(&node->values[idx], &node->values[idx + 1], (node->n_keys - 1 - idx) * sizeof(PyObject *));
    }
    node->keys[node->n_keys - 1] = NULL;
    node->values[node->n_keys - 1] = NULL;

    /* Shift parent's children */
    if (node->n_keys > idx + 1) {
        memmove(&node->children[idx + 1], &node->children[idx + 2], (node->n_keys - (idx + 1)) * sizeof(PyBTreeNode *));
    }
    node->children[node->n_keys] = NULL;

    child->n_keys += sibling->n_keys + 1;
    node->n_keys--;

    sibling->n_keys = 0;
    Py_DECREF(sibling);
}

/* Borrow a key from children[idx-1] */
static void
borrow_from_prev(PyBTreeNode *node, Py_ssize_t idx)
{
    PyBTreeNode *child = node->children[idx];
    PyBTreeNode *sibling = node->children[idx - 1];

    /* Shift child's keys right */
    memmove(&child->keys[1], &child->keys[0], child->n_keys * sizeof(PyObject *));
    memmove(&child->values[1], &child->values[0], child->n_keys * sizeof(PyObject *));

    if (!child->is_leaf) {
        memmove(&child->children[1], &child->children[0], (child->n_keys + 1) * sizeof(PyBTreeNode *));
    }

    /* Move key from parent to child */
    child->keys[0] = node->keys[idx - 1];
    child->values[0] = node->values[idx - 1];

    if (!child->is_leaf) {
        child->children[0] = sibling->children[sibling->n_keys];
        sibling->children[sibling->n_keys] = NULL;
    }

    /* Move key from sibling to parent */
    node->keys[idx - 1] = sibling->keys[sibling->n_keys - 1];
    node->values[idx - 1] = sibling->values[sibling->n_keys - 1];
    sibling->keys[sibling->n_keys - 1] = NULL;
    sibling->values[sibling->n_keys - 1] = NULL;

    child->n_keys++;
    sibling->n_keys--;
}

/* Borrow a key from children[idx+1] */
static void
borrow_from_next(PyBTreeNode *node, Py_ssize_t idx)
{
    PyBTreeNode *child = node->children[idx];
    PyBTreeNode *sibling = node->children[idx + 1];

    /* Move key from parent to child */
    child->keys[child->n_keys] = node->keys[idx];
    child->values[child->n_keys] = node->values[idx];

    if (!child->is_leaf) {
        child->children[child->n_keys + 1] = sibling->children[0];
    }

    /* Move key from sibling to parent */
    node->keys[idx] = sibling->keys[0];
    node->values[idx] = sibling->values[0];

    /* Shift sibling's keys left */
    if (sibling->n_keys > 1) {
        memmove(&sibling->keys[0], &sibling->keys[1], (sibling->n_keys - 1) * sizeof(PyObject *));
        memmove(&sibling->values[0], &sibling->values[1], (sibling->n_keys - 1) * sizeof(PyObject *));
    }
    sibling->keys[sibling->n_keys - 1] = NULL;
    sibling->values[sibling->n_keys - 1] = NULL;

    if (!sibling->is_leaf) {
        memmove(&sibling->children[0], &sibling->children[1], sibling->n_keys * sizeof(PyBTreeNode *));
        sibling->children[sibling->n_keys] = NULL;
    }

    child->n_keys++;
    sibling->n_keys--;
}

/* Ensure children[idx] has at least t keys */
static void
fill_child(PyBTreeNode *node, Py_ssize_t idx)
{
    int order = node->order;
    Py_ssize_t t = order;

    if (idx > 0 && node->children[idx - 1]->n_keys >= t) {
        borrow_from_prev(node, idx);
    }
    else if (idx < node->n_keys && node->children[idx + 1]->n_keys >= t) {
        borrow_from_next(node, idx);
    }
    else {
        if (idx < node->n_keys) {
            merge_children(node, idx);
        }
        else {
            merge_children(node, idx - 1);
        }
    }
}

/* Forward declaration */
static int delete_from_node(PyBTreeNode *node, PyObject *key);

/* Delete from a leaf node */
static int
delete_from_leaf(PyBTreeNode *node, Py_ssize_t idx)
{
    Py_DECREF(node->keys[idx]);
    Py_DECREF(node->values[idx]);

    if (node->n_keys - 1 > idx) {
        memmove(&node->keys[idx], &node->keys[idx + 1], (node->n_keys - 1 - idx) * sizeof(PyObject *));
        memmove(&node->values[idx], &node->values[idx + 1], (node->n_keys - 1 - idx) * sizeof(PyObject *));
    }
    node->keys[node->n_keys - 1] = NULL;
    node->values[node->n_keys - 1] = NULL;
    node->n_keys--;

    return 0;
}

/* Delete from an internal node */
static int
delete_from_internal(PyBTreeNode *node, Py_ssize_t idx)
{
    PyObject *key = node->keys[idx];
    Py_ssize_t t = node->order;

    if (node->children[idx]->n_keys >= t) {
        /* Get predecessor and replace */
        PyObject *pred_key, *pred_value;
        get_predecessor(node, idx, &pred_key, &pred_value);
        Py_INCREF(pred_key);
        Py_INCREF(pred_value);
        Py_DECREF(node->keys[idx]);
        Py_DECREF(node->values[idx]);
        node->keys[idx] = pred_key;
        node->values[idx] = pred_value;
        return delete_from_node(node->children[idx], pred_key);
    }
    else if (node->children[idx + 1]->n_keys >= t) {
        /* Get successor and replace */
        PyObject *succ_key, *succ_value;
        get_successor(node, idx, &succ_key, &succ_value);
        Py_INCREF(succ_key);
        Py_INCREF(succ_value);
        Py_DECREF(node->keys[idx]);
        Py_DECREF(node->values[idx]);
        node->keys[idx] = succ_key;
        node->values[idx] = succ_value;
        return delete_from_node(node->children[idx + 1], succ_key);
    }
    else {
        /* Merge children and delete from merged node */
        merge_children(node, idx);
        return delete_from_node(node->children[idx], key);
    }
}

/* Delete a key from a node */
static int
delete_from_node(PyBTreeNode *node, PyObject *key)
{
    int found;
    Py_ssize_t idx = node_search_key(node, key, &found);
    if (idx < 0) {
        return -1;
    }

    if (found) {
        if (node->is_leaf) {
            return delete_from_leaf(node, idx);
        }
        else {
            return delete_from_internal(node, idx);
        }
    }
    else {
        if (node->is_leaf) {
            PyErr_SetObject(PyExc_KeyError, key);
            return -1;
        }

        int last_child = (idx == node->n_keys);
        Py_ssize_t t = node->order;

        if (node->children[idx]->n_keys < t) {
            fill_child(node, idx);
        }

        if (last_child && idx > node->n_keys) {
            return delete_from_node(node->children[idx - 1], key);
        }
        else {
            return delete_from_node(node->children[idx], key);
        }
    }
}

/* ==================== B-Tree Public API ==================== */

PyObject *
PyBTree_New(int order)
{
    PyBTreeObject *btree;

    if (order < BTREE_MIN_ORDER) {
        order = BTREE_DEFAULT_ORDER;
    }

    btree = PyObject_GC_New(PyBTreeObject, &PyBTree_Type);
    if (btree == NULL) {
        return NULL;
    }

    btree->order = order;
    btree->size = 0;
    btree->root = (PyBTreeNode *)btreenode_new(order, 1);  /* Start with leaf root */
    if (btree->root == NULL) {
        Py_DECREF(btree);
        return NULL;
    }

    PyObject_GC_Track((PyObject *)btree);
    return (PyObject *)btree;
}

Py_ssize_t
PyBTree_Size(PyObject *btree)
{
    if (!PyBTree_Check(btree)) {
        PyErr_BadInternalCall();
        return -1;
    }
    return ((PyBTreeObject *)btree)->size;
}

int
PyBTree_Insert(PyObject *self, PyObject *key, PyObject *value)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    int order = btree->order;
    int result;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return -1;
    }

    /* If root is full, create a new root */
    if (btree->root->n_keys == 2 * order - 1) {
        PyBTreeNode *new_root = (PyBTreeNode *)btreenode_new(order, 0);
        if (new_root == NULL) {
            return -1;
        }
        new_root->children[0] = btree->root;
        btree->root = new_root;

        if (split_child(new_root, 0) < 0) {
            return -1;
        }
    }

    result = insert_non_full(btree->root, key, value);
    if (result < 0) {
        return -1;
    }
    if (result == 0) {
        btree->size++;  /* New key inserted */
    }
    return 0;
}

PyObject *
PyBTree_Search(PyObject *self, PyObject *key)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    if (btree->root == NULL) {
        return NULL;
    }

    return node_search(btree->root, key);
}

int
PyBTree_Delete(PyObject *self, PyObject *key)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    int result;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return -1;
    }

    if (btree->root == NULL || btree->size == 0) {
        PyErr_SetObject(PyExc_KeyError, key);
        return -1;
    }

    result = delete_from_node(btree->root, key);
    if (result < 0) {
        return -1;
    }

    btree->size--;

    /* If root has no keys but has a child, make the child the new root */
    if (btree->root->n_keys == 0 && !btree->root->is_leaf) {
        PyBTreeNode *old_root = btree->root;
        btree->root = old_root->children[0];
        old_root->children[0] = NULL;
        Py_DECREF(old_root);
    }

    return 0;
}

/* Optimized contains check - avoids INCREF/DECREF overhead */
static int
node_contains(PyBTreeNode *node, PyObject *key)
{
    int found;

    while (node != NULL) {
        Py_ssize_t i = node_search_key(node, key, &found);
        if (i < 0) {
            return -1;  /* Error */
        }

        if (found) {
            return 1;  /* Found */
        }

        if (node->is_leaf) {
            return 0;  /* Not found */
        }

        node = node->children[i];
    }

    return 0;
}

int
PyBTree_Contains(PyObject *self, PyObject *key)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return -1;
    }

    if (btree->root == NULL) {
        return 0;
    }

    return node_contains(btree->root, key);
}

/* Optimized helper to collect keys with pre-allocated index */
static int
collect_keys_fast(PyBTreeNode *node, PyObject **items, Py_ssize_t *idx)
{
    Py_ssize_t i;

    if (node == NULL) {
        return 0;
    }

    for (i = 0; i < node->n_keys; i++) {
        if (!node->is_leaf && node->children[i]) {
            if (collect_keys_fast(node->children[i], items, idx) < 0) {
                return -1;
            }
        }
        Py_INCREF(node->keys[i]);
        items[*idx] = node->keys[i];
        (*idx)++;
    }

    if (!node->is_leaf && node->children[node->n_keys]) {
        if (collect_keys_fast(node->children[node->n_keys], items, idx) < 0) {
            return -1;
        }
    }

    return 0;
}

PyObject *
PyBTree_Keys(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    /* Pre-allocate list with exact size */
    PyObject *list = PyList_New(btree->size);
    if (list == NULL) {
        return NULL;
    }

    if (btree->size > 0) {
        Py_ssize_t idx = 0;
        if (collect_keys_fast(btree->root, &PyList_GET_ITEM(list, 0), &idx) < 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    return list;
}

/* Optimized helper to collect values with pre-allocated index */
static int
collect_values_fast(PyBTreeNode *node, PyObject **items, Py_ssize_t *idx)
{
    Py_ssize_t i;

    if (node == NULL) {
        return 0;
    }

    for (i = 0; i < node->n_keys; i++) {
        if (!node->is_leaf && node->children[i]) {
            if (collect_values_fast(node->children[i], items, idx) < 0) {
                return -1;
            }
        }
        Py_INCREF(node->values[i]);
        items[*idx] = node->values[i];
        (*idx)++;
    }

    if (!node->is_leaf && node->children[node->n_keys]) {
        if (collect_values_fast(node->children[node->n_keys], items, idx) < 0) {
            return -1;
        }
    }

    return 0;
}

PyObject *
PyBTree_Values(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    /* Pre-allocate list with exact size */
    PyObject *list = PyList_New(btree->size);
    if (list == NULL) {
        return NULL;
    }

    if (btree->size > 0) {
        Py_ssize_t idx = 0;
        if (collect_values_fast(btree->root, &PyList_GET_ITEM(list, 0), &idx) < 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    return list;
}

/* Optimized helper to collect items with pre-allocated index */
static int
collect_items_fast(PyBTreeNode *node, PyObject **items, Py_ssize_t *idx)
{
    Py_ssize_t i;

    if (node == NULL) {
        return 0;
    }

    for (i = 0; i < node->n_keys; i++) {
        if (!node->is_leaf && node->children[i]) {
            if (collect_items_fast(node->children[i], items, idx) < 0) {
                return -1;
            }
        }
        PyObject *tuple = PyTuple_Pack(2, node->keys[i], node->values[i]);
        if (tuple == NULL) {
            return -1;
        }
        items[*idx] = tuple;
        (*idx)++;
    }

    if (!node->is_leaf && node->children[node->n_keys]) {
        if (collect_items_fast(node->children[node->n_keys], items, idx) < 0) {
            return -1;
        }
    }

    return 0;
}

PyObject *
PyBTree_Items(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    /* Pre-allocate list with exact size */
    PyObject *list = PyList_New(btree->size);
    if (list == NULL) {
        return NULL;
    }

    if (btree->size > 0) {
        Py_ssize_t idx = 0;
        if (collect_items_fast(btree->root, &PyList_GET_ITEM(list, 0), &idx) < 0) {
            Py_DECREF(list);
            return NULL;
        }
    }

    return list;
}

static PyObject *
get_min_from_node(PyBTreeNode *node)
{
    if (node == NULL || node->n_keys == 0) {
        return NULL;
    }
    while (!node->is_leaf) {
        node = node->children[0];
    }
    Py_INCREF(node->keys[0]);
    return node->keys[0];
}

static PyObject *
get_max_from_node(PyBTreeNode *node)
{
    if (node == NULL || node->n_keys == 0) {
        return NULL;
    }
    while (!node->is_leaf) {
        node = node->children[node->n_keys];
    }
    Py_INCREF(node->keys[node->n_keys - 1]);
    return node->keys[node->n_keys - 1];
}

PyObject *
PyBTree_GetMin(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    return get_min_from_node(btree->root);
}

PyObject *
PyBTree_GetMax(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    return get_max_from_node(btree->root);
}

int
PyBTree_Clear(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    if (!PyBTree_Check(self)) {
        PyErr_BadInternalCall();
        return -1;
    }

    return btree_clear_internal(btree);
}

/* ==================== Type Methods ==================== */

static void
btree_dealloc(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;

    PyObject_GC_UnTrack(self);

    Py_XDECREF(btree->root);

    Py_TYPE(self)->tp_free(self);
}

static int
btree_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    Py_VISIT(btree->root);
    return 0;
}

static int
btree_clear_internal(PyBTreeObject *btree)
{
    int order = btree->order;
    Py_CLEAR(btree->root);
    btree->size = 0;

    /* Create a new empty root */
    btree->root = (PyBTreeNode *)btreenode_new(order, 1);
    if (btree->root == NULL) {
        return -1;
    }

    return 0;
}

static int
btree_clear_slot(PyObject *self)
{
    return btree_clear_internal((PyBTreeObject *)self);
}

static PyObject *
btree_repr(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    return PyUnicode_FromFormat("BTreeDict(order=%d, size=%zd)",
                                btree->order, btree->size);
}

static Py_ssize_t
btree_length(PyObject *self)
{
    return ((PyBTreeObject *)self)->size;
}

static int
btree_contains(PyObject *self, PyObject *key)
{
    return PyBTree_Contains(self, key);
}

static PyObject *
btree_subscript(PyObject *self, PyObject *key)
{
    PyObject *value = PyBTree_Search(self, key);
    if (value == NULL) {
        if (!PyErr_Occurred()) {
            PyErr_SetObject(PyExc_KeyError, key);
        }
        return NULL;
    }
    return value;
}

static int
btree_ass_subscript(PyObject *self, PyObject *key, PyObject *value)
{
    if (value == NULL) {
        return PyBTree_Delete(self, key);
    }
    else {
        return PyBTree_Insert(self, key, value);
    }
}

/* ==================== BTreeDict Iterator ==================== */

/* Stack-based iterator for efficient in-order traversal without copying */
#define ITER_STACK_SIZE 64  /* Max tree depth - sufficient for huge trees */

typedef struct {
    PyBTreeNode *node;
    Py_ssize_t key_idx;  /* Next key index to return */
} IterStackFrame;

typedef struct {
    PyObject_HEAD
    PyBTreeObject *btree;           /* The B-tree being iterated */
    Py_ssize_t remaining;           /* Items remaining for length hint */
    Py_ssize_t stack_top;           /* Top of stack (-1 = empty) */
    IterStackFrame stack[ITER_STACK_SIZE];  /* Stack for tree traversal */
} PyBTreeIterObject;

static PyTypeObject PyBTreeIter_Type;

/* Push a node onto the stack and descend to leftmost leaf */
static void
iter_descend_left(PyBTreeIterObject *it, PyBTreeNode *node)
{
    while (node != NULL) {
        it->stack_top++;
        it->stack[it->stack_top].node = node;
        it->stack[it->stack_top].key_idx = 0;
        
        if (node->is_leaf) {
            break;
        }
        node = node->children[0];
    }
}

static void
btreeiter_dealloc(PyObject *self)
{
    PyBTreeIterObject *it = (PyBTreeIterObject *)self;
    PyObject_GC_UnTrack(self);
    Py_XDECREF(it->btree);
    PyObject_GC_Del(self);
}

static int
btreeiter_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyBTreeIterObject *it = (PyBTreeIterObject *)self;
    Py_VISIT(it->btree);
    return 0;
}

static PyObject *
btreeiter_next(PyObject *self)
{
    PyBTreeIterObject *it = (PyBTreeIterObject *)self;
    
    while (it->stack_top >= 0) {
        IterStackFrame *frame = &it->stack[it->stack_top];
        PyBTreeNode *node = frame->node;
        
        if (frame->key_idx < node->n_keys) {
            /* Return current key and advance */
            PyObject *key = node->keys[frame->key_idx];
            frame->key_idx++;
            it->remaining--;
            
            /* If not a leaf, descend into right child of this key */
            if (!node->is_leaf) {
                iter_descend_left(it, node->children[frame->key_idx]);
            }
            
            Py_INCREF(key);
            return key;
        } else {
            /* Done with this node, pop stack */
            it->stack_top--;
        }
    }
    
    return NULL;  /* Iteration complete */
}

static PyObject *
btreeiter_len(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyBTreeIterObject *it = (PyBTreeIterObject *)self;
    return PyLong_FromSsize_t(it->remaining > 0 ? it->remaining : 0);
}

static PyMethodDef btreeiter_methods[] = {
    {"__length_hint__", btreeiter_len, METH_NOARGS, "Private method returning estimate of len(list(it))."},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PyBTreeIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "btree_iterator",                           /* tp_name */
    sizeof(PyBTreeIterObject),                  /* tp_basicsize */
    0,                                          /* tp_itemsize */
    btreeiter_dealloc,                          /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    btreeiter_traverse,                         /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    btreeiter_next,                             /* tp_iternext */
    btreeiter_methods,                          /* tp_methods */
    0,                                          /* tp_members */
};

static PyObject *
btree_iter(PyObject *self)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    PyBTreeIterObject *it;

    it = PyObject_GC_New(PyBTreeIterObject, &PyBTreeIter_Type);
    if (it == NULL) {
        return NULL;
    }

    Py_INCREF(btree);
    it->btree = btree;
    it->remaining = btree->size;
    it->stack_top = -1;  /* Empty stack */

    /* Initialize by descending to leftmost leaf */
    if (btree->root != NULL && btree->root->n_keys > 0) {
        iter_descend_left(it, btree->root);
    }

    PyObject_GC_Track((PyObject *)it);
    return (PyObject *)it;
}

/* ==================== Reversed Iterator ==================== */

typedef struct {
    PyObject_HEAD
    PyBTreeObject *btree;           /* The B-tree being iterated */
    Py_ssize_t remaining;           /* Items remaining for length hint */
    Py_ssize_t stack_top;           /* Top of stack (-1 = empty) */
    IterStackFrame stack[ITER_STACK_SIZE];  /* Stack for tree traversal */
} PyBTreeReverseIterObject;

static PyTypeObject PyBTreeReverseIter_Type;

/* Push a node onto the stack and descend to rightmost leaf */
static void
iter_descend_right(PyBTreeReverseIterObject *it, PyBTreeNode *node)
{
    while (node != NULL) {
        it->stack_top++;
        it->stack[it->stack_top].node = node;
        it->stack[it->stack_top].key_idx = node->n_keys - 1;
        
        if (node->is_leaf) {
            break;
        }
        node = node->children[node->n_keys];
    }
}

static void
btreereviter_dealloc(PyObject *self)
{
    PyBTreeReverseIterObject *it = (PyBTreeReverseIterObject *)self;
    PyObject_GC_UnTrack(self);
    Py_XDECREF(it->btree);
    PyObject_GC_Del(self);
}

static int
btreereviter_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyBTreeReverseIterObject *it = (PyBTreeReverseIterObject *)self;
    Py_VISIT(it->btree);
    return 0;
}

static PyObject *
btreereviter_next(PyObject *self)
{
    PyBTreeReverseIterObject *it = (PyBTreeReverseIterObject *)self;
    
    while (it->stack_top >= 0) {
        IterStackFrame *frame = &it->stack[it->stack_top];
        PyBTreeNode *node = frame->node;
        
        if (frame->key_idx >= 0) {
            /* Return current key and move backwards */
            PyObject *key = node->keys[frame->key_idx];
            Py_ssize_t child_idx = frame->key_idx;
            frame->key_idx--;
            it->remaining--;
            
            /* If not a leaf, descend into left child of this key */
            if (!node->is_leaf) {
                iter_descend_right(it, node->children[child_idx]);
            }
            
            Py_INCREF(key);
            return key;
        } else {
            /* Done with this node, pop stack */
            it->stack_top--;
        }
    }
    
    return NULL;  /* Iteration complete */
}

static PyObject *
btreereviter_len(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyBTreeReverseIterObject *it = (PyBTreeReverseIterObject *)self;
    return PyLong_FromSsize_t(it->remaining > 0 ? it->remaining : 0);
}

static PyMethodDef btreereviter_methods[] = {
    {"__length_hint__", btreereviter_len, METH_NOARGS, "Private method returning estimate of len(list(it))."},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PyBTreeReverseIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "btree_reverseiterator",                    /* tp_name */
    sizeof(PyBTreeReverseIterObject),           /* tp_basicsize */
    0,                                          /* tp_itemsize */
    btreereviter_dealloc,                       /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    btreereviter_traverse,                      /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    btreereviter_next,                          /* tp_iternext */
    btreereviter_methods,                       /* tp_methods */
    0,                                          /* tp_members */
};

static PyObject *
btree_reversed(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    PyBTreeReverseIterObject *it;

    it = PyObject_GC_New(PyBTreeReverseIterObject, &PyBTreeReverseIter_Type);
    if (it == NULL) {
        return NULL;
    }

    Py_INCREF(btree);
    it->btree = btree;
    it->remaining = btree->size;
    it->stack_top = -1;  /* Empty stack */

    /* Initialize by descending to rightmost leaf */
    if (btree->root != NULL && btree->root->n_keys > 0) {
        iter_descend_right(it, btree->root);
    }

    PyObject_GC_Track((PyObject *)it);
    return (PyObject *)it;
}

/* ==================== Range Iterator (irange) ==================== */

typedef struct {
    PyObject_HEAD
    PyBTreeObject *btree;           /* The B-tree being iterated */
    PyObject *min_key;              /* Minimum key (inclusive), NULL for no min */
    PyObject *max_key;              /* Maximum key (exclusive), NULL for no max */
    int inclusive_min;              /* Include min_key */
    int inclusive_max;              /* Include max_key */
    Py_ssize_t stack_top;           /* Top of stack (-1 = empty) */
    IterStackFrame stack[ITER_STACK_SIZE];  /* Stack for tree traversal */
    int started;                    /* Whether iteration has started */
} PyBTreeRangeIterObject;

static PyTypeObject PyBTreeRangeIter_Type;

static void
btreerangeiter_dealloc(PyObject *self)
{
    PyBTreeRangeIterObject *it = (PyBTreeRangeIterObject *)self;
    PyObject_GC_UnTrack(self);
    Py_XDECREF(it->btree);
    Py_XDECREF(it->min_key);
    Py_XDECREF(it->max_key);
    PyObject_GC_Del(self);
}

static int
btreerangeiter_traverse(PyObject *self, visitproc visit, void *arg)
{
    PyBTreeRangeIterObject *it = (PyBTreeRangeIterObject *)self;
    Py_VISIT(it->btree);
    Py_VISIT(it->min_key);
    Py_VISIT(it->max_key);
    return 0;
}

/* Descend to first key >= min_key (or leftmost if no min) */
static void
range_iter_descend_to_start(PyBTreeRangeIterObject *it, PyBTreeNode *node)
{
    while (node != NULL) {
        it->stack_top++;
        it->stack[it->stack_top].node = node;
        
        if (it->min_key == NULL) {
            /* No minimum, start from leftmost */
            it->stack[it->stack_top].key_idx = 0;
            if (node->is_leaf) {
                break;
            }
            node = node->children[0];
        } else {
            /* Find position where keys >= min_key */
            int found;
            Py_ssize_t idx = node_search_key(node, it->min_key, &found);
            if (idx < 0) {
                return;  /* Error */
            }
            
            if (found && !it->inclusive_min) {
                /* Found exact match but not inclusive, move to next */
                idx++;
            }
            
            it->stack[it->stack_top].key_idx = idx;
            
            if (node->is_leaf) {
                break;
            }
            
            /* Descend to appropriate child */
            if (found && !it->inclusive_min) {
                if (idx <= node->n_keys) {
                    node = node->children[idx];
                } else {
                    break;
                }
            } else {
                node = node->children[idx];
            }
        }
    }
}

static PyObject *
btreerangeiter_next(PyObject *self)
{
    PyBTreeRangeIterObject *it = (PyBTreeRangeIterObject *)self;
    
    /* Initialize on first call */
    if (!it->started) {
        it->started = 1;
        if (it->btree->root != NULL && it->btree->root->n_keys > 0) {
            range_iter_descend_to_start(it, it->btree->root);
        }
    }
    
    while (it->stack_top >= 0) {
        IterStackFrame *frame = &it->stack[it->stack_top];
        PyBTreeNode *node = frame->node;
        
        if (frame->key_idx < node->n_keys) {
            PyObject *key = node->keys[frame->key_idx];
            
            /* Check if we've exceeded max_key */
            if (it->max_key != NULL) {
                int cmp = compare_keys(key, it->max_key);
                if (cmp == -2) return NULL;  /* Error */
                if (it->inclusive_max) {
                    if (cmp > 0) return NULL;  /* Past max, done */
                } else {
                    if (cmp >= 0) return NULL;  /* At or past max, done */
                }
            }
            
            frame->key_idx++;
            
            /* If not a leaf, descend into right child of this key */
            if (!node->is_leaf) {
                PyBTreeNode *child = node->children[frame->key_idx];
                while (child != NULL) {
                    it->stack_top++;
                    it->stack[it->stack_top].node = child;
                    it->stack[it->stack_top].key_idx = 0;
                    if (child->is_leaf) {
                        break;
                    }
                    child = child->children[0];
                }
            }
            
            Py_INCREF(key);
            return key;
        } else {
            /* Done with this node, pop stack */
            it->stack_top--;
        }
    }
    
    return NULL;  /* Iteration complete */
}

static PyTypeObject PyBTreeRangeIter_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "btree_rangeiterator",                      /* tp_name */
    sizeof(PyBTreeRangeIterObject),             /* tp_basicsize */
    0,                                          /* tp_itemsize */
    btreerangeiter_dealloc,                     /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    0,                                          /* tp_doc */
    btreerangeiter_traverse,                    /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    PyObject_SelfIter,                          /* tp_iter */
    btreerangeiter_next,                        /* tp_iternext */
    0,                                          /* tp_methods */
    0,                                          /* tp_members */
};

PyDoc_STRVAR(btree_irange_doc,
"irange(min=None, max=None, inclusive=(True, False), /)\n"
"--\n\n"
"Return an iterator over keys in the range [min, max).\n\n"
"By default, the range is inclusive of min and exclusive of max.\n"
"Use inclusive=(True, True) for a fully closed range.\n\n"
"Args:\n"
"    min: Minimum key (inclusive by default). None for no minimum.\n"
"    max: Maximum key (exclusive by default). None for no maximum.\n"
"    inclusive: Tuple of (min_inclusive, max_inclusive) booleans.\n\n"
"Example:\n"
"    >>> bt = BTreeDict()\n"
"    >>> for i in range(10): bt[i] = i\n"
"    >>> list(bt.irange(3, 7))\n"
"    [3, 4, 5, 6]\n"
"    >>> list(bt.irange(3, 7, inclusive=(True, True)))\n"
"    [3, 4, 5, 6, 7]\n");

static PyObject *
btree_irange(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    PyBTreeRangeIterObject *it;
    PyObject *min_key = Py_None;
    PyObject *max_key = Py_None;
    PyObject *inclusive = NULL;
    int inclusive_min = 1;  /* Default: inclusive of min */
    int inclusive_max = 0;  /* Default: exclusive of max */
    
    static char *kwlist[] = {"min", "max", "inclusive", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OOO", kwlist,
                                     &min_key, &max_key, &inclusive)) {
        return NULL;
    }
    
    /* Parse inclusive parameter */
    if (inclusive != NULL && inclusive != Py_None) {
        if (!PyTuple_Check(inclusive) || PyTuple_GET_SIZE(inclusive) != 2) {
            PyErr_SetString(PyExc_TypeError,
                "inclusive must be a tuple of two booleans");
            return NULL;
        }
        inclusive_min = PyObject_IsTrue(PyTuple_GET_ITEM(inclusive, 0));
        inclusive_max = PyObject_IsTrue(PyTuple_GET_ITEM(inclusive, 1));
        if (inclusive_min < 0 || inclusive_max < 0) {
            return NULL;
        }
    }
    
    it = PyObject_GC_New(PyBTreeRangeIterObject, &PyBTreeRangeIter_Type);
    if (it == NULL) {
        return NULL;
    }
    
    Py_INCREF(btree);
    it->btree = btree;
    it->min_key = (min_key == Py_None) ? NULL : min_key;
    it->max_key = (max_key == Py_None) ? NULL : max_key;
    Py_XINCREF(it->min_key);
    Py_XINCREF(it->max_key);
    it->inclusive_min = inclusive_min;
    it->inclusive_max = inclusive_max;
    it->stack_top = -1;
    it->started = 0;
    
    PyObject_GC_Track((PyObject *)it);
    return (PyObject *)it;
}

/* ==================== Python Methods ==================== */

PyDoc_STRVAR(btree_insert_doc,
"insert(key, value, /)\n"
"--\n\n"
"Insert a key-value pair into the B-tree.");

static PyObject *
btree_insert(PyObject *self, PyObject *args)
{
    PyObject *key, *value;
    if (!PyArg_ParseTuple(args, "OO", &key, &value)) {
        return NULL;
    }
    if (PyBTree_Insert(self, key, value) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(btree_get_doc,
"get(key, default=None, /)\n"
"--\n\n"
"Return the value for key if key is in the B-tree, else default.");

static PyObject *
btree_get(PyObject *self, PyObject *args)
{
    PyObject *key, *default_value = Py_None;

    if (!PyArg_ParseTuple(args, "O|O", &key, &default_value)) {
        return NULL;
    }

    PyObject *value = PyBTree_Search(self, key);
    if (value == NULL) {
        if (PyErr_Occurred()) {
            return NULL;
        }
        Py_INCREF(default_value);
        return default_value;
    }
    return value;
}

PyDoc_STRVAR(btree_pop_doc,
"pop(key, default=<marker>, /)\n"
"--\n\n"
"Remove specified key and return the corresponding value.\n"
"If key is not found, default is returned if given, otherwise KeyError is raised.");

static PyObject *
btree_pop(PyObject *self, PyObject *args)
{
    PyObject *key, *default_value = NULL;

    if (!PyArg_ParseTuple(args, "O|O", &key, &default_value)) {
        return NULL;
    }

    PyObject *value = PyBTree_Search(self, key);
    if (value == NULL) {
        if (PyErr_Occurred()) {
            return NULL;
        }
        if (default_value != NULL) {
            Py_INCREF(default_value);
            return default_value;
        }
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }

    if (PyBTree_Delete(self, key) < 0) {
        Py_DECREF(value);
        return NULL;
    }

    return value;
}

PyDoc_STRVAR(btree_keys_doc,
"keys()\n"
"--\n\n"
"Return a list of all keys in the B-tree (in sorted order).");

static PyObject *
btree_keys_method(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyBTree_Keys(self);
}

PyDoc_STRVAR(btree_values_doc,
"values()\n"
"--\n\n"
"Return a list of all values in the B-tree (in key-sorted order).");

static PyObject *
btree_values_method(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyBTree_Values(self);
}

PyDoc_STRVAR(btree_items_doc,
"items()\n"
"--\n\n"
"Return a list of (key, value) tuples in the B-tree (in sorted order).");

static PyObject *
btree_items_method(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    return PyBTree_Items(self);
}

PyDoc_STRVAR(btree_clear_doc,
"clear()\n"
"--\n\n"
"Remove all items from the B-tree.");

static PyObject *
btree_clear_method(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    if (PyBTree_Clear(self) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(btree_min_doc,
"min()\n"
"--\n\n"
"Return the minimum key in the B-tree.");

static PyObject *
btree_min(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *result = PyBTree_GetMin(self);
    if (result == NULL && !PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "min() arg is an empty B-tree");
    }
    return result;
}

PyDoc_STRVAR(btree_max_doc,
"max()\n"
"--\n\n"
"Return the maximum key in the B-tree.");

static PyObject *
btree_max(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyObject *result = PyBTree_GetMax(self);
    if (result == NULL && !PyErr_Occurred()) {
        PyErr_SetString(PyExc_ValueError, "max() arg is an empty B-tree");
    }
    return result;
}

/* ==================== setdefault Method ==================== */

PyDoc_STRVAR(btree_setdefault_doc,
"setdefault(key, default=None, /)\n"
"--\n\n"
"Insert key with a value of default if key is not in the B-tree.\n\n"
"Return the value for key if key is in the B-tree, else default.");

static PyObject *
btree_setdefault(PyObject *self, PyObject *args)
{
    PyObject *key, *default_value = Py_None;

    if (!PyArg_ParseTuple(args, "O|O", &key, &default_value)) {
        return NULL;
    }

    PyObject *value = PyBTree_Search(self, key);
    if (value != NULL) {
        return value;  /* Key exists, return existing value */
    }
    if (PyErr_Occurred()) {
        return NULL;
    }

    /* Key doesn't exist, insert default and return it */
    if (PyBTree_Insert(self, key, default_value) < 0) {
        return NULL;
    }
    Py_INCREF(default_value);
    return default_value;
}

/* ==================== update Method ==================== */

PyDoc_STRVAR(btree_update_doc,
"update([other], **kwargs)\n"
"--\n\n"
"Update the B-tree with key/value pairs from other and kwargs.\n\n"
"If other is present, it must be a mapping or an iterable of key/value pairs.\n"
"Keyword arguments are also added as key/value pairs.");

static int
btree_merge_from_seq2(PyObject *self, PyObject *seq2)
{
    PyObject *it;       /* iter(seq2) */
    Py_ssize_t i = 0;   /* index into seq2 */
    PyObject *item;     /* seq2[i] */
    PyObject *fast;     /* item as a 2-tuple or 2-list */

    it = PyObject_GetIter(seq2);
    if (it == NULL)
        return -1;

    while ((item = PyIter_Next(it)) != NULL) {
        PyObject *key, *value;

        /* Convert item to sequence, and verify length 2. */
        fast = PySequence_Fast(item, "");
        if (fast == NULL) {
            if (PyErr_ExceptionMatches(PyExc_TypeError)) {
                PyErr_Format(PyExc_TypeError,
                    "cannot convert B-tree update "
                    "sequence element #%zd to a sequence",
                    i);
            }
            goto Fail;
        }
        if (PySequence_Fast_GET_SIZE(fast) != 2) {
            PyErr_Format(PyExc_ValueError,
                "B-tree update sequence element #%zd "
                "has length %zd; 2 is required",
                i, PySequence_Fast_GET_SIZE(fast));
            goto Fail;
        }

        key = PySequence_Fast_GET_ITEM(fast, 0);
        value = PySequence_Fast_GET_ITEM(fast, 1);
        if (PyBTree_Insert(self, key, value) < 0) {
            goto Fail;
        }
        Py_DECREF(fast);
        Py_DECREF(item);
        i++;
    }
    Py_DECREF(it);
    if (PyErr_Occurred())
        return -1;
    return 0;

Fail:
    Py_XDECREF(fast);
    Py_DECREF(item);
    Py_DECREF(it);
    return -1;
}

static int
btree_update_common(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyObject *arg = NULL;

    if (!PyArg_UnpackTuple(args, "update", 0, 1, &arg)) {
        return -1;
    }

    if (arg != NULL) {
        if (PyBTree_Check(arg)) {
            /* Fast path: merge from another BTreeDict */
            PyObject *items = PyBTree_Items(arg);
            if (items == NULL)
                return -1;
            Py_ssize_t n = PyList_GET_SIZE(items);
            for (Py_ssize_t i = 0; i < n; i++) {
                PyObject *item = PyList_GET_ITEM(items, i);
                PyObject *key = PyTuple_GET_ITEM(item, 0);
                PyObject *value = PyTuple_GET_ITEM(item, 1);
                if (PyBTree_Insert(self, key, value) < 0) {
                    Py_DECREF(items);
                    return -1;
                }
            }
            Py_DECREF(items);
        }
        else if (PyDict_Check(arg)) {
            /* Fast path for dict */
            PyObject *key, *value;
            Py_ssize_t pos = 0;
            while (PyDict_Next(arg, &pos, &key, &value)) {
                if (PyBTree_Insert(self, key, value) < 0)
                    return -1;
            }
        }
        else if (PyObject_HasAttrString(arg, "keys")) {
            /* Mapping-like object */
            PyObject *keys = PyMapping_Keys(arg);
            if (keys == NULL)
                return -1;
            PyObject *iter = PyObject_GetIter(keys);
            Py_DECREF(keys);
            if (iter == NULL)
                return -1;
            PyObject *key;
            while ((key = PyIter_Next(iter)) != NULL) {
                PyObject *value = PyObject_GetItem(arg, key);
                if (value == NULL) {
                    Py_DECREF(key);
                    Py_DECREF(iter);
                    return -1;
                }
                int status = PyBTree_Insert(self, key, value);
                Py_DECREF(key);
                Py_DECREF(value);
                if (status < 0) {
                    Py_DECREF(iter);
                    return -1;
                }
            }
            Py_DECREF(iter);
            if (PyErr_Occurred())
                return -1;
        }
        else {
            /* Iterable of key-value pairs */
            if (btree_merge_from_seq2(self, arg) < 0)
                return -1;
        }
    }

    if (kwds != NULL && PyDict_Size(kwds) > 0) {
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(kwds, &pos, &key, &value)) {
            if (PyBTree_Insert(self, key, value) < 0)
                return -1;
        }
    }

    return 0;
}

static PyObject *
btree_update(PyObject *self, PyObject *args, PyObject *kwds)
{
    if (btree_update_common(self, args, kwds) < 0) {
        return NULL;
    }
    Py_RETURN_NONE;
}

/* ==================== copy Method ==================== */

PyDoc_STRVAR(btree_copy_doc,
"copy()\n"
"--\n\n"
"Return a shallow copy of the B-tree.");

static PyObject *
btree_copy(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    PyObject *new_btree;
    PyObject *items;

    new_btree = PyBTree_New(btree->order);
    if (new_btree == NULL) {
        return NULL;
    }

    items = PyBTree_Items(self);
    if (items == NULL) {
        Py_DECREF(new_btree);
        return NULL;
    }

    Py_ssize_t n = PyList_GET_SIZE(items);
    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyList_GET_ITEM(items, i);
        PyObject *key = PyTuple_GET_ITEM(item, 0);
        PyObject *value = PyTuple_GET_ITEM(item, 1);
        if (PyBTree_Insert(new_btree, key, value) < 0) {
            Py_DECREF(items);
            Py_DECREF(new_btree);
            return NULL;
        }
    }
    Py_DECREF(items);

    return new_btree;
}

/* ==================== __eq__ Comparison ==================== */

static PyObject *
btree_richcompare(PyObject *self, PyObject *other, int op)
{
    PyBTreeObject *a, *b;
    PyObject *a_items, *b_items;
    int result;

    /* Only support equality/inequality */
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }

    /* Must be comparing two BTreeDicts */
    if (!PyBTree_Check(other)) {
        if (op == Py_EQ) {
            Py_RETURN_FALSE;
        }
        else {
            Py_RETURN_TRUE;
        }
    }

    a = (PyBTreeObject *)self;
    b = (PyBTreeObject *)other;

    /* Quick size check */
    if (a->size != b->size) {
        if (op == Py_EQ) {
            Py_RETURN_FALSE;
        }
        else {
            Py_RETURN_TRUE;
        }
    }

    /* Empty trees are equal */
    if (a->size == 0) {
        if (op == Py_EQ) {
            Py_RETURN_TRUE;
        }
        else {
            Py_RETURN_FALSE;
        }
    }

    /* Compare items */
    a_items = PyBTree_Items(self);
    if (a_items == NULL) {
        return NULL;
    }
    b_items = PyBTree_Items(other);
    if (b_items == NULL) {
        Py_DECREF(a_items);
        return NULL;
    }

    result = PyObject_RichCompareBool(a_items, b_items, Py_EQ);
    Py_DECREF(a_items);
    Py_DECREF(b_items);

    if (result < 0) {
        return NULL;
    }

    if (op == Py_EQ) {
        return PyBool_FromLong(result);
    }
    else {
        return PyBool_FromLong(!result);
    }
}

/* ==================== peekitem Method ==================== */

PyDoc_STRVAR(btree_peekitem_doc,
"peekitem(index=-1, /)\n"
"--\n\n"
"Return (key, value) pair at index. Default is the last (maximum) item.\n"
"Raises IndexError if the B-tree is empty or index is out of range.\n\n"
"Negative indices count from the end. Only -1 (last) and 0 (first) are\n"
"supported for O(log n) performance.");

static PyObject *
btree_peekitem(PyObject *self, PyObject *args)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    Py_ssize_t index = -1;
    PyBTreeNode *node;
    PyObject *key, *value, *result;

    if (!PyArg_ParseTuple(args, "|n", &index)) {
        return NULL;
    }

    if (btree->size == 0) {
        PyErr_SetString(PyExc_IndexError, "peekitem from empty B-tree");
        return NULL;
    }

    /* Only support 0 (first) and -1 (last) for O(log n) */
    if (index == 0) {
        /* Get minimum */
        node = btree->root;
        while (!node->is_leaf) {
            node = node->children[0];
        }
        key = node->keys[0];
        value = node->values[0];
    }
    else if (index == -1 || index == btree->size - 1) {
        /* Get maximum */
        node = btree->root;
        while (!node->is_leaf) {
            node = node->children[node->n_keys];
        }
        key = node->keys[node->n_keys - 1];
        value = node->values[node->n_keys - 1];
    }
    else {
        /* For other indices, we need O(n) traversal - not supported efficiently */
        PyErr_SetString(PyExc_IndexError,
            "peekitem() only supports index 0 (first) or -1 (last) for O(log n) access");
        return NULL;
    }

    result = PyTuple_Pack(2, key, value);
    return result;
}

/* ==================== popitem Method ==================== */

PyDoc_STRVAR(btree_popitem_doc,
"popitem(index=-1, /)\n"
"--\n\n"
"Remove and return (key, value) pair at index. Default is the last (maximum) item.\n"
"Raises KeyError if the B-tree is empty.\n\n"
"Only -1 (last) and 0 (first) are supported for O(log n) performance.");

static PyObject *
btree_popitem(PyObject *self, PyObject *args)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    Py_ssize_t index = -1;
    PyObject *key, *value, *result;

    if (!PyArg_ParseTuple(args, "|n", &index)) {
        return NULL;
    }

    if (btree->size == 0) {
        PyErr_SetString(PyExc_KeyError, "popitem(): B-tree is empty");
        return NULL;
    }

    /* Get the key first */
    if (index == 0) {
        key = PyBTree_GetMin(self);
    }
    else if (index == -1 || index == btree->size - 1) {
        key = PyBTree_GetMax(self);
    }
    else {
        PyErr_SetString(PyExc_IndexError,
            "popitem() only supports index 0 (first) or -1 (last) for O(log n) access");
        return NULL;
    }

    if (key == NULL) {
        return NULL;
    }

    /* Get the value before deleting */
    value = PyBTree_Search(self, key);
    if (value == NULL) {
        Py_DECREF(key);
        if (!PyErr_Occurred()) {
            PyErr_SetString(PyExc_RuntimeError, "key disappeared during popitem");
        }
        return NULL;
    }

    /* Delete the key */
    if (PyBTree_Delete(self, key) < 0) {
        Py_DECREF(key);
        Py_DECREF(value);
        return NULL;
    }

    result = PyTuple_Pack(2, key, value);
    Py_DECREF(key);
    Py_DECREF(value);
    return result;
}

static PyMethodDef btree_methods[] = {
    {"insert", btree_insert, METH_VARARGS, btree_insert_doc},
    {"get", btree_get, METH_VARARGS, btree_get_doc},
    {"pop", btree_pop, METH_VARARGS, btree_pop_doc},
    {"setdefault", btree_setdefault, METH_VARARGS, btree_setdefault_doc},
    {"update", (PyCFunction)btree_update, METH_VARARGS | METH_KEYWORDS, btree_update_doc},
    {"copy", btree_copy, METH_NOARGS, btree_copy_doc},
    {"keys", btree_keys_method, METH_NOARGS, btree_keys_doc},
    {"values", btree_values_method, METH_NOARGS, btree_values_doc},
    {"items", btree_items_method, METH_NOARGS, btree_items_doc},
    {"clear", btree_clear_method, METH_NOARGS, btree_clear_doc},
    {"min", btree_min, METH_NOARGS, btree_min_doc},
    {"max", btree_max, METH_NOARGS, btree_max_doc},
    {"peekitem", btree_peekitem, METH_VARARGS, btree_peekitem_doc},
    {"popitem", btree_popitem, METH_VARARGS, btree_popitem_doc},
    {"irange", (PyCFunction)btree_irange, METH_VARARGS | METH_KEYWORDS, btree_irange_doc},
    {"__reversed__", btree_reversed, METH_NOARGS, "Return a reverse iterator over the keys."},
    {NULL, NULL, 0, NULL}
};

/* ==================== Sequence/Mapping Protocols ==================== */

static PySequenceMethods btree_as_sequence = {
    btree_length,                               /* sq_length */
    0,                                          /* sq_concat */
    0,                                          /* sq_repeat */
    0,                                          /* sq_item */
    0,                                          /* sq_slice */
    0,                                          /* sq_ass_item */
    0,                                          /* sq_ass_slice */
    btree_contains,                             /* sq_contains */
    0,                                          /* sq_inplace_concat */
    0,                                          /* sq_inplace_repeat */
};

static PyMappingMethods btree_as_mapping = {
    btree_length,                               /* mp_length */
    btree_subscript,                            /* mp_subscript */
    btree_ass_subscript,                        /* mp_ass_subscript */
};

/* ==================== BTreeDict __init__ ==================== */

PyDoc_STRVAR(btree_doc,
"BTreeDict(order=8, /)\n"
"--\n\n"
"Create a new B-tree with the specified order (minimum degree).\n\n"
"The order determines the minimum and maximum number of keys in each node:\n"
"- Each node (except root) has at least order-1 keys\n"
"- Each node has at most 2*order-1 keys\n"
"- Default order is 8 (up to 15 keys per node)\n\n"
"Example:\n"
"    >>> bt = BTreeDict()\n"
"    >>> bt[1] = 'one'\n"
"    >>> bt[2] = 'two'\n"
"    >>> bt[1]\n"
"    'one'\n"
"    >>> 1 in bt\n"
"    True\n"
"    >>> list(bt)\n"
"    [1, 2]\n");

static int
btree_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    PyBTreeObject *btree = (PyBTreeObject *)self;
    int order = BTREE_DEFAULT_ORDER;

    static char *kwlist[] = {"order", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &order)) {
        return -1;
    }

    if (order < BTREE_MIN_ORDER) {
        PyErr_Format(PyExc_ValueError,
                     "order must be at least %d, got %d",
                     BTREE_MIN_ORDER, order);
        return -1;
    }

    btree->order = order;
    btree->size = 0;

    /* Clear any existing root */
    Py_CLEAR(btree->root);

    btree->root = (PyBTreeNode *)btreenode_new(order, 1);
    if (btree->root == NULL) {
        return -1;
    }

    return 0;
}

static PyObject *
btree_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyBTreeObject *self;

    self = (PyBTreeObject *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }

    self->root = NULL;
    self->size = 0;
    self->order = BTREE_DEFAULT_ORDER;

    return (PyObject *)self;
}

/* ==================== Type Definition ==================== */

static PyTypeObject PyBTree_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "btree.BTreeDict",                          /* tp_name */
    sizeof(PyBTreeObject),                      /* tp_basicsize */
    0,                                          /* tp_itemsize */
    btree_dealloc,                              /* tp_dealloc */
    0,                                          /* tp_vectorcall_offset */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_as_async */
    btree_repr,                                 /* tp_repr */
    0,                                          /* tp_as_number */
    &btree_as_sequence,                         /* tp_as_sequence */
    &btree_as_mapping,                          /* tp_as_mapping */
    PyObject_HashNotImplemented,                /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    PyObject_GenericGetAttr,                    /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC |
        Py_TPFLAGS_BASETYPE,                    /* tp_flags */
    btree_doc,                                  /* tp_doc */
    btree_traverse,                             /* tp_traverse */
    btree_clear_slot,                           /* tp_clear */
    btree_richcompare,                          /* tp_richcompare */
    0,                                          /* tp_weaklistoffset */
    btree_iter,                                 /* tp_iter */
    0,                                          /* tp_iternext */
    btree_methods,                              /* tp_methods */
    0,                                          /* tp_members */
    0,                                          /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    btree_init,                                 /* tp_init */
    PyType_GenericAlloc,                        /* tp_alloc */
    btree_new,                                  /* tp_new */
    PyObject_GC_Del,                            /* tp_free */
};

/* ==================== Module Definition ==================== */

static struct PyModuleDef btreemodule = {
    PyModuleDef_HEAD_INIT,
    "pybtree",
    "B-Tree data structure module.\n\n"
    "A B-tree is a self-balancing tree data structure that maintains sorted\n"
    "data and allows searches, sequential access, insertions, and deletions\n"
    "in logarithmic time.\n",
    -1,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC
PyInit_pybtree(void)
{
    PyObject *m;

    /* Finalize the type objects */
    if (PyType_Ready(&PyBTreeNode_Type) < 0) {
        return NULL;
    }
    if (PyType_Ready(&PyBTree_Type) < 0) {
        return NULL;
    }
    if (PyType_Ready(&PyBTreeIter_Type) < 0) {
        return NULL;
    }
    if (PyType_Ready(&PyBTreeReverseIter_Type) < 0) {
        return NULL;
    }
    if (PyType_Ready(&PyBTreeRangeIter_Type) < 0) {
        return NULL;
    }

    m = PyModule_Create(&btreemodule);
    if (m == NULL) {
        return NULL;
    }

    /* Add the BTreeDict type to the module */
    Py_INCREF(&PyBTree_Type);
    if (PyModule_AddObject(m, "BTreeDict", (PyObject *)&PyBTree_Type) < 0) {
        Py_DECREF(&PyBTree_Type);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
