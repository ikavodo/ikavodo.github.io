---
title: "Aronson Sequences, pt.2: Generation Strategies"
layout: post
date: 2025-4-7 19:00
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
description: "Continuing the Aronson sequence research: generation strategies and set intersections."
---

## Introduction
This post picks up from [pt.1](https://ikavodo.github.io/aronson-sequences-pt1/), where we left off with an open question about the intersection $(A_T(\to)\cap A_T(\gets))$.

## Generating Aronson sequences

If you need a reminder of past events, be sure to look back to the [first part of this blog-post series](https://ikavodo.github.io/aronson-sequences-pt1/). 

The initial goal in this post is to answer in a satisfactory way the last question provided in the previous blog post, regarding the set of $(A_T(\to)\cap A_T(\gets))$. I thought up a few possible strategies for attempting to address this question. 

The simplest one strategy would be the following: supposing we had all of the time in the world, we could begin to generate random integer sequences, and for each such sequence check whether it is in either $A_T(\to)$, or $A_T(\gets)$ or both. The only additional program this strategy would require then is a *verifier*. 

A different strategy: suppose we had a magic black box that generates sequences from either set. We could enumerate from both in parallel, checking each new sequence against what the other set has already produced.

Let's begin with the task of writing an efficient verifier for $A_T(\to)$.

## Verifier for Aronson sequences   

A verifier is a program that checks whether an input is a valid solution. In the Aronson case: given an input sequence, generate the sentence it implies and check that each element maps to an occurrence of the target letter. This has $\Theta(N)$ time complexity (ignoring the $\Theta(\log k)$ growth of ordinal representations, as shown in pt.1).

A simple verifier which "gets the job done" would be the following:


```python
def verifier1(letter, indices, forward=True):

    sequence = get_sequence(letter, indices, forward)
    # Reverse the sequence if forward is False
    if not forward:
        sequence = sequence[::-1]
    # Check if the input letter matches at the specified indices
    try:
        return all(sequence[i - 1] == letter for i in indices)
    except IndexError:
        return False
```

Where we treat the subroutine get_sequence() as a black box function which generates the underlying sentence from a sequence, ignoring the actual implementation of this function (it is not particularly interesting or relevant for our purposes). The purpose of the try/except blocks is to prevent errors resulting from sequences with elements larger than the length of the resulting generating sentence (i.e. think "T is the first, one hundredth letter").

What else can be said about this specific implementation? The all() function does lazy evaluation (see [this](https://stackoverflow.com/questions/39348588/is-any-evaluated-lazily)), with the bulk of computation being done by the get_sequence() subroutine. In the case of wrong inputs (say an extremely long input sequence with a wrong element at the beginning), this function would then be extremely inefficient! We can take this into account by implementing a second verifier which adresses this shortcoming.

## Second verifier

```python
# consts
START = " is the "
END = " letter"

def verifier2(letter, indices, forward=True):
    # Determine the initial sequence based on the direction (forward or reverse)
    s = (letter + START).replace(" ", "") if forward else END.replace(" ", "")[::-1]
    for idx in indices:
        # Add the ordinal to the sequence
        s += (n2w(idx) if forward else n2w(idx)[::-1])
        try:
            # Check if the letter matches the expected position
            if s[idx - 1] != letter:
                return False
        except IndexError:
            # If the index is out of range, return False
            return False
    return True
``` 

Now let's write a simple script for which the second verifier will run much faster than the first, by generating the first n elements in Aronson's sequence (we'll use a helper function for this), and then "contaminating" these by planting consecutive elements [..,x,x+1,..] somewhere within the sequence. This would correspond to 2 consecutive 't's within the generating sentence- making the sentence most-likely false and leading to verifier2() exiting early. Here's some intuition for this methodology:

```python
#Aronson
def aronson(n, letter, forward=True, inp=None):
    return list(islice(agen_better(letter, forward=forward, inp=inp), n - len(inp)))

>>> seq = aronson(100,'t') 
>>> intervals = [seq[i] - seq[i-1] for i in range(1,len(seq))]
>>> sum([interval == 1 for interval in intervals])
#Number of consecutive elements within first 100 terms of Aronson's sequence 
0
```

Benchmarking on 256 contaminated sequences (consecutive elements planted at a random position) confirms the advantage — verifier_slow averages 0.009s, verifier_fast averages 0.004s per call. The early-exit in verifier_fast saves roughly half the work on inputs that fail near the start.

But verifier_fast has a correctness problem. Notice the following

```python
>>> verifier_fast('l',[1,23])
False
```

where we already established in the previous blogpost that "L is the first, twenty-third letter" is a correct sentence! This means then that verifier_fast() doesn't work correctly for forward-referring sequences (how about verifier_slow())? 
We use then the following final verifier version

```python
def verifier(letter, indices, forward=True, forward_referring=True):
    if forward_referring:
        #slower, correct for edge-cases
        return verifier_slow(letter, indices, forward)
    else:
        #faster, demands building sentence sequentially from ordinals one by one
        return verifier_fast(letter, indices, forward)
```
Notice that we can utilize verifier_fast() only if we have *prior-knowledge* that the sequence of question is not forward-referring, as the process of checking this would be as computationally expensive as the runtime of verifier_slow() (why?). We take on a 'pessimistic' view at the moment, that we may potentially investigate forward-referring sequences, and use the faster version only when we are assured that it is correct.

## Verifier use-cases

### Generating variations on Aronson sequences from input
Our first use-case for our implemented verifier has to do with extending the generating algorithm proposed in the previous blogpost . We saw already that this algorithm looks backwards to generate new elements, while we take into account additional self-referring ('T is the tenth, twelfth,...') and forward-referring sequences in our characterisation of generalized Aronson sequences. We will talk more into depth in the next blog-post (!) about possible approaches for generating such sequences, as this is a non-trivial task, but before doing so, we notice the following:

Say we have an initial self-referring sequence which is not self-contained, for example [10,12] (check this!). Then this sequence can be extended indefinitely with backward-referring elements in a way which could not impact the resulting sequence's correctness (is this true also in the case of forward-referring sequences? Why not?). 

Using the previous example, we would get:

'T is the tenth (self-referring), twelfth (self-referring), seventeenth (backward-referring), twenty-fourth 
(backward-referring).. letter'
 
This allows us to generate new Aronson sequences using our original algorithm, by starting from some input sequence and then generating new elements on the fly from there! 

Here's how this could be done

```python
class VerifierError(Exception):
    pass

#updated Aronson
def aronson(n, letter, forward=True, inp=None, forward_referring=True):
    if inp is None:
        return list(islice(agen_better(letter, forward=forward), n))
    else:
        return inp + list(islice(agen_better(letter, forward=forward, inp=inp, 
            forward_referring=forward_referring), n - len(inp)))

#updated generating function
def agen_better(letter, forward=True, inp=None, forward_referring = True):
    
    def update_from_inp(forward, inp, letter, s):

        if not verifier(letter, inp, forward, forward_referring):
            raise VerifierError(input_data=inp)
        for i in inp:
            s += (n2w(i) if forward else n2w(i)[::-1])
        idx = max(inp)  # inp[-1] if monotonically rising
        s = s[idx:]
        return s, idx

    # Initialize sequence based on direction
    s = (letter + START).replace(" ", "") if forward else END.replace(" ", "")[::-1]
    idx = 0
    if inp:
        # update to given point
        s, idx = update_from_inp(forward, inp, letter, s)
    while True:
        #we saw this already
        try:
            # Find the next occurrence of the letter. If not inside s.find() returns -1, so repeats infinitely
            idx_rel = 1 + s.find(letter)
        except ValueError:
            # safety measure
            break  # Stop if letter is not found
        idx += idx_rel
        yield idx
        # Adjust the sequence for the next iteration
        s = s[idx_rel:] + (n2w(idx) if forward else n2w(idx)[::-1])
```
Notice we use the verifier to check that the initial input sequence is correct, as otherwise the resulting sequence won't be correct either.

Here's a possible way to use the extended algorithm:

```python
>>> n = 5
>>> letter = 't'
>>> inp_seqs = [[], [1, 11], [10, 12]]
>>> for inp in inp_seqs:
#       none of these sequences is forward-referring
        extend = aronson(n,letter,forward=True,inp=inp,forward_referring=False)
        print_sequence(letter, extend)

#Aronson
t is the first, fourth, eleventh, sixteenth, twenty-fourth letter

#First variation generated by removing second element 
t is the first, eleventh, eighteenth, twenty-fourth, twenty-eighth letter

#Second variation generated by giving self-referring input, converges with previous 
t is the tenth, twelfth, seventeenth, twenty-fourth, twenty-eighth letter
```
 
And we can now generate as many variations as we want on Aronson's sequence using the following procedure

```python

def generate_variations(n, letter, forward=True, inp=None):
    # where to start generating variations from
    orig = aronson(n, letter, forward, inp)
    start_idx = -1
    #keep track of generated sequences and which idxs were removed
    stack = [(orig, start_idx)]
    while stack:
        cur, cur_idx = stack.pop()
        yield cur
        # only remove indices forward
        for idx in range(cur_idx + 1, n - 1):
            # slice out current index to generate a new sequence
            inp = cur[:idx] + [cur[idx + 1]]
            try:
                #extend the series to length n
                extend = aronson(n, letter, forward, inp)
            except VerifierError:
                # verifier returned False- meaning sequence is incorrect and can't be extended
                continue
            stack.append((extend, idx))

>>> seen = []
>>> [print(seq) for seq in generate_variations(5, 't')
       if seq not in seen]

#these are all valid, Aronson sequences
[1, 4, 11, 16, 24]
[1, 4, 11, 24, 26]
[1, 4, 16, 21, 25]
[1, 11, 18, 24, 28]
[4, 11, 19, 25, 29]
# ... (12 total)
```

### Finding the intersection of sets

Now we can use our verifier to look for some sequences in both sets of sequences $(A_T(\to)\cap A_T(\gets))$!
Going with the previously mentioned first strategy, a good place to start would be to look for more singleton sequences, as the search space over these sequences is bounded. 

Intuitively, there must be a minimal $m$ for which both of the following hold:

1. For all $n \geq m$, the ordinal word $\text{ordinal}(n)$ is at least as long as $\text{ordinal}(m)$ — i.e., ordinal word lengths are non-decreasing from $m$ onward.
2. $m$ exceeds the total character count of its own sentence: $m > \lvert\text{"t is the "} + \text{ordinal}(m) + \text{" letter"}\rvert$.

This $m$ is then an upper bound on valid singleton indices: any $n \geq m$ produces a sentence shorter than $n$, so position $n$ cannot appear in it.

We can find a minimal upper bound using the following code, where we start from a heuristic upper bound (m=100) and then 'fix' it to something smaller.

```python
START = " is the "
END = " letter" #approximately same length as START
def find_minimal_upper_bound():
    lower = len(START.replace(" ", ""))
    upper = 100  # For n >= 100, len(ordinal(n)) >= len("one-hundred")

    for m in range(2 * lower, upper):
        len_ord_m = len(n2w(m))
        # Check that all larger ordinals are at least as long
        is_candidate = all([len(n2w(k)) >= len_ord_m for k in range(m + 1, upper)])
        # Ensure m is long enough relative to surrounding text
        is_long_enough = (m >= 2 * lower + len_ord_m)

        if is_candidate and is_long_enough:
            return m
>>> find_minimal_upper_bound()
40
```
Now that we have this upper-bound, we can bound the search space and use our verifiers to find singleton sequences within the intersection of sets $(A_T(\to)\cap A_T(\gets))$

```python
def find_singletons(letter):
    upper = find_singleton_upper_bound()
    return {(i,) for i in range(upper) if verifier(letter, (i,), True) and verifier(letter, (i,), False)}

>>> singletons = find_singletons('t')
>>> singletons
{(19,), (4,)}
>>> for seq in singletons:
#       safety measure
        assert(verifier(letter, seq, True))
        assert(verifier(letter, seq, False))
#No AssertionError
```
Surprise: we've found a new singleton sequence ([19]) in $(A_T(\to)\cap A_T(\gets))$! We notice that this sequence is forward-referring in both directions.
However, the search range become in fact unbounded when we look at longer and longer sequences, meaning that the same strategy is unfeasible if we want to find arbitrarily large non-singleton sequences.
Let's now rephrase the original question:

* Are there any *non-singleton* sequences in $(A_T(\to)\cap A_T(\gets))$?

To attempt to answer this question we will use an algorithm based on the second previously discussed strategy:

* Generate sequences from the forward and backward Aronson sequences using the previously implemented generate_variations() function
* Build the power-set of each such sequence, checking for any sub-sequences which belong to both families
* Run verifiers for both directions on these sub-sequences   

The code implementation looks like this, using the slower verifier to correctly handle forward-referring sequences.

```python
def intersect_aronson_sets(n, letter):
    def power_set(seq):
        return set(chain.from_iterable(combinations(seq, r) for r in range(len(seq) + 1)))

    # Initialize sets to accumulate power sets for both directions
    power_sets = [set(), set()]
    # Create generators for both directions
    gen_forward = generate_variations(n, letter, True)
    gen_backward = generate_variations(n, letter, False)
    for seq_fwd, seq_bwd in zip(gen_forward, gen_backward):
        power_sets[0].update(power_set(seq_fwd))
        power_sets[1].update(power_set(seq_bwd))

    # Compute intersection of both power sets
    common_subsets = power_sets[0] & power_sets[1]
    # Filter by verifier
    return {i for i in intersection if verifier(letter,i,forward=True) and verifier(letter,i,forward=False)}
```  
```shell
> print(intersect_aronson_sets(n, letter))
{(19,), (4,), ()}
```
No luck, it seems that we will have to work harder than this to find non-singleton sequences in the intersection of sets (if such exist at all).

## Conclusion
We discovered a valuable tool for our search problem in the form of a verifier, and have shown how it helps us generate new, correct Aronson sequences, as well as received more insight into the nature of the opening enquiry, about the intersection of sets of Aronson sequences. Not bad for a day's work.

Until next time!