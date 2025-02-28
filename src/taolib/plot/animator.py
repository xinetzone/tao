from dataclasses import dataclass
from numbers import Number
from matplotlib import pyplot as plt
from IPython import display
from .utils import use_svg_display, set_axes

@dataclass
class Animator:
    """For plotting data in animation."""
    nrows: int = 1
    ncols: int = 1
    xlabel: str | None = None
    ylabel: str | None = None
    legend: list[str] | None = None
    xlim: tuple[float, float] | None = None
    ylim: tuple[float, float] | None = None
    xscale: str = 'linear'
    yscale: str = 'linear'
    fmts: tuple[str, ...] = ('-', 'm--', 'g-.', 'r:')  # 明确元组类型
    figsize: tuple[float, float] = (3.5, 2.5)

    def __post_init__(self):
        if self.legend is None:
            self.legend = []
        use_svg_display()
        self.fig, self.axes = plt.subplots(self.nrows, self.ncols, figsize=self.figsize)
        if self.nrows * self.ncols == 1:
            self.axes = [self.axes, ]
        # Use a lambda function to capture arguments
        self.config_axes = lambda: set_axes(
            self.axes[0], self.xlabel, self.ylabel, self.xlim, self.ylim, self.xscale, self.yscale, self.legend)
        self.X, self.Y = None, None

    def add(self, x: Number|list[Number], y: Number|list[Number]):
        # Add multiple data points into the figure
        if not hasattr(y, "__len__"):
            y = [y]
        n = len(y)
        if not hasattr(x, "__len__"):
            x = [x] * n
        if not self.X:
            self.X = [[] for _ in range(n)]
        if not self.Y:
            self.Y = [[] for _ in range(n)]
        for i, (a, b) in enumerate(zip(x, y)):
            if a is not None and b is not None:
                self.X[i].append(a)
                self.Y[i].append(b)
        self.axes[0].cla()
        for x, y, fmt in zip(self.X, self.Y, self.fmts):
            self.axes[0].plot(x, y, fmt)
        self.config_axes()
        display.display(self.fig)
        display.clear_output(wait=True)
