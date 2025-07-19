'''Use help reference at https://www.jianshu.com/p/c6a2b400d0b9

Selector and SelectorFrame are developer-oriented and do not 
    require users to pay attention to their implementation details.
'''
from tkinter import ttk, StringVar

from .base import Canvas


class Selector(Canvas):
    '''A selection icon that sets the shape and color of the graphic.

    Example:
    ======================
    from tkinter import Tk
    root =Tk()
    select = Selector(root)
    select.grid()
    root.mainloop()
    '''
    colors = 'red', 'blue', 'black', 'purple', 'green', 'skyblue', 'yellow', 'white', 'orange', 'pink'
    shapes = 'rectangle', 'oval', 'line', 'oval_point', 'rectangle_point'

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self.start, self.end = 15, 50
        self.create_color()
        self.create_shape()
        self.dtag('graph')

    def create_color(self):
        '''Set the color selector'''
        self.create_text((self.start, self.start),
                         text='color', font='Times 15', anchor='w')
        self.start += 10
        for k, color in enumerate(Selector.colors):
            t = 7+30*(k+1)
            direction = self.start+t, self.start-20, self.end+t, self.end-20
            tags = f"color {color}"
            self.draw_graph('rectangle', direction,
                            'yellow', tags=tags, fill=color)
        self.dtag('rectangle')

    def create_shape(self):
        '''Set the shape selector'''
        self.create_text((self.start-10, self.start+30),
                         text='shape', font='Times 15', anchor='w')
        for k, shape in enumerate(Selector.shapes):
            t = 7+30*(k+1)
            direction = self.start+t, self.start+20, self.end+t, self.end+20
            fill = 'blue' if 'point' in shape else 'white'
            width = 10 if shape == 'line' else 1
            kw = {
                'width': width,
                'fill': fill,
                'tags': f"shape {shape}"
            }
            self.draw_graph(shape.split('_')[0], direction, 'blue', **kw)


class SelectorFrame(ttk.Frame):
    '''Binding the left mouse button function of the graphics selector to achieve the color and 
        shape of the graphics change.

    Example:
    ===============================================
    from tkinter import Tk
    root = Tk()
    selector = SelectorFrame(root)
    selector.layout()
    selector.grid()
    root.mainloop()
    '''

    def __init__(self, master=None, graph_type='rectangle', color='blue', **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        :param graph_type: The initial shape value of the graph.
        :param color: The initial color value of the graph.
        '''
        super().__init__(master, **kw)
        self.color = color
        self.graph_type = graph_type
        self.selector = Selector(
            self, background='lightgreen', width=360, height=80)
        [self.color_bind(self.selector, color) for color in Selector.colors]
        [self.graph_type_bind(self.selector, graph_type)
         for graph_type in Selector.shapes]
        self.info_var = StringVar()
        self.info = ttk.Label(self, textvariable=self.info_var)
        # 布局
        self.selector.grid(row=0, column=0)
        self.info.grid(row=1, column=0)

    def update_info(self):
        '''Update info information.'''
        if self.color or self.graph_type:
            text = f"You Selected: {self.color},{self.graph_type}"
            self.info_var.set(text)

    def update_color(self, new_color):
        '''Update color information.'''
        self.color = new_color
        self.update_info()

    def update_graph_type(self, new_graph_type):
        '''Update graph_type information.'''
        self.graph_type = new_graph_type
        self.update_info()

    def color_bind(self, canvas, color):
        canvas.tag_bind(color, '<1>', lambda e: self.update_color(color))

    def graph_type_bind(self, canvas, graph_type):
        canvas.tag_bind(graph_type, '<1>',
                        lambda e: self.update_graph_type(graph_type))
