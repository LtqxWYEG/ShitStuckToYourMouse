
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
from io import BytesIO
#from json import (load as jsonload, dump as jsondump)
import PySimpleGUI as sg
from subprocess import PIPE, Popen, CREATE_NO_WINDOW
from PIL import Image, ImageTk
from os import path, listdir, getpid, kill, getcwd
from os.path import exists
import sys
from shutil import rmtree
import psutil
import signal


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


# settings = dict(config.items('SPARKLES'))  # I don't understand this for now
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
    except:
        sg.popup_no_wait('Error: Image does not exist', text_color = '#ffc000', button_type = 5, auto_close = True,
                         auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
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
    children = parent.children(recursive = True)
    if include_parent:
        children.append(parent)
    for p in children:
        p.send_signal(sig)
    gone, alive = psutil.wait_procs(children, timeout = timeout, callback = on_terminate)
    return gone, alive  # Thank you very much Mr. PySimpleGUI :)


def killProcessUsingOS(pid, sig=signal.SIGTERM):
    kill(pid, sig)
    return


def make_window(theme):
    global particleColor, fontColor, ageColorSpeed, imagePath
    sg.theme(theme)
    file_types = [("Images", "*.png *.jpg *.jpeg *.tiff *.bmp *.gif"), ("All files (*.*)", "*.*")]

    general_layout = [[sg.Spin([i for i in range(1, 400)], initial_value = 60, font=("Segoe UI", 16), k = 'FPS', enable_events = True),
                       sg.T('Frames per second. Also affects number of particles as they are spawned per frame.')],
                      [sg.Checkbox('Interpolate mouse movement', default = True, k = 'interpolateMouseMovement', enable_events = True)],
                      [sg.T('Exp.: Draw some particles between current position of the cursor and that of last frame. (Interpolation should have almost no effect on performance)', pad = (10, (0, 15)))],
                      [sg.Checkbox('Add offset to the position of the particle origin', default = False, k = 'useOffset', enable_events = True),
                       sg.Checkbox('Mark position of particle origin. Use for offset tuning', default = False, k = 'markPosition', disabled = False, enable_events = True)],
                      [sg.T('X '), sg.Spin([i for i in range(-99, 99)], initial_value = 20, font=("Segoe UI", 16), k = 'offsetX', disabled = False, enable_events = True),
                       sg.T('Y '), sg.Spin([i for i in range(-99, 99)], initial_value = 10, font=("Segoe UI", 16), k = 'offsetY', disabled = False, enable_events = True),
                       sg.T('Offset in pixel. (0, 0 = tip of cursor)')],
                      [sg.Spin([i for i in range(1, 11)], initial_value = 2, font=("Segoe UI", 16), k = 'particleSize', enable_events = True), sg.T('Particle size in pixel * pixel')],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 1, font=("Segoe UI", 16), k = 'numParticles', enable_events = True), sg.T('Number of particles to spawn every frame')],

                      [sg.HorizontalSeparator()],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 60, font=("Segoe UI", 16), k = 'particleAge', enable_events = True), sg.T('Particle age (in frames) OR modifier for time until brightness < 7 (death)')],
                      [sg.T('Increase for slower brightness decline (concavity of downward slope)', pad = (10, (15, 0)))],
                      [sg.Slider(range=(0.001, 9.999), default_value = 5.300, font=("Segoe UI", 14), resolution = .001, size=(70, 15),
                                 orientation='horizontal', k = 'ageBrightnessMod', enable_events = True)],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 12, font=("Segoe UI", 16), k = 'ageBrightnessNoise', enable_events = True),
                       sg.T('Adds random noise (twinkling) to age/brightness: brightness = random(+|-value). 0 for no noise')],

                      [sg.HorizontalSeparator()],
                      [sg.T('Adds random motion to random direction to particles: mouseSpeed(xy) +|- randomMod. Deactivate with 0. Deactivated if dynamic is True', pad = (10, (15, 0)))],
                      [sg.Slider(range = (0, 100), default_value = 10, font=("Segoe UI", 14), resolution = 1, size = (70, 15),
                                 orientation = 'horizontal', disabled = False, k = 'randomMod', enable_events = True, trough_color = sg.theme_slider_color())],
                      #[sg.T('--- Scroll down ---')],
                      [sg.T('Multiply velocity added to particle by mouse movement: velocity * velocityMod', pad = (10, (15, 0)))],
                      [sg.Slider(range=(-3.000, 3.000), default_value = 1.000, font=("Segoe UI", 14), resolution = .001, size=(70, 15),
                                 orientation='horizontal', k = 'velocityMod', enable_events = True)],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 200, font=("Segoe UI", 16), k = 'velocityClamp', enable_events = True),
                       sg.T('Max. particle velocity')],
                      [sg.T('x and y motion added to any particle each frame. (Motion vector with direction: 0.0, 0.1 = a motion of .1 in downwards direction.)', pad = (10, (15, 0)))],
                      [sg.Slider(range=(-29.999, 29.999), default_value = 0.000, font=("Segoe UI", 14), resolution = .001, size=(34, 15),
                                 orientation='horizontal', k = 'GRAVITY_X', enable_events = True),
                       sg.Slider(range=(-29.999, 29.999), default_value = 0.025, font=("Segoe UI", 14), resolution = .001, size=(35, 15),
                                 orientation='horizontal', k = 'GRAVITY_Y', enable_events = True)],
                      [sg.T('Particle drag, higher equals less drag: (drag * particle speed) per frame. --If >1 then particles speed up--', pad = (10, (15, 0)))],
                      [sg.Slider(range = (0.000, 2.999), default_value = 0.850, font=("Segoe UI", 14), resolution = .001, size = (70, 15),
                                 orientation = 'horizontal', k = 'drag', enable_events = True)]
                      ]

    color_layout = [[sg.Input(visible=False, enable_events=True, k='particleColor'), sg.ColorChooserButton('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor), size = (25, 2), font=("Segoe UI", 16), k = 'color picker button')],
                    [sg.T('Use "#ff0001" for full HSV color when ageColor is True. (Full 255 red plus 1 blue = hsv hue of 360°)', pad = (10, (0, 15)))],
                    [sg.Checkbox('Randomly colored particles', default = False, k = 'particleColorRandom', enable_events = True)],
                    [sg.Checkbox('Change hue over time. (Hue aging)', default = True, k = 'ageColor', enable_events = True)],

                    [sg.HorizontalSeparator()],
                    [sg.T('Hue aging speed factor. Negative values decrease hue [of hsv color] over time, positive increase it. (Neg: towards orange. Pos: towards purple)', pad = (10, (15, 0)))],
                    [sg.Slider(range = (-99.99, 99.99), default_value = -5.50, font=("Segoe UI", 14), resolution = .01, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorSpeed', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                    [sg.T('Fine adjustment: ', font=("Segoe UI", 14)),
                     sg.Slider(range = (ageColorSpeed-2.00, ageColorSpeed+2.00), default_value = ageColorSpeed, font=("Segoe UI", 14), resolution = .001, size = (56.9, 15),
                               orientation = 'horizontal', k = 'ageColorSpeedFine', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox('Age on a concave downward curve: At the start slower, but then increasingly faster decline of hue value.', default = True, k = 'ageColorSlope', disabled = False, enable_events = True)],
                    [sg.T('(More pronounced upper colors. [Like purple and blue])', pad = (10, (0, 15)))],
                    [sg.T('Increase concavity of the downward slope that represents hue over time. (Think: https://i.stack.imgur.com/bGi9k.jpg)', pad = (10, (15, 0)))],
                    [sg.Slider(range = (0.000, 1.199), default_value = 0.420, font=("Segoe UI", 14), resolution = .001, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorSlopeConcavity', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Spin([i for i in range(0, 200)], initial_value = 50, font=("Segoe UI", 16), k = 'ageColorNoise', enable_events = True),
                       sg.T('Add random hue variation to combat too uniform-looking hue-aging: hue = random(+|-value). "0" disables this.')],
                    [sg.T('Hue variation bias towards more positive or negative values: 0 = only positive noise | 0.5 = balanced | 1.0 = only negative noise', pad = (10, (15, 0)))],
                    [sg.Slider(range = (0.000, 1.000), default_value = 0.420, font=("Segoe UI", 14), resolution = .001, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorNoiseMod', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())]
                    ]

    dynamic_layout = [[sg.Text('Dynamics settings')],
                      [sg.Checkbox('Enable dynamic behavior', default = True, k = 'dynamic', enable_events = True)],
                      [sg.T('Exp.: The faster the movement, the more particles are created and the more random motion will be added.', pad = (10, (0, 15)))],

                      [sg.HorizontalSeparator()],
                      [sg.T('Adds random motion to random direction to DYNAMIC particles: mouseSpeed(direction) * randomMod.', pad = (10, (15, 0)))],
                      [sg.Slider(range = (0.00, 0.99), default_value = 0.16, font=("Segoe UI", 14), resolution = .01, size = (70, 15),
                                 orientation = 'horizontal', k = 'randomModDynamic', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],

                      [sg.HorizontalSeparator()],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 5, font=("Segoe UI", 16), k = 'levelNumParticles_1', disabled = False, enable_events = True), sg.T('Level 1 '),
                       sg.Spin([i for i in range(1, 100)], initial_value = 8, font=("Segoe UI", 16), k = 'levelNumParticles_2', disabled = False, enable_events = True), sg.T('Level 2 '),
                       sg.Spin([i for i in range(1, 100)], initial_value = 14, font=("Segoe UI", 16), k = 'levelNumParticles_3', disabled = False, enable_events = True), sg.T('Level 3'),
                       sg.Spin([i for i in range(1, 100)], initial_value = 20, font=("Segoe UI", 16), k = 'levelNumParticles_4', disabled = False, enable_events = True), sg.T('Level 4 - spawn this many particles ...')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 15, font=("Segoe UI", 16), k = 'levelVelocity_1', disabled = False, enable_events = True), sg.T('Level 1'),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 30, font=("Segoe UI", 16), k = 'levelVelocity_2', disabled = False, enable_events = True), sg.T('Level 2'),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 60, font=("Segoe UI", 16), k = 'levelVelocity_3', disabled = False, enable_events = True), sg.T('Level 3 '),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 120, font=("Segoe UI", 16), k = 'levelVelocity_4', disabled = False, enable_events = True), sg.T('Level 4 - if mouse is moving this fast in pixels per frame ...')],
                      [sg.T('Number of particles at mouse velocities below "Level 1" are defined by the value (numParticles) in the General tab.')]
                      ]

    other_layout = [[sg.Text("Anything else one could find interesting to adhere to your mouse-cursor!")],
                    [sg.Text('Notice: FPS and offset from the "General"-tab are also used here:')],
                    [sg.Checkbox('Add offset to the position of the upper-right corner of these stupid things', default = False, k = 'useOffset2', enable_events = True)],
                    [sg.T('X '), sg.Spin([i for i in range(-99, 99)], initial_value = 20, font = ("Segoe UI", 16), k = 'offsetX2', disabled = False, enable_events = True),
                     sg.T('Y '), sg.Spin([i for i in range(-99, 99)], initial_value = 10, font = ("Segoe UI", 16), k = 'offsetY2', disabled = False, enable_events = True),
                     sg.T('Offset in pixel. (0, 0 = tip of cursor)')],

                    [sg.HorizontalSeparator()],
                    [sg.Input(visible = False, enable_events = True, k = 'fontColor'),
                     sg.ColorChooserButton('Font color picker: %s' % fontColor, button_color = ("#010101", fontColor), size = (25, 2), font = ("Segoe UI", 16), k = 'font color picker button')],

                    [sg.Spin([i for i in range(1, 100)], initial_value = 10, font = ("Segoe UI", 16), k = 'fontSize', enable_events = True),
                     sg.T('Font size in pt.')],
                    [sg.Checkbox('Show RGB value of the color of the pixel under the cursor. Also draws a 40x40 square in that color.', default = False, k = 'showColor', disabled = False, enable_events = True)],
                    [sg.Checkbox('Show complementary color instead', default = False, k = 'complementaryColor', disabled = False, enable_events = True)],
                    [sg.Checkbox('rgb complement', default = False, k = 'rgbComplement', disabled = False, enable_events = True),
                     sg.Checkbox('ryb (artist) complement (Follows: "red–green, yellow–purple, and blue–orange" but seems inaccurate inbetween', default = True, k = 'artistComplement', disabled = False, enable_events = True)],
                    [sg.Checkbox('Clock: Show a text-based clock on the right the cursor.', default = False, k = 'showClock', disabled = False, enable_events = True)],
                    [sg.Checkbox('CPU-usage: Show in percent beside the cursor.', default = False, k = 'showCPU', disabled = False, enable_events = True)],
                    [sg.Checkbox('RAM-usage: Show in percent alongside the cursor', default = False, k = 'showRAM', disabled = False, enable_events = True)],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox("Draw an image somewhere around the cursor (gifs don't move)", default = False, k = 'showImage', disabled = False, enable_events = True)],
                    [sg.Text('Choose Image'), sg.InputText(size = (65, 1), k = 'imagePath'),
                     sg.FileBrowse('Browse', size = (10, 1), file_types = file_types, enable_events = True)],
                    [sg.T('(Only ".png", ".jpg", ".jpeg", ".tiff" ".gif" or ".bmp" supported.)', font = ("Segoe UI", 10))],
                    [sg.Image(data = get_img_data(imagePath, first = True), k = 'image')]
                    ]

    console_layout = [[sg.Output(size = (120, 33), font = ("Segoe UI", 10))],
                      [sg.T('Nothing to see here.')]]

    tabs_layout = [[sg.TabGroup([[sg.Tab('General settings', general_layout),
                                  sg.Tab('Color settings', color_layout),
                                  sg.Tab('Dynamics', dynamic_layout),
                                  sg.Tab('Other things stuck to your mouse', other_layout),
                                  sg.Tab('Console output', console_layout)]])]]

    layout = [[sg.T('PoopStuckToYourMouse', size = (74, 1), justification = 'center',
                    font = ("Segoe UI", 16), relief = sg.RELIEF_RIDGE)],
              [sg.Column(tabs_layout, scrollable = True, vertical_scroll_only = True, size = (900, 600))],
              [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '),
               sg.Button('Close child process', k = 'Close', enable_events = True), sg.T('  '),
               sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
              [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    return sg.Window('PoopStuckToYourMouse configuration', layout, finalize=True)


def main(config):
    print("DEV TEST main entry")
    global particleColor, fontColor, ageColorSpeed, imagePath
    sg.theme('Dark')
    sg.set_options(font=("Segoe UI", 10))
    window = make_window('Dark')
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
    while True:
        print("DEV TEST while loop start")
        event, values = window.read(timeout=250)
        particleColor = values['particleColor']
        fontColor = values['fontColor']
        imagePath = values['imagePath']
        if event in (None, 'Exit'):
            if proc or otherProc:
                #kill_proc_tree(pid = pid)
                killProcessUsingOS(pid = pid)
            proc = False
            otherProc = False
            break

        if values['showColor'] or values['showImage']:
            window['showClock'].update(disabled = True)
            window['showCPU'].update(disabled = True)
            window['showRAM'].update(disabled = True)
            if values['showColor']:
                window['showColor'].update(disabled = False)
                window['complementaryColor'].update(disabled = False)
                if values['complementaryColor']:
                    window['rgbComplement'].update(disabled = False)
                    window['artistComplement'].update(disabled = False)
                else:
                    window['rgbComplement'].update(disabled = True)
                    window['artistComplement'].update(disabled = True)
                window['showImage'].update(disabled = True)
            else:
                window['showColor'].update(disabled = True)
                window['complementaryColor'].update(disabled = True)
                window['rgbComplement'].update(disabled = True)
                window['artistComplement'].update(disabled = True)
                window['showImage'].update(disabled = False)
        elif values['showClock'] or values['showCPU'] or values['showRAM']:
            window['showClock'].update(disabled = False)
            window['showCPU'].update(disabled = False)
            window['showRAM'].update(disabled = False)
            window['showImage'].update(disabled = True)
            window['showColor'].update(disabled = True)
            window['complementaryColor'].update(disabled = True)
            window['rgbComplement'].update(disabled = True)
            window['artistComplement'].update(disabled = True)
        else:
            window['showClock'].update(disabled = False)
            window['showCPU'].update(disabled = False)
            window['showRAM'].update(disabled = False)
            window['showImage'].update(disabled = False)
            window['showColor'].update(disabled = False)
            window['complementaryColor'].update(disabled = True)
            window['rgbComplement'].update(disabled = True)
            window['artistComplement'].update(disabled = True)

        if not values['ageColor']:
            window['ageColorSpeed'].update(disabled = True)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorSpeedFine'].update(disabled = True)
            window['ageColorSpeedFine'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorSlope'].update(disabled = True)
            window['ageColorSlopeConcavity'].update(disabled = True)
            window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorNoise'].update(disabled = True)
            window['ageColorNoiseMod'].update(disabled = True)
            window['ageColorNoiseMod'].Widget.config(troughcolor = sg.theme_background_color())
        else:
            window['ageColorSpeed'].update(disabled = False)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_slider_color())
            window['ageColorSpeedFine'].update(disabled = False)
            window['ageColorSpeedFine'].Widget.config(troughcolor = sg.theme_slider_color())
            window['ageColorSlope'].update(disabled = False)
            window['ageColorSlopeConcavity'].update(disabled = False)
            window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_slider_color())
            window['ageColorNoise'].update(disabled = False)
            window['ageColorNoiseMod'].update(disabled = False)
            window['ageColorNoiseMod'].Widget.config(troughcolor = sg.theme_slider_color())
            if values['ageColorSlope']:
                window['ageColorSpeed'].update(disabled = True)
                window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_background_color())
                window['ageColorSpeedFine'].update(disabled = True)
                window['ageColorSpeedFine'].Widget.config(troughcolor = sg.theme_background_color())
                window['ageColorSlopeConcavity'].update(disabled = False)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_slider_color())
            else:
                window['ageColorSpeed'].update(disabled = False)
                window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_slider_color())
                window['ageColorSpeedFine'].update(disabled = False)
                window['ageColorSpeedFine'].Widget.config(troughcolor = sg.theme_slider_color())
                window['ageColorSlopeConcavity'].update(disabled = True)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_background_color())

        if values['dynamic']:
            window['randomMod'].update(disabled = True)
            window['randomMod'].Widget.config(troughcolor = sg.theme_background_color())
            window['randomModDynamic'].update(disabled = False)
            window['randomModDynamic'].Widget.config(troughcolor = sg.theme_slider_color())
            window['levelVelocity_1'].update(disabled = False)
            window['levelVelocity_2'].update(disabled = False)
            window['levelVelocity_3'].update(disabled = False)
            window['levelVelocity_4'].update(disabled = False)
            window['levelNumParticles_1'].update(disabled = False)
            window['levelNumParticles_2'].update(disabled = False)
            window['levelNumParticles_3'].update(disabled = False)
            window['levelNumParticles_4'].update(disabled = False)
        else:
            window['randomMod'].update(disabled = False)
            window['randomMod'].Widget.config(troughcolor = sg.theme_slider_color())
            window['randomModDynamic'].update(disabled = True)
            window['randomModDynamic'].Widget.config(troughcolor = sg.theme_background_color())
            window['levelVelocity_1'].update(disabled = True)
            window['levelVelocity_2'].update(disabled = True)
            window['levelVelocity_3'].update(disabled = True)
            window['levelVelocity_4'].update(disabled = True)
            window['levelNumParticles_1'].update(disabled = True)
            window['levelNumParticles_2'].update(disabled = True)
            window['levelNumParticles_3'].update(disabled = True)
            window['levelNumParticles_4'].update(disabled = True)
        if values['useOffset']:
            window['offsetX'].update(disabled = False)
            window['offsetY'].update(disabled = False)
            window['markPosition'].update(disabled = False)
            window['offsetX2'].update(disabled = False)
            window['offsetY2'].update(disabled = False)
        else:
            window['offsetX'].update(disabled = True)
            window['offsetY'].update(disabled = True)
            window['markPosition'].update(disabled = True)
            window['offsetX2'].update(disabled = True)
            window['offsetY2'].update(disabled = True)

        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print('\n============ Event = ', event, ' ==============')
            if not event == 'Save' and not event == 'Close' and not event == 'Browse' and not event == 'Reset':
                print(values[event])

        if event in (None, 'Reset'):
            answer = sg.popup_yes_no('Reset all settings to defaults?')
            if answer == 'Yes' or answer == 'yes':
                if proc or otherProc:
                    kill_proc_tree(pid = pid)
                    print('Subprocess killed')
                proc = False
                otherProc = False
                setDefaults()
                getVariablesFromConfig(window)
                event, values = window.read(timeout = 250)
                values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                values['fontColor'] = config.get("OTHER", "fontColor")
                fontColor = values['fontColor']
                window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))
                values['useOffset2'] = values['useOffset']
                values['offsetX2'] = values['offsetX']
                values['offsetY2'] = values['offsetY']
                window['useOffset2'].update(values['useOffset'])
                window['offsetX2'].update(values['offsetX'])
                window['offsetY2'].update(values['offsetY'])
                values['imagePath'] = str(config.get("OTHER", "imagePath"))
                imagePath = values['imagePath']
                if exists(imagePath):
                    window['image'].update(data = get_img_data(imagePath, first = True))
            else:
                continue

        elif event in (None, 'Browse') or event in (None, 'imagePath'):
            imagePath = values['imagePath']
            if exists(imagePath):
                window['image'].update(data = get_img_data(imagePath, first = True))
                doesImageFileExist = True
            else:
                window['image'].update(data = '')
                sg.popup_no_wait('Error: File does not exist', text_color = '#ffc000', button_type = 5, auto_close = True,
                                 auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
                doesImageFileExist = False
                print('Error: %s does not exist' % imagePath)

        # ---------------------
        elif event in (None, 'Save'):
            values['randomMod'] = int(values['randomMod'])  # because slider returns FLOAT, even if "(range = (0, 100),  resolution = 1)". GRRR
            updateConfig(values)
            print('All values saved to config.ini')
            print(values)
            event, values = window.read(timeout = 250)
            values['particleColor'] = config.get("SPARKLES", "particleColor")
            particleColor = values['particleColor']
            window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
            values['fontColor'] = config.get("OTHER", "fontColor")
            fontColor = values['fontColor']
            window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))
            values['useOffset2'] = values['useOffset']
            values['offsetX2'] = values['offsetX']
            values['offsetY2'] = values['offsetY']
            window['useOffset2'].update(values['useOffset'])
            window['offsetX2'].update(values['offsetX'])
            window['offsetY2'].update(values['offsetY'])
            if values['showImage']:
                if not exists(imagePath) or imagePath == '':
                    window['image'].update(data = '')
                    sg.popup_no_wait('Error: File does not exist', text_color = '#ffc000', button_type = 5, auto_close = True,
                                     auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
                    doesImageFileExist = False
                    print('Error: %s does not exist' % imagePath)
                else:
                    window['image'].update(data = get_img_data(imagePath, first = True))
                    doesImageFileExist = True
            if proc or otherProc:
                #kill_proc_tree(pid = pid)
                killProcessUsingOS(pid = pid)
                print('Subprocess killed')
            proc = False
            otherProc = False
            if values['showColor'] or values['showClock'] or values['showCPU'] or values['showRAM'] or (values['showImage'] and doesImageFileExist):
                sg.popup_no_wait('Starting ...', text_color = '#00ff00', button_type = 5, auto_close = True,
                                 auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
                otherProc = Popen("other.exe", shell = False, stdout = PIPE, stdin = PIPE, stderr = PIPE, creationflags = CREATE_NO_WINDOW,
                                  cwd = getcwd())
                #otherProc = Popen("py other.pyw", shell = False, stdout = PIPE, stdin = PIPE, stderr = PIPE, creationflags = CREATE_NO_WINDOW)
                pid = otherProc.pid
                print('Subprocess Started')
                print(otherProc, " with process id: ", pid)
            # elif values['showImage'] and doesImageFileExist:
            #     sg.popup_no_wait('Starting ...', text_color = '#00ff00', button_type = 5, auto_close = True,
            #                      auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
            #     otherProc = Popen("py other.py", shell = False, stdout = PIPE, stdin = PIPE, stderr = PIPE, creationflags = CREATE_NO_WINDOW)
            #     pid = otherProc.pid
            #     print('Subprocess Started')
            #     print(otherProc, " with process id: ", pid)
            elif not values['showColor'] and not values['showClock'] and not values['showCPU'] and not values['showRAM'] and not values['showImage']:
                sg.popup_no_wait('Starting ... if this is the first time it can take a while', text_color = '#00ff00', button_type = 5, auto_close = True,
                                 auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True, keep_on_top = True)
                proc = Popen("sparkles.exe", shell = False, stdout = PIPE, stdin = PIPE, stderr = PIPE, creationflags = CREATE_NO_WINDOW,
                             cwd = getcwd())
                #proc = Popen("py sparkles.pyw", shell = False, stdout = PIPE, stdin = PIPE, stderr = PIPE, creationflags = CREATE_NO_WINDOW)
                pid = proc.pid
                print('Subprocess Started')
                print(proc, " with process id: ", pid)
            else:
                if proc or otherProc:
                    #kill_proc_tree(pid = pid)
                    killProcessUsingOS(pid = pid)
                    print('Subprocess killed')
                proc = False
                otherProc = False
        # ---------------------

        elif event in (None, 'Close'):
            if proc or otherProc:
                #kill_proc_tree(pid = pid)
                killProcessUsingOS(pid = pid)
                print('Subprocess killed')
            proc = False
            otherProc = False

        elif event in (None, 'particleColor'):  # Update color and text of the color-picker button
            if particleColor == "None":
                particleColor = config.get("SPARKLES", "particleColor")
                values['particleColor'] = config.get("SPARKLES", "particleColor")
            particleColor = values['particleColor']
            window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))

        elif event in (None, 'fontColor'):  # Update color and text of the color-picker button
            if fontColor == "None":
                fontColor = config.get("OTHER", "fontColor")
                values['fontColor'] = config.get("OTHER", "fontColor")
            fontColor = values['fontColor']
            window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))

        elif event in (None, 'ageColorSpeed'):  # Update ageColorSpeedFine slider
            ageColorSpeed = values['ageColorSpeed']
            values['ageColorSpeedFine'] = ageColorSpeed
            window['ageColorSpeedFine'].update(ageColorSpeed, range = (ageColorSpeed-2.00, ageColorSpeed+2.00))

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

        elif event in (None, 'rgbComplement'):
            values['artistComplement'] = False
            window['artistComplement'].update(values['artistComplement'])

        elif event in (None, 'artistComplement'):
            values['rgbComplement'] = False
            window['rgbComplement'].update(values['rgbComplement'])

    print("DEV TEST while end")
    if proc or otherProc:
        #kill_proc_tree(pid = pid)
        killProcessUsingOS(pid = pid)
    window.close()


if __name__ == '__main__':
    print("DEV TEST if main")
    cleanup_mei()  # see comment inside
    config = CaseConfigParser()
    #parseList = CaseConfigParser(converters = {'list': lambda x: [i.strip() for i in x.split(',')]})
    config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
    config.read("config.ini")  # Read config file
    if not config.has_section("SPARKLES") or not config.has_section("OTHER"):
        setDefaults()
        print('No config file exists. Writing new one with default values...')
        print(config)
    particleColor = str(config.get("SPARKLES", "particleColor"))
    fontColor = str(config.get("OTHER", "fontColor"))
    ageColorSpeed = float(config.get("SPARKLES", "ageColorSpeed"))
    imagePath = str(config.get("OTHER", "imagePath"))
    # I forgot why those four up there were necessary...
    main(config)
#dead
print("DEV TEST end")
