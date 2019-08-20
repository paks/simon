import os
import board
from digitalio import DigitalInOut, Direction
import time
import touchio
import pulseio
import random
import adafruit_dotstar

print(dir(board), os.uname()) # Print a little about ourselves

# Game speed options
SLOW = 1.25
NORMAL = 0.75
FAST = 0.25
game_speed = NORMAL

piezo = pulseio.PWMOut(board.A3, duty_cycle=(65536 // 2), frequency=440, variable_frequency=True)

# Dotstar led setup
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)

pixel = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1, auto_write=False)
def set_dotstar_color(color):
    pixel.fill(color) # Turn off the dotstar
    pixel.show()

set_dotstar_color(BLACK)

# Capacitive touch pads setup
touches = [DigitalInOut(board.CAP0)]
for p in (board.CAP1, board.CAP2, board.CAP3):
    touches.append(touchio.TouchIn(p))

# Setup leds above the capacitive touch pads
leds = []
led = DigitalInOut(board.LED4)
led.direction = Direction.OUTPUT
leds.append(led) # Appended twice. Position '0' is not going to be used
leds.append(led) # This is to simplify the game code.
for p in (board.LED5, board.LED6, board.LED7):
    led = DigitalInOut(p)
    led.direction = Direction.OUTPUT
    leds.append(led)

# Turn them off
for led in leds:
    led.value = False

# The musical notes used in the game
NOTE_E3 = 165
NOTE_CS4 = 277
NOTE_D4 = 294
NOTE_DS4 = 311
NOTE_E4 = 330
NOTE_A4 = 440

# Tones used in the game
game_notes = [0, NOTE_A4, NOTE_CS4, NOTE_E3, NOTE_E4]
# Game over tune. Each tuple has the note play and the duration in fractions of a second
game_over_tones_duration = [(NOTE_E4, 2), (NOTE_DS4, 2), (NOTE_D4, 2), (NOTE_CS4, 2), (NOTE_CS4,8), (NOTE_D4, 8), (NOTE_DS4, 8), (NOTE_E4, 8)]

# Setup capacitive touch array
cap_touches = [False, False, False, False]

def game_over_action():
    """
    Notify the player that the game is over.

    The function will print "Game Over" in the serial console.
    Then, play the game over tune and turn the dotstar led red.
    """
    print("game over")
    for i,tone_duration in enumerate(game_over_tones_duration):
        if tone_duration[0] == 0:
            piezo.duty_cycle = 0  # Off
        else:
            piezo.frequency = tone_duration[0] # Tone
            piezo.duty_cycle = 65536 // 2
        led_index = (i % 4) + 1
        leds[led_index].value = True
        time.sleep(1 / tone_duration[1]) # Duration
        leds[led_index].value = False
    piezo.duty_cycle = 0
    set_dotstar_color(RED)


def play_note(frequency = 440, duration = 2):
    """
    Play a note in the piezo buzzer.

    :param int frecuency: Frecuancy to play in Hertzs. Default 440 Hz
    :param float duration: How long should the tone play in seconds. 
                           The default is 2 secods.
    """
    piezo.frequency = frequency
    piezo.duty_cycle = 65536 // 2  # On 50%
    time.sleep(duration)  # On
    piezo.duty_cycle = 0  # Off

def read_caps():
    """
    Read the 4 capacitive touch pads in the PyRuler.

    This function wil read the 4 capacitive touch pads and
    update the touches array with a boolean value. If the value
    is True, the pad was touched. Otherwise, false.
    [0] -> CAP0
    [1] -> CAP1
    [2] -> CAP2
    [3] -> CAP3

    Returns:
    [Boolean]: A boolean array with True for the pads that were touched.
               Otherwise, False.
    """
    t0_count = 0
    t0 = touches[0]
    t0.direction = Direction.OUTPUT
    t0.value = True
    t0.direction = Direction.INPUT
    # funky idea but we can 'diy' the one non-hardware captouch device by hand
    # by reading the drooping voltage on a tri-state pin.
    t0_count = t0.value + t0.value + t0.value + t0.value + t0.value + \
               t0.value + t0.value + t0.value + t0.value + t0.value + \
               t0.value + t0.value + t0.value + t0.value + t0.value
    cap_touches[0] = t0_count > 2
    cap_touches[1] = touches[1].raw_value > 3000
    cap_touches[2] = touches[2].raw_value > 3000
    cap_touches[3] = touches[3].raw_value > 3000
    return cap_touches

def read_cap():
    """
    Returns the index of the capacitive touch pad that
    was touched. Otherwise return zero. If multiple pads 
    are touched, the function would return only the value
    of the first one from left to right.

    Return:
    int: 0 -> nothing was touched.
         1 -> CAP0 was touched
         2 -> CAP1 was touched
         3 -> CAP2 was touched
         4 -> CAP3 was touched

    """
    caps = read_caps()
    if caps[0]:
        return 1
    if caps[1]:
        return 2
    if caps[2]:
        return 3
    if caps[3]:
        return 4
    return 0      # No pad has been touched.

def touched_action(index, duration = 2):
    """
    Play the capacitive pad tone and turn on the led above the pad.
    Used by both the player and the microcontroller.

    :param int index: The index of the PyRuler pad from 1 to 4. #1 is the first pad on the left.
    :param float duration: how long should the tone play in seconds. The default is 2 secods
    """
    leds[index].value = True
    f = game_notes[index]
    play_note(f, duration)
    leds[index].value = False

# This array contains the secuence of capacitive pads that need to be
# touched by the palyer. A new pad number is added after each turn.
steps = []

def show_steps():
    """
    Show the steps (capacitive pad leds) that the player needs to touch
    to keep playing the game.

    At each step, turn on the led an play the tone associated with the pad.
    """
    for i in steps:
        touched_action(i, game_speed)
        time.sleep(game_speed - 0.10)

game_active = True
while game_active:
    pad = random.randrange(1, 5)             # Posible values => 1,2,3, or 4
    steps.append(pad)
    print(steps)
    show_steps()                             # to play to the player
    set_dotstar_color(GREEN)                 # Indicate to the player that it's 
                                             # his/her turn to play.

    for i in steps:                          # It's the player's turn to play
        touched_cap = 0
        while not touched_cap:               # wait for the player to touch a capacitive pad
           touched_cap = read_cap()
        if touched_cap == i:                 # Did the player touched the correct one?
            touched_action(touched_cap, 0.5) # Yes! Play the tone and turn on the led for that pad. 
        else:
            game_active = False              # Nope :( End the game loop.
                                             # The player's turn ended.
    set_dotstar_color(BLACK)                 # Turn off the dotstar led
    time.sleep(0.75)                         # Let the player rest for a little bit.

                                             # We're out of the game loop.    
game_over_action()                           # Notify the player that the game is over. 

while True:                                  # The game is over. 
    time.sleep(1)                            # The player needs to reset the PyRuler to play again.
