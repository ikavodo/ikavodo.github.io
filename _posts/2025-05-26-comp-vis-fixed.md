---
title: "Computer Vision Cheat Sheet: Key Concepts and Formulas"
layout: post
date: 2025-5-26 13:15
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

These are some processed notes from a Computer Vision course I took at Aalto University in 2023.

---

## 1. Camera Calibration & Projective Geometry

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
- $s$: skew (non-rectangular pixels)
- $(u_0, v_0)$: principal point
- $a$: aspect ratio

### Homogeneous Coordinates

Projective transformations have **8 degrees of freedom** because scaling is irrelevant:

<div>
$$
c \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \equiv \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix}
$$
</div>

Parallel lines intersect at infinity in projective space.

---

## 2. Feature Detection & Matching

### Harris Corner Detection

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

Eigenvalue interpretation: $\lambda_1 \gg \lambda_2$ → edge; $\lambda_1 \approx \lambda_2$ (large) → corner; both small → flat region.

### SIFT Descriptors

A **128-dimensional** descriptor per keypoint: divide a $16\times16$ neighborhood into $4\times4$ sub-patches and compute 8-bin orientation histograms per patch. Matching uses the Nearest Neighbor Distance Ratio:

<div>
$$
\mathrm{NNDR} = \frac{d_1}{d_2} \leq 0.8
$$
</div>

---

## 3. Optical Flow & Motion Estimation

### Lucas-Kanade Method

Assumes brightness constancy, small inter-frame motion, and local spatial coherence. The per-pixel constraint is:

<div>
$$
\begin{bmatrix} I_x & I_y \end{bmatrix}
\begin{bmatrix} u \\ v \end{bmatrix}
= -I_t
$$
</div>

Solved over a local patch via least squares (normal equations).

### Aperture Problem

When only edge information is available, the motion component along the edge is unobservable — only the normal component can be recovered.

---

## 4. RANSAC & Model Fitting

1. Randomly sample the minimal point set (e.g., 4 points for a homography).
2. Fit the model.
3. Count inliers: points within threshold $t$ where $t^2 = 3.84\sigma^2$.
4. Refit using all inliers.

The required number of iterations for success probability $p$ with outlier ratio $e$ and sample size $s$:

<div>
$$
N = \frac{\log(1 - p)}{\log(1 - (1 - e)^s)}
$$
</div>

---

## 5. Hough Transform

For line detection: after edge detection (e.g., Canny), each edge point votes for all $(\theta, \rho)$ pairs consistent with it. Peaks in the accumulator correspond to detected lines.

---

## 6. Triangulation & 3D Reconstruction

### Triangulation

Given camera matrices $P_1$, $P_2$ and corresponding image points $x_1$, $x_2$, the 3D point $X$ satisfies:

<div>
$$
x_1 \times (P_1 X) = 0, \quad x_2 \times (P_2 X) = 0
$$
</div>

Solved via SVD.

### Bundle Adjustment

Non-linear optimization jointly refining 3D structure (points $X$) and camera motion (matrices $P_i$) to minimize reprojection error.

---

## 7. Deep Learning for Vision

### CNN Basics

Convolutional layers with pooling (max or average) for dimensionality reduction. Standard classification loss:

<div>
$$
\mathcal{L} = -\sum_i t_i \log p_i
$$
</div>

### Region Proposal Networks

Propose candidate bounding boxes as the first stage of two-stage detectors (e.g., Faster R-CNN).

---

## References

1. [Visualizing Linear Transformations (Geogebra)](https://www.geogebra.org/m/YCZa8TAH)
2. [RANSAC Lecture Notes (PSU)](https://www.cse.psu.edu/~rtc12/CSE486/lecture15_6pp.pdf)
3. [Homogeneous Coordinates (Song Ho)](http://www.songho.ca/math/homogeneous/homogeneous.html)
