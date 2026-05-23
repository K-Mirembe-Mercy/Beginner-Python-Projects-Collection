"""
four_algorithms.py
==================
Demonstrations of 4 classic algorithms:
  1. Binary Search       – O(log n) search in a sorted list
  2. Bubble Sort         – O(n²) comparison-based sort
  3. Merge Sort          – O(n log n) divide-and-conquer sort
  4. Fibonacci (Dynamic) – O(n) DP with memoisation
"""

import time
import random


# ─────────────────────────────────────────────
# 1. BINARY SEARCH
# ─────────────────────────────────────────────
def binary_search(arr: list, target: int) -> int:
    """
    Search for *target* in a sorted list using Binary Search.

    Returns the index of the target if found, otherwise -1.
    Time complexity : O(log n)
    Space complexity: O(1)
    """
    low, high = 0, len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


# ─────────────────────────────────────────────
# 2. BUBBLE SORT
# ─────────────────────────────────────────────
def bubble_sort(arr: list) -> list:
    """
    Sort a list in ascending order using Bubble Sort.

    Repeatedly steps through the list, compares adjacent elements,
    and swaps them if they are in the wrong order.
    Time complexity : O(n²)  –  O(n) best case (already sorted)
    Space complexity: O(1)
    """
    arr = arr.copy()          # don't mutate the original
    n = len(arr)

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:       # early-exit optimisation
            break

    return arr


# ─────────────────────────────────────────────
# 3. MERGE SORT
# ─────────────────────────────────────────────
def merge_sort(arr: list) -> list:
    """
    Sort a list in ascending order using Merge Sort.

    Divides the list in half, recursively sorts each half,
    then merges the sorted halves back together.
    Time complexity : O(n log n)
    Space complexity: O(n)
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return _merge(left, right)


def _merge(left: list, right: list) -> list:
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]);  i += 1
        else:
            result.append(right[j]); j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ─────────────────────────────────────────────
# 4. FIBONACCI – DYNAMIC PROGRAMMING (memoisation)
# ─────────────────────────────────────────────
def fibonacci(n: int, memo: dict | None = None) -> int:
    """
    Return the n-th Fibonacci number using top-down Dynamic Programming
    (memoisation).

    F(0) = 0,  F(1) = 1,  F(n) = F(n-1) + F(n-2)
    Time complexity : O(n)
    Space complexity: O(n)
    """
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]
    if n <= 0:
        return 0
    if n == 1:
        return 1

    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]


# ─────────────────────────────────────────────
# DEMO / MAIN
# ─────────────────────────────────────────────
def separator(title: str) -> None:
    width = 52
    print(f"\n{'═' * width}")
    print(f"  {title}")
    print(f"{'═' * width}")


def demo_binary_search() -> None:
    separator("1. BINARY SEARCH")
    data = sorted(random.sample(range(1, 200), 20))
    print(f"  Sorted list : {data}")

    for target in [data[5], data[-1], 999]:
        idx = binary_search(data, target)
        if idx != -1:
            print(f"  Search {target:>3}  →  found at index {idx}")
        else:
            print(f"  Search {target:>3}  →  not found")


def demo_bubble_sort() -> None:
    separator("2. BUBBLE SORT")
    data = random.sample(range(1, 100), 10)
    print(f"  Before : {data}")
    sorted_data = bubble_sort(data)
    print(f"  After  : {sorted_data}")


def demo_merge_sort() -> None:
    separator("3. MERGE SORT")
    data = random.sample(range(1, 100), 10)
    print(f"  Before : {data}")
    sorted_data = merge_sort(data)
    print(f"  After  : {sorted_data}")

    # Quick performance comparison against bubble sort on a larger list
    big = random.sample(range(1, 10_001), 2_000)

    t0 = time.perf_counter()
    bubble_sort(big)
    t_bubble = time.perf_counter() - t0

    t0 = time.perf_counter()
    merge_sort(big)
    t_merge = time.perf_counter() - t0

    print(f"\n  Performance on 2 000 random integers:")
    print(f"    Bubble Sort : {t_bubble * 1000:.2f} ms")
    print(f"    Merge Sort  : {t_merge  * 1000:.2f} ms")


def demo_fibonacci() -> None:
    separator("4. FIBONACCI – DYNAMIC PROGRAMMING")
    terms = [0, 1, 5, 10, 20, 30, 40, 50]
    print("  n   →  F(n)")
    for n in terms:
        print(f"  {n:<3} →  {fibonacci(n)}")

    # Show the speed benefit of memoisation
    t0 = time.perf_counter()
    result = fibonacci(900)
    elapsed = (time.perf_counter() - t0) * 1_000
    print(f"\n  F(900) computed in {elapsed:.4f} ms")
    print(f"  F(900) = {result}")


if __name__ == "__main__":
    print("\n  FOUR CLASSIC ALGORITHMS – Python Demo")

    demo_binary_search()
    demo_bubble_sort()
    demo_merge_sort()
    demo_fibonacci()

    print(f"\n{'═' * 52}\n  All demos complete.\n{'═' * 52}\n")
