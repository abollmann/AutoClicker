from tkinter import *


class CreateToolTip:
    """ Create a tooltip for a given widget. """

    tw: Toplevel

    def __init__(self, widget, text='widget info', color='yellow'):
        self.widget = widget
        self.text = text
        self.color = color
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                      background=self.color, relief='solid', borderwidth=1,
                      font=("times", "10", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()
