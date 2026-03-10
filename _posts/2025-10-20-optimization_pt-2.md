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


## Linear operators
We begin our deep dive into the world of Fourier operators with the observation that most of the operations we've seen within our algorithmic framework are *linear*. For a brief recap on this, recall that a linear operator T over a vector space is defined by 
<div>
$$
T(\alpha_1 x_1 + \alpha_2 x_2) = \alpha_1 T(x_1) + \alpha_2 T(x_2)
$$
</div>
Linear operators have all kinds of very nice properties, such as the fact that a composition of two linear transformations $(T_2 \circ T_1)(x) = T_2(T_1(x))$ is itself linear. Recall that we can always represent linear transformations T1, T2 over a vector in matrix form via matrix-vector multiplication. What is the implication of this for representating the composition $T_2 \circ T_1$ in matrix form? Which matrix operation becomes "equivalent" (isomorphous) to the composition of linear transformations?

### Parametric motion and linearity
Let's now take the rather abstract mathematical concept of linearity and connect it back to the objects we are working with, which are different motion models. We can represent these by composing linear operators, meaning by multiplying matrices representing the individual motion operations. For the case of 2D translation we have the rather simple
<div>
$$
T(p) = p + v
$$
</div>

where $p = \begin{bmatrix} x \\ y \end{bmatrix}^T$ is a 2D vector of pixel coordinates, and v a fixed 2D velocity vector representing the direction in which the pixel p is displaced at each timestep t. We can represent this in matrix form via   
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
where p is represented in [homogeneous coordinates](https://en.wikipedia.org/wiki/Homogeneous_coordinates), and the matrix T has *two* degrees of freedom, representing the 2D motion model transformation.

As previously explained, we can add motion parameters to obtain more complicated motion, represented by a transformation with *more* degrees of freedom. As a result of the linearity of the motion transformation, the matrix is most easily represented as a *composition* of matrices representing the different motion parameter components. It is worthwhile then to *decompose* the motion transformation into the different matrix components, as we do in the next example, which represents a 3DoF rotation motion model: 
<div>
$$R_{\theta}(p) = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & 0 \\ \sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} 1 & 0 & v_x \\ 0 & 1 & v_y \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} x \\ y \\ 1 \end{bmatrix} = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & \cos(\theta)\cdot v_x -\sin(\theta)\cdot v_y \\ \sin(\theta) & \cos(\theta) & \sin(\theta)\cdot v_x + \cos(\theta)\cdot v_y \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$
</div>

Note that the composition 'rotates' the translation vector in the direction of rotation. What happens if we change the order of operations?

<div>
$$R'_{\theta} = \begin{bmatrix} 1 & 0 & v_x \\ 0 & 1 & v_y \\ 0 & 0 & 1 \end{bmatrix} \cdot \begin{bmatrix} \cos(\theta) & -\sin(\theta) & 0 \\ \sin(\theta) & \cos(\theta) & 0 \\ 0 & 0 & 1 \end{bmatrix} = \begin{bmatrix} \cos(\theta) & -\sin(\theta) & v_x \\ \sin(\theta) & \cos(\theta) & v_y \\ 0 & 0 & 1 \end{bmatrix} \neq R_{\theta}
$$
</div>

Meaning that the two operations are not commutative (think about the difference between translating an image and then rotating it, vs. rotating it and then translating). Which of the two operators $R_{\theta}, R'_{\theta}$ is a more "sensible" choice for a parametric motion model, in the sense that it describes how objects move in the world (think of a wheel in motion)?  

