
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

import configparser
from math import sqrt, pow
from random import randrange, uniform
from ctypes import byref, c_int, Structure, windll

import pygame
import pygame.gfxdraw
from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, GetDC, ReleaseDC
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED
from win32api import RGB
from pygame.locals import *  # for Color
from vec2d import Vec2d
import cProfile
import pstats



def cleanup_mei():
    """
    Rudimentary workaround for https://github.com/pyinstaller/pyinstaller/issues/2379
    """
    from os import path, listdir
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
    def optionxform(self, optionstr):  # To keep thing's FUCKING case! WTH is the problem, configparser devs?
        return optionstr

    def getlist(self, section, option):  # Seriously, what is wrong with them? Why is something so basic not implemented? FF
        value = self.get(section, option)
        return list(filter(None, (x.strip() for x in value.split(','))))

    def getlistint(self, section, option):  # It's so annoying.
        return [int(x) for x in self.getlist(section, option)]

    def getlistfloat(self, section, option):  # No wonder ppl use the horrible JSON... (Although I have no idea if that's better)
        return [float(x) for x in self.getlist(section, option)]


config = CaseConfigParser()
parseList = CaseConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
config.read("config.ini")  # Read config file
config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


# settings = dict(config.items('SPARKLES'))
def readVariables():  # --- I do not like this, but now it's done and I don't care anymore
    global config, transparentColor, particleSize, particleAge, ageBrightnessMod, ageBrightnessNoise, velocityMod,\
        velocityClamp, GRAVITY, drag, FPS, interpolateMouseMovement, particleColor, particleColorRandom, ageColor, ageColorSpeed,\
        ageColorSlope, ageColorSlopeConcavity, ageColorNoise, ageColorNoiseMod, useOffset, offsetX, offsetY, markPosition,\
        numParticles, randomMod, dynamic, randomModDynamic, printMouseSpeed, levelVelocity, levelNumParticles  # God damn it
    transparentColor = str(config.get("SPARKLES", "transparentColor"))
    particleSize = int(config.get("SPARKLES", "particleSize"))
    particleAge = int(config.get("SPARKLES", "particleAge"))
    ageBrightnessMod = float(config.get("SPARKLES", "ageBrightnessMod"))
    ageBrightnessNoise = int(config.get("SPARKLES", "ageBrightnessNoise"))
    velocityMod = float(config.get("SPARKLES", "velocityMod"))
    velocityClamp = int(config.get("SPARKLES", "velocityClamp"))
    GRAVITY = config.getlistfloat("SPARKLES", "GRAVITY")
    drag = float(config.get("SPARKLES", "drag"))
    FPS = int(config.get("SPARKLES", "FPS"))
    interpolateMouseMovement = config.getboolean("SPARKLES", "interpolateMouseMovement")
    particleColor = str(config.get("SPARKLES", "particleColor"))
    particleColorRandom = config.getboolean("SPARKLES", "particleColorRandom")
    ageColor = config.getboolean("SPARKLES", "ageColor")
    ageColorSpeed = float(config.get("SPARKLES", "ageColorSpeed"))
    ageColorSlope = config.getboolean("SPARKLES", "ageColorSlope")
    ageColorSlopeConcavity = float(config.get("SPARKLES", "ageColorSlopeConcavity"))
    ageColorNoise = int(config.get("SPARKLES", "ageColorNoise"))
    ageColorNoiseMod = float(config.get("SPARKLES", "ageColorNoiseMod"))
    useOffset = config.getboolean("SPARKLES", "useOffset")
    offsetX = int(config.get("SPARKLES", "offsetX"))
    offsetY = int(config.get("SPARKLES", "offsetY"))
    markPosition = config.getboolean("SPARKLES", "markPosition")
    numParticles = int(config.get("SPARKLES", "numParticles"))
    randomMod = int(config.get("SPARKLES", "randomMod"))
    dynamic = config.getboolean("SPARKLES", "dynamic")
    randomModDynamic = float(config.get("SPARKLES", "randomModDynamic"))
    printMouseSpeed = config.getboolean("SPARKLES", "printMouseSpeed")
    levelVelocity = config.getlistint("SPARKLES", "levelVelocity")
    levelNumParticles = config.getlistint("SPARKLES", "levelNumParticles")
    # I didn't like this whole ordeal. I suck and expect things to be more easy. :P


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    setWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
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


