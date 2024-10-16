# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#  Copyright (c) 2024.                                                         \
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


import base64
import configparser
import signal
import sys
from io import BytesIO
from os import path, listdir, getpid, kill, getcwd
from os.path import exists
from shutil import rmtree
from subprocess import PIPE, Popen, run, CREATE_NO_WINDOW
from time import sleep

# from json import (load as jsonload, dump as jsondump)
import FreeSimpleGUI as sg
import acrylic
import psutil
from PIL import Image, ImageTk

#from psgtray import SystemTray

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
    window['velocityFactorVector'].update(float(config.get("SPARKLES", "velocityFactorVector")))
    window['softClampVelocityVector'].update(int(config.get("SPARKLES", "softClampVelocityVector")))
    string = config.getlistfloat("SPARKLES", "manualSecondVector")
    window["manualSecondVector_X"].update(string[0])
    window["manualSecondVector_Y"].update(string[1])
    window['drag'].update(float(config.get("SPARKLES", "drag")))
    window['FPS'].update(int(config.get("SPARKLES", "FPS")))
    window['multitasking'].update(int(config.get("SPARKLES", "multitasking")))
    window['interpolateMouseMovement'].update(config.getboolean("SPARKLES", "interpolateMouseMovement"))
    window['useOffset'].update(config.getboolean("SPARKLES", "useOffset"))
    window['offsetX'].update(int(config.get("SPARKLES", "offsetX")))
    window['offsetY'].update(int(config.get("SPARKLES", "offsetY")))
    window['markPosition'].update(config.getboolean("SPARKLES", "markPosition"))
    window['numParticles'].update(int(config.get("SPARKLES", "numParticles")))
    window['dynamic'].update(config.getboolean("SPARKLES", "dynamic"))

    window['particleColor'].update(str(config.get("SPARKLES", "particleColor")))
    window['useColorUnderMouse'].update(config.getboolean("SPARKLES", "useColorUnderMouse"))
    window['particleColorHue'].update(float(config.get("SPARKLES", "particleColorHue")))
    window['particleColorRandom'].update(config.getboolean("SPARKLES", "particleColorRandom"))
    window['ageColor'].update(config.getboolean("SPARKLES", "ageColor"))
    window['colorRollover'].update(config.getboolean("SPARKLES", "colorRollover"))
    window['ageLinear'].update(config.getboolean("SPARKLES", "ageLinear"))
    window['ageLinearSpeed'].update(float(config.get("SPARKLES", "ageLinearSpeed")))
    window['ageColorSpeed'].update(float(config.get("SPARKLES", "ageColorSpeed")))
    window['ageColorSlope'].update(config.getboolean("SPARKLES", "ageColorSlope"))
    window['ageColorSlopeConcavity'].update(float(config.get("SPARKLES", "ageColorSlopeConcavity")))
    window['ageColorNoise'].update(int(config.get("SPARKLES", "ageColorNoise")))
    window['ageColorNoiseMod'].update(float(config.get("SPARKLES", "ageColorNoiseMod")))

    window['addRandomMouseInfluenceVector'].update(config.getboolean("SPARKLES", "addRandomMouseInfluenceVector"))
    window['randomSecondVector'].update(float(config.get("SPARKLES", "randomSecondVector")))
    window['chaoticSecondVector'].update(float(config.get("SPARKLES", "chaoticSecondVector")))
    window['addChaosSecondVector'].update(config.getboolean("SPARKLES", "addChaosSecondVector"))
    window['clampVelocitySecondVector'].update(config.getboolean("SPARKLES", "clampVelocitySecondVector"))

    window['addRandomParticleVector'].update(float(config.get("SPARKLES", "addRandomParticleVector")))
    window['vectorRotation'].update(float(config.get("SPARKLES", "vectorRotation")))
    window['randomRotation'].update(config.getboolean("SPARKLES", "randomRotation"))
    window['cumulativeVectorRotation'].update(config.getboolean("SPARKLES", "cumulativeVectorRotation"))
    window['secondVectorRotation'].update(config.getboolean("SPARKLES", "secondVectorRotation"))
    window['particleVectorRotation'].update(config.getboolean("SPARKLES", "particleVectorRotation"))
    window['strengthMouseInfluenceVector'].update(float(config.get("SPARKLES", "strengthMouseInfluenceVector")))
    
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
    config.set("SPARKLES", "velocityFactorVector", str(values['velocityFactorVector']))
    config.set("SPARKLES", "softClampVelocityVector", str(values['softClampVelocityVector']))
    string = [str(values["manualSecondVector_X"]), ', ', str(values["manualSecondVector_Y"])]
    secondVector_STRING = "".join(string)
    config.set("SPARKLES", "manualSecondVector", secondVector_STRING)
    config.set("SPARKLES", "drag", str(values['drag']))
    config.set("SPARKLES", "FPS", str(values['FPS']))
    config.set("SPARKLES", "multitasking", str(values['multitasking']))
    config.set("SPARKLES", "interpolateMouseMovement", str(values['interpolateMouseMovement']))
    config.set("SPARKLES", "useOffset", str(values['useOffset']))
    config.set("SPARKLES", "offsetX", str(values['offsetX']))
    config.set("SPARKLES", "offsetY", str(values['offsetY']))
    config.set("SPARKLES", "markPosition", str(values['markPosition']))
    config.set("SPARKLES", "numParticles", str(values['numParticles']))
    config.set("SPARKLES", "dynamic", str(values['dynamic']))

    config.set("SPARKLES", "particleColor", values['particleColor'])
    config.set("SPARKLES", "useColorUnderMouse", str(values['useColorUnderMouse']))
    config.set("SPARKLES", "particleColorHue", str(values['particleColorHue']))
    config.set("SPARKLES", "particleColorRandom", str(values['particleColorRandom']))
    config.set("SPARKLES", "ageColor", str(values['ageColor']))
    config.set("SPARKLES", "colorRollover", str(values['colorRollover']))
    config.set("SPARKLES", "ageLinear", str(values['ageLinear']))
    config.set("SPARKLES", "ageLinearSpeed", str(values['ageLinearSpeed']))
    config.set("SPARKLES", "ageColorSpeed", str(values['ageColorSpeed']))
    config.set("SPARKLES", "ageColorSlope", str(values['ageColorSlope']))
    config.set("SPARKLES", "ageColorSlopeConcavity", str(values['ageColorSlopeConcavity']))
    config.set("SPARKLES", "ageColorNoise", str(values['ageColorNoise']))
    config.set("SPARKLES", "ageColorNoiseMod", str(values['ageColorNoiseMod']))

    config.set("SPARKLES", "addRandomMouseInfluenceVector", str(values['addRandomMouseInfluenceVector']))
    config.set("SPARKLES", "randomSecondVector", str(values['randomSecondVector']))
    config.set("SPARKLES", "chaoticSecondVector", str(values['chaoticSecondVector']))
    config.set("SPARKLES", "addChaosSecondVector", str(values['addChaosSecondVector']))
    config.set("SPARKLES", "clampVelocitySecondVector", str(values['clampVelocitySecondVector']))

    config.set("SPARKLES", "addRandomParticleVector", str(values['addRandomParticleVector']))
    config.set("SPARKLES", "vectorRotation", str(values['vectorRotation']))
    config.set("SPARKLES", "randomRotation", str(values['randomRotation']))
    config.set("SPARKLES", "cumulativeVectorRotation", str(values['cumulativeVectorRotation']))
    config.set("SPARKLES", "secondVectorRotation", str(values['secondVectorRotation']))
    config.set("SPARKLES", "particleVectorRotation", str(values['particleVectorRotation']))
    config.set("SPARKLES", "strengthMouseInfluenceVector", str(values['strengthMouseInfluenceVector']))
    
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
                         auto_close_duration=3, non_blocking=True, font=(globalFont, 26 + globalFontSizeModifier), no_titlebar=True, keep_on_top=True)
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
    return gone, alive


