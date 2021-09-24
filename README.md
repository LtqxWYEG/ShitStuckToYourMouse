```
 _____ _     _ _     _____ _              _     _____    __   __                ___  ___                     
/  ___| |   (_) |   /  ___| |            | |   |_   _|   \ \ / /                |  \/  |                     
\ `--.| |__  _| |_  \ `--.| |_ _   _  ___| | __  | | ___  \ V /___  _   _ _ __  | .  . | ___  _   _ ___  ___ 
 `--. \ '_ \| | __|  `--. \ __| | | |/ __| |/ /  | |/ _ \  \ // _ \| | | | '__| | |\/| |/ _ \| | | / __|/ _ \
/\__/ / | | | | |_  /\__/ / |_| |_| | (__|   <   | | (_) | | | (_) | |_| | |    | |  | | (_) | |_| \__ \  __/
\____/|_| |_|_|\__| \____/ \__|\__,_|\___|_|\_\  \_/\___/  \_/\___/ \__,_|_|    \_|  |_/\___/ \__,_|___/\___|
```
Yeah, bitch! It's the 90s again! Get some shit stuck to your mouse, like ppl did in the 90s! Yay!! Waste some CPU-cycles, have visuals... the 90s!! Who cares about 5% CPU! Get this hit stuck to your mouse cursor! woot

Draws mouse-cursor-following text, cursor coordinates, color of pixel under cursor, pictures or a clock - for when you really need to keep an eye on the time. Uses PyGame for low resource usage. Works by creating a transparent full-screen window that is click-through, on top of the z-order. (But not on top of the context menu.)

---

The intention for this is to build upon it to create something interesting - like cellular automata to draw fancy graphics over/around mouse cursor. Something like that.

Usage:
- Run main.pyw for a heavily configurable, nice sparkle effect with velocity and gravity. (not optimized)
- ^--- 
- Run clock.py for a clock beneath your cursor. (optimized)
- Run color.py for RGB values of the pixel. Also draws a 40x40 square, filled with the color for visibility.
- Run picture.py to have a stupid python image follow your mouse.
- The other programs are inferior. (Like, literally every other)


Special features:
- Name is stupid!
- Basically just experimentation
- Surprisingly high performance, much higher than using tkinter
- It's at least something. *shrugs*


Performance Clock.py: (single core)
- Laptop with AMD A4-6210: 1 to 4% CPU usage @60 fps. Reaches up to 400 fps
- Desktop with AMD Ryzen 5 2600 @4Ghz: 0 to 0.5% CPU usage @60 fps. Reaches 2500 to 3333 fps


Prerequisites:
- Windows (I used Windows 10 21H1)
- PyGame
- PySimpleGUI



---
Thank you, various netizens, for all the StackOverflow questions whose answers helped me grasp an incredibly rudimentary understanding of Python.
