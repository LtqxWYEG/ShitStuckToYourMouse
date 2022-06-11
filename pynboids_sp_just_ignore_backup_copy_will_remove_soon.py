#!/usr/bin/env python3
from ctypes import windll, Structure, c_int, byref
from math import pi, sin, cos, atan2, radians, degrees, sqrt
from random import randint
from win32gui import SetWindowLong, SetLayeredWindowAttributes, GetWindowLong, SetWindowPos
from win32con import HWND_TOPMOST, GWL_EXSTYLE, SWP_NOMOVE, SWP_NOSIZE, WS_EX_TRANSPARENT, LWA_COLORKEY, WS_EX_LAYERED, WS_EX_TOOLWINDOW
from win32api import RGB
import pygame as pg

"""
PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
This version uses a spatial partitioning grid to improve performance.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
"""
FLLSCRN = False  # True for Fullscreen, or False for Window
BOIDZ = 20  # How many boids to spawn, too many may slow fps
WRAP = False  # False avoids edges, True wraps to other side
FISH = False  # True to turn boids into fish
SPEED = 150  # Movement speed
WIDTH = 600  # Window Width (1200)
HEIGHT = 600  # Window Height (800)
BGCOLOR = (0, 0, 0)  # Background color in RGB
FPS = 60  # 30-90
SHOWFPS = False  # frame rate debug


def setWindowAttributes(hwnd):  # set all kinds of option for win32 windows
    # windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW)  # no taskbar button
    SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_LAYERED | WS_EX_TRANSPARENT,)
    SetLayeredWindowAttributes(hwnd, RGB(*transparentColorTuple), 255, LWA_COLORKEY)
    SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)


# HWND_TOPMOST

class Mouse:
    def __init__(self):
        super().__init__()
        mousePosition = POINT()
        windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure

        self.pos = pg.Vector2(mousePosition.x, mousePosition.y)
        self.rect = pg.Rect((mousePosition.x, mousePosition.y), (5, 5))
        self.angle = 0


