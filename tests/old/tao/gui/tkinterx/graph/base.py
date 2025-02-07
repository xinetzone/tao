'''Some of the actions related to the graph. see https://www.jianshu.com/p/011a318ffd1e'''
from tkinter import Canvas as _Canvas, StringVar, ttk


class Canvas(_Canvas):
    '''Graphic elements are composed of line(segment), rectangle, ellipse, and arc.'''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.

        Args:
            master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)

    def draw_graph(self, graph_type, direction, color='blue', width=1, tags=None, **kwargs):
        '''Draw basic graphic elements.

        Args:
            direction: Specifies the orientation of the graphic element. 
                Union[int, float] -> (x_0,y_0,x_,y_1), (x_0, y_0) refers to the starting point of 
                the reference brush (i.e., the left mouse button is pressed), and (x_1, y_1) refers to 
                the end position of the reference brush (i.e., release the left mouse button).
                Multipoint sequences are supported for 'line' and 'polygon',
                for example ((x_0, y_0), (x_1, y_1), (x_2, y_2)).

            graph_type: Types of graphic elements.
                (str) 'rectangle', 'oval', 'line', 'arc'(That is, segment), 'polygon'.
                Note that 'line' can no longer pass in the parameter 'fill', and 
                the remaining graph_type cannot pass in the parameter 'outline'.

            color: The color of the graphic element.

            width: The width of the graphic element.(That is, center fill)

            tags: The tags of the graphic element. 
                It cannot be a pure number (such as 1 or '1' or '1 2 3'), it can be a list, a tuple, 
                or a string separated by a space(is converted to String tupers separated by a blank space). 
                The collection or dictionary is converted to a string.
                
                Example:
                    ['line', 'graph'], ('test', 'g'), 'line',
                    ' line kind '(The blanks at both ends are automatically removed), and so on.

            style: Style of the arc in {'arc', 'chord', or 'pieslice'}.

        return: Unique identifier solely for graphic elements.
        '''
        if tags is None:
            if graph_type in ('rectangle', 'oval', 'line', 'arc'):
                tags = f"graph {graph_type}"
            else:
                tags = 'graph'

        com_kw = {'width': width, 'tags': tags}
        kw = {**com_kw, 'outline': color}
        line_kw = {**com_kw, 'fill': color}
        if graph_type == 'line':
            kwargs.update(line_kw)
        else:
            kwargs.update(kw)
        func = eval(f"self.create_{graph_type}")
        graph_id = func(*direction, **kwargs)
        return graph_id

class Drawing(Canvas):
    '''Create graphic elements (graph) including rectangular boxes (which can be square points), ovals (circular points), and segments.
        
    Press the left mouse button to start painting, release the left mouse button for the end of the painting.
    '''

    def __init__(self, master=None, selector=None, cnf={}, **kw):
        '''Click the left mouse button to start painting, release the left mouse button to complete the painting.

        Args:
            selector: The graphics selector, which is an instance of Selector.
        '''
        super().__init__(master, cnf, **kw)
        self.selector = selector

        self._init_params()
        self._draw_bind()

    def _draw_bind(self):
        self.bind("<1>", self.update_xy)
        self.bind("<ButtonRelease-1>", self.draw)

    def _init_params(self):
        self.x = self.y = 0

    def update_xy(self, event):
        '''Press the left mouse button to record the coordinates of the left mouse button'''
        self.x = self.canvasx(event.x)
        self.y = self.canvasy(event.y)

    def get_bbox(self, event):
        x0, y0 = self.x, self.y  # The upper-left coordinates of the graph
        self.update_xy(event)
        x1, y1 = self.x, self.y  # Lower-right coordinates of the graph
        bbox = x0, y0, x1, y1
        return bbox

    def draw(self, event):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        bbox = self.get_bbox(event)
        self.create_graph(bbox)

    def create_graph(self, bbox):
        '''Create a graphic.

        Args:
            bbox: (x0,y0,x1,y1)
        '''
        x0, y0, x1, y1 = bbox
        cond1 = x0 == x1 and y0 == y1 and 'point' not in self.selector.graph_type
        cond2 = 'point' in self.selector.graph_type and (x0 != x1 or y0 != y1)
        if cond1 or cond2:
            return
        else:
            self.draw_graph(self.selector.graph_type.split('_')
                            [0], bbox, self.selector.color)

