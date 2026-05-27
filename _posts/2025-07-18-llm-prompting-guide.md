---
title: "LLM Prompting & Learning Guide"
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
description: "LLM Prompting and Learning Guide"
---

# LLM Prompting & Learning Guide  
I spent today downloading and processing all of my chats with LLMs, with the purpose of compressing my previous prompts and using them to get an LLM prompt-review!
I got some useful tips which I think might prove helpful for other researchers, then I'm going ahead and putting up this **practical companion for improving efficiency, learning, and collaboration with language models.**



---

## Strengths in LLM Interactions

### 1. **Precision in Technical Queries**
- Clear and concise code-related queries.
- Specific task-driven requests (e.g., “make this function a one-liner”).

### 2. **Depth of Exploration**
- Engage conceptual boundaries (e.g., AI agency).
- Stress-test LLM capabilities (e.g., “solve Riemann’s hypothesis”).

### 3. **Iterative Refinement**
- Follow up to clarify or correct model outputs.
- Request simplifications, optimizations, or alternative approaches.

### 4. **Multimodal Use**
- Apply LLMs across disciplines: code, music, philosophy, bureaucracy, etc.

---

## ⚙Areas for Improvement

### 1. **Add Context to Abstract Queries**
- Add background.  
  _Example_:  
  > “In Transformer architectures, why must Q/K matrices share dimensionality? Explain with attention-score normalization.”

### 2. **Avoid Over-Fragmentation**
- Batch related ideas.  
  _Example_:  
  > “Implement `|` and `|=` for my `AronsonSet` class. Ensure `iter_dict` updates.”

### 3. **Clarify Ownership of Requests**
- State whether you want critique, explanation, or rewrite.  
  _Example_:  
  > “Critique this `ceil()` implementation for edge cases.”

### 4. **Ask for Error Traps**
- Prompt for edge cases and what can break.  
  _Example_:  
  > “What could break this regex? `r'\bT is the (\S+) letter'`”

### 5. **Balance Theory with Practice**
- Anchor the theoretical with application or testing.  
  _Example_:  
  > “Given Borges’ Tlön, design a test for LLM ‘independent thought’. Provide pseudocode.”

---

## Interaction Style Reflection

- **Tone**: Direct, efficient.  
- **Strength**: Low fluff, high information density.  
- **Risk**: Might discourage nuance.

### Suggested Style Enhancers:
1. _“Explain like I’m a beginner.”_
2. _“Now optimize for brevity.”_

---

## Optimizing LLM Outputs

### 1. **Pre-constrain Format**
> “Give a 3-sentence summary, then 3 bullet points of caveats.”

### 2. **Force Prioritization**
> “Rank these by memory usage for n=1e6.”

### 3. **Meta-Awareness**
> “What key question did I forget to ask about [topic]?”

---

## The BQH Prompt Framework

- **B**ackground: Give 1 sentence of context.  
- **Q**uestion: What do you want?  
- **H**ypothesis: Share your assumption (optional).  
  _Example_:  
  > “SIFT isn’t differentiable — confirm?”

---

## Learning and Development Tips

### For Programming:
- Automate documentation (docstrings, linters).
- Use test generation (LLM-assisted or libraries).
- Read advanced PyTorch tutorials and profiling tools (e.g., Nsight).

### For Theoretical Growth:
- Dive deeper into \<insert fields here\>.
- Study foundational \<insert fields here\>.

### Research Practices:
- Use reproducibility tools (e.g., DVC).
- Contribute to open-source CV/ML libraries.
- Turn experiments into papers or interactive demos.

---

## Using LLMs as a Learning Partner

- Ask for failure cases:  
  > “What edge cases should I test for this motion vector code?”

- Simulate peer review:  
  > “Critique this research idea. What assumptions might be invalid?”

- Scaffold interaction:  
  > “First explain `grid_sample`, then show how to use it with motion maps.”

---

## Final Motto

> **“Optimize, but leave room for the serendipitous.”**