def kill_all():
    global pid, proc, otherproc
    numberPIDs = len(pid)
    i = 0
    while i < numberPIDs:
        # if proc[i] or otherProc:
        if psutil.pid_exists(pid[i]):
            kill_proc_tree(pid = pid[i], include_parent = True)
            print("Subprocess " + str(pid[i]) + " killed")
        else:
            print("Subprocess already dead")
        i += 1
        if i == numberPIDs:
            proc = []
            pid = []
            otherProc = False
    print("Killed last subprocess")

#  Old version
    # numberPIDs = len(pid)
    # i = 0
    # while i < numberPIDs:
    #     if proc[i] or otherProc:
    #         if psutil.pid_exists(pid[i]):
    #             kill_proc_tree(pid = pid[i])
    #             print('Subprocess killed')
    #         else:
    #             print("Subprocess already dead")
    #
    #     otherProc = False
    #     i += 1
    #     if i == numberPIDs:
    #         proc = []
    #         pid = []


# def killProcessUsingOsKill(pid, sig=signal.SIGTERM):  # Use this for when compiled to exe // Apparently not. Mark for deletion
#     kill(pid, sig)
#     return


def make_window(theme):
    global particleColor, particleColorHue, fontColor, outlineColor, ageColorSpeed, imagePath, globalFont, globalFontSizeModifier, useColorUnderMouse
    sg.theme(theme)
    file_types = [("Images", "*.png *.jpg *.jpeg *.tiff *.bmp *.gif"), ("All files (*.*)", "*.*")]

    general_layout = [[sg.Spin([i for i in range(1, 400)], initial_value=60, font=(globalFont, 16 + globalFontSizeModifier), k='FPS', enable_events=True),
                       sg.T('Frames per second. Also affects number of particles - as they are spawned per frame.')],
                      [sg.Spin([i for i in range(1, 128)], initial_value=1, font=(globalFont, 16 + globalFontSizeModifier), k='multitasking', enable_events=True),
                       sg.T("Number of simultaneous threads. - More is not always better! - Start with one.")],
                      [sg.T("Try adding a thread if you see particles slow down when you quickly swish the mouse diagonally over the whole screen, or in big circles.")],
                      [sg.Checkbox('Interpolate mouse movement', default=True, k='interpolateMouseMovement', enable_events=True)],
                      [sg.T('Exp.: Draw some particles between current position of the cursor and that of last frame. (Interpolation should have almost no effect on performance)', pad=(10, (0, 15)))],
                      [sg.Spin([i for i in range(1, 100)], initial_value=1, font=(globalFont, 16 + globalFontSizeModifier), k='numParticles', enable_events=True), sg.T('Number of particles to spawn per frame'),
                      sg.Spin([i for i in range(1, 11)], initial_value=2, font=(globalFont, 16 + globalFontSizeModifier), k='particleSize', enable_events=True), sg.T('Particle size in pixel')],

                      [sg.Frame('Offsets', [[sg.Checkbox('Add offset to the position of the particle origin', default=False, k='useOffset', enable_events=True),
                       sg.Checkbox('Mark position of particle origin. Use for offset tuning', default=False, k='markPosition', disabled=False, enable_events=True)],
                      [sg.T('X='), sg.Spin([i for i in range(-99, 99)], initial_value=20, font=(globalFont, 16 + globalFontSizeModifier), k='offsetX', disabled=False, enable_events=True),
                       sg.T('Y='), sg.Spin([i for i in range(-99, 99)], initial_value=10, font=(globalFont, 16 + globalFontSizeModifier), k='offsetY', disabled=False, enable_events=True),
                       sg.T('Offset in pixel. (0, 0=tip of cursor)')]],)],

                      [sg.Spin([i for i in range(1, 1000)], initial_value = 20, font = (globalFont, 16 + globalFontSizeModifier), k = 'softClampVelocityVector', enable_events = True),
                       sg.T('Soft LIMIT on velocity of particle vector. Allows exceeding. Is used as factor on velocity.')],
                      [sg.Spin([i for i in range(0, 100)], initial_value=12, font=(globalFont, 16 + globalFontSizeModifier), k='ageBrightnessNoise', enable_events=True),
                       sg.T('Adds random noise (twinkling) to brightness: brightness = random(+|-value). Deactivate with 0'),
                       sg.T('                                     Scroll down      |')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value=60, font=(globalFont, 16 + globalFontSizeModifier), k='particleAge', enable_events=True), sg.T('Particle age (in frames) OR modifier for time until brightness < 7 (death)'),
                       sg.T('                                                                                           v')],
                      [sg.T('Increase slider to >1.00 to slow down brightness decline. Faster dimming leads to earlier death. (Exponential) Deactivate with 0.', pad=(10, (15, 0)))],
                      [sg.Slider(range=(0.00, 29.95), default_value=5.300, font=(globalFont, 14 + globalFontSizeModifier), resolution=.05, size=(73.5, 10), pad=(5, (0, 25)),
                                 orientation='horizontal', k='ageBrightnessMod', enable_events=True)],
                      [sg.HorizontalSeparator()],
                      [sg.HorizontalSeparator()],

                      [sg.T('Explanation of how all this behaves: ', font = (globalFont, 13 + globalFontSizeModifier), pad = (10, (25, 0)))],
                      [sg.T('Every particle has a vector. Here, a vector is a motion with velocity(N) in direction(X,Y) from position(X,Y).', font = (globalFont, 11 + globalFontSizeModifier), pad = (10, (0, 10)))],
                      [sg.T('There are mainly two different ways to affect the vector: By manipulating velocity or direction either directly or by adding a second vector.', font = (globalFont, 8 + globalFontSizeModifier), pad = (10, (2, 0)))],
                      [sg.T("You can set that the vector and amount of created particles to be influenced by mouse movement or not. This is done in the Dynamic tab.", font = (globalFont, 8 + globalFontSizeModifier), pad = (10, (2, 0)))],
                      [sg.T('A vector can be manipulated once at time of particle genesis or every frame. See indicator in titles.', font = (globalFont, 8 + globalFontSizeModifier), pad = (10, (2, 0)))],
                      [sg.T('A second vector that will be added to the inherent first one can be manipulated with some sliders.', font = (globalFont, 8 + globalFontSizeModifier), pad = (10, (2, 0)))],
                      [sg.HorizontalSeparator()],

                      [sg.T("(Any Vector) ONCE/PER FRAME: Add degrees of rotation into any vector.", font = (globalFont, 15 + globalFontSizeModifier),  pad = (10, (15, 0)))],
                      [sg.T("--Deactivate with 0 or uncheck all boxes--", pad = (10, (10, 0)))],
                      [sg.T("When added to particle vector, particles will turn around with N amount of strength.", pad = (10, (0, 0)))],
                      [sg.T("When added to second vector, particles can spiral in one direction, making the rotation independent of its initial direction.", pad = (10, (0, 0)))],
                      [sg.T("If no effect is visible, reduce the amount or increase velocity. Their turn radius is too small.", pad = (10, (0, 0)))],
                      [sg.Checkbox('Add again every frame (cumulative)', default = False, k = 'cumulativeVectorRotation', enable_events = True),
                       sg.Checkbox('ADD to particle vector', default = False, k = 'particleVectorRotation', enable_events = True),
                       sg.Checkbox('ADD to second vector', default = True, k = 'secondVectorRotation', enable_events = True),
                       sg.Checkbox('Randomize rotation for particles', default = True, k = 'randomRotation', enable_events = True)],
                      [sg.Slider(range = (0.0, 100.0), default_value = 1, font = (globalFont, 14 + globalFontSizeModifier), resolution = 0.1, size = (73.5, 10),
                                 orientation = 'horizontal', disabled = False, k = 'vectorRotation', enable_events = True, trough_color = sg.theme_slider_color())],
                      [sg.HorizontalSeparator()],
                      [sg.HorizontalSeparator()],

                      [sg.T('NOTE: These next sliders will be influenced by sliders from the "dynamic" tab.', font = (globalFont, 15 + globalFontSizeModifier), pad = (100, (15, 0)))],
                      [sg.HorizontalSeparator()],
                      [sg.T('(Second Vector) PER FRAME: INITIALIZE and ADD with these values. --Deactivate with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad=(10, (10, 0)))],
                      [sg.T('-- IGNORED if last slider is not at position 0 and without "ADD" checkbox checked --', font = (globalFont, 13 + globalFontSizeModifier), pad = (10, (0, 0)))],
                      [sg.T('Can simulate gravity or wind force. (i.e. For gravity: X=0.0, Y=0.1) - Results in a constant motion downwards motion with a speed of 0.1 to all particles.', pad=(10, (10, 0)))],
                      [sg.T('( vector2(X/Y) = vector2(X/Y) + VALUE(X/Y) )', pad=(10, (0, 0)))],
                      [sg.Slider(range=(-3.00, 3.00), default_value=0.00, font=(globalFont, 14 + globalFontSizeModifier), resolution=.01, size=(36.5, 10),
                                 orientation='horizontal', k="manualSecondVector_X", enable_events=True),
                       sg.Slider(range=(-3.00, 3.00), default_value=0.00, font=(globalFont, 14 + globalFontSizeModifier), resolution=.01, size=(36.5, 10),
                                 orientation='horizontal', k="manualSecondVector_Y", enable_events=True)],
                      [sg.T('X', pad = (216, (0, 0)), font=(globalFont, 14 + globalFontSizeModifier)),
                       sg.T('Y', pad = (218, (0, 0)), font=(globalFont, 14 + globalFontSizeModifier))],

                      [sg.T('(Second Vector) ONCE: RESET with random values. (SMOOTH) --Deactivate with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)))],
                      [sg.T('-- IGNORED if last slider is not at position 0 and without "ADD" checkbox checked --', font = (globalFont, 13 + globalFontSizeModifier), pad = (10, (0, 0)))],
                      [sg.T('Once at time of particle generation. Spreads them apart.', pad = (10, (10, 0)))],
                      [sg.T('( vector2(X/Y) = random_between(+-VALUE) )', pad = (10, (0, 0)))],
                      [sg.Slider(range = (0.00, 1.00), default_value = 0.1, font = (globalFont, 14 + globalFontSizeModifier), resolution = 0.001, size = (73.5, 10),
                                 orientation = 'horizontal', disabled = False, k = 'randomSecondVector', enable_events = True, trough_color = sg.theme_slider_color())],

                      [sg.T('(Second Vector) PER FRAME: RESET with - or ADD random values. (CHAOTIC) --Deactivate with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad=(10, (15, 0)))],
                      [sg.T('-- OVERRIDES last two sliders if not at position 0 and without "ADD" checkbox checked--', font = (globalFont, 13 + globalFontSizeModifier), pad = (10, (0, 0)))],
                      [sg.T('Particles turn in other direction every frame. Makes it look like a angry swarm of bees or brownian motion.', pad = (10, (10, 0)))],
                      [sg.T('( vector2(X/Y) = random_between(+-VALUE) )', pad = (10, (0, 0)))],
                      [sg.Checkbox('ADD to second vector instead replace. Use to add chaotic movement to other motion. By nature cumulative.', default = False, k = 'addChaosSecondVector',
                                   enable_events = True, pad = (5, (0, 0)))],
                      [sg.Checkbox('LIMITS second vector velocity to "some dynamic value". Useful when ADD funktion is enabled. Off if 0.',
                                   default = False, k = 'clampVelocitySecondVector', enable_events = True, pad = (5, (0, 0)))],
                      [sg.Slider(range=(0.00, 2.0), default_value= 0.2, font=(globalFont, 14 + globalFontSizeModifier), resolution=0.001, size=(73.5, 10),
                                 orientation='horizontal', disabled=False, k='chaoticSecondVector', enable_events=True, trough_color=sg.theme_slider_color())],
                      [sg.T('', pad = (10, (0, 0)))],
                      [sg.T('', pad = (10, (0, 0)))],
                      ]

    dynamic_layout = [[sg.Checkbox('Enable dynamic behavior (i.e. mouseSpeed dependant particle creation)', font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)), default = True, k = 'dynamic', enable_events = True)],
                      [sg.T('Exp.: No particles are created when mouse is held still. When moved, the faster the movement, the more particles are created.', pad = (10, (0, 15)))],
                      [sg.Frame('Number of particles:',
                                [[sg.Spin([i for i in range(2, 100)], initial_value = 4, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelNumParticles_1', disabled = False, enable_events = True), sg.T('Level 1 '),
                                  sg.Spin([i for i in range(2, 200)], initial_value = 8, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelNumParticles_2', disabled = False, enable_events = True), sg.T('Level 2 '),
                                  sg.Spin([i for i in range(2, 300)], initial_value = 16, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelNumParticles_3', disabled = False, enable_events = True), sg.T('Level 3'),
                                  sg.Spin([i for i in range(2, 400)], initial_value = 32, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelNumParticles_4', disabled = False, enable_events = True),
                                  sg.T('Level 4 - spawn this many particles per frame ...')]], )],
                      [sg.Frame('At mouse velocity in pixel per frame:',
                                [[sg.Spin([i for i in range(1, 1000)], initial_value = 15, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelVelocity_1', disabled = False, enable_events = True), sg.T('Level 1'),
                                  sg.Spin([i for i in range(1, 1000)], initial_value = 30, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelVelocity_2', disabled = False, enable_events = True), sg.T('Level 2'),
                                  sg.Spin([i for i in range(1, 1000)], initial_value = 65, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelVelocity_3', disabled = False, enable_events = True), sg.T('Level 3 '),
                                  sg.Spin([i for i in range(1, 1000)], initial_value = 130, font = (globalFont, 16 + globalFontSizeModifier), k = 'levelVelocity_4', disabled = False, enable_events = True),
                                  sg.T('Level 4 - if mouse is moving this fast in pixels per frame ...')]], )],
                      [sg.T('Exp.: Sets the number of particles created per frame at the specified speed of mouse movement. (Below "Level 1" is defined in the General tab.', pad = (10, (0, 15)))],
                      [sg.HorizontalSeparator()],
                      [sg.HorizontalSeparator()],

                      [sg.T('(Particle Vector) ONCE: Add random velocity to vector. --Only dynamic OFF // Deactivate with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)))],
                      [sg.T('Kick particles apart in RANDOM directions right after creation.', pad = (10, (10, 0)))],
                      [sg.T('( vector(X/Y) = vector(X/Y) + random_between(+-VALUE)', pad = (10, (0, 0)))],
                      [sg.Slider(range = (0.0, 100.0), default_value = 10, font = (globalFont, 14 + globalFontSizeModifier), resolution = 0.5, size = (73.5, 10),
                                 orientation = 'horizontal', disabled = False, k = 'addRandomParticleVector', enable_events = True, trough_color = sg.theme_slider_color())],

                      [sg.Checkbox('(Particle Vector) ONCE: Influence vector randomly by how fast you have moved the mouse.', default = False,
                                   k = 'addRandomMouseInfluenceVector', disabled = False, enable_events = True, font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)))],
                      [sg.T("( vector(X/Y) = vector(X/Y) + random_between(+-mouseSpeed) )", pad = (10, (0, 0)))],
                      [sg.T("Control strength of influence. (Random velocity in random direction) --Only dynamic ON--", font = (globalFont, 14 + globalFontSizeModifier), pad = (10, (5, 0)))],
                      [sg.T("Kicks particles apart without much regards to direction.", pad = (10, (0, 0)))],
                      [sg.T("( vector(X/Y) = vector(X/Y) + random_between(+-mouseSpeed * VALUE) )", pad = (10, (0, 0)))],
                      [sg.Slider(range = (0.0, 2.0), default_value = 0.160, font = (globalFont, 14 + globalFontSizeModifier), resolution = .001, size = (73.5, 10),
                                 orientation = 'horizontal', k = 'strengthMouseInfluenceVector', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                      [sg.HorizontalSeparator()],

                      [sg.T('(Particle Vector) ONCE: Multiply velocity by VALUE. --Deactivate Vector with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)))],
                      [sg.T('Push particles apart, but keep direction. Applied once at particle genesis, at vector conversion into velocity. Equal to mouse movement at 1.', pad = (10, (10, 0)))],
                      [sg.T('( velocity * VALUE )', pad = (10, (0, 0)))],
                      [sg.Slider(range = (0.0, 1.0), default_value = 1.00, font = (globalFont, 14 + globalFontSizeModifier), resolution = .001 , size = (73.5, 10),
                                 orientation = 'horizontal', k = 'velocityFactorVector', enable_events = True)],

                      [sg.T('(Particle Vector) PER FRAME: Multiply velocity by VALUE. --Deactivate with 0--', font = (globalFont, 15 + globalFontSizeModifier), pad = (10, (15, 0)))],
                      [sg.T('Can simulate drag or drive: Like air does to you in windy weather. Every frame velocity is multiplied by this value.', pad = (10, (10, 0)))],
                      [sg.T('If it is bigger than 1.0 then particles will speed up instead. If it is 0, all particles stand still.', pad=(10, (0, 0)))],
                      [sg.T('( velocity * VALUE )', pad=(10, (0, 0)))],
                      [sg.Slider(range = (0.5, 1.5), default_value = 0.990, font = (globalFont, 14 + globalFontSizeModifier), resolution = .001, size = (73.5, 10),
                                 orientation = 'horizontal', k = 'drag', enable_events = True)]
                      ]

    color_layout = [[sg.Input(visible=False, enable_events=True, k='particleColor'), sg.ColorChooserButton('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor),
                              size=(25, 2), font=(globalFont, 16+ globalFontSizeModifier), k='color picker button'),
                    sg.Frame('', border_width = 0, layout =[[sg.T('Hue slider', expand_x = True, justification='center', font=(globalFont, 16 + globalFontSizeModifier))],
                                                            [sg.Slider(range=(0.00, 359.88), default_value=particleColorHue, font=(globalFont, 14 + globalFontSizeModifier), resolution=0.01, size=(45, 10),
                                                                       orientation='horizontal', k='particleColorHue', disabled=False, enable_events=True)]],)],  # , trough_color=particleColor
                    [sg.Radio('Use color picker.', 'colorSwitch', default=False, k=None, enable_events=True)],
                    [sg.Radio('Randomize particle color. (Control bightness with color picker)', 'colorSwitch', default=False, k='particleColorRandom', enable_events=True),
                     sg.Radio('Use color under mouse. (Very slow. Use with one thread only)', 'colorSwitch',  default=False, k='useColorUnderMouse', enable_events=True)],
                    [sg.Checkbox('Rollover from hue = 360 to 0 or the other way around. (Depending on if positive or negative aging is used.', default=False, k='colorRollover', enable_events=True)],

                    [sg.HorizontalSeparator()],
                    [sg.Spin([i for i in range(0, 200)], initial_value=50, font=(globalFont, 16 + globalFontSizeModifier), k='ageColorNoise', enable_events=True),
                    sg.Frame('', border_width = 0, layout =[[sg.T('Add randomness to hue. (inject noise) A number between range +-value is added at time of creation.', pad=(0, (0, 0)))],
                                                            [sg.T('Use to combat too uniform looking particle color change. Deactivate with 0.', pad=(0, (0, 0))), ]])],
                    [sg.T('Skew this number with a bias more towards positive or negative values: 0 = only negative noise | 0.5 = balanced | 1.0 = only positive noise', pad=(10, (15, 0)))],
                    [sg.Slider(range=(0.00, 1.00), default_value=0.42, font=(globalFont, 14 + globalFontSizeModifier), resolution=.01, size=(73.5, 10),
                               orientation='horizontal', k='ageColorNoiseMod', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox('Change hue over time. (hue - age * VALUE)', font = (globalFont, 15 + globalFontSizeModifier), default=True, k='ageColor', enable_events=True)],
                    [sg.T('Hue aging speed factor. Negative values decrease hue over time, positive increase it. (i.e. if Cyan, then Neg: towards green, Pos: towards blue)', pad=(10, (0, 0)))],
                    [sg.Slider(range=(-19.99, 19.99), default_value=-5.50, font=(globalFont, 14 + globalFontSizeModifier), resolution=.10, size=(73.5, 10),
                               orientation='horizontal', k='ageColorSpeed', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],
                    [sg.T('Fine adjustment: ', font=(globalFont, 14 + globalFontSizeModifier)),
                     sg.Slider(range=(ageColorSpeed-1.00, ageColorSpeed+1.00), default_value=ageColorSpeed, font=(globalFont, 14 + globalFontSizeModifier), resolution=.005, size=(56.9, 10),
                               orientation='horizontal', k='ageColorSpeedFine', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox('Linear aging instead  (hue - time)', default = True, k = 'ageLinear', enable_events = True)],
                    [sg.T('Speed of linear aging')],
                    [sg.Slider(range = (-30.0, 30.0), default_value = .5, font = (globalFont, 14 + globalFontSizeModifier), resolution = .1, size = (73.5, 10),
                               orientation = 'horizontal', k = 'ageLinearSpeed', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],

                    [sg.Checkbox('Age on a concave downward curve: At the start slower, but then increasingly faster change of hue value.', default=True, k='ageColorSlope', disabled=False, enable_events=True)],
                    [sg.T('(i.e. Longer stay of earlier colors. May be "logarithmic" aging.)', pad=(10, (0, 0)))],
                    [sg.T('Increase concavity of the downward slope that represents hue over time. (Think: https://i.stack.imgur.com/bGi9k.jpg)', pad=(10, (0, 0)))],
                    [sg.Slider(range=(-2.00, 2.00), default_value=0.420, font=(globalFont, 14 + globalFontSizeModifier), resolution=.01, size=(73.5, 10),
                               orientation='horizontal', k='ageColorSlopeConcavity', disabled=False, enable_events=True, trough_color=sg.theme_slider_color())]
                    ]

    other_layout = [[sg.Text("Anything else one could find interesting to adhere to your mouse cursor!", font=(globalFont, 16 + globalFontSizeModifier))],
                    [sg.Text('Notice: FPS and the origin-offset from the "General"-tab are also used here:'),
                     sg.Checkbox('Add offset to the position of the upper-right corner of these stupid things', default=False, k='useOffset2', enable_events=True)],
                    [sg.T('X '), sg.Spin([i for i in range(-99, 99)], initial_value=20, font=(globalFont, 16 + globalFontSizeModifier), k='offsetX2', disabled=False, enable_events=True),
                     sg.T('Y '), sg.Spin([i for i in range(-99, 99)], initial_value=10, font=(globalFont, 16 + globalFontSizeModifier), k='offsetY2', disabled=False, enable_events=True),
                     sg.T('Offset in pixel. (0, 0=tip of cursor)')],

                    [sg.HorizontalSeparator()],
                    [sg.Input(visible=False, enable_events=True, k='fontColor'),
                     sg.ColorChooserButton('Font color picker: %s' % fontColor, button_color=("#010101", fontColor), size=(25, 1), font=(globalFont, 16 + globalFontSizeModifier), k='font color picker button'),
                    sg.Input(visible=False, enable_events=True, k='outlineColor'),
                     sg.ColorChooserButton('Outline color picker: %s' % outlineColor, button_color=("#808080", outlineColor), size=(25, 1), font=(globalFont, 16 + globalFontSizeModifier), k='outline color picker button')],
                    [sg.Spin([i for i in range(1, 100)], initial_value=10, font=(globalFont, 16 + globalFontSizeModifier), k='fontSize', enable_events=True),
                     sg.T('Font size in pt.'),
                    sg.Spin([i for i in range(0, 10)], initial_value=1, font=(globalFont, 16 + globalFontSizeModifier), k='outlineThickness', enable_events=True),
                     sg.T('Thickness of the outline in pixel. Use "0" to deactivate the outline')],
                    [sg.Checkbox("Enable antialiasing for the font. (''Pixel-smearing'' of the edges to reduce blockiness. Can be blurry)", default=False, k='fontAntialiasing', disabled=False, enable_events=True)],
                    [sg.HorizontalSeparator()],
                    [sg.T('Untick all in order to activate the sparkly particles again.', font=(globalFont, 16 + globalFontSizeModifier))],
                    [sg.Checkbox('Show RGB value of the color of the pixel under the cursor. Also draws a 40x40 square in that color.', default=False, k='showColor', disabled=False, enable_events=True)],
                    [sg.Checkbox('Show complementary color instead', default=False, k='complementaryColor', disabled=False, enable_events=True)],
                    [sg.Radio('rgb complement', 'compSwitch', default=True, k='rgbComplement', disabled=False, enable_events=True),
                     sg.Radio('ryb (artist) complement (Follows: "red–green, yellow–purple, and blue–orange" but seems inaccurate inbetween', 'compSwitch', k='artistComplement', disabled=False, enable_events=True)],
                    [sg.Checkbox('Clock: Show a text-based clock on the right the cursor.', default=False, k='showClock', disabled=False, enable_events=True)],
                    [sg.Checkbox('CPU-usage: Show in percent beside the cursor.', default=False, k='showCPU', disabled=False, enable_events=True)],
                    [sg.Checkbox('RAM-usage: Show in percent alongside the cursor', default=False, k='showRAM', disabled=False, enable_events=True)],

                    [sg.HorizontalSeparator()],
                    [sg.Checkbox("Draw an image somewhere around the cursor (gifs don't move)", default=False, k='showImage', disabled=False, enable_events=True)],
                    [sg.Text('Choose Image'), sg.InputText(size=(65, 1), k='imagePath'),
                     sg.FileBrowse('Browse', size=(10, 1), file_types=file_types, enable_events=True)],
                    [sg.T('(Only ".png", ".jpg", ".jpeg", ".tiff" ".gif" or ".bmp" supported.)', font=(globalFont, 10 + globalFontSizeModifier))],
                    [sg.Image(data=get_img_data(imagePath, first=True), k='image')]
                    ]

    # preview_layout = [[sg.Canvas(size=(120, 33), k='graph')],
    #                   [sg.T('scatter plot with color map that changes?? X is time, Y is brightness (to death) and the color is color, of course?')],
    #                   [sg.T('')]]

    console_layout = [[sg.Output(size=(120, 33), font=(globalFont, 10 + globalFontSizeModifier))],
                      [sg.T("Please don't look under the rug.")]]

    tabs_layout = [[sg.TabGroup([[sg.Tab('General particle settings', general_layout),
                                  sg.Tab('Particle dynamics', dynamic_layout),
                                  sg.Tab('Color settings', color_layout),
                                  sg.Tab('Other things stuck to your mouse', other_layout),
                                  #sg.Tab('Preview', preview_layout),
                                  sg.Tab('Console output', console_layout)]])]]

    layout = [[sg.T('ShitStuckToYourMouse', size=(74, 1), justification='center', font=(globalFont, 16 + globalFontSizeModifier), relief=sg.RELIEF_RIDGE)],
              [sg.Column(tabs_layout, scrollable=True, vertical_scroll_only=True, size=(900, 600))],
              [sg.Button('Save and Run', k='Save-n-Run', enable_events=True), sg.T('  '),
               sg.Button('Save', k='Save', enable_events=True), sg.T('  '),
               sg.Button('Close child process', k='Close', enable_events=True), sg.T('  '),
               sg.Button('Reset to defaults', k='Reset', enable_events=True)],
              [sg.Button('Exit', k='Exit', enable_events=True),
               #sg.Button('Hide Window', k='Hide', enable_events=True),
               sg.T('Press "F5" to Save and Run or "Esc" to Close')]]

    return sg.Window('ShitStuckToYourMouse configuration', layout, icon=poopImage, finalize=True, enable_close_attempted_event=True)

# import re  # forgot what that was for
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
    global config, particleColor, particleColorHue, fontColor, outlineColor, ageColorSpeed, imagePath, globalFont, globalFontSizeModifier, pid, proc, otherproc
    #sg.theme('Dark')  # redundant
    globalFont = "Segoe UI"  # default "Segoe UI"
    globalFontSizeModifier = 0
    sg.set_options(font=(globalFont, 10 + globalFontSizeModifier))  # global font
    #menu = ["", ["Show Window", "Hide Window", "---", "Exit"]]  # Tray-icon context-menu
    window = make_window('darkgrey15')  # Good one: Dark, darkgrey1, -2, -11, -13, -15, darkbrown1
    window.bind('<F5>', 'F5 pressed')
    window.bind('<Escape>', 'Escape pressed')
    #tray = SystemTray(menu, single_click_events=False, window=window, tooltip="ShitStuckToYourMouse", icon=resource_path(".\poop.ico"))
    print(sg.get_versions())
    proc = []  # Initiate variable for check if subprocess.Popen == True
    otherProc = False
    pid = []
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
    values['particleColorHue'] = particleColorHue
    window['particleColorHue'].update(values['particleColorHue'])

    try:
        while True:
            event, values = window.read(timeout=1000)  # value['particleColor'] and the other revert here after being set twice?
            #colorHEX = ''
            #colorHSV = ''
            particleColor = values['particleColor']
            particleColorHue = values['particleColorHue']
            fontColor = values['fontColor']
            outlineColor = values['outlineColor']
            imagePath = values['imagePath']

            if event in (None, 'Exit'):
                updateConfig(values)
                kill_all()
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
                window['colorRollover'].update(disabled=True)
                window['ageColorSpeed'].update(disabled=True)
                window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                window['ageColorSpeedFine'].update(disabled=True)
                window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_background_color())
                window['ageLinear'].update(disabled=True)
                window['ageLinearSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                window['ageColorSlope'].update(disabled=True)
                window['ageColorSlopeConcavity'].update(disabled=True)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_background_color())
            else:
                window['colorRollover'].update(disabled=False)
                window['ageColorSpeed'].update(disabled=False)
                window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_slider_color())
                window['ageColorSpeedFine'].update(disabled=False)
                window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_slider_color())
                window['ageLinear'].update(disabled=False)
                window['ageLinearSpeed'].Widget.config(troughcolor=sg.theme_slider_color())
                window['ageColorSlope'].update(disabled=False)
                window['ageColorSlopeConcavity'].update(disabled=False)
                window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_slider_color())
                if values['ageLinear']:
                    window['ageColorSpeed'].update(disabled=True)
                    window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSpeedFine'].update(disabled=True)
                    window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSlope'].update(disabled=True)
                    window['ageColorSlopeConcavity'].update(disabled=True)
                    window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_background_color())
                elif values['ageColorSlope']:
                    window['ageColorSpeed'].update(disabled=True)
                    window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSpeedFine'].update(disabled=True)
                    window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageLinear'].update(disabled=True)
                    window['ageLinearSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSlope'].update(disabled=False)
                    window['ageColorSlopeConcavity'].update(disabled=False)
                    window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_slider_color())
                else:
                    window['ageColorSpeed'].update(disabled=False)
                    window['ageColorSpeed'].Widget.config(troughcolor=sg.theme_slider_color())
                    window['ageColorSpeedFine'].update(disabled=False)
                    window['ageColorSpeedFine'].Widget.config(troughcolor=sg.theme_slider_color())
                    window['ageLinear'].update(disabled=False)
                    window['ageLinearSpeed'].Widget.config(troughcolor=sg.theme_background_color())
                    window['ageColorSlope'].update(disabled=False)
                    window['ageColorSlopeConcavity'].update(disabled=False)
                    window['ageColorSlopeConcavity'].Widget.config(troughcolor=sg.theme_background_color())

            if values['dynamic']:
                window['addRandomParticleVector'].update(disabled = True)
                window['addRandomParticleVector'].Widget.config(troughcolor=sg.theme_background_color())
                window['addRandomMouseInfluenceVector'].update(disabled=False)
                if values['addRandomMouseInfluenceVector']:
                    window['strengthMouseInfluenceVector'].update(disabled=False)
                    window['strengthMouseInfluenceVector'].Widget.config(troughcolor=sg.theme_slider_color())
                else:
                    window['strengthMouseInfluenceVector'].update(disabled=True)
                    window['strengthMouseInfluenceVector'].Widget.config(troughcolor=sg.theme_background_color())
                window['levelVelocity_1'].update(disabled=False)
                window['levelVelocity_2'].update(disabled=False)
                window['levelVelocity_3'].update(disabled=False)
                window['levelVelocity_4'].update(disabled=False)
                window['levelNumParticles_1'].update(disabled=False)
                window['levelNumParticles_2'].update(disabled=False)
                window['levelNumParticles_3'].update(disabled=False)
                window['levelNumParticles_4'].update(disabled=False)
            else:
                window['addRandomParticleVector'].update(disabled=False)
                window['addRandomParticleVector'].Widget.config(troughcolor=sg.theme_slider_color())
                window['addRandomMouseInfluenceVector'].update(disabled=True)
                window['strengthMouseInfluenceVector'].update(disabled=True)
                window['strengthMouseInfluenceVector'].Widget.config(troughcolor=sg.theme_background_color())
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

            # if event == tray.key:
            #     #print(f"System Tray Event = ", values[event])  # create key-error
            #     event = values[event]

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
                                     auto_close_duration=3, non_blocking=True, font=(globalFont, 26 + globalFontSizeModifier), no_titlebar=True, keep_on_top=True)
                    doesImageFileExist = False
                    print('Error: %s does not exist' % imagePath)
            #----------------------

            if event in (None, 'Reset'):
                answer = sg.popup_yes_no('Reset all settings to defaults?')
                if answer == 'Yes' or answer == 'yes':
                    kill_all()
                    setDefaults()
                    getVariablesFromConfig(window)
                    event, values = window.read(timeout=1250)
                    values['particleColor'] = config.get("SPARKLES", "particleColor")
                    particleColor = values['particleColor']
                    window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                    values['particleColorHue'] = float(config.get("SPARKLES", "particleColorHue"))
                    particleColorHue = values['particleColorHue']
                    #window['particleColorHue'].update(trough_color=particleColor)  # Does not work at all
                    window['particleColorHue'].update(values['particleColorHue'])
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
                #values['addRandomParticleVector'] = int(values['addRandomParticleVector'])  # because slider returns FLOAT, even if "(range=(0, 100),  resolution=1)". GRRR
                if particleColor == "None" or values['particleColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = particleColor
                if particleColorHue == "None" or values['particleColorHue'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    particleColorHue = float(config.get("SPARKLES", "particleColorHue"))  # Get last saved values
                    values['particleColorHue'] = particleColorHue
                if fontColor == "None" or values['fontColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("SPARKLES", "fontColor")  # Get last saved values
                    values['fontColor'] = fontColor
                if outlineColor == "None" or values['outlineColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    outlineColor = config.get("SPARKLES", "outlineColor")  # Get last saved values
                    values['outlineColor'] = outlineColor
                updateConfig(values)
                print('All values saved to config.ini')
                event, values = window.read(timeout=1000)
                values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                values['particleColorHue'] = float(config.get("SPARKLES", "particleColorHue"))
                particleColorHue = values['particleColorHue']
                #window['particleColorHue'].update(trough_color=particleColor)  # Does not work at all
                window['particleColorHue'].update(values['particleColorHue'])
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
                                         auto_close_duration=3, non_blocking=True, font=(globalFont, 26 + globalFontSizeModifier), no_titlebar=True, keep_on_top=True)
                        doesImageFileExist = False
                        print('Error: %s does not exist' % imagePath)
                    else:
                        window['image'].update(data=get_img_data(imagePath, first=True))
                        doesImageFileExist = True

                kill_all()

                if values['showColor'] or values['showClock'] or values['showCPU'] or values['showRAM'] or (values['showImage'] and doesImageFileExist):
                    if isCompiledToExe:
                        otherProc = Popen("other.exe", shell=False, creationflags=CREATE_NO_WINDOW, cwd=getcwd())
                    else:
                        otherProc = Popen("python other.pyw", shell=False, creationflags=CREATE_NO_WINDOW)
                    pid.append(otherProc.pid)
                    print('Subprocess Started')
                    print(otherProc, " with process id: ", pid)
                elif not values['showColor'] and not values['showClock'] and not values['showCPU'] and not values['showRAM'] and not values['showImage']:
                    sg.popup_no_wait('Starting ... ', text_color='#00ff00', button_type=5, auto_close=True,
                                        auto_close_duration=3, non_blocking=True, font=(globalFont, 26 + globalFontSizeModifier), no_titlebar=True, keep_on_top=True)
                    numberTasks = values['multitasking']
                    if values['multitasking'] > values['numParticles'] and not values['dynamic']:
                        numberTasks = values['numParticles']  # Don't create more threads than there are particles
                    i = 0
                    while i < numberTasks:
                        if isCompiledToExe:
                            returnValue = Popen("sparkles.exe", shell=False, creationflags=CREATE_NO_WINDOW, cwd=getcwd())
                            proc.append(returnValue)
                            if numberTasks > 1:
                                sleep(1.5)  # random errors occur when running multiple exe at the same time. Sleep does help
                        else:
                            returnValue = Popen("python sparkles.pyw", shell=False, creationflags=CREATE_NO_WINDOW)
                            proc.append(returnValue)
                        pid.append(returnValue.pid)
                        print('Subprocess Started')
                        print(proc[i], " with process id: ", pid[i])
                        i += 1
                else:
                    kill_all()
            # ---------------------

            elif event in (None, 'Save'):
                #values['addRandomParticleVector'] = int(values['addRandomParticleVector'])  # because slider returns FLOAT, even if "(range = (0, 100),  resolution = 1)". GRRR
                if particleColor == "None" or values['particleColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = particleColor
                if particleColorHue == "None" or values['particleColorHue'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    particleColorHue = float(config.get("SPARKLES", "particleColorHue"))  # Get last saved values
                    values['particleColorHue'] = particleColorHue
                if fontColor == "None" or values['fontColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("SPARKLES", "fontColor")  # Get last saved values
                    values['fontColor'] = fontColor
                if outlineColor == "None" or values['outlineColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    outlineColor = config.get("SPARKLES", "outlineColor")  # Get last saved values
                    values['outlineColor'] = outlineColor
                updateConfig(values)
                print('All values saved to config.ini')
                # print(values)
                event, values = window.read(timeout=1000)
                values['particleColor'] = config.get("SPARKLES", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                values['particleColorHue'] = float(config.get("SPARKLES", "particleColorHue"))
                particleColorHue = values['particleColorHue']
                #window['particleColorHue'].update(trough_color=particleColor)  # Does not work at all
                window['particleColorHue'].update(values['particleColorHue'])
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
                                         auto_close_duration=3, non_blocking=True, font=(globalFont, 26 + globalFontSizeModifier), no_titlebar=True, keep_on_top=True)
                        doesImageFileExist = False
                        print('Error: %s does not exist' % imagePath)
                    else:
                        window['image'].update(data=get_img_data(imagePath, first=True))
                        doesImageFileExist = True
            # ---------------------

            elif event in (None, 'Close') or event in (None, 'Escape pressed'):
                kill_all()

            # elif event in (None, 'Hide'):  # psgtray
            #     window.hide()
            #     tray.show_icon()

            elif event in (None, 'Exit'):
                #tray.hide_icon()
                kill_all()
                break

            # elif event in (None, sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            #     window.un_hide()
            #     window.bring_to_front()
            #
            # elif event in ("Show Window", sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            #     window.un_hide()
            #     window.bring_to_front()
            #
            elif event in ("Hide Window", sg.WIN_CLOSE_ATTEMPTED_EVENT):
                #tray.hide_icon()
                kill_all()
                break

            elif event in (None, 'particleColorHue'):
                if particleColorHue == "None" or values['particleColorHue'] == "None":  # maybe??
                    particleColorHue = float(config.get("SPARKLES", "particleColorHue"))  # Get last saved values
                    values['particleColorHue'] = particleColorHue
                #particleColorHue = values['particleColorHue']
                colorHSV = acrylic.Color(hex = particleColor).hsv  # get S and V values for next step
                colorHEX = acrylic.Color(hsv = [particleColorHue, colorHSV.s, colorHSV.v]).hex
                particleColor = colorHEX  # convert hsv to hex
                values['particleColor'] = colorHEX
                window['particleColor'].update(values['particleColor'])
                window['color picker button'].update(values['particleColor'])
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
                # background_color: str = None,
                # text_color: str = None,
                # trough_color: str = None
                #window['particleColorHue'].update(background_color = particleColor)  # Crash

            elif event in (None, 'particleColor'):  # Update color and text of the color-picker button
                if particleColor == "None" or values['particleColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    particleColor = config.get("SPARKLES", "particleColor")  # Get last saved values
                    values['particleColor'] = particleColor
                #particleColor = values['particleColor']
                colorHSV = acrylic.Color(hex = particleColor).hsv  # convert hex to hsv
                particleColorHue = colorHSV.h  # extract hue
                values['particleColorHue'] = particleColorHue
                window['particleColorHue'].update(values['particleColorHue'])  # , trough_color=particleColor
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))

            elif event in (None, 'fontColor'):  # Update color and text of the color-picker button
                if fontColor == "None" or values['fontColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
                    fontColor = config.get("OTHER", "fontColor")  # Get last saved values
                    values['fontColor'] = config.get("OTHER", "fontColor")
                fontColor = values['fontColor']
                event, values = window.read(timeout=1000)
                window['font color picker button'].update(('Font color picker: %s' % fontColor), button_color=("#010101", fontColor))

            elif event in (None, 'outlineColor'):  # Update color and text of the color-picker button
                if outlineColor == "None" or values['outlineColor'] == "None":  # check if no color was chosen in the popup. Happens when cancelled
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
        #tray.hide_icon()
        kill_all()

    kill_all()
    print("close window")
    #tray.hide_icon()  # sometimes doesn't have an effect and the icon stays ...
    #tray.close()  # optional but without a close, the icon may "linger" until moused over | still with it
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
    colorHSV = acrylic.Color(hex = particleColor).hsv  # convert hex to hsv
    particleColorHue = float(colorHSV.h)  # extract hue
    fontColor = str(config.get("OTHER", "fontColor"))
    outlineColor = str(config.get("OTHER", "outlineColor"))
    ageColorSpeed = float(config.get("SPARKLES", "ageColorSpeed"))
    imagePath = str(config.get("OTHER", "imagePath"))
    # I forgot why those five up there were necessary...

    layout = ""  # bullshit
    main()
#dead
