---
title: "From Convolution to Modulation: Proving the sinc–Lowpass Duality"
layout: post
date: 2024-11-13 16:05
image: /assets/images/fourier%20transf.png
headerImage: true
tags:
  - Fourier Transform
  - DSP
  - Math
star: true
category: blog
author: Ido Akov
description: "Using the modulation theorem and Hilbert transformer to show that the sinc function and the ideal lowpass filter are Fourier pairs."
---

## Introduction

In [Part 1](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/) we explored the duality of the DTFT and IDTFT through a simple problem. Now we turn to another facet of Fourier theory: the **convolution theorem** and its dual, the **modulation theorem**. While convolution is celebrated for enabling fast algorithms via the FFT, the modulation theorem often seems less glamorous – but it is equally powerful.  

In this post, we’ll use the modulation theorem to prove a classic result: the unnormalized sinc function $\frac{\sin t}{t}$ and the ideal lowpass filter are Fourier transform pairs (up to a constant). Along the way we’ll meet the Hilbert transformer, an essential tool in signal processing and communications.

**What you will learn**  
- The definition of the ideal lowpass filter and why it’s called “brick‑wall”.  
- The Hilbert transformer and its frequency response.  
- How the modulation theorem elegantly derives the Fourier transform of $\operatorname{sinc}(t)$.  
- Why the ideal lowpass filter cannot be implemented in practice – and what we do instead.

---

## Ideal Lowpass Filter

An **ideal lowpass filter** passes all frequency components below a cutoff $\omega_c$ with gain 1 and completely blocks everything above $\omega_c$. Its frequency response is a rectangle:

<div>
$$H_{LP}(j\omega) = \begin{cases} 
1, & |\omega| \le \omega_c,\\
0, & |\omega| > \omega_c.
\end{cases}$$
</div>

This is a “brick‑wall” response – a sharp transition that is impossible to realize exactly with a finite impulse response, but conceptually invaluable.

For simplicity, we’ll take $\omega_c = 1$ (the results scale easily). Our goal is to find the inverse Fourier transform of $H_{LP}(j\omega)$, i.e., the impulse response $h_{LP}(t)$. That turns out to be the sinc function.

---

## The Hilbert Transformer

The **Hilbert transformer** is an all‑pass filter that introduces a $-\frac{\pi}{2}$ phase shift. Its impulse response and frequency response are  

<div> 
$$ h_{HT}(t) = \frac{1}{\pi t}, \qquad 
H_{HT}(j\omega) = -j\,\operatorname{sgn}(\omega). $$
</div>

(Here $\operatorname{sgn}(\omega)$ is the sign function.)  
The Hilbert transform is used to create **analytic signals**: for a real signal $x(t)$, the analytic signal $z(t) = x(t) + j\,\mathcal{H}\{x(t)\}$ has a Fourier transform that is zero for negative frequencies. This property is crucial in communications and also in our derivation.

---

## Proving the sinc–Lowpass Pair

We want to show that  

<div>
$$\frac{\sin t}{\pi t} \quad\overset{\mathcal{F}}{\longleftrightarrow}\quad H_{LP}(j\omega),$$
</div>

with $\omega_c = 1$. (The factor $1/\pi$ will give exactly the brick‑wall response.)  
Equivalently, we need the Fourier transform of $\frac{\sin t}{\pi t}$. Write it as a product:

<div>
$$\frac{\sin t}{\pi t} = \sin t \cdot \frac{1}{\pi t}.$$
</div>

The factor $\frac{1}{\pi t}$ is exactly $h_{HT}(t)$, the Hilbert transformer impulse response. So we can use the **modulation theorem**, which is the dual of convolution:

<div>
$$x(t) y(t) \overset{\mathcal{F}}{\longleftrightarrow} \frac{1}{2\pi} \int_{-\infty}^{\infty} X(j\theta) Y(j(\omega-\theta)) d\theta.$$
</div>

In our case, $x(t)=\sin t$ and $y(t)=h_{HT}(t)$.

---

### Step 1: Fourier transform of $\sin t$

Using Euler’s formula $\sin t = \frac{e^{jt} - e^{-jt}}{2j}$,  

<div>
$$\mathcal{F}\{\sin t\} = \frac{1}{2j}\left( \mathcal{F}\{e^{jt}\} - \mathcal{F}\{e^{-jt}\} \right).$$
</div>

