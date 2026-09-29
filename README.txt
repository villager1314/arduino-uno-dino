Arduino Uno + Python/Pygame dinosaur runner

Detected board port: COM32 (USB-SERIAL CH340)
Serial speed: 115200 baud

1. Open uno_platform_game/uno_platform_game.ino in Arduino IDE.
2. Select Arduino Uno and port COM32, then upload.
3. Close Arduino IDE Serial Monitor.
4. In this outputs folder run:
   python uno_game.py --port COM32

Controls: Space, W, Up, or left mouse click jumps. After a collision,
Space/Up/click restarts. P pauses or resumes; R resets; Esc quits.

Each iced-tea bottle adds one shield layer (up to 9). Each hit consumes one layer.
Aircraft fire jumpable low bullets. Meteors mark a point ahead, fall, and leave
moving ground fire. Touching either the meteor or fire is fatal without a shield.

Hazard spacing scales with speed so every generated sequence remains avoidable.

Stickmen fire bullets and tanks fire shells; both can be stomped from above.
Poison pools must be jumped. Day and night switch every 300 points.

If the Uno is unplugged, the game freezes and displays ARDUINO DISCONNECTED.
It automatically reconnects when the CH340 serial port returns.

For Python 3.14 this project uses pygame-ce, imported in code as pygame.
