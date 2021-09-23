
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
#  Copyright (c) 2021.                                                         \
#  Matthias Grommisch <distelzombie@protonmail.com>                            \
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
import PySimpleGUI as sg
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
    global config, transparentColor, particleSize, particleAge, ageBrightnessMod, ageBrightnessNoise, velocityMod, \
        velocityClamp, GRAVITY, drag, FPS, particleColor, particleColorRandom, ageColor, ageColorSpeed, ageColorSlope, \
        ageColorSlopeConcavity, ageColorNoise, ageColorNoiseMod, offsetX, offsetY, markPosition, numParticles, \
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


def updateVariables(values):
    global particleSize, particleAge, ageBrightnessMod, ageBrightnessNoise, velocityMod, \
        velocityClamp, GRAVITY, drag, FPS, particleColor, particleColorRandom, ageColor, ageColorSpeed, ageColorSlope, \
        ageColorSlopeConcavity, ageColorNoise, ageColorNoiseMod, offsetX, offsetY, markPosition, numParticles, \
        randomMod, dynamic, randomModDynamic, printMouseSpeed, levelVelocity, levelNumParticles  # God damn it
    particleSize = int(values['particleSize'])
    particleAge = int(values['particleAge'])
    ageBrightnessMod = float(values['ageBrightnessMod'])
    ageBrightnessNoise = int(values['ageBrightnessNoise'])
    velocityMod = float(values['velocityMod'])
    velocityClamp = int(values['velocityClamp'])
    GRAVITY = (values['GRAVITY_X'], values['GRAVITY_Y'])
    drag = float(values['drag'])
    FPS = int(values['FPS'])
    particleColor = str(values['particleColor'])
    particleColorRandom = values['particleColorRandom']
    ageColor = values['ageColor']
    ageColorSpeed = float(values['ageColorSpeed'])
    ageColorSlope = values['ageColorSlope']
    ageColorSlopeConcavity = float(values['ageColorSlopeConcavity'])
    ageColorNoise = int(values['ageColorNoise'])
    ageColorNoiseMod = float(values['ageColorNoiseMod'])
    offsetX = int(values['offsetX'])
    offsetY = int(values['offsetY'])
    markPosition = values['markPosition']
    numParticles = int(values['numParticles'])
    randomMod = float(values['randomMod'])
    dynamic = values['dynamic']
    randomModDynamic = float(values['randomModDynamic'])
    printMouseSpeed = values['printMouseSpeed']
    levelVelocity = (values['levelVelocity_1'], values['levelVelocity_2'], values['levelVelocity_3'], values['levelVelocity_4'], values['levelVelocity_5'])
    levelNumParticles = (values['levelNumParticles_1'], values['levelNumParticles_2'], values['levelNumParticles_3'], values['levelNumParticles_4'], values['levelNumParticles_5'])


