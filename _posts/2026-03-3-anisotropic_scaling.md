---
title: "From 4→6DoF: anisotropic scale refinement via log-polar phase correlation"
layout: post
date: 2026-03-03 18:00
headerImage: false
tags: [Computer Science, Math, Optimization]
star: true
category: blog
author: Ido Akov
description: "Optimization"
---

# Anisotropic Scale Refinement via Log-Polar Phase Correlation

Goal: refine a similarity-aligned pair of images by estimating the **residual anisotropic scaling** (magnitude + axis) using a lightweight log-polar procedure.

---

## 1. Setup: factor translation, then model the linear part

Let $I_{\mathrm{ref}}$ be a reference image and $I_{\mathrm{mov}}$ a moving image related by a planar transform. Translation is handled separately (standard phase correlation), so we focus on the **linear** part:
$$
x \mapsto A x,\quad A\in \mathrm{GL}(2).
$$

### 1.1 Use Polar Decomposition

Write the **polar decomposition**
$$
A = R\,P,
\quad R\in \mathrm{SO}(2),\quad P\succ 0\ \text{(SPD)}.
$$
- $R$: rotation (orientation change)
- $P$: pure stretch (where anisotropic scale lives)

Since $P$ is SPD, it has an eigen-decomposition
$$
P = Q\,\mathrm{diag}(\lambda_1,\lambda_2)\,Q^\top,\quad Q\in \mathrm{SO}(2),\ \lambda_1\ge \lambda_2>0.
$$

So anisotropic scaling is $\kappa = \frac{\lambda_1}{\lambda_2} \gt 1$.

### 1.2 Isotropic–anisotropic parameterization
#### Explicit recovery of $\lambda_{\mathrm{iso}}$ and $\delta$

Assume the stretch part $P\succ 0$ (from the polar decomposition $A=RP$) has eigen-decomposition
$$
P = R(\phi)\,\mathrm{diag}(\lambda_1,\lambda_2)\,R(-\phi),
\qquad \lambda_1\ge \lambda_2>0.
$$

We want to factor $P$ into an isotropic scale and a unit-determinant anisotropic residual:
$$
P = \lambda_{\mathrm{iso}}\, S_{\mathrm{aniso}}(\delta,\phi),
\qquad
S_{\mathrm{aniso}}(\delta,\phi)=R(\phi)\,\mathrm{diag}(e^\delta,e^{-\delta})\,R(-\phi).
$$

Match eigenvalues on both sides. Since $R(\phi)$ is the same eigenbasis,
$$
\lambda_1 = \lambda_{\mathrm{iso}} e^\delta,\qquad
\lambda_2 = \lambda_{\mathrm{iso}} e^{-\delta}.
$$

Now solve explicitly:

1) Multiply the two equations:
$$
\lambda_1\lambda_2 = \lambda_{\mathrm{iso}}^2 e^\delta e^{-\delta}=\lambda_{\mathrm{iso}}^2
\quad\Rightarrow\quad
\boxed{\ \lambda_{\mathrm{iso}}=\sqrt{\lambda_1\lambda_2}\ }.
$$

2) Divide the two equations:
$$
\frac{\lambda_1}{\lambda_2}=\frac{\lambda_{\mathrm{iso}}e^\delta}{\lambda_{\mathrm{iso}}e^{-\delta}}=e^{2\delta}
\quad\Rightarrow\quad
\boxed{\ \delta=\tfrac12\log\!\left(\frac{\lambda_1}{\lambda_2}\right)\ }.
$$

Equivalently, using the determinant and condition number:
$$
\lambda_{\mathrm{iso}}=\sqrt{\det(P)},\qquad
\delta=\tfrac12\log \kappa(P),\quad \kappa(P)=\frac{\lambda_1}{\lambda_2}.
$$

Finally, the residual stretch is exactly the normalized stretch:
$$
\boxed{\ S_{\mathrm{aniso}}(\delta,\phi)=\frac{1}{\lambda_{\mathrm{iso}}}P\ },
$$
since dividing $P$ by $\lambda_{\mathrm{iso}}$ rescales its eigenvalues to $(e^\delta,e^{-\delta})$ and enforces $\det(S_{\mathrm{aniso}})=1$.

---

## 2. Baseline: Fourier–Mellin (FM) gives similarity alignment

FM estimates rotation + isotropic scale (and translation via phase correlation):
- take Fourier magnitude (removes translation),
- map to log-polar coordinates $(\alpha,\rho)$ with $\rho=\log r$,
- phase correlation gives shifts in $\alpha$ (rotation) and $\rho$ (isotropic scale).

After applying the FM similarity correction, we obtain $I_{\mathrm{cur}}$: aligned for rotation + isotropic scale, but possibly still anisotropically distorted.

What remains is dominated by $S_{aniso}(\delta,\phi)$.

---

## 3. Key geometric fact: anisotropy becomes an angle-dependent radial shift in log-polar

### 3.1 Directional gain of the residual stretch

