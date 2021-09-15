import tkinter as tk
from ctypes import windll, Structure, c_int, byref
from win32api import GetSystemMetrics
import win32gui
import win32con


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


mousePos = 0
mouseX = 0
mouseY = 0
dev = 1
pt = POINT()


class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.label = tk.Label(text=mousePos, bg="#ffffff", fg="#00ff00", font=("fixedsys", 10), relief="flat")
        # relief must be flat, groove, raised, ridge, solid, or sunken
        self.update()

    def update(self):
        queryMousePosition()
        self.label.place(x=mouseX+20, y=mouseY+20)
        if dev == 1: self.label.configure(text="x%i, y%i" % (mouseX, mouseY))
        else: self.label.configure(text="<-- cursor")
        self.after(15, self.update)


def queryMousePosition():
    global mouseX, mouseY, pt
    windll.user32.GetCursorPos(byref(pt))
    mouseX = pt.x
    mouseY = pt.y
    return mouseX, mouseY


def setClickthrough(hwnd):
    # setting window properties
    try:
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        styles = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)
    except Exception as e:
        print(e)


width = GetSystemMetrics(0)
height = GetSystemMetrics(1)

root = tk.Tk()
app = Window(root)
root.overrideredirect(True)
setClickthrough(app.winfo_id())
root.geometry('%dx%d' % (width, height))
root.title('MouseDickWhatever')
root.config(bg='white')
root.attributes('-transparentcolor', 'white', '-topmost', 1)
root.mainloop()