def make_window(theme):
    global particleColor
    sg.theme(theme)
    general_layout = [[sg.Spin([i for i in range(1, 400)], initial_value = 60, k = 'FPS', enable_events = True), sg.T('Frames per second. Also affects number of particles as they are spawned per frame.')],
                      [sg.Spin([i for i in range(1, 11)], initial_value = 2, k = 'particleSize', enable_events = True), sg.T('Particle size in pixel * pixel')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 60, k = 'particleAge', enable_events = True),
                       sg.T('Particle age (in frames) OR modifier for time until brightness < 7 (death)')],
                      [sg.Slider(range=(0.00, 9.99), default_value = 5.30, resolution = .01, size=(40, 15), orientation='horizontal', k = 'ageBrightnessMod', enable_events = True)],
                      [sg.T('Increase for slower brightness decline (concavity of downward slope)')],
                      # [sg.Text('_______________________________________________________________________________________________________')],
                      [sg.Spin([i for i in range(1, 100)], initial_value = 12, k = 'ageBrightnessNoise', enable_events = True),
                       sg.T('Adds (twinkling) random noise to age/brightness: Between +-ageBrightnessNoise. 0 for no noise')],
                      # [sg.Text('_______________________________________________________________________________________________________')],
                      [sg.Slider(range=(0.00, 9.99), default_value = 1.60, resolution = .01, size=(40, 15), orientation='horizontal', k = 'velocityMod', enable_events = True)],
                      [sg.T('Lowers velocity added to particle based on mouse speed: mouse speed / velocityMod')],
                      # [sg.Text('_______________________________________________________________________________________________________')],
                      [sg.Spin([i for i in range(1, 1000)], initial_value = 200, k = 'velocityClamp', enable_events = True),
                       sg.T('Max. particle velocity')],
                      [sg.Slider(range=(-29.999, 29.999), default_value = 0.000, resolution = .001, size=(19, 15), orientation='horizontal', k = 'GRAVITY_X', enable_events = True),
                       sg.Slider(range=(-29.999, 29.999), default_value = 0.025, resolution = .001, size=(19, 15), orientation='horizontal', k = 'GRAVITY_Y', enable_events = True)],
                      [sg.T('x and y motion added to any particle. Maybe turn negative and simulate smoke or flames')],
                      # [sg.Text('_______________________________________________________________________________________________________')],
                      [sg.Slider(range = (0.000, 2.999), default_value = 0.850, resolution = .001, size = (40, 15), orientation = 'horizontal', k = 'drag', enable_events = True)],
                      [sg.T('Particle drag, higher equals less drag: (drag * particle speed) per frame')],
                      # [sg.Text('_______________________________________________________________________________________________________')],
                      [sg.T('_______________________________________________________________________________________________________')],
                      [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '), sg.Button('Close child process',
                                  k = 'Close', enable_events = True), sg.T('  '), sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
                      [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    color_layout = [[sg.Input(visible=False, enable_events=True, k='particleColor'), sg.ColorChooserButton('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor), size = (25, 2))],
                    [sg.T('Use "#ff0001" for full HSV color when ageColor is True')],
                    [sg.Checkbox('Randomly colored particles', default = False, k = 'particleColorRandom', enable_events = True)],
                    [sg.Checkbox('Change hue linearly, based on age.', default = True, k = 'ageColor', enable_events = True)],
                    [sg.Slider(range = (0.000, 99.999), default_value = 5.500, resolution = .001, size = (40, 15),
                               orientation = 'horizontal', k = 'ageColorSpeed', enable_events = True), sg.T('Hue aging speed factor. Not used if ageColorSlope = True')],
                    [sg.Checkbox('Age like concave downward curve IF ageColor = True: For more pronounced pink and blue colors', default = True, k = 'ageColorSlope', enable_events = True)],
                    [sg.T('(Or whatever is highest hue value of particleColor)')],
                    [sg.Slider(range = (0.000, 9.999), default_value = 0.420, resolution = .001, size = (40, 15),
                               orientation = 'horizontal', k = 'ageColorSlopeConcavity', enable_events = True)],
                    [sg.T('Increase concavity of downward slope representing values over age. (Think: https://i.stack.imgur.com/bGi9k.jpg)')],
                    [sg.Spin([i for i in range(1, 100)], initial_value = 12, k = 'ageColorNoise', enable_events = True),
                     sg.T('Adds random noise to hue: Between +-ageColorNoise. 0 for no noise')],
                    [sg.Slider(range = (0.000, 1.000), default_value = 0.420, resolution = .001, size = (40, 15),
                               orientation = 'horizontal', k = 'ageColorNoiseMod', enable_events = True)],
                    [sg.T('Shifts color noise weight to be more positive or negative: 0 = only positive noise, 0.5 = balanced, 1.0 = only negative noise, etc')],
                    [sg.T('_______________________________________________________________________________________________________')],
                    [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '), sg.Button('Close child process',
                                k = 'Close', enable_events = True), sg.T('  '), sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
                    [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    dynamic_layout = [[sg.Text('Dynamics settings')],
                      [sg.T('_______________________________________________________________________________________________________')],
                      [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '), sg.Button('Close child process', k = 'Close', enable_events = True), sg.T('  '),
                       sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
                      [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    graphing_layout = [[sg.Text("Anything you would use to graph will display here!")],
                       [sg.Graph((200, 200), (0, 0), (200, 200), background_color = "black", enable_events = True)],
                       # [sg.Table(values = data, headings = headings, max_col_width = 25,
                       #           background_color = 'black',
                       #           auto_size_columns = True,
                       #           display_row_numbers = True,
                       #           justification = 'right',
                       #           num_rows = 2,
                       #           alternating_row_color = 'black',
                       #           k = '-TABLE-',
                       #           row_height = 25)]]
                       [sg.T('_______________________________________________________________________________________________________')],
                       [sg.Button('Save and Run', k = 'Save', enable_events = True), sg.T('  '), sg.Button('Close child process', k = 'Close', enable_events = True), sg.T('  '),
                        sg.Button('Reset to defaults', k = 'Reset', enable_events = True)],
                       [sg.Button('Exit', k = 'Exit', enable_events = True)]]

    layout = [[sg.T('ShitStuckToYourMouse', size = (38, 1), justification = 'center',
                    font = ("Segoe UI", 16), relief = sg.RELIEF_RIDGE, enable_events = True)]]

    layout += [[sg.TabGroup([[sg.Tab('General settings', general_layout),
                              sg.Tab('Color settings', color_layout),
                              sg.Tab('Dynamics', dynamic_layout),
                              sg.Tab('Preview', graphing_layout)]])]]

    return sg.Window('ShitStuckToYourMouse', layout)


def main():
    global particleColor
    oldColor = particleColor
    window = make_window(sg.theme('Dark'))
    sg.set_options(font = "Segoe UI")  # Grrrrrr
    while True:
        event, values = window.read(timeout=250)
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            print('============ Event = ', event, ' ==============')
            print('-------- Values Dictionary (key:value) --------')
            print(values['particleColor'])
        if event in (None, 'Exit'):
            print("[LOG] Clicked Exit!")
            break
        elif event in (None, 'Reset'):
            print("[LOG] Reset to defaults...")
            answer = sg.popup_yes_no('Reset all settings to defaults?')
            if answer == 'Yes':
                setDefaults()
                readVariables()
            else:
                continue
        elif event in (None, 'Save'):
            print("[LOG] Save to config.ini and run programm...")
            updateVariables(values)
            with open("config.ini", 'w') as configfile:
                config.write(configfile)
            if proc: proc.kill()
            else: proc = subprocess.Popen("py sparkles.py")
        elif event in (None, 'Close'):
            proc.kill()
        elif event in (None, 'particleColor'):  # Update color and text of the color-picker button
            particleColor = values['particleColor']
            window['Particle color picker: %s' % oldColor].update('Particle color picker: %s' % particleColor, button_color=("#010101", particleColor))
            oldColor = values['particleColor']

    window.close()
    exit(0)


if __name__ == '__main__':
    if not config.has_section("SETTINGS"):
        setDefaults()
    readVariables()  # Read variables from config.ini
    main()
