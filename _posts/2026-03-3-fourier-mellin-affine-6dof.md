---
title: "Beyond Similarity: Anisotropic Refinement for Affine Registration"
layout: post
date: 2026-03-03 18:00
headerImage: false
tags: [Computer Science, Math, Optimization]
star: true
category: blog
author: Ido Akov
description: "Extending Fourier–Mellin registration toward 6-DoF affine alignment via a lightweight anisotropic scale refinement step."
---

Most classical image registration pipelines stop at **similarity transforms**: translation, rotation, and a single isotropic scale factor. That's 4 degrees of freedom, and it covers a surprisingly wide range of scenarios. But real-world deformations often include **anisotropic scaling** or shear — think a camera with a slightly non-square sensor, or a medical image stretched along one axis — and those require a full **6-DoF affine model**.

This post works out a simple extension: keep Fourier–Mellin (FM) for the similarity part, which is fast and well-understood, and add a lightweight refinement step that estimates the remaining anisotropic stretch from the residual in log-polar space.

---

## The linear component

Translation can be handled separately via phase correlation, so we focus on the **linear component** $A$ of the affine map between a reference image $I_{\mathrm{ref}}$ and a moving image $I_{\mathrm{mov}}$:

<div>
$$
x \mapsto A x, \qquad A \in \mathrm{GL}(2).
$$
</div>

### Polar decomposition

Any invertible linear map factors uniquely into a rotation followed by a symmetric stretch. Writing this polar decomposition:

<div>
$$
A = R\,P, \qquad R \in \mathrm{SO}(2),\quad P \succ 0
$$
</div>

where $R$ is a rotation and $P$ is a symmetric positive-definite stretch matrix. The stretch itself has an eigen-decomposition:

<div>
$$
P = Q\,\mathrm{diag}(\lambda_1,\lambda_2)\,Q^\top, \qquad \lambda_1 \ge \lambda_2 > 0.
$$
</div>

The degree of anisotropy is captured by the condition number $\kappa = \lambda_1 / \lambda_2$. When $\kappa = 1$ the stretch is isotropic; larger $\kappa$ means more directional distortion.

---

## Isotropic–anisotropic parameterization

To separate what FM can already handle (isotropic scale) from what it cannot, we factor the stretch as:

<div>
$$
P = \lambda_{\mathrm{iso}}\,S_{\mathrm{ani}}(\delta,\phi)
$$
</div>

where the anisotropic component is:

<div>
$$
S_{\mathrm{ani}}(\delta,\phi) = R(\phi)\,\mathrm{diag}(e^\delta, e^{-\delta})\,R(-\phi).
$$
</div>

Matching eigenvalues gives $\lambda_1 = \lambda_{\mathrm{iso}} e^\delta$ and $\lambda_2 = \lambda_{\mathrm{iso}} e^{-\delta}$, from which:

<div>
$$
\lambda_{\mathrm{iso}} = \sqrt{\lambda_1 \lambda_2}, \qquad \delta = \tfrac{1}{2}\log\frac{\lambda_1}{\lambda_2}.
$$
</div>

Isotropic stretch is the special case $\delta = 0$. The parameter $\delta$ measures the log-ratio of the two scales, and $\phi$ gives the principal axis direction.

---

## Baseline: Fourier–Mellin

The classical FM pipeline estimates similarity transforms in three steps:

1. Compute the Fourier magnitude spectrum (this removes translation, since the spectrum is shift-invariant).
2. Map to log-polar coordinates (this converts rotation and isotropic scale to translations).
3. Use phase correlation to recover both rotation and isotropic scale.

After applying the similarity correction we obtain $I_{\mathrm{cur}}$, which may still contain anisotropic stretch — the part FM cannot see.

---

## Log-polar view of anisotropy

Here is the key geometric insight. Let $u(\alpha) = (\cos\alpha, \sin\alpha)$ be the unit vector at angle $\alpha$. The anisotropic stretch scales this direction by:

<div>
$$
g(\alpha) = \|S_{\mathrm{ani}}(\delta,\phi)\,u(\alpha)\|
$$
</div>

which works out to:

<div>
$$
g^2(\alpha) = e^{2\delta}\cos^2(\alpha-\phi) + e^{-2\delta}\sin^2(\alpha-\phi).
$$
</div>

In log-polar coordinates, a radial scale multiplier becomes an additive shift: $\rho = \log r \mapsto \rho + \log g$. So the anisotropic distortion produces an **angle-dependent radial shift**:

<div>
$$
s(\alpha) = \log g(\alpha).
$$
</div>

Instead of one global shift (what FM measures), we now have a shift *curve* indexed by angle — and that curve contains the anisotropy signal.

---

## Small-anisotropy approximation

For small $\lvert \delta \rvert$, using $e^{\pm 2\delta} \approx 1 \pm 2\delta$, the shift curve simplifies to:

