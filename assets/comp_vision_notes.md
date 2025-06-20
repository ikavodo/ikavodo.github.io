
---

# **Computer Vision Notes (Aalto)**  

---

## **1. Camera Calibration & Projective Geometry**  
### **Intrinsic Camera Matrix**  
\[
K = \begin{bmatrix}
f & s & u_0 \\
0 & a f & v_0 \\
0 & 0 & 1
\end{bmatrix}
\]  
- **Parameters**:  
  - \(f\): Focal length  
  - \(s\): Skew (non-rectangular pixels)  
  - \((u_0, v_0)\): Principal point  
  - \(a\): Aspect ratio  

### **Homogeneous Coordinates**  
- **Projective transformations** have **8 degrees of freedom (DoF)** because scaling is irrelevant:  
  \[
  c \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} \equiv \begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix}
  \]  
- **Parallel lines** intersect at infinity in projective space.  

---

## **2. Feature Detection & Matching**  
### **Harris Corner Detection**  
1. Compute gradients \(I_x\), \(I_y\) (using Sobel filters).  
2. Construct second-moment matrix \(M\):  
   \[
   M = \begin{bmatrix}
   I_x^2 & I_x I_y \\
   I_x I_y & I_y^2
   \end{bmatrix}
   \]  
3. Corner response:  
   \[
   R = \det(M) - k \cdot \text{trace}(M)^2
   \]  
   - **Eigenvalues**:  
     - \(\lambda_1 \gg \lambda_2\): Edge  
     - \(\lambda_1 \approx \lambda_2\) (large): Corner  
     - Both small: Flat region  

### **SIFT Descriptors**  
- **128-dimensional vector** per keypoint:  
  - Divide **16×16 neighborhood** into **4×4 sub-patches**.  
  - Compute **8-bin orientation histograms** per sub-patch.  
- **Matching**: Use **NNDR** (Nearest Neighbor Distance Ratio):  
  \[
  \text{NNDR} = \frac{\text{distance to 1st NN}}{\text{distance to 2nd NN}} \leq 0.8
  \]  

---

## **3. Optical Flow & Motion Estimation**  
### **Lucas-Kanade Method**  
- **Assumptions**:  
  1. Brightness constancy.  
  2. Small motion between frames.  
  3. Spatial coherence (local pixels move similarly).  
- **Equation**:  
  \[
  \begin{bmatrix}
  I_x & I_y
  \end{bmatrix}
  \begin{bmatrix}
  u \\ v
  \end{bmatrix}
  = -I_t
  \]  
  - Solved via **least squares** (normal equations).  

### **Aperture Problem**  
- Ambiguity in motion direction when only **edge information** is available.  

---

## **4. RANSAC & Model Fitting**  
### **RANSAC Algorithm**  
1. **Randomly sample** minimal points (e.g., 4 for homography).  
2. **Fit model** (e.g., line, homography).  
3. **Count inliers** (points within threshold \(t\)).  
4. **Refit model** using all inliers.  

- **Threshold \(t\)**:  
  \[
  t^2 = 3.84 \sigma^2
  \]  
- **Number of iterations \(N\)**:  
  \[
  N = \frac{\log(1 - p)}{\log(1 - (1 - e)^s)}
  \]  
  - \(p\): Desired success probability (e.g., 0.99).  
  - \(e\): Outlier ratio.  

---

## **5. Hough Transform**  
### **Line Detection**  
1. **Edge detection** (e.g., Canny).  
2. **Vote in \((\theta, \rho)\) space**:  
   - Each edge point votes for all lines passing through it.  
   - Peaks in Hough space = detected lines.  

---

## **6. Triangulation & 3D Reconstruction**  
### **Triangulation Equations**  
Given two camera matrices \(P_1\), \(P_2\) and corresponding points \(x_1\), \(x_2\):  
\[
x_1 \times (P_1 X) = 0, \quad x_2 \times (P_2 X) = 0
\]  
- Solved via **SVD**.  

### **Bundle Adjustment**  
- **Non-linear optimization** to refine:  
  - **Structure** (3D points \(X\)).  
  - **Motion** (camera matrices \(P_i\)).  

---

## **7. Deep Learning for Vision**  
### **CNN Basics**  
- **Pooling**: Reduces dimensionality (max/average pooling).  
- **Softmax + Cross-Entropy Loss**:  
  \[
  \mathcal{L} = -\sum t_i \log(p_i)
  \]  

### **Region Proposal Networks (RPN)**  
- Proposes **bounding boxes** for object detection.  

---

## **References & Resources**  
1. [Visualizing Linear Transformations (Geogebra)](https://www.geogebra.org/m/YCZa8TAH)  
2. [RANSAC Lecture Notes (PSU)](https://www.cse.psu.edu/~rtc12/CSE486/lecture15_6pp.pdf)  
3. [Homogeneous Coordinates (Song Ho)](http://www.songho.ca/math/homogeneous/homogeneous.html)  

---