# led-disco-dancefloor

Welcome to the LED Disco Dance Floor project!

As seen at:

- Oggcamp 2017
- LJC Mad Scientists 2016

## Overview

The dancefloor project was conceived, as all good ideas are, at the pub.
The plan was to create a fully illuminated dancefloor, as a surpise, for the
wedding of two of my good friends; Gav & Anna.

The timeline from conception (pub) to completion (wedding) was roughly 8 months
between July of 2013 and the wedding in February 2014. Ideas were bounced around,
rejected, reworked, costed, rejected, reworked, and reworked some more over the
summer, and construction began in earnest November, and continued for 3 solid
months.

The result was a dancefloor consisting of 432 illuminated tiles, each 6"x6" (
because wood comes in feet and inches) creating an usable dancing area of 12'x9'.
The dancefloor was split into 9 modules (for transportation reasons), each coming
in at 4'x3' and about 15kg.

Patterns were created via a connected laptop via the included python program
to be displayed on each module by an ATMega328 microcontroller & TLC5940 constant
current LED drivers.

## The Software

The python software is available in `software/controller/`, and can be run with
or without an attached dancefloor for demonstration and testing purposes.

The software makes use of the **pygame** library to read input from connected joypads
and keyboards, as well as draw the GUI and handle the framerate. If a dancefloor
is connected, **pyserial** is used to send the data at 1Mbps

## The PCB & Firmware

The PCB is relatively simple and is only concerned with the action of parsing
incoming data via a serial connection and displaying it on the 48 connected RGB
LEDs. An ATMega328 is used as the microcontroller, and 3xTLC5940 ICs are used
to drive 16 LEDs each. Each of the Red, Green, and Blue LEDs are strobed, and
the switching is handled via 3 p-channel MOSFETs.

The firmware is written to be flashed using the Arduino IDE for convenience, but
uses very few of the Arduino library convenience functions (`random()`, which is
used in the failsafe backup pattern, being the exception) as most of the tight
loop is highly optimised for speed.

## Power

The entire dancefloor runs off 5v, and requires a high current power supply -
roughly 2.5A per module. An old ATX power supply with all the 5v rails tied
together has proved very reliable.
