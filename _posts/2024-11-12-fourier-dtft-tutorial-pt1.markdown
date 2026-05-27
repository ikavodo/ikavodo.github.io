---
title: "Demystifying the DTFT: A Deep Dive with a Simple Problem"
layout: post
date: 2024-11-12 11:58
image: /assets/images/fourier%20transf.png
headerImage: true
tags:
  - Fourier transform
  - DSP
  - Math
star: true
category: blog
author: Ido Akov
description: "A step‑by‑step exploration of the Discrete‑Time Fourier Transform and its inverse, using a single textbook problem to uncover deep duality."
---

## Introduction
If there's one thing the internet is full of (except for [cats](https://www.youtube.com/watch?v=Of2HU3LGdbo)) it's tutorials about the Fourier transform. Some of these are [really well done](https://betterexplained.com/articles/an-interactive-guide-to-the-fourier-transform/), so why write another?  
In my case, the answer is quite selfish: I'm currently studying DSP in depth via Sanjit Mitra’s excellent book [*Digital Signal Processing: A Computer‑Based Approach*](https://www.mathworks.com/academia/books/digital-signal-processing-mitra.html), and I want a vehicle to test my deeper understanding beyond solving exercises. What better way than to explain the concepts to someone else?

**What you will learn in this post**  
- The definition of the Discrete‑Time Fourier Transform (DTFT) and its inverse (IDTFT).  
- How a seemingly simple textbook integral can reveal the deep duality between time and frequency domains.  
- Two ways to evaluate that integral – naive and informed – and why the informed way is so powerful.  
- How the time‑shift theorem connects the IDTFT to a “plucking” operation.

---

## The basics

### Discrete‑Time Fourier Transform (DTFT)
Let $x[n]$ be a sequence (if finite, we extend it with zeros). The DTFT is defined as  

<div>
$$X(e^{j\omega}) = \sum_{n=-\infty}^{\infty} x[n] e^{-j\omega n}, \quad \omega \in [-\pi, \pi].$$
</div>

- $x[n]\overset{\text{FT}}{\leftrightarrow}X(e^{j\omega})$ is a Fourier transform pair.  
- $\omega$ is angular frequency in radians per sample. Because $X(e^{j\omega}) = X(e^{j(\omega+2\pi)})$, the DTFT is $2\pi$-periodic; we can pick any interval of length $2\pi$ to represent it uniquely.

### Inverse Discrete‑Time Fourier Transform (IDTFT)
The IDTFT recovers $x[n]$ from its transform:

<div>
$$x[n] = \frac{1}{2\pi} \int_{-\pi}^{\pi} X(e^{j\omega}) e^{j\omega n} d\omega.$$
</div>

The integral can be taken over any $2\pi$-wide interval. At first glance this formula looks abstract – we’ll soon give it a concrete interpretation.

---

## A simple (yet illuminating) problem

The following exercise from Mitra’s book was an eye‑opener for me.  

**Problem:** Let $X(e^{j\omega})$ be the DTFT of $x[n]$. Evaluate  

<div>
$$\int_{-\pi}^{\pi} X(e^{j\omega}) d\omega.$$
</div>

A quick solution using the IDTFT is:

<div>
$$\int_{-\pi}^{\pi} X(e^{j\omega}) d\omega = 2\pi \left( \frac{1}{2\pi} \int_{-\pi}^{\pi} X(e^{j\omega}) e^{j\omega 0} d\omega \right) = 2\pi x[0].$$
</div>

But there is much more hidden in that integral. Let’s expand $X(e^{j\omega})$ via its definition:

<div>
$$\int_{-\pi}^{\pi} X(e^{j\omega}) d\omega 
= \int_{-\pi}^{\pi} \left( \sum_{n=-\infty}^{\infty} x[n] e^{-j\omega n} \right) d\omega 
\overset{\text{swap}}{=} \sum_{n=-\infty}^{\infty} x[n] \left( \int_{-\pi}^{\pi} e^{-j\omega n} d\omega \right).$$
</div>

Now we need to understand the inner integral $I[n] = \int_{-\pi}^{\pi} e^{-j\omega n} d\omega$. We’ll evaluate it in two ways.

---

### The naive way

Compute the indefinite integral:

<div>
$$\int e^{-j\omega n} d\omega = \frac{e^{-j\omega n}}{-j n}.$$
</div>

Applying the limits $-\pi$ to $\pi$:

<div>
$$I[n] = \left[ \frac{e^{-j\omega n}}{-j n} \right]_{-\pi}^{\pi} = \frac{e^{-j\pi n} - e^{j\pi n}}{-j n}.$$
</div>

Using Euler’s formula $e^{-j\pi n} - e^{j\pi n} = -2j \sin(\pi n)$ gives  

<div>
$$I[n] = \frac{2 \sin(\pi n)}{n}.$$
</div>

For integer $n$, $\sin(\pi n)=0$, so $I[n]=0$ when $n\neq 0$. At $n=0$ the expression is undefined, so we compute directly:

<div>
$$I[0] = \int_{-\pi}^{\pi} 1 \, d\omega = 2\pi.$$
</div>

Thus  

<div>
$$I[n] = \begin{cases}
2\pi, & n=0,\\
0, & n\neq 0.
\end{cases}$$
</div>

This is exactly $2\pi\delta[n]$, where $\delta[n]$ is the unit impulse.  

So the naive calculation already yields a fundamental result – but can we see it more elegantly?

---

### The informed way

Fourier analysis thrives on known transform pairs and theorems. The most basic pair is  

<div>
$$\delta[n] \overset{\text{FT}}{\longleftrightarrow} 1,$$
</div>

since $\sum_n \delta[n] e^{-j\omega n} = 1$.  

Now recall the **convolution theorem**:  

<div>
$$x[n] \circledast h[n] \overset{\text{FT}}{\longleftrightarrow} X(e^{j\omega}) H(e^{j\omega}),$$
</div>

where $\circledast$ denotes convolution. Because $\delta[n]$ is the identity for convolution, its transform must be the identity for multiplication, i.e. $H(e^{j\omega})=1$.  

> **Note:** The same conclusion follows from the modulation theorem: setting $H(e^{j\omega})=2\pi\delta(e^{j\omega})$ gives $h[n]=1$ – a useful dual perspective.

---

### The duality theorem

For Fourier transforms over the same domain (continuous or discrete), duality holds:  

<div>
$$X(t) \overset{\text{FT}}{\longleftrightarrow} 2\pi x(-j\omega).$$
</div>

For the DTFT, time is discrete and frequency continuous, so we need a slight trick. Define a “DTFT‑like” operation on a continuous‑frequency function:

<div>
$$\text{DTFT}\{X(e^{j\omega})\} = \int_{-\pi}^{\pi} X(e^{j\omega}) e^{-j\omega n} d\omega.$$
</div>

Then

<div>
$$\int_{-\pi}^{\pi} X(e^{j\omega}) e^{-j\omega n} d\omega 
= 2\pi \left( \frac{1}{2\pi} \int_{-\pi}^{\pi} X(e^{j\omega}) e^{j\omega(-n)} d\omega \right) 
\overset{\text{IDTFT}}{=} 2\pi x[-n].$$
</div>

Now apply this to our mystery integral with $X(e^{j\omega}) = 1$:

<div>
$$\int_{-\pi}^{\pi} e^{-j\omega n} d\omega = 2\pi \left( \frac{1}{2\pi} \int_{-\pi}^{\pi} 1 \cdot e^{j\omega(-n)} d\omega \right) 
= 2\pi \, \delta[-n] = 2\pi \delta[n].$$
</div>

(We used that $\delta[n]$ is even.) So the integral is $2\pi\delta[n]$ – exactly what the naive method gave.

Returning to the original problem:

<div>
$$\sum_{n=-\infty}^{\infty} x[n] \left( \int_{-\pi}^{\pi} e^{-j\omega n} d\omega \right) 
= \sum_{n=-\infty}^{\infty} x[n] \cdot 2\pi \delta[n] = 2\pi x[0].$$
</div>

**What have we learned?**  
The integral $\int_{-\pi}^{\pi} e^{-j\omega n} d\omega$ can be interpreted as applying the DTFT operator to the constant frequency‑domain function $1$, yielding $2\pi\delta[n]$. This is a beautiful illustration of duality.

---

### The time‑shift theorem

The time‑shift theorem states:

<div>
$$x[n-n_0] \overset{\text{FT}}{\longleftrightarrow} e^{-j\omega n_0} X(e^{j\omega}).$$
</div>

Using it, we get $\delta[n-n_0] \overset{\text{FT}}{\longleftrightarrow} e^{-j\omega n_0}$. Now look at the IDTFT again:

<div>
$$\frac{1}{2\pi} \int_{-\pi}^{\pi} X(e^{j\omega}) e^{j\omega n_0} d\omega 
= \frac{1}{2\pi} \int_{-\pi}^{\pi} \left( \sum_n x[n] e^{-j\omega n} \right) e^{j\omega n_0} d\omega \\
= \frac{1}{2\pi} \sum_n x[n] \left( \int_{-\pi}^{\pi} e^{j\omega (n_0 - n)} d\omega \right) 
= \frac{1}{2\pi} \sum_n x[n] \cdot 2\pi \delta[n_0 - n] = x[n_0].$$
</div>

So the IDTFT is nothing but a “plucking” operation: it picks out the sample $x[n_0]$ by correlating with a shifted impulse in the frequency domain.

---

## Key Takeaways

- The DTFT and IDTFT are dual; the same integral can be interpreted in both domains.  
- A simple textbook integral can reveal profound duality when examined through Fourier theorems.  
- The time‑shift theorem gives the IDTFT an intuitive meaning: it extracts a single sample by matching a phase‑shifted complex exponential.  
<!-- - Understanding these fundamentals prepares you for deeper topics like convolution, filtering, and the fast Fourier transform. -->

That’s it for now – stay tuned for **Part 2**, where we’ll use the modulation theorem to derive the Fourier transform of the sinc function and connect it to the ideal lowpass filter.