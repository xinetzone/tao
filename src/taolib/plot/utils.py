"""画图相关工具"""
from matplotlib import pyplot as plt
from matplotlib_inline import backend_inline
# import matplotlib as mpl


# mpl.rcParams['font.family'] = 'SimHei'  # 设定 matplotlib 支持中文的
# plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题


def use_svg_display():
    """使用 SVG 格式在 Jupyter 中显示绘图"""
    backend_inline.set_matplotlib_formats('svg')

def set_figsize(figsize=(3.5, 2.5)):
    """设置 matplotlib 的图表大小"""
    plt.rcParams['figure.figsize'] = figsize

def annotate(text, xy, xytext):
    """添加文字注解"""
    plt.gca().annotate(text, xy=xy, xytext=xytext,
                       arrowprops={"arrowstyle": "->"})

def set_axes(axes, xlabel, ylabel, 
            xlim = None,
            ylim = None,
            xscale = 'linear',
            yscale = 'linear', 
            legend=None):
    """设置 matplotlib 的轴"""
    if xlim:
        axes.set_xlim(xlim)
    if ylim:
        axes.set_ylim(ylim)
    if legend:
        axes.legend(legend)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.set_xscale(xscale)
    axes.set_yscale(yscale)
    axes.grid()
    return axes

def plot(X, Y=None, xlabel=None, ylabel=None, legend=None, xlim=None,
         ylim=None, xscale='linear', yscale='linear',
         fmts=('-', 'm--', 'g-.', 'r:'), figsize=(3.5, 2.5), axes=None):
    """绘制数据点
    这里 `Y` 可以是一组数据，比如
        >>> x = np.arange(0, 3, 0.1)
        >>> plot(x, [f(x), 2 * x - 3], 'x', 'f(x)', legend=['f(x)', 'Tangent line (x=1)'])
    """
    if legend is None:
        legend = []

    set_figsize(figsize)
    axes = axes if axes else plt.gca()

    # 如果X有一个轴，输出True
    def has_one_axis(X):
        return (hasattr(X, "ndim") and X.ndim == 1 or isinstance(X, list)
                and not hasattr(X[0], "__len__"))

    if has_one_axis(X):
        X = [X]
    if Y is None:
        X, Y = [[]] * len(X), X
    elif has_one_axis(Y):
        Y = [Y]
    if len(X) != len(Y):
        X = X * len(Y)
    axes.cla()
    for x, y, fmt in zip(X, Y, fmts):
        if len(x):
            axes.plot(x, y, fmt)
        else:
            axes.plot(y, fmt)
    set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend)