class Particle(object):
    """
    Superclass for other particle types.
    """

    def __init__(self, surface, pos, vel, gravity, container, mouseSpeedPixelPerFrame, color):
        """
        surface : Surface :  The Surface to draw on.
        pos : (x,y) : tuple/list x,y position at time of creation.
        vel : (x,y) : tuple/list x,y velocity at time of creation.
        gravity : (x,y) : tuple/list x,y gravity effecting the particle.
        container : list : The passed in list that contains all the particles to draw.
            Used so particles can be deleted.
        """
        self.surface = surface
        self.pos = Vec2d(pos)
        if dynamic:
            vel = [vel[0]+uniform(-(mouseSpeedPixelPerFrame * randomModDynamic), (mouseSpeedPixelPerFrame * randomModDynamic)),
                   vel[1]+uniform(-(mouseSpeedPixelPerFrame * randomModDynamic), (mouseSpeedPixelPerFrame * randomModDynamic))]
        else:
            vel = [vel[0]+uniform(-randrange(randomMod), randrange(randomMod)),
                   vel[1]+uniform(-randrange(randomMod), randrange(randomMod))]
        vel = [vel[0], vel[1]]
        self.vel = Vec2d(vel) * velocityMod

        if self.vel.length > velocityClamp:  # Clamp any huge velocities
            self.vel.length = velocityClamp

        self.gravity = Vec2d(gravity)
        self.container = container

        self.color = Color(color)
        hsva = self.color.hsva  # H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]  # unpack hue from hsva tuple
        hue = hue + uniform(-ageColorNoise + shiftAgeColorNoise, ageColorNoise + shiftAgeColorNoise)
        hue = clamp(hue, 0, 359)  # Clamp hue within limits
        self.color.hsva = (hue, int(hsva[1]), int(hsva[2]))  # pack new hue value into hsva tuple

        self.surfSize = surface.get_size()
        self.drag = drag

    def updateParticle(self):
        global oldParticleContainer
        """
        Update position and existence per frame.
        """
        self.vel = (self.vel + self.gravity) * self.drag
        self.pos = self.pos + self.vel
        if self.outOfBounds():
            try:
                self.container.remove(self)
            except ValueError:
                pass

    def drawParticle(self):
        """
        Override with subclass drawing method.
        """
        pass

    def outOfBounds(self):
        """
        Calculate if particle still exists based on exiting the screen.
        """
        outOfBounds = False
        if self.pos[0] < 0 or self.pos[0] > self.surfSize[0]:
            outOfBounds = True
        elif self.pos[1] < 0 or self.pos[1] > self.surfSize[1]:
            outOfBounds = True
        return outOfBounds


class ParticleClass(Particle):
    """
    Draw particles.
    """

    def __init__(self, surface, pos, vel, gravity, container, color, mouseSpeedPixelPerFrame):
        """
        age : How long the particle will live.  Will get darker as it gets older.
        """
        # Init superclass:
        super(ParticleClass, self).__init__(surface, pos, vel, gravity, container, mouseSpeedPixelPerFrame, color)
        self.age = particleAge

    def updateParticle(self):
        # Override superclass, but call to superclass method first:
        super(ParticleClass, self).updateParticle()
        self.ageStep = 100.0/float(self.age)
        # Update color, and existance based on color:
        hsva = self.color.hsva  # Limits: H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]
        if ageColor:
            if ageColorSlope:
                hue -= self.ageStep * (self.ageStep * ((self.ageStep / (10 ** ageColorSlopeConcavity)) / (10 ** ageColorSlopeConcavity)))
            else:
                hue += self.ageStep * ageColorSpeed
            #hue = hue + random.uniform(-ageColorNoise + shiftAgeColorNoise, ageColorNoise + shiftAgeColorNoise)

        brightness = hsva[2]
        brightness -= self.ageStep / ageBrightnessMod
        brightness = brightness + uniform(-ageBrightnessNoise, ageBrightnessNoise)
        brightness = clamp(brightness, 0, 99)
        hue = clamp(hue, 0, 359)  # Clamp hue within limits
        # alpha = hsva[3]  # alpha is not used with pygame.draw :(
        # alpha -= self.brightnessStep
        self.age -= 1
        if brightness < 7 or self.age == 0:  # If brightness falls below 7, remove particle
            try:  # It's possible this particle was removed already by the superclass.
                self.container.remove(self)
            except ValueError:
                pass
        else:
            self.color.hsva = (hue, int(hsva[1]), brightness)  # , alpha)

    def drawParticle(self):
        if particleSize <= 2:
            # Draw just a simple point:
            pygame.draw.rect(self.surface, self.color, ((self.pos[0], self.pos[1]), (particleSize, particleSize)))
        else:
            pygame.draw.circle(self.surface, self.color, (self.pos[0], self.pos[1]), particleSize-1)

    def getParticleRect(self):
        particleRect = ((self.pos[0], self.pos[1]), (particleSize, particleSize))
        return particleRect


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


