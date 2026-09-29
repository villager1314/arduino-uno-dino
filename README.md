# Arduino Uno Dino

An endless-runner game whose gameplay logic runs on an Arduino Uno (ATmega328P), while a Windows Python/Pygame application handles rendering and input.

## Hardware

- Arduino Uno or compatible ATmega328P board
- CH340 USB-to-serial interface
- USB connection to a Windows PC

## Features

- Arduino-controlled jumping, gravity, collision detection, scoring, and difficulty
- Cacti, birds, armed stick figures, tanks, poison pools, aircraft, and meteors
- Stackable iced-tea shields (up to 9 layers)
- Day/night cycle and progressively increasing speed
- Built-in LED lights while jumping and flashes after death
- Pause support and automatic CH340 reconnection
- Fair-spacing rules that prevent unavoidable obstacle combinations

## Setup

1. Open `uno_platform_game/uno_platform_game.ino` in Arduino IDE.
2. Select **Arduino Uno**, choose the CH340 serial port, and upload at 115200 baud.
3. Close Arduino IDE's Serial Monitor.
4. Install the Python dependencies:

   ```powershell
   python -m pip install pygame-ce pyserial
   ```

5. Start the game (replace `COM32` when necessary):

   ```powershell
   python uno_game.py --port COM32
   ```

The program can normally detect a CH340 port automatically, so `--port` may be omitted.

## Controls

- `Space`, `W`, `Up`, or left mouse button: jump
- `P`: pause or resume
- `R`: restart
- `Esc`: quit

Stick figures fire bullets and tanks fire shells. Both can be defeated by jumping on them from above. The dinosaur does not fire weapons.

## Architecture

The PC sends only input state over USB serial. The Uno calculates gameplay and returns compact JSON state messages. Pygame renders those states without owning the game rules.
