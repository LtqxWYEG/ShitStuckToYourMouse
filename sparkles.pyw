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


import configparser
from ctypes import byref, c_int, Structure, windll

import pygame
import pygame.gfxdraw
from pygame.math import Vector2
from os import path, listdir, environ
from pygame.locals import *  # for Color
from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, SetWindowPos
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED, WS_EX_TOOLWINDOW
from win32api import RGB
from time import sleep, process_time
from math import sqrt
from random import uniform, randrange

# pyximport.install(pyimport = True, inplace = False)  # change "inplace" to true to start compiling everytime to cython
# from functools import lru_cache
# from multiprocessing import Pool, Process, Pipe

# numpy is slower than random.random()


def cleanup_mei():
    """
    Rudimentary workaround for https://github.com/pyinstaller/pyinstaller/issues/2379
    """
    import sys
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
    def optionxform(self, optionstr):  # For things to keep case
        return optionstr

    def getlist(self, section, option):  # More case keeping
        value = self.get(section, option)
        return list(filter(None, (x.strip() for x in value.split(","))))

    def getlistint(self, section, option):  # The keeper of cases
        return [int(x) for x in self.getlist(section, option)]

    def getlistfloat(self, section, option):  # Case caseing of case
        return [float(x) for x in self.getlist(section, option)]


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def readVariables():
    global settings
    settings = dict()  # config.items('OTHER')

    settings["transparentColor"] = str(config.get("SPARKLES", "transparentColor"))
    settings["particleSize"] = int(config.get("SPARKLES", "particleSize"))
    settings["particleAge"] = int(config.get("SPARKLES", "particleAge"))
    settings["ageBrightnessMod"] = float(config.get("SPARKLES", "ageBrightnessMod"))
    settings["ageBrightnessNoise"] = int(config.get("SPARKLES", "ageBrightnessNoise"))
    settings["velocityMod"] = float(config.get("SPARKLES", "velocityMod"))
    settings["velocityClamp"] = int(config.get("SPARKLES", "velocityClamp"))
    settings["GRAVITY"] = config.getlistfloat("SPARKLES", "GRAVITY")
    settings["drag"] = float(config.get("SPARKLES", "drag"))
    settings["FPS"] = int(config.get("SPARKLES", "FPS"))
    settings["interpolateMouseMovement"] = config.getboolean("SPARKLES", "interpolateMouseMovement")
    settings["particleColor"] = str(config.get("SPARKLES", "particleColor"))
    settings["particleColorRandom"] = config.getboolean("SPARKLES", "particleColorRandom")
    settings["ageColor"] = config.getboolean("SPARKLES", "ageColor")
    settings["ageColorSpeed"] = float(config.get("SPARKLES", "ageColorSpeed"))
    settings["ageColorSlope"] = config.getboolean("SPARKLES", "ageColorSlope")
    settings["ageColorSlopeConcavity"] = float(config.get("SPARKLES", "ageColorSlopeConcavity"))
    settings["ageColorNoise"] = int(config.get("SPARKLES", "ageColorNoise"))
    settings["ageColorNoiseMod"] = float(config.get("SPARKLES", "ageColorNoiseMod"))
    settings["useOffset"] = config.getboolean("SPARKLES", "useOffset")
    settings["offsetX"] = int(config.get("SPARKLES", "offsetX"))
    settings["offsetY"] = int(config.get("SPARKLES", "offsetY"))
    settings["markPosition"] = config.getboolean("SPARKLES", "markPosition")
    settings["numParticles"] = int(config.get("SPARKLES", "numParticles"))
    settings["randomMod"] = int(config.get("SPARKLES", "randomMod"))
    settings["brownianMotion"] = float(config.get("SPARKLES", "brownianMotion"))
    settings["dynamic"] = config.getboolean("SPARKLES", "dynamic")
    settings["randomModDynamic"] = float(config.get("SPARKLES", "randomModDynamic"))
    settings["printMouseSpeed"] = config.getboolean("SPARKLES", "printMouseSpeed")
    settings["levelVelocity"] = config.getlistint("SPARKLES", "levelVelocity")
    settings["levelNumParticles"] = config.getlistint("SPARKLES", "levelNumParticles")