def clamp(val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val


def loop():
    global config, transparentColor, particleSize, particleAge, ageBrightnessMod, ageBrightnessNoise, velocityMod, \
        velocityClamp, GRAVITY, drag, FPS, interpolateMouseMovement, particleColor, particleColorRandom, ageColor, ageColorSpeed, \
        ageColorSlope, ageColorSlopeConcavity, ageColorNoise, ageColorNoiseMod, useOffset, offsetX, offsetY, markPosition, \
        numParticles, randomMod, dynamic, randomModDynamic, printMouseSpeed, levelVelocity, levelNumParticles, firstPos, \
        secondPos, mouseVelocity, ageColorNoiseRange, shiftAgeColorNoise, drawParticles, mouseSpeedPixelPerFrame
    loop = True
    while loop:
        clock.tick(FPS)  # limit the fps of the program
        display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes
        windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure
        firstPos = (mousePosition.x - offsetX, mousePosition.y - offsetY)
        mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))
        if interpolateMouseMovement:
            firstMiddlePos = (firstPos[0] - (mouseVelocity[0] / 3),
                              firstPos[1] - (mouseVelocity[1] / 3))  # To triple resolution
            secondMiddlePos = (firstPos[0] - (mouseVelocity[0] - (mouseVelocity[0] / 3)),
                               firstPos[1] - (mouseVelocity[1] - (mouseVelocity[1] / 3)))
        # pygame.mouse.get_rel()  # --- Note: doesn't work because window is usually not focused or something like that

        for event in pygame.event.get():
            setFocus(hwnd)  # Brings window back to focus if any key or mouse button is pressed.
            # This is done in order to put the display_window back on top of z-order, because HWND_TOPMOST doesn't work. (Probably because display_window is a child window)
            # (Doing this too often, like once per frame, crashes pygame without error message. Probably some Windows internal spam protection thing)
            if event.type == pygame.QUIT:
                loop = False
            # elif event.type == pygame.KEYDOWN:  # --- Note: practically uneccessary because window isn't focused
            #     if event.key == pygame.K_ESCAPE:
            #         loop = False

        # fastest tuple arithmatic solution: (a[0] - b[0], a[1] - b[1]). NOT np, sub, lambda, zip...
        if dynamic is True:
            mouseSpeedPixelPerFrame = sqrt(pow(mouseVelocity[0], 2) + pow(mouseVelocity[1], 2))
            if printMouseSpeed: print("Mouse speed in pixel distance traveled this frame: ", mouseSpeedPixelPerFrame)
            drawParticles = False
            if mouseSpeedPixelPerFrame == 0:
                drawParticles = False
            elif mouseSpeedPixelPerFrame < levelVelocity[0]:
                numParticles = numParticlesBackup
                drawParticles = True
            elif mouseSpeedPixelPerFrame < levelVelocity[1]:
                numParticles = levelNumParticles[0]
                drawParticles = True
            elif mouseSpeedPixelPerFrame < levelVelocity[2]:
                numParticles = levelNumParticles[1]
                drawParticles = True
            elif mouseSpeedPixelPerFrame < levelVelocity[3]:
                numParticles = levelNumParticles[2]
                drawParticles = True
            else:
                numParticles = levelNumParticles[3]
                drawParticles = True

        x = 0
        y = 0
        while x < numParticles and drawParticles is True:
            if particleColorRandom is True: particleColor = (randrange(256), randrange(256), randrange(256))
            if not interpolateMouseMovement:
                particleContainer.append(ParticleClass(display_window, firstPos, mouseVelocity, GRAVITY, particleContainer, particleColor, mouseSpeedPixelPerFrame))
                y = -1
            elif y == 0:
                particleContainer.append(ParticleClass(display_window, firstMiddlePos, mouseVelocity, GRAVITY, particleContainer, particleColor, mouseSpeedPixelPerFrame))
                y = 1
            elif y == 1:
                particleContainer.append(ParticleClass(display_window, secondMiddlePos, mouseVelocity, GRAVITY, particleContainer, particleColor, mouseSpeedPixelPerFrame))
                y = 2
            elif y == 2:
                particleContainer.append(ParticleClass(display_window, firstPos, mouseVelocity, GRAVITY, particleContainer, particleColor, mouseSpeedPixelPerFrame))
                y = 0
            x += 1

        for part in particleContainer:
            part.updateParticle()
            part.drawParticle()

        ''' I tried to optimize the code by only updating the used display area instead of the whole screen.
        Performance of pygame.display.update() depends on the following: (obviously)
        - area of rectangle
        - number of rectangles
        If one rectangle is smaller than the other it is drawn faster. I use that in other.py to speed up drawing text alongside the mouse.
        There it makes a big difference if I update the whole screen or just the small rectangle with the text. (times two)
            (If drawColor is true, four rectangles are updated. But that is still faster than updating the whole screen.)

        The following code produces hundreds of rectangles. In this case the huge amount of rectangles are negating any performance
        improvements I gained by reducing the area down to a combined couple hundred pixels.

        # for part in particleContainer:
        #     partRect = part.getParticleRect()
        #     particleContainerRects.append(partRect)
        # listOfRects.extend(oldParticleContainer)
        # listOfRects.extend(particleContainerRects)
        # pygame.display.update(listOfRects)
        # oldParticleContainer = []
        # particleContainerRects = []
        # listOfRects = []
        # for part in particleContainer:
        #     partRect = part.getParticleRect()
        #     oldParticleContainer.append(partRect)
        '''

        if markPosition is True:
            markPositionRect = pygame.draw.circle(display_window, "#ff0000", firstPos, 2).get_rect()  # used for tuning offset
        pygame.display.update()
        secondPos = firstPos  # for getting mouse velocity
    # while ends here


