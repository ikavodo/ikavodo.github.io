---
title: "Getting More from LLMs: A Practical Self-Audit"
layout: post
date: 2025-07-18 15:45
image: /assets/images/llms.jpg
headerImage: true
tags:
  - LLMs
  - Research
star: true
category: blog
author: Ido Akov
description: "Practical tips for improving LLM prompting, distilled from an audit of my own chat history."
---

I recently compressed all my LLM conversations and ran them through an AI prompt-review. The results were instructive — not because they revealed anything shocking, but because seeing patterns in your own prompts is different from knowing they exist in the abstract.

## What Was Missing

The clearest theme: I was often too terse about context. A question like “why does this convolution look wrong?” is hard to answer without knowing what it’s supposed to do, what “wrong” means, and what I’d already tried. The more useful version names the domain and stakes:

> “In Transformer architectures, why must Q/K matrices share dimensionality? Explain with attention-score normalization.”

Closely related: I kept sending fragmented follow-ups when I should have batched them. Three consecutive messages about the same class method wastes context and generates redundant preambles. Better to combine:

> “Implement `|` and `|=` for my `AronsonSet` class. Ensure `iter_dict` updates.”

Two smaller habits that help:

- **State the mode.** “Critique this `ceil()` implementation for edge cases” is cleaner than “look at this” — it tells the model whether to explain, rewrite, or challenge.
- **Ask for failure cases.** Prompting for what breaks (“What could break this regex? `r’\bT is the (\S+) letter’`”) is more useful than asking whether something works.

---

## Controlling the Output

My natural style is direct and information-dense, which works well for code and technical questions. The risk is that it can discourage nuance. Two modifiers worth keeping handy:

- _”Explain like I’m a beginner.”_
- _”Now optimize for brevity.”_

A few structural tricks also help:

**Pre-constrain the format.** “Give a 3-sentence summary, then 3 bullet points of caveats” produces tighter responses than an open-ended question. The model fills available space — constrain it.

**Force prioritization.** “Rank these by memory usage for n=1e6” is more useful than “compare these.” It produces a decision, not a list.

**Ask the meta-question.** “What key question did I forget to ask about [topic]?” is surprisingly effective — the model often surfaces a constraint or assumption you hadn’t thought to name.

---

## A Simple Prompt Framework

The most reusable pattern I found: **Background, Question, Hypothesis** (BQH). Give one sentence of context, state what you want, and optionally share your current assumption.

Example: *”SIFT isn’t differentiable — confirm?”* That’s B (SIFT), Q (confirm this property), and an implicit H (my assumption is yes). The hypothesis is optional but useful when you want pushback rather than explanation.

---

## LLMs as a Learning Partner

The prompts I got the most from weren’t tasks — they were adversarial or generative:

- “What edge cases should I test for this motion vector code?” forces the model to think about failure, not correctness.
- “Critique this research idea. What assumptions might be invalid?” turns it into a skeptical collaborator.
- “First explain `grid_sample`, then show how to use it with motion maps.” scaffolds understanding rather than just providing an answer.

---

> **”Optimize, but leave room for the serendipitous.”**