### GCC-PHAT for noisy signal sequences
Suppose that we are working with a video consisting of *noisy* frames, where the noise is static (we will see later what and how this has to do with occlusion). 
This means that we model each noisy frame as $I_t = W^t(I_0, \tau^*) + V$, with V representing the constant noise mask. 
Now, we want to estimate a cohesive-translation motion model (same translation between each pair of frames) over this video. 

A naive approach would be to compute phase-correlation between a given pair of images. Note that for *any* such pair some variant of GCC-PHAT would yield a translation of $\tau=0$ (why?).
Instead, we can use our knowledge from this [previous blogpost](https://ikavodo.github.io/optimization_pt-3) regarding the moving-average filter (specifically that it is *optimal* for denoising) to integrate our video into a *pair* of integrated images, and then use a variant of GCC-PHAT over this pair!

We obtain a pair of integrated images by partitioning our video into even and odd frame subsets, and then compute integrated images in the following way:
<div>
$$
I_{even} = \frac{2}{N-1}\sum_{t=2m}^{N-1} W^t(I_t, \tau) = \frac{2}{N-1}\sum_{t=2m}^{N-1} e^{-j\omega t\phi} \cdot (e^{-j\omega t\phi^*}  \mathcal{F} \lbrace I_0 \rbrace + \mathcal{F} \lbrace V \rbrace) \\ 
= \frac{2}{N-1}(\sum_{m=0}^{\frac{N-1}{2}} e^{-j\omega 2m\Delta \phi} \mathcal{F} \lbrace I_0 \rbrace + \sum_{m=0}^{\frac{N-1}{2}} e^{-j\omega 2m\phi} \mathcal{F} \lbrace V \rbrace) = \left( \mathcal{H_{\frac{N}{2}}}(\Delta \phi) \cdot \mathcal{F} \lbrace I_0 \rbrace + \mathcal{H_{\frac{N}{2}}}(\phi) \cdot \mathcal{F} \lbrace V \rbrace \right)
$$
</div>
where $\phi = \frac{\tau}{W}, \quad \Delta \phi = \frac{\tau - \tau^*}{W}$ and
   $ \mathcal{H_{\frac{N}{2}}}(\phi)$ is a moving-average filter of order $\frac{N}{2}$ (see [previous blog-post](https://ikavodo.github.io/optimization_pt-3/)) with frequency responses parameterized by $\phi$.

$I_{odd}$ is constructed similarly over frames with odd time-steps, with the only exception 
<div>
    $$
    I_{odd} = \frac{2}{N-1}\sum_{t=2m+1}^{N-1} W^{t-1}(I_t, \tau) = ...
    $$
</div> 
Meaning that all odd-frames are mapped translated back to the *reference odd frame* (why we do it this way will become clear soon).

Note that of the two moving-average filters derived in the equation, $\mathcal{H_{\frac{N}{2}}}(\Delta \phi)$ depends on the ground-truth shift, while $\mathcal{H_{\frac{N}{2}}}(\phi)$ doesn't, meaning that noise reduction is *independent* of the ground-truth shift. On the other hand, for 'zero-motion' ($\tau=0$) noise energy is maximised, which creates a *spurious* (false) maxima in our optimization problem. This is the reason why computing phase correlation between any pair of noisy images doesn't work in this case! 

Now coming back to our integrated images, note that 
<div>
    $$
    I_{odd} = e^{-j\omega \phi^*} \cdot I_{even}
    $$
</div>

From here computing GCC-PHAT is straightforward, where we have  

<div>
    $$
    \frac{I_{odd} \cdot \overline{I_{even}}}{|I_{odd} \cdot \overline{I_{even}}|^\alpha} = \frac{e^{-j\omega \phi^*} I_{even} \cdot \overline{I_{even}}}{|e^{-j\omega \phi^*} I_{even} \cdot \overline{I_{even}}|^\alpha} = \frac{ e^{-j\omega \phi^*}|I_{even}|^2}{|I_{even}|^{2\alpha}} =  |I_{even}|^{2(1-\alpha)}e^{-j\omega \phi^*} 
    $$
</div> 
plugging in $\alpha=0.5$ we get

<div>
    $$
    |I_{even}|e^{-j\omega \phi^*} = |\mathcal{H_{\frac{N}{2}}}(\Delta \phi) \cdot \mathcal{F} \lbrace I_0 \rbrace + \mathcal{H_{\frac{N}{2}}}(\phi) \cdot \mathcal{F} \lbrace V \rbrace| * e^{-j\omega \phi^*} \approx |\mathcal{H_{\frac{N}{2}}}(\Delta \phi) \cdot \mathcal{F} \lbrace I_0 \rbrace + \frac{\mathcal{F} \lbrace V \rbrace}{\sqrt{\frac{N}{2}}}| * e^{-j\omega \phi^*}
    $$
</div>
Using the fact that the moving-average filter noise reduction is approximately equal to a factor of the square-root of the order of the filter (see explanation elsewhere).

Now as N grows we have  
<div>
    $$
    \lim_{N \to +\infty} |\mathcal{H_{\frac{N}{2}}}(\Delta \phi) \cdot \mathcal{F} \lbrace I_0 \rbrace + \frac{\mathcal{F} \lbrace V \rbrace}{\sqrt{\frac{N}{2}}}| * e^{-j\omega \phi} = |\mathcal{H_\infty}(\Delta \phi) \cdot \mathcal{F} \lbrace I_0 \rbrace| * e^{-j\omega \phi}
    $$
</div>
Meaning that the effect of the noise-component becomes negligable compared to that of the signal, meaning we have successfully found a GCC-PHAT informed algorithm to compute shifts between noisy frames!   
