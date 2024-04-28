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
#  along with this program. If not, see <https://www.gnu.org/licenses/>.      \
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


from ctypes import windll, Structure, c_int, byref
import pygame

from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, GetDC, ReleaseDC, SetWindowPos
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED, WS_EX_TOOLWINDOW
from win32api import RGB
from datetime import datetime
from time import sleep, process_time
from psutil import cpu_percent, virtual_memory, Process
from threading import Thread
import configparser
from os import path, listdir, environ
import sys
import acrylic


# import cython
# from functools import lru_cache


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
        return list(filter(None, (x.strip() for x in value.split(","))))

    def getlistint(self, section, option):  # It's so annoying.
        return [int(x) for x in self.getlist(section, option)]

    def getlistfloat(self, section, option):  # No wonder ppl use the horrible JSON... (Although I have no idea if that's actually horrible)
        return [float(x) for x in self.getlist(section, option)]  # it just looks horrible


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def readVariables():  # --- I do not like this, but now it's done and I don't care anymore ... I'm doing it again
    # global config, fontColor, fontSize, offsetX, offsetY, useOffset, showClock, showCPU, showRAM, showColor, FPS,\
    #     showImage, imagePath, complementaryColor, rgbComplement, artistComplement, outlineThickness, outlineColor
    global settings

    settings = dict()  # config.items('OTHER')

    settings["FPS"] = int(config.get("SPARKLES", "FPS"))
    settings["offsetX"] = int(config.get("SPARKLES", "offsetX"))
    settings["offsetY"] = int(config.get("SPARKLES", "offsetY"))
    settings["useOffset"] = config.getboolean("SPARKLES", "useOffset")

    settings["fontColor"] = str(config.get("OTHER", "fontColor"))
    settings["fontSize"] = int(config.get("OTHER", "fontSize"))
    settings["outlineColor"] = str(config.get("OTHER", "outlineColor"))
    settings["outlineThickness"] = int(config.get("OTHER", "outlineThickness"))
    settings["fontAntialiasing"] = config.getboolean("OTHER", "fontAntialiasing")
    settings["showColor"] = config.getboolean("OTHER", "showColor")
    settings["complementaryColor"] = config.getboolean("OTHER", "complementaryColor")
    settings["rgbComplement"] = config.getboolean("OTHER", "rgbComplement")
    settings["artistComplement"] = config.getboolean("OTHER", "artistComplement")
    settings["showClock"] = config.getboolean("OTHER", "showClock")
    settings["showCPU"] = config.getboolean("OTHER", "showCPU")
    settings["showRAM"] = config.getboolean("OTHER", "showRAM")
    settings["showImage"] = config.getboolean("OTHER", "showImage")
    settings["imagePath"] = str(config.get("OTHER", "imagePath"))
    print(settings)
    return


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
    colorTuple = tuple(int(hex.lstrip("#")[y : y + 2], 16) for y in (0, 2, 4))  # convert hexadecimal color to tuple. Thanks John1024
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
    global cpuPercent, looping, devShowOwnCPUPercentInstead
    processID = Process()
    if devShowOwnCPUPercentInstead:
        print(processID)
    while looping:
        if devShowOwnCPUPercentInstead:
            cpuPercent = processID.cpu_percent(interval=1)
        else:
            cpuPercent = cpu_percent(interval=1)
        # cpu percent of THIS process


def ram_Percent():
    global ramPercent, looping
    while looping:
        ramPercent = virtual_memory().percent
        sleep(1)


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