Recall that $\mathcal{F}\{e^{j\omega_0 t}\} = 2\pi \delta(\omega - \omega_0)$. Hence  

<div>
$$\mathcal{F}\{\sin t\} = \frac{1}{2j}\left( 2\pi\delta(\omega-1) - 2\pi\delta(\omega+1) \right) = \frac{\pi}{j}\big( \delta(\omega-1) - \delta(\omega+1) \big).$$
</div>

### Step 2: Apply the modulation theorem

Let $X(j\omega) = \mathcal{F}\{\sin t\}$ and $Y(j\omega) = H_{HT}(j\omega) = -j\,\operatorname{sgn}(\omega)$. Then  

<div>
$$\mathcal{F}\left\{\frac{\sin t}{\pi t}\right\} = \frac{1}{2\pi} \int_{-\infty}^{\infty} X(j\theta) Y(j(\omega-\theta)) d\theta.$$
</div>

Substitute $X(j\theta)$:

<div>
$$= \frac{1}{2\pi} \int_{-\infty}^{\infty} \frac{\pi}{j}\big( \delta(\theta-1) - \delta(\theta+1) \big) Y(j(\omega-\theta)) d\theta.$$
</div>

The delta functions pick out two values of $\theta$:

<div>
$$= \frac{1}{2j} \left( Y(j(\omega-1)) - Y(j(\omega+1)) \right).$$
</div>

Now insert $Y(j\Omega) = -j\,\operatorname{sgn}(\Omega)$:

<div>
$$\mathcal{F}\left\{\frac{\sin t}{\pi t}\right\} = \frac{1}{2j} \left( -j\,\operatorname{sgn}(\omega-1) + j\,\operatorname{sgn}(\omega+1) \right) = \frac{1}{2} \left( \operatorname{sgn}(\omega+1) - \operatorname{sgn}(\omega-1) \right).$$
</div>

### Step 3: Interpret the result

The sign function $\operatorname{sgn}(x)$ is $-1$ for $x<0$, $+1$ for $x>0$. Evaluate the expression for different $\omega$:

- When $|\omega| < 1$, we have $\omega+1 > 0$, $\omega-1 < 0$, so  
  $\operatorname{sgn}(\omega+1)=1$, $\operatorname{sgn}(\omega-1)=-1$, and the difference is $1$.
- When $|\omega| > 1$, the two signs are the same:  
  for $\omega > 1$, both $\omega+1 > 0$ and $\omega-1 > 0$;  
  for $\omega < -1$, both are negative.  
  Hence the difference is $0$.

Therefore  

<div>
$$\mathcal{F}\left\{\frac{\sin t}{\pi t}\right\} = 
\begin{cases}
1, & |\omega| \le 1,\\
0, & |\omega| > 1,
\end{cases}$$
</div>

which is exactly $H_{LP}(j\omega)$ with $\omega_c = 1$. **QED.**

---

## Why This Matters

We have shown that the ideal lowpass filter’s impulse response is the sinc function $\frac{\sin t}{\pi t}$. This has profound practical consequences:

- The sinc function extends infinitely in both directions, so an ideal lowpass filter is **non‑causal** and cannot be implemented in real‑time.
- In practice we must use **finite approximations** (windowed sinc filters) that trade off sharp cutoff for realizability.
- The derivation also illustrates the power of the modulation theorem: a seemingly difficult transform pair fell out naturally once we recognized the product structure and employed the Hilbert transformer.

---

## Key Takeaways

- The modulation theorem is the dual of convolution and is equally fundamental.  
- The Hilbert transformer is a key building block, especially for creating analytic signals.  
- The Fourier pair $\frac{\sin t}{\pi t} \leftrightarrow$ brick‑wall lowpass is a cornerstone of filter design.  
<!-- - Understanding these relationships prepares you for advanced topics like multirate processing, filter banks, and wavelet transforms. -->

---
<!-- 
## What’s Next?

In **Part 3** (coming soon), we’ll explore how these concepts appear in practical applications: sampling, aliasing, and the connection to the discrete Fourier transform. Stay tuned!

---
 -->
<!-- ### Footnotes

[^1]: See [Part 1](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/) for the duality discussion.  
[^2]: FM modulation underpins both radio and the famous Yamaha DX7 synthesizer – check out [80’s pop](https://www.youtube.com/watch?v=djV11Xbc914) for that unmistakable sound. -->