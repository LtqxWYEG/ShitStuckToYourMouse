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


import configparser
import math
import random
from ctypes import byref, c_int, Structure, windll

import pygame
import pygame.gfxdraw
import pygame.math
#from pygame.math import Vector2
from os import path, listdir, environ
from pygame.locals import *  # for Color
from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, SetWindowPos
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED, WS_EX_TOOLWINDOW
from win32api import RGB
from time import sleep, process_time
from math import sqrt, sin
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
    settings["velocityFactorVector"] = float(config.get("SPARKLES", "velocityFactorVector"))
    settings["softClampVelocityVector"] = int(config.get("SPARKLES", "softClampVelocityVector"))
    settings["manualSecondVector"] = config.getlistfloat("SPARKLES", "manualSecondVector")
    settings["drag"] = float(config.get("SPARKLES", "drag"))
    settings["FPS"] = int(config.get("SPARKLES", "FPS"))
    settings["multitasking"] = int(config.get("SPARKLES", "multitasking"))
    settings["interpolateMouseMovement"] = config.getboolean("SPARKLES", "interpolateMouseMovement")
    settings["useOffset"] = config.getboolean("SPARKLES", "useOffset")
    settings["offsetX"] = int(config.get("SPARKLES", "offsetX"))
    settings["offsetY"] = int(config.get("SPARKLES", "offsetY"))
    settings["markPosition"] = config.getboolean("SPARKLES", "markPosition")
    settings["numParticles"] = int(config.get("SPARKLES", "numParticles"))
    settings["addRandomParticleVector"] = float(config.get("SPARKLES", "addRandomParticleVector"))

    settings["particleColor"] = str(config.get("SPARKLES", "particleColor"))
    settings["particleColorRandom"] = config.getboolean("SPARKLES", "particleColorRandom")
    settings["ageColor"] = config.getboolean("SPARKLES", "ageColor")
    settings["colorRollover"] = config.getboolean("SPARKLES", "colorRollover")
    settings["ageLinear"] = config.getboolean("SPARKLES", "ageLinear")
    settings["ageLinearSpeed"] = float(config.get("SPARKLES", "ageLinearSpeed"))
    settings["ageColorSpeed"] = float(config.get("SPARKLES", "ageColorSpeed"))
    settings["ageColorSlope"] = config.getboolean("SPARKLES", "ageColorSlope")
    settings["ageColorSlopeConcavity"] = float(config.get("SPARKLES", "ageColorSlopeConcavity"))
    settings["ageColorNoise"] = int(config.get("SPARKLES", "ageColorNoise"))
    settings["ageColorNoiseMod"] = float(config.get("SPARKLES", "ageColorNoiseMod"))

    settings["addRandomMouseInfluenceVector"] = config.getboolean("SPARKLES", "addRandomMouseInfluenceVector")
    settings["randomSecondVector"] = float(config.get("SPARKLES", "randomSecondVector"))
    settings["chaoticSecondVector"] = float(config.get("SPARKLES", "chaoticSecondVector"))
    settings["addChaosSecondVector"] = config.getboolean("SPARKLES", "addChaosSecondVector")
    settings["clampVelocitySecondVector"] = config.getboolean("SPARKLES", "clampVelocitySecondVector")

    settings["vectorRotation"] = float(config.get("SPARKLES", "vectorRotation"))
    settings["randomRotation"] = config.getboolean("SPARKLES", "randomRotation")
    settings["cumulativeVectorRotation"] = config.getboolean("SPARKLES", "cumulativeVectorRotation")
    settings["secondVectorRotation"] = config.getboolean("SPARKLES", "secondVectorRotation")
    settings["particleVectorRotation"] = config.getboolean("SPARKLES", "particleVectorRotation")

    settings["dynamic"] = config.getboolean("SPARKLES", "dynamic")
    settings["strengthMouseInfluenceVector"] = float(config.get("SPARKLES", "strengthMouseInfluenceVector"))
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
    def __init__(self, surface, pos, vector, container, color, randomHuePart, mouse_Speed_Pixel_Per_Frame):

        """
        surface : Surface :  The Surface to draw on.
        pos : (x,y) : tuple/list x,y position at time of creation.
        vector : (x,y) : tuple/list x,y velocity at time of creation.
        secondVector : (x,y) : tuple/list x,y secondVector effecting the particle.
        container : list : The passed in list that contains all the particles to draw.
        color : Color : Used so particles can be deleted.
        mouse_Speed_Pixel_Per_Frame : selfexplanatory
        """
        self.ageStep = None  # I don't understand why this IDE wants me to do this
        self.surface = surface
        self.pos = pygame.math.Vector2(pos)
        self.rotationRate = 0

        if settings["chaoticSecondVector"] > 0 and settings["clampVelocitySecondVector"]:
            self.maxVelocitySecondVector = settings["softClampVelocityVector"] / (33 / settings["chaoticSecondVector"])  # Add slider to adjust!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if settings["dynamic"]:
            if settings["addRandomMouseInfluenceVector"]:
                vector = [vector[0] + uniform(-(mouse_Speed_Pixel_Per_Frame * settings["strengthMouseInfluenceVector"]), (mouse_Speed_Pixel_Per_Frame * settings["strengthMouseInfluenceVector"])),
                          vector[1] + uniform(-(mouse_Speed_Pixel_Per_Frame * settings["strengthMouseInfluenceVector"]), (mouse_Speed_Pixel_Per_Frame * settings["strengthMouseInfluenceVector"])),]
            else:
                vector = [vector[0] + mouse_Vector[0],
                          vector[1] + mouse_Vector[1]]
        elif settings["addRandomParticleVector"] > 0:
            vector = [vector[0] + uniform(-settings["addRandomParticleVector"], settings["addRandomParticleVector"]),
                      vector[1] + uniform(-settings["addRandomParticleVector"], settings["addRandomParticleVector"])]
        else:
            vector = [vector[0], vector[1]]  # ... then just initialize with mouse_Vector

        if settings["velocityFactorVector"] > 0:
            self.particleVector = pygame.math.Vector2(vector) * settings["velocityFactorVector"]
        else:
            self.particleVector = pygame.math.Vector2(0)

        # Set second vector
        if settings["manualSecondVector"]:
            self.secondVector = pygame.math.Vector2(settings["manualSecondVector"])

        if settings["randomSecondVector"] > 0:  # Reset Vector2 to random.
            self.secondVector[0] = uniform(-settings["randomSecondVector"], settings["randomSecondVector"]) #/ 2
            self.secondVector[1] = uniform(-settings["randomSecondVector"], settings["randomSecondVector"]) #/ 2

        if settings["vectorRotation"] > 0:  # IMPOSSIBLE?: and self.counter == 0:  # initialize rotation rate
            if settings["randomRotation"]:
                self.rotationRate = uniform(-settings["vectorRotation"], settings["vectorRotation"]) / 100
            else:
                self.rotationRate = random.choice([settings["vectorRotation"] / 100, -settings["vectorRotation"] / 100])  # flicks between left and reight rotation
            # IMPOSSIBLE?: self.counter = 1  # set rotation speed only once at time of creation

        self.container = container
        self.color = Color(color)
        self.colorStatic = Color(color)
        hsva = self.color.hsva  # H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        if settings["particleColorRandom"]:
            hue = randomHuePart
        else:
            hue = hsva[0]  # unpack hue from hsva tuple
        hue += uniform(-settings["ageColorNoise"] + shiftAgeColorNoise, settings["ageColorNoise"] + shiftAgeColorNoise)
        hue = clamp(hue, 0, 359)  # Clamp hue within limits
        self.color.hsva = (hue, int(hsva[1]), int(hsva[2]))  # pack new hue value into hsva tuple
        self.surfSize = surface.get_size()
        self.drag = settings["drag"]
        self.age = settings["particleAge"]

    def updateParticle(self):
        #self.particleVector = (self.particleVector + self.secondVector) * self.drag
        self.particleVector *= self.drag
        self.pos += self.particleVector
        #self.rotationRate = self.rotationRate  # what?

        # if settings["randomSecondVector"] > 0:
        #     self.secondVector[0] = self.gravityX
        #     self.secondVector[1] = self.gravityY

        if settings["chaoticSecondVector"] > 0:
            if settings["addChaosSecondVector"]:
                self.secondVector[0] += uniform(-settings["chaoticSecondVector"], settings["chaoticSecondVector"]) * 0.05  # Add slider to adjust!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.secondVector[1] += uniform(-settings["chaoticSecondVector"], settings["chaoticSecondVector"]) * 0.05  # modify second vector and tame it
            else:
                self.secondVector[0] = uniform(-settings["chaoticSecondVector"], settings["chaoticSecondVector"]) * 2  # Reset second vector to random values
                self.secondVector[1] = uniform(-settings["chaoticSecondVector"], settings["chaoticSecondVector"]) * 2  # Reset second vector to random values
            if settings["clampVelocitySecondVector"]:
                self.secondVector[0] = clamp(self.secondVector[0], -self.maxVelocitySecondVector, self.maxVelocitySecondVector)
                self.secondVector[1] = clamp(self.secondVector[1], -self.maxVelocitySecondVector, self.maxVelocitySecondVector)

        if settings["vectorRotation"] > 0:  # Maybe bring particle vector rotation settings down here????
            if settings["secondVectorRotation"]:
                if settings["randomRotation"]:
                    self.rotationRate = uniform(-settings["vectorRotation"], settings["vectorRotation"]) / 20  # Add slider to adjust!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                if settings["cumulativeVectorRotation"]: # and not settings["particleVectorRotation"]:
                    self.rotationRate += self.rotationRate * 0.01  # Add slider to adjust!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                self.secondVector.rotate_ip_rad(self.rotationRate)
            if settings["particleVectorRotation"]:  # randomRotation for particle vector is in __init__
                if settings["cumulativeVectorRotation"]: # and not (settings["secondVectorRotation"] and settings["particleVectorRotation"]):
                    self.rotationRate += self.rotationRate * 0.01  # Add slider to adjust!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Popupmenu???? Add rotation decay!!!
                self.particleVector.rotate_ip_rad(self.rotationRate)
            self.rotationRate = clamp(self.rotationRate, -359, 359)

        # if self.particleVector.length > settings['softClampVelocityVector']:  # Clamp any huge velocities
        #     self.particleVector.length = settings['softClampVelocityVector']  # old version for vec2d.py
        if self.particleVector.length() > settings["softClampVelocityVector"]:  # Clamp any huge velocities
            self.particleVector = self.particleVector.normalize() * settings["softClampVelocityVector"]

        self.particleVector += self.secondVector  # Add second vector
        # Last motion related ------------------------------------------------------

        # Color manipulation -------------------------------------------------------
        self.ageStep = 100.0 / float(self.age)
        # Update color, and existence based on color:
        hsva = self.color.hsva  # Limits: H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]
        if settings["ageColor"]:
            if settings["ageLinear"]:
                hue += settings["ageLinearSpeed"]
                if settings["colorRollover"]:
                    if hue < 1 and settings["ageLinearSpeed"] < 0:
                        hue = 360
                    if hue > 359 and settings["ageLinearSpeed"] > 0:
                        hue = 0
            elif settings["ageColorSlope"]:
                hue += self.ageStep * (self.ageStep * ((self.ageStep / (10 ** settings["ageColorSlopeConcavity"])) / (10 ** settings["ageColorSlopeConcavity"])))
                if settings["colorRollover"]:
                    if hue < 1 and settings["ageColorSlopeConcavity"] < 0:
                        hue = 360
                    if hue > 359 and settings["ageColorSlopeConcavity"] > 0:
                        hue = 0
            else:
                hue += self.ageStep * settings["ageColorSpeed"]
                if settings["colorRollover"]:
                    if hue < 1 and settings["ageColorSpeed"] < 0:
                        hue = 360
                    if hue > 359 and settings["ageColorSpeed"] > 0:
                        hue = 0

        brightness = hsva[2]
        if settings["ageBrightnessMod"] > 0:
            brightness -= self.ageStep / settings["ageBrightnessMod"]

        if settings["ageBrightnessNoise"] > 0:
            brightness += uniform(-settings["ageBrightnessNoise"], settings["ageBrightnessNoise"])
            if brightness < 9 and self.age > 10:  # to avoid killing them with this
                brightness = 9

        brightness = clamp(brightness, 0, 99)
        hue = clamp(hue, 1, 357)  # Clamp hue within limits. Has to be 357, otherwise it will roll over with high ageBrightnessNoise for some reason

        self.age -= 1
        if brightness < 7 or self.age == 0:  # If brightness falls below 7, remove particle
            try:  # It's possible this particle was removed already.
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass
        else:
            self.color.hsva = (hue, int(hsva[1]), brightness)  # , alpha)
        
        if self.pos[0] < 0 or self.pos[0] > self.surfSize[0]:  # remove if outside surface bounds
            try:
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass
        elif self.pos[1] < 0 or self.pos[1] > self.surfSize[1]:  # remove if outside surface bounds
            try:
                self.color.hsva = (0, 0, 0)  # , alpha)
                self.container.remove(self)
            except ValueError:
                pass

        # if self.particleVector == [0, 0] or self.particleVector == [-0, 0] and settings["dynamic"]:
        #     try:  # It's possible this particle was removed already.
        #         self.color.hsva = (0, 0, 0)  # , alpha)
        #         self.container.remove(self)
        #     except ValueError:
        #         pass

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


