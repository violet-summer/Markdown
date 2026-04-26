---
title: 工科数学分析的复习
published: 2025-05-13
description: 工数的二次复习，重点为试卷，支援期中考试和期末
tags:
  - math
  - review
category: course
draft: true
image: /violet.png
---

# 叙述定义

## 小概念

### 聚点（Limit Point）

设 $D$ 是平面或空间中的一个点集，$P_0$ 是某一点。如果 **任意邻域** 内都包含 $D$ 中 **无限多个** 不同于 $P_0$ 的点，则称 $P_0$ 为 $D$ 的聚点。

- **例子**：区间 $(0,1)$ 的聚点包括所有 $x \in [0,1]$，因为任意接近 $0$ 或 $1$ 的点都有无限多个其他点在其邻域内。  

### 孤立点（Isolated Point）

若 $P_0 \in D$，但存在某个邻域 **仅包含 $P_0$ 本身**，则称 $P_0$ 为 $D$ 的孤立点。 

- **例子**：点集 $\{0\} \cup \{\frac{1}{n} \mid n \in \mathbb{N}\}$ 中，$0$ 是聚点，而每个 $\frac{1}{n}$ 是孤立点。  

### 级数（Series）的定义与基本概念

#### 级数的定义

在数学中，**级数**是指将数列的各项依次相加所构成的**无限求和表达式**。一般形式为：  
$$
S = \sum_{n=1}^{\infty} a_n = a_1 + a_2 + a_3 + \cdots + a_n + \cdots
$$
其中：
- $a_n$ 称为级数的**通项**（或**一般项**），
- $S_n = a_1 + a_2 + \cdots + a_n$ 称为级数的**前 $n$ 项部分和**。

#### 级数的收敛与发散

- **收敛（Convergent）**：如果部分和数列 $\{S_n\}$ 的极限存在，即  
  $$
  \lim_{n \to \infty} S_n = S \quad (\text{有限值}),
  $$  
  则称级数 $\sum a_n$ **收敛**，$S$ 称为级数的**和**。  
- **发散（Divergent）**：如果 $\lim_{n \to \infty} S_n$ 不存在（如趋于无穷或振荡），则称级数**发散**。

#### 常见级数类型

| 级数类型 | 定义 | 例子 |
|----------|------|------|
| **常数项级数** | 通项 $a_n$ 为常数 | $\sum_{n=1}^{\infty} \frac{1}{n}$（调和级数） |
| **交错级数** | 通项符号交替变化 | $\sum_{n=1}^{\infty} (-1)^{n-1} \frac{1}{n}$（莱布尼茨级数） |
| **幂级数** | 形如 $\sum_{n=0}^{\infty} c_n x^n$ | $\sum_{n=0}^{\infty} \frac{x^n}{n!} = e^x$ |
| **傅里叶级数** | 用三角函数展开 | $f(x) = \frac{a_0}{2} + \sum_{n=1}^{\infty} (a_n \cos nx + b_n \sin nx)$ |

#### 判断级数收敛的方法

- **比较判别法**：与已知收敛/发散的级数对比（如 $p$-级数 $\sum \frac{1}{n^p}$）。  
- **比值判别法**：计算 $\lim_{n \to \infty} \left| \frac{a_{n+1}}{a_n} \right|$。  
- **积分判别法**：将级数转化为积分判断（适用于单调递减正项级数）。  
- **莱布尼茨判别法**：用于交错级数（见前文）。

#### **例子**  
- **收敛级数**：$\sum_{n=1}^{\infty} \frac{1}{n^2} = \frac{\pi^2}{6}$（巴塞尔问题）。  
- **发散级数**：$\sum_{n=1}^{\infty} \frac{1}{n}$（调和级数）。  



#### 交错级数（Alternating Series）

形如 $\sum_{n=1}^{\infty} (-1)^{n-1} a_n$（$a_n > 0$）的级数，其项正负交替出现。  

- **判别法（莱布尼茨）**：若 $a_n$ **单调递减** 且 $\lim_{n \to \infty} a_n = 0$，则级数收敛。  
- **例子**：$\sum_{n=1}^{\infty} (-1)^{n-1} \frac{1}{n}$ 收敛（但非绝对收敛）。  

