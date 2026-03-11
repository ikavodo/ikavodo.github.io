---
title: "The Fourier Transform: pt. 2"
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
description: "Fourier Transform tutorial: pt. 2"
---

## Introduction
The Fourier convolution theorem[^1] is an extremely important result from the computational perspective, as with a sufficiently fast algorithm ([FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform)) the order of computational complexity of a convolution operation drops from $O(n^2)$ to $O(n\log n$) (read [this](https://en.wikipedia.org/wiki/Big_O_notation) if you have no idea what I'm talking about). This means that implementing a convolution as a multiplication in the frequency domain is significantly faster than computing it in the time-domain (for sufficiently large $n>N$). On the other hand, the modulation theorem (which is the dual of the previously mentioned convolution theorem) defined as 
<div>
$$x[n]h[n]\overset{\text{FT}}{\leftrightarrow}\frac{1}{2\pi}\int_{-\pi}^{\pi}X(e^{j\theta})H(e^{j(w-\theta)} d\theta),$$
</div>
seems to be less appealing from a computational perspective, and is perhaps more domain-specific (ask the telecommunications people or [synthesizer geeks](https://www.youtube.com/watch?v=vvBl3YUBUyY)[^2] about it).
This post aims to disprove this notion by showing that the modulation theorem can be used constructively to prove results in DSP, via an example involving an important theoretical tool: the ideal lowpass filter.

---

## Ideal Lowpass Filter

An **ideal lowpass filter** is a filter that perfectly passes all frequency components below a certain cutoff frequency $\omega_c$, while completely attenuating all frequencies above $\omega_c$. This type of filter has a **brick-wall frequency response**, meaning it has a sharp cutoff at the boundary between passband and stopband.

### Frequency Response of the Ideal Lowpass Filter

The frequency response of an ideal lowpass filter, $H_{LP}(j\omega)$, is defined as:

<div>
$$H_{LP}(j\omega) = \begin{cases} 
   1, & |\omega| \leq \omega_c \\
   0, & |\omega| > \omega_c, 
\end{cases}$$
</div>

Where we suppose for now that the cutoff frequency is unity, meaning $\omega_c=1$. \\
What does the time-domain representation of this filter look like? Could we use it to implement lowpass filtering by convolution in the time-domain? In order to answer these question we will make use of another important concept in DSP: the Hilbert transformer.

## Hilbert transformer

### Definition

The Hilbert transformer is defined via an impulse response $h_{HT}$ as:

<div> 
$$ 
h_{HT}(t) = \frac{1}{\pi t}, 
$$ 
</div>

with a Fourier transform of

<div> 
$$ 
H_{HT}(j\omega)= -j\, \text{sign}(\omega),
$$ 
</div>

We can use the Hilbert transformer to generate an **analytic**, or complex representation $z[n]$, such that

<div> 
$$ 
z(t) = x(t) + j*(x(t)\circledast h_{HT}(t)) 
$$ 
</div>

where $\circledast$ is the convolution operator and j is the imaginary unit. The frequency domain representation of this signal retains the positive frequency components of x[n], while setting all negative frequency components to zero. This effectively halves the frequency bandwidth, enabling transmission over a narrower band.


## Using the modulation theorem to find the Fourier transform of sinc(t)
We will use the Hilbert transformer and the Fourier modulation theorem to find the frequency-domain representation of the unnormalized sinc function, defined by 

<div>
$$
sinc(t) = \frac{\sin{t}}{t}
$$ 
</div>.
For this purpose we will multiply it by a scalar $\frac{1}{\pi}$ to obtain

<div> 
$$ 
\frac{sinc(t)}{\pi} =\frac{\sin{t}}{\pi t}
$$ 
</div>

Does the denominator of this function now look familiar? Let's first find the Fourier transform of the numerator in order to use the modulation theorem.

<div> 
$$ 
F\{\sin{t}\}= \int_{-\infty}^{\infty} sin(t)e^{-j\omega t}dt = \frac{1}{2j}\int_{-\infty}^{\infty} (e^{jt}-e^{-jt})e^{-j\omega t}dt \\ \overset{lin.}{=} \frac{1}{2j}(\int_{-\infty}^{\infty}e^{-j(\omega-1)t}dt - \int_{-\infty}^{\infty}e^{-j(\omega+1)t}dt) 
\overset{time-shift}{=} \frac{\pi(\delta(\omega-1) - \delta(\omega+1))}{j} \\
\overset{\omega_c=1}{=} \frac{\pi(\delta(\omega-\omega_c) - \delta(\omega+\omega_c))}{j}
$$ 
</div>

Where $\delta(t)$ is the [Dirac delta function](https://en.wikipedia.org/wiki/Dirac_delta_function). \\
Now we can finally use the modulation theorem:

<div> 
$$ 
\frac{\sin{t}}{\pi t} = \sin{t}* \frac{1}{\pi t}\overset{F}{\leftrightarrow} \frac{\pi}{2\pi j}\int_{-\pi}^{\pi} (\delta(\theta-\omega_c) - \delta(\theta-\omega_c))H_{HT}(j(\omega-\theta))d\theta \\ 
= \frac{1}{2j}(H_{HT}(j(\omega-\omega_c))-H_{HT}(j(\omega+\omega_c))).
$$ 
</div>

Let's divide into the cases 
<div>
$$
\begin{cases}
1. \, |\omega|<= \omega_c, \\
2. \, |\omega|> \omega_c,
\end{cases}
$$ 
</div>

and respectively evaluate our intermediate result.
In the first case we have
<div>
$$
H_{HT}(j(\omega-\omega_c)) = j, \, H_{HT}(j(\omega+\omega_c)) = -j \implies\\ 
\frac{1}{2j}(H_{HT}(j(\omega-\omega_c))-H_{HT}(j(\omega+\omega_c))) = \frac{2j}{2j} = 1.
$$ 
</div>
Whereas in the second
<div>
$$
H_{HT}(j(\omega-\omega_c)) = j, \, H_{HT}(j(\omega+\omega_c)) = j \implies\\ 
\frac{1}{2j}(H_{HT}(j(\omega-\omega_c))-H_{HT}(j(\omega+\omega_c))) = \frac{0}{2j} = 0.
$$ 
</div>

Then we can conclude 
<div>
$$

\frac{1}{2j}(H_{HT}(j(\omega-\omega_c))-H_{HT}(j(\omega+\omega_c))) = \\
\begin{cases} 
   1, & |\omega| \leq \omega_c \\
   0, & |\omega| > \omega_c 
\end{cases} \\
= H_{LP}
$$ 
</div>

Meaning we have proven that the unnormalized sinc function and ideal low-pass filter constitute a Fourier transform pair (up to a scalar $\frac{1}{\pi}$).
One of the consequences of this fact is that the we are unable to implement an ideal-lowpass filter in the time domain, as the sinc function extends infinitely in each direction. This means we must find finite (and hopefully causal) approximations of the ideal low-pass for effective lowpass filtering in the time domain...
That's it for now!

---
### Footnotes 

[^1]: see [previous post](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/)
[^2]: FM-modulation actually lies behind radio technology and FM synthesis- a technique which led to the development of the best-selling Yamaha DX7 synthesizer. This synth is responsible for **Lots** of funky sounds you might recognize from [80's pop](https://www.youtube.com/watch?v=djV11Xbc914&list=PLsAmsnfaNA4-CevYq1hrcD_aIP5xWe9Xr).