def HEXtoRGB(hexa):
    rgb = []
    hexa = hexa.removeprefix('#')  # hexa.replace('#', '');  # = filter(lambda ch: ch not in "#", hexa) not working
    for n in (0, 2, 4):
        decimal = int(hexa[n:n + 2], 16)
        rgb.append(decimal)

    return tuple(rgb)


# @lru_cache(maxsize = 1024)  # TypeError: unhashable type: 'list' because particleContainer?
def loop(first_Run, transparent_Color, interpolate_Mouse_Movement, particle_Container, particle_Color, random_Hue, offset_X, offset_Y, mark_Position, num_Particles, level_Velocity, level_Num_Particles, second_Pos, mouse_Position, draw_Particles):
    global looping, devMeasureLoopLength, timer, mouse_Vector
    particle_Container_append = particle_Container.append
    ONE_THIRD = 1.0 / 3.0  # optimization, if I remember correctly
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
                # if event.type == pygame.MOUSEMOTION:
                #     # mouse_Position = pygame.mouse.get_pos()
                #     distanceX, distanceY = event.rel
                #     mouse_Speed_Pixel_Per_Frame = (distanceX ** 2 + distanceY ** 2) **0.5  # Pythagoras theorem.
                #     if devPrintMouseSpeed:
                #         print("Mouse speed by pygame: ", pygame.mouse.get_rel())  # --- Note: doesn't work because window is usually not focused or something like that

            windll.user32.GetCursorPos(byref(mouse_Position))  # get mouse cursor position and save it in the POINT() structure
            # mouse_Position = pygame.mouse.get_pos()
            first_Pos = (mouse_Position.x - offset_X, mouse_Position.y - offset_Y)
            if first_Run:
                mouse_Vector = (0, 0)
                first_Run = False
            else:
                mouse_Vector = ((first_Pos[0] - second_Pos[0]), (first_Pos[1] - second_Pos[1]))
            # fastest tuple arithmatic solution: (a[0] - b[0], a[1] - b[1]). NOT np, sub, lambda, zip...
            mouse_Speed_Pixel_Per_Frame = (mouse_Vector[0] ** 2 + mouse_Vector[1] ** 2) ** 0.5  # Pythagoras theorem

            if interpolate_Mouse_Movement:
                firstMiddlePos = (first_Pos[0] - (mouse_Vector[0] * ONE_THIRD), first_Pos[1] - (mouse_Vector[1] * ONE_THIRD))  # To triple resolution
                secondMiddlePos = (first_Pos[0] - (mouse_Vector[0] - (mouse_Vector[0] * ONE_THIRD)), first_Pos[1] - (mouse_Vector[1] - (mouse_Vector[1] * ONE_THIRD)))
                #thirdMiddlePos = (first_Pos[0] - (mouse_Vector[0] - (mouse_Vector[0] * 0.5)), first_Pos[1] - (mouse_Vector[1] - (mouse_Vector[1] * 0.5)))
            #  old position mouse speed pixel
            if devPrintMouseSpeed:
                print("Mouse speed in pixel distance traveled this frame: ", mouse_Speed_Pixel_Per_Frame)
                # print("Mouse speed by pygame: ", pygame.mouse.get_rel())  # --- Note: doesn't work because window is usually not focused or something like that

            if settings["dynamic"]:
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
                if settings["particleColorRandom"]:
                    random_Hue = randrange(360)
                if not interpolate_Mouse_Movement:
                    #print("pool")
                    particle_Container_append(ParticleClass(display_window, first_Pos, mouse_Vector, particle_Container, particle_Color, random_Hue, mouse_Speed_Pixel_Per_Frame))
                    y = -1
                elif y == 0:
                    particle_Container_append(ParticleClass(display_window, second_Pos, mouse_Vector, particle_Container, particle_Color, random_Hue, mouse_Speed_Pixel_Per_Frame))
                    y = 1
                elif y == 1:
                    particle_Container_append(ParticleClass(display_window, firstMiddlePos, mouse_Vector, particle_Container, particle_Color, random_Hue, mouse_Speed_Pixel_Per_Frame))
                    y = 2
                elif y == 2:
                    particle_Container_append(ParticleClass(display_window, secondMiddlePos, mouse_Vector, particle_Container, particle_Color, random_Hue, mouse_Speed_Pixel_Per_Frame))
                    y = 3
                # elif y == 3:
                #     particle_Container_append(ParticleClass(display_window, thirdMiddlePos, mouse_Vector, particle_Container, particle_Color, mouse_Speed_Pixel_Per_Frame))
                #     y = 4
                elif y == 3:
                    particle_Container_append(ParticleClass(display_window, first_Pos, mouse_Vector, particle_Container, particle_Color, random_Hue, mouse_Speed_Pixel_Per_Frame))
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
                # But I've read that they aren't closing anyway, so why only 1% cpu?
                # can it really be that updateParticle() is not the culprit, even though it takes over 50 to 70% of the process time?
                #

            second_Pos = first_Pos  # for getting mouse velocity
            #first_Run = False

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
            activeRect[0] -= settings['particleSize']  # otherwise bigger particles would leave render-area
            activeRect[1] -= settings['particleSize']
            activeRect[2] += 2*settings['particleSize']
            activeRect[3] += 2*settings['particleSize']  # otherwise bigger particles would leave render-area

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
                if timer == devMeasureLoopLength:
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
timer = 0  # Initialization only