Let $u(\alpha)=(\cos\alpha,\sin\alpha)$. Under the residual stretch,
$$
g^2(\alpha) = \|S_{aniso}(\delta,\phi)u(\alpha)\|^2
= e^{2\delta}\cos^2(\alpha-\phi)+e^{-2\delta}\sin^2(\alpha-\phi).
$$
This is the directional frequency scaling after similarity alignment.

### 3.2 Convert to log-polar “radial shift”

In log-polar, a scale factor $s$ in radius means an additive shift $\log s$ in $\rho$. Therefore define
$$
s(\alpha) :=\tfrac12\log\!\Big(\|S_{aniso}(\delta,\phi)u(\alpha)\|^2\Big)
=\frac12\log\!\Big(e^{2\delta}\cos^2 t + e^{-2\delta}\sin^2 t\Big),
\quad t:=\alpha-\phi.
$$

This is the exact relationship:
- isotropic scale → constant shift in $\rho$
- anisotropy → shift that depends on angle $\alpha$

---
## 4. Approximation in $\delta$ of per-angle log-polar shift

### 4.1 Why linearize in $\delta$?

In the log-polar magnitude, anisotropy produces an angle-dependent radial shift
$$
s(\alpha)=\frac12\log\!\Big(e^{2\delta}\cos^2 t + e^{-2\delta}\sin^2 t\Big),\quad t=\alpha-\phi.
$$
If $\|\delta\|$ is small, then:
- exponentials can be expanded as $e^{\pm 2\delta}\approx 1\pm 2\delta$,
- and the log can be linearized via $\log(1+x)\approx x$.

Empirically (e.g., in affNIST-style warps), $\|\delta\|$ stays in a range where the second harmonic dominates and higher harmonics/bias terms are comparatively weak (see bound below).

Use small-$\delta$ expansions:
$$
e^{\pm 2\delta}\approx 1\pm 2\delta.
$$
Then
$$
g^2(\alpha) = e^{2\delta}\cos^2 t + e^{-2\delta}\sin^2 t \approx 1+2\delta(\cos^2 t-\sin^2 t)=1+2\delta\cos(2t).
$$
For small $x$, $\log(1+x)\approx x$, hence
$$
s(\alpha)=\tfrac12\log(g^2(\alpha))
\approx \tfrac12\cdot 2\delta\cos(2t)
=\delta\cos(2(\alpha-\phi)).
$$

**Takeaway:** the anisotropy-induced log-radial shift is (approximately) a **second-harmonic sinusoid** in angle.

### 4.3 affNIST ranges ⇒ $\delta$ is bounded (so first-order is reasonable)

affNIST samples independent horizontal/vertical expansions
$$
h,v \sim \text{Unif}[0.8,1.2],
$$
and a shear parameter
$$
s \sim \text{Unif}[-0.2,0.2],
\qquad
H(s)=\begin{pmatrix}1&0\\ s&1\end{pmatrix},
\qquad
D(h,v)=\mathrm{diag}(h,v).
$$

Using submultiplicativity $\kappa_2(AB)\le \kappa_2(A)\kappa_2(B)$ and the fact that rotations have $\kappa_2(R)=1$, it suffices to bound $\kappa_2(H(s)D(h,v))$.

**Axis scales:** Since $D$ is diagonal,
$$
\kappa_2(D)=\frac{\max(h,v)}{\min(h,v)}\le \frac{1.2}{0.8}=1.5.
$$

**Shear:** (skipping some calculations) $\|s\|=0.2 \implies \kappa_2(H)\approx 1.221$.

**Combined bound.** Hence

$$
\kappa_2(H(s)D(h,v))
\le \kappa_2(H(s))\kappa_2(D(h,v))
\le 1.221\times 1.5 \approx 1.83,
$$

and thus
$$
\|\delta\|\le \tfrac12\log(1.83)\approx 0.303.
$$

**Interpretation.** Under affNIST parameter ranges, a conservative worst-case bound is $\|\delta\|\lesssim 0.30$. At $\delta=0.3$, the neglected $O(\delta^2)$ terms are not tiny: $\delta^2/2=0.045$. This motivates more refined approximation via quadratic correction terms.

### 4.4 Second-order (quadratic) approximation: bias + $\cos(4t)$ leakage

Start from the exact directional gain
$$
g^2(t)=e^{2\delta}\cos^2 t + e^{-2\delta}\sin^2 t,
\qquad
s(t)=\tfrac12\log g^2(t).
$$

Expand exponentials to second order:
$$
e^{2\delta}\approx 1+2\delta+2\delta^2,\qquad
e^{-2\delta}\approx 1-2\delta+2\delta^2,
$$
giving
$$
g^2(t)\approx 1 + 2\delta\cos(2t) + 2\delta^2.
$$

Now expand the log to second order using $\log(1+x)\approx x-\tfrac{x^2}{2}$ with
$x=2\delta\cos(2t)+2\delta^2$:
$$
\begin{aligned}
s(t)
&\approx \tfrac12\Big(x-\tfrac{x^2}{2}\Big)
= \delta\cos(2t)+\delta^2-\delta^2\cos^2(2t)\\
&= \delta\cos(2t)+\frac{\delta^2}{2}-\frac{\delta^2}{2}\cos(4t).
\end{aligned}
$$

