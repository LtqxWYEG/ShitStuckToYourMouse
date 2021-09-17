#
# Copyright (C) 2021 by Matthias Grommisch <distelzombie@protonmail.com>
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
import math
import win32gui
import win32con
import win32api
import pygame.gfxdraw
from pygame.locals import *  # for Color
import random
# Vec2D comes from here: http://pygame.org/wiki/2DVectorClass
from vec2d import Vec2d


"""
Sparkly code by Eric Pavey - 2010-06-21
simpleParticle01.py
"""


# Settings ---------------------------------------------------
# ---------- General:
transparentColor = "#000000"  # global transparent color
particleSize = 2
particleAge = 40  # Modifier for time until brightness < 10 (death) OR max lifetime in frames
ageBrightnessMod = 6.5  # increase for slower brightness decline (concavity of downward slope)
particleColor = "#ff0001"#"#ffa020"  # "#c78217"  # Use "#ff0001" for full color when ageColor is True
particleRainbow = False
ageColor = True  # Change hue linearly, based on age.
ageColorSpeed = 5.0  # Hue aging factor. Not used if ageColorSlope = True
ageColorSlope = True  # If ageColor = True: Age like concave downward curve. For more pronounced pink and blue colors (Or whatever is highest hue value of particleColor)
ageColorSlopeConcavity = 0.3  # increase concavity of downward slope representing values over age
velocityMod = 1.6  # lowers velocity added to particle based on mouse speed: mouse speed / velocityMod
velocityClamp = 200  # max. velocity
GRAVITY = (0, .025)  # x, y motion added to any particle. maybe turn negative and simulate smoke or flames
drag = .85  # particle drag, higher equals less drag: (drag * particle speed) per frame
FPS = 60

# ---------- Non-dynamic:
offsetX = -12  # offset to mouse cursor position in pixel. (0, 0 = tip of cursor)
offsetY = -28  # offset for Y position
markPosition = False  # Use for offset tuning
numParticles = 1  # per frame, if dynamic is False
randomMod = 5.5  # adds random motion to particles: mouse speed xy +- randomMod

