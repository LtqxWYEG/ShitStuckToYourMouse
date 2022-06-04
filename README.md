```
      __                __                ______) __     __)          __     __)              
  (__/  ) /)   ,    (__/  )        /)    (, /    (, )   /            (, /|  /|                
    /    (/     _/_   / _/_     _ (/_      /   ___ /   /  ___    __    / | / |  ___    _    _ 
 ) /     / )__(_(__) /  (__(_(_(__/(__  ) /   (_) (___/_ (_)(_(_/ (_) /  |/  |_(_)(_(_/_)__(/_
(_/               (_/                  (_/       )   /             (_/   '                    
                                                (__ /
```
Yea boy! It's the 00s again! Get some _*very elegant*_ shit stuck to your mouse - *like ppl did in the early 00s! Yay!!* Waste some CPU-cycles with nice visuals! ... The 00s!! Who cares about 5% CPU! Sense? 00! Get this shit stuck to your mouse cursor! Now! NOW!

Draws a very nice looking sparkle/glitter/smoke/fire effect following/on your mouse.
Can also draw mouse-cursor-following text, CPU and RAM usage, pictures or a clock with milliseconds - for when you really need to keep an eye on the time.  
It can also show you the color of the pixel under the cursor in real RGB, complementary RGB or complementary RYB. (RYB is kinda inaccurate between the r, y, and b colors.)  
Uses PyGame for 'low' resource usage. Works by creating a TOPMOST transparent full-screen window that is click-through and has no taskbar button. (But not on top of the context menus, start menu and all these things.)

The intention for this is to build upon it to create something interesting - like cellular automata to draw fancy graphics over/around mouse cursor. Something like that. We'll see.
(Hahaha, a year ago I wrote "cellular automata". Pffff. Boids maybe next though)

---

Usage:
- Run ShitStuckToYourMouse.exe for a heavily configurable, very nice sparkle effect with velocity and gravity and more. (not optimized)
- ^--- "Do it!" - Palpatine
- Other possibilities: 
   - Display color under mouse cursor
      - RGB, RGB complementary and RYB complementary (With caveats)
   - Display a clock
   - CPU usage
   - RAM usage
   - Both/All
   - An image
- You can also run 'other.exe' or 'sparkles.exe' alone. (Or the .py versions) They'll use the settings stored in the 'config.ini' - or if that file doesn't exist, create it with the values saved in 'defaults.ini'.

---

Special features:
- Name is stupid! (Now less vulgar!)
- Single core capable, but sometimes with threads!
- Fancy colors!
- Basically just an experimentation!
- It's at least something. *shrugs*
- Rainbow colors!
- I completely disregard all Linux users!
- Good performance!

---
Sparkles:  
Performance with 20 particles per frame @60fps: (runs only on a single core)
- Laptop with AMD A4-6210:              20 to 25% CPU usage. (max per core: 25%) Now with double the framerate!
- Desktop with AMD Ryzen 5 2600 @4Ghz:  1.7 to 3.5% CPU usage. (max per core: 8.33%)


---

Prerequisites:
- Windows (I used Windows 10 21H2)
- Pillow
- configparser 
- pywin32
- psutil 
- pygame 
- pyinstaller
- pefile
- setuptools
- PySimpleGUI
- acrylic - Only for the RYB complemantary color

---

Here you can see what the GUI looks like. There are also small samples of the capabilities of this thing visible.

![Current GUI](https://i.imgur.com/eDaJJLI.png?raw=true)  
![Current GUI](https://i.imgur.com/powKnfT.png?raw=true)  
![Current GUI](https://i.imgur.com/E73vlHL.png?raw=true)  
![Current GUI](https://i.imgur.com/PQeCyuU.png?raw=true)  


---
Thank you, various netizens, for all the StackOverflow questions and answers that helped me grasp an incredibly rudimentary understanding of Python.
