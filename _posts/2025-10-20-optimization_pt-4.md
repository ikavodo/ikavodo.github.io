---
title: "Motion computation via an unsupervised-learning approach (pt.4)"
layout: post
date: 2025-11-25 18:00
image: 
headerImage: false
tags:
  - Computer Science
  - Math
  - Optimization
star: true
category: blog
author: Ido Akov
description: "Optimization"
---
As promised previously, this time we talk about generalized cross-correlation phase transform (GCC-PHAT) and possible connections to our algorithm.
This time we'll be taking a look at a 1D formulation of our problem, and see if anything new comes out of this.
We'll also discuss occlusion models, and how they impact our Fourier formulation, as well as possible implications of this.

## 1D formulation

Recall that we are working with a 2D image modality. To think of the 1D formulation of the problem- imagine "slicing" our motion video with respect to one axis, and looking at the change in some such 'strip' across the motion video. For example, given our square object, this is equivalent to extracting a single strip from the motion video $I_{t}[i], i \in [\frac{H}{4}, \frac{3H}{4}]$, or equivalently $I_{t}[:, j], j \in [\frac{W}{4}, \frac{3W}{4}]$ (why are the two equivalent?), where this strip would correspond to a shifted rectangular pulse for each frame within the video. 

We can use the following code (should look familiar by now) to show what 1D-integrated images corresponding to different shifts would look like
```python
import torch
import matplotlib.pyplot as plt 

def integrate_mean_by_roll(x: torch.Tensor, N: int, tau: int) -> torch.Tensor:
    """
    Build T frames by successively rolling x by j*tau (j=0..T-1),
    then return the mean over frames (weighted=False).
    NOTE: tau is integer; torch.roll is integer-shifted, circular.
    """
    L = x.numel()
    acc = torch.zeros_like(x)
    for j in range(N):
        acc += torch.roll(x, shifts=(j * tau) % L, dims=0)
    return acc / N

# Signal: rectangular pulse (Heaviside window)
M = 256
width = M//8 + 1
x = torch.zeros(M)
lower = M//2 - width//2
upper = M//2 + width//2 
bounds = slice(lower, upper)
x[bounds] = 1.0

# Choose N (often tied to width / number of frames)
N = width

# ---- Compute integrated signals for each tau ----
taus = [1, 2, 3]
integrated = {tau: integrate_mean_by_roll(x, N, tau) for tau in taus}

# ---- Plot ----
plt.figure(figsize=(10, 5))
idx = torch.arange(M) - M//2
plot_bounds = slice(lower - width//2, len(idx)) 
for tau in taus:
    plt.plot(idx[plot_bounds], integrated[tau].numpy()[plot_bounds], 
                     label=fr"$\tau = {tau}$")

# (Optional) show original signal for reference (light dashed)
plt.plot(idx[plot_bounds], x.numpy()[plot_bounds], '--', alpha=0.4, label="original x")

plt.xlabel("Index")
plt.ylabel("Integrated mean value")
plt.title(f"Mean of N={N} shifted signals for different shift values τ")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("integrated_sigs.png")
plt.show()
``` 
![Integrated 1D](/assets/integrated_sigs.png)  