# slow but very good looking if outline >1
def textWithOutline2(text, font_face, font_Color, outline_Color, outline_Thickness):
    if settings["fontAntialiasing"]:
        textSurface = font_face.render(text, True, font_Color)
    else:
        textSurface = font_face.render(text, False, font_Color)  # .convert_alpha() was there, but made the outline worse
    width = textSurface.get_width() + 2 * outline_Thickness
    height = textSurface.get_height() + 2 * outline_Thickness
    outlineSurface = pygame.Surface((width, height)).convert_alpha()
    outlineSurface.fill((1, 1, 1, 0))
    wholeSurface = outlineSurface.copy()
    if settings["fontAntialiasing"]:
        outlineSurface.blit(font_face.render(text, True, outline_Color), (0, 0))
    else:
        outlineSurface.blit(font_face.render(text, False, outline_Color).convert_alpha(), (0, 0))

    #  Paint areas left blank black otherwise if outline_Thickness is greater than 2. Heavy on CPU because I'm dumb
    if outline_Thickness > 3:
        j = outline_Thickness
        outline_Thickness = []
        i = 0
        while j >= i:
            outline_Thickness.append(i)
            i += 1
        for each in outline_Thickness:
            for dx, dy in _circlepoints(each):
                wholeSurface.blit(outlineSurface, (dx + each, dy + each))
        wholeSurface.blit(textSurface, (j, j))
    else:
        for dx, dy in _circlepoints(outline_Thickness):
            wholeSurface.blit(outlineSurface, (dx + outline_Thickness, dy + outline_Thickness))
        wholeSurface.blit(textSurface, (outline_Thickness, outline_Thickness))
    return wholeSurface


# very fast and best of all looking if outline=1
def textWithOutline(text, font_face, font_Color, outline_Color, outline_Thickness):
    if settings["fontAntialiasing"]:
        outlineSurf = font_face.render(text, True, outline_Color)
    else:
        outlineSurf = font_face.render(text, False, outline_Color)
    outlineSize = outlineSurf.get_size()
    textSurf = pygame.Surface((outlineSize[0] + outline_Thickness * 2, outlineSize[1] + 2 * outline_Thickness))
    textRect = textSurf.get_rect()
    offsets = [(ox, oy) for ox in range(-outline_Thickness, 2 * outline_Thickness, outline_Thickness) for oy in range(-outline_Thickness, 2 * outline_Thickness, outline_Thickness) if ox != 0 or ox != 0]
    listOffsets = [list(x) for x in offsets]
    listOffsets[1][0] -= outline_Thickness / 2 - 0.5
    listOffsets[4][0] += outline_Thickness / 2 - 0.5
    for ox, oy in offsets:
        px, py = textRect.center
        textSurf.blit(outlineSurf, outlineSurf.get_rect(center=(px + ox, py + oy)))
    if settings["fontAntialiasing"]:
        innerText = font_face.render(text, True, font_Color)
    else:
        innerText = font_face.render(text, False, font_Color)  # .convert_alpha() why are the these everywhere when they make the outline look worse
    textSurf.blit(innerText, innerText.get_rect(center=textRect.center))
    return textSurf


# Slow and bad looking, don't use
def textWithOutline3(text, font_face, font_Color, outline_Color, outline_width):
    text_surface = font_face.render(text, True, font_Color)
    text_outline_surface = font_face.render(text, True, outline_Color)
    # There is no good way to get an outline with pygame, so we draw
    # the text at 8 points around the main text to simulate an outline.
    directions = [(outline_width, outline_width), (0, outline_width), (-outline_width, outline_width), (outline_width, 0), (-outline_width, 0), (outline_width, -outline_width), (0, -outline_width), (-outline_width, -outline_width)]
    textRect = text_surface.get_rect()
    for direction in directions:
        text_surface.blit(text_outline_surface, (textRect[0] - direction[0], textRect[1] - direction[1]))
    # blit foreground image to the screen
    innerText = font_face.render(text, False, font_Color)
    text_surface.blit(innerText, innerText.get_rect(center=textRect.center))
    return text_surface


# def textWithOutline4(text, font_face, font_Color, outline_Color, outline_Thickness):
#     textSurface, textRect = font_face.render(text, font_Color, settings['transparentColor'], size=settings['fontSize'])
#     # Rect(left, top, width, height) -> Rect
#
#     font_face.render_to(textSurface, (textRect[0], textRect[1]), "HELLO", outline_Color, "#00FF00", size=outline_Thickness)
#     # render_to(surf, dest, text, fgcolor=None, bgcolor=None, style=STYLE_DEFAULT, rotation=0, size=0) -> Rect
#
#     return textSurface


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW)  # no taskbar button
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


def loop(main_rect, last_rect, last_main_rect, last_color_rect):
    global looping, length, timer
    # ----optimizations----
    # useOffset = settings['useOffset']
    # offsetX = settings['offsetX']
    # offsetY = settings['offsetY']
    # showColor = settings['showColor']
    # complementaryColor = settings['complementaryColor']:
    # rgbComplement = settings['rgbComplement']:
    # artistComplement = settings['artistComplement']
    # fontColor = settings['fontColor']
    # transparentColor = settings['transparentColor']
    # showImage = settings['showImage']
    # etc...
    try:
        while looping:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("loop false, return")
                    looping = False
                    return  # probably redundant
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("loop false, return")
                        looping = False
                        return  # probably redundant

            windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure

            if mousePosition.x > windowWidth - 125 or mousePosition.y > windowHeight - 55:
                if settings["useOffset"]:
                    main_rect.topleft = (mousePosition.x - settings["offsetX"] - 65, mousePosition.y - settings["offsetY"] - 60)  # update rectangle position
                else:
                    main_rect.topleft = (mousePosition.x - 65, mousePosition.y - 60)
            else:
                if settings["useOffset"]:
                    main_rect.topleft = (mousePosition.x - settings["offsetX"], mousePosition.y - settings["offsetY"])  # set position of rectangle to mouse cursor
                else:
                    main_rect.topleft = (mousePosition.x, mousePosition.y)

            if settings["showColor"]:
                colorPx = rgbIntToTuple(windll.gdi32.GetPixel(handleDeviceContext, mousePosition.x, mousePosition.y))

                if mousePosition.x > windowWidth - 125 or mousePosition.y > windowHeight - 55:
                    if settings["useOffset"]:
                        color_rect.topleft = (mousePosition.x - settings["offsetX"] - 65, mousePosition.y - settings["offsetY"] - 45)  # update rectangle position
                    else:
                        color_rect.topleft = (mousePosition.x - 65, mousePosition.y - 45)
                else:
                    if settings["useOffset"]:
                        color_rect.topleft = (mousePosition.x - settings["offsetX"], mousePosition.y - settings["offsetY"] + text_height + 2)
                    else:
                        color_rect.topleft = (mousePosition.x, mousePosition.y + text_height + 2)

                if settings["complementaryColor"]:
                    if settings["rgbComplement"]:
                        colorPx = rgbComplementaryColor(colorPx[0], colorPx[1], colorPx[2])
                    elif settings["artistComplement"]:
                        colorPx = acrylic.Color(rgb=(colorPx[0], colorPx[1], colorPx[2]))
                        colorPx = colorPx.scheme(acrylic.Schemes.COMPLEMENTARY, in_rgb=False, fuzzy=0)
                        colorPx = acrylic.Color(ryb=(colorPx[0].ryb[0], colorPx[0].ryb[1], colorPx[0].ryb[2]))
                        colorPx = (colorPx.rgb[0], colorPx.rgb[1], colorPx.rgb[2])
                        # colorPx = acrylic.Color(hsl = (colorPx[0], colorPx[1], colorPx[2]))
                        # colorPx = (colorPx.rgb[0], colorPx.rgb[1], colorPx.rgb[2])
                        # colorPx = (colorPx[0].rgb[0], colorPx[0].rgb[1], colorPx[0].rgb[2])
                        # colorPx = rgbComplementaryColor(colorPx.ryb[0], colorPx.ryb[1], colorPx.ryb[2])
                        # colorPx = artistComplementaryColor(colorPx)
                        # colorPx = tuple(int(round(x)) for x in colorPx)  # Convert float values to int
                colorSquare.fill(colorPx, small_color_rect)  # fill surface with color, the size and position of smaller rectangle, to create a 1px border
                display_window.blit(colorSquare, color_rect)  # blit'it

                #text = font.render(str(colorPx), False, settings["fontColor"], "#303030")  # gets color under cursor, then renders it in 'text' Surface object
                text = drawOutlineAroundText(str(colorPx), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                display_window.blit(text, main_rect)  # copy main_rect to the display Surface object 'text'

                pygame.display.update((last_main_rect, main_rect, last_color_rect, color_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
                last_main_rect = ((main_rect.x - 1, main_rect.y - 1), (main_rect.width + 2, main_rect.height + 2))  # set last_main_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
                last_color_rect = ((color_rect.x - 1, color_rect.y - 1), (color_rect.width + 2, color_rect.height + 2))
                display_window.fill(settings["transparentColor"], last_color_rect)

            elif settings["showImage"]:
                display_window.blit(image, main_rect)
                pygame.display.update((last_rect, main_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
                last_rect = ((main_rect.x - 1, main_rect.y - 1), (main_rect.width + 2, main_rect.height + 2))  # set last_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
            else:
                if devVisibleUpdateRect:
                    highlight = pygame.Surface((main_rect.w + 2, main_rect.h + 2))
                    highlight.fill("#ff0000")
                    display_window.blit(highlight, main_rect)

                match settings["activeThings"]:
                    case 1:
                        textRAM = drawOutlineAroundText(str("RAM: %s" % ramPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textRAM, main_rect)
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 2:
                        textCPU = drawOutlineAroundText(str("CPU: %s" % cpuPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textCPU, main_rect)
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 3:
                        textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])  # gets current time from datetime.now() and formats it to get rid of date, then renders it in 'text' Surface object
                        display_window.blit(textClock, main_rect)
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 4:
                        textCPU = drawOutlineAroundText(str("CPU: %s" % cpuPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        textRAM = drawOutlineAroundText(str("RAM: %s" % ramPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textCPU, main_rect)  # copy main_rect to the display Surface object 'text'
                        display_window.blit(textRAM, (main_rect[0], main_rect[1] + text_height + 2))
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 5:
                        textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        textCPU = drawOutlineAroundText(str("RAM: %s" % ramPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                        display_window.blit(textCPU, (main_rect[0], main_rect[1] + text_height + 2))
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 6:
                        textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        textCPU = drawOutlineAroundText(str("CPU: %s" % cpuPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                        display_window.blit(textCPU, (main_rect[0], main_rect[1] + text_height + 2))
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + text_height + 0))
                    case 7:
                        textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        textCPU = drawOutlineAroundText(str("CPU: %s" % cpuPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        textRAM = drawOutlineAroundText(str("RAM: %s" % ramPercent), font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
                        display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                        display_window.blit(textCPU, (main_rect[0], main_rect[1] + text_height + 2))
                        display_window.blit(textRAM, (main_rect[0], main_rect[1] + (2 * text_height + 5)))
                        pygame.display.update((last_rect, main_rect))
                        last_rect = ((main_rect.x - 2, main_rect.y - 2), (main_rect.width + 4, main_rect.height + 2 * text_height + 0))
                    case _:
                        return

                # old and a teeeeensy bit slower maybe
                # if settings['showClock'] and settings['showCPU'] and settings['showRAM']:
                #     textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     textCPU = drawOutlineAroundText(str('CPU: %s' % cpuPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     textRAM = drawOutlineAroundText(str('RAM: %s' % ramPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                #     display_window.blit(textCPU, (main_rect[0], main_rect[1]+text_height+2))
                #     display_window.blit(textRAM, (main_rect[0], main_rect[1]+(2*text_height+5)))
                #
                # elif settings['showClock'] and settings['showRAM'] and not settings['showCPU']:
                #     textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     textCPU = drawOutlineAroundText(str('RAM: %s' % ramPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                #     display_window.blit(textCPU, (main_rect[0], main_rect[1]+text_height+2))
                #
                # elif settings['showCPU'] and settings['showRAM'] and not settings['showClock']:
                #     textRAM = drawOutlineAroundText(str('RAM: %s' % ramPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     textCPU = drawOutlineAroundText(str('CPU: %s' % cpuPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textCPU, main_rect)  # copy main_rect to the display Surface object 'text'
                #     display_window.blit(textRAM, (main_rect[0], main_rect[1]+text_height+2))
                #
                # elif settings['showClock'] and settings['showCPU'] and not settings['showRAM']:
                #     textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     textCPU = drawOutlineAroundText(str('CPU: %s' % cpuPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textClock, main_rect)  # copy main_rect to the display Surface object 'text'
                #     display_window.blit(textCPU, (main_rect[0], main_rect[1]+text_height+2))
                #
                # elif settings['showClock'] and not (settings['showCPU'] or settings['showRAM']):
                #     textClock = drawOutlineAroundText(str(datetime.now().time()), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])  # gets current time from datetime.now() and formats it to get rid of date, then renders it in 'text' Surface object
                #     display_window.blit(textClock, main_rect)
                #
                # elif settings['showCPU'] and not (settings['showClock'] or settings['showRAM']):
                #     textCPU = drawOutlineAroundText(str('CPU: %s' % cpuPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textCPU, main_rect)
                #
                # elif settings['showRAM'] and not (settings['showCPU'] or settings['showClock']):
                #     textRAM = drawOutlineAroundText(str('RAM: %s' % ramPercent), font, settings['fontColor'], settings['outlineColor'], settings['outlineThickness'])
                #     display_window.blit(textRAM, main_rect)
                #
                # pygame.display.update((last_rect, main_rect))  # First overwrite old rectangle with fill(RGB) color, then draw new rectangle with text in it
                #
                # if settings['showClock'] and settings['showCPU'] and settings['showRAM']:  # Fine tuning of updating rect
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + 2*text_height+0))  # set last_rect size and position so it's one pixel bigger on every side. Removes glitches due to uneven monospace fonts
                # elif settings['showClock'] and settings['showRAM'] and not settings['showCPU']:
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showCPU'] and settings['showRAM'] and not settings['showClock']:
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showClock'] and settings['showCPU'] and not settings['showRAM']:
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showClock'] and settings['showCPU'] and not settings['showRAM']:
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showClock'] and not (settings['showCPU'] or settings['showRAM']):
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showCPU'] and not (settings['showClock'] or settings['showRAM']):
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # elif settings['showRAM'] and not (settings['showCPU'] or settings['showClock']):
                #     last_rect = ((main_rect.x-2, main_rect.y-2), (main_rect.width+4, main_rect.height + text_height+0))
                # # ----------  showCPU, showRAM, showClock only END -----------

            display_window.fill(settings["transparentColor"], last_rect)  # instead of filling the whole screen, fill only small rect
            # that saves about 70 to 100% time overall

            if devMeasureLoop:  # Activates a timer and exec ceiling for this loop
                if timer == length:
                    looping = False
                    return
                timer += 1

            if devFPSUnlimited:
                if devPrintFPS:
                    clock.tick(0)
                    print(int(clock.get_fps()))  # print fps in console (average)
                else:
                    clock.tick(0)  # limit the fps of the program
            else:
                if devPrintFPS:
                    clock.tick(settings["FPS"])
                    print(int(clock.get_fps()))  # print fps in console (average)
                else:
                    clock.tick(settings["FPS"])
            # print(_circlepoints.cache_info())
    finally:  # catch every exception and make sure to leave correctly, however it suppresses all tracebacks :(
        looping = False
        return  # Should be redundant


#
#
#
#
# --------- DEV FLAGS ----------
#  -------------------------------
timer = 0  # Initialization only

devDebugging = False  # To make it no longer TOPMOST
devMeasureLoop = False  # don't forget to make fps unlimited too
length = 20000
devShowOwnCPUPercentInstead = False  # Maybe wrong? Taskmanager different, lower.
devPrintFPS = False
devFPSUnlimited = False
devSnakevizIt = False  # no sleep(10) at the end of execution
devVisibleUpdateRect = False

#  -------------------------------
# --------- DEV FLAGS ----------
#
#
#
#


config = CaseConfigParser()
# parseList = CaseConfigParser(converters = {'list': lambda x: [i.strip() for i in x.split(',')]})
config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
config.read("config.ini")  # Read config file
if not config.has_section("SPARKLES") or not config.has_section("OTHER"):
    setDefaults()
    print("No config file exists. Writing new one with default values...")
    print(config)
cleanup_mei()  # see comment inside

# ---------------- Variables
blit_rect = []  # also
old_rect = []
old_blit_rect = []  # also
old_color_rect = []
text_Clock = ""
text_CPU = ""
getCPU = ""
text_RAM = ""
getRAM = ""
handleDeviceContext = 0
settings = {"": 0}
mousePosition = POINT()
_circle_cache = {}

readVariables()
settings["transparentColor"] = "#000000"

if settings["outlineColor"] == "#000000":
    settings["outlineColor"] = "#010101"

if settings["outlineThickness"] >= 2:  # Create alias of function to easily switch between them
    drawOutlineAroundText = textWithOutline2
else:
    drawOutlineAroundText = textWithOutline

# first is Clock, second CPU, third RAM
# stuff for the "match: case" in the loop
if settings["showRAM"] and not (settings["showCPU"] or settings["showClock"]):
    settings["activeThings"] = 1
elif settings["showCPU"] and not (settings["showClock"] or settings["showRAM"]):
    settings["activeThings"] = 2
elif settings["showClock"] and not (settings["showCPU"] or settings["showRAM"]):
    settings["activeThings"] = 3
elif settings["showCPU"] and settings["showRAM"] and not settings["showClock"]:
    settings["activeThings"] = 4
elif settings["showClock"] and settings["showRAM"] and not settings["showCPU"]:
    settings["activeThings"] = 5
elif settings["showClock"] and settings["showCPU"] and not settings["showRAM"]:
    settings["activeThings"] = 6
elif settings["showClock"] and settings["showCPU"] and settings["showRAM"]:
    settings["activeThings"] = 7
else:
    settings["activeThings"] = "000"

# ----------------- Window stuff
environ["SDL_VIDEO_WINDOW_POS"] = "0,0"  # Set window position to (0,0) as that is necessary now for some reason
pygame.init()
pygame.display.set_caption("ShitStuckToYourMouse - Other")  # title(stupid)
numDisplays = pygame.display.get_num_displays()

# ----------------- Multi-monitor handling
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
        i += 1
    highestHeight = max(info, key=lambda x: x[1])

    print("biggestHeight = ", highestHeight[1])
    print("combinedWidth = ", combinedWidth)
    print()

    if devDebugging:
        display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE)  # not TOPMOST
    else:
        display_window = pygame.display.set_mode((combinedWidth, highestHeight[1]), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
else:
    if devDebugging:
        display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE)  # not TOPMOST
    else:
        display_window = pygame.display.set_mode((0, 0), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future

# ------------------ more window stuff
display_window.fill(settings["transparentColor"])  # fill with transparent color set in win32gui.SetLayeredWindowAttributes
transparentColorTuple = tuple(int(settings["transparentColor"].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024
setFocus = windll.user32.SetFocus  # sets focus to window
handleWindowDeviceContext = pygame.display.get_wm_info()["window"]  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(handleWindowDeviceContext)  # set all kinds of option for win32 windows. Makes it transparent and click-through
displayInfo = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
windowWidth = int(displayInfo.current_w)
windowHeight = int(displayInfo.current_h)

# ----------------- Other
clock = pygame.time.Clock()  # for FPS limiting
font = pygame.font.Font(resource_path("./fonts/Nouveau_IBM_Stretch.TTF"), settings["fontSize"])  # Set Font and font size
outlineFont = pygame.font.Font(resource_path("./fonts/Nouveau_IBM_Stretch.TTF"), settings["fontSize"])
# font = pygame.freetype.Font("./fonts/Nouveau_IBM_Stretch.TTF", settings['fontSize'])
# font.antialiased = False
# font.style = 0 #  0 = normal. otherwise could become italic
# Topaz8: good above 12pt
# Pixel LCD-7: good above 8, 10
# Digital Dismay: good above 12
# ComputoMonospace: good above 8
# speculum: good for above 7
# ShareTechMono-Regular: 10, maybe 8 min
# OxygenMono-Regular: 10 plus
# Nouveau_IBM_Stretch: very small and suprisingly readable at 8, perfect at 9 and 12
# Nouveau_IBM: min 9, ok looking
text_height = font.get_linesize()  # sized_height_w when freetype

# ----------------- Conditionals
if settings["showColor"]:
    textColor = drawOutlineAroundText("(888, 888, 888)", font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
    blit_rect = textColor.get_rect()
    blit_rect.update(0, 0, blit_rect.width + 2, blit_rect.height + 2)
    colorSquare = pygame.Surface((42, 42))  # make surface
    colorSquare.fill(settings["fontColor"])  # fill surface with color
    color_rect = colorSquare.get_rect()  # get rectangle from surface
    old_color_rect = colorSquare.get_rect()  # second one
    old_blit_rect = colorSquare.get_rect()
    small_color_rect = pygame.Rect((1, 1), (40, 40))  # create smaller rectangle to fill with color from pixel
    old_rect = blit_rect  # initialize as well
    handleDeviceContext = GetDC(0)  # Get display content for measuring RGB value
    looping = True
elif settings["showImage"]:
    image = pygame.image.load(settings["imagePath"])
    blit_rect = image.get_rect()
    old_rect = blit_rect  # initialize as well
    looping = True
elif settings["showCPU"] or settings["showRAM"] or settings["showClock"]:
    looping = True
    if settings["showClock"]:
        text_Clock = drawOutlineAroundText("88:88:88.8888888", font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])  # draw text to a new Surface. 'transparentColor' is text background color
        # "88:88:88.8888888" defines size of resulting rectangle, so we don't have to text.get_rect() inside the while loop
        blit_rect = text_Clock.get_rect()
    if settings["showCPU"]:
        text_CPU = drawOutlineAroundText("CPU: 888.8", font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
        getCPU = Thread(target=cpu_Percent)  # define function as separate thread
        getCPU.start()  # start thread
        cpuPercent = 0.0  # initialize variable
        blit_rect = text_CPU.get_rect()
    if settings["showRAM"]:
        text_RAM = drawOutlineAroundText("RAM: 888.8", font, settings["fontColor"], settings["outlineColor"], settings["outlineThickness"])
        getRAM = Thread(target=ram_Percent)  # define function as separate thread
        getRAM.start()  # start thread
        ramPercent = 0.0  # initialize variable
        blit_rect = text_RAM.get_rect()
    if settings["showClock"] and settings["showCPU"] and settings["showRAM"]:
        blit_rect = text_Clock.get_rect()
        blit_rect = blit_rect.inflate(0, 2 * text_height + 2)
    elif settings["showClock"] and settings["showCPU"] or settings["showClock"] and settings["showRAM"]:
        blit_rect = text_Clock.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, text_height + 2)  # double height
    elif settings["showCPU"] and settings["showRAM"] and not settings["showClock"]:
        blit_rect = text_CPU.get_rect()  # get rectangle size and position (0,0) from Surface 'text', save as Rectangle
        blit_rect = blit_rect.inflate(0, text_height + 2)
    old_rect = blit_rect  # initialize as aswell
else:
    looping = False  # Interpreter should never reach this if using configuration GUI


setFocus(handleWindowDeviceContext)  # sets focus on pygame window

if devMeasureLoop:
    startTime = process_time()
loop(blit_rect, old_rect, old_blit_rect, old_color_rect)
if devMeasureLoop:
    endTime = process_time()
    # get execution time
    result = endTime - startTime
    print("CPU Execution time:", result, "seconds")

print("exited loop")
if settings["showColor"]:
    ReleaseDC(0, handleDeviceContext)
print("window handle released")
if settings["showCPU"]:
    getCPU.join(5)
if settings["showRAM"]:
    getRAM.join(5)
print("threads killed")
print("quitting")
pygame.quit()

if devMeasureLoop and not devSnakevizIt:
    sleep(10)
