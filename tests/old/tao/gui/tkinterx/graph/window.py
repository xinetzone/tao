from tkinter import Tk, Menu, filedialog
from PIL import Image, ImageTk


class WindowMeta(Tk):
    def __init__(self):
        super().__init__()
        self._menu_init()
        self.create_menu()

    def _menu_init(self):
        # The settings menu cannot pop up from the window.
        self.option_add('*tearOff', False)

    def create_menu(self):
        self.menu_bar = Menu(self)
        self['menu'] = self.menu_bar  # Or `root.config(menu=menubar)`
        self._create_menu()

    def _create_menu(self):
        self._create_file_menu()
        self._create_edit_menu()

    def _create_edit_menu(self):
        self.edit_bar = Menu(self.menu_bar)
        self.move_menu = Menu(self.edit_bar)
        self.delete_menu = Menu(self.edit_bar)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_bar)
        self.edit_bar.add_cascade(label="move", menu=self.move_menu)
        self.edit_bar.add_cascade(label="delete", menu=self.delete_menu)

    def _create_file_menu(self):
        self.file_bar = Menu(self.menu_bar)
        self.image_menu = Menu(self.file_bar)
        self.tags_menu = Menu(self.file_bar)
        self.menu_bar.add_cascade(label="File", menu=self.file_bar)

    def seek_folder_name(self):
        return filedialog.askdirectory()

    def seek_filename(self):
        return filedialog.askopenfilename()

    def seek_filenames(self):
        return filedialog.askopenfilenames()

    def name2image(self, image_name):
        I = Image.open(image_name)
        _ = ImageTk.PhotoImage(I)
        return ImageTk.PhotoImage(I)


class Window(WindowMeta):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.I = None

    def update_edit_menu(self, graph):
        kw_menu = {
            'variable': graph.edit_var,
            'command': graph.bind_graph
        }
        self.edit_bar.add_radiobutton(label=f"drawing", **kw_menu)
        [self.move_menu.add_radiobutton(
            label=f"move/{option}", **kw_menu) for option in graph.tags_dict]
        [self.delete_menu.add_radiobutton(
            label=f"delete/{option}", **kw_menu) for option in graph.tags_dict]

    def update_file(self):
        self.file_name = self.seek_filename()

    def update_image(self):
        self.I = self.name2image(self.file_name)

    def reload_image(self, graph):
        graph.create_image(0, 0, anchor='nw', image=self.I, tags='image')

    def load_image(self, graph):
        self.update_file()
        self.update_image()
        self.reload_image(graph)

    def update_file_menu(self, graph):
        self.file_bar.add_radiobutton(
            label="Seek filename", command=lambda : self.load_image(graph))

