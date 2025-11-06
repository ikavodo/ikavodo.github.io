---
title: "Motion computation via an unsupervised-learning approach (pt.2)"
layout: post
date: 2025-11-06 14:00
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
Hihi! Here's to part two of this series, which is documenting my research in real-time, for purposes mostly of making things clearer for me, myself and I. 
This part deals mainly with implementation of the motion computation algorithm in the Fourier domain.

 
## Fourier operators
We begin our deep dive into the world of Fourier operators with the observation that most of the operations we've seen within our algorithmic framework are *linear*. For a brief recap on this, recall that a linear operator over a vector space is defined by 
<div>
$$
T(\alpha_1 x_1 + \alpha_2 x_2) = \alpha_1 T(x_1) + \alpha_2 T(x_2)
$$
</div>
Linear operators have all kinds of very nice properties, such as the fact that a composition of two linear transformations $T(x) = T_2 \circ T_1 = T_2(T_1(x))$ is itself linear. Now, supposing that we can represent the transformations T1, T2 in matrix form, what is the implication of this for representating the operator T? Which matrix operation becomes "equivalent" to the composition of linear transformations?

Let's now take the rather abstract mathematical concept of linearity and connect it back to the objects we are working with, which are different motion models. We can represent these by composing linear operators, meaning by multiplying matrices representing the individual motion operations. For the case of 2D translation we have the rather simple
<div>
$$
T(p) = p + tv
$$
</div>

