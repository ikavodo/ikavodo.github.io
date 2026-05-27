---
title: "Motion Under Occlusion, pt.5: The Occlusion Bias"
layout: post
date: 2025-12-10 18:00
image: 
headerImage: false
tags:
- Computer Science
- Math
- Optimization
star: true
hidden: true
category: blog
author: Ido Akov
description: "Deriving the two-term Fourier structure under static occlusion, and comparing the Fourier and spatial objectives empirically under controlled occlusion density."
---
The [previous four posts](https://ikavodo.github.io/optimization_pt-4/) were all about 2DoF translation. This post adds the piece that was missing from pt.4: a static occlusion model. We show how it biases the Fourier objective toward zero motion, and compare the Fourier and spatial objectives empirically under controlled occlusion density.

---
## Static occlusion and the zero-motion bias

In [pt.4](https://ikavodo.github.io/optimization_pt-4/) we saw that applying the moving-average integration in the presence of a static component splits the Fourier result into two competing terms. The same structure appears in 2D with fragmented occlusion.

Model each frame as a moving target with a static occluder layered on top:

<div>
$$
I_t = W^t(I_{\mathrm{mov}},\,\theta^*) + I_{\mathrm{occ}}
$$
</div>

where $I_{\mathrm{mov}}$ is the target appearance, $I_{\mathrm{occ}}$ the static occluder, and $\theta^*$ the true motion. By the Fourier shift theorem and linearity, the integrated image becomes

<div>
$$
\mathcal{F} \{\overline{I}(\theta)\} = H(\Delta\phi) \cdot \mathcal{F}\{I_{\mathrm{mov}}\} + H(\phi) \cdot \mathcal{F}\{I_{\mathrm{occ}}\}
$$
</div>

where $H$ is the moving-average filter from [pt.2](https://ikavodo.github.io/optimization_pt-2/), $\phi(\theta)$ is the phase parameter, and $\Delta\phi = \phi(\theta) - \phi(\theta^*)$ is the phase error. The variance objective therefore becomes

<div>
$$
f_{\mathrm{opt}}(\theta) \overset{\text{DFT}}{\leftrightarrow} \sum_{(m,n)\neq(0,0)} |H(\Delta\phi) \cdot \mathcal{F}\{I_{\mathrm{mov}}\} + H(\phi) \cdot \mathcal{F}\{I_{\mathrm{occ}}\}|^2
$$
</div>

The first term is maximized when $\Delta\phi = 0$, i.e., at the true motion $\theta = \theta^*$, where $H(0) = 1$. The second is maximized when $\phi = 0$, i.e., at *zero* motion. These two compete directly, and as occlusion density grows the zero-motion bias wins.

Note that $H$ is a moving-average filter of order $T$, which attenuates the occluder contribution by approximately $\sqrt{T}$. So integrating more frames weakens the bias — but for finite $T$ the competition is real.

In the frequency domain, the two competing terms are visible explicitly, unlike in the spatial domain where occlusion simply "hurts" without giving insight. The occluder term is anchored at $\theta = 0$, while the moving target term peaks at the true motion $\theta^*$. The variance objective is therefore a balance between these two contributions.

---

## Experiment: Fourier vs. spatial under occlusion

Setup: $T=8$ frames, $128\times128$ images, Adam at learning rate $0.1$, 200 iterations, EPE threshold $\|\hat{\tau} - \tau^*\|_2 < 0.5$, occlusion density swept from 0 to ~80%.

The Fourier objective matches the spatial baseline in success rate across all occlusion densities. At low-to-mid densities it reaches the EPE threshold in fewer iterations, and its time-to-threshold profile is flatter — it converges more consistently rather than just faster on average. At higher densities both methods fail: the zero-motion bias in the occlusion term overwhelms the moving-object term regardless of domain.

---

The Fourier formulation makes the occlusion problem legible: instead of just "hurts at high density", you can read off exactly why and at what rate. The next post extends this to similarity motion — where the challenge turns out to be structural even before occlusion enters.

Until then!
