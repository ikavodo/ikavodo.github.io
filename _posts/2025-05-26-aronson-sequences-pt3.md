---
title: "Aronson Sequences, pt.3: Enumeration and Pruning"
layout: post
date: 2025-5-26 19:00
image: /assets/images/aronson.png
headerImage: true
tags:
  - Algorithms
  - Sequences
  - Set Theory
  - Computer Science
  - Discrete mathematics
star: true
category: blog
author: Ido Akov
description: "Exhaustively enumerating all Aronson sequences up to length 5 via backtracking with metric-based pruning."
---

## Introduction

In [pt.1](https://ikavodo.github.io/aronson-sequences-pt1/) and [pt.2](https://ikavodo.github.io/aronson-sequences-pt2/) we defined two sets of self-referential Aronson sequences — the forward set $A_T(\to)$ and the backward set $A_T(\gets)$ — and asked what their intersection looks like. We found a handful of singletons but left the general question open.

I finally got around to building the full enumeration machinery. For sequences of length $\leq 5$ we can list *every* valid forward and backward Aronson sequence — but only if we prune the search space aggressively. This post walks through the bounds and the algorithm, and ends with the counts.

---

## Why the Search Space is Finite per Length

A valid Aronson sequence of length $n$ is a list of positive integers $i_1, i_2, \dots, i_n$ such that in the sentence

> T is the [ord($i_1$)], [ord($i_2$)], … [ord($i_n$)] letter

(stripping spaces, commas and hyphens) the letter 'T' appears exactly at positions $i_1, \dots, i_n$.

The key observation is that the largest index $M = \max_k i_k$ cannot be arbitrarily large. The sentence has a fixed part (the prefix "tisthe" and the suffix "letter") and a variable part made up of the stripped ordinal strings. Letting $\ell(i)$ denote the length of the stripped ordinal for $i$ (e.g. $\ell(11) = 8$ for `"eleventh"`), the total sentence length is

<div>
$$L = C + \sum_{k=1}^{n} \ell(i_k)$$
</div>

where $C = 12$ accounts for the fixed prefix and suffix. Since $M$ is itself a position in the sentence we need $M \leq L$, and since $\ell(i_k) \leq \ell_{\max}(M)$ for all $k$, this gives

<div>
$$M \leq C + n \cdot \ell_{\max}(M) \tag{1}$$
</div>

where $\ell_{\max}(M)$ is the maximum ordinal length among all integers up to $M$. The function $\ell_{\max}$ is non-decreasing and jumps only when $M$ crosses a power of ten. Inequality (1) therefore gives an implicit upper bound on $M$ for any fixed $n$. For $n = 5$ this works out to roughly $M \leq 92$, making the search space about $\binom{92}{5} \approx 2.7 \times 10^7$ candidate sets — large, but manageable with good pruning.

---

## Bounds and Non-Elements Pruning

To make the bound concrete we need $\ell_{\max}(d)$ for each digit length $d$, computed by scanning all ordinals up to $10^d$. The resulting table is stored as a constant:

```python
ORD_TABLE = {i + 1: j for i, j in enumerate([7, 14, 26, 39, 45, 56, 69, 75, 87, 99])}
```

| digits | max ordinal length |
|--------|------------------:|
| 1      | 7                 |
| 2      | 14                |
| 3      | 26                |
| 4      | 39                |
| 5      | 45                |
| ...    | ...               |


A quick empirical observation cuts the search space further: certain integers never appear in *any* correct forward or backward Aronson sequence over 't'. Specifically:

- **Forward**: $\{2, 3, 5, 6, 8, 9\}$
- **Backward**: $\{1, 2, 5, 6, 9, 10\}$

The intuition: the initial fixed prefix `"tisthe"` (forward) or `"rettel"` (backward) determines which character positions can hold a 't'. Positions 2, 3, 5, 6, 8, 9 simply don't land on 't' in the forward prefix — and adding more ordinals to the sentence only shifts things rightward, never bringing 't' to those slots. These can be provably excluded from the search at no cost.

---

## Backtracking with Metric Pruning

The generator tries to extend a partial sequence by appending the next candidate integer, checking at each step whether the partial sequence can possibly be completed. The key is an aggressive pruning condition applied at the leaves.

Given a complete candidate sequence, compute:

```python
mean = current_sum / max_len
metric = max(x - mean for x in current_perm)
upper_metric_bound = ceil(log2(len(current_perm)) * ORD_TABLE[cur_ord_key])

if metric <= upper_metric_bound:
    yield current_perm.copy()
```

The **metric** measures how far the largest index is from the mean — i.e., how "spread out" the sequence is. If it's too spread, the large indices won't fit inside the sentence their own ordinals generate. The bound `ceil(log2(n) * ORD_TABLE[key])` scales with sequence length (longer sequences allow proportionally more spread) and with the current digit count of the upper bound (longer ordinals permit larger indices).

This heuristic cuts the search space by orders of magnitude. Combined with the `non_elements` exclusion and the upper bound from (1), the backtracking becomes tractable up to length 5.

The repo also implements `generate_fast()`, which replaces backtracking with rule-based swap and subset operations. It's faster and suitable for continuing from an already-enumerated set, but not guaranteed to find every sequence. The two methods are designed to be used together: `generate_full(n)` for exact counts up to some length, then `generate_fast(m)` to extend quickly.

---

## Results

Running the enumeration (parallelised across cores) and verifying each candidate gives the following counts:

| $n$ | $A_T(\to)$ | $A_T(\gets)$ | $A_T(\to)\cap A_T(\gets)$ |
|-----|--------:|---------:|-------------:|
| 1   | 8       | 7        | 2            |
| 2   | 73      | 67       | 4            |
| 3   | 955     | 771      | 7            |
| 4   | 16,205  | 13,113   | 8            |
| 5   | 336,890 | 279,981  | 37           |

The intersection is extremely sparse relative to either set, yet it does grow with $n$. Whether the growth eventually becomes exponential — matching the growth of the full sets — is an open question that would likely require either a proof or enumeration at length 6 and beyond.

---

All the code used here is in the following [repository](https://github.com/ikavodo/aron_gen). On the more surprising side: a question about Aronson sets was submitted to [Humanity's Last Exam](https://agi.safe.ai/) and reviewed favorably — it turns out that counting these self-referential sequences is easy to state and hard to solve, which is precisely what that benchmark looks for.
