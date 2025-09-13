---
title: "Motion model analysis"
layout: post
date: 2025-9-10 14:15
image: 
headerImage: false
tags:
  - Computer Science
  - Math
  - DSP
star: true
category: blog
author: Ido Akov
description: "Motion model analysis"
---

# **Motion model analysis**  

---

## **Motion Model Analysis via DSP Methods**

### **1. The Motion Model**

We consider a **time-varying affine transformation**:

<div>

$$
f(x,y,t) = 
\begin{bmatrix}
\theta_{k1} + \alpha_{k1}t + (\theta_{k2} + \alpha_{k2}t)x + (\theta_{k3} + \alpha_{k3}t)y \\
\theta_{k4} + \alpha_{k4}t + (\theta_{k5} + \alpha_{k5}t)x + (\theta_{k6} + \alpha_{k6}t)y
\end{bmatrix}.
$$

</div>

In compact matrix form:

<div>

$$
f(x,y,t) = (W_0 + t W_1)\phi(x,y), \quad 
\phi(x,y) = \begin{bmatrix}1 \\ x \\ y \end{bmatrix},
$$  

where $W_0, W_1 \in \mathbb{R}^{2 \times 3}$.  

</div>

- $W_0$: base affine transform (at $t=0$)  
- $W_1$: linear time drift (change rate of transform)  

---

### **2. DSP Interpretation**

- This is a **linear time-varying (LTV) operator** acting on a 2D spatial signal across time.  
- At each fixed $t$, $f$ is a standard affine warp: rotation, scale, shear, translation.  
- Across $t$, the parameters evolve **linearly** (first-order modulation).  

From a DSP perspective:  
- The system is **not LTI** → no single frequency response.  
- Must use **time–frequency methods** (e.g., STFT) or **local stationarity approximations**.  

---

### **3. Frequency-Domain Effects**

For an image $I$ with Fourier transform $\hat I(\omega)$, affine warp gives:

<div>

$$
\mathcal{F}\{I(A(t)\mathbf{u}+b(t))\}(\omega) = 
\frac{1}{\|\det A(t)\|} e^{-j \omega^\top A(t)^{-1} b(t)} 
\hat I(A(t)^{-T}\omega).
$$

</div>

- **Translation** → phase ramp in spectrum.  
- **Rotation** → rotation in frequency plane.  
- **Scaling** → frequency stretching + amplitude rescaling.  
- **Shear** → mixes frequencies linearly.  

---

### **4. Motion Planes in 3D Spectrum**

For pure translation $b(t)=vt$, the 3D Fourier transform of the video lies on **motion planes**:

<div>

$$
\omega_t + v_x \omega_x + v_y \omega_y = 0.
$$  

</div>

- With affine velocity fields, motion planes become **tilted and space-dependent**.  
- This corresponds to **Doppler-like effects** in spatiotemporal frequency space.  

---

### **5. Implementation as DSP Operations**

- **Resampling**: Warping = nonuniform sampling → requires interpolation.  
- **Anti-aliasing**: Apply pre-lowpass when $\|\det A(t)\|<1$.  
- **Interpolation kernels**: bilinear (fast), bicubic/B-spline (balanced), sinc (ideal).  
- **Shear decomposition**: Affine = composition of 3 shears → implementable with 1D fractional-delay filters.  

---

### **6. Parameter Estimation as Demodulation**

- **Phase correlation** (FFT-based): translation.  
- **Fourier–Mellin**: rotation + scale.  
- **Lucas–Kanade (gradient-based)**: local affine parameters, solved via least squares.  
- **Kalman filtering**: smooth temporal evolution of $(W_0, W_1)$.  

This is analogous to **carrier phase synchronization** in communications: maximizing alignment of warped frames is a **coherent integration** problem.  
