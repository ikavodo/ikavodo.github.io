---
title: "Aronson Sequences: A Self‑Referential Rabbit Hole (Part 1)"
layout: post
date: 2025-01-27 19:00
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
description: "Introducing the Aronson sequence, its generalizations, and the first steps into an ongoing research project."
---

## Introduction

A few months ago, while clearing out a storage space, my parents unearthed my old copy of Douglas Hofstadter’s *Metamagical Themas*. Flipping through it reminded me of an essay on self‑referential sentences, in particular one that generates the **Aronson sequence**:

> "T is the first, fourth, eleventh, sixteenth… letter (in this sentence, not counting spaces or commas)."

I first encountered this sequence years ago, when I tried (and failed) to implement it in Python. That failure stuck with me. Now, with a bit more experience under my belt, I’m ready to dive back in – and this time I want to document the journey in real time. Consider this the first entry in a research diary.

In this post we’ll define the Aronson sequence, explore its properties, and start generalizing it in several directions. We’ll also see some code, some data, and end with open questions that will guide the next installment.

---

## What is the Aronson Sequence?

The generating sentence is self‑referential: it lists the positions of the letter **t** within itself. The sequence of ordinals is

```
1, 4, 11, 16, 24, 29, 33, 35, 39, 45, …
```

(These are the indices where the letter `t` appears, counting from 1 and ignoring spaces and punctuation.)

A few immediate observations:

- **Self‑reference:** The sentence talks about its own letters.
- **Semantic correctness:** The ordinals really do point to positions where `t` occurs.
- **Backward reference:** Each new ordinal points to a position *earlier* in the sentence.
- **Completeness**: The first N terms of the sequence map to *all* `t`s in some prefix of the generating sentence. Intuitively this means that every *ordinal-enumerated* `t` is eventually captured (what about the `t`s in "letter"?).

The last two points hint at whether the sequence can be enumerated ad infinitum. Intuitively, if the gaps between ordinals and their positions grow without bound, the probability of encountering a long stretch without a `t` becomes vanishingly small – so the sequence is almost certainly infinite.

---
## Implementation

Michael Branicky contributed a wonderfully compact generator to the OEIS ([A005224](https://oeis.org/A005224)). Here it is, slightly adapted:

```python
from num2words import num2words
from itertools import islice

def n2w(n):
    # ordinal as a string, stripped of spaces, commas, hyphens
    os = num2words(n, ordinal=True).replace(" and", "")
    return os.replace(", ", "").replace(" ", "").replace("-", "")

def agen():
    s, idx = "tisthe", 0
    while True:
        idx_rel = 1 + s.index('t')
        idx += idx_rel
        yield idx
        s = s[idx_rel:] + n2w(idx)

print(list(islice(agen(), 10)))
# [1, 4, 11, 16, 24, 29, 33, 35, 39, 45]
```

The generator works by keeping a moving window `s` that always starts just after the last counted `t`. As long as `t`s exist in the updated `s`, we can enumerate terms ad infinitum!  

### Finite or infinite?
I set up an experiment to keep track of the number of `t`s in `s` and their overall density for the first 100 000 Aronson sequence terms:

| **n** | **len(s)** | **#t** | &nbsp;&nbsp;&nbsp; **$\frac{\text{#t}}{len(s)}$** |
|------:|-----------:|------------:|----------:|
| 1     | 6          | 2           | 33.3%     |
| 10    | 60         | 13          | 21.7%     |
| 100   | 1239       | 127         | 10.3%     |
| 1000  | 22878      | 2452        | 10.7%     |
| 10000 | 289786     | 36618       | 12.6%     |
| 100000| 3848300    | 398603      | 10.4%     |

Comparing the first and third columns reveals that at every index **n** we can generate *at least* **n** more terms from the sliding window. It suffices to prove this via induction to show that the sequence is infinite (Exercise for the reader).

Note also that the ratio **$\frac{\text{#t}}{len(s)}$** stabilizes and remains approximately constant, meaning that both the sliding window `s` and the density of `t`s have the same order of growth $\mathcal{\Omega}(n)$.

---

## Generalizations

Once you have one self‑referential sequence, it’s hard not to ask: what about other letters? Other directions?

### Other Letters

If we replace ‘t’ with another character, the generating sentence may still be meaningful. For example:

> "L is the first, twenty‑third letter."

is semantically correct, self‑contained, and *forward‑referring* – the ordinal 23 points ahead of itself. We’ll call such sequences **forward‑referring**, while the original Aronson is **backward‑referring**.

Not all letters work; only those that appear in the fixed parts of the sentence (`isthelr`) have a chance. But even among those, some yield finite sequences (e.g., ‘i’ consumes itself immediately).

### Variations

We can also generate variations of the original by omitting or swapping ordinals, as long as the sentence remains correct. For instance:

> t is the first, eleventh, eighteenth, twenty‑fourth… letter

(we skipped the second term) still works, and is presumably infinite. This shows there are infinitely many different Aronson‑type sequences – we can denote the set of all such (for letter ‘t’) as $A_T(\to)$.

### Reverse Direction

What if we generate the sentence from the end, counting *backwards*? Starting with the last word “letter” and working leftwards, we obtain the **reverse Aronson sequence**:

> (counting backwards) t is the …thirteenth, eleventh, fourth, third letter.

This yields `3, 4, 11, 13, …`. Its generator can be obtained by a small modification of the forward algorithm.
Note that this sequence also appear to be infinite.

Next, we can denote the set of all reverse sequences $A_T(\gets)$. This is set is presumably infinite as well, for the same reason as $A_T(\to)$.

---

## Open Questions

Let's generalise the sets $A_T(\to), A_T(\gets)$ to include *all* semantically correct, Aronson-like sequences. This allows for sentences such as "T is the tenth letter", which cannot be derived from the original (why?).

A few questions come to mind:

1. Are there infinitely many *forward‑referring* sequences in $A_T(\to), A_T(\gets)$? 
2. What about sequences that are correct with regard to both directions? Are there any such, and if so is $A_T(\to) \cap A_T(\gets)$ also countably infinite?  
3. Can we generate a monotonically *decreasing* infinite Aronson‑type sequence in either set?  

In the next post, we’ll tackle question 2 by building a **verifier** – a program that checks whether a given list of ordinals can form a correct Aronson sentence – and using it to search for sequences that belong to both families.

---

[^1]: A rigorous proof of infiniteness would involve showing that the gaps between ordinals grow slower than the expected waiting time for the next `t`. But that’s a project for another day.
