
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#  Copyright (c) 2021.                                                         \
#  LtqxWYEG <distelzombie@protonmail.com>                                      \
#                                                                              \
#  This program is free software: you can redistribute it and/or modify        \
#  it under the terms of the GNU General Public License as published by        \
#  the Free Software Foundation, either version 3 of the License, or           \
#  (at your option) any later version.                                         \
#                                                                              \
#  This program is distributed in the hope that it will be useful,             \
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              \
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               \
#  GNU General Public License for more details.                                \
#                                                                              \
#  You should have received a copy of the GNU General Public License           \
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.      \
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


from ctypes import windll, Structure, c_int, byref
import pygame
import win32gui
import win32con
import win32api
from datetime import datetime
from time import sleep
from psutil import cpu_percent, virtual_memory
from threading import Thread
import configparser
from os import path, listdir
import sys


"""
Copyright (C) of font <Pixel LCD-7.ttf> by:
fontSizenko Alexander
Style-7
http://www.styleseven.com
Created: November 24 2012

"""


def cleanup_mei():
    """
    Rudimentary workaround for https://github.com/pyinstaller/pyinstaller/issues/2379
    """
    from shutil import rmtree

    mei_bundle = getattr(sys, "_MEIPASS", False)

    if mei_bundle:
        dir_mei, current_mei = mei_bundle.split("_MEI")
        for file in listdir(dir_mei):
            if file.startswith("_MEI") and not file.endswith(current_mei):
                try:
                    rmtree(path.join(dir_mei, file))
                except PermissionError:  # mainly to allow simultaneous pyinstaller instances
                    pass


class CaseConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):  # To keep thing's FUCKING case! WTH is the problem, configparser devs?
        return optionstr

    def getlist(self, section, option):  # Seriously, what is wrong with them? Why is something so basic not implemented? FF
        value = self.get(section, option)
        return list(filter(None, (x.strip() for x in value.split(','))))

    def getlistint(self, section, option):  # It's so annoying.
        return [int(x) for x in self.getlist(section, option)]

    def getlistfloat(self, section, option):  # No wonder ppl use the horrible JSON... (Although I have no idea if that's better)
        return [float(x) for x in self.getlist(section, option)]


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


# settings = dict(config.items('SPARKLES'))
def readVariables():  # --- I do not like this, but now it's done and I don't care anymore ... I'm doing it again
    global config, fontColor, fontSize, offsetX, offsetY, useOffset, showClock, showCPU, showRAM, showColor, FPS,\
        showImage, imagePath
    # fontColor = "#00ff00"
    # fontSize = 10
    # offsetX = 20  # offset to mouse cursor position in pixel. (= tip of cursor)
    # offsetY = 10  # offset for Y position
    # FPS = 60
    # showClock = True
    # showCPU = True
    # showRAM = True
    FPS = int(config.get("SPARKLES", "FPS"))
    offsetX = int(config.get("SPARKLES", "offsetX"))
    offsetY = int(config.get("SPARKLES", "offsetY"))
    useOffset = config.getboolean("SPARKLES", "useOffset")
    fontColor = str(config.get("OTHER", "fontColor"))
    fontSize = int(config.get("OTHER", "fontSize"))
    showColor = config.getboolean("OTHER", "showColor")
    showClock = config.getboolean("OTHER", "showClock")
    showCPU = config.getboolean("OTHER", "showCPU")
    showRAM = config.getboolean("OTHER", "showRAM")
    showImage = config.getboolean("OTHER", "showImage")
    imagePath = str(config.get("OTHER", "imagePath"))


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


def cpu_Percent():
    global cpuPercent
    while True:
        cpuPercent = cpu_percent(interval = 1)


def ram_Percent():
    global ramPercent
    while True:
        ramPercent = virtual_memory().percent
        sleep(1)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


class POINT(Structure): _fields_ = [("x", c_int), ("y", c_int)]
# def human_size(bytes, units=(' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')):
#     """ Returns a human readable string reprentation of bytes"""
#     return str(bytes) + units[0] if bytes < 1024 else human_size(bytes >> 10, units[1:])


config = CaseConfigParser()
parseList = CaseConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
config.read("config.ini")  # Read config file
config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
if not config.has_section("OTHER"):
    setDefaults()
readVariables()
cleanup_mei()  # see comment inside
transparentColor = "#000000"
mousePosition = POINT()
setWindowPos = windll.user32.SetWindowPos  # see setWindowAttributes()
setFocus = windll.user32.SetFocus  # sets focus to
pygame.init()
pygame.display.set_caption('ShitStuckToYourMouse - Other')  # title(stupid)
clock = pygame.time.Clock()  # for FPS limiting
info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # flags to set in pygame.display.set_mode
# FULLSCREEN: Create a fullscreen display
# DOUBLEBUF: Double buffering. Creates a separate block of memory to apply all the draw routines and then copying that block (buffer) to video memory. (Thanks, Foon)
# HWSURFACE: hardware accelerated window, only in FULLSCREEN. (Uses memory on video card)

windowWidth = int(info.current_w)
windowHeight = int(info.current_h)
display_window = pygame.display.set_mode((windowWidth, windowHeight), flags, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with tranparent color set in win32gui.SetLayeredWindowAttributes
transparentColorTuple = tuple(int(transparentColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024

hwnd = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(hwnd)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough

font = pygame.font.Font(resource_path("Pixel LCD-7.ttf"), fontSize)  # Set Font and font size
#font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", fontSize)
text_height = font.get_linesize()
if showColor:
    textColor = font.render("(888, 888, 888)", True, fontColor, transparentColor)
    blit_rect = textColor.get_rect()
    blit_rect.update(0, 0, blit_rect.width + 2, blit_rect.height + 2)
    old_blit_rect = blit_rect  # also
    colorSquare = pygame.Surface((42, 42))  # make surface
    colorSquare.fill(fontColor)  # fill surface with color
    color_rect = colorSquare.get_rect()  # get rectangle from surface
    old_color_rect = colorSquare.get_rect()  # second one
    small_color_rect = pygame.Rect((1, 1), (40, 40))  # create smaller rectangle to fill with color from pixel
    hdc = win32gui.GetDC(0)  # Get display content for emqsuring RGB value
    old_rect = blit_rect  # initialize as aswell
    loop = True
elif showImage:
    image = pygame.image.load(imagePath)
    blit_rect = image.get_rect()
    old_rect = blit_rect  # initialize as aswell
    loop = True
elif showCPU or showRAM or showClock:
    if showClock:
        textClock = font.render("88:88:88.8888888", True, fontColor, transparentColor)  # draw text to a new Surface. 'transparentColor' is text background color
        # "88:88:88.8888888" defines size of resulting rectangle, so we don't have to text.get_rect() inside the while loop
        # 'True' declares use of antialiasing. Antialiasing does not only look better, it is also more optimized. (See: https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render)
        blit_rect = textClock.get_rect()
    if showCPU:
        textCPU = font.render("CPU: 888.8", True, fontColor, transparentColor)
        getCPU = Thread(target = cpu_Percent)  # define function as separate thread
        getCPU.start()  # start thread
        cpuPercent = 0.0  # initialze variabel
        blit_rect = textCPU.get_rect()
    if showRAM:
        textRAM = font.render("RAM: 888.8", True, fontColor, transparentColor)
        getRAM = Thread(target = ram_Percent)  # define function as separate thread
        getRAM.start()  # start thread
        ramPercent = 0.0  # initialize variabel
        blit_rect = textRAM.get_rect()
    if showClock and showCPU and showRAM:
        blit_rect = textClock.get_rect()
        blit_rect = blit_rect.inflate(0, 18)
    elif showClock and showCPU or showClock and showRAM:
        blit_rect = textClock.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, 8)  # double height
    elif showCPU and showRAM and not showClock:
        blit_rect = textCPU.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, 8)
    old_rect = blit_rect  # initialize as aswell
    loop = True
else:
    loop = False  # Interpreter should nevre reach this if using configuration GUI


setFocus(hwnd)  # sets focus on pygame window
while loop:
    display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes
    windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure

    for event in pygame.event.get():
        setFocus(hwnd)  # Brings window back to focus if any key or mouse button is pressed.
        # This is done in order to put the display_window back on top of z-order, because HWND_TOPMOST doesn't work. (Probably because display_window is a child window)
        # (Doing this too often, like once per frame, crashes pygame without error message. Probably some Windows internal spam protection thing)
        if event.type == pygame.QUIT:
            loop = False
        # elif event.type == pygame.KEYDOWN:  # --- Note: practically uneccessary because window isn't focused
        #     if event.key == pygame.K_ESCAPE:
        #         loop = False
    if showColor:
        colorPx = rgbIntToTuple(windll.gdi32.GetPixel(hdc, mousePosition.x, mousePosition.y))
        if mousePosition.x > windowWidth - 130 or mousePosition.y > windowHeight - 55:
            if useOffset:
                color_rect.topleft = (mousePosition.x + offsetX - 65, mousePosition.y + offsetY - 45)  # update rectangle position
            else:
                color_rect.topleft = (mousePosition.x - 65, mousePosition.y - 45)
        else:
            if useOffset:
                color_rect.topleft = (mousePosition.x + offsetX, mousePosition.y + offsetY + 15)
            else:
                color_rect.topleft = (mousePosition.x, mousePosition.y + 15)
        colorSquare.fill(colorPx, small_color_rect)  # fill surface with color, the size and position of smaller rectangle, to create a 1px border
        display_window.blit(colorSquare, color_rect)  # blit'it

        if mousePosition.x > windowWidth - 130 or mousePosition.y > windowHeight - 55:
            if useOffset:
                blit_rect.topleft = (mousePosition.x + offsetX - 125, mousePosition.y + offsetY - 58)  # update rectangle position
            else:
                blit_rect.topleft = (mousePosition.x - 125, mousePosition.y - 58)
        else:
            if useOffset:
                blit_rect.topleft = (mousePosition.x + offsetX, mousePosition.y + offsetY)  # set position of rectangle to mouse cursor
            else:
                blit_rect.topleft = (mousePosition.x, mousePosition.y)
        text = font.render(str(colorPx), True, fontColor, '#303030')  # gets color under cursor, then renders it in 'text' Surface object
        display_window.blit(text, blit_rect)  # copy blit_rect to the display Surface object 'text'

        pygame.display.update((old_blit_rect, blit_rect, old_color_rect, color_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
        old_blit_rect = ((blit_rect.x - 1, blit_rect.y - 1), (blit_rect.width + 2, blit_rect.height + 2))  # set old_blit_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
        old_color_rect = ((color_rect.x - 1, color_rect.y - 1), (color_rect.width + 2, color_rect.height + 2))
    elif showImage:
        if useOffset:
            blit_rect.topleft = (mousePosition.x + offsetX, mousePosition.y + offsetY)
        else:
            blit_rect.topleft = (mousePosition.x, mousePosition.y)
        display_window.blit(image, blit_rect)
        pygame.display.update((old_rect, blit_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
        old_rect = ((blit_rect.x - 1, blit_rect.y - 1), (blit_rect.width + 2, blit_rect.height + 2))  # set old_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
    else:
        if useOffset:
            blit_rect.topleft = (mousePosition.x+offsetX, mousePosition.y+offsetY)  # set position of rectangle to mouse cursor
        else:
            blit_rect.topleft = (mousePosition.x, mousePosition.y)
        if showClock and showCPU and showRAM:
            textClock = font.render(str(datetime.now().time()), True, fontColor, transparentColor)
            textCPU = font.render(str('CPU: %s' % cpuPercent), True, fontColor, transparentColor)
            textRAM = font.render(str('RAM: %s' % ramPercent), True, fontColor, transparentColor)
            display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
            display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height))
            display_window.blit(textRAM, (blit_rect[0], blit_rect[1]+(2*text_height)))
        elif showClock and showRAM and not showCPU:
            textClock = font.render(str(datetime.now().time()), True, fontColor, transparentColor)
            textCPU = font.render(str('RAM: %s' % ramPercent), True, fontColor, transparentColor)
            display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
            display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height))
        elif showCPU and showRAM and not showClock:
            textRAM = font.render(str('RAM: %s' % ramPercent), True, fontColor, transparentColor)
            textCPU = font.render(str('CPU: %s' % cpuPercent), True, fontColor, transparentColor)
            display_window.blit(textCPU, blit_rect)  # copy blit_rect to the display Surface object 'text'
            display_window.blit(textRAM, (blit_rect[0], blit_rect[1]+text_height))
        elif showClock and showCPU and not showRAM:
            textClock = font.render(str(datetime.now().time()), True, fontColor, transparentColor)
            textCPU = font.render(str('CPU: %s' % cpuPercent), True, fontColor, transparentColor)
            display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
            display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height))
        elif showClock and not (showCPU or showRAM):
            textClock = font.render(str(datetime.now().time()), True, fontColor, transparentColor)  # gets current time from datetime.now() and formats it to get rid of date, then renders it in 'text' Surface object
            display_window.blit(textClock, blit_rect)
        elif showCPU and not (showClock or showRAM):
            textCPU = font.render(str('CPU: %s' % cpuPercent), True, fontColor, transparentColor)
            display_window.blit(textCPU, blit_rect)
        elif showRAM and not (showCPU or showClock):
            textRAM = font.render(str('RAM: %s' % ramPercent), True, fontColor, transparentColor)
            display_window.blit(textRAM, blit_rect)
        pygame.display.update((old_rect, blit_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
        old_rect = ((blit_rect.x-1, blit_rect.y-1), (blit_rect.width+2, blit_rect.height+2))  # set old_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts

    # limit the fps of the program
    clock.tick(FPS)
# while end

win32gui.ReleaseDC(0, hdc)
getCPU.join()
getRAM.join()
pygame.quit()