#### 余项（Remainder）

级数 $\sum_{n=1}^{\infty} (-1)^{n-1} a_n$ 前 $n$ 项部分和为 $S_n$，则余项 $r_n = S - S_n$ 表示截断误差。 

- **估计**：若级数满足莱布尼茨条件，则 $|r_n| \leq a_{n+1}$（即下一项的绝对值）。  

## 二元函数的连续性

定义7.2.2 设 $z=f(x,y)$ 的定义域为 $D$，$P_0$ 是 $D$ 的聚点且 $P_0 \in D$。如果  

$$
\lim_{P \to P_0} f(P) = f(P_0),
$$
则称 $f(x,y)$ 在 $P_0 (x_0, y_0)$ 处连续，$(x_0, y_0)$ 为 $f(x,y)$ 的连续点。  用“$\epsilon$”的语言叙述，就是：$\forall \epsilon > 0$，$\exists \delta > 0$。当 $|| P - P_0 || < \delta$ 时，有

$$
|| f(P) - f(P_0) || < \epsilon.
$$
由上述定义可见，$P_0$ 是 $D$ 的孤立点时，上述条件也满足。因此我们约定：定义域 $D$ 中的孤立点都是函数的连续点。若 $f(x,y)$ 在 $D$ 的每一点都是连续的，则称 $f(x,y)$ 在 $D$ 连续，记作 $f \in C(D)$。

## 方向导数

定义7.5.1(方向导数) 设函数 $z=f(x,y)$ 在点 $P_0 (x_0, y_0)$ 处的邻域内有若干极限  

$$
\lim_{t \to 0} \frac{f(P_0 + t)}{t} = f(P_0)
$$

存在，则称它为 $f(x,y)$ 在点 $P_0$ 沿方向 $l$ 的方向导数，记作  

$$
\left. \frac{\partial f(P_0)}{\partial l} \right|_{P_0}
$$

$f(x,y)$ 在任意点 $P$ 沿方向 $l$ 的方向导数记作  

$$
   \left. \frac{\partial f(P)}{\partial l} \right|_{P_0}, \quad \text{或} \quad \left. \frac{\partial f}{\partial l} \right|_{P_0}.
$$

## Green公式

定理9.5.1 设 $D$ 是以分段光滑的曲线 $L$ 为边界的平面闭区域，函数 $P(x,y)$ 和 $Q(x,y)$ 在 $D$ 上具有一阶连续偏导数，则有公式  

$$
\iint\limits_{D} \left( \frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y} \right) dxdy = \oint\limits_{L} Pdx + Qdy,
$$

其中 $L$ 是 $D$ 的取正向的边界曲线。  

## 莱布尼茨判别法

定理10.3.1（莱布尼茨判别法） 设交错级数（10.3.1）满足条件

1. $a_n \geq a_{n+1}, n=1,2,\cdots;$  
2. $\lim_{n \to \infty} a_n = 0.$  

则级数收敛且对于余项 $r_n = \sum_{k=n+1}^{\infty} (-1)^{k-1}a_k$，有估计式
   
$$
|r_n| = \left| \sum_{k=n+1}^{\infty} (-1)^{k-1}a_k \right| \leq a_{n+1}.
$$





## 曲面积分
### 问题重述

计算曲面积分：

$$
I = \iint_{\Sigma} \frac{x \, dy dz + (z+1)^2 \, dx dy}{\sqrt{x^2 + y^2 + z^2}},
$$
其中 $\Sigma$ 是下半球面 $z = -\sqrt{1 - x^2 - y^2}$ 的上侧。

### 简化思路

题目提示这是一个简单的二重积分问题，因此我们尝试将曲面积分直接转化为 \(xy\)-平面上的二重积分。

#### 1. 曲面方程

下半球面的方程为：

$$
z = -\sqrt{1 - x^2 - y^2}, \quad x^2 + y^2 \leq 1.
$$

#### 2. 曲面积分转化为二重积分

