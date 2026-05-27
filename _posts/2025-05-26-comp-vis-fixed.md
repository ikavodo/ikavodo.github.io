---
title: "Computer Vision Cheat Sheet: Key Concepts and Formulas"
layout: post
date: 2025-6-26 13:15
image: 
headerImage: false
tags:
  - Computer Science
  - Math
star: true
category: blog
author: Ido Akov
description: "Processed notes from a Computer Vision course covering camera calibration, feature detection, optical flow, RANSAC, and 3D reconstruction."
---

These are processed notes from a Computer Vision course I took at Aalto University in 2023. The course covered the classical pipeline from image formation through 3D reconstruction, with detours into feature matching, robust estimation, and deep learning for vision. I found it useful to have the key formulas and ideas in one place, so here they are.

---

## 1. Camera Calibration & Projective Geometry

Before doing anything useful with an image, you need to know how the camera maps the 3D world onto its 2D sensor. That mapping is captured by the intrinsic matrix.

### Intrinsic Camera Matrix

<div>
$$
K = \begin{bmatrix}
f & s & u_0 \\
0 & af & v_0 \\
0 & 0 & 1
\end{bmatrix}
$$
</div>

- $f$: focal length
- $s$: skew (non-rectangular pixels; usually ≈ 0 for modern cameras)
- $(u_0, v_0)$: principal point (image center)
- $a$: aspect ratio

### Homogeneous Coordinates

Working in homogeneous coordinates is what makes projective geometry tractable — it turns perspective division into a linear operation. Projective transformations have **8 degrees of freedom** because an overall scale factor is irrelevant:

<div>
$$
c \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \equiv \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix}
$$
</div>

A useful consequence: parallel lines, which never meet in Euclidean space, intersect at a well-defined point at infinity in projective space.

---

## 2. Feature Detection & Matching

Matching images across viewpoints or time requires finding distinctive, repeatable locations. Two workhorses: Harris corners and SIFT descriptors.

### Harris Corner Detection

A corner is a point where the image intensity changes strongly in two directions — unlike an edge (one direction) or a flat region (none). Harris detects this by analyzing the second-moment matrix of local gradients:

1. Compute image gradients $I_x$, $I_y$ (Sobel filters).
2. Construct the second-moment matrix:

<div>
$$
M = \begin{bmatrix}
I_x^2 & I_x I_y \\
I_x I_y & I_y^2
\end{bmatrix}
$$
</div>

3. Corner response:

<div>
$$
R = \det(M) - k \cdot \mathrm{trace}(M)^2
$$
</div>

The eigenvalues of $M$ tell the story: $\lambda_1 \gg \lambda_2$ → edge; $\lambda_1 \approx \lambda_2$ (both large) → corner; both small → flat region.

### SIFT Descriptors

SIFT trades some localization precision for invariance to scale, rotation, and illumination change. Each keypoint gets a **128-dimensional** descriptor: divide a $16\times16$ neighborhood into $4\times4$ sub-patches and compute 8-bin orientation histograms per patch. Matching then uses the Nearest Neighbor Distance Ratio to suppress ambiguous matches:

<div>
$$
\mathrm{NNDR} = \frac{d_1}{d_2} \leq 0.8
$$
</div>

---

## 3. Optical Flow & Motion Estimation

Optical flow estimates how each pixel moves between frames. It underlies video stabilization, action recognition, and anything that needs to track motion over time.

### Lucas-Kanade Method

Under three assumptions — brightness constancy, small inter-frame motion, and local spatial coherence — each pixel's velocity $(u, v)$ satisfies:

<div>
$$
\begin{bmatrix} I_x & I_y \end{bmatrix}
\begin{bmatrix} u \\ v \end{bmatrix}
= -I_t
$$
</div>

This is one equation in two unknowns. The coherence assumption lets you pool constraints from a local patch and solve the overdetermined system via least squares.

### Aperture Problem

A single constraint per pixel is not enough. When you can only see a small patch around an edge, the velocity component *along* the edge is invisible — only the normal component can be recovered. This is the aperture problem, and it's why optical flow needs spatial pooling or additional assumptions to work.

---

## 4. RANSAC & Model Fitting

Real data has outliers. RANSAC (Random Sample Consensus) fits a model robustly by iterating: fit on a tiny random subset, count how many other points agree, keep the best hypothesis.

1. Randomly sample the minimal point set (e.g., 4 points for a homography).
2. Fit the model.
3. Count inliers: points within threshold $t$, where $t^2 = 3.84\sigma^2$.
4. Refit using all inliers.

The required number of iterations for success probability $p$, outlier ratio $e$, and sample size $s$ is:

<div>
$$
N = \frac{\log(1 - p)}{\log(1 - (1 - e)^s)}
$$
</div>

---

## 5. Hough Transform

The Hough transform is a voting-based approach to detecting parametric shapes. For lines: after edge detection (e.g., Canny), each edge point votes for all $(\theta, \rho)$ pairs consistent with it. Peaks in the accumulator correspond to detected lines — even when those lines are partially occluded or noisy.

---

## 6. Triangulation & 3D Reconstruction

With two calibrated cameras observing the same point, you can recover its 3D position by triangulation — finding the point that best explains both 2D observations.

### Triangulation

Given camera matrices $P_1$, $P_2$ and corresponding image points $x_1$, $x_2$, the 3D point $X$ satisfies:

<div>
$$
x_1 \times (P_1 X) = 0, \quad x_2 \times (P_2 X) = 0
$$
</div>

Solved via SVD.

### Bundle Adjustment

In practice, both camera poses and 3D point positions are estimated with noise. Bundle adjustment jointly refines 3D structure (points $X$) and camera motion (matrices $P_i$) by minimizing total reprojection error — the gold standard for multi-view reconstruction accuracy, at the cost of being a large nonlinear least-squares problem.

---

## 7. Deep Learning for Vision

### CNN Basics

Convolutional networks learn spatial feature hierarchies through repeated convolution, nonlinearity, and pooling. Pooling reduces spatial resolution while increasing receptive field. The standard multi-class classification loss is cross-entropy:

<div>
$$
\mathcal{L} = -\sum_i t_i \log p_i
$$
</div>

### Region Proposal Networks

Two-stage detectors (e.g., Faster R-CNN) first generate candidate bounding boxes via a Region Proposal Network, then classify and refine each box. The RPN shares convolutional features with the detection head, making the whole pipeline trainable end-to-end.

---

## References

1. [Visualizing Linear Transformations (Geogebra)](https://www.geogebra.org/m/YCZa8TAH)
2. [RANSAC Lecture Notes (PSU)](https://www.cse.psu.edu/~rtc12/CSE486/lecture15_6pp.pdf)
3. [Homogeneous Coordinates (Song Ho)](http://www.songho.ca/math/homogeneous/homogeneous.html)
