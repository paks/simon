# Simon says game for the Adafruit PyRuler

## Overview

The new Adafruit PyRuler comes with 4 capacitive touch pads. There 
are four colored leds above the pads. This makes the PyRuler perfect 
for implementing a Simon says game in CircuitPython. The libraries
included in this project are for CircuitPython 4.x (bundle-4.x-mpy-20190815).

## Project Parts

* [Adafruit PyRuler](https://www.adafruit.com/product/4319)
* [Piezo Buzzer](adafruit.com/product/160)
* [USB cable](adafruit.com/product/592)

## Circuit Diagram

The PyRuler is a fully featured microcontroller board! Embedded in the end is a 
Trinket M0. For the pourpose of this project, the piezo buzzer is connected to 
the ground pin and the analog pin 3.

![PyRuler Trinket M0 wiring](./diagram/sketch_bb.png)

## Code with Circuit Python

The code is well documented. You can see it [here](https://github.com/paks/simon/blob/master/code.py).