曲面积分的一般形式为：
$$
\iint_{\Sigma} P \, dy dz + Q \, dz dx + R \, dx dy.
$$
对于曲面 \(z = z(x, y)\)，可以表示为：
$$
\iint_{\Sigma} R \, dx dy = \iint_{D} R(x, y, z(x, y)) \, dx dy,
$$
$$
\iint_{\Sigma} P \, dy dz = \iint_{D} P(x, y, z(x, y)) \left(-\frac{\partial z}{\partial x}\right) dx dy,
$$
其中 \(D\) 是曲面在 \(xy\)-平面的投影（这里是单位圆盘）。

#### 3. 计算各部分

- **\(R \, dx dy\) 部分**：

$$
  R = \frac{(z+1)^2}{\sqrt{x^2 + y^2 + z^2}} = \frac{\left(-\sqrt{1 - x^2 - y^2} + 1\right)^2}{1} = \left(1 - \sqrt{1 - x^2 - y^2}\right)^2.
$$
  因此：
$$
  \iint_{\Sigma} R \, dx dy = \iint_{D} \left(1 - \sqrt{1 - x^2 - y^2}\right)^2 dx dy.
$$

- **\(P \, dy dz\) 部分**：
$$
  P = \frac{x}{\sqrt{x^2 + y^2 + z^2}} = x.
$$
  计算 
  $$\frac{\partial z}{\partial x}$$
$$
  \frac{\partial z}{\partial x} = \frac{x}{\sqrt{1 - x^2 - y^2}}.
$$
  因此：
$$
  \iint_{\Sigma} P \, dy dz = \iint_{D} x \left(-\frac{x}{\sqrt{1 - x^2 - y^2}}\right) dx dy = -\iint_{D} \frac{x^2}{\sqrt{1 - x^2 - y^2}} dx dy.
$$

#### 4. 合并积分

总积分：
$$
I = -\iint_{D} \frac{x^2}{\sqrt{1 - x^2 - y^2}} dx dy + \iint_{D} \left(1 - \sqrt{1 - x^2 - y^2}\right)^2 dx dy.
$$

#### 5. 极坐标变换

设 
$$
x = r \cos \theta，y = r \sin \theta，dx dy = r dr d\theta，D 为 0 \leq r \leq 1，0 \leq \theta \leq 2\pi
$$

- **第一项**：
$$
  -\int_0^{2\pi} \int_0^1 \frac{r^2 \cos^2 \theta}{\sqrt{1 - r^2}} r dr d\theta = -\int_0^{2\pi} \cos^2 \theta d\theta \int_0^1 \frac{r^3}{\sqrt{1 - r^2}} dr.
 $$
  计算角度部分：
$$
  \int_0^{2\pi} \cos^2 \theta d\theta = \pi.
$$
  计算径向部分（设 \(u = 1 - r^2\)）：
$$
  \int_0^1 \frac{r^3}{\sqrt{1 - r^2}} dr = \frac{2}{3}.
$$
  因此第一项为：
$$
  -\pi \cdot \frac{2}{3} = -\frac{2\pi}{3}.
$$
- **第二项**：
$$
  \int_0^{2\pi} \int_0^1 \left(1 - \sqrt{1 - r^2}\right)^2 r dr d\theta = 2\pi \int_0^1 \left(1 - 2\sqrt{1 - r^2} + (1 - r^2)\right) r dr.
$$
  计算径向部分：
 $$
  \int_0^1 \left(2 - 2\sqrt{1 - r^2} - r^2\right) r dr = \frac{1}{12}.
$$
  因此第二项为：
$$
  2\pi \cdot \frac{1}{12} = \frac{\pi}{6}.
$$

#### 6. 最终结果
$$
I = -\frac{2\pi}{3} + \frac{\pi}{6} = -\frac{\pi}{2}.
$$

### 最终答案
$$
\boxed{ -\frac{\pi}{2} }
$$


# 极限

关于定义，主要来自课本，因为需要极高的规范性

## 极限的定义

极限是微积分和数学分析中的核心概念。以下是几种基本类型的极限定义：

### 1. 数列的极限 (Limit of a Sequence)