So the **quadratic model** is
$$
\boxed{
s_2(\alpha)\approx
\delta\cos(2(\alpha-\phi))+\frac{\delta^2}{2}-\frac{\delta^2}{2}\cos(4(\alpha-\phi)).
}
$$

**What it adds beyond first order.**
- A **DC bias** term $\delta^2/2$ (shifts all radii slightly).
- A small **fourth-harmonic** term with amplitude $\delta^2/2$.

Let's validate the improvement numerically at $\delta=0.3, \quad t\in[0,\pi), \quad t=\alpha-\phi$:
- first-order $s_1(t)$:  
  $\max|s_1-s|\approx 0.088$, RMS $\approx 0.054$, mean error $\approx -0.044$.
- second-order $s_2(t)$:  
  $\max|s_2-s|\approx 0.0135$, RMS $\approx 0.0088$, mean error $\approx 6.6\times 10^{-4}$.

---

## 5. Estimating $s(\alpha)$ from data: per-angle 1D phase correlation

We work in the log-polar Fourier magnitude domain:
$$
M(\alpha,\rho) := \mathcal{L}\big(|\mathcal{F}(I)|\big).
$$

After similarity correction, anisotropy manifests as:
$$
M_{\mathrm{cur}}(\alpha,\rho)\approx M_{\mathrm{ref}}(\alpha,\rho - s(\alpha)).
$$

So for each discrete angle bin $\alpha_i$, treat the $\rho$-profile as a 1D signal:
$$
m_{\mathrm{ref},i}(\rho) := M_{\mathrm{ref}}(\alpha_i,\rho),\quad
m_{\mathrm{cur},i}(\rho) := M_{\mathrm{cur}}(\alpha_i,\rho).
$$

Then estimate the shift $\widehat{s}_i$ by **1D phase correlation** along $\rho$:
- compute cross-power spectrum of the 1D FFTs,
- inverse FFT → correlation peak,
- peak location → shift in $\rho$ bins.
Result: a vector of shifts
$$
\{\hat{s}_i\}_{i=0}^{H_\alpha-1},
$$
which samples $s(\alpha)$.
---

## 6. Fit the second harmonic and recover $\phi$ and $\delta$

Fit
$$\hat{s}(\alpha)\approx a_0 + a_c\cos(2\alpha)+a_s\sin(2\alpha).
$$

Then equivalently
$$
\widehat{s}(\alpha)\approx a_0 + A\cos(2(\alpha-\phi)),
$$
with
$$
A=\sqrt{a_c^2+a_s^2},\quad
\phi=\tfrac12\operatorname{atan2}(a_s,a_c).
$$

If one $\rho$-bin equals $\Delta\rho=\log(b)$ (natural log units), then:
$$
\text{log-shift} \approx \widehat{s}(\alpha)\,\Delta\rho.
$$
Under the first-order model $s(\alpha)\approx \delta\cos(2(\alpha-\phi))$, the amplitude maps as:
$$
\boxed{\ \delta \approx A\,\Delta\rho = A\log(b)\ }.
$$

---

## 7. Practical refinement loop (similarity ↔ anisotropy)

Repeat a small number of iterations:

1. **FM similarity step**  
   Estimate 
   $$
   (\widehat{\lambda}_{\mathrm{iso}},\widehat{\theta})$$ 
   and translation; warp $I_{\mathrm{mov}}\to I_{\mathrm{cur}}$.

2. **Anisotropy estimation step**  
   In log-polar Fourier magnitude:
   - run 1D phase correlation along $\rho$ for each $\alpha_i$,
   - fit the second harmonic → $(\widehat{\delta},\widehat{\phi})$.

3. **Discrete ambiguity / robustness step (peak scoring)**  
   Because correlation and log-polar discretization can induce wrap/alias ambiguities, score a *small set* of candidate anisotropy updates (e.g., $\pm\widehat{\delta}$, $\widehat{\phi}$ and $\widehat{\phi}+\pi/2$, plus possible $\rho$-wrap variants) by applying the candidate warp and measuring a spatial-domain correlation peak. Pick the best.

4. **Apply update and accumulate parameters**  
   Update the current warp with $S(\widehat{\delta},\widehat{\phi})$; continue.

---

## 8. Summary

- Model the linear part as $A=RP$ (polar decomposition): all anisotropic scale lives in SPD $P$.
- After FM, remaining distortion is well-approximated by $S_{aniso}(\delta,\phi)$.
- In log-polar Fourier magnitude, anisotropy becomes an **angle-dependent radial shift** $s(\alpha)$.
- For small/moderate anisotropy, $s(\alpha)$ is dominated by the **second harmonic** $\cos(2(\alpha-\phi))$.
- Estimate per-angle radial shifts via **1D phase correlation**, then fit the second harmonic to recover $(\delta,\phi)$.

(TBA: experimental section involving affNIST. Report error in $(\lambda_1,\lambda_2,\phi)$ vs FM-only, and show convergence over iterations.)