where $p = \begin{bmatrix} x \\ y \end{bmatrix}^T$ is a 2D vector of pixel coordinates, and v a 2D velocity vector representing the direction in which the pixel p is displaced at each timestep t. We can represent this in matrix form via   
<div>
$$
T(p) = T \cdot p = \begin{bmatrix} 
1 & 0 & v_x \\ 
0 & 1 & v_y \\ 
0 & 0 & 1 
\end{bmatrix} \cdot \begin{bmatrix} 
x \\ 
y \\ 
1 
\end{bmatrix}
$$
</div>
where p is represented in [homogeneous coordinates](https://en.wikipedia.org/wiki/Homogeneous_coordinates), and the matrix T has two degrees of freedom, representing the 2D motion model transformation.

As previously explained, we can add motion parameters to obtain more complicated motion, represented by a transformation with more degrees of freedom. As a result of the linearity of the motion transformation, the matrix is most easily represented as a *composition* of matrices representing the different motion parameter components. It is worthwhile then to *decompose* the motion transformation into the different matrix components, as we do in the next example, which represents a 3DoF rotation motion model: 
<div>
$$R_{\theta}(p) = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & 0 \\ \sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} 1 & 0 & v_x \\ 0 & 1 & v_y \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & v_x \\ \sin(\theta) & \cos(\theta) & v_y \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$
</div>
What are the next steps to get matrix representations of similarity (4DoF) and affine (6DoF) transformations? (*hint*: see [this](https://math.stackexchange.com/questions/2866077/degrees-of-freedom-in-affine-transformation-and-homogeneous-transformation))

Now that we understand how to represent motion transformations as linear compositions of relatively simple linear operators, we can begin to understand how to apply these different operators in the *Fourier domain*. First, let's get some context as to why we would want to do this in the first place.

## Operator equivalence
### Background
Why should we compute certain mathematical operations in the Fourier domain? The simplest answer to this inquiry has to do with the notion of *duality* between operators with regard to the two domains (see [first](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/) and [second](https://ikavodo.github.io/fourier-transform-tutorial-pt-2/) blogposts). If one of two dual operators is more efficient to compute, then naturally its relevant domain is the better one within which to do the computation, given that we can transform to that domain 'fast enough' with respect to the order of complexity of the original problem  (does it make sense to transform to the Fourier domain to compute the *power* of a signal? Why not?). 

For example, if we want to compute a convolution between two signals $s_1 \circledast s_2 $, we can use the duality $\circledast \overset{\mathcal{FT}}{\longleftrightarrow} \times$ together with a fast transform algorithm such as [FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform) to compute the convolution as multiplication in the Fourier domain, finally transforming back to get the desired result. Somewhat surprisingly, for long enough signals $s_1 s_2$, this would actually *be faster* than simply performing the convolution in the initial time/spatial domain.  

Next, why would we want to compute *our* specific motion-computation algorithm in the Fourier domain? This will hopefully become more clear in a bit, and it has to do with two different facets, the first of which relates to speed and computational-efficiency, and the second (and more important) one to utilizing *additional* Fourier-domain-based transforms and algorithms to in essence *convert* various motion models into others. Let's first understand why the Fourier transform is a 'good-fit' for our objective function in the first case, and how representing it in the Fourier domain in fact makes it *more interpretable*, as well as gives additional perspective about the problem.

### The Fourier transform as a linear operator
A bit of mathematical background as justification: we begin with the observation that the Fourier transform $\mathcal{F}\lbrace T \rbrace$ of a function $T(x)$ is a *linear* operator (prove this! It's straightforward). This basically means that if we can represent our objective as a composition of "simple" linear operators, then the linearity of the Fourier transform ensures that the equivalent objective in the Fourier domain (namely the composition of equivalent Fourier operators) remains equally "simple". This will become clear soon.

*Note*: there is an operator within our objective function which is *not* linear, but rather *bilinear*. This is the *interpolation* operator used for ensuring smoothness when warping frames (see [this](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.grid_sample.html)). We will get back to this operation later, ignoring it at the moment for simplicity's sake.

Now let's show how the linearity of the Fourier Transform comes into play: 

<div>
$$
f_{\text{obj}}(I_0,\dots,I_{T-1}, \theta)
=
\mathrm{Var}\!\left(
\overline{I}
\right)
=
\mathrm{Var}\!\left(
\frac{1}{T}\sum_{t=0}^{T-1} W^t(I_t,\theta)
\right)
$$
</div>

We can use the linearity of the Fourier Transform to show that for the integrated frame $\overline{I}$ the equivalent Fourier operator is 

 <div>
$$
\mathcal{F}\lbrace \overline{I} \rbrace \overset{\text{definition}}= 
\mathcal{F} \lbrace \frac{1}{T}\sum_{t=0}^{T-1} W^t(I_t,\theta) \rbrace \overset{linearity}= 
\frac{1}{T} \mathcal{F}\lbrace \sum_{t=0}^{T-1} W^t(I_t,\theta) \rbrace \overset{linearity}=
\frac{1}{T}\sum_{t=0}^{T-1} \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace
$$
</div>

Which looks simple enough already! Now what's left is to verify how we can explicitly write the operator $\mathcal{F} \lbrace W^t(I^t,\theta) \rbrace$.

### Time-domain translation vs. phase-shift

Recall the duality previously introduced in the [first]() blogpost.
We had 
<div>
$$x[n-n_0]\overset{\text{FT}}{\leftrightarrow}e^{-j\omega n_o}X(e^{j\omega})$$,
</div>
Meaning that in 1D a shift in the time/spatial domain is equivalent to a phase shift in the frequency domain.
Now supposing a 2D translation model, this means in essence that we can model 
$W(I,\theta) = I(x- \tau_x, y-\tau_y)$ where $ \theta = \begin{bmatrix} \tau_x \\ \tau_y \end{bmatrix}^T $ is a 2D motion parameter vector, in terms of a phase shift with regard to both height/width axes in the picture, meaning that in the Fourier domain it transforms into
<div>
$$\mathcal{F} \lbrace W(I_t,\theta) \rbrace = \mathcal{F} \lbrace I(x-\tau_x, y-	\tau_y) \rbrace = e^{-j\omega \phi}*\mathcal{F} \lbrace I \rbrace$$ 
</div>
with $\phi = \frac{\tau_x}{W}+\frac{\tau_y}{H}$ for an image I of dimensions $H \times W$. Now let's plug this back into our original equation, using the fact that 
 <div>
    $$
    W^t(I_t,\theta) = I_t(x-t 	\tau_x, y-t 	\tau_y) \rightarrow \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace = e^{-j\omega t \phi}*\mathcal{F} \lbrace I_t \rbrace
    $$
 </div>
 Now then plugging back into the original equation we get 
 <div>
    $$
    \mathcal{F}\lbrace \overline{I} \rbrace \overset{\text{definition}} = 
    \frac{1}{T}\sum_{t=0}^{T-1} \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace = 
    \frac{1}{T}\sum_{t=0}^{T-1} e^{-j\omega t\phi}*\mathcal{F} \lbrace I_t \rbrace \rbrace
    $$
 </div>

Now if we model 

<div>
$$I_t(x, y) = I(x + t\tau_x^*, y + t\tau_y^*)$$
</div>

for some ground truth motion vector $\tau^* = \begin{bmatrix} \tau_x^* \\ \tau_y^* \end{bmatrix}^T $, then as previously done we have
<div>
$$\mathcal{F} \lbrace W^t(I_t,\theta) \rbrace = e^{-j\omega t\phi}*\mathcal{F} \lbrace I_t \rbrace = 
e^{-j\omega t\phi}*e^{j\omega t\phi^*}\mathcal{F} \lbrace I \rbrace = 
e^{-j\omega t\Delta\phi} *\mathcal{F} \lbrace I \rbrace
$$ 
</div>
where $ \Delta\phi = \frac{\tau_x - \tau_x^* }{W} + \frac{\tau_y - \tau_y^* }{H} $, meaning the resulting phase shift represents the displacement between the estimated motion vector and the ground truth.

Next, if we plug this in to our Fourier-domain objective we finally obtain the following closed-form 
 <div>
    $$
    \mathcal{F}\lbrace \overline{I} \rbrace \overset{\text{definition}} = 
    \frac{1}{T}\sum_{t=0}^{T-1} e^{-j\omega t(\frac{    \tau_x}{W}+\frac{   \tau_y}{H})}*\mathcal{F} \lbrace I_t \rbrace \rbrace
    $$
 </div>