class Particle(object):
    """
    Superclass for other particle types.
    """

    def __init__(self):
        pass

    def updateParticle(self):
        pass


class ParticleClass(Particle):
    """
    Draw particles.
    """

    # @lru_cache()  # TypeError: unhashable type: 'list'
    def __init__(self, surface, pos, vel, gravity, container, color, mouse_Speed_Pixel_Per_Frame):

        """
        surface : Surface :  The Surface to draw on.
        pos : (x,y) : tuple/list x,y position at time of creation.
        vel : (x,y) : tuple/list x,y velocity at time of creation.
        gravity : (x,y) : tuple/list x,y gravity effecting the particle.
        container : list : The passed in list that contains all the particles to draw.
        color : Color : Used so particles can be deleted.
        mouse_Speed_Pixel_Per_Frame : self explanatory
        """
        self.ageStep = None  # I don't understand why this IDE wants me to do this
        self.surface = surface
        self.pos = Vector2(pos)
        if settings["dynamic"]:
            vel = [
                vel[0] + uniform(-(mouse_Speed_Pixel_Per_Frame * settings["randomModDynamic"]), (mouse_Speed_Pixel_Per_Frame * settings["randomModDynamic"])),
                vel[1] + uniform(-(mouse_Speed_Pixel_Per_Frame * settings["randomModDynamic"]), (mouse_Speed_Pixel_Per_Frame * settings["randomModDynamic"])),
            ]
        elif settings["randomMod"] > 0:
            vel = [vel[0] + uniform(-randrange(settings["randomMod"]), randrange(settings["randomMod"])), vel[1] + uniform(-randrange(settings["randomMod"]), randrange(settings["randomMod"]))]
        # else:
        #     vel = [vel[0], vel[1]]  # I forgot why commented out

        vel = [vel[0], vel[1]]
        if settings["velocityMod"] > 0:
            self.vel = Vector2(vel) * settings["velocityMod"]
        else:
            self.vel = Vector2(vel) * 0
        # if self.vel.length > settings['velocityClamp']:  # Clamp any huge velocities
        #     self.vel.length = settings['velocityClamp']  # old version for vec2d.py
        if self.vel.length() > settings["velocityClamp"]:  # Clamp any huge velocities
            self.vel = self.vel.normalize() * settings["velocityClamp"]

        self.gravity = Vector2(settings["GRAVITY"])
        self.container = container
        self.color = Color(color)
        self.colorFixed = Color(color)
        hsva = self.color.hsva  # H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]  # unpack hue from hsva tuple
        hue = hue + uniform(-settings["ageColorNoise"] + shiftAgeColorNoise, settings["ageColorNoise"] + shiftAgeColorNoise)
        hue = clamp(hue, 0, 359)  # Clamp hue within limits
        self.color.hsva = (hue, int(hsva[1]), int(hsva[2]))  # pack new hue value into hsva tuple
        self.surfSize = surface.get_size()
        self.drag = settings["drag"]
        self.age = settings["particleAge"]

    def updateParticle(self):
        # self.vel = (self.vel + self.gravity) * self.drag
        self.vel += self.gravity  # Optimization or not?
        self.vel *= self.drag  # Optimization or not?
        self.pos += self.vel

        if self.pos[0] < 0 or self.pos[0] > self.surfSize[0]:
            try:
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass
        elif self.pos[1] < 0 or self.pos[1] > self.surfSize[1]:
            try:
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass

        if settings["brownianMotion"] > 0:
            self.gravity[0] += uniform(-settings["brownianMotion"], settings["brownianMotion"])
            self.gravity[1] += uniform(-settings["brownianMotion"], settings["brownianMotion"])
        self.ageStep = 100.0 / float(self.age)
        # Update color, and existence based on color:
        hsva = self.color.hsva  # Limits: H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]
        if settings["ageColor"]:
            if settings["ageColorSlope"]:
                if self.colorFixed.hsva[0] > 180:
                    hue -= self.ageStep * (self.ageStep * ((self.ageStep / (10 ** settings["ageColorSlopeConcavity"])) / (10 ** settings["ageColorSlopeConcavity"])))
                else:
                    hue += self.ageStep * (self.ageStep * ((self.ageStep / (10 ** settings["ageColorSlopeConcavity"])) / (10 ** settings["ageColorSlopeConcavity"])))
            else:
                hue += self.ageStep * settings["ageColorSpeed"]

        brightness = hsva[2]
        brightness -= self.ageStep / settings["ageBrightnessMod"]
        if settings["ageBrightnessNoise"] > 0:
            brightness += uniform(-settings["ageBrightnessNoise"], settings["ageBrightnessNoise"])
        brightness = clamp(brightness, 0, 99)
        hue = clamp(hue, 0, 359)  # Clamp hue within limits

        self.age -= 1
        if brightness < 7 or self.age == 0:  # If brightness falls below 7, remove particle
            try:  # It's possible this particle was removed already.
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass
        else:
            self.color.hsva = (hue, int(hsva[1]), brightness)  # , alpha)

        if settings["particleSize"] <= 2:
            # Draw just a simple point:
            pygame.draw.rect(self.surface, self.color, (*self.pos, settings["particleSize"], settings["particleSize"]))
        else:
            pygame.draw.circle(self.surface, self.color, self.pos, settings["particleSize"] - 1)


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


def clamp(val, minval, maxval):
    if val < minval:
        return minval
    if val > maxval:
        return maxval
    return val


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW)  # no taskbar button
    SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED | WS_EX_TRANSPARENT,)
    SetLayeredWindowAttributes(hwnd, RGB(*transparentColorTuple), 255, LWA_COLORKEY)
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    # HWND_TOPMOST: Places the window above all non-topmost windows. The window maintains its topmost position even when it is deactivated. (Well, it SHOULD. But doesn't.)
    # It's not necessary to set the SWP_SHOWWINDOW flag.
    # SWP_NOMOVE: Retains the current position (ignores X and Y parameters).
    # SWP_NOSIZE: Retains the current size (ignores the cx and cy parameters).
    # GWL_EXSTYLE: Retrieve the extended window styles of the window.
    # WS_EX_TRANSPARENT: The window should not be painted until siblings beneath the window have been painted, making it transparent.
    # WS_EX_LAYERED: The window is a layered window, so that we can set attributes like color with SetLayeredWindowAttributes ...
    # LWA_COLORKEY: ... and make that color the transparent color of the window.


# @lru_cache(maxsize = 1024)  # TypeError: unhashable type: 'list' because particleContainer?
def loop(transparent_Color, interpolate_Mouse_Movement, particle_Container, particle_Color, particle_Color_Random, offset_X, offset_Y, mark_Position, num_Particles, print_Mouse_Speed, level_Velocity, level_Num_Particles, second_Pos, draw_Particles):
    global looping, length, timer
    particle_Container_append = particle_Container.append
    ONE_THIRD = 1.0 / 3.0
    oldActiveRect = pygame.Rect((0, 0), (0, 0))
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
            first_Pos = (mousePosition.x - offset_X, mousePosition.y - offset_Y)
            mouse_Velocity = ((first_Pos[0] - second_Pos[0]), (first_Pos[1] - second_Pos[1]))
            if interpolate_Mouse_Movement:
                firstMiddlePos = (first_Pos[0] - (mouse_Velocity[0] * ONE_THIRD), first_Pos[1] - (mouse_Velocity[1] * ONE_THIRD))  # To triple resolution
                secondMiddlePos = (first_Pos[0] - (mouse_Velocity[0] - (mouse_Velocity[0] * ONE_THIRD)), first_Pos[1] - (mouse_Velocity[1] - (mouse_Velocity[1] * ONE_THIRD)))
            # pygame.mouse.get_rel()  # --- Note: doesn't work because window is usually not focused or something like that

            # fastest tuple arithmatic solution: (a[0] - b[0], a[1] - b[1]). NOT np, sub, lambda, zip...
            mouse_Speed_Pixel_Per_Frame = sqrt((mouse_Velocity[0] * mouse_Velocity[0]) + (mouse_Velocity[1] * mouse_Velocity[1]))
            if settings["dynamic"]:
                # mouse_Speed_Pixel_Per_Frame = sqrt((mouse_Velocity[0] * mouse_Velocity[0]) + (mouse_Velocity[1] * mouse_Velocity[1]))
                if print_Mouse_Speed:
                    print("Mouse speed in pixel distance traveled this frame: ", mouse_Speed_Pixel_Per_Frame)
                if mouse_Speed_Pixel_Per_Frame == 0:  # For dynamic behaviour. No movement = no particles spawned
                    draw_Particles = False
                elif mouse_Speed_Pixel_Per_Frame < level_Velocity[0]:  # For dynamic behaviour.
                    num_Particles = numParticlesBackup
                    draw_Particles = True
                elif mouse_Speed_Pixel_Per_Frame < level_Velocity[1]:  # For dynamic behaviour.
                    num_Particles = level_Num_Particles[0]
                    draw_Particles = True
                elif mouse_Speed_Pixel_Per_Frame < level_Velocity[2]:  # For dynamic behaviour.
                    num_Particles = level_Num_Particles[1]
                    draw_Particles = True
                elif mouse_Speed_Pixel_Per_Frame < level_Velocity[3]:  # For dynamic behaviour.
                    num_Particles = level_Num_Particles[2]
                    draw_Particles = True
                else:
                    num_Particles = level_Num_Particles[3]
                    draw_Particles = True

            # ---multi processing entry

            # ------------

            x = 0
            y = 0
            while x < num_Particles and draw_Particles:
                if particle_Color_Random:
                    particle_Color = (randrange(256), randrange(256), randrange(256))
                if not interpolate_Mouse_Movement:
                    print("pool")
                    particle_Container_append(ParticleClass(display_window, first_Pos, mouse_Velocity, settings["GRAVITY"], particle_Container, particle_Color, mouse_Speed_Pixel_Per_Frame))
                    y = -1
                elif y == 0:
                    particle_Container_append(ParticleClass(display_window, firstMiddlePos, mouse_Velocity, settings["GRAVITY"], particle_Container, particle_Color, mouse_Speed_Pixel_Per_Frame))
                    y = 1
                elif y == 1:
                    particle_Container_append(ParticleClass(display_window, secondMiddlePos, mouse_Velocity, settings["GRAVITY"], particle_Container, particle_Color, mouse_Speed_Pixel_Per_Frame))
                    y = 2
                elif y == 2:
                    particle_Container_append(ParticleClass(display_window, first_Pos, mouse_Velocity, settings["GRAVITY"], particle_Container, particle_Color, mouse_Speed_Pixel_Per_Frame))
                    y = 0
                x += 1

            for part in particle_Container:
                part.updateParticle()
                # pool.map(part.updateParticle(), ())
                # if n == 0:
                #     pool.apply_async(part.updateParticle(), args=())
                #     n += 1
                # if n == 1:
                #     pool.apply_async(part.updateParticle(), args=())
                #     n += 1
                # if n == 2:
                #     pool.apply_async(part.updateParticle(), args=())
                #     n += 1
                # if n == 3:
                #     pool.apply_async(part.updateParticle(), args=())
                #     n += 1
                # if n == 4:
                #     n = 0
                # Doesn't work because it spawns a process for only one particle, then after 4 it stops creating new processes
                # until thex are finished with simulating theri one particle. :(
                # existing processes use only ~1% CPU time because they only have to update one particle.
                # So I'd need four processes that never stop.
                # But i've read that they aren't closing anyways, so why only 1% cpu?
                # can it really be that updateParticle() is not the culprit, even though it takes over 50 to 70% of the process time?
                #

            second_Pos = first_Pos  # for getting mouse velocity

            if mark_Position:
                pygame.draw.circle(display_window, "#ff0000", first_Pos, 2)  # Circle at origin point used by user for tuning offset

            partsXcoordinates = list()
            partsYcoordinates = list()
            if particle_Container:
                for part in particle_Container:
                    partsXcoordinates.append(int(part.pos.x))  # fill lists with all particle positions X and Y
                    partsYcoordinates.append(int(part.pos.y))
            else:
                partsXcoordinates = list((0, 0))  # at least initialize if no movement/particles
                partsYcoordinates = list((0, 0))

            rightestPart = max(partsXcoordinates)
            leftestPart = min(partsXcoordinates)
            lowestPart = max(partsYcoordinates)
            highestPart = min(partsYcoordinates)
            activeRect = pygame.Rect((leftestPart - 1, highestPart - 1), (rightestPart - leftestPart + 1, lowestPart - highestPart + 1))

            if mark_Position:
                if activeRect[2] < 50:  # if rect size less than 50 pixel, increase by 5
                    activeRect[2] += 5  # for the red dot. It otherwise leaves red marks
                if activeRect[3] < 50:
                    activeRect[3] += 5

            if devVisibleUpdateRect:
                highlight = pygame.Surface((activeRect.w + 2, activeRect.h + 2))
                highlight.fill("#ff0000")
                display_window.blit(highlight, activeRect)

            pygame.display.update((oldActiveRect, activeRect))
            oldActiveRect = pygame.Rect((activeRect[0] - 2, activeRect[1] - 2), (activeRect[2] + 4, activeRect[3] + 4))
            display_window.fill(transparent_Color, oldActiveRect)  # instead of filling the whole screen, fill only a small rect

            # pygame.display.update()  # old. Keep for now
            # display_window.fill(transparent_Color)

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

    finally:  # catch every exception and make sure to leave correctly, however it suppresses all tracebacks :(
        print("loop ended")  # Wait, does it? IDK anymore
        # looping = False
        # return  # Should be redundant