Follow-up question: how can we obtain matrix representations of similarity (4DoF) and affine (6DoF) transformations? (*Hint*: see [this](https://math.stackexchange.com/questions/2866077/degrees-of-freedom-in-affine-transformation-and-homogeneous-transformation))

Now that we understand how to represent motion transformations as linear compositions of relatively simple linear operators, we can leverage this to apply these different operators in the *Fourier* domain. First, let's get some context as to why we would want to do this in the first place.

### Spatial vs. Fourier-domain operators
Why compute certain mathematical operations in the Fourier domain? The simplest answer has to do with the notion of *duality* between operators with regard to the two domains (see [first](https://ikavodo.github.io/fourier-transform-tutorial-pt-1/) [and second](https://ikavodo.github.io/fourier-transform-tutorial-pt-2/) blogposts). If one of two dual operators is more efficient to compute, then naturally its relevant domain is the better one within which to do the computation, given that we can transform to that domain 'fast enough' with respect to the order of complexity of the original problem  (does it make sense to transform to the Fourier domain to compute the *power* of a signal? Why not?). 

For example, if we want to compute a convolution between two signals $s_1 \circledast s_2 $, we can use the duality $\circledast \overset{\text{FT}}{\longleftrightarrow} \times$ together with a fast transform algorithm such as [FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform) to compute the convolution as multiplication in the Fourier domain, finally transforming back to get the desired result. Somewhat surprisingly, for long enough signals $s_1 s_2$, this would actually *be faster* than simply performing the convolution in the initial domain.  

Next, why compute *our* specific motion-computation algorithm in the Fourier domain? This will hopefully become more clear in a bit, and it has to do with two different facets, the first of which relates to speed and computational-efficiency, and the second (and more important) one to utilizing *additional* Fourier-domain-based transforms and algorithms in order to *simplify* various motion models. Let's first understand why the Fourier transform is a 'good-fit' for our objective function in the first case, and how representing it in the Fourier domain in fact makes it *more interpretable*, as well as gives additional perspective about the problem.

### The Fourier transform as a linear operator
A bit of mathematical background as justification: we begin with the observation that the Fourier transform $\mathcal{F}\lbrace T \rbrace$ of a function $T(x)$ is a *linear* operator (prove this! It's straightforward). This basically means that if we can represent our objective as a composition of "simple" linear operators, then the linearity of the Fourier transform ensures that the equivalent objective in the Fourier domain (namely the composition of equivalent Fourier operators) remains equally "simple". This will become clear soon.

*Note*: there is an operator within our objective function which is *not* linear, but rather *bi*linear. This is the interpolation operator used for frame warping (see [this](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.grid_sample.html)). We will get back to this operation later, ignoring it at the moment for simplicity's sake.

Let's show how the linearity of the Fourier Transform comes into play, reminding ourselves first of our objective function: 

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

The equivalent Fourier operator for our warped-frame integration operator $\overline{I}$ becomes then (solely on the basis of linearity): 

<div>
$$
\mathcal{F}\lbrace \overline{I} \rbrace \overset{\text{definition}}= 
\mathcal{F} \lbrace \frac{1}{T}\sum_{t=0}^{T-1} W^t(I_t,\theta) \rbrace \overset{linearity}= 
\frac{1}{T}\sum_{t=0}^{T-1} \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace
$$
</div>

Which looks simple enough already! It remains to become clear how we can *explicitly* write the operator $\mathcal{F} \lbrace W^t(I^t,\theta) \rbrace$.

### Integration of warped frames: a Fourier-domain formulation

Let's express the integrated image now in terms of equivalent Fourier-domain operators. Recall the duality previously introduced in the [first]() blogpost.
We had 
<div>
$$x[n-n_0]\overset{\text{FT}}{\leftrightarrow}e^{-j\omega n_o}\cdot X(e^{j\omega})$$,
</div>
Meaning that in 1D a shift in the time/spatial domain is equivalent to a phase shift in the frequency domain.
Now suppose that we are working with a 2D (translation) parametric motion model, meaning that 
$W(I,\theta) = I(x- \tau_x, y-\tau_y)$ where $ \theta = \begin{bmatrix} \tau_x \\ \tau_y \end{bmatrix}^T $. In the Fourier domain this transforms then into
<div>
$$\mathcal{F} \lbrace W(I_t,\theta) \rbrace = \mathcal{F} \lbrace I(x-\tau_x, y-	\tau_y) \rbrace = e^{-j\omega \phi}\cdot \mathcal{F} \lbrace I \rbrace$$ 
</div>
with $\phi = \frac{\tau_x}{W}+\frac{\tau_y}{H}$ for an image I of dimensions $H \times W$. Now let's plug this back into our original equation, using the fact that 

<div>
$$
W^t(I_t,\theta) = I_t(x-t 	\tau_x, y-t 	\tau_y) \rightarrow \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace = e^{-j\omega t \phi}\cdot \mathcal{F} \lbrace I_t \rbrace
$$
</div>
plugging back into the original equation we get 
<div>
$$
\mathcal{F}\lbrace \overline{I} \rbrace \overset{\text{definition}} = 
\frac{1}{T}\sum_{t=0}^{T-1} \mathcal{F} \lbrace W^t(I_t,\theta) \rbrace \overset{\text{shift theorem}}= 
\frac{1}{T}\sum_{t=0}^{T-1} e^{-j\omega t\phi}\cdot \mathcal{F} \lbrace I_t \rbrace \rbrace
$$
</div>

Now if we model 

<div>
$$I_t(x, y) = I(x + t\tau_x^*, y + t\tau_y^*)$$
</div>

for some ground truth motion vector $\theta^* = \begin{bmatrix} \tau_x^* \\ \tau_y^* \end{bmatrix}^T $, then continuing to simplify our previous expression we get
<div>
$$\mathcal{F} \lbrace W^t(I_t,\theta) \rbrace = e^{-j\omega t\phi}\cdot \mathcal{F} \lbrace I_t \rbrace = 
e^{-j\omega t\phi}\cdot (e^{j\omega t\phi^*}\mathcal{F} \lbrace I \rbrace) = 
e^{-j\omega t\Delta\phi} \cdot \mathcal{F} \lbrace I \rbrace
$$ 
</div>
where $ \Delta\phi = \phi - \phi^* = \frac{\tau_x - \tau_x^* }{W} + \frac{\tau_y - \tau_y^* }{H} $, meaning the resulting phase shift represents the displacement between the estimated motion vector and the ground truth.

Next, if we plug this in to our Fourier-domain objective we finally obtain the following closed-form 
<div>
$$
\mathcal{F}\lbrace \overline{I} \rbrace = 
\frac{1}{T}\sum_{t=0}^{T-1} e^{-j\omega t\Delta\phi} \cdot \mathcal{F} \lbrace I \rbrace = \frac{\mathcal{F} \lbrace I \rbrace}{T}\sum_{t=0}^{T-1} e^{-j\omega t\Delta\phi} \overset{\text{geometric sum}}= 
\mathcal{F} \lbrace I \rbrace \cdot \frac{1-e^{-j\omega T \Delta\phi}}{T(1-e^{-j\omega\Delta\phi})}
$$
</div>
**Whew**! What do we have here? It seems that we are multiplying the scaled Fourier-representation of the original reference frame by a rational, complex function, the numerator and denominator of which are both polynomials in the same complex number. To better understand the behavior of this function let's simplify each of these polynomials by replacing $z = e^{-j\omega\Delta\phi}$, thus obtaining the following *transfer function*
<div>
$$
H(z)=\frac{1−z^T}{T(1-z)}
$$
</div> 
This is known as a *moving average filter* (this makes sense!). We will get back to it in the next blog-post, and understand just what exactly it does. Until then, let's complete the Fourier-domain formulation of our optimization objective.


### Variance: a Fourier-domain formulation
The variance operator can be defined over a random variable $X$ via 
<div>
$$
\mathrm{Var}\!\left(X\right) = \mathbb{E}(X^2) - \mathbb{E}(X)^2
$$
</div> 
Now for an image I of dimensions $H \times W$ we can use the sample mean to represent the expectation
<div>
$$
\mathbb{E}(I) = \frac{1}{HW} \sum_{x=0}^{W-1}\sum_{y=0}^{H-1} I(x, y)
$$
</div> 
Note that 
<div>
$$ 
 \sum_{x=0}^{W-1}\sum_{y=0}^{H-1} I(x, y) = \sum_{x=0}^{W-1}\sum_{y=0}^{H-1} I(x, y)\cdot e^{-2\pi j0} 
 = \mathcal{F}_{0, 0} \lbrace{I} \rbrace 
$$
</div>

Meaning we can represent the expectation term $\mathbb{E}(X)$ via the DC-component of the signal.

Next, Parseval's theorem states 
<div>
$$
\sum_{x=0}^{W-1}\sum_{y=0}^{H-1} |I(x, y)|^2 = \frac{1}{MN} \sum_{m=0}^{M-1}\sum_{n=0}^{N-1} |\mathcal{F} \lbrace{I} \rbrace(m, n)|^2
$$
</div>
Meaning that signal energy is retained between the two domains (up to a scalar).

We have then the necessary representations for computing variance in the Fourier domain! More specifically we get 
<div>
$$
\mathcal{F} \lbrace{\mathrm{Var}\!\left(I\right)} \rbrace  \propto \sum_{m=0}^{M-1}\sum_{n=0}^{N-1} (|\mathcal{F} \lbrace{I} \rbrace(m, n)|^2) - |\mathcal{F}_{0, 0} \lbrace{I} \rbrace| ^2 = 
\sum_{(m, n) \neq (0, 0)} |\mathcal{F} \lbrace{I} \rbrace(m, n)|^2 
$$
</div> 
Meaning that in the Fourier domain variance is equivalent to the signal energy minus the squared DC-component. Surprisingly straightforward!

Now putting everything together we have our Fourier objective
<div>
$$
\mathcal{F} \lbrace {f_{\text{obj}}} \rbrace = \sum_{(m, n) \neq (0, 0)} |\mathcal{F}\lbrace \overline{I} \rbrace (m, n)|^2 
$$
</div>

Where we plug in for $\mathcal{F}\lbrace \overline{I} \rbrace $ the previously computed closed analytical form.
Let's see this now in action.

## Computation in the Fourier-domain in practice
We begin by addressing the first of our previously stated motivations for Fourier-domain computation: that of more efficient computation time.
We saw previously that to obtain a closed form for $\mathcal{F}\lbrace \overline{I} \rbrace $ we need to specify an *explicit* displacement quantity $\Delta\phi = \phi^* - \phi$, which demands our knowing the value of the ground-truth shift. We can bypass this issue by modeling the objective (variance of the integrated image) as a function *purely* of $\Delta\phi$, rather than of the unknown ground-truth shift. This changes our model, in the sense that we don't *need* an input video generated with some unknown shift, but rather generate this video ourselves as a function of the input displacement (can you see why? Note that translation is a group operation, meaning that the composition of shifts is a shift). 
<!-- Note that we obtain maximal variance at $\Delta\phi = 0$,   -->

Let's clarify this with some code. 
Note that for the sake of "fairness" we compute shifts in the spatial-domain using torch.roll(), which is more computationally efficient than torch.grid_sample() (Recall that the latter uses interpolation, which increases computation but adds differentiability).The former is *non-differentiable* (why?), but this doesn't matter too much at the moment, as we are only interested in the computation time of our objective function, rather than in gradient backpropagation.


```python
import torch
import torch.nn.functional as F

def create_motion_vids(frames, T, shifts): 
"""
Create motion videos of length T from batch of input frames, which are successively shifted using shifts.
Impemented using torch.roll()-> non-differentiable (can't use autograd)
"""
if frames.ndim == 3: 
    frames.unsqueeze(1)

B, _, H, W = frames.shape 
if shifts.shape[0] != B: 
    raise AssertionError("Dimensions of shifts must match batch size.") 
motion_vids = torch.zeros(B, T, H, W) 
for i in range(B): 
    for j in range(T): 
        cur_frame = frames[i] if frames.shape[1] == 1 else frames[i, j] 
        dy, dx = tuple(shifts[i] * j)  
        # Roll image along specified axes using shifts
        motion_vids[i, j, ...] = torch.roll(cur_frame, shifts=(dx, dy), dims=(-2, -1)) 

return motion_vids

def spatial_pipeline(frames: torch.Tensor, T: int, shifts: torch.Tensor, dims = (-2, -1)):
"""
Pipeline implemented in spatial domain
"""
motion_vids = create_motion_vids(frames, T, shifts)
integrated = motion_vids.mean(dim=1).unsqueeze(1)
variance = integrated.var(dim=dims)
return integrated, variance
```    

Next we implement our Fourier-domain objective as previously described. 

```python
def fourier_pipeline(frames: torch.Tensor, T: int, shifts: torch.Tensor, dim=(-2, -1), eps=1e-12, fourier_input=False):
"""
Pipeline implemented in Fourier domain
"""
if frames.ndim == 3:
    frames = frames.unsqueeze(1)  # Ensure x has a channel dimension (B, 1, H, W)

B, _, H, W = frames.shape
if shifts.shape[0] != B:
    raise AssertionError("Dimensions of shifts must match batch size.")

# Use Fourier-representation as input for more efficient computation, otherwise compute Fourier transform of input
X = torch.fft.fft2(frames, norm='forward', dim=dim) if not fourier_input else frames

# Create frequency grids (u, v)
dtype = X.real.dtype

# Frequency grids
v, u = torch.meshgrid(
    torch.arange(H, device=X.device, dtype=dtype),
    torch.arange(W, device=X.device, dtype=dtype),
    indexing='ij'
)

# Expand shifts for broadcasting
shifts_expanded = shifts.view(B, 1, 1, 2)  # (B, 1, 1, 2)

# Compute normalized frequency * shift
omega = (u.unsqueeze(0) * shifts_expanded[..., 0] / W +
         v.unsqueeze(0) * shifts_expanded[..., 1] / H)  # (B, H, W)

if omega.ndim < X.ndim:  # add channel dim if needed
    omega = omega.unsqueeze(1)

r = torch.exp(-2j * torch.pi * omega)  # complex exponent

# Compute numerator and denominator
numerator = 1 - r**T
denominator = 1 - r

# Differentiable masking for r ≈ 1
mask = torch.abs(denominator) < eps
denominator_safe = torch.where(mask, torch.ones_like(denominator), denominator)
numerator_safe = torch.where(mask, torch.ones_like(numerator), numerator)

geo_sum = numerator_safe / denominator_safe
geo_sum = torch.where(mask, torch.tensor(1., device=X.device) * T, geo_sum)

summed_fft = X * geo_sum
integrated_fft = summed_fft/T
    
# Compute squared magnitude |X|^2
mag2 = integrated_fft.real.square() + integrated_fft.imag.square()
# Sum over all frequency bins
total_power = mag2.sum(dim=dim)
dc_power = mag2[...,0,0]
variance_fft = total_power - dc_power
return integrated_fft, variance_fft
```

Quick sanity check that the spatial and Fourier domain implementations yield the same value:
```python

# image dimensions
B = 2  # Batch size
H, W = 128, 128  # Image dimensions
T = 5  # Number of frames in motion video

SHIFT_SCALE = max(H, W)//(5*T*B) # Use this to set up a margin for movement within the video

# comparison params
atol = 1e-4 #close enough for variance checks, can be set to 1e-4 for almost all purposes in this notebooks

# Define shifts (for example, shift by (5, 3) for each sample in the batch)
shifts = (torch.arange(-B, B).reshape(B,2)) * SHIFT_SCALE # shape (B, 2)
image_dims = B, H, W

# Implemented this in previous blog-post
frames, _ = make_image(image_dims)

# Both pipelines
integrated_spatial, var_spatial = spatial_pipeline(frames, T, shifts)
integrated_fourier, var_fourier = fourier_pipeline(frames, T, shifts)

assert torch.allclose(var_spatial, var_fourier, atol=atol), "Domain implementations don't yield same result"
```

All quiet on the western front.

Now that we have shown that the two are equivalent, we can compare their computation times. For longer, high-res videos we can *expect* an increase in computationally efficiency in the Fourier domain computation (Why? *Hint*: recall the closed-form geometric sum term in the formulation of $\mathcal{F}\lbrace \overline{I} \rbrace$).


```python
# higher-res videos for benchmarking
frames_high_res = torch.rand(B, 1, 1024, 1024)

# Processing time scales with number of frames in video
T_long = 64

print('spatial pipeline processing time: ')
%timeit spatial_pipeline(frames_high_res, T_long, shifts)

# pre-compute Fourier transforms for faster processing
frames_fourier_high_res = torch.fft.fft2(frames_high_res, norm='forward', dim=(-2, -1))
print('fourier pipeline processing time: ')
%timeit fourier_pipeline(frames_fourier_high_res, T_long, shifts, fourier_input=True) 
```
```bash
spatial pipeline processing time: 
122 ms ± 9.7 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
fourier pipeline processing time: 
46.7 ms ± 1.71 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
```

It seems that the Fourier domain implementation is ~2.5 times faster than the spatial domain implementation. Not too bad!

Next time, we'll deal with the actual optimization procedure in the Fourier domain, and adddress some problems which come up, learning something in the process. 
