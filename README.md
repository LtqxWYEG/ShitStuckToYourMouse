```
  _____ _     _ _    _____ _              _ _________     __              __  __                      
 / ____| |   (_) |  / ____| |            | |__   __\ \   / /             |  \/  |                     
| (___ | |__  _| |_| (___ | |_ _   _  ___| | _| | __\ \_/ /__  _   _ _ __| \  / | ___  _   _ ___  ___ 
 \___ \| '_ \| | __|\___ \| __| | | |/ __| |/ / |/ _ \   / _ \| | | | '__| |\/| |/ _ \| | | / __|/ _ \
 ____) | | | | | |_ ____) | |_| |_| | (__|   <| | (_) | | (_) | |_| | |  | |  | | (_) | |_| \__ \  __/
|_____/|_| |_|_|\__|_____/ \__|\__,_|\___|_|\_\_|\___/|_|\___/ \__,_|_|  |_|  |_|\___/ \__,_|___/\___|
```
Yeah, bitch! It's the 90s again! Get some shit stuck to your mouse, like ppl did in the 90s! Yay!! Waste some CPU-cycles, have visuals... the 90s!! Who cares about 5% CPU! Get this hit stuck to your mouse cursor! woot

Draws mouse-cursor-following text, cursor coordinates, color of pixel under cursor, pictures or a clock - for when you really need to keep an eye on the time. Uses PyGame for 'low' resource usage. Works by creating a transparent full-screen window that is click-through, on top of the z-order. (But not on top of the context menus, start menu and all these things.)

The intention for this is to build upon it to create something interesting - like cellular automata to draw fancy graphics over/around mouse cursor. Something like that. We'll see.


---


Usage:
- Run ShitStuckToYourMouse.exe for a heavily configurable, nice sparkle effect with velocity and gravity and more. (not optimized)
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
- If you execute ShitStuckToYourMouse.exe, (or main.pyw) don't have any other programs running that are also named "other.exe" or "sparkles.exe", otherwise they'll be terminated. So far this is the only working solution to kill the spawned processes. :(


Special features:
- Name is stupid!
- Single core capable
- Fancy colors!
- Basically just experimentation
- It's at least something. *shrugs*
- Rainbow colors!
- I completely disregard all Linux users.


Performance with 20 particles per frame @60fps: (runs only on a single core)
- Laptop with AMD A4-6210:              20 to 25% CPU usage. (max per core: 25%)
- Desktop with AMD Ryzen 5 2600 @4Ghz:  4.7 to 5.5% CPU usage. (max per core: 8.33%)


Prerequisites:
- Windows (I used Windows 10 21H1)
- PyGame
- PySimpleGUI
- psutil
- pywin32
- Pillow



![Current GUI](https://i.imgur.com/u55J7IS.png?raw=true)

---
Thank you, various netizens, for all the StackOverflow questions and answers that helped me grasp an incredibly rudimentary understanding of Python.
