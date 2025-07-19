# 微分定义

有矩阵 $\mathbf{A} = [\mathbf{a}_1, \mathbf{a}_2, \cdots, \mathbf{a}_m]{\top} \in \mathbb{R}^{m \times n}$ 和向量 $\mathbf{x} = [x_1, x_2, \cdots, x_n]{\top} \in \mathbb{R}^{n}$，则有：

$$
\mathbf{Ax} = \begin{bmatrix}
   \langle \mathbf{a}_1, \mathbf{x} \rangle\\
   \langle \mathbf{a}_2, \mathbf{x} \rangle\\
   \vdots \\
   \langle \mathbf{a}_m, \mathbf{x} \rangle
\end{bmatrix}
$$

## 向量值函数的导数

令 $\mathbf{f}: \mathbb{R}^n \rightarrow \mathbb{R}^m$，则梯度记作：

$$
\nabla_{\mathbf{x}} \mathbf{f(x)} = \bigg[\frac{\partial \mathbf{f(x)}}{\partial x_1}, \frac{\partial \mathbf{f(x)}}{\partial x_2}, \ldots, \frac{\partial \mathbf{f(x)}}{\partial x_n}\bigg]
$$

若有 $\mathbf{y} = [y_1, y_2, \ldots, y_m]^\top$，$x \in \mathbb{R}$，则：

$$
\frac{\partial \mathbf{y}}{\partial x} = \bigg[\frac{\partial y_1}{\partial x}, \frac{\partial y_2}{\partial x}, \ldots, \frac{\partial y_m}{\partial x}\bigg]^\top
$$

还有，

$$
\frac{\partial \mathbf{y}}{\partial \mathbf{x}} = \bigg[\frac{\partial y_1}{\partial \mathbf{x}}, \frac{\partial y_2}{\partial \mathbf{x}}, \ldots, \frac{\partial y_m}{\partial \mathbf{x}}\bigg]^\top = \begin{bmatrix} \frac{\partial y_1}{\partial x_1} & \frac{\partial y_1}{\partial x_2} &\cdots &\frac{\partial y_1}{\partial x_n} \\
\frac{\partial y_2}{\partial x_1} & \frac{\partial y_2}{\partial x_2} & \cdots & \frac{\partial y_2}{\partial x_n}\\
\vdots & \vdots & \ddots & \vdots \\
\frac{\partial y_m}{\partial x_1} & \frac{\partial y_m}{\partial x_2} & \cdots & \frac{\partial y_m}{\partial x_n}
\end{bmatrix}
$$

可以记作：$\mathbf{f^{'}(x)}$ 或者 $\mathbf{D} \mathbf{f(x)}$。容易推出：

$$
\nabla_\mathbf{x} \mathbf{f(x)} = \mathbf{f^{'}(x)}^{\top}\\
$$

### 例1 计算：$\nabla_{\mathbf{x}} ||\mathbf{x}||^2$

因为，

$$
\begin{align}
\mathbf{d} ||\mathbf{x}||^2 &= 
\mathbf{d} \langle \mathbf{x}, \mathbf{x} \rangle\\
&=
\mathbf{d} \sum_{i=1}^n x_i^2\\
&=
\sum_{i=1}^n \mathbf{d} x_i^2\\
&=
2 \sum_{i=1}^n x_i \mathbf{d} x_i\\
&=
2 \mathbf{x}^{\top} \mathbf{d} \mathbf{x}\\
\end{align}
$$

所以，$\nabla_{\mathbf{x}} ||\mathbf{x}||^2 = 2 \mathbf{x}$

### 拓展

可以借助**内积**运算简化求解过程，比如：

$$
\begin{align}
\mathbf{d} ||\mathbf{x}||^2 &=
\langle \mathbf{d} \mathbf{x}, \mathbf{x} \rangle + \langle \mathbf{x}, \mathbf{d} \mathbf{x} \rangle\\
&= \langle 2 \mathbf{x}, \mathbf{d} \mathbf{x} \rangle\\
&= \langle \nabla_{\mathbf{x}} ||\mathbf{x}||^2, \mathbf{dx} \rangle
\end{align}
$$