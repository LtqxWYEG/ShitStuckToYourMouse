
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
import math
import random
from ctypes import byref, c_int, Structure, windll

import pygame
import pygame.gfxdraw
import win32api
import win32con
import win32gui
from pygame.locals import *  # for Color
from vec2d import Vec2d


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


# settings = dict(config.items('SETTINGS'))
def readVariables():  # --- I do not like this, but now it's done and I don't care anymore
    global config, transparentColor, particleSize, particleAge, ageBrightnessMod, ageBrightnessNoise, velocityMod,\
        velocityClamp, GRAVITY, drag, FPS, particleColor, particleColorRandom, ageColor, ageColorSpeed, ageColorSlope,\
        ageColorSlopeConcavity, ageColorNoise, ageColorNoiseMod, useOffset, offsetX, offsetY, markPosition, numParticles,\
        randomMod, dynamic, randomModDynamic, printMouseSpeed, levelVelocity, levelNumParticles  # God damn it
    transparentColor = str(config.get("SETTINGS", "transparentColor"))
    particleSize = int(config.get("SETTINGS", "particleSize"))
    particleAge = int(config.get("SETTINGS", "particleAge"))
    ageBrightnessMod = float(config.get("SETTINGS", "ageBrightnessMod"))
    ageBrightnessNoise = int(config.get("SETTINGS", "ageBrightnessNoise"))
    velocityMod = float(config.get("SETTINGS", "velocityMod"))
    velocityClamp = int(config.get("SETTINGS", "velocityClamp"))
    GRAVITY = config.getlistfloat("SETTINGS", "GRAVITY")
    drag = float(config.get("SETTINGS", "drag"))
    FPS = int(config.get("SETTINGS", "FPS"))
    particleColor = str(config.get("SETTINGS", "particleColor"))
    particleColorRandom = config.getboolean("SETTINGS", "particleColorRandom")
    ageColor = config.getboolean("SETTINGS", "ageColor")
    ageColorSpeed = float(config.get("SETTINGS", "ageColorSpeed"))
    ageColorSlope = config.getboolean("SETTINGS", "ageColorSlope")
    ageColorSlopeConcavity = float(config.get("SETTINGS", "ageColorSlopeConcavity"))
    ageColorNoise = int(config.get("SETTINGS", "ageColorNoise"))
    ageColorNoiseMod = float(config.get("SETTINGS", "ageColorNoiseMod"))
    useOffset = config.getboolean("SETTINGS", "useOffset")
    offsetX = int(config.get("SETTINGS", "offsetX"))
    offsetY = int(config.get("SETTINGS", "offsetY"))
    markPosition = config.getboolean("SETTINGS", "markPosition")
    numParticles = int(config.get("SETTINGS", "numParticles"))
    randomMod = float(config.get("SETTINGS", "randomMod"))
    dynamic = config.getboolean("SETTINGS", "dynamic")
    randomModDynamic = float(config.get("SETTINGS", "randomModDynamic"))
    printMouseSpeed = config.getboolean("SETTINGS", "printMouseSpeed")
    levelVelocity = config.getlistint("SETTINGS", "levelVelocity")
    levelNumParticles = config.getlistint("SETTINGS", "levelNumParticles")
    # I didn't like this whole ordeal. I suck and expect things to be more easy. :P


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
            vel = [vel[0]+random.uniform(-(mouseSpeedPixelPerFrame / randomModDynamic), (mouseSpeedPixelPerFrame / randomModDynamic)),
                   vel[1]+random.uniform(-(mouseSpeedPixelPerFrame / randomModDynamic), (mouseSpeedPixelPerFrame / randomModDynamic))]
        else:
            vel = [vel[0]+random.uniform(-randomMod, randomMod), vel[1]+random.uniform(-randomMod, randomMod)]
        vel = [vel[0], vel[1]]
        self.vel = Vec2d(vel) / velocityMod

        if self.vel.length > velocityClamp:  # Clamp any huge velocities
            self.vel.length = velocityClamp

        self.gravity = Vec2d(gravity)
        self.container = container
        self.color = Color(color)

        self.surfSize = surface.get_size()
        self.drag = drag

    def update(self):
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

    def draw(self):
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