#
#
#
#
# --------- DEV FLAGS ----------
#  -------------------------------
timer = 0  # Initialization only

devDebugging = False  # To make it no longer TOPMOST and 400x400 in the upper left corner
devMeasureLoop = False  # don't forget to make fps unlimited too
length = 300
devMeasureLoopParticlesAmount = 20
devShowOwnCPUPercentInstead = False  # Maybe wrong? Taskmanager different, lower.
devPrintFPS = False
devFPSUnlimited = False
devSnakevizIt = True  # no sleep(10) at the end of execution if devMeasureLoop is True
devVisibleUpdateRect = False

#  -------------------------------
# --------- DEV FLAGS ----------
#
#
#
#


if __name__ == "__main__":
    # ---------- multiproc initialisation
    #
    # pool=Pool(processes=4)  # not yet working or wasting processing power itself
    # res=pool.apply_async(square,(10,))
    # print(res.get())

    cleanup_mei()  # see comment inside
    environ["SDL_VIDEO_WINDOW_POS"] = "0,0"  # Set window position to (0,0) as that is necessary now for some reason
    pygame.init()
    pygame.display.set_caption("ShitStuckToYourMouse - Sparkles")  # title(stupid)
    # pygame.mouse.set_visible(False)  # set mouse cursor visibility  --- Note: This does NOT work

    # --------- Initiatlize variables:
    startTime = 0
    looping = True
    # settings['numParticles'] = 0  #       initialization no longer necessary since dictionary??
    # settings['ageColorNoiseMod'] = 0
    # settings['ageColorNoise'] = 0
    # settings['transparentColor'] = ""
    # settings['GRAVITY'] = 0
    # settings['FPS'] = 0
    # settings['interpolateMouseMovement'] = False
    particleContainer = []
    # settings['particleColor'] = ""
    # settings['particleColorRandom'] = 0
    # settings['useOffset'] = False
    # settings['offsetX'] = 0
    # settings['offsetY'] = 0
    # settings['markPosition'] = 0
    # settings['dynamic'] = False
    # settings['printMouseSpeed'] = False
    # settings['levelVelocity'] = []
    # settings['levelNumParticles'] = []
    config = CaseConfigParser()
    parseList = CaseConfigParser(converters={"list": lambda x: [i.strip() for i in x.split(",")]})
    config.read("config.ini")  # Read config file
    config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
    if not config.has_section("SPARKLES"):
        setDefaults()
    readVariables()
    drawParticles: bool = True  # For dynamic: Don't draw particles if mouse doesn't move
    particleContainer = []
    mostUppereLeftPart = []
    numParticlesBackup = settings["numParticles"]
    mouseSpeedPixelPerFrame = 0
    mousePosition = POINT()
    firstPos = (mousePosition.x, mousePosition.y)  # Initiate positions
    secondPos = firstPos
    mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))
    blitRectSize = 5
    clock = pygame.time.Clock()  # for FPS limiting
    info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
    if devMeasureLoop:
        settings["numParticles"] = devMeasureLoopParticlesAmount
        settings["particleSize"] = 2
        settings["dynamic"] = False

    # ---------- Correct input errors and precalculate things:
    settings["ageColorNoiseMod"] = clamp(settings["ageColorNoiseMod"], 0.0, 1.0)
    ageColorNoiseRange = [x for x in range(-settings["ageColorNoise"], settings["ageColorNoise"] + 1)]
    shiftAgeColorNoise = ageColorNoiseRange[round((settings["ageColorNoise"] * 2) * settings["ageColorNoiseMod"])]
    transparentColorTuple = tuple(int(settings["transparentColor"].lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))  # convert settings['transparentColor'] to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024

    # ---------- Set things up:
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
            display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE)  # not TOPMOST
        else:
            display_window = pygame.display.set_mode((combinedWidth, highestHeight[1]), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
    else:
        if devDebugging:
            display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE)  # not TOPMOST
        else:
            display_window = pygame.display.set_mode((0, 0), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
    display_window.fill(settings["transparentColor"])  # fill with transparent color set in win32gui.SetLayeredWindowAttributes
    setFocus = windll.user32.SetFocus  # sets focus to
    handleWindowDeviceContext = pygame.display.get_wm_info()["window"]  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
    setWindowAttributes(handleWindowDeviceContext)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough
    if not settings["useOffset"]:
        settings["offsetX"] = 0
        settings["offsetY"] = 0

    # --------- Optimizations:
    # ------- RECONSIDER THIS --------
    # clock_tick = clock.tick
    # display_window_fill = display_window.fill
    # windll_user32_GetCursorPos = windll.user32.GetCursorPos
    # pygame_display_update = pygame.display.update
    # ------- RECONSIDER THIS --------

    # ---------- Start the lööp:
    # setFocus(handleWindowDeviceContext)  # sets focus on pygame window
    # with cProfile.Profile() as pr:
    if devMeasureLoop:
        startTime = process_time()

    loop(  # looks better
        settings["transparentColor"],
        settings["interpolateMouseMovement"],
        particleContainer,
        settings["particleColor"],
        settings["particleColorRandom"],
        settings["offsetX"],
        settings["offsetY"],
        settings["markPosition"],
        settings["numParticles"],
        settings["printMouseSpeed"],
        settings["levelVelocity"],
        settings["levelNumParticles"],
        secondPos,
        drawParticles,
    )

    if devMeasureLoop:
        endTime = process_time()
        # get execution time
        result = endTime - startTime
        print("CPU Execution time:", result, "seconds")
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()

    # loop()
    # ...
    pygame.quit()

if devMeasureLoop and not devSnakevizIt:
    sleep(10)
