---
title: "Motion computation via an unsupervised-learning approach (pt.1)"
layout: post
date: 2025-10-20 16:34
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

## Introduction
This new blog-post series is about how seemingly-distant fields (computer-vision, audio) and their underlying principles (deep-learning vs. DSP) come together, through my (and everyone's) favorite mathematical concept: the **Fourier Transform** (see [first](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/) [and second](https://ikavodo.github.io/fourier-transform-tutorial-pt-2/) blog-posts).
This first part will introduce a novel approach for computing motion in occluded videos, and build the foundation from which we will cross the threshold into the Fourier (complex) domain and its associated operators. We will do this step-by-step for responsible pedagogy on my part! First though, a little introduction about what/where/who.


### Motion computation and fragmented occlusion
For those who know: I (not so) recently started a PhD in computer vision in Vienna, and was immediately thrown into a niche problem not many people are currently focusing on: that of estimating the motion of objects in *occluded* scenarios. While there are various types of occlusion out there, I am mainly focusing on *fragmented occlusion*, whereby occluders potentially create individually unrecognisable *fragments* of an object (think of this [Magritte painting](https://www.moma.org/audio/playlist/180/2378), had he chosen less recognisable body-parts). 

For the case of motion computation under fragmented occlusion, think about describing this squirrel's movement (put some [death metal](https://www.youtube.com/watch?v=iKZ94I-oqgE&list=PLMUoA2MhTasdHBgTzqSInIzde4MqoQMOW&index=1) in the background instead of that annoying music). 
<iframe width="560" height="315" src="https://www.youtube.com/embed/kHcoWVrDUh4" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
More specifically, within the first 10 seconds of this video, in approximately how many frames (if any) can the squirrel be seen *in full*?

While general algorithms for motion computation have been in existence since the 1980's, these algorithms are usually built on underlying assumptions which don't really hold in occluded scenarios (to understand why- read more about the [brightness constancy assumption](https://www.cs.cmu.edu/~16385/s17/Slides/14.1_Brightness_Constancy.pdf)). Thus, a *different* set of computational tools is necessary for computing motion in the occluded case. I'll try to briefly present these tools, and get on to the more interesting stuff.

### Parametric motion models
Working in the occluded case demands a *simplified* motion, i.e. we begin with a global *parametric-motion model* assumption over *all* pixels in the image instead of assuming that local neighborhoods move coherently, with smooth variation in motion across the entire image. This motion depends on an initial number of parameters, which are used at each time-step to successively warp some initial frame, thus creating a *motion video*. 

The simplest such example is a *translation* model, equivalent to using one finger to move a widget across your mobile-phone desktop. Somewhat more elaborate motions can be modelled via rotation (3DoF = translation + rotation), similarity (4DoF: translation+rotation+scale), affine (6DoF- all previously mentioned + shear) motion models, and even projective (9DoF) where each of these transformations have different geometric *invariants*. for example: a *similarity* transformation preserves shape up to a scalar, whereas an affine motion model need not necessarily retain shape, but rather preserves parallel lines (a square may morph into a parallelogram), and the ratios of lengths of parallel line segments.

See this example for a synthetic 6DoF affine motion video featuring a moving soccerball-like object. Notice that it moves towards the bottom-right corner, rotating counter-clockwise and eventualy deforming into an elongated ellipsoid (shear is non-zero). 

<video width="128" height="128" controls>
  <source src="/assets/occ_motion.mp4" type="video/mp4">
</video>


### Motion computation via an unsupervised-learning objective

An effective algorithm for motion computation in occluded videos has been thought up by my PhD supervisor. So far it works well for computing 1D-horizontal (very simple) motion, as well as reconstructing hidden moving objects in heavily-occluded videos. Unfortunately, the algorithm as it is doesn't work so well in the *higher-dimensional* parametric motion model case. Here then is the algorithm (soon to be published in a paper)

**Inputs:**
- Video frames $ I_0, I_1, \dots, I_{T-1} $, where $ I_j $ is an image of dimensions $HxW$

**Output:**
- Optimal motion parameters $ \theta^\star $


#### Step 1 — Initialize
Initialize motion parameters:

<div>
$$
\theta = [\theta_1, \dots, \theta_K]^T
$$
</div>

for a $K$-dimensional parametric motion model.


#### Step 2 — Warp Frames
For each timestep $t = 0, \dots, T-1$:

1) Warp the frame $I_t$ using the current motion parameters:

<div>
$$
\overline{I_t} = W_t(I_t, \theta)
$$
</div>

2) The composite warp $W_t$ is defined as a composition of $t$ successive warps:

<div>
$$
W_t(I_t, \theta) =
\underbrace{W \circ W \circ \cdots \circ W}_{t \text{ times}}(I_t, \theta)
$$
</div>

3) Note: Depending on the motion model, the composition $W_t$ can often be simplified analytically (e.g., when motion transformations form a group).

#### Step 3 — Integrate Warped Frames
Integrate the warped frames into a single averaged image:

<div>
$$
\overline{I} = \frac{1}{T}\sum_{t=0}^{T-1} \overline{I_t}
$$
</div>

#### Step 4 — Compute Variance
Compute the variance of the integrated image:

<div>
$$
f_{\text{obj}}(I_0,\dots,I_{T-1}) = \mathrm{Var}(\overline{I})
$$
</div>

#### Step 5 — Optimize Motion Parameters
Define the optimization objective:

<div>
$$
\theta^\star =
\arg\max_{\theta}\;
f_{\text{obj}}(I_0,\dots,I_{T-1})
=
\arg\max_{\theta}\;
\mathrm{Var}\!\left(
\frac{1}{T}\sum_{t=0}^{T-1} W_t(I_t,\theta)
\right)
$$
</div>

Solve for $\theta^\star$ using a numerical optimization method (e.g., gradient ascent/descent), with backpropagation through the warp operator $W_t$, updating $\theta$ at each iteration.


#### Intuition
The ground-truth motion parameters $\theta^\star$ should yield an integrated image $\overline{I}$ with $maximal$ variance (meaning maximum image contrast). The reason why this algorithm works well in the case of fragmented occlusion is because occlusion is in essence "smoothed" out by the integration procedure, thus leaving only a sharp image of the object in motion, notwithstanding certain assumptions about object visibility across all frames, static occluders, etc... In the next blog-post we will go more into depth with this algorithm, gaining *another interpretation* of our objective, namely the variance of the integrated image, through the Fourier Transform and the equivalent operator in the Fourier-domain.

#### Toy example (bonus)
Suppose our image is of a white square centered within an unoccluded black background, and we choose a 2D translation motion model $\theta=[\tau_x, \tau_y]$, where at each step we shift the square towards the top-left corner (non-zero negative values for both $\tau_x, \tau_y$). Compare then the integrated image with shift parameters $\theta=[0, 0]$ to that obtained with the ground truth shift parameters $\theta^\star$

![Optim](/assets/images/comparison_integ.png)  

Until next time!