class Boid(pg.sprite.Sprite):
    def __init__(self, grid, drawSurf, isFish=False):  # , cHSV=None
        super().__init__()
        self.grid = grid
        self.drawSurf = drawSurf
        self.image = pg.Surface((15, 15)).convert()
        self.image.set_colorkey(0)
        self.color = pg.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0, 360), 90, 90)  # if cHSV is None else cHSV # randint(5,55) #4goldfish
        if isFish:  # (randint(120,300) + 180) % 360  #4noblues
            pg.draw.polygon(self.image, self.color, ((7, 0), (12, 5), (3, 14), (11, 14), (2, 5), (7, 0)), width=3)
            self.image = pg.transform.scale(self.image, (16, 24))
        else:
            pg.draw.polygon(self.image, self.color, ((7, 0), (13, 14), (7, 11), (1, 14), (7, 0)))
        self.boidSize = 22 if isFish else 17
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
        self.dir = pg.Vector2(1, 0)  # sets up forward direction
        surfaceWidth, surfaceHeight = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, surfaceWidth - 50), randint(50, surfaceHeight - 50)))
        self.angle = randint(0, 360)  # random start angle, & position ^
        self.pos = pg.Vector2(self.rect.center)
        self.grid_lastpos = self.grid.getcell(self.pos)
        self.grid.add(self, self.grid_lastpos)


    def update(self, dt, speed, mouseposition, mousevelocity, mouse_Speed_Pixel_Per_Frame, screenWrap=False):
        mousePos = pg.Vector2(mouseposition.x, mouseposition.y)
        mouseRect = pg.Rect((mouseposition.x, mouseposition.y), (5, 5))
        Mouse.pos = mousePos
        Mouse.rect = mouseRect
        Mouse.angle = int(degrees(atan2(mousevelocity[1], mousevelocity[0])))
        mouseVelocity = mousevelocity
        targetDistance = 0
        angleDifference = 0
        surfaceWidth, surfaceHeight = self.drawSurf.get_size()
        selfCenter = pg.Vector2(self.rect.center)
        turnToDirection = targetVelocityX = targetVelocityY = targetAngleY = targetAngleX = 0
        turnRate = 120 * dt  # about 120 seems ok
        margin = 42
        self.angle = self.angle + randint(-4, 4)
        # Grid update stuff
        self.grid_pos = self.grid.getcell(self.pos)

        if self.grid_pos != self.grid_lastpos:
            self.grid.add(self, self.grid_pos)
            self.grid.remove(self, self.grid_lastpos)
            self.grid_lastpos = self.grid_pos

        # get nearby boids and sort by distance
        near_boids = self.grid.getnear(self, self.grid_pos)
        neighborBoids = sorted(near_boids, key=lambda i: pg.Vector2(i.rect.center).distance_to(selfCenter))
        del neighborBoids[7:]  # keep 7 closest, dump the rest
        if neighborBoids == "None":
            neighborBoids[0] = Mouse
        else:
            neighborBoids.append(Mouse)

        # computes the difference to reach target angle, for smooth steering
        mouseDifference = mousevelocity - selfCenter  # get angle differences for steering
        mouseDistance, Mouse.angle = pg.math.Vector2.as_polar(mouseDifference)
        mouseAngleDifference = (Mouse.angle - self.angle) + 180
        if abs(Mouse.angle - self.angle) > 0.5:
            turnToMouse = (mouseAngleDifference / 360 - (mouseAngleDifference // 360)) * 360 - 180
        distanceToMouse = pg.Vector2.distance_to(self.pos, Mouse.pos)
        # when boid has neighborS (walrus := sets neighborCount)
        if (neighborCount := len(neighborBoids)) > 1:  # ( := ) is operator for assignment of variables within expressions:
            nearestBoid = pg.Vector2(mousePos)

            for neighbor in neighborBoids:  # adds up neighbor vectors & angles for averaging
                targetVelocityX += neighbor.rect.centerx
                targetVelocityY += neighbor.rect.centery
                targetAngleY += sin(radians(neighbor.angle))
                targetAngleX += cos(radians(neighbor.angle))

            targetAverageAngle = degrees(atan2(targetAngleY, targetAngleX))
            targetVelocity = (targetVelocityX / neighborCount, targetVelocityY / neighborCount)

            # if too close, move away from closest neighbor
            if selfCenter.distance_to(nearestBoid) < self.boidSize:
                targetVelocity = nearestBoid

            tDiff = targetVelocity - selfCenter  # get angle differences for steering
            targetDistance, targetAngle = pg.math.Vector2.as_polar(tDiff)

            # if boid is close enough to neighbors, match their average angle
            if targetAngle < self.boidSize * 5:
                targetAngle = targetAverageAngle

            if distanceToMouse > 50:
                targetAngle = mouseAngleDifference
                # computes the difference to reach target angle, for smooth steering
            angleDifference = (targetAngle - self.angle) + 180
            if abs(targetAngle - self.angle) > 0.5:
                turnToDirection = (angleDifference / 360 - (angleDifference // 360)) * 360 - 180

            # if boid gets too close to target, steer away
            if targetDistance < self.boidSize and targetVelocity == nearestBoid:
                turnToDirection = -turnToDirection



        # Avoid edges of screen by turning toward the edge normal-angle
        spriteCenterPosX, spriteCenterPosY = self.rect.centerx, self.rect.centery
        if not screenWrap and min(spriteCenterPosX, spriteCenterPosY, surfaceWidth - spriteCenterPosX, surfaceHeight - spriteCenterPosY) < margin:
            if spriteCenterPosX < margin:
                targetAngle = 0
            elif spriteCenterPosX > surfaceWidth - margin:
                targetAngle = 180
            if spriteCenterPosY < margin:
                targetAngle = 90
            elif spriteCenterPosY > surfaceHeight - margin:
                targetAngle = 270

            angleDifference = (targetAngle - self.angle) + 180  # increase turnRate to keep boids on screen

            turnToDirection = (angleDifference / 360 - (angleDifference // 360)) * 360 - 180

            distanceToEdge = min(spriteCenterPosX, spriteCenterPosY, surfaceWidth - spriteCenterPosX, surfaceHeight - spriteCenterPosY)
            turnRate = turnRate + (1 - distanceToEdge / margin) * (20 - turnRate)  # turnRate=minRate, 20=maxRate


        #distanceToMouse = pg.Vector2.distance_to(self.pos, Mouse.pos)

        if turnToDirection != 0:  # steers based on turnToDirection, handles left or right
            self.angle += turnRate * abs(turnToDirection) / turnToDirection

        self.angle %= 360  # ensures that the angle stays within 0-360
        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.angle).normalize()
        self.pos += self.dir * dt * (speed + (7 - neighborCount) * 5)  # movement speed

        # Optional screen wrap
        if screenWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0:
                self.pos.y = surfaceHeight
            elif self.rect.top > surfaceHeight:
                self.pos.y = 0
            if self.rect.right < 0:
                self.pos.x = surfaceWidth
            elif self.rect.left > surfaceWidth:
                self.pos.x = 0

        # Actually update position of boid
        self.rect.center = self.pos


class BoidGrid:  # tracks boids in spatial partition grid
    def __init__(self):
        self.grid_size = 100
        self.dict = {}

    # finds the grid cell corresponding to given pos
    def getcell(self, pos):
        return (pos[0] // self.grid_size, pos[1] // self.grid_size)

    # boids add themselves to cells when crossing into new cell
    def add(self, boid, key):
        if key in self.dict:
            self.dict[key].append(boid)
        else:
            self.dict[key] = [boid]

    # they also remove themselves from the previous cell
    def remove(self, boid, key):
        if key in self.dict and boid in self.dict[key]:
            self.dict[key].remove(boid)

    # Returns a list of nearby boids within all surrounding 9 cells
    def getnear(self, boid, key):
        if key in self.dict:
            nearby = []
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    nearby += self.dict.get((key[0] + x, key[1] + y), [])
            nearby.remove(boid)
        return nearby


class POINT(Structure):  # used for the mouse position
    _fields_ = [("x", c_int), ("y", c_int)]


def main():
    global transparentColorTuple
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try:
        pg.display.set_icon(pg.image.load("nboids.png"))
    except:
        print("Note: nboids.png icon not found, skipping..")
    # setup fullscreen or window mode
    # if FLLSCRN:
    #     currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    #     screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=1)
    #     pg.mouse.set_visible(False)
    # else:
    #     screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE | pg.SCALED, vsync=1)
    transparentColor = "#000000"
    transparentColorTuple = tuple(int(transparentColor.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))  # convert settings['transparentColor'] to tuple for win32api.RGB(), to reduce hard-coded values. Thanks John1024
    display_window = pg.display.set_mode((0, 0), 0, vsync=0)
    display_window.fill(transparentColor)  # fill with transparent color set in win32gui.SetLayeredWindowAttributes
    setFocus = windll.user32.SetFocus  # sets focus to
    handleWindowDeviceContext = pg.display.get_wm_info()["window"]  # get window manager information about this pygame window, in order to address it in setWindowAttributes()
    setWindowAttributes(handleWindowDeviceContext)
    mousePosition = POINT()
    second_Pos = (0, 0)
    boidTracker = BoidGrid()
    nBoids = pg.sprite.Group()
    # spawns desired # of boidz
    for n in range(BOIDZ):
        nBoids.add(Boid(boidTracker, display_window, FISH))

    if SHOWFPS:
        font = pg.font.Font(None, 30)
    clock = pg.time.Clock()

    # main loop
    setFocus(handleWindowDeviceContext)
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and (e.key == pg.K_ESCAPE or e.key == pg.K_q or e.key == pg.K_SPACE):
                return
        windll.user32.GetCursorPos(byref(mousePosition))  # get mouse cursor position and save it in the POINT() structure
        first_Pos = (mousePosition.x, mousePosition.y)
        mouseVelocity = ((first_Pos[0] - second_Pos[0]), (first_Pos[1] - second_Pos[1]))  # OR
        mouse_Speed_Pixel_Per_Frame = sqrt((mouseVelocity[0] * mouseVelocity[0]) + (mouseVelocity[1] * mouseVelocity[1]))
        dt = clock.tick(FPS) / 1000
        display_window.fill(BGCOLOR)
        # update boid logic, then draw them
        nBoids.update(dt, SPEED, mousePosition, mouseVelocity, mouse_Speed_Pixel_Per_Frame, WRAP)
        nBoids.draw(display_window)
        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS:
            display_window.blit(font.render(str(int(clock.get_fps())), True, [0, 200, 0]), (8, 8))
        second_Pos = first_Pos
        pg.display.update()
        print("MousePosition = ", mousePosition.x, ", ", mousePosition.y, " Velocity = ", mouseVelocity)


if __name__ == "__main__":
    main()  # by Nik
    pg.quit()
