#
# Copyright (C) 2021 by LtqxWYEG <distelzombie@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from ctypes import windll, Structure, c_int, byref
import pygame
import win32gui
import win32con
import win32api
from datetime import datetime


"""
Copyright (C) of font <Pixel LCD-7.ttf> by:
fontSizenko Alexander
Style-7
http://www.styleseven.com
Created: November 24 2012

"""


# Settings
transparentColor = "#000000"
fontColor = "#00ff00"
fontSize = 10
offsetX = 20  # offset to mouse cursor position in pixel. (= tip of cursor)
offsetY = 10  # offset for Y position
FPS = 60


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    setWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*transparentColorTuple), 0, win32con.LWA_COLORKEY)
    # HWND_TOPMOST: Places the window above all non-topmost windows. The window maintains its topmost position even when it is deactivated. (Well, it SHOULD. But doesn't.)
    # It's not necessary to set the SWP_SHOWWINDOW flag.
    # SWP_NOMOVE: Retains the current position (ignores X and Y parameters).
    # SWP_NOSIZE: Retains the current size (ignores the cx and cy parameters).
    # GWL_EXSTYLE: Retrieve the extended window styles of the window.
    # WS_EX_TRANSPARENT: The window should not be painted until siblings beneath the window have been painted, making it transparent.
    # WS_EX_LAYERED: The window is a layered window, so that we can set attributes like color with SetLayeredWindowAttributes ...
    # LWA_COLORKEY: ... and make that color the transparent color of the window.


class POINT(Structure): _fields_ = [("x", c_int), ("y", c_int)]


mousePosition = POINT()
setWindowPos = windll.user32.SetWindowPos  # see setWindowAttributes()
setFocus = windll.user32.SetFocus  # sets focus to
pygame.init()
pygame.display.set_caption('MouseDickWhatever')  # title(stupid)
clock = pygame.time.Clock()  # for FPS limiting
info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # flags to set in pygame.display.set_mode
# FULLSCREEN: Create a fullscreen display
# DOUBLEBUF: Double buffering. Creates a separate block of memory to apply all the draw routines and then copying that block (buffer) to video memory. (Thanks, Foon)
# HWSURFACE: hardware accelerated window, only in FULLSCREEN. (Uses memory on video card)

display_window = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with tranparent color set in win32gui.SetLayeredWindowAttributes
transparentColorTuple = tuple(int(transparentColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024

hwnd = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(hwnd)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough

font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", fontSize)  # Set Font and font size
text = font.render("88:88:88.8888888", True, fontColor, transparentColor)  # draw text to a new Surface. 'transparentColor' is text background color
# "88:88:88.8888888" defines size of resulting rectangle, so we don't have to text.get_rect() inside the while loop
# 'True' declares use of antialiasing. Antialiasing does not only look better, it is also more optimized. (See: https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render)

text_rect = text.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
old_rect = text.get_rect()  # initialize as aswell
print("--- To stop overlay, close this window ---")  # notify on what to do to stop program
setFocus(hwnd)  # sets focus on pygame window

while True:
    windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure
    text_rect.topleft = (mousePosition.x+offsetX, mousePosition.y+offsetY)  # set position of rectangle to mouse cursor
    display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes

    text = font.render(str(datetime.now().time()), True, fontColor, transparentColor)  # gets current time from datetime.now() and formats it to get rid of date, then renders it in 'text' Surface object
    display_window.blit(text, text_rect)  # copy text_rect to the display Surface object 'text'

    for event in pygame.event.get(): setFocus(hwnd)  # Brings window back to focus if any key or mouse button is pressed.
    # This is done in order to put the display_window back on top of z-order, because HWND_TOPMOST doesn't work. (Probably because display_window is a child window)
    # (Doing this too often, like once per frame, crashes pygame without error message. Probably some Windows internal spam protection thing)

    pygame.display.update((old_rect, text_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
    old_rect = ((text_rect.x-1, text_rect.y-1), (text_rect.width+2, text_rect.height+2))  # set old_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts

    # limit the fps of the program
    clock.tick(FPS)
# while end

pygame.quit()
input()
