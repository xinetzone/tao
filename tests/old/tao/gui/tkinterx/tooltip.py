from tkinter import Tk, Toplevel, ttk


class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, tip_text):
        "Display text in a tooltip window"
        if self.tip_window or not tip_text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")      # get size of widget
        x = x + self.widget.winfo_rootx() + 25          # calculate to display tooltip
        y = y + cy + self.widget.winfo_rooty() + 25     # below and to the right
        # create new tooltip window
        self.tip_window = tw = Toplevel(self.widget)
        # remove all Window Manager (wm) decorations
        tw.wm_overrideredirect(True)
        # tw.wm_overrideredirect(False)                 # uncomment to see the effect
        tw.wm_geometry("+%d+%d" % (x, y))               # create window size

        label = ttk.Label(tw, text=tip_text, justify='left',
                          background="#ffffe0", relief='solid',
                          font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_ToolTip(widget, text):
    toolTip = ToolTip(widget)       # create instance of class

    def enter(event):
        toolTip.show_tip(text)

    def leave(event):
        toolTip.hide_tip()
    widget.bind('<Enter>', enter)   # bind mouse events
    widget.bind('<Leave>', leave)
