# selfcar
a raspberry pi powered self driving toy car

Goal
======

Just to have some fun with a toy race car, and AI/machine learning.

Hardware
========

- A very old race car body from my friend. It still has a DC motor (now broken and I'm ordering a new one), and a servo for steering
- Raspberry PI 3
- Camera for raspberry
- 10 A H-bridge for controlling DC motor
- 3S lipo battery
- Bread board and wire

This car only allow me to steering from 50 to 100 degrees, this is the real 'hardware' limitation. Also, the precision of the servo and the steerin wheel is a bit broken (this is a race car did a lot of heavy duty task by crawling under the house to do home inspection).

Software
========

My plan is to start recording some data with this car, hopefully after fixing the motor and gears. Then we could use any machine learning library to handle the data. The image sequence is data/*.png files, and steering data is data/steer.csv.

Status
======

- 2017/12/14 DC motor is doomed. Ordered a new one, and a bunch of gears.
- 2017/12/15 Working on the software part, looks like the recording is OK.