devNotTopmost = False  # remove TOPMOST flag from window properties. Fix black screen using debugger
devDebugging = False  # To make it no longer TOPMOST and 400x400 in the upper left corner
devMeasureLoop = False  # don't forget to make fps unlimited too
devMeasureLoopLength = 300  # if  true
devMeasureLoopParticlesAmount = 20
devShowOwnCPUPercentInstead = False  # Maybe wrong? Taskmanager different, lower.
devPrintMouseSpeed = False
devPrintFPS = False
devFPSUnlimited = False
devSnakevizIt = True  # if devMeasureLoop is True: no sleep(10) at the end of execution
devVisibleUpdateRect = False
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
    pygame.display.set_caption("ShitStuckToYourMouse - Sparkles")  # title. (stupid)
    # pygame.mouse.set_visible(False)  # set mouse cursor visibility  --- Note: This does NOT work

    # --------- Initiatlize variables:
    startTime = 0
    looping = True
    firstRun = True
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
    # settings['levelVelocity'] = []
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

    # Multitasking particle number reduction
    i = 0
    if settings["multitasking"] > 1:
        settings["numParticles"] = int(settings["numParticles"] / settings["multitasking"])
        if settings["numParticles"] < 1:
            settings["numParticles"] = 1
        while i < 4:
            settings["levelNumParticles"][i] = int(settings["levelNumParticles"][i] / settings["multitasking"])
            i += 1

    #colorRGB = colorRGB
    colorRGB = Color(HEXtoRGB(settings["particleColor"]))
    hsva = colorRGB.hsva  # Limits: H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
    randomHue = hsva[0]

    numParticlesBackup = settings["numParticles"]
    mousePosition = POINT()
    mouseSpeedPixelPerFrame = 0
    firstPos = (mousePosition.x, mousePosition.y)  # Initiate positions
    secondPos = firstPos
    #mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))
    mouseVelocity = (0, 0)
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
    if (numDisplays := pygame.display.get_num_displays()) > 1:  # numDisplays declaration AND if
        print()
        print("----------- More than one displays detected -----------")
        print("pygame.display.get_num_displays = ", pygame.display.get_num_displays())
        print("pygame.display.Info = ", pygame.display.Info())
        print("pygame.display.get_desktop_sizes = ", pygame.display.get_desktop_sizes())
        print()
        info = pygame.display.get_desktop_sizes()
        # Get the highest display height and widest width
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
            display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE, vsync=0)  # not TOPMOST
        else:
            display_window = pygame.display.set_mode((combinedWidth, highestHeight[1]), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
    else:
        if devDebugging:
            display_window = pygame.display.set_mode((400, 400), pygame.RESIZABLE, vsync=0)  # not TOPMOST
        else:
            display_window = pygame.display.set_mode((0, 0), 0, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future

    display_window.fill(settings["transparentColor"])  # fill with transparent color set in win32gui.SetLayeredWindowAttributes
    setFocus = windll.user32.SetFocus  # sets focus to
    hWnd = pygame.display.get_wm_info()["window"]  # get window handle (hWnd => handleWindow) about this pygame window, in order to address it in setWindowAttributes()
    if devDebugging:
        SetWindowPos(hWnd, 0, 0, 0, 0, 0, SWP_NOSIZE)
    else:
        windll.user32.SetWindowLongPtrW(hWnd, GWL_EXSTYLE, windll.user32.GetWindowLongPtrW(hWnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW)  # no taskbar button
        SetWindowLong(hWnd, GWL_EXSTYLE, GetWindowLong(hWnd, GWL_EXSTYLE) | WS_EX_LAYERED | WS_EX_TRANSPARENT,)
        SetLayeredWindowAttributes(hWnd, RGB(*transparentColorTuple), 255, LWA_COLORKEY)
        if devNotTopmost:
            SetWindowPos(hWnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
        else:
            SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    # HWND_TOPMOST: Places the window above all non-topmost windows. The window maintains its topmost position even when it is deactivated. (Well, it SHOULD. But doesn't.)
    # It's not necessary to set the SWP_SHOWWINDOW flag.
    # SWP_NOMOVE: Retains the current position (ignores X and Y parameters).
    # SWP_NOSIZE: Retains the current size (ignores the cx and cy parameters).
    # GWL_EXSTYLE: Retrieve the extended window styles of the window.
    # WS_EX_TRANSPARENT: The window should not be painted until siblings beneath the window have been painted, making it transparent.
    # WS_EX_LAYERED: The window is a layered window, so that we can set attributes like color with SetLayeredWindowAttributes ...
    # LWA_COLORKEY: ... and make that color the transparent color of the window.
    # setWindowAttributes(handleWindowDeviceContext)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough
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
        firstRun,
        settings["transparentColor"],
        settings["interpolateMouseMovement"],
        particleContainer,
        settings["particleColor"],
        randomHue,
        settings["offsetX"],
        settings["offsetY"],
        settings["markPosition"],
        settings["numParticles"],
        settings["levelVelocity"],
        settings["levelNumParticles"],
        secondPos,
        mousePosition,
        drawParticles,
    )
    # loop(  # looks better
    #     firstRun,
    #     settings["transparentColor"],
    #     settings["interpolateMouseMovement"],
    #     particleContainer,
    #     settings["particleColor"],
    #     settings["particleColorRandom"],
    #     settings["offsetX"],
    #     settings["offsetY"],
    #     settings["markPosition"],
    #     settings["numParticles"],
    #     mouseSpeedPixelPerFrame,
    #     mouseVelocity,
    #     settings["levelVelocity"],
    #     settings["levelNumParticles"],
    #     secondPos,
    #     mousePosition,
    #     drawParticles,
    # )

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