cleanup_mei()  # see comment inside
pygame.init()
pygame.display.set_caption('PoopStuckToYourMouse - Sparkles')  # title(stupid)
# pygame.mouse.set_visible(False)  # set mouse cursor visibility  --- Note: This does NOT work


# --------- Initiate variables:
if not config.has_section("SPARKLES"):
    setDefaults()
readVariables()
drawParticles = True  # For dynamic: Don't draw particles if mouse doesn't move
particleContainer = []

# global oldParticleContainer
# particleContainerRects = []
# oldParticleContainer = []
# listOfRects = []
# markPositionRect = (((0, 0), (0, 0)), ((0, 0), (0, 0)))
# oldMarkPositionRect = markPositionRect

numParticlesBackup = numParticles
mouseSpeedPixelPerFrame = 0
mousePosition = POINT()
firstPos = (mousePosition.x, mousePosition.y)  # Initiate positions
secondPos = firstPos
mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))
clock = pygame.time.Clock()  # for FPS limiting
info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
setWindowPos = windll.user32.SetWindowPos  # see setWindowAttributes()
setFocus = windll.user32.SetFocus  # sets focus to
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # flags to set in pygame.display.set_mode
# FULLSCREEN: Create a fullscreen display
# DOUBLEBUF: Double buffering. Creates a separate block of memory to apply all the draw routines and then copying that block (buffer) to video memory. (Thanks, Foon)
# HWSURFACE: hardware accelerated window, only in FULLSCREEN. (Uses memory on video card)


# ---------- Correct input errors and precalculate things:
ageColorNoiseMod = clamp(ageColorNoiseMod, 0.0, 1.0)
ageColorNoiseRange = [x for x in range(-ageColorNoise, ageColorNoise+1)]
shiftAgeColorNoise = ageColorNoiseRange[round((ageColorNoise * 2) * ageColorNoiseMod)]
transparentColorTuple = tuple(int(transparentColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024


# ---------- Set things up:
display_window = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with tranparent color set in win32gui.SetLayeredWindowAttributes
hwnd = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(hwnd)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough
if not useOffset:
    offsetX = 0
    offsetY = 0

# ---------- Start the lööp:
setFocus(hwnd)  # sets focus on pygame window
with cProfile.Profile(timeunit=0.000000, subcalls=True, builtins=True) as pr:
    loop()
stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.print_stats()

#loop()
# ...
pygame.quit()

''' performance analysis
cumsec  per call    name
7.033	0.007466	~:0(<method 'tick' of 'Clock' objects>)             # highest per-call
4.668	1.23e-05	sparkles.py:223(updateParticle)
3.014	7.94e-06	sparkles.py:179(updateParticle)
1.678	0.001781	~:0(<built-in method pygame.display.flip>)          # second highest
0.9605	1.265e-06	vec2d.py:91(__add__)
0.9322	2.456e-06	sparkles.py:253(drawParticle)
0.7923	2.087e-06	sparkles.py:198(outOfBounds)
0.6166	0.0006545	~:0(<method 'fill' of 'pygame.Surface' objects>)    # third highest
0.5493	1.414e-06	vec2d.py:140(__mul__)

update instead of flip:
per call
0.001688	~:0(<built-in method pygame.display.update>)
0.001781	~:0(<built-in method pygame.display.flip>)

'''