# ---------- Dynamic:
dynamic = True  # The faster the movement, the more particles and random motion will be added. For the SCREEEETCH-effect
randomModDynamic = 6.0  # adds random motion to particles: velocity / randomModDynamic
printMouseSpeed = False  # Use for tuning the next parameters. Prints current mouse speed in pixels per frame.
levelVelocity =     [15, 30, 60, 120, '#']  # at which mouse speed in pixels per frame...
levelNumParticles = [ 1,  4,  8,  16,  24]  # this many particles
# levels = 5  # may be used in future to make dynamic more dynamic



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

    def __init__(self, surface, pos, vel, gravity, container, delta, color='red'):
        """
        surface : Surface :  The Surface to draw on.
        pos : (x,y) : tuple/list x,y position at time of creation.
        vel : (x,y) : tuple/list x,y velocity at time of creation.
        gravity : (x,y) : tuple/list x,y gravity effecting the particle.
        container : list : The passed in list that contains all the particles to draw.
            Used so particles can be deleted.
        color : str : String color value, default 'red'.
        """
        self.surface = surface
        self.pos = Vec2d(pos)
        if dynamic:
            vel = [vel[0]+random.uniform(-(delta / randomModDynamic), (delta / randomModDynamic)), vel[1]+random.uniform(-(delta / randomModDynamic), (delta / randomModDynamic))]
        else:
            vel = [vel[0]+random.uniform(-randomMod, randomMod), vel[1]+random.uniform(-randomMod, randomMod)]
        vel = [vel[0], vel[1]]
        self.vel = Vec2d(vel) / velocityMod
        # Clamp any huge velocities:
        if self.vel.length > velocityClamp:
            self.vel.length = velocityClamp

        self.gravity = Vec2d(gravity)
        self.container = container
        self.color = Color(color)

        self.surfSize = surface.get_size()
        self.drag = drag

    def update(self):
        """
        Update position and existance per frame.
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

    def __init__(self, surface, pos, vel, gravity, container, color, delta):
        """
        age : How long the particle will live.  Will get darker as it gets older.
        """
        # Init superclass:
        super(ParticleSparkle, self).__init__(surface, pos, vel, gravity, container, delta, color)
        self.age = particleAge

    def update(self):
        # Override superclass, but call to superclass method first:
        super(ParticleSparkle, self).update()
        self.ageStep = 100.0/float(self.age)
        # Update color, and existance based on color:
        hsva = self.color.hsva  # H = [0, 360], S = [0, 100], V = [0, 100], A = [0, 100]
        if ageColor:
            if ageColorSlope:
                hue = hsva[0]
                hue -= self.ageStep / ageColorSlopeConcavity
            else:
                hue = hsva[0]
                hue -= self.ageStep * ageColorSpeed
        brightness = hsva[2]
        brightness -= self.ageStep / ageBrightnessMod
        self.age -= 1
        # alpha = hsva[3]  # alpha is not used with pygame.draw
        # alpha -= self.brightnessStep
        if brightness < 10 or self.age == 0:
            # It's possible this particle was removed already by the superclass.
            try:
                self.container.remove(self)
            except ValueError:
                pass
        else:
            if hue < 0: hue = 0
            self.color.hsva = (hue, int(hsva[1]), brightness)  # , alpha)

    def draw(self):
        # Draw just a simple point:
        pygame.draw.rect(self.surface, self.color, ((self.pos[0], self.pos[1]), (particleSize, particleSize)))


class POINT(Structure): _fields_ = [("x", c_int), ("y", c_int)]


drawParticles = True
delta = 0
mousePosition = POINT()
setWindowPos = windll.user32.SetWindowPos  # see setWindowAttributes()
setFocus = windll.user32.SetFocus  # sets focus to
pygame.init()
pygame.display.set_caption('MouseDickWhatever')  # title(stupid)
# pygame.mouse.set_visible(False)  # set mouse cursor visibility  --- Note: This does NOT work
clock = pygame.time.Clock()  # for FPS limiting
info = pygame.display.Info()  # get screen information like size, to set in pygame.display.set_mode
flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE  # flags to set in pygame.display.set_mode
# FULLSCREEN: Create a fullscreen display
# DOUBLEBUF: Double buffering. Creates a separate block of memory to apply all the draw routines and then copying that block (buffer) to video memory. (Thanks, Foon)
# HWSURFACE: hardware accelerated window, only in FULLSCREEN. (Uses memory on video card)

display_window = pygame.display.set_mode((info.current_w, info.current_h), flags, vsync=0)  # vsync only works with OPENGL flag, so far. Might change in the future
display_window.fill(transparentColor)  # fill with tranparent color set in win32gui.SetLayeredWindowAttributes
transparentColorTuple = tuple(int(transparentColor.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))  # convert transparentColor to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024

hwnd = pygame.display.get_wm_info()['window']  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
setWindowAttributes(hwnd)  # set all kinds of option for win32 windows. Makes it transparent and clickthrough

print("--- To stop overlay, close this window ---")  # notify on what to do to stop program
setFocus(hwnd)  # sets focus on pygame window
particles = []
firstPos = (mousePosition.x, mousePosition.y)
secondPos = firstPos
mouseVelocity = ((firstPos[0] - secondPos[0]), (firstPos[1] - secondPos[1]))

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
        # if event.type == pygame.QUIT:  # --- Note: practically uneccessary because window isn't focused
        #     loop = False
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_ESCAPE:
        #         loop = False

    # fastest tuple arithmatic solution: (a[0] - b[0], a[1] - b[1]). NOT np, sub, lambda, zip...
    if dynamic is True:
        offsetX = 0
        offsetY = 0
        delta = math.sqrt(math.pow(mouseVelocity[0], 2) + math.pow(mouseVelocity[1], 2))
        if printMouseSpeed: print("Mouse speed in pixel distance traveled this frame: ", delta)
        drawParticles = False
        #print(delta)
        if delta == 0:
            drawParticles = False
        elif delta < levelVelocity[0]:
            #print("first")
            numParticles = levelNumParticles[0]
            drawParticles = True
        elif delta < levelVelocity[1]:
            #print("second")
            numParticles = levelNumParticles[1]
            drawParticles = True
        elif delta < levelVelocity[2]:
            #print("third")
            numParticles = levelNumParticles[2]
            drawParticles = True
        elif delta < levelVelocity[3]:
            #print("fourth")
            numParticles = levelNumParticles[3]
            drawParticles = True
        else:
            #print("fifth")
            numParticles = levelNumParticles[4]
            drawParticles = True
            
    x = 0
    while x < numParticles and drawParticles is True:
        if particleRainbow is True: particleColor = (random.randrange(256), random.randrange(256), random.randrange(256))
        particles.append(ParticleSparkle(display_window, firstPos, mouseVelocity, GRAVITY, particles, particleColor, delta))
        x += 1
    for spark in particles:
        spark.update()
        spark.draw()

    if markPosition is True: pygame.draw.circle(display_window, "#ff0000", firstPos, 2)  # used for tuning offset
    secondPos = firstPos  # for getting mouse velocity
    pygame.display.update()
# while end

pygame.quit()
input()