设 $\{a_n\}$ 是一个实数数列。如果存在一个实数 $L$，使得 $\forall \epsilon > 0$，$\exists N \in \mathbb{Z}^+$（$N$ 通常依赖于 $\epsilon$），使得当 $n > N$ 时，不等式
$$
|a_n - L| < \epsilon
$$
都成立，则称数列 $\{a_n\}$ **收敛** (converges) 于 $L$，或者说 $L$ 是数列 $\{a_n\}$ 的**极限** (limit)。记作：
$$
\lim_{n \to \infty} a_n = L \quad \text{或} \quad a_n \to L \quad (n \to \infty)
$$
如果这样的 $L$ 不存在，则称数列 $\{a_n\}$ **发散** (diverges)。

**符号解释**:
-   $\{a_n\}$: 表示一个数列，例如 $a_1, a_2, a_3, \dots$
-   $L$: 数列的极限值。
-   $\epsilon$ (epsilon): 一个任意小的正数，表示 $a_n$ 与 $L$ 之间的容许误差。
-   $N$: 一个正整数，表示从数列的第 $N+1$ 项开始，所有项都满足误差要求。
-   $|a_n - L|$: $a_n$ 与 $L$ 之间距离的绝对值。
-   $\lim_{n \to \infty}$: 表示当 $n$ 趋向于无穷大时的极限。
-   $\forall$: 全称量词，表示“对于任意的”或“对于所有的”。
-   $\exists$: 存在量词，表示“存在”。
-   $\mathbb{Z}^+$: 正整数集合。

### 函数的极限 (Limit of a Function of One Variable)

设函数 $f(x)$ 在点 $x_0$ 的某个去心邻域内有定义。如果存在一个常数 $A$，使得 $\forall \epsilon > 0$，$\exists \delta > 0$（$\delta$ 通常依赖于 $\epsilon$），使得当 $\forall x:$  $0 < |x - x_0| < \delta$ 时，不等式
$$
|f(x) - A| < \epsilon
$$
都成立，则称常数 $A$ 为函数 $f(x)$ 当 $x \to x_0$ 时的**极限**。记作：
$$
\lim_{x \to x_0} f(x) = A \quad \text{或} \quad f(x) \to A \quad (x \to x_0)
$$

#### 单侧极限 (One-Sided Limits)

- **右极限**: 如果$\forall \epsilon > 0$，使得$\forall x: 0<x-a<\delta$，都有 $|f(x)-A|< \epsilon $，则称A是$f(x)$当$x \to a$时的右极限，记作
$$
\lim_{x \to a^+} f(x) = A
$$

-   **左极限 (Left-hand limit)**: 当 $x \to x_0^-$ (从小于 $x_0$ 的方向趋近 $x_0$) 时，$f(x) \to A$。定义为：$\forall \epsilon > 0$，$\exists \delta > 0$，使得当 $x_0 - \delta < x < x_0$ 时，$|f(x) - A| < \epsilon$。记作 $\lim_{x \to x_0^-} f(x) = A$。


函数 $f(x)$ 在 $x \to x_0$ 时的极限存在的充分必要条件是左极限和右极限都存在且相等，即 $\lim_{x \to x_0^-} f(x) = \lim_{x \to x_0^+} f(x) = A$。

### 二元函数的极限 (Limit of a Function of Two Variables)

设函数 $z = f(x,y)$ 的定义域为 $D \subseteq \mathbb{R}^2$，$P_0(x_0, y_0)$ 是 $D$ 的一个聚点。如果存在一个常数 $A$，使得 $\forall \epsilon > 0$，$\exists \delta > 0$，使得当点 $P(x,y) \in D$ 且满足 $0 < ||P - P_0|| < \delta$ 时（即 $0 < \sqrt{(x-x_0)^2 + (y-y_0)^2} < \delta$），不等式

$$
|f(x,y) - A| < \epsilon
$$
都成立，则称常数 $A$ 为函数 $f(x,y)$ 当点 $P(x,y)$ 趋向于点 $P_0(x_0, y_0)$ 时的**极限**。记作：
$$
\lim_{(x,y) \to (x_0,y_0)} f(x,y) = A \quad \text{或} \quad \lim_{P \to P_0} f(P) = A
$$

**符号解释**:
-   $f(x,y)$: 定义在变量 $x, y$ 上的二元函数。
-   $P_0(x_0, y_0)$: 点 $(x,y)$ 趋近的点。
-   $A$: 函数的极限值。
-   $||P - P_0||$: 点 $P(x,y)$ 与点 $P_0(x_0,y_0)$ 之间的欧氏距离。
-   $0 < ||P - P_0|| < \delta$: 表示点 $P$ 在以 $P_0$ 为中心的半径为 $\delta$ 的去心邻域内。
-   $\forall$: 全称量词。
-   $\exists$: 存在量词。
-   $\mathbb{R}^2$: 二维实数空间。

与一元函数不同，二元函数中点 $P(x,y)$ 趋向于 $P_0(x_0,y_0)$ 的路径是任意的。如果沿不同路径趋近 $P_0$ 时函数 $f(x,y)$ 趋向不同的值，或者沿某条路径趋近时极限不存在，则函数 $f(x,y)$ 在 $P_0$ 点的极限不存在。

# 级数

## 泰勒函数

好的，我已经理解并会在“泰勒级数与麦克劳林级数的核心公式”这部分也采用 **Markdown 嵌套 LaTeX** 的格式。

---

## 泰勒级数展开通项：标准Markdown与LaTeX结合

泰勒级数是一种将函数在某一点附近展开为无穷多项式的方法。这使得我们可以用多项式来近似复杂的函数，从而简化计算和分析。当展开点为 x0​=0 时，这个特殊的泰勒级数被称为**麦克劳林级数**。

---

### 泰勒级数与麦克劳林级数的核心公式

对于一个在点 x0​ 处能够无限次求导的函数 f(x)，其**泰勒级数**的通用表达式如下：

f(x)=n=0∑∞​n!f(n)(x0​)​(x−x0​)n

这个公式展开后就是我们熟悉的：

f(x)=f(x0​)+f′(x0​)(x−x0​)+2!f′′(x0​)​(x−x0​)2+⋯+n!f(n)(x0​)​(x−x0​)n+⋯

其中，f(n)(x0​) 代表函数 f(x) 在 x0​ 点的 n 阶导数，n! 是 n 的阶乘。

当展开点 x0​=0 时，我们得到**麦克劳林级数**，其通项公式为：

f(x)=n=0∑∞​n!f(n)(0)​xn

展开形式为：

f(x)=f(0)+f′(0)x+2!f′′(0)​x2+⋯+n!f(n)(0)​xn+⋯


### 常见函数的麦克劳林级数展开通项

掌握这些常见函数的麦克劳林级数展开式对于高等数学和工程应用至关重要。

1. 指数函数 ex
$$e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots \quad \text{($-\infty < x < \infty$)}$$
    
3. 正弦函数 sin(x)
$$\sin(x) = \sum_{n=0}^{\infty} \frac{(-1)^n}{(2n+1)!}x^{2n+1} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \frac{x^7}{7!} + \cdots \quad \text{($-\infty < x < \infty$)}$$
    
4. 余弦函数 cos(x)
$$\cos(x) = \sum_{n=0}^{\infty} \frac{(-1)^n}{(2n)!}x^{2n} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \frac{x^6}{6!} + \cdots \quad \text{($-\infty < x < \infty$)}$$
    
5. 几何级数 ​$\frac{1}{1-x}​$
$$\frac{1}{1-x} = \sum_{n=0}^{\infty} x^n = 1 + x + x^2 + x^3 + \cdots \quad \text{($-1 < x < 1$)}$$
    
6. 自然对数 ln(1+x)$$\ln(1+x) = \sum_{n=1}^{\infty} \frac{(-1)^{n-1}}{n}x^n = x - \frac{x^2}{2} + \frac{x^3}{3} - \frac{x^4}{4} + \cdots \quad \text{($-1 < x \le 1$)}$$
    
7. 二项式级数 (1+x)α$$(1+x)^\alpha = \sum_{n=0}^{\infty} \binom{\alpha}{n} x^n = 1 + \alpha x + \frac{\alpha(\alpha-1)}{2!}x^2 + \frac{\alpha(\alpha-1)(\alpha-2)}{3!}x^3 + \cdots \quad \text{($-1 < x < 1$)}$$
    
其中，二项式系数 (nα​) 的定义是：
    
    (nα​)=n!α(α−1)⋯(α−n+1)​
    
