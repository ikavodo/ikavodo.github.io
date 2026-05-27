---

title: "Aronson Sequences: In Search of the Intersection (Part 2)"
layout: post
date: 2025-04-07 19:00
image: /assets/images/aronson.png
headerImage: true
tags:
  - Algorithms
  - Sequences
  - Set Theory
  - Computer Science
  - Discrete Mathematics
star: true
category: blog
author: Ido Akov
description: "Using a verifier to explore sequences that are both forward‑ and backward‑referring."
---

## Introduction

In [Part 1](https://ikavodo.github.io/aronson-1/) we met the Aronson sequence and its generalizations. We defined two sets:

- $A_T(\to)$ – Aronson-like sequences for the letter ‘t’.
- $A_T(\gets)$ – Reverse sequences (counting from the end).

The most intriguing question in the previous post was: **What is $A_T(\to) \cap A_T(\gets)$?** Which sequences work in both directions, and are there infinitely many such?

This post describes my attempt to find them, using a computational **verifier** and a bit of combinatorial search.

---

## A Backward Verifier for Aronson Sentences

A verifier takes a candidate sequence (a list of integers) and a letter, and returns `True` if the corresponding sentence correctly places that letter at the given indices. 

Here’s an implementation that works for both directions:

```python
from num2words import num2words

def n2w(n):
    """Ordinal as a string, stripped of spaces, commas, hyphens, and 'and'."""
    os = num2words(n, ordinal=True).replace(" and", "")
    return os.replace(", ", "").replace(" ", "").replace("-", "")

def verifier(letter, indices, forward):
    # Fixed parts (ignoring spaces)
    prefix = letter + "isthe"
    suffix = "letter"
    
    # Build the sentence in reading order:
    ords_in_order = indices if forward else reversed(indices)
    
    # Phase 1: construct the string and note indices that are out of reach
    sentence = prefix
    pending = []          # indices that couldn't be checked yet
    for i in ords_in_order:
        word = n2w(i)
        sentence += word
        if i > len(sentence):
            # The target position hasn't been built yet – postpone
            pending.append(i)
        else:
            if sentence[i-1] != letter:
                return False
    
    # Add the suffix
    sentence += suffix
    
    # Phase 2: check all postponed indices now that the sentence is complete
    for i in pending:
        if i > len(sentence) or sentence[i-1] != letter:
            return False
    
    return True
```
(We ignore spaces and punctuation for simplicity – they don’t affect the logic.)

In the case of backward-referring sequences, the verifier checks correctness index by index, which is more efficient than generating the entire sentence. In the case of forward-referring sequences this becomes necessary. 

---

## Bounding the Search for Singleton Sequences

Before hunting for long sequences, let’s find all *one‑element* (singleton) sequences that belong to both sets. ordinal string representations grow with order $\mathcal{O}(\log(n))$ (similarly to digit representations), whereas the generating sentence length has order $\mathcal{\theta}(n)$ (terms accumulate), meaning there is some maximum position $M$, the ordinal representation of which is "too short" for the sentence to be semantically correct. 

A quick script finds that $M=40$, and looking for the intersection over singleton sets in both directions reveals:

```python
{(4,), (19,)}
```

Note that the first is *backward-referring*, and the second *forward-referring* in both directions.

---

## Searching for Non‑Singleton Intersections

Now we can try to find longer sequences that work in both directions. The space is huge, so we need a strategy.

**Idea 1:** Generate all variations of the forward Aronson sequence (by omitting or swapping terms) and check each against the backward verifier (all variations are backwards-referring). If a variation is valid in both directions, we’ve found an intersection element.

We can generate variations using a simple BFS on the original forward sequence: start with the full sequence of length `n`, then recursively generate all subsequences (keeping order) and extend them back to length `n` using the original generator. This yields a set of candidate sequences.

**Idea 2:** Use the same idea but start from the reverse Aronson sequence. 

Unfortunately, in both cases the result is 
```python
{(4,), ()}
```
meaning that generating backward-referring sequences is insufficient for finding *all* sequences in the intersection set. This motivates then a *brute-force* approach.

---

## Conclusion

We built a verifier for backward-referring Aronson‑type sentences and used it to probe the intersection $A_T(\to) \cap A_T(\gets)$. So far only two singleton candidates have appeared; the search continues.

In the next installment, I'll suggest a metric for pruning sequences, allowing us to generate non-trivial sequences of increasing length. 

Until then, happy self‑referencing!