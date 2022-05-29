
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
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE or SIGNIFICANCE.          \
#  See the GNU General Public License for more details.                        \
#                                                                              \
#  You should have received a copy of the GNU General Public License           \
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.      \
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


from ctypes import windll, Structure, c_int, byref
import pygame
from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, GetDC, ReleaseDC, SetWindowPos
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED
from win32api import RGB
from datetime import datetime
from time import sleep
from psutil import cpu_percent, virtual_memory, Process
from threading import Thread
import configparser
from os import path, listdir, environ
import sys
import acrylic

import cython
from functools import lru_cache


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


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


class CaseConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):  # To keep thing's FUCKING case! WTH is the problem, configparser devs?
        return optionstr

    def getlist(self, section, option):  # Seriously, what is wrong with them? Why is something so basic not implemented? FF
        value = self.get(section, option)
        return list(filter(None, (x.strip() for x in value.split(','))))

    def getlistint(self, section, option):  # It's so annoying.
        return [int(x) for x in self.getlist(section, option)]

    def getlistfloat(self, section, option):  # No wonder ppl use the horrible JSON... (Although I have no idea if that's actually horrible)
        return [float(x) for x in self.getlist(section, option)]  # it just looks horrible


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", "w") as configfile:
        config.write(configfile)


# settings = dict(config.items('SPARKLES'))
def readVariables():  # --- I do not like this, but now it's done and I don't care anymore ... I'm doing it again
    global config, fontColor, fontSize, offsetX, offsetY, useOffset, showClock, showCPU, showRAM, showColor, FPS,\
        showImage, imagePath, complementaryColor, rgbComplement, artistComplement, outlineThickness, outlineColor
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
    outlineColor = str(config.get("OTHER", "outlineColor"))
    outlineThickness = int(config.get("OTHER", "outlineThickness"))
    showColor = config.getboolean("OTHER", "showColor")
    complementaryColor = config.getboolean("OTHER", "complementaryColor")
    rgbComplement = config.getboolean("OTHER", "rgbComplement")
    artistComplement = config.getboolean("OTHER", "artistComplement")
    showClock = config.getboolean("OTHER", "showClock")
    showCPU = config.getboolean("OTHER", "showCPU")
    showRAM = config.getboolean("OTHER", "showRAM")
    showImage = config.getboolean("OTHER", "showImage")
    imagePath = str(config.get("OTHER", "imagePath"))


class POINT(Structure):  # used for the mouse position
    _fields_ = [("x", c_int), ("y", c_int)]


# Sum of the min & max of (a, b, c)
def sumMinMax(a, b, c):
    if c < b:
        b, c = c, b
    if b < a:
        a, b = b, a
    if c < b:
        b, c = c, b
    return a + c


def rgbHexToTuple(hex):
    colorTuple = tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert hexadecimal color to tuple. Thanks John1024
    return colorTuple


def rgbIntToTuple(RGBint):
    red = RGBint & 255
    green = (RGBint >> 8) & 255
    blue = (RGBint >> 16) & 255
    return red, green, blue


def rgbComplementaryColor(r, g, b):
    k = sumMinMax(r, g, b)
    return tuple(k - u for u in (r, g, b))


def convertFloatTupleToInt(tup):
    tup = tuple(int(x) for x in tup)  # Convert float values to int
    return tup


def cpu_Percent():
    global cpuPercent, loop, devShowOwnCPUPercentInstead
    processID = Process()
    if devShowOwnCPUPercentInstead:
        print(processID)
    while loop:
        if devShowOwnCPUPercentInstead:
            cpuPercent = processID.cpu_percent(interval = 1)
        else:
            cpuPercent = cpu_percent(interval = 1)
        # cpu percent of THIS process


def ram_Percent():
    global ramPercent, loop
    while loop:
        ramPercent = virtual_memory().percent
        sleep(1)


_circle_cache = {}
def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points


def renderTextWithOutline(text, font, fontColor, outlineColor, outlineThickness):
    textSurface = font.render(text, True, fontColor)  # .convert_alpha() was there, but made the outline worse
    width = textSurface.get_width() + 2 * outlineThickness
    height = textSurface.get_height() + 2 * outlineThickness
    outlineSurface = pygame.Surface((width, height)).convert_alpha()
    outlineSurface.fill((1, 1, 1, 0))
    wholeSurface = outlineSurface.copy()
    outlineSurface.blit(font.render(text, True, outlineColor).convert_alpha(), (0, 0))

    #  Paint areas left blank black otherwise if outlineThickness is greater than 2. Heavy on CPU because I'm dumb
    if outlineThickness > 3:
        j = outlineThickness
        outlineThickness = []
        i = 0
        while j >= i:
            outlineThickness.append(i)
            i += 1
        for each in outlineThickness:
            for dx, dy in _circlepoints(each):
                wholeSurface.blit(outlineSurface, (dx + each, dy + each))
        wholeSurface.blit(textSurface, (j, j))
    else:
        for dx, dy in _circlepoints(outlineThickness):
            wholeSurface.blit(outlineSurface, (dx + outlineThickness, dy + outlineThickness))
        wholeSurface.blit(textSurface, (outlineThickness, outlineThickness))
    return wholeSurface


def textWithOutline(text, font, fontColor, outlineColor, outlineThickness):
    outlineSurf = font.render(text, False, outlineColor)
    outlineSize = outlineSurf.get_size()
    textSurf = pygame.Surface((outlineSize[0] + outlineThickness*2, outlineSize[1] + 2*outlineThickness))
    textRect = textSurf.get_rect()
    offsets = [(ox, oy)
               for ox in range(-outlineThickness, 2*outlineThickness, outlineThickness)
               for oy in range(-outlineThickness, 2*outlineThickness, outlineThickness)
               if ox != 0 or ox != 0]
    listOffsets = [list(x) for x in offsets]
    listOffsets[1][0] -= outlineThickness/2-0.5
    listOffsets[4][0] += outlineThickness/2-0.5
    for ox, oy in offsets:
        px, py = textRect.center
        textSurf.blit(outlineSurf, outlineSurf.get_rect(center = (px+ox, py+oy)))
    innerText = font.render(text, False, fontColor)  # .convert_alpha() why are the these everywhere when they make the outline look worse
    textSurf.blit(innerText, innerText.get_rect(center = textRect.center))
    return textSurf


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_TRANSPARENT | WS_EX_LAYERED)
    SetLayeredWindowAttributes(hwnd, RGB(*transparentColorTuple), 0, LWA_COLORKEY)
    # HWND_TOPMOST: Places the window above all non-topmost windows. The window maintains its topmost position even when it is deactivated. (Well, it SHOULD. But doesn't.)
    # It's not necessary to set the SWP_SHOWWINDOW flag.
    # SWP_NOMOVE: Retains the current position (ignores X and Y parameters).
    # SWP_NOSIZE: Retains the current size (ignores the cx and cy parameters).
    # GWL_EXSTYLE: Retrieve the extended window styles of the window.
    # WS_EX_TRANSPARENT: The window should not be painted until siblings beneath the window have been painted, making it transparent.
    # WS_EX_LAYERED: The window is a layered window, so that we can set attributes like color with SetLayeredWindowAttributes ...
    # LWA_COLORKEY: ... and make that color the transparent color of the window.


def loop(old_blit_rect, old_color_rect):
    global loop
    old_rect = blit_rect
    old_blit_rect = blit_rect
    old_color_rect = blit_rect
    while loop:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("loop false, return")
                    loop = False
                    return  # probably redundant
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("loop false, return")
                        loop = False
                        return  # probably redundant
        except KeyboardInterrupt:  # almost never gets killed at a point where this will get triggered. idk
            loop = False
            return

        windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure

        if mousePosition.x > windowWidth - 125 or mousePosition.y > windowHeight - 55:
            if useOffset:
                blit_rect.topleft = (mousePosition.x - offsetX - 65, mousePosition.y - offsetY - 60)  # update rectangle position
            else:
                blit_rect.topleft = (mousePosition.x - 65, mousePosition.y - 60)
        else:
            if useOffset:
                blit_rect.topleft = (mousePosition.x - offsetX, mousePosition.y - offsetY)  # set position of rectangle to mouse cursor
            else:
                blit_rect.topleft = (mousePosition.x, mousePosition.y)

        if showColor:
            colorPx = rgbIntToTuple(windll.gdi32.GetPixel(handleDeviceContext, mousePosition.x, mousePosition.y))

            if mousePosition.x > windowWidth - 125 or mousePosition.y > windowHeight - 55:
                if useOffset:
                    color_rect.topleft = (mousePosition.x - offsetX - 65, mousePosition.y - offsetY - 45)  # update rectangle position
                else:
                    color_rect.topleft = (mousePosition.x - 65, mousePosition.y - 45)
            else:
                if useOffset:
                    color_rect.topleft = (mousePosition.x - offsetX, mousePosition.y - offsetY + text_height+2)
                else:
                    color_rect.topleft = (mousePosition.x, mousePosition.y + text_height+2)

            if complementaryColor:
                if rgbComplement:
                    colorPx = rgbComplementaryColor(colorPx[0], colorPx[1], colorPx[2])
                elif artistComplement:
                    colorPx = acrylic.Color(rgb = (colorPx[0], colorPx[1], colorPx[2]))
                    colorPx = colorPx.scheme(acrylic.Schemes.COMPLEMENTARY, in_rgb=False, fuzzy=0)
                    colorPx = acrylic.Color(ryb = (colorPx[0].ryb[0], colorPx[0].ryb[1], colorPx[0].ryb[2]))
                    colorPx = (colorPx.rgb[0], colorPx.rgb[1], colorPx.rgb[2])
                    #colorPx = acrylic.Color(hsl = (colorPx[0], colorPx[1], colorPx[2]))
                    #colorPx = (colorPx.rgb[0], colorPx.rgb[1], colorPx.rgb[2])
                    #colorPx = (colorPx[0].rgb[0], colorPx[0].rgb[1], colorPx[0].rgb[2])
                    #colorPx = rgbComplementaryColor(colorPx.ryb[0], colorPx.ryb[1], colorPx.ryb[2])
                    #colorPx = artistComplementaryColor(colorPx)
                    #colorPx = tuple(int(round(x)) for x in colorPx)  # Convert float values to int
            colorSquare.fill(colorPx, small_color_rect)  # fill surface with color, the size and position of smaller rectangle, to create a 1px border
            display_window.blit(colorSquare, color_rect)  # blit'it

            text = font.render(str(colorPx), False, fontColor, '#303030')  # gets color under cursor, then renders it in 'text' Surface object
            display_window.blit(text, blit_rect)  # copy blit_rect to the display Surface object 'text'

            pygame.display.update((old_blit_rect, blit_rect, old_color_rect, color_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
            old_blit_rect = ((blit_rect.x - 1, blit_rect.y - 1), (blit_rect.width + 2, blit_rect.height + 2))  # set old_blit_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
            old_color_rect = ((color_rect.x - 1, color_rect.y - 1), (color_rect.width + 2, color_rect.height + 2))
            display_window.fill(transparentColor, old_color_rect)

        elif showImage:
            display_window.blit(image, blit_rect)
            pygame.display.update((old_rect, blit_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
            old_rect = ((blit_rect.x - 1, blit_rect.y - 1), (blit_rect.width + 2, blit_rect.height + 2))  # set old_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
        else:
            if showClock and showCPU and showRAM:
                textClock = textWithOutline(str(datetime.now().time()), font, fontColor, outlineColor, outlineThickness)
                textCPU = textWithOutline(str('CPU: %s' % cpuPercent), font, fontColor, outlineColor, outlineThickness)
                textRAM = textWithOutline(str('RAM: %s' % ramPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
                display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height+2))
                display_window.blit(textRAM, (blit_rect[0], blit_rect[1]+(2*text_height+5)))

            elif showClock and showRAM and not showCPU:
                textClock = textWithOutline(str(datetime.now().time()), font, fontColor, outlineColor, outlineThickness)
                textCPU = textWithOutline(str('RAM: %s' % ramPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
                display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height+2))

            elif showCPU and showRAM and not showClock:
                textRAM = textWithOutline(str('RAM: %s' % ramPercent), font, fontColor, outlineColor, outlineThickness)
                textCPU = textWithOutline(str('CPU: %s' % cpuPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textCPU, blit_rect)  # copy blit_rect to the display Surface object 'text'
                display_window.blit(textRAM, (blit_rect[0], blit_rect[1]+text_height+2))

            elif showClock and showCPU and not showRAM:
                textClock = textWithOutline(str(datetime.now().time()), font, fontColor, outlineColor, outlineThickness)
                textCPU = textWithOutline(str('CPU: %s' % cpuPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textClock, blit_rect)  # copy blit_rect to the display Surface object 'text'
                display_window.blit(textCPU, (blit_rect[0], blit_rect[1]+text_height+2))

            elif showClock and not (showCPU or showRAM):
                textClock = textWithOutline(str(datetime.now().time()), font, fontColor, outlineColor, outlineThickness)  # gets current time from datetime.now() and formats it to get rid of date, then renders it in 'text' Surface object
                display_window.blit(textClock, blit_rect)

            elif showCPU and not (showClock or showRAM):
                textCPU = textWithOutline(str('CPU: %s' % cpuPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textCPU, blit_rect)

            elif showRAM and not (showCPU or showClock):
                textRAM = textWithOutline(str('RAM: %s' % ramPercent), font, fontColor, outlineColor, outlineThickness)
                display_window.blit(textRAM, blit_rect)

            pygame.display.update((old_rect, blit_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it

            if showClock and showCPU and showRAM:  # Fine tuning of updating rect
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + 2*text_height+0))  # set old_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
            elif showClock and showRAM and not showCPU:
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showCPU and showRAM and not showClock:
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showClock and showCPU and not showRAM:
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showClock and showCPU and not showRAM:
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showClock and not (showCPU or showRAM):
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showCPU and not (showClock or showRAM):
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            elif showRAM and not (showCPU or showClock):
                old_rect = ((blit_rect.x-2, blit_rect.y-2), (blit_rect.width+4, blit_rect.height + text_height+0))
            # ----------  showCPU, showRAM, showClock only END -----------
        # display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes
        if devVisibleUpdateRect:
            display_window.fill("#ff0000", old_rect)
        else:
            display_window.fill(transparentColor, old_rect)  # instead of filling the whole screen, fill only small rect
        # that saves about 7 to 10% time overall

        if devPrintFPS:
            clock.tick(0)
            print(int(clock.get_fps()))  # print fps in console (average)
        else:
            clock.tick(FPS) # limit the fps of the program
        # print(_circlepoints.cache_info())


# --------- DEV FLAGS ----------
#  -------------------------------

devDebugging = False  # To make it no longer TOPMOST
devShowOwnCPUPercentInstead = True  # Maybe wrong? Taskmanager different, lower.
devPrintFPS = False
devVisibleUpdateRect = False

#  -------------------------------
# --------- DEV FLAGS ----------






config = CaseConfigParser()
# parseList = CaseConfigParser(converters = {'list': lambda x: [i.strip() for i in x.split(',')]})
config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
config.read("config.ini")  # Read config file
if not config.has_section("SPARKLES") or not config.has_section("OTHER"):
    setDefaults()
    print('No config file exists. Writing new one with default values...')
    print(config)
readVariables()
cleanup_mei()  # see comment inside
transparentColor = "#000000"
if outlineColor == "#000000": outlineColor = "#010101"
mousePosition = POINT()

#----------------- Window stuff
environ['SDL_VIDEO_WINDOW_POS'] = '0,0'  # Set window position to (0,0) as that is necessary now for some reason
pygame.init()
pygame.display.set_caption('PoopStuckToYourMouse - Other')  # title(stupid)
icon = pygame.image.load('.\poop.png')  # icon(stupid)
pygame.display.set_icon(icon)
numDisplays = pygame.display.get_num_displays()

if numDisplays != 1:
    print()
    print("----------- More than one displays detected -----------")
    print("pygame.display.get_num_displays = ", pygame.display.get_num_displays())
    print("pygame.display.Info = ", pygame.display.Info())
    print("pygame.display.get_desktop_sizes = ", pygame.display.get_desktop_sizes())
    print()

    info = pygame.display.get_desktop_sizes()

    # Get highest display height and widest width
    listHeights = []
    combinedWidth = 0
    i = 0
    while i < numDisplays:
        combinedWidth = combinedWidth + info[i][0]
        i = i + 1
    highestHeight = max(info, key=lambda x: x[1])

    print("biggestHeight = ", highestHeight[1])
    print("combinedWidth = ", combinedWidth)
    print()

    if devDebugging:
        display_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync = 0)  # not TOPMOST
    else:
        display_window = pygame.display.set_mode((combinedWidth, highestHeight[1]), 0, vsync = 0)  # vsync only works with OPENGL flag, so far. Might change in the future
else:
    if devDebugging:
        display_window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, vsync = 0)  # not TOPMOST
    else:
        display_window = pygame.display.set_mode((0, 0), 0, vsync = 0)  # vsync only works with OPENGL flag, so far. Might change in the future

#display_window = pygame.display.set_mode((0, 0), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with transparent color set in win32gui.SetLayeredWindowAttributes
transparentColorTuple = tuple(int(transparentColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024
setFocus = windll.user32.SetFocus  # sets focus to window
handleWindowDeviceContext = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(handleWindowDeviceContext)  # set all kinds of option for win32 windows. Makes it transparent and click-through
displayInfo = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
windowWidth = int(displayInfo.current_w)
windowHeight = int(displayInfo.current_h)

#----------------- Other
clock = pygame.time.Clock()  # for FPS limiting
font = pygame.font.Font(resource_path("./fonts/Nouveau_IBM_Stretch.TTF"), fontSize)  # Set Font and font size
outlineFont = pygame.font.Font(resource_path("./fonts/Nouveau_IBM_Stretch.TTF"), fontSize)
# Topaz8: good above 12pt
# Pixel LCD-7: good above 8, 10
# Digital Dismay: good above 12
# ComputoMonospace: good above 8
# speculum: good for above 7
# ShareTechMono-Regular: 10, maybe 8 min
# OxygenMono-Regular: 10 plus
# Nouveau_IBM_Stretch: very small and suprisingly readable at 8, 9 perfect
# Nouveau_IBM: min 9, ok looking
#font = pygame.font.Font("./fonts/Pixel LCD-7.ttf", fontSize)
text_height = font.get_linesize()
blit_rect = []  # also
old_blit_rect = blit_rect  # also
old_color_rect = []

#----------------- Conditionals
if showColor:
    textColor = font.render("(888, 888, 888)", False, fontColor, transparentColor)
    blit_rect = textColor.get_rect()
    blit_rect.update(0, 0, blit_rect.width + 2, blit_rect.height + 2)
    colorSquare = pygame.Surface((42, 42))  # make surface
    colorSquare.fill(fontColor)  # fill surface with color
    color_rect = colorSquare.get_rect()  # get rectangle from surface
    old_color_rect = colorSquare.get_rect()  # second one
    small_color_rect = pygame.Rect((1, 1), (40, 40))  # create smaller rectangle to fill with color from pixel
    old_rect = blit_rect  # initialize as well
    handleDeviceContext = GetDC(0)  # Get display content for measuring RGB value
    looping = True
elif showImage:
    image = pygame.image.load(imagePath)
    blit_rect = image.get_rect()
    old_rect = blit_rect  # initialize as well
    looping = True
elif showCPU or showRAM or showClock:
    if showClock:
        textClock = textWithOutline("88:88:88.8888888", font, fontColor, outlineColor, outlineThickness)  # draw text to a new Surface. 'transparentColor' is text background color
        # "88:88:88.8888888" defines size of resulting rectangle, so we don't have to text.get_rect() inside the while loop
        # 'True' declares use of antialiasing. Antialiasing does not only look better, it is also more optimized. (See: https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render)
        blit_rect = textClock.get_rect()
    if showCPU:
        textCPU = textWithOutline("CPU: 888.8", font, fontColor, outlineColor, outlineThickness)
        getCPU = Thread(target = cpu_Percent)  # define function as separate thread
        getCPU.start()  # start thread
        cpuPercent = 0.0  # initialize variable
        blit_rect = textCPU.get_rect()
    if showRAM:
        textRAM = textWithOutline("RAM: 888.8", font, fontColor, outlineColor, outlineThickness)
        getRAM = Thread(target = ram_Percent)  # define function as separate thread
        getRAM.start()  # start thread
        ramPercent = 0.0  # initialize variable
        blit_rect = textRAM.get_rect()
    if showClock and showCPU and showRAM:
        blit_rect = textClock.get_rect()
        blit_rect = blit_rect.inflate(0, 2*text_height+2)
    elif showClock and showCPU or showClock and showRAM:
        blit_rect = textClock.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, text_height+2)  # double height
    elif showCPU and showRAM and not showClock:
        blit_rect = textCPU.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, text_height+2)
    old_rect = blit_rect  # initialize as aswell
    looping = True
else:
    looping = False  # Interpreter should never reach this if using configuration GUI


setFocus(handleWindowDeviceContext)  # sets focus on pygame window
loop(old_blit_rect, old_color_rect)
print("exited loop")
if showColor: ReleaseDC(0, handleDeviceContext)
print("window handle released")
if showCPU: getCPU.join(5)
if showRAM: getRAM.join(5)
print("threads killed")
pygame.quit()
