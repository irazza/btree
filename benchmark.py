
import time
import random
import btree

def benchmark():
    N = 100000
    t = btree.BTree(50) # Order 50
    keys = list(range(N))
    random.shuffle(keys)
    
    start = time.time()
    for k in keys:
        t[k] = k
    end = time.time()
    print(f"Insert {N} items: {end - start:.4f}s")
    
    start = time.time()
    for k in keys:
        _ = t[k]
    end = time.time()
    print(f"Search {N} items: {end - start:.4f}s")

    start = time.time()
    for k in keys:
        del t[k]
    end = time.time()
    print(f"Delete {N} items: {end - start:.4f}s")

if __name__ == "__main__":
    benchmark()
