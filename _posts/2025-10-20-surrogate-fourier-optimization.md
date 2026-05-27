---
title: "Surrogate Fourier Optimization via Wirtinger Derivatives"
layout: post
date: 2025-10-20 17:00
headerImage: false
tags:
- Computer Science
- Math
- Optimization
star: true
category: blog
author: Ido Akov
description: "Replacing a non-convex Fourier objective with a differentiable surrogate using Wirtinger calculus."
---

## **Motivation**
I’m currently working on expanding an optimization pipeline over **2D parametric motion (translation)** to **more general motion models** such as **Affine 6DoF**.

In Fourier-based approaches, **4DoF motion estimation** (translation + rotation + scale) is well-known through algorithms like the **Fourier–Mellin Transform** (see [the following](https://sthoduka.github.io/imreg_fmt/docs/log-polar-transform/)).  
Since my existing spatial-domain objective — based on **variance of the integrated image from multiple shifted frames** — is entirely linear, I sought to translate it into the **Fourier domain**.

However, I encountered a problem:  
> The Fourier-domain objective is **non-convex**, and its gradients do not correspond directly to those of the spatial-domain version.

That led me to the paper:
  
> [**“Sinusoidal Frequency Estimation by Gradient Descent”**, IEEE 2023](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10095188&tag=1)

It proposes a **surrogate formulation** that allows stable optimization of oscillatory Fourier objectives using **Wirtinger derivatives**.

I decided to test whether I could apply this idea to my own Fourier objective.

---

## **Formulation**
To simplify analysis, I reduced the problem to **1D** with a simple analytical function — a **Heaviside (rectangular) pulse** — and a single translation parameter **$\tau$**.

This setting lets us understand the structure of the optimization landscape analytically and visually before extending to the full 2D image case.

---

## **Objective Analysis**

### 1️⃣ Integration
Our spatial integration operation is:


$I(\tau) = \frac{1}{N}\sum_{n=0}^{N-1}x(t - n\tau)$


This can be viewed as a **generalized convolution**: convolution of $x(t)$ with a comb-like kernel


$h(t) = \frac{1}{N}\sum_{n=0}^{N-1}\delta(t - n\tau)$


so that $$I(\tau) = (x * h)(t)$$.

➡️ For integer $$\tau=1$$, this operation becomes a discrete convolution of the signal with itself.  
If $$x\)$ is a **rectangular pulse** of width $\(W\)$ and $\(N=W\)$, then $\(I(t)\)$ is a **triangular function** — the self-convolution of $\(x$$.

```python
# Example: integration via torch.roll
taus = [-2, -1, 0, 1, 2]
integrated = {tau: integrate_mean_by_roll(x, N, tau) for tau in taus}

plt.figure(figsize=(10, 5))
idx = np.arange(M)
for tau in taus:
    plt.plot(idx, integrated[tau].numpy(), label=fr"$\tau={tau}$")
plt.legend(); plt.grid(True)
plt.title("Mean of N shifted signals for various τ")
```
---

### 2️⃣ Fourier Domain Formulation
Taking the Fourier transform of the geometric sum gives:

\[
\sum_{n=0}^{N-1}e^{-j\omega n\tau} = \frac{1 - e^{-j\omega N\tau}}{1 - e^{-j\omega \tau}}
\]

This is the **Dirichlet kernel**, a comb filter that selectively amplifies frequencies coherent with the shift lattice.  
Thus, the Fourier-domain integration acts as **banded filtering** on $X(\omega)$.

---

### 3️⃣ Variance Objective
Variance of the integrated image is equivalent to its **power spectral density minus DC power**:

\[
\mathrm{Var}(x) = \int |X(\omega)|^2 d\omega - |X(0)|^2
\]

This gives intuitive insight:  
- The **maximum variance** occurs at **zero shift ($\tau = 0$)**,  
- Larger shifts correspond to **comb-filtered spectra** where destructive interference reduces total power.

---

## **Naive Optimization**
We first implement an **autodifferentiable 1D version** of the Fourier integration:

```python
class PhaseShiftAutoDiff1D:
    def __init__(self, base_alpha=0.5, eps=1e-12):
        self.base_alpha = base_alpha
        self.eps = eps

    def forward(self, x: torch.Tensor, T: int, tau: torch.Tensor,
                weighted=False, fourier_input=False):
        ...
```
Then, we run optimization from several starting deltas:

```python
starts = [-1.5, -0.8, -0.2, 0.3, 0.9]
results = [model.optimize(x, T, delta0=s, weighted=False) for s in starts]
```

Plotting the optimization trajectories:

```python
plot_result_field(results, field="deltas", starts=starts,
                  ylabel="delta (value on y-axis)",
                  title="Delta trajectories during optimization",
                  hline0=True)
```

**Result:**  
The optimization fails to converge to a single minimum —  
the objective is **highly oscillatory and non-convex** in the Fourier domain.

---

## **Surrogate Objective**
To address this, we build a **surrogate complex objective**, inspired by the IEEE paper above.

The surrogate replaces the oscillatory exponential with a **complex polynomial form**, maintaining differentiability while smoothing oscillations.

### Example from the paper
The surrogate is defined as:

\[
s_n(z_k) = \Re(z_k^n)
\]
where $z_k = e^{j\omega_k}$.

This can be interpreted as the **real part of an exponentially decaying sinusoid** —  
a differentiable approximation to a pure sinusoidal phase shift.

---

### **Wirtinger Derivatives (optional derivation)**
For a function $f:\mathbb{C}\rightarrow \mathbb{R}$:

\[
\frac{\partial f}{\partial z} = \frac{1}{2}\left(\frac{\partial f}{\partial x} - j\frac{\partial f}{\partial y}\right), \quad
\frac{\partial f}{\partial \bar{z}} = \frac{1}{2}\left(\frac{\partial f}{\partial x} + j\frac{\partial f}{\partial y}\right)
\]

This basis change from $(x,y)\) to \((z,\bar{z})\) allows us to **treat \(z\) and \(\bar{z}$ as independent variables**, enabling gradient-based optimization over complex-valued functions that aren’t holomorphic.

---

## **Definition of Surrogate Optimization Objective**
We decompose the geometric sum as:

\[
F(z) = \frac{1 - z^N}{1 - z} = F_{\text{re}}(z)\,F_{\text{im}}(z)
\]

and derive analytic gradients for both $F_{\text{re}}\) and \(F_{\text{im}}$ using Wirtinger calculus.

For the **weighted case**, we include:

\[
r = (1 - \alpha)e^{-j\delta \omega}, \quad F(z) = \frac{1 - r^N}{1 - r}
\]
and normalize by:

\[
\text{α-sum} = 1 - (1 - \alpha)^N
\]

so that gradients respect geometric weighting.

---

### Analytic gradient (weighted and unweighted)
```python
def dF_dz(z, N, base_alpha=None, weighted=False, eps=1e-8):
    one = torch.ones_like(z)
    if weighted and base_alpha is not None:
        r = (1 - base_alpha) * z
        num = one - N * r**(N - 1) + (N - 1) * r**N
        den = (one - r)**2
        dFdz = num / den
    else:
        num = one - N * z**(N - 1) + (N - 1) * z**N
        den = (one - z)**2
        dFdz = num / den
    mask = (den.abs() < eps)
    if mask.any():
        dFdz = torch.where(mask, torch.as_tensor(N*(N-1)/2, dtype=z.dtype, device=z.device), dFdz)
    return dFdz
```

---

### Weighted optimization
```python
opt_analytic_weighted = PhaseShiftOptimizer(obj, weighted=True, ascent=True)
results_weighted = [opt_analytic_weighted.optimize(tau0=s, steps=200, alpha=0.5) for s in starts]
```

**Observation:**  
With weighting, the geometric decay stabilizes the gradient field, producing smooth, monotonic convergence to the correct translation parameter $\tau = 0$.

---

## **Optimization Over Surrogate Objective**
Using the same starting deltas, the surrogate-based optimization converges consistently across initializations, unlike the raw Fourier case.

```python
plot_result_field(results_weighted, field="deltas", starts=starts,
                  ylabel="tau (value on y-axis)",
                  title="Delta trajectories (weighted surrogate)",
                  hline0=True)
```

---

## **Summary**
We began with a **spatial-domain motion optimization** based on variance maximization,  
translated it into the **Fourier domain**,  
and found the direct formulation to be **non-convex** and unsuitable for gradient-based learning.

By introducing a **surrogate complex polynomial objective**, inspired by sinusoidal estimation methods,  
we derived smooth, analytically tractable **Wirtinger gradients** and achieved stable convergence in the 1D case.

This framework generalizes naturally to **2D motion** (translations), and potentially to **affine 6DoF motion** models — providing a unified way to perform differentiable motion estimation in the Fourier domain.

---

**References**
1. Szurley, J. & Raczynski, C. *“Sinusoidal Frequency Estimation by Gradient Descent”*, IEEE 2023.  
   [https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10095188](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10095188)
2. Papoulis, A. *The Fourier Integral and Its Applications*.
3. Mallat, S. *A Wavelet Tour of Signal Processing*.

---

📄 **Next steps:**
- Extend to 2D Fourier motion fields.
- Replace $\tau$ with affine parameters.
- Explore differentiable implementation of the surrogate kernel in PyTorch for real-time motion optimization.
