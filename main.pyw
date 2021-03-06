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
from io import BytesIO
#from json import (load as jsonload, dump as jsondump)
import PySimpleGUI as sg
from psgtray import SystemTray
from subprocess import PIPE, Popen, CREATE_NO_WINDOW
from PIL import Image, ImageTk
from os import path, listdir, getpid, kill, getcwd
from os.path import exists
import sys
from shutil import rmtree
import psutil
import signal
import base64

poopImage = base64.b64decode("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")
poopImage2 = "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"


def image_file_to_bytes(image64, size):
    image_file = BytesIO(base64.b64decode(image64))
    img = Image.open(image_file)
    img.thumbnail(size, Image.ANTIALIAS)
    bio = BytesIO()
    img.save(bio, format='PNG')
    imgbytes = bio.getvalue()
    return imgbytes


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)


def cleanup_mei():
    """
    Rudimentary workaround for https://github.com/pyinstaller/pyinstaller/issues/2379
    """
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

    def getlistfloat(self, section, option):  # No wonder ppl use the horribly looking JSON... (Although I have no idea if that's better)
        return [float(x) for x in self.getlist(section, option)]


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


# settings=dict(config.items('SPARKLES'))  # I don't understand this for now
def getVariablesFromConfig(window):
    window['particleSize'].update(int(config.get("SPARKLES", "particleSize")))
    window['particleAge'].update(int(config.get("SPARKLES", "particleAge")))
    window['ageBrightnessMod'].update(float(config.get("SPARKLES", "ageBrightnessMod")))
    window['ageBrightnessNoise'].update(int(config.get("SPARKLES", "ageBrightnessNoise")))
    window['velocityMod'].update(float(config.get("SPARKLES", "velocityMod")))
    window['velocityClamp'].update(int(config.get("SPARKLES", "velocityClamp")))
    string = config.getlistfloat("SPARKLES", "GRAVITY")
    window['GRAVITY_X'].update(string[0])
    window['GRAVITY_Y'].update(string[1])
    window['drag'].update(float(config.get("SPARKLES", "drag")))
    window['FPS'].update(int(config.get("SPARKLES", "FPS")))
    window['interpolateMouseMovement'].update(config.getboolean("SPARKLES", "interpolateMouseMovement"))
    window['particleColor'].update(str(config.get("SPARKLES", "particleColor")))
    window['particleColorRandom'].update(config.getboolean("SPARKLES", "particleColorRandom"))
    window['ageColor'].update(config.getboolean("SPARKLES", "ageColor"))
    window['ageColorSpeed'].update(float(config.get("SPARKLES", "ageColorSpeed")))
    window['ageColorSlope'].update(config.getboolean("SPARKLES", "ageColorSlope"))
    window['ageColorSlopeConcavity'].update(float(config.get("SPARKLES", "ageColorSlopeConcavity")))
    window['ageColorNoise'].update(int(config.get("SPARKLES", "ageColorNoise")))
    window['ageColorNoiseMod'].update(float(config.get("SPARKLES", "ageColorNoiseMod")))
    window['useOffset'].update(config.getboolean("SPARKLES", "useOffset"))
    window['offsetX'].update(int(config.get("SPARKLES", "offsetX")))
    window['offsetY'].update(int(config.get("SPARKLES", "offsetY")))
    window['markPosition'].update(config.getboolean("SPARKLES", "markPosition"))
    window['numParticles'].update(int(config.get("SPARKLES", "numParticles")))
    window['randomMod'].update(int(config.get("SPARKLES", "randomMod")))
    window['brownianMotion'].update(float(config.get("SPARKLES", "brownianMotion")))
    window['dynamic'].update(config.getboolean("SPARKLES", "dynamic"))
    window['randomModDynamic'].update(float(config.get("SPARKLES", "randomModDynamic")))
    string = config.getlistint("SPARKLES", "levelVelocity")
    window['levelVelocity_1'].update(string[0])
    window['levelVelocity_2'].update(string[1])
    window['levelVelocity_3'].update(string[2])
    window['levelVelocity_4'].update(string[3])
    string = config.getlistint("SPARKLES", "levelNumParticles")
    window['levelNumParticles_1'].update(string[0])
    window['levelNumParticles_2'].update(string[1])
    window['levelNumParticles_3'].update(string[2])
    window['levelNumParticles_4'].update(string[3])
    window['fontColor'].update(str(config.get("OTHER", "fontColor")))
    window['fontSize'].update(int(config.get("OTHER", "fontSize")))
    window['outlineColor'].update(str(config.get("OTHER", "outlineColor")))
    window['outlineThickness'].update(int(config.get("OTHER", "outlineThickness")))
    window['fontAntialiasing'].update(config.getboolean("OTHER", "fontAntialiasing"))
    window['showColor'].update(config.getboolean("OTHER", "showColor"))
    window['complementaryColor'].update(config.getboolean("OTHER", "complementaryColor"))
    window['rgbComplement'].update(config.getboolean("OTHER", "rgbComplement"))
    window['artistComplement'].update(config.getboolean("OTHER", "artistComplement"))
    window['showClock'].update(config.getboolean("OTHER", "showClock"))
    window['showCPU'].update(config.getboolean("OTHER", "showCPU"))
    window['showImage'].update(config.getboolean("OTHER", "showImage"))
    window['imagePath'].update(str(config.get("OTHER", "imagePath")))
    return window


def updateConfig(values):
    config.set("SPARKLES", "particleSize", str(values['particleSize']))
    config.set("SPARKLES", "particleAge", str(values['particleAge']))
    config.set("SPARKLES", "ageBrightnessMod", str(values['ageBrightnessMod']))
    config.set("SPARKLES", "ageBrightnessNoise", str(values['ageBrightnessNoise']))
    config.set("SPARKLES", "velocityMod", str(values['velocityMod']))
    config.set("SPARKLES", "velocityClamp", str(values['velocityClamp']))
    string = [str(values['GRAVITY_X']), ', ', str(values['GRAVITY_Y'])]
    GRAVITYStr = "".join(string)
    config.set("SPARKLES", "GRAVITY", GRAVITYStr)
    config.set("SPARKLES", "drag", str(values['drag']))
    config.set("SPARKLES", "FPS", str(values['FPS']))
    config.set("SPARKLES", "interpolateMouseMovement", str(values['interpolateMouseMovement']))
    config.set("SPARKLES", "particleColor", values['particleColor'])
    config.set("SPARKLES", "particleColorRandom", str(values['particleColorRandom']))
    config.set("SPARKLES", "ageColor", str(values['ageColor']))
    config.set("SPARKLES", "ageColorSpeed", str(values['ageColorSpeed']))
    config.set("SPARKLES", "ageColorSlope", str(values['ageColorSlope']))
    config.set("SPARKLES", "ageColorSlopeConcavity", str(values['ageColorSlopeConcavity']))
    config.set("SPARKLES", "ageColorNoise", str(values['ageColorNoise']))
    config.set("SPARKLES", "ageColorNoiseMod", str(values['ageColorNoiseMod']))
    config.set("SPARKLES", "useOffset", str(values['useOffset']))
    config.set("SPARKLES", "offsetX", str(values['offsetX']))
    config.set("SPARKLES", "offsetY", str(values['offsetY']))
    config.set("SPARKLES", "markPosition", str(values['markPosition']))
    config.set("SPARKLES", "numParticles", str(values['numParticles']))
    config.set("SPARKLES", "randomMod", str(values['randomMod']))
    config.set("SPARKLES", "brownianMotion", str(values['brownianMotion']))
    config.set("SPARKLES", "dynamic", str(values['dynamic']))
    config.set("SPARKLES", "randomModDynamic", str(values['randomModDynamic']))
    string = [str(values['levelVelocity_1']), ', ', str(values['levelVelocity_2']), ', ', str(values['levelVelocity_3']), ', ', str(values['levelVelocity_4'])]
    levelVelocityStr = "".join(string)
    config.set("SPARKLES", "levelVelocity", levelVelocityStr)
    string = [str(values['levelNumParticles_1']), ', ', str(values['levelNumParticles_2']), ', ', str(values['levelNumParticles_3']), ', ', str(values['levelNumParticles_4'])]
    levelNumParticlesStr = "".join(string)
    config.set("SPARKLES", "levelNumParticles", levelNumParticlesStr)
    config.set("OTHER", "fontColor", str(values['fontColor']))
    config.set("OTHER", "fontSize", str(values['fontSize']))
    config.set("OTHER", "outlineColor", str(values['outlineColor']))
    config.set("OTHER", "outlineThickness", str(values['outlineThickness']))
    config.set("OTHER", "fontAntialiasing", str(values['fontAntialiasing']))
    config.set("OTHER", "showColor", str(values['showColor']))
    config.set("OTHER", "complementaryColor", str(values['complementaryColor']))
    config.set("OTHER", "rgbComplement", str(values['rgbComplement']))
    config.set("OTHER", "artistComplement", str(values['artistComplement']))
    config.set("OTHER", "showClock", str(values['showClock']))
    config.set("OTHER", "showCPU", str(values['showCPU']))
    config.set("OTHER", "showRAM", str(values['showRAM']))
    config.set("OTHER", "showImage", str(values['showImage']))
    config.set("OTHER", "imagePath", str(values['imagePath']))
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


def get_img_data(f, maxsize=(1200, 850), first=False):
    """
    Generate image data using PIL
    """
    try:
        img = Image.open(f)
        img.thumbnail(maxsize)
        print('Image opened')
        print(img)
        if first:                     # tkinter is inactive the first time
            bio = BytesIO()
            img.save(bio, format="PNG")
            del img
            return bio.getvalue()
        return ImageTk.PhotoImage(img)
    except:  # yes yes yes, later. not yet
        sg.popup_no_wait('Error: Image does not exist', text_color='#ffc000', button_type=5, auto_close=True,
                         auto_close_duration=3, non_blocking=True, font=("Segoe UI", 26), no_titlebar=True, keep_on_top=True)
        print('Error: %s does not exist' % imagePath)
        return


def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=False, timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates.
    """
    if pid == getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
    return gone, alive  # Thank you very much Mr. PySimpleGUI :)


def killProcessUsingOsKill(pid, sig=signal.SIGTERM):  # Use this for when compiled to exe
    kill(pid, sig)
    return


def make_window(theme):
    global particleColor, fontColor, outlineColor, ageColorSpeed, imagePath
    sg.theme(theme)
    file_types = [("Images", "*.png *.jpg *.jpeg *.tiff *.bmp *.gif"), ("All files (*.*)", "*.*")]

    general_layout = [[sg.Spin([i for i in range(1, 400)], initial_value=60, font=("Segoe UI", 16), k='FPS', enable_events=True),
                       sg.T('Frames per second. Also affects number of particles as they are spawned per frame.')],
                      [sg.Checkbox('Interpolate mouse movement', default=True, k='interpolateMouseMovement', enable_events=True)],
                      [sg.T('Exp.: Draw some particles between current position of the cursor and that of last frame. (Interpolation should have almost no effect on performance)', pad=(10, (0, 15)))],
                      [sg.Spin([i for i in range(1, 100)], initial_value=1, font=("Segoe UI", 16), k='numParticles', enable_events=True), sg.T('Number of particles to spawn per frame'),
                      sg.Spin([i for i in range(1, 11)], initial_value=2, font=("Segoe UI", 16), k='particleSize', enable_events=True), sg.T('Particle size in pixel')],

                      [sg.Frame('Offsets', [[sg.Checkbox('Add offset to the position of the particle origin', default=False, k='useOffset', enable_events=True),
                       sg.Checkbox('Mark position of particle origin. Use for offset tuning', default=False, k='markPosition', disabled=False, enable_events=True)],
                      [sg.T('X='), sg.Spin([i for i in range(-99, 99)], initial_value=20, font=("Segoe UI", 16), k='offsetX', disabled=False, enable_events=True),
                       sg.T('Y='), sg.Spin([i for i in range(-99, 99)], initial_value=10, font=("Segoe UI", 16), k='offsetY', disabled=False, enable_events=True),
                       sg.T('Offset in pixel. (0, 0=tip of cursor)')]],)],

                      [sg.Spin([i for i in range(0, 100)], initial_value=12, font=("Segoe UI", 16), k='ageBrightnessNoise', enable_events=True),
                       sg.T('Adds random noise (twinkling) to age/brightness: brightness = random(+|-value). 0 for no noise'),
                       sg.T('                                     Scroll down  |')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value=60, font=("Segoe UI", 16), k='particleAge', enable_events=True), sg.T('Particle age (in frames) OR modifier for time until brightness < 7 (death)'),
                       sg.T('                                                                                           v')],
                      [sg.T('Increase slider to slow down brightness decline. Faster dimming equals faster death. Sets concavity. (Slower first, then faster)', pad=(10, (15, 0)))],
                      [sg.Slider(range=(0.001, 29.999), default_value=5.300, font=("Segoe UI", 14), resolution=.001, size=(70, 10),
                                 orientation='horizontal', k='ageBrightnessMod', enable_events=True)],
                      [sg.HorizontalSeparator()],
                      [sg.T('Adds random motion, like brownian motion, to particles. Increases exponentially over time and with gravity. Deactivate with 0.', pad=(10, (15, 0)))],
                      [sg.Slider(range=(0.000, 1.000), default_value=10, font=("Segoe UI", 14), resolution=0.0001, size=(70, 10),
                                 orientation='horizontal', disabled=False, k='brownianMotion', enable_events=True, trough_color=sg.theme_slider_color())],
                      #[sg.T('--- Scroll down ---')],
                      [sg.HorizontalSeparator()],
                      [sg.T('Adds random motion in random direction to particles depending on mouse velocity.', pad=(10, (15, 0)))],
                      [sg.T('mouseVelocity[x][y] +- rnd(randomMod). Ignored if dynamic is on. Deactivate with 0.', pad=(10, (0, 0)))],
                      [sg.Slider(range=(0, 100), default_value=10, font=("Segoe UI", 14), resolution=1, size=(70, 10),
                                 orientation='horizontal', disabled=False, k='randomMod', enable_events=True, trough_color=sg.theme_slider_color())],
                      [sg.HorizontalSeparator()],
                      [sg.T('Add to and multiply velocity of particle dependant on mouse movement direction and speed: velocity[x][y] * velocityMod', pad=(10, (15, 0)))],
                      [sg.Slider(range=(-2.99, 2.99), default_value=1.00, font=("Segoe UI", 14), resolution=.01, size=(70, 10),
                                 orientation='horizontal', k='velocityMod', enable_events=True)],
                      [sg.Spin([i for i in range(1, 1000)], initial_value=200, font=("Segoe UI", 16), k='velocityClamp', enable_events=True),
                       sg.T('Max. particle velocity in pixel per frame')],
                      [sg.HorizontalSeparator()],
                      [sg.T('X and Y motion added to any particle each frame. Can be gravity or wind.', pad=(10, (15, 0)))],
                      [sg.T('(Motion vector with direction: 0.0, 0.1 = a motion of .1 in downwards direction.)', pad=(10, (0, 0)))],
                      [sg.Slider(range=(-9.999, 9.999), default_value=0.000, font=("Segoe UI", 14), resolution=.001, size=(34, 10),
                                 orientation='horizontal', k='GRAVITY_X', enable_events=True),
                       sg.Slider(range=(-3.000, 3.000), default_value=0.025, font=("Segoe UI", 14), resolution=.001, size=(35, 10),
                                 orientation='horizontal', k='GRAVITY_Y', enable_events=True)],
                      [sg.HorizontalSeparator()],
                      [sg.T('Particle drag, higher equals more movement, less drag: drag * particle speed per frame. (If >1 then particles speed up)', pad=(10, (15, 0)))],
                      [sg.Slider(range=(0.000, 2.999), default_value=0.850, font=("Segoe UI", 14), resolution=.001, size=(70, 10),
                                 orientation='horizontal', k='drag', enable_events=True)]
                      ]

    color_layout = [[sg.Input(visible=False, enable_events=True, k='particleColor'), sg.ColorChooserButton('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor),
                                                                                                           size=(25, 2), font=("Segoe UI", 16), k='color picker button')],
                    [sg.T('Use "#ff0001" for full HSV color when ageColor is True. (Full 255 red plus 1 blue=hsv hue of 360??)', pad=(10, (0, 15)))],
                    [sg.Checkbox('Sets color of particles to a random one.', default=False, k='particleColorRandom', enable_events=True)],

                    [sg.HorizontalSeparator()],
                    [sg.Spin([i for i in range(0, 200)], initial_value=50, font=("Segoe UI", 16), k='ageColorNoise', enable_events=True),
                     sg.T('Add random hue variation to combat too uniform-looking sparkles: hue = random(+|-value). "0" disables this.')],
                    [sg.T('Hue variation bias towards more positive or negative values: 0 = only negative noise | 0.5 = balanced | 1.0 = only positive noise', pad=(10, (15, 0)))],
                    [sg.Slider(range=(0.00, 1.00), default_value=0.42, font=("Segoe UI", 14), resolution=.01, size=(70, 10),
                               orientation='horizontal', k='ageColorNoiseMod', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox('Change hue over time. (Hue aging)', default=True, k='ageColor', enable_events=True)],
                    [sg.T('')],
                    [sg.T('Hue aging speed factor. Negative values decrease hue [of hsv color] over time, positive increase it. (Neg: towards orange. Pos: towards purple)', pad=(10, (15, 0)))],
                    [sg.Slider(range=(-19.99, 19.99), default_value=-5.50, font=("Segoe UI", 14), resolution=.10, size=(70, 10),
                               orientation='horizontal', k='ageColorSpeed', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],
                    [sg.T('Fine adjustment: ', font=("Segoe UI", 14)),
                     sg.Slider(range=(ageColorSpeed-1.00, ageColorSpeed+1.00), default_value=ageColorSpeed, font=("Segoe UI", 14), resolution=.005, size=(56.9, 10),
                               orientation='horizontal', k='ageColorSpeedFine', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox('Age on a concave downward curve: At the start slower, but then increasingly faster decline of hue value.', default=True, k='ageColorSlope', disabled=False, enable_events=True)],
                    [sg.T('(More pronounced upper colors. [Like purple and blue])', pad=(10, (0, 0)))],
                    [sg.T('Increase concavity of the downward slope that represents hue over time. (Think: https://i.stack.imgur.com/bGi9k.jpg)', pad=(10, (0, 0)))],
                    [sg.Slider(range=(0.001, 1.999), default_value=0.420, font=("Segoe UI", 14), resolution=.001, size=(70, 10),
                               orientation='horizontal', k='ageColorSlopeConcavity', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())]
                    ]

    dynamic_layout = [[sg.Text('Dynamics settings')],
                      [sg.Checkbox('Enable dynamic behavior', default=True, k='dynamic', enable_events=True)],
                      [sg.T('Exp.: The faster the movement, the more particles are created and the more random motion will be added.', pad=(10, (0, 15)))],

                      [sg.HorizontalSeparator()],
                      [sg.T('Adds random motion to random direction to DYNAMIC particles: mouseSpeed(direction) * randomMod.', pad=(10, (15, 0)))],
                      [sg.Slider(range=(0.000, 0.999), default_value=0.160, font=("Segoe UI", 14), resolution=.001, size=(70, 10),
                                 orientation='horizontal', k='randomModDynamic', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],

                      [sg.HorizontalSeparator()],  # find better way to do this. Maybe tables? There's a demo for that. Frames are ok though
                      [sg.Frame('Number of particles:',[[sg.Spin([i for i in range(1, 100)], initial_value=5, font=("Segoe UI", 16), k='levelNumParticles_1', disabled=False, enable_events=True), sg.T('Level 1 '),
                       sg.Spin([i for i in range(1, 100)], initial_value=8, font=("Segoe UI", 16), k='levelNumParticles_2', disabled=False, enable_events=True), sg.T('Level 2 '),
                       sg.Spin([i for i in range(1, 100)], initial_value=14, font=("Segoe UI", 16), k='levelNumParticles_3', disabled=False, enable_events=True), sg.T('Level 3'),
                       sg.Spin([i for i in range(1, 100)], initial_value=20, font=("Segoe UI", 16), k='levelNumParticles_4', disabled=False, enable_events=True), sg.T('Level 4 - spawn this many particles ...')]],)],
                      [sg.Frame('At mouse velocity in pixel per frame:',[[sg.Spin([i for i in range(1, 1000)], initial_value=15, font=("Segoe UI", 16), k='levelVelocity_1', disabled=False, enable_events=True), sg.T('Level 1'),
                       sg.Spin([i for i in range(1, 1000)], initial_value=30, font=("Segoe UI", 16), k='levelVelocity_2', disabled=False, enable_events=True), sg.T('Level 2'),
                       sg.Spin([i for i in range(1, 1000)], initial_value=60, font=("Segoe UI", 16), k='levelVelocity_3', disabled=False, enable_events=True), sg.T('Level 3 '),
                       sg.Spin([i for i in range(1, 1000)], initial_value=120, font=("Segoe UI", 16), k='levelVelocity_4', disabled=False, enable_events=True), sg.T('Level 4 - if mouse is moving this fast in pixels per frame ...')]],)],
                      [sg.T('Number of particles at mouse velocities below "Level 1" are defined by the value (numParticles) in the General tab.')]
                      ]

    other_layout = [[sg.Text("Anything else one could find interesting to adhere to your mouse-cursor!", font=("Segoe UI", 16))],
                    [sg.Text('Notice: FPS and offset from the "General"-tab are also used here:')],
                    [sg.Checkbox('Add offset to the position of the upper-right corner of these stupid things', default=False, k='useOffset2', enable_events=True)],
                    [sg.T('X '), sg.Spin([i for i in range(-99, 99)], initial_value=20, font=("Segoe UI", 16), k='offsetX2', disabled=False, enable_events=True),
                     sg.T('Y '), sg.Spin([i for i in range(-99, 99)], initial_value=10, font=("Segoe UI", 16), k='offsetY2', disabled=False, enable_events=True),
                     sg.T('Offset in pixel. (0, 0=tip of cursor)')],

                    [sg.HorizontalSeparator()],
                    [sg.Input(visible=False, enable_events=True, k='fontColor'),
                     sg.ColorChooserButton('Font color picker: %s' % fontColor, button_color=("#010101", fontColor), size=(25, 1), font=("Segoe UI", 16), k='font color picker button'),
                    sg.Input(visible=False, enable_events=True, k='outlineColor'),
                     sg.ColorChooserButton('Outline color picker: %s' % outlineColor, button_color=("#808080", outlineColor), size=(25, 1), font=("Segoe UI", 16), k='outline color picker button')],
                    [sg.Spin([i for i in range(1, 100)], initial_value=10, font=("Segoe UI", 16), k='fontSize', enable_events=True),
                     sg.T('Font size in pt.'),
                    sg.Spin([i for i in range(0, 10)], initial_value=1, font=("Segoe UI", 16), k='outlineThickness', enable_events=True),
                     sg.T('Thickness of the outline in pixel. Use "0" to deactivate the outline')],
                    [sg.Checkbox("Enable antialiasing for the font. (''Pixel-smearing'' of the edges to reduce blockiness. Can be blurry)", default=False, k='fontAntialiasing', disabled=False, enable_events=True)],
                    [sg.HorizontalSeparator()],
                    [sg.T('Untick all in order to activate the sparkly particles again.', font=("Segoe UI", 16))],
                    [sg.Checkbox('Show RGB value of the color of the pixel under the cursor. Also draws a 40x40 square in that color.', default=False, k='showColor', disabled=False, enable_events=True)],
                    [sg.Checkbox('Show complementary color instead', default=False, k='complementaryColor', disabled=False, enable_events=True)],
                    [sg.Radio('rgb complement', 'compSwitch', default=True, k='rgbComplement', disabled=False, enable_events=True),
                     sg.Radio('ryb (artist) complement (Follows: "red???green, yellow???purple, and blue???orange" but seems inaccurate inbetween', 'compSwitch', k='artistComplement', disabled=False, enable_events=True)],
                    [sg.Checkbox('Clock: Show a text-based clock on the right the cursor.', default=False, k='showClock', disabled=False, enable_events=True)],
                    [sg.Checkbox('CPU-usage: Show in percent beside the cursor.', default=False, k='showCPU', disabled=False, enable_events=True)],
                    [sg.Checkbox('RAM-usage: Show in percent alongside the cursor', default=False, k='showRAM', disabled=False, enable_events=True)],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox("Draw an image somewhere around the cursor (gifs don't move)", default=False, k='showImage', disabled=False, enable_events=True)],
                    [sg.Text('Choose Image'), sg.InputText(size=(65, 1), k='imagePath'),
                     sg.FileBrowse('Browse', size=(10, 1), file_types=file_types, enable_events=True)],
                    [sg.T('(Only ".png", ".jpg", ".jpeg", ".tiff" ".gif" or ".bmp" supported.)', font=("Segoe UI", 10))],
                    [sg.Image(data=get_img_data(imagePath, first=True), k='image')]
                    ]

    preview_layout = [[sg.Canvas(size=(120, 33), k='graph')],
                      [sg.T('scatter plot with color map that changes?? X is time, Y is brightness (to death) and the color is color, of course?')],
                      [sg.T('')]]

    console_layout = [[sg.Output(size=(120, 33), font=("Segoe UI", 10))],
                      [sg.T("Please don't look under the rug.")]]

    tabs_layout = [[sg.TabGroup([[sg.Tab('General settings', general_layout),
                                  sg.Tab('Color settings', color_layout),
                                  sg.Tab('Dynamics', dynamic_layout),
                                  sg.Tab('Other things stuck to your mouse', other_layout),
                                  #sg.Tab('Preview', preview_layout),
                                  sg.Tab('Console output', console_layout)]])]]

    layout = [[sg.T('ShitStuckToYourMouse', size=(74, 1), justification='center', font=("Segoe UI", 16), relief=sg.RELIEF_RIDGE)],
              [sg.Column(tabs_layout, scrollable=True, vertical_scroll_only=True, size=(900, 600))],
              [sg.Button('Save and Run', k='Save-n-Run', enable_events=True), sg.T('  '),
               sg.Button('Save', k='Save', enable_events=True), sg.T('  '),
               sg.Button('Close child process', k='Close', enable_events=True), sg.T('  '),
               sg.Button('Reset to defaults', k='Reset', enable_events=True)],
              [sg.Button('Exit', k='Exit', enable_events=True),
               sg.Button('Hide Window', k='Hide', enable_events=True),
               sg.T('Press "F5" to Save and Run or "Esc" to Close')]]

    return sg.Window('ShitStuckToYourMouse configuration', layout, icon=poopImage, finalize=True, enable_close_attempted_event=True)

# import re
# str='#ffffff' # Your Hex
#
# match=re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', str)
#
# if match:
#   print 'Hex is valid'
#
# else:
#   print 'Hex is not valid'

def main():
    global config, particleColor, fontColor, outlineColor, ageColorSpeed, imagePath
    #sg.theme('Dark')  # redundant
    sg.set_options(font=("Segoe UI", 10))  # global font
    menu = ["", ["Show Window", "Hide Window", "---", "Exit"]]  # Tray-icon context-menu
    window = make_window('darkbrown1')  # not dark enough // Good one: Dark, darkgrey1, 11, 13, 15, darkbrown1
    # add them browser? naaaah
    window.bind('<F5>', 'F5 pressed')
    window.bind('<Escape>', 'Escape pressed')
    tray = SystemTray(menu, single_click_events=False, window=window, tooltip="ShitStuckToYourMouse", icon=resource_path(".\poop.ico"))
    print(sg.get_versions())
    proc = False  # Initiate variable for check if subprocess.Popen == True
    otherProc = False
    pid = None
    if not exists(imagePath) or imagePath == '':
        doesImageFileExist = False
    else:
        doesImageFileExist = True
    getVariablesFromConfig(window)

    #update display of some settings once
    event, values = window.read(timeout=250)
    window['useOffset'].update(values['useOffset'])
    window['offsetX'].update(values['offsetX'])
    window['offsetY'].update(values['offsetY'])
    values['useOffset2'] = values['useOffset']
    values['offsetX2'] = values['offsetX']
    values['offsetY2'] = values['offsetY']
    window['useOffset2'].update(values['useOffset2'])
    window['offsetX2'].update(values['offsetX2'])
    window['offsetY2'].update(values['offsetY2'])
    try:
        while True:
            event, values = window.read(timeout=1000)
            particleColor = values['particleColor']
            fontColor = values['fontColor']
            outlineColor = values['outlineColor']
            imagePath = values['imagePath']

            if event in (None, 'Exit'):
                if proc or otherProc:
                    if psutil.pid_exists(pid):
                        kill_proc_tree(pid=pid)
                        print('Subprocess killed')
                    else:
                        print("Subprocess already dead")
                proc = False
                otherProc = False
                break

            if values['showColor'] or values['showImage']:
                window['showClock'].update(disabled=True)
                window['showCPU'].update(disabled=True)
                window['showRAM'].update(disabled=True)
                if values['showColor']:
                    window['showColor'].update(disabled=False)
                    window['complementaryColor'].update(disabled=False)
                    if values['complementaryColor']:
                        window['rgbComplement'].update(disabled=False)
                        window['artistComplement'].update(disabled=False)
                    else:
                        window['rgbComplement'].update(disabled=True)
                        window['artistComplement'].update(disabled=True)
                    window['showImage'].update(disabled=True)
                else:
                    window['showColor'].update(disabled=True)
                    window['complementaryColor'].update(disabled=True)
                    window['rgbComplement'].update(disabled=True)
                    window['artistComplement'].update(disabled=True)
                    window['showImage'].update(disabled=False)
            elif values['showClock'] or values['showCPU'] or values['showRAM']:
                window['showClock'].update(disabled=False)
                window['showCPU'].update(disabled=False)
                window['showRAM'].update(disabled=False)
                window['showImage'].update(disabled=True)
                window['showColor'].update(disabled=True)
                window['complementaryColor'].update(disabled=True)
                window['rgbComplement'].update(disabled=True)
                window['artistComplement'].update(disabled=True)
            else:
                window['showClock'].update(disabled=False)
                window['showCPU'].update(disabled=False)
                window['showRAM'].update(disabled=False)
                window['showImage'].update(disabled=False)
                window['showColor'].update(disabled=False)
                window['complementaryColor'].update(disabled=True)
                window['rgbComplement'].update(disabled=True)
                window['artistComplement'].update(disabled=True)

            if not values['ageColor']:
                window['ageColorSpeed'].update(disabled=True)
                window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                window['ageColorSpeedFine'].update(disabled=True)
                window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_background_color())
                window['ageColorSlope'].update(disabled=True)
                window['ageColorSlopeConcavity'].update(disabled=True)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_background_color())
            else:
                window['ageColorSpeed'].update(disabled=False)
                window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_slider_color())
                window['ageColorSpeedFine'].update(disabled=False)
                window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_slider_color())
                window['ageColorSlope'].update(disabled=False)
                window['ageColorSlopeConcavity'].update(disabled=False)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_slider_color())
                if values['ageColorSlope']:
                    window['ageColorSpeed'].update(disabled=True)
                    window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSpeedFine'].update(disabled=True)
                    window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSlopeConcavity'].update(disabled=False)
                    window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_slider_color())
                else:
                    window['ageColorSpeed'].update(disabled=False)
                    window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_slider_color())
                    window['ageColorSpeedFine'].update(disabled=False)
                    window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_slider_color())
                    window['ageColorSlopeConcavity'].update(disabled=False)
                    window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_background_color())

            if values['dynamic']:
                window['randomMod'].update(disabled=True)
                window['randomMod'].Widget.config(troughcolor=sg.theme_background_color())
                window['randomModDynamic'].update(disabled=False)
                window['randomModDynamic'].Widget.config(troughcolor=sg.theme_slider_color())
                window['levelVelocity_1'].update(disabled=False)
                window['levelVelocity_2'].update(disabled=False)
                window['levelVelocity_3'].update(disabled=False)
                window['levelVelocity_4'].update(disabled=False)
                window['levelNumParticles_1'].update(disabled=False)
                window['levelNumParticles_2'].update(disabled=False)
                window['levelNumParticles_3'].update(disabled=False)
                window['levelNumParticles_4'].update(disabled=False)
            else:
                window['randomMod'].update(disabled=False)
                window['randomMod'].Widget.config(troughcolor=sg.theme_slider_color())
                window['randomModDynamic'].update(disabled=True)
                window['randomModDynamic'].Widget.config(troughcolor=sg.theme_background_color())
                window['levelVelocity_1'].update(disabled=True)
                window['levelVelocity_2'].update(disabled=True)
                window['levelVelocity_3'].update(disabled=True)
                window['levelVelocity_4'].update(disabled=True)
                window['levelNumParticles_1'].update(disabled=True)
                window['levelNumParticles_2'].update(disabled=True)
                window['levelNumParticles_3'].update(disabled=True)
                window['levelNumParticles_4'].update(disabled=True)

            if values['useOffset']:
                window['offsetX'].update(disabled=False)
                window['offsetY'].update(disabled=False)
                window['markPosition'].update(disabled=False)
                window['offsetX2'].update(disabled=False)
                window['offsetY2'].update(disabled=False)
            else:
                window['offsetX'].update(disabled=True)
                window['offsetY'].update(disabled=True)
                window['markPosition'].update(disabled=True)
                window['offsetX2'].update(disabled=True)
                window['offsetY2'].update(disabled=True)

            if event == tray.key:
                #print(f"System Tray Event = ", values[event])  # create key-error
                event = values[event]

            if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
                print('\n============ Event=', event, ' ==============')
                # if not event == 'Save-n-Run' and not event == 'Save' and not event == 'Close' and not event == 'Browse' and not event == 'Reset' and not event == 'Hide':
                #     print(values[event])

            elif event in (None, 'Browse') or event in (None, 'imagePath'):
                imagePath = values['imagePath']
                if exists(imagePath):
                    window['image'].update(data=get_img_data(imagePath, first=True))
                    doesImageFileExist = True
                else:
                    window['image'].update(data='')
                    sg.popup_no_wait('Error: File does not exist', text_color='#ffc000', button_type=5, auto_close=True,
                                     auto_close_duration=3, non_blocking=True, font=("Segoe UI", 26), no_titlebar=True, keep_on_top=True)
                    doesImageFileExist = False
                    print('Error: %s does not exist' % imagePath)
            #----------------------

            if event in (None, 'Reset'):
                answer = sg.popup_yes_no('Reset all settings to defaults?')
                if answer == 'Yes' or answer == 'yes':
                    if proc or otherProc:
                        if psutil.pid_exists(pid):
                            kill_proc_tree(pid=pid)
                            print("Subprocess killed")
                        else:
                            print("Subprocess already dead")
                    proc = False
                    otherProc = False
                    setDefaults()
                    getVariablesFromConfig(window)
                    event, values = window.read(timeout=250)
                    values['particleColor'] = config.get("SPARKLES", "particleColor")
                    particleColor = values['particleColor']
                    window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                    values['fontColor'] = config.get("OTHER", "fontColor")
                    fontColor = values['fontColor']
                    window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))
                    values['outlineColor'] = config.get("OTHER", "outlineColor")
                    outlineColor = values['outlineColor']
                    window['outline color picker button'].update(('Outline color picker: %s' % outlineColor), button_color=("#808080", outlineColor))
                    values['useOffset2'] = values['useOffset']
                    values['offsetX2'] = values['offsetX']
                    values['offsetY2'] = values['offsetY']
                    window['useOffset2'].update(values['useOffset'])
                    window['offsetX2'].update(values['offsetX'])
                    window['offsetY2'].update(values['offsetY'])
                    values['imagePath'] = str(config.get("OTHER", "imagePath"))
                    imagePath = values['imagePath']
                    if exists(imagePath):
                        window['image'].update(data=get_img_data(imagePath, first=True))
                else:
                    continue
            # ---------------------
            # F5                               65474     0xFFC2
            elif event in (None, 'Save-n-Run') or event in (None, 'F5 pressed'):
                values['randomMod'] = int(values['randomMod'])  # because slider returns FLOAT, even if "(range=(0, 100),  resolution=1)". GRRR
                if particleColor == "None" or values['particleColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = config.get("SPARKLES", "particleColor")
                if fontColor == "None" or values['fontColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("OTHER", "fontColor")  # Get last saved values
                    values['fontColor'] = config.get("OTHER", "fontColor")
                if outlineColor == "None" or values['outlineColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    outlineColor = config.get("OTHER", "outlineColor")  # Get last saved values
                    values['outlineColor'] = config.get("OTHER", "outlineColor")
                updateConfig(values)
                print('All values saved to config.ini')
                # print(values)
                event, values = window.read(timeout=1000)
                values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                values['fontColor'] = config.get("OTHER", "fontColor")
                fontColor = values['fontColor']
                window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))
                values['outlineColor'] = config.get("OTHER", "outlineColor")
                outlineColor = values['outlineColor']
                window['outline color picker button'].update(('Outline color picker: %s' % outlineColor), button_color=("#808080", outlineColor))
                values['useOffset2'] = values['useOffset']
                values['offsetX2'] = values['offsetX']
                values['offsetY2'] = values['offsetY']
                window['useOffset2'].update(values['useOffset'])
                window['offsetX2'].update(values['offsetX'])
                window['offsetY2'].update(values['offsetY'])
                if values['showImage']:
                    if not exists(imagePath) or imagePath == '':
                        window['image'].update(data='')
                        sg.popup_no_wait('Error: File does not exist', text_color='#ffc000', button_type=5, auto_close=True,
                                         auto_close_duration=3, non_blocking=True, font=("Segoe UI", 26), no_titlebar=True, keep_on_top=True)
                        doesImageFileExist = False
                        print('Error: %s does not exist' % imagePath)
                    else:
                        window['image'].update(data=get_img_data(imagePath, first=True))
                        doesImageFileExist = True
                if proc or otherProc:
                    if psutil.pid_exists(pid):
                        kill_proc_tree(pid=pid)
                        print('Subprocess killed')
                    else:
                        print("Subprocess already dead")
                proc = False
                otherProc = False
                if values['showColor'] or values['showClock'] or values['showCPU'] or values['showRAM'] or (values['showImage'] and doesImageFileExist):
                    if isCompiledToExe:
                        otherProc = Popen("other.exe", shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW, cwd=getcwd())
                    else:
                        otherProc = Popen("py other.pyw", shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW)
                    pid = otherProc.pid
                    print('Subprocess Started')
                    print(otherProc, " with process id: ", pid)
                elif not values['showColor'] and not values['showClock'] and not values['showCPU'] and not values['showRAM'] and not values['showImage']:
                    sg.popup_no_wait('Starting ... ', text_color='#00ff00', button_type=5, auto_close=True,
                                     auto_close_duration=3, non_blocking=True, font=("Segoe UI", 26), no_titlebar=True, keep_on_top=True)
                    if isCompiledToExe:
                        proc = Popen("sparkles.exe", shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW, cwd=getcwd())
                    else:  # getcwd() because of an error that thw current working directory couldn't be opened, I think
                        proc = Popen("py sparkles.pyw", shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE, creationflags=CREATE_NO_WINDOW)
                    pid = proc.pid
                    print('Subprocess Started')
                    print(proc, " with process id: ", pid)
                else:
                    if proc or otherProc:
                        if psutil.pid_exists(pid):
                            kill_proc_tree(pid=pid)
                            print('Subprocess killed')
                        else:
                            print("Subprocess already dead")
                    proc = False
                    otherProc = False
            # ---------------------

            elif event in (None, 'Save'):
                values['randomMod'] = int(values['randomMod'])  # because slider returns FLOAT, even if "(range = (0, 100),  resolution = 1)". GRRR
                if particleColor == "None" or values['particleColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = config.get("SPARKLES", "particleColor")
                if fontColor == "None" or values['fontColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("SPARKLES", "fontColor")  # Get last saved values
                    values['fontColor'] = config.get("SPARKLES", "fontColor")
                if outlineColor == "None" or values['outlineColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    outlineColor = config.get("SPARKLES", "outlineColor")  # Get last saved values
                    values['outlineColor'] = config.get("SPARKLES", "outlineColor")
                updateConfig(values)
                print('All values saved to config.ini')
                # print(values)
                event, values = window.read(timeout=1000)
                values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                values['fontColor'] = config.get("OTHER", "fontColor")
                fontColor = values['fontColor']
                window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))
                values['outlineColor'] = config.get("OTHER", "outlineColor")
                outlineColor = values['outlineColor']
                window['outline color picker button'].update(('Outline color picker: %s' % outlineColor), button_color=("#808080", outlineColor))
                values['useOffset2'] = values['useOffset']
                values['offsetX2'] = values['offsetX']
                values['offsetY2'] = values['offsetY']
                window['useOffset2'].update(values['useOffset'])
                window['offsetX2'].update(values['offsetX'])
                window['offsetY2'].update(values['offsetY'])
                if values['showImage']:
                    if not exists(imagePath) or imagePath == '':
                        window['image'].update(data='')
                        sg.popup_no_wait('Error: File does not exist', text_color='#ffc000', button_type=5, auto_close=True,
                                         auto_close_duration=3, non_blocking=True, font=("Segoe UI", 26), no_titlebar=True, keep_on_top=True)
                        doesImageFileExist = False
                        print('Error: %s does not exist' % imagePath)
                    else:
                        window['image'].update(data=get_img_data(imagePath, first=True))
                        doesImageFileExist = True
            # ---------------------
            elif event in (None, 'Close') or event in (None, 'Escape pressed'):
                if proc or otherProc:
                    if psutil.pid_exists(pid):
                        kill_proc_tree(pid=pid)
                        print('Subprocess killed')
                    else:
                        print("Subprocess already dead")
                proc = False
                otherProc = False

            elif event in (None, 'Hide'):
                window.hide()
                tray.show_icon()

            elif event in (None, 'Exit'):
                tray.hide_icon()
                if proc or otherProc:
                    if psutil.pid_exists(pid):
                        kill_proc_tree(pid=pid)
                        print('Subprocess killed')
                    else:
                        print("Subprocess already dead")
                proc = False
                otherProc = False
                break

            elif event in (None, sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                window.un_hide()
                window.bring_to_front()

            elif event in ("Show Window", sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                window.un_hide()
                window.bring_to_front()

            elif event in ("Hide Window", sg.WIN_CLOSE_ATTEMPTED_EVENT):
                tray.hide_icon()
                if proc or otherProc:
                    if psutil.pid_exists(pid):
                        kill_proc_tree(pid=pid)
                        print('Subprocess killed')
                    else:
                        print("Subprocess already dead")
                proc = False
                otherProc = False
                break

            elif event in (None, 'particleColor'):  # Update color and text of the color-picker button
                if particleColor == "None" or values['particleColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                event, values = window.read(timeout=1000)
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))

            elif event in (None, 'fontColor'):  # Update color and text of the color-picker button
                if fontColor == "None" or values['fontColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("OTHER", "fontColor")  # Get last saved values
                    values['fontColor'] = config.get("OTHER", "fontColor")
                fontColor = values['fontColor']
                event, values = window.read(timeout=1000)
                window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))

            elif event in (None, 'outlineColor'):  # Update color and text of the color-picker button
                if outlineColor == "None" or values['outlineColor'] == "None" :  # check if no color was chosen in the popup. Happens when cancelled
                    outlineColor = config.get("OTHER", "outlineColor")  # Get last saved values
                    values['outlineColor'] = config.get("OTHER", "outlineColor")
                outlineColor = values['outlineColor']
                event, values = window.read(timeout=1000)
                window['outline color picker button'].update(('Outline color picker: %s' % outlineColor), button_color=("#808080", outlineColor))

            elif event in (None, 'ageColorSpeed'):  # Update ageColorSpeedFine slider
                ageColorSpeed = values['ageColorSpeed']
                values['ageColorSpeedFine'] = ageColorSpeed
                window['ageColorSpeedFine'].update(ageColorSpeed, range=(ageColorSpeed-2.00, ageColorSpeed+2.00))

            elif event in (None, 'ageColorSpeedFine'):  # Update ageColorSpeedFine slider
                values['ageColorSpeed'] = values['ageColorSpeedFine']
                window['ageColorSpeed'].update(values['ageColorSpeedFine'])

            elif event in (None, 'useOffset2') or event in (None, 'offsetX2') or event in (None, 'offsetY2'):
                values['useOffset'] = values['useOffset2']
                values['offsetX'] = values['offsetX2']
                values['offsetY'] = values['offsetY2']
                window['useOffset'].update(values['useOffset'])
                window['offsetX'].update(values['offsetX'])
                window['offsetY'].update(values['offsetY'])

            elif event in (None, 'useOffset') or event in (None, 'offsetX') or event in (None, 'offsetY'):
                values['useOffset2'] = values['useOffset']
                values['offsetX2'] = values['offsetX']
                values['offsetY2'] = values['offsetY']
                window['useOffset2'].update(values['useOffset2'])
                window['offsetX2'].update(values['offsetX2'])
                window['offsetY2'].update(values['offsetY2'])

            # elif event in (None, 'rgbComplement'):
            #     values['artistComplement'] = False
            #     window['artistComplement'].update(values['artistComplement'])
            #
            # elif event in (None, 'artistComplement'):
            #     values['rgbComplement'] = False
            #     window['rgbComplement'].update(values['rgbComplement'])

            # write console output of subprocess into parent console
            # THIS HANGS THE GUI --- TRY SOMETHING ELSE
            # if proc or otherProc:
            #     if proc:
            #         for line in proc.stdout:
            #             print(line.decode("utf8"))
            #     else:
            #         for line in otherProc.stdout:
            #             print(line.decode("utf8"))

    finally:  # catch every exception and make sure to leave correctly
        tray.hide_icon()
        if proc or otherProc:
            if psutil.pid_exists(pid):
                kill_proc_tree(pid=pid)
                print('Subprocess killed err')
            else:
                print("Subprocess already dead err")

    if proc or otherProc:
        if psutil.pid_exists(pid):
            kill_proc_tree(pid=pid)
            print('Subprocess killed main')
        else:
            print("Subprocess already dead main")

            print("killed last subprocess")
    print("close window")
    tray.hide_icon()  # sometimes doesn't have an effect and the icon stays ...
    tray.close()  # optional but without a close, the icon may "linger" until moused over | still with it
    window.close()


if __name__ == '__main__':
    global config
    # --------- DEV FLAGS ----------
    #  -------------------------------

    isCompiledToExe = False

    #  -------------------------------
    # --------- DEV FLAGS ----------

    cleanup_mei()  # see comment inside
    config = CaseConfigParser()
    config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
    config.read("config.ini")  # Read config file

    if not config.has_section("SPARKLES") or not config.has_section("OTHER"):
        setDefaults()
        print('No config file exists. Writing new one with default values...')
        print(config)

    particleColor = str(config.get("SPARKLES", "particleColor"))
    fontColor = str(config.get("OTHER", "fontColor"))
    outlineColor = str(config.get("OTHER", "outlineColor"))
    ageColorSpeed = float(config.get("SPARKLES", "ageColorSpeed"))
    imagePath = str(config.get("OTHER", "imagePath"))
    # I forgot why those five up there were necessary...

    layout = ""  # bullshit
    main()
#dead
