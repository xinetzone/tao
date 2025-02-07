#from functools import lru_cache
from .base import TrajectoryDrawing

class Rectangle:
    def __init__(self, bbox):
        self.x0, self.y0, self.x1, self.y1 = bbox
        self.bunch = {
            'left_top_corner': (self.x0, self.y0),
            'top_middle': (self.center[0], self.y0),
            'right_top_corner': (self.x1, self.y0),
            'right_middle': (self.x1, self.center[1]),
            'right_bottom_corner': (self.x1, self.y1),
            'bottom_middle': (self.center[0], self.y1),
            'left_bottom_corner': (self.x0, self.y1),
            'left_middle': (self.x0, self.center[1])
        }

    @property
    def grad_x(self):
        return self.x1 - self.x0

    @property
    def grad_y(self):
        return self.y1 - self.y0

    @property
    def width(self):
        return abs(self.grad_x)

    @property
    def height(self):
        return abs(self.grad_y)

    @property
    def center(self):
        x = (self.x0 + self.x1)/2
        y = (self.y0 + self.y1)/2
        return x, y

    def __contains__(self, point):
        x, y = point
        x_cond = x in range(self.x0, self.x1)
        y_cond = y in range(self.y0, self.y1)
        return x_cond and y_cond

    def __lt__(self, other):
        '''self < other'''
        return self.width < other.width or self.height < other.height

    def __le__(self, other):
        '''self < other'''
        return self.width <= other.width or self.height <= other.height

class DrawRectangle(TrajectoryDrawing):
    def __init__(self, master=None, alpha=0.2, color='blue', graph_type='rectangle',
                 min_size=7, mask_color='red', cnf={}, **kw):
        '''
        '''
        super().__init__(master, graph_type, color, min_size, cnf, **kw)
        self.alpha= alpha
        self.mask_color = mask_color
        self.rectangle_selector = []
        self.tag_bind('mask', "<ButtonPress-1>", self.scroll_start)
        self.tag_bind('mask', "<B1-Motion>", self.scroll_move)

    def scroll_start(self, event):
        self.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        # self.move('current', w, h)
        # graph_id = self.find_withtag('current')
        # self.select_from(graph_id, 1)
        self.scan_dragto(event.x, event.y, gain=1)

    def create_mask(self, size, alpha, fill):
        '''设置透明蒙版'''
        fill = self.master.winfo_rgb(fill) + (alpha,)
        return Image.new('RGBA', size, fill)
        
    def draw_mask(self, x1, y1, x2, y2):
        size = x2-x1, y2-y1
        alpha = int(self.alpha * 255)
        image = self.create_mask(size, alpha, self.mask_color)
        self.rectangle_selector.append(ImageTk.PhotoImage(image))
        return self.create_image(x1, y1, image=self.rectangle_selector[-1], anchor='nw', tags='mask')

    def finish_drawing(self, *event,  **kw):
        if self.graph_type and self.record_bbox:
            if graph_id := self.drawing(width=1, tags=None, **kw):
                bbox = self.bbox(graph_id)
                mask = self.draw_mask(*bbox)
        self.reset(event)