class TrajectoryDrawing(Drawing):
    '''Draw based on the mouse's trajectory.

    Click the left mouse button to start painting, move the 
        left mouse button 'after_time' after the completion of painting.
    '''

    def __init__(self, master,  selector, after_time=1000, cnf={}, **kw):
        super().__init__(master, selector, cnf, **kw)
        self.after_time = after_time
        self.bind("<1>", self.update_xy)
        self.bind("<ButtonRelease-1>", self.update_xy)
        self.bind("<Button1-Motion>", self.draw)

    def draw(self, event):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        self.after(self.after_time)
        bbox = self.get_bbox(event)
        self.create_graph(bbox)

class Graph(Drawing):
    '''Graph is a drawing tool for manipulating graphic objects.'''
    def __init__(self, master,  selector, cnf={}, **kw):
        super().__init__(master, selector, cnf, **kw)
        self.selected_tags = None
        self.edit_var = StringVar()

    @property
    def tags_dict(self):
        return {
            'Single element': 'current',
            'All elements': 'all',
            'All graphic elements': 'graph',
            '⬜': 'rectangle',
            '⚪': 'oval',
            '⸺': 'line',
            '⯀': 'rectangle_point',
            '●': 'oval_point'
        }

    def move_strides(self, event):
        x, y = self.x, self.y
        self.update_xy(event)
        x_move = self.x - x
        y_move = self.y - y
        return x_move, y_move

    def move_graph(self, event):
        x_move, y_move = self.move_strides(event)
        self.move(self.selected_tags, x_move, y_move)

    def delete_graph(self, event):
        self.delete(self.selected_tags)

    def select_graph(self, event, edit_option):
        self.configure(cursor="target")
        self.update_xy(event)
        tags = self.tags_dict[edit_option]
        if tags == 'current':
            self.selected_tags = self.find_withtag(tags)
        else:
            self.selected_tags = tags

    def bind_graph(self):
        self.unbind('<ButtonRelease-1>')
        self.unbind('<1>')
        edit = self.edit_var.get()
        if edit == 'drawing':
            self._draw_bind()  # reset bind
        elif 'move' in edit:
            self.bind('<1>', lambda event: self.select_graph(
                event, edit.split('/')[1]))
            self.bind('<ButtonRelease-1>', self.move_graph)
        elif 'delete' in edit:
            self.bind('<1>', lambda event: self.select_graph(
                event, edit.split('/')[1]))
            self.bind('<ButtonRelease-1>', self.delete_graph)

class GraphScrollable(Graph):
    '''Pin the picture and label it on it.'''

    def __init__(self, master,  selector, cnf={}, **kw):
        super().__init__(master, selector, cnf, **kw)
        self.coord_var = StringVar()
        self.coord_label = ttk.Label(self, textvariable=self.coord_var)
        self._set_scroll()
        self._scroll_command()
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.bind("<3>", self.mouse_motion)
        self.bind("<Configure>", self.resize)
        self.update_idletasks()
        #self.minsize(self.winfo_width(), self.winfo_height())
        self.scroll_x.pack(side='top', fill='x')
        self.pack(side='left', expand='yes', fill='both')
        self.scroll_y.pack(side='right', fill='y')
        self.coord_label.pack(side='bottom', fill='x')

    def draw(self, event):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        bbox = self.get_bbox(event)
        self.create_graph(bbox)
        self.coord_var.set(f'coordinate: {bbox[:2]} to {bbox[2:]}')

    def select_graph(self, event, edit_option):
        self.configure(cursor="target")
        self.update_xy(event)
        tags = self.tags_dict[edit_option]
        image_tags = self.find_withtag('image')
        selected_tags = self.find_withtag(tags)
        self.selected_tags = set(selected_tags) - set(image_tags)

    def move_graph(self, event):
        x_move, y_move = self.move_strides(event)
        for tag in self.selected_tags:
            self.move(tag, x_move, y_move)

    def delete_graph(self, event):
        for tag in self.selected_tags:
            self.delete(tag)

    def _set_scroll(self):
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal')
        self.scroll_y = ttk.Scrollbar(self, orient='vertical')

    def mouse_motion(self, event):
        x = event.x
        y = event.y
        text = f"coordinate: ({x}, {y})|| {self.canvasx(x), self.canvasy(y)}"
        self.coord_var.set(text)

    def _scroll_command(self):
        self.scroll_x['command'] = self.xview
        self.scroll_y['command'] = self.yview

    def resize(self, event):
        region = self.bbox('all')
        self.configure(scrollregion=region)

