```
    _____                 __                ______) __     __)          __     __)              
   (, /   )           (__/  )        /)    (, /    (, )   /            (, /|  /|                
    _/__ / ________     / _/_     _ (/_      /   ___ /   /  ___    __    / | / |  ___    _    _ 
    /     (_)(_) /_)_) /  (__(_(_(__/(__  ) /   (_) (___/_ (_)(_(_/ (_) /  |/  |_(_)(_(_/_)__(/_
 ) /          .-/   (_/                  (_/       )   /             (_/   '                    
(_/          (_/                                  (__ /
```
Yea boy! It's the 90s again! Get some _*very elegant*_ poop stuck to your mouse - *like ppl did in the 90s! Yay!!* Waste some CPU-cycles with nice visuals! ... The 90s!! Who cares about 5% CPU! Get this poop stuck to your mouse cursor! Now! NOW!

Draws mouse-cursor-following text, cursor coordinates, color of pixel under cursor, pictures or a clock - for when you really need to keep an eye on the time. Uses PyGame for 'low' resource usage. Works by creating a transparent full-screen window that is click-through, on top of the z-order. (But not on top of the context menus, start menu and all these things.)

The intention for this is to build upon it to create something interesting - like cellular automata to draw fancy graphics over/around mouse cursor. Something like that. We'll see.

---

Usage:
- Run PoopStuckToYourMouse.exe for a heavily configurable, nice sparkle effect with velocity and gravity and more. (not optimized)
- ^--- "Do it!" - Palpatine
- Other possibilities: 
   - Display color under mouse cursor
   - Display a clock
   - CPU usage
   - RAM usage
   - Both/All
   - An image
- You can also run 'other.exe' or 'sparkles.exe' alone. (Or the .py versions) They'll use the settings stored in the 'config.ini' - or if the files doesn't exist, create it with the values saved in 'defaults.ini'.

Important notice:
- If you execute PoopStuckToYourMouse.exe, (or main.pyw) don't have any other programs running that are also named "other.exe" or "sparkles.exe", otherwise they'll be terminated. So far this is the only working solution to kill the spawned processes. :(

---

Special features:
- Name is stupid! (Now less vulgar!)
- Single core capable
- Fancy colors!
- Basically just experimentation
- It's at least something. *shrugs*
- Rainbow colors!
- I completely disregard all Linux users.

---

Ah... currently using the sparkles increases the energy usage of my PC by 20W. Maybe don't use it untill I find a better suited package than PyGame.

Performance with 20 particles per frame @60fps: (runs only on a single core)
- Laptop with AMD A4-6210:              25% CPU usage. (max per core: 25%)
- Desktop with AMD Ryzen 5 2600 @4Ghz:  4.7 to 5.5% CPU usage. (max per core: 8.33%)

Performance of Clock, Color, Image, CPU, RAM ...:
- Laptop:   3 to 5% CPU usage. (max per core: 25%)
- Desktop:  0.7 to 1% CPU usage. (max per core: 8.33%)

For some reason, if no subprocesses are running, PoopStuckToYourMouse.exe (or main.pyw) uses 4 to 5% CPU on my laptop.

Also, running any of the executables for the first time in, maybe, 30 minutes, takes a long time because Windows Defender needs to scan the file again and again. (And, I guess, because they are basically ~15MB big archives full of pure code, they take a long time to scan) If you exclude the folder in the security center then the starting time is only 1/10th or less.

---

Prerequisites:
- Windows (I used Windows 10 21H1)
- PyGame
- PySimpleGUI
- psutil
- pywin32
- Pillow

---

![Current GUI](https://i.imgur.com/u55J7IS.png?raw=true)

---
Thank you, various netizens, for all the StackOverflow questions and answers that helped me grasp an incredibly rudimentary understanding of Python.