<div>
$$
s(\alpha) \approx \delta \cos(2(\alpha - \phi)).
$$
</div>

Anisotropy appears as a **second harmonic sinusoid** in the angular shift profile. This is a clean structure: it has only two free parameters ($\delta$ and $\phi$) and can be recovered by a simple harmonic fit.

---

## Estimating the shift curve

Working in the log-polar Fourier magnitude $M(\alpha, \rho) = \mathcal{L}(\lvert \mathcal{F}(I)\rvert)$, the anisotropic distortion produces:

<div>
$$
M_{\mathrm{cur}}(\alpha, \rho) \approx M_{\mathrm{ref}}(\alpha, \rho - s(\alpha)).
$$
</div>

For each angular bin we estimate the radial shift using **1-D phase correlation**, yielding a shift sample per bin:

<div>
$$
\hat{\mathbf{s}} = [\hat{s}_0, \ldots, \hat{s}_{H_\alpha - 1}].
$$
</div>

---

## Recovering anisotropy

We fit the second harmonic model to the estimated shift samples:

<div>
$$
\hat{s}(\alpha) = a_0 + a_c \cos(2\alpha) + a_s \sin(2\alpha).
$$
</div>

The amplitude and phase of the fitted sinusoid give the anisotropy parameters directly:

<div>
$$
A = \sqrt{a_c^2 + a_s^2}, \qquad \phi = \tfrac{1}{2}\operatorname{atan2}(a_s, a_c).
$$
</div>

The anisotropy magnitude then follows as:

<div>
$$
\delta \approx A \log b
$$
</div>

where $b$ is the log-polar radial base. The whole recovery is a linear least-squares problem — cheap and stable.

---

## Refinement loop

The full algorithm alternates between similarity removal and anisotropy estimation:

1. **FM step** — estimate isotropic scale and rotation via log-polar phase correlation.
2. **Anisotropy estimation** — measure per-angle radial shifts and fit the harmonic model.
3. **Resolve discrete ambiguities** — evaluate candidates $(\pm\delta, \phi)$ and $(\pm\delta, \phi + \pi/2)$ and keep the best alignment score.
4. **Accumulate and iterate.**

Only a few outer iterations are needed — the similarity step accounts for the bulk of the deformation, and the anisotropy refinement converges quickly in the residual.

---

## Experiment

We evaluate on **5,000 affNIST image pairs** with known ground-truth affine parameters.

![affNIST dataset](/assets/images/affnist_transforms.png)

The table below compares recovered singular values with and without anisotropic refinement (2 steps):

| Metric | Baseline (FM) | Refined ($\delta, \phi$) | Change |
|---|---:|---:|---:|
| MAE($\lambda_1$)  | 0.094 | 0.077 | **−18.1%** |
| MAE($\lambda_2$)  | 0.092 | 0.063 | **−31.5%** |
| RMSE($\lambda_1$) | 0.121 | 0.111 | **−8.3%** |
| RMSE($\lambda_2$) | 0.117 | 0.090 | **−23.1%** |

The refinement consistently improves recovery of both singular values, with the largest gains for the smaller eigenvalue $\lambda_2$ — the one that FM underestimates most.

The anisotropy estimate itself remains the hardest part. The recovered $\delta$ reaches only $\sim 0.3$ correlation with ground truth, and systematically underestimates deformation magnitude:

<div>
$$
\mathbb{E}[\hat{\delta}] = 0.04, \qquad \mathbb{E}[\delta_{\mathrm{gt}}] = 0.09.
$$
</div>

The refinement improves the *effect* of anisotropy (better recovered scales) even when it underestimates its *magnitude*.

---

## Parameter distributions

![Distribution comparison](/assets/images/02_distributions.png)

The isotropic scale estimates show mild quantization — a consequence of discretizing the log-radius axis in FM. Each bin corresponds to a fixed multiplicative scale step, which produces slight clustering in the recovered scale distribution.

The anisotropic estimates show a strong bias toward smaller values. Because the harmonic fit is noisy and phase correlation is only approximate at the per-bin level, the estimated $\delta$ is systematically pulled toward zero. This causes the recovered singular values to cluster near the isotropic scale rather than spanning their true range.

---

## Final thoughts

Fourier–Mellin registration handles similarity well, and this experiment shows it can be nudged toward affine alignment with a modest extra step. The anisotropy refinement is cheap (a per-angle 1-D phase correlation plus a harmonic fit), interpretable (second harmonic → two parameters), and consistently improves the recovered scales even in its current noisy form.

The method works best as a **fast initialization** for full affine registration, or as a **cheap refinement layer** on top of similarity alignment when full affine optimization is overkill. More broadly, it highlights how much mileage careful geometric modeling can extract from classical frequency-domain tools.
