/* B-Tree object interface
 *
 * A self-balancing tree data structure that maintains sorted data and allows
 * searches, sequential access, insertions, and deletions in logarithmic time.
 * This implementation stores Python objects as keys.
 */

#ifndef Py_BTREEOBJECT_H
#define Py_BTREEOBJECT_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declarations */
typedef struct _PyBTreeNode PyBTreeNode;
typedef struct _PyBTreeObject PyBTreeObject;

/* Type objects */
PyAPI_DATA(PyTypeObject) PyBTree_Type;
PyAPI_DATA(PyTypeObject) PyBTreeNode_Type;
PyAPI_DATA(PyTypeObject) PyBTreeIter_Type;
PyAPI_DATA(PyTypeObject) PyBTreeReverseIter_Type;
PyAPI_DATA(PyTypeObject) PyBTreeRangeIter_Type;

/* Type check macros */
#define PyBTree_Check(op) PyObject_TypeCheck((op), &PyBTree_Type)
#define PyBTree_CheckExact(op) Py_IS_TYPE((op), &PyBTree_Type)

/* Public API functions */

/* Create a new empty B-tree with specified order (minimum degree).
 * Order must be >= 2. Default order is 64 if order <= 1.
 * Returns NULL on failure.
 */
PyAPI_FUNC(PyObject *) PyBTree_New(int order);

/* Get the number of items in the B-tree */
PyAPI_FUNC(Py_ssize_t) PyBTree_Size(PyObject *btree);

/* Insert a key-value pair into the B-tree.
 * Returns 0 on success, -1 on failure.
 */
PyAPI_FUNC(int) PyBTree_Insert(PyObject *btree, PyObject *key, PyObject *value);

/* Search for a key in the B-tree.
 * Returns a new reference to the value if found, NULL if not found.
 * Does not set an exception if key is not found.
 */
PyAPI_FUNC(PyObject *) PyBTree_Search(PyObject *btree, PyObject *key);

/* Delete a key from the B-tree.
 * Returns 0 on success, -1 on failure (key not found or error).
 */
PyAPI_FUNC(int) PyBTree_Delete(PyObject *btree, PyObject *key);

/* Check if a key exists in the B-tree.
 * Returns 1 if found, 0 if not found, -1 on error.
 */
PyAPI_FUNC(int) PyBTree_Contains(PyObject *btree, PyObject *key);

/* Get minimum key in the B-tree.
 * Returns a new reference, or NULL if tree is empty.
 */
PyAPI_FUNC(PyObject *) PyBTree_GetMin(PyObject *btree);

/* Get maximum key in the B-tree.
 * Returns a new reference, or NULL if tree is empty.
 */
PyAPI_FUNC(PyObject *) PyBTree_GetMax(PyObject *btree);

/* Get all keys as a list (in sorted order).
 * Returns a new list object, or NULL on failure.
 */
PyAPI_FUNC(PyObject *) PyBTree_Keys(PyObject *btree);

/* Get all values as a list (in key-sorted order).
 * Returns a new list object, or NULL on failure.
 */
PyAPI_FUNC(PyObject *) PyBTree_Values(PyObject *btree);

/* Get all items as a list of (key, value) tuples (in sorted order).
 * Returns a new list object, or NULL on failure.
 */
PyAPI_FUNC(PyObject *) PyBTree_Items(PyObject *btree);

/* Clear all items from the B-tree.
 * Returns 0 on success.
 */
PyAPI_FUNC(int) PyBTree_Clear(PyObject *btree);

/* Copy the B-tree (shallow copy).
 * Returns a new B-tree object, or NULL on failure.
 */
PyAPI_FUNC(PyObject *) PyBTree_Copy(PyObject *btree);

/* Update B-tree with items from another mapping or iterable.
 * Returns 0 on success, -1 on failure.
 */
PyAPI_FUNC(int) PyBTree_Update(PyObject *btree, PyObject *other);

#ifdef __cplusplus
}
#endif
#endif /* !Py_BTREEOBJECT_H */
