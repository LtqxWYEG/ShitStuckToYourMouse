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


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


pt = POINT()
SetWindowPos = windll.user32.SetWindowPos
SetFocus = windll.user32.SetFocus
mouseX = 0
mouseY = 0
color = "#00ff00"  # font color


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


pygame.init()
# pygame.display.init()
pygame.display.set_caption('MouseDickWhatever')
info = pygame.display.Info()
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # | pygame.OPENGL)  # Also try NOFRAME
display_surface = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far
display_surface.fill((0, 0, 0))

hwnd = pygame.display.get_wm_info()['window']
SetFocus(hwnd)
setClickthrough(hwnd)
queryMousePosition()

clock = pygame.time.Clock()
image = pygame.image.load('./images/pysmall2.png')
image_rect = image.get_rect()
update_rect = image.get_rect()
print("--- To stop overlay, close this window ---")

done = 0
while done < 200:
    queryMousePosition()
    image_rect = image.get_rect()
    image_rect.topleft = (mouseX+20, mouseY+10)
    display_surface.fill((0, 0, 0))
    display_surface.blit(image, (mouseX+20, mouseY+10))  # copy text_rect to the display Surface object

    # Brings window back to focus in order to bring it back on top of Z_BUFFER, because fucking HWND_TOPMOST doesn't work. (Probably a child window)
    for event in pygame.event.get(): SetFocus(hwnd)  # Doing thid too often crashes pygame without error message. Probably some Windows performance thing

    pygame.display.update((update_rect, image_rect))  # First overwrite old Rect, then draw new one to surface
    update_rect = ((image_rect.x-1, image_rect.y-1), (image_rect.width+2, image_rect.height+2))

    clock.tick(60)

pygame.quit()
input()
