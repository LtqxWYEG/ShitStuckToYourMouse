
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
import os
import PySimpleGUI as sg
import signal
import subprocess


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


def setDefaults():  # Set Defaults and/or write ini-file if it doesn't exist
    global config
    config.read("defaults.ini")
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


# settings = dict(config.items('SETTINGS'))  # I don't understand this for now
def getVariablesFromConfig(window):
    window['particleSize'].update(int(config.get("SETTINGS", "particleSize")))
    window['particleAge'].update(int(config.get("SETTINGS", "particleAge")))
    window['ageBrightnessMod'].update(float(config.get("SETTINGS", "ageBrightnessMod")))
    window['ageBrightnessNoise'].update(int(config.get("SETTINGS", "ageBrightnessNoise")))
    window['velocityMod'].update(float(config.get("SETTINGS", "velocityMod")))
    window['velocityClamp'].update(int(config.get("SETTINGS", "velocityClamp")))
    string = config.getlistfloat("SETTINGS", "GRAVITY")
    window['GRAVITY_X'].update(string[0])
    window['GRAVITY_Y'].update(string[1])
    window['drag'].update(float(config.get("SETTINGS", "drag")))
    window['FPS'].update(int(config.get("SETTINGS", "FPS")))
    window['interpolateMouseMovement'].update(config.getboolean("SETTINGS", "interpolateMouseMovement"))
    window['particleColor'].update(str(config.get("SETTINGS", "particleColor")))
    window['particleColorRandom'].update(config.getboolean("SETTINGS", "particleColorRandom"))
    window['ageColor'].update(config.getboolean("SETTINGS", "ageColor"))
    window['ageColorSpeed'].update(float(config.get("SETTINGS", "ageColorSpeed")))
    window['ageColorSlope'].update(config.getboolean("SETTINGS", "ageColorSlope"))
    window['ageColorSlopeConcavity'].update(float(config.get("SETTINGS", "ageColorSlopeConcavity")))
    window['ageColorNoise'].update(int(config.get("SETTINGS", "ageColorNoise")))
    window['ageColorNoiseMod'].update(float(config.get("SETTINGS", "ageColorNoiseMod")))
    window['useOffset'].update(config.getboolean("SETTINGS", "useOffset"))
    window['offsetX'].update(int(config.get("SETTINGS", "offsetX")))
    window['offsetY'].update(int(config.get("SETTINGS", "offsetY")))
    window['markPosition'].update(config.getboolean("SETTINGS", "markPosition"))
    window['numParticles'].update(int(config.get("SETTINGS", "numParticles")))
    window['randomMod'].update(float(config.get("SETTINGS", "randomMod")))
    window['dynamic'].update(config.getboolean("SETTINGS", "dynamic"))
    window['randomModDynamic'].update(float(config.get("SETTINGS", "randomModDynamic")))
    string = config.getlistint("SETTINGS", "levelVelocity")
    window['levelVelocity_1'].update(string[0])
    window['levelVelocity_2'].update(string[1])
    window['levelVelocity_3'].update(string[2])
    window['levelVelocity_4'].update(string[3])
    string = config.getlistint("SETTINGS", "levelNumParticles")
    window['levelNumParticles_1'].update(string[0])
    window['levelNumParticles_2'].update(string[1])
    window['levelNumParticles_3'].update(string[2])
    window['levelNumParticles_4'].update(string[3])
    return window


def updateConfig(values):
    config.set("SETTINGS", "particleSize", str(values['particleSize']))
    config.set("SETTINGS", "particleAge", str(values['particleAge']))
    config.set("SETTINGS", "ageBrightnessMod", str(values['ageBrightnessMod']))
    config.set("SETTINGS", "ageBrightnessNoise", str(values['ageBrightnessNoise']))
    config.set("SETTINGS", "velocityMod", str(values['velocityMod']))
    config.set("SETTINGS", "velocityClamp", str(values['velocityClamp']))
    string = [str(values['GRAVITY_X']), ', ', str(values['GRAVITY_Y'])]
    GRAVITYStr = "".join(string)
    config.set("SETTINGS", "GRAVITY", GRAVITYStr)
    config.set("SETTINGS", "drag", str(values['drag']))
    config.set("SETTINGS", "FPS", str(values['FPS']))
    config.set("SETTINGS", "interpolateMouseMovement", str(values['interpolateMouseMovement']))
    config.set("SETTINGS", "particleColor", values['particleColor'])
    config.set("SETTINGS", "particleColorRandom", str(values['particleColorRandom']))
    config.set("SETTINGS", "ageColor", str(values['ageColor']))
    config.set("SETTINGS", "ageColorSpeed", str(values['ageColorSpeed']))
    config.set("SETTINGS", "ageColorSlope", str(values['ageColorSlope']))
    config.set("SETTINGS", "ageColorSlopeConcavity", str(values['ageColorSlopeConcavity']))
    config.set("SETTINGS", "ageColorNoise", str(values['ageColorNoise']))
    config.set("SETTINGS", "ageColorNoiseMod", str(values['ageColorNoiseMod']))
    config.set("SETTINGS", "useOffset", str(values['useOffset']))
    config.set("SETTINGS", "offsetX", str(values['offsetX']))
    config.set("SETTINGS", "offsetY", str(values['offsetY']))
    config.set("SETTINGS", "markPosition", str(values['markPosition']))
    config.set("SETTINGS", "numParticles", str(values['numParticles']))
    config.set("SETTINGS", "randomMod", str(values['randomMod']))
    config.set("SETTINGS", "dynamic", str(values['dynamic']))
    config.set("SETTINGS", "randomModDynamic", str(values['randomModDynamic']))
    string = [str(values['levelVelocity_1']), ', ', str(values['levelVelocity_2']), ', ', str(values['levelVelocity_3']), ', ', str(values['levelVelocity_4'])]
    levelVelocityStr = "".join(string)
    config.set("SETTINGS", "levelVelocity", levelVelocityStr)
    string = [str(values['levelNumParticles_1']), ', ', str(values['levelNumParticles_2']), ', ', str(values['levelNumParticles_3']), ', ', str(values['levelNumParticles_4'])]
    levelNumParticlesStr = "".join(string)
    config.set("SETTINGS", "levelNumParticles", levelNumParticlesStr)
    with open("config.ini", 'w') as configfile:
        config.write(configfile)


