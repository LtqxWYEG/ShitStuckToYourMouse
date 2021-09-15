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
offsetY = 0  # offset for Y position
FPS = 60

# Change system mouse cursor to crosshair semi-permanently
# from os import system
# path = r"HKEY_CURRENT_USER\Control Panel\Cursors"
# cur_loc = r".\cross_im.cur"
# system(f"""REG ADD "{path}" /v Arrow /t REG_EXPAND_SZ /d "{cur_loc}" /f""")
# windll.user32.SystemParametersInfoA(0x57)


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    setWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*rgbHexToTuple(transparentColor)), 0, win32con.LWA_COLORKEY)
    # HWND_TOPMOST: Places the window above all non-topmost windows. The window maintains its topmost position even when it is deactivated. (Well, it SHOULD. But doesn't.)
    # It's not necessary to set the SWP_SHOWWINDOW flag.
    # SWP_NOMOVE: Retains the current position (ignores X and Y parameters).
    # SWP_NOSIZE: Retains the current size (ignores the cx and cy parameters).
    # GWL_EXSTYLE: Retrieve the extended window styles of the window.
    # WS_EX_TRANSPARENT: The window should not be painted until siblings beneath the window have been painted, making it transparent.
    # WS_EX_LAYERED: The window is a layered window, so that we can set attributes like color with SetLayeredWindowAttributes ...
    # LWA_COLORKEY: ... and make that color the transparent color of the window.


def rgbHexToTuple(hex):
    colorTuple = tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert hexadecimal color to tuple. Thanks John1024
    return colorTuple


def rgbIntToTuple(RGBint):
    red = RGBint & 255
    green = (RGBint >> 8) & 255
    blue = (RGBint >> 16) & 255
    return (red, green, blue)


class POINT(Structure): _fields_ = [("x", c_int), ("y", c_int)]


mousePosition = POINT()
setWindowPos = windll.user32.SetWindowPos  # see setWindowAttributes()
setFocus = windll.user32.SetFocus  # sets focus to window
pygame.init()
pygame.display.set_caption('MouseDickWhatever')  # title(stupid)
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)  # So far it gets immediately overridden by other windows lower on the z-order
clock = pygame.time.Clock()  # for FPS limiting
info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # flags to set in pygame.display.set_mode
# FULLSCREEN: Create a fullscreen display
# DOUBLEBUF: Double buffering. Creates a separate block of memory to apply all the draw routines and then copying that block (buffer) to video memory. (Thanks, Foon)
# HWSURFACE: hardware accelerated window, only in FULLSCREEN. (Uses memory on video card)

display_window = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with tranparent color set in win32gui.SetLayeredWindowAttributes

hwnd = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(hwnd)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough

font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", fontSize)  # Set Font and font size
text = font.render("(888, 888, 888)", True, fontColor, transparentColor)  # draw text to a new Surface. 'transparentColor' is text background color
# "88:88:88.8888888" defines size of resulting rectangle, so we don't have to text.get_rect() inside the while loop
# 'True' declares use of antialiasing. Antialiasing does not only look better, it is also more optimized. (See: https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render)

windll.user32.GetCursorPos(byref(mousePosition))
text_rect = text.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
text_rect.update(0, 0, text_rect.width+2, text_rect.height+2)
old_text_rect = text_rect  # also
colorSquare = pygame.Surface((42, 42))  # make surface
colorSquare.fill(fontColor)  # fill surface with color
color_rect = colorSquare.get_rect()  # get rectangle from surface
old_color_rect = colorSquare.get_rect()  # second one
small_color_rect = pygame.Rect((1, 1), (40, 40))  # create smaller rectangle to fill with color from pixel

print("--- To stop overlay, close this window ---")  # notify on what to do to stop program
setFocus(hwnd)  # sets focus on pygame window
start = pygame.time.get_ticks()
done = 0
hdc = win32gui.GetDC(0)
while done < 1000:
    display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes
    windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure
    
    # win32gui.GetPixel version:
    #color = rgbIntToTuple(win32gui.GetPixel(hdc, mousePosition.x, mousePosition.y))  # use cursor position to get pixel color

    # windll.gdi32.GetPixel version:
    color = rgbIntToTuple(windll.gdi32.GetPixel(hdc, mousePosition.x, mousePosition.y))

    if mousePosition.x > info.current_w-130 or mousePosition.y > info.current_h-55: color_rect.topleft = (mousePosition.x+offsetX-65, mousePosition.y+offsetY-45)  # update rectangle position
    else: color_rect.topleft = (mousePosition.x+offsetX, mousePosition.y+offsetY+15)
    colorSquare.fill(color, small_color_rect)  # fill surface with color, the size and position of smaller rectangle, to create a 1px border
    display_window.blit(colorSquare, color_rect)  # blit'it

    if mousePosition.x > info.current_w-130 or mousePosition.y > info.current_h-55: text_rect.topleft = (mousePosition.x+offsetX-125, mousePosition.y+offsetY-58)  # update rectangle position
    else: text_rect.topleft = (mousePosition.x+offsetX, mousePosition.y+offsetY)  # set position of rectangle to mouse cursor
    text = font.render(str(color), True, fontColor, '#303030')  # gets color under cursor, then renders it in 'text' Surface object
    display_window.blit(text, text_rect)  # copy text_rect to the display Surface object 'text'

    for event in pygame.event.get(): setFocus(hwnd)  # Brings window back to focus if any key or mouse button is pressed.
    # This is done in order to put the display_window back on top of z-order, because HWND_TOPMOST doesn't work. (Probably because display_window is a child window)
    # (Doing this too often, like once per frame, crashes pygame without error message. Probably some Windows internal spam protection thing)

    pygame.display.update((old_text_rect, text_rect, old_color_rect, color_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
    old_text_rect = ((text_rect.x-1, text_rect.y-1), (text_rect.width+2, text_rect.height+2))  # set old_text_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
    old_color_rect = ((color_rect.x-1, color_rect.y-1), (color_rect.width+2, color_rect.height+2))

    # limit the fps of the program
    #print(clock)
    clock.tick(0)
    #done += 1
# while end
win32gui.ReleaseDC(0, hdc)
elapsed = pygame.time.get_ticks() - start
print(elapsed)
print("press something")
pygame.quit()
input()
