#
# Copyright (c) 2021 by LtqxWYEG <distelzombie@protonmail.com>. GPL-3.0 License
#

from ctypes import windll, Structure, c_int, byref
import pygame
import win32gui
import win32con
import win32api
from random import randrange
import time
from datetime import datetime


"""
Fonts by:
Copyright (c) 2014, Cedric Knight <fonts@cedders.com>,
with Reserved Font Name "Segment7".
---
Sizenko Alexander
Style-7
http://www.styleseven.com
Created: November 24 2012

Please visit http://www.styleseven.com/ for download our other products as freeware as shareware.
We will welcome any useful suggestions and comments; please send them to ms-7@styleseven.com
"""


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


SetWindowPos = windll.user32.SetWindowPos
SetFocus = windll.user32.SetFocus
mousePos = 0
mouseX = 0
mouseY = 0
dev = 0  # information in console, cursor position instead of TIME
binary = 0  # print numbers as binary
color = "#00ff00"  # font color
buunt = 0  # color changing rainbow beam power attack, idk
ms = 1  # time with milliseconds
ns = 0  # time with nanoseconds
pt = POINT()


def queryMousePosition():
    global mouseX, mouseY, pt
    windll.user32.GetCursorPos(byref(pt))
    mouseX = pt.x
    mouseY = pt.y
    return mouseX, mouseY


def setClickthrough(hwnd):
    SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED | win32con.WS_CLIPSIBLINGS | win32con.WS_OVERLAPPED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*(0, 0, 0)), 0, win32con.LWA_COLORKEY)


def binaryNumbers(num):
    binary = format(num, '012b')
    return binary

# import os
# os.environ['PYGAME_VSYNC'] = "1"  # This should enable vsync. DOES have some effect on FPS


pygame.init()
# pygame.display.init()
pygame.display.set_caption('MouseDickWhatever')
info = pygame.display.Info()
if dev == 1: print("_______________________"), print("Display information:"), print(info)
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # | pygame.OPENGL)  # Also try NOFRAME
display_surface = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far
display_surface.fill((0, 0, 0))

hwnd = pygame.display.get_wm_info()['window']
SetFocus(hwnd)
setClickthrough(hwnd)
queryMousePosition()
if dev == 1: print("_______________________"), print("win32gui information:"), print(hwnd), print(queryMousePosition())
clock = pygame.time.Clock()

if binary == 1:
    font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", 8)  # Set Font and size

if dev == 1:
    font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", 14)  # Set Font and size
    if binary == 1:
        text = font.render("888888888888__888888888888", True, color, '#000000')
    else:
        text = font.render("8888_8888", True, '#ff0000', '#000000')
elif ms == 1:
    font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", 10)  # Set Font and size
    if binary == 1:
        text = font.render("8888888:88888888:88888888.8888888888888888888888888888888888", True, color, '#000000')
    else:
        text = font.render("88:88:88.8888888", True, color, '#000000')
elif ns == 1:
    font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", 10)  # Set Font and size
    if binary == 1:
        text = font.render("8888888888888888888888888888888888888888888", True, color, '#000000')
    else:
        text = font.render("88888888888888888888", True, color, '#000000')
else:
    font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", 10)  # Set Font and size
    text = font.render("88:88:88", True, color, '#000000')  # "8888_8888" sets the max. width of text_rect. True for anti-aliasing

text_rect = text.get_rect()
update_rect = text.get_rect()
print("--- To stop overlay, close this window ---")
# print(str(time.time_ns()))
start = pygame.time.get_ticks()
done = 0
while done < 1000:
    queryMousePosition()
    text_rect = text.get_rect()
    text_rect.topleft = (mouseX+20, mouseY+10)
    # text_rect.update(mouseX+20, mouseY+10, 125, 22)
    display_surface.fill((0, 0, 0))

    if buunt == 1:
        color = (randrange(256), randrange(256), randrange(256))

    if dev == 1:
        if binary == 1:
            mouseX = binaryNumbers(mouseX)
            mouseY = binaryNumbers(mouseY)
        text = font.render(("%s, %s" % (mouseX, mouseY)), True, '#ff0000')
    elif ms == 1:
        now = str(datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')).split(" ", 1)
        # if binary == 1:
        #     now = binaryNumbers(now)
        text = font.render(now[1], True, color, '#000000')
    elif ns == 1:
        if binary == 1:
            text = font.render(str(binaryNumbers(time.time_ns())), True, color, '#000000')
        else:
            text = font.render(str(time.time_ns()), True, color, '#000000')
    else:
        # if binary == 1:
        #     text = font.render(binaryNumbers(time.strftime("%H:%M:%S", time.localtime())), True, color)
        # else:
        text = font.render(time.strftime("%H:%M:%S", time.localtime()), True, color)

    display_surface.blit(text, text_rect)  # copy text_rect to the display Surface object

    # display_surface.blit((font.render(("%s, %s" % (mouseX, mouseY)), True, color)), text_rect)  # copy text_rect to the display Surface object

    # Brings window back to focus in order to bring it back on top of Z_BUFFER, because fucking HWND_TOPMOST doesn't work. (Probably a child window)
    for event in pygame.event.get(): SetFocus(hwnd)  # Doing thid too often crashes pygame without error message. Probably some Windows performance thing

    pygame.display.update((update_rect, text_rect))  # First overwrite old Rect, then draw new one to surface
    update_rect = ((text_rect.x-1, text_rect.y-1), (text_rect.width+4, text_rect.height+2))

# Benchmarking stuff and FPS limiting:
    # clock.tick_busy_loop(60)
    clock.tick(60)
    done += 1
elapsed = pygame.time.get_ticks() - start
print(elapsed)
print("press something")
pygame.quit()
input()