def make_window(theme):
    global particleColor
    variables = ''
    sg.theme(theme)

    general_layout = [[sg.Spin([i for i in range(1, 400)], initial_value = 60, font=("Segoe UI", 16), k = 'FPS', enable_events = True),
                       sg.T('Frames per second. Also affects number of particles as they are spawned per frame.')],
                      [sg.Checkbox('Interpolate mouse movement', default = True, k = 'interpolateMouseMovement', enable_events = True)],
                      [sg.T('Exp.: Draw some particles between current position of the cursor and that of last frame. (Interpolation should have almost no effect on performance)', pad = (10, (0, 15)))],
                      [sg.Checkbox('Add offset to the particle origin', default = False, k = 'useOffset', enable_events = True),
                       sg.Checkbox('Mark position of particle origin. Use for offset tuning', default = False, k = 'markPosition', disabled = False, enable_events = True)],
                      [sg.Spin([i for i in range(-99, 99)], initial_value = 0, font=("Segoe UI", 16), k = 'offsetX', disabled = False, enable_events = True), sg.T('X '),
                       sg.Spin([i for i in range(-99, 99)], initial_value = 0, font=("Segoe UI", 16), k = 'offsetY', disabled = False, enable_events = True),
                       sg.T('Offset in pixel. (0, 0 = tip of cursor)')],
                      [sg.Spin([i for i in range(1, 11)], initial_value = 2, font=("Segoe UI", 16), k = 'particleSize', enable_events = True), sg.T('Particle size in pixel * pixel')],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 1, font=("Segoe UI", 16), k = 'numParticles', enable_events = True), sg.T('Number of particles to spawn every frame')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 60, font=("Segoe UI", 16), k = 'particleAge', enable_events = True), sg.T('Particle age (in frames) OR modifier for time until brightness < 7 (death)')],
                      [sg.Slider(range=(0.001, 9.999), default_value = 5.300, font=("Segoe UI", 14), resolution = .001, size=(70, 15), orientation='horizontal', k = 'ageBrightnessMod', enable_events = True)],
                      [sg.T('Increase for slower brightness decline (concavity of downward slope)', pad = (10, (0, 15)))],
                      # [sg.HorizontalSeparator()],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 12, font=("Segoe UI", 16), k = 'ageBrightnessNoise', enable_events = True),
                       sg.T('Adds (twinkling) random noise to age/brightness: Between +-ageBrightnessNoise. 0 for no noise')],
                      [sg.Slider(range = (0.00, 99.99), default_value = 5.50, font=("Segoe UI", 14), resolution = .01, size = (70, 15), orientation = 'horizontal', disabled = False, k = 'randomMod', enable_events = True, trough_color = sg.theme_slider_color())],
                      [sg.T('Adds random motion to random direction to particles: mouseSpeed(xy) +- randomMod. Deactivate with 0. Deactivated if dynamic is True', pad = (10, (0, 15)))],
                      # [sg.HorizontalSeparator()],
                      [sg.Slider(range=(0.0, 9.9), default_value = 1.6, font=("Segoe UI", 14), resolution = .1, size=(70, 15), orientation='horizontal', k = 'velocityMod', enable_events = True)],
                      [sg.T('Lowers velocity added to particle based on mouse speed: mouseSpeed / velocityMod', pad = (10, (0, 15)))],
                      # [sg.HorizontalSeparator()],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 200, font=("Segoe UI", 16), k = 'velocityClamp', enable_events = True),
                       sg.T('Max. particle velocity')],
                      [sg.Slider(range=(-29.999, 29.999), default_value = 0.000, font=("Segoe UI", 14), resolution = .001, size=(34, 15), orientation='horizontal', k = 'GRAVITY_X', enable_events = True),
                       sg.Slider(range=(-29.999, 29.999), default_value = 0.025, font=("Segoe UI", 14), resolution = .001, size=(35, 15), orientation='horizontal', k = 'GRAVITY_Y', enable_events = True)],
                      [sg.T('x and y motion added to any particle each frame. (Motion vector with direction: 0.0, 0.1 = a motion of .1 in downwards direction.)', pad = (10, (0, 15)))],
                      # [sg.HorizontalSeparator()],
                      [sg.Slider(range = (0.000, 2.999), default_value = 0.850, font=("Segoe UI", 14), resolution = .001, size = (70, 15), orientation = 'horizontal', k = 'drag', enable_events = True)],
                      [sg.T('Particle drag, higher equals less drag: (drag * particle speed) per frame. --If >1 then particles speed up--', pad = (10, (0, 15)))],
                      # [sg.HorizontalSeparator()],
                      [sg.HorizontalSeparator()],
                      [sg.Button('Save and Run', k = 'Save1', enable_events = True), sg.T('  '), sg.Button('Close child process',
                                  k = 'Close1', enable_events = True), sg.T('  '), sg.Button('Reset to defaults', k = 'Reset1', enable_events = True)],
                      [sg.Button('Exit', k = 'Exit1', enable_events = True)]]

    color_layout = [[sg.Input(visible=False, enable_events=True, k='particleColor'), sg.ColorChooserButton('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor), size = (25, 2), font=("Segoe UI", 16), k = 'color picker button')],
                    [sg.T('Use "#ff0001" for full HSV color when ageColor is True. (Full 255 red plus 1 blue', pad = (10, (0, 15)))],
                    [sg.Checkbox('Randomly colored particles', default = False, k = 'particleColorRandom', enable_events = True)],
                    [sg.Checkbox('Change hue over time.', default = True, k = 'ageColor', enable_events = True)],
                    [sg.Slider(range = (0.00, 99.99), default_value = 5.50, font=("Segoe UI", 14), resolution = .01, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorSpeed', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                    [sg.T('Hue aging speed factor. Not used if ageColorSlope = True', pad = (10, (0, 15)))],
                    [sg.Checkbox('Age on a concave downward curve. For more pronounced pink and blue colors', default = True, k = 'ageColorSlope', disabled = False, enable_events = True)],
                    [sg.T('(Or whatever is highest hue value of particleColor)', pad = (10, (0, 15)))],
                    [sg.Slider(range = (0.000, 9.999), default_value = 0.420, font=("Segoe UI", 14), resolution = .001, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorSlopeConcavity', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                    [sg.T('Increase concavity of downward slope representing values over age. (Think: https://i.stack.imgur.com/bGi9k.jpg)', pad = (10, (0, 15)))],
                    [sg.Spin([i for i in range(1, 100)], initial_value = 12, font=("Segoe UI", 16), k = 'ageColorNoise', disabled = False, enable_events = True),
                     sg.T('Adds random noise to hue: Between +-ageColorNoise. 0 for no noise')],
                    [sg.Slider(range = (0.000, 1.000), default_value = 0.420, font=("Segoe UI", 14), resolution = .001, size = (70, 15),
                               orientation = 'horizontal', k = 'ageColorNoiseMod', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                    [sg.T('Shifts color noise weight to be more positive or negative: 0 = only positive noise, 0.5 = balanced, 1.0 = only negative noise, etc', pad = (10, (0, 15)))],
                    [sg.HorizontalSeparator()],
                    [sg.Button('Save and Run', k = 'Save2', enable_events = True), sg.T('  '), sg.Button('Close child process',
                                k = 'Close2', enable_events = True), sg.T('  '), sg.Button('Reset to defaults', k = 'Reset2', enable_events = True)],
                    [sg.Button('Exit', k = 'Exit2', enable_events = True)]]

    dynamic_layout = [[sg.Text('Dynamics settings')],
                      [sg.Checkbox('The faster the movement, the more particles and random motion will be added.', default = True, k = 'dynamic', enable_events = True)],
                      [sg.Slider(range = (0.00, 0.99), default_value = 0.05, font=("Segoe UI", 14), resolution = .01, size = (70, 15), orientation = 'horizontal', k = 'randomModDynamic', disabled = False, enable_events = True, trough_color = sg.theme_slider_color())],
                      [sg.T('Adds random motion to random direction to dynamic particles: +|-mouseSpeed(xy) * randomMod.', pad = (10, (0, 15)))],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 5, font=("Segoe UI", 16), k = 'levelNumParticles_1', disabled = False, enable_events = True), sg.T('Level 1 '),
                       sg.Spin([i for i in range(1, 100)], initial_value = 8, font=("Segoe UI", 16), k = 'levelNumParticles_2', disabled = False, enable_events = True), sg.T('Level 2 '),
                       sg.Spin([i for i in range(1, 100)], initial_value = 14, font=("Segoe UI", 16), k = 'levelNumParticles_3', disabled = False, enable_events = True), sg.T('Level 3'),
                       sg.Spin([i for i in range(1, 100)], initial_value = 20, font=("Segoe UI", 16), k = 'levelNumParticles_4', disabled = False, enable_events = True), sg.T('Level 4 - spawn this many particles ...')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 15, font=("Segoe UI", 16), k = 'levelVelocity_1', disabled = False, enable_events = True), sg.T('Level 1'),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 30, font=("Segoe UI", 16), k = 'levelVelocity_2', disabled = False, enable_events = True), sg.T('Level 2'),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 60, font=("Segoe UI", 16), k = 'levelVelocity_3', disabled = False, enable_events = True), sg.T('Level 3 '),
                       sg.Spin([i for i in range(1, 1000)], initial_value = 120, font=("Segoe UI", 16), k = 'levelVelocity_4', disabled = False, enable_events = True), sg.T('Level 4 - if mouse is moving this fast in pixels per frame ...')],
                      [sg.T('Number of particles at mouse velocities below "Level 1" are defined by the value in the General tab.')],
                      [sg.HorizontalSeparator()],
                      [sg.Button('Save and Run', k = 'Save3', enable_events = True), sg.T('  '), sg.Button('Close child process',
                                  k = 'Close3', enable_events = True), sg.T('  '), sg.Button('Reset to defaults', k = 'Reset3', enable_events = True)],
                      [sg.Button('Exit', k = 'Exit3', enable_events = True)]]

    graphing_layout = [[sg.Text("Anything you would use to graph will display here!")],
                       [sg.Graph((200, 200), (0, 0), (200, 200), background_color = "#123456", enable_events = True)],
                       [sg.Text("Current values of all variables:")],
                       [sg.Text(variables, k = 'inGUIConsole')],
                       [sg.HorizontalSeparator()],
                       [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '),
                        sg.Button('Close child process', k = 'Close', enable_events = True), sg.T('  '),
                        sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
                       [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    layout = [[sg.T('ShitStuckToYourMouse', size = (38, 1), justification = 'center',
                    font = ("Segoe UI", 16), relief = sg.RELIEF_RIDGE, enable_events = True)]]

    layout += [[sg.TabGroup([[sg.Tab('General settings', general_layout),
                              sg.Tab('Color settings', color_layout),
                              sg.Tab('Dynamics', dynamic_layout),
                              sg.Tab('Preview', graphing_layout)]])]]

    return sg.Window('ShitStuckToYourMouse configuration', layout, finalize=True)



def PopenNotice():
    sg.popup_auto_close('Starting ...')



def main(config):
    sg.theme('Dark')
    sg.set_options(font=("Segoe UI", 10))
    window = make_window('Dark')
    proc = False  # Initiate variable to check if subprocess.Popen == True
    getVariablesFromConfig(window)
    while True:
        global particleColor, variables
        event, values = window.read(timeout=250)
        particleColor = values['particleColor']
        if event in (None, 'Exit1') or event in (None, 'Exit2') or event in (None, 'Exit3'):
            if proc:
                proc.kill()
            break
        if not values['ageColor']:
            window['ageColorSpeed'].update(disabled = True)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorSlope'].update(disabled = True)
            window['ageColorSlopeConcavity'].update(disabled = True)
            window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorNoise'].update(disabled = True)
            window['ageColorNoiseMod'].update(disabled = True)
            window['ageColorNoiseMod'].Widget.config(troughcolor = sg.theme_background_color())
        else:
            window['ageColorSpeed'].update(disabled = False)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_slider_color())
            window['ageColorSlope'].update(disabled = False)
            window['ageColorSlopeConcavity'].update(disabled = False)
            window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_slider_color())
            window['ageColorNoise'].update(disabled = False)
            window['ageColorNoiseMod'].update(disabled = False)
            window['ageColorNoiseMod'].Widget.config(troughcolor = sg.theme_slider_color())
        if values['ageColorSlope']:
            window['ageColorSpeed'].update(disabled = True)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_background_color())
            window['ageColorSlopeConcavity'].update(disabled = False)
            window['ageColorSlopeConcavity'].Widget.config(troughcolor = sg.theme_slider_color())
        else:
            window['ageColorSpeed'].update(disabled = False)
            window['ageColorSpeed'].Widget.config(troughcolor = sg.theme_slider_color())
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
        else:
            window['offsetX'].update(disabled = True)
            window['offsetY'].update(disabled = True)
            window['markPosition'].update(disabled = True)
        #if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            #print('============ Event = ', event, ' ==============')
            #print('-------- Values Dictionary (key:value) --------')
            #print(values)
            #variables = values
            #window['inGUIConsole'].update(variables)
            #values['inGUIConsole'] = None
        if event in (None, 'Reset1') or event in (None, 'Reset2') or event in (None, 'Reset3'):
            answer = sg.popup_yes_no('Reset all settings to defaults?')
            if answer == 'Yes' or answer == 'yes':
                setDefaults()
                getVariablesFromConfig(window)
                values['particleColor'] = config.get("SETTINGS", "particleColor")
                particleColor = values['particleColor']
                window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
            else:
                continue
            print("[LOG] Reset to defaults...")
        elif event in (None, 'Save1') or event in (None, 'Save2') or event in (None, 'Save3'):
            print("[LOG] Save to config.ini and run programm...")
            updateConfig(values)
            if proc:
                proc.kill()
            sg.popup_no_wait('Starting ...', text_color = '#00ff00', button_type = 5, auto_close = True, auto_close_duration = 3, non_blocking = True, font = ("Segoe UI", 26), no_titlebar = True)
            proc = subprocess.Popen("py sparkles.py", shell = False, stdout = subprocess.PIPE, stdin = subprocess.PIPE, stderr = subprocess.PIPE, creationflags = subprocess.CREATE_NO_WINDOW)
        elif event in (None, 'Close1') or event in (None, 'Close2') or event in (None, 'Close3'):
            if proc:
                proc.kill()
                #subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))
                #subprocess.Popen("TASKKILL /F /IM ShitStuckToYourMouse")
                # or use ("TASKKILL /F /IM ShitStuckToYourMouse")
                #os.pgkill(os.getpgid(proc.pid), signal.SIGTERM)
            #proc = False
        elif event in (None, 'particleColor'):  # Update color and text of the color-picker button
            if particleColor == "None":
                particleColor = config.get("SETTINGS", "particleColor")
                values['particleColor'] = config.get("SETTINGS", "particleColor")
            particleColor = values['particleColor']
            window['color picker button'].update(('Particle color picker: %s' % particleColor), button_color=("#010101", particleColor))
    if proc:
        proc.kill()
    window.close()


if __name__ == '__main__':
    config = CaseConfigParser()
    parseList = CaseConfigParser(converters = {'list': lambda x: [i.strip() for i in x.split(',')]})
    config.optionxform = str  # Read/write case-sensitive (Actually, read/write as string, which is case-sensitive)
    config.read("config.ini")  # Read config file
    if not config.has_section("SETTINGS"):
        setDefaults()
    particleColor = str(config.get("SETTINGS", "particleColor"))
    main(config)