class ParticleSparkle(Particle):
    """
    Draw particle 'sparkles'.
    """

    def __init__(self, surface, pos, vel, gravity, container, color, mouseSpeedPixelPerFrame):
        """
        age : How long the particle will live.  Will get darker as it gets older.
        """
        # Init superclass:
        super(ParticleSparkle, self).__init__(surface, pos, vel, gravity, container, mouseSpeedPixelPerFrame, color)
        self.age = particleAge

    def update(self):
        # Override superclass, but call to superclass method first:
        super(ParticleSparkle, self).update()
        self.ageStep = 100.0/float(self.age)
        # Update color, and existance based on color:
        hsva = self.color.hsva  # H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        hue = hsva[0]
        if ageColor:
            if ageColorSlope:
                hue -= self.ageStep / ageColorSlopeConcavity
            else:
                hue -= self.ageStep * ageColorSpeed
            hue = hue + random.uniform(-ageColorNoise + shiftAgeColorNoise, ageColorNoise + shiftAgeColorNoise)
            hue = clamp(hue, 0, 359)  # Clamp Noise within limits
        brightness = hsva[2]
        brightness -= self.ageStep / ageBrightnessMod
        self.age -= 1
        brightness = brightness + random.uniform(-ageBrightnessNoise, ageBrightnessNoise)
        brightness = clamp(brightness, 0, 99)

        # alpha = hsva[3]  # alpha is not used with pygame.draw
        # alpha -= self.brightnessStep
        if brightness < 7 or self.age == 0:  # If brightness falls below 7, remove particle
            try:  # It's possible this particle was removed already by the superclass.
                self.container.remove(self)
            except ValueError:
                pass
        else:
            self.color.hsva = (hue, int(hsva[1]), brightness)  # , alpha)

    def draw(self):
        # Draw just a simple point:
        pygame.draw.rect(self.surface, self.color, ((self.pos[0], self.pos[1]), (particleSize, particleSize)))


class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]


def clamp(val, minval, maxval):
    if val < minval: return minval
    if val > maxval: return maxval
    return val


pygame.init()
pygame.display.set_caption('ShitStuckToYourMouse')  # title(stupid)
# pygame.mouse.set_visible(False)  # set mouse cursor visibility  --- Note: This does NOT work


# --------- Initiate variables:
if not config.has_section("SETTINGS"):
    setDefaults()
readVariables()
drawParticles = True
mouseSpeedPixelPerFrame = 0
mousePosition = POINT()
particles = []
firstPos = (mousePosition.x, mousePosition.y)
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
print("--- To stop overlay, close this window ---")  # notify on what to do to stop program
setFocus(hwnd)  # sets focus on pygame window
loop = True
while loop:
    clock.tick(FPS)  # limit the fps of the program
    display_window.fill(transparentColor)  # fill with color set to be transparent in win32gui.SetLayeredWindowAttributes
    windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure
    firstPos = (mousePosition.x-offsetX, mousePosition.y-offsetY)
    mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))
    # pygame.mouse.get_rel()  # --- Note: doesn't work because window is usually not focused or something

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
        mouseSpeedPixelPerFrame = math.sqrt(math.pow(mouseVelocity[0], 2) + math.pow(mouseVelocity[1], 2))
        if printMouseSpeed: print("Mouse speed in pixel distance traveled this frame: ", mouseSpeedPixelPerFrame)
        drawParticles = False
        #print(mouseSpeedPixelPerFrame)
        if mouseSpeedPixelPerFrame == 0:
            drawParticles = False
        elif mouseSpeedPixelPerFrame < levelVelocity[0]:
            #print("first")
            numParticles = levelNumParticles[0]
            drawParticles = True
        elif mouseSpeedPixelPerFrame < levelVelocity[1]:
            #print("second")
            numParticles = levelNumParticles[1]
            drawParticles = True
        elif mouseSpeedPixelPerFrame < levelVelocity[2]:
            #print("third")
            numParticles = levelNumParticles[2]
            drawParticles = True
        elif mouseSpeedPixelPerFrame < levelVelocity[3]:
            #print("fourth")
            numParticles = levelNumParticles[3]
            drawParticles = True
        else:
            #print("fifth")
            numParticles = levelNumParticles[4]
            drawParticles = True
            
    x = 0
    while x < numParticles and drawParticles is True:
        if particleColorRandom is True: particleColor = (random.randrange(256), random.randrange(256), random.randrange(256))
        particles.append(ParticleSparkle(display_window, firstPos, mouseVelocity, GRAVITY, particles, particleColor, mouseSpeedPixelPerFrame))
        x += 1
    for spark in particles:
        spark.update()
        spark.draw()

    if markPosition is True: pygame.draw.circle(display_window, "#ff0000", firstPos, 2)  # used for tuning offset
    secondPos = firstPos  # for getting mouse velocity
    pygame.display.update()
# while ends here

pygame.quit()
