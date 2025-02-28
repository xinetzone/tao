import collections
from dataclasses import dataclass, field
from typing import NamedTuple, Any
from IPython import display as _display
from .utils import use_svg_display, plt


class Point(NamedTuple):
    """表示空间中的点"""
    x: float
    y: float


@dataclass
class BoardX:
    """Plot data points in animation."""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple = (3.5, 2.5)
    xlim: list = field(default_factory=list)
    ylim: list = field(default_factory=list)
    xscale: str = 'linear'
    yscale: str = 'linear'
    linestyle: tuple = ('-', '--', '-.', ':')
    colors: tuple = ('C0', 'C1', 'C2', 'C3')
    display: bool = True
    fig: Any = None
    axes: Any = None

    def draw(self, x, y, label, every_n=1):
        if not hasattr(self, 'raw_points'):
            self.raw_points = collections.OrderedDict()
            self.data = collections.OrderedDict()
        if label not in self.raw_points:
            self.raw_points[label] = []
            self.data[label] = []
        points = self.raw_points[label]
        line = self.data[label]
        points.append(Point(x, y))
        if len(points) != every_n:
            return

        def mean(x): return sum(x) / len(x)
        line.append(Point(mean([p.x for p in points]),
                          mean([p.y for p in points])))
        points.clear()
        if not self.display:
            return
        use_svg_display()
        if self.fig is None:
            self.fig = plt.figure(figsize=self.figsize)
        plt_lines, labels = [], []
        for (k, v), linestyle, color in zip(self.data.items(), self.linestyle, self.colors):
            plt_lines.append(plt.plot([p.x for p in v], [p.y for p in v],
                                      linestyle=linestyle, color=color)[0])
            labels.append(k)
        axes = self.axes if self.axes else plt.gca()
        if self.xlim:
            axes.set_xlim(self.xlim)
        if self.ylim:
            axes.set_ylim(self.ylim)
        if not self.xlabel:
            self.xlabel = x
        axes.set_xlabel(self.xlabel)
        axes.set_ylabel(self.ylabel)
        axes.set_xscale(self.xscale)
        axes.set_yscale(self.yscale)
        axes.legend(plt_lines, labels)
        _display.display(self.fig)
        _display.clear_output(wait=True)
