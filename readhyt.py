#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This program reads out IST HYT sensors(HYT-221, HYT-271, HYT-939)
#
# License: Public Domain/CC0
# Original source: https://github.com/joppiesaus/python-hyt/
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Humidity:
#   0x0000      -       0x3FFFF  hex
#   0           -       16383    dec
#   0           -       100      % RH
#
# Temperature:
#   0x0000      -       0x3FFF   hex
#   0           -       16383    dec
#  -40          -       125      °C
#   233.15      -       298.15   °K
#   ???         -       ???      °F
#
#  |  byte 0  |  byte 1  |  byte 2  |  byte 3  |  
#  |---------------------|---------------------|
#  |      Humidity       |     Temperature     |
#  |---------------------|---------------------|
#  | 2 bit |   14 bit    |   14 bit    | 2 bit |
#  |-------|-------------|-------------|-------|
#  | state |    data     |    data     | dummy |
#      |
#      +-----------------------+
#      |   bit 0   |   bit 1   |
#      | CMode bit | stale bit |
#      +-----------------------+
#
# CMode bit: if 1 - sensor is in "command mode"
# Stale bit: if 1 - no new value has been created since the last reading
#
# RH = (100 / (2^14 - 1)) * RHraw
# T  = (165 / (2^14 - 1)) * Traw - 40
#
# crappy ascii picture from top to see pinout:
#  ---
# |~ ~|
# | O |
# |___|
# ||||
# |||+-SCL
# ||+--VDD
# |+---GND
# +----SDA
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


import time
import smbus

addr = 0x28 # default address for hyt sensors
delay = 50.0 / 1000.0 # 50-60 ms delay. Without delay, it doesn't work.
# I should test that delay more.
bus = smbus.SMBus(1) # use /dev/i2c1

def read():
	bus.write_byte(addr, 0x00) # send some stuff
	time.sleep(delay) # wait a bit
	reading = bus.read_i2c_block_data(addr, 0x00, 4) # read the bytes
	# Mask the first two bits
	humidity = ((reading[0] & 0x3F) * 0x100 + reading[1]) * (100.0 / 16383.0)
	# Mask the last two bits, shift 2 bits to the right
	temperature = 165.0 / 16383.0 * ((reading[2] * 0x100 + (reading[3] & 0xFC)) >> 2) - 40
	return humidity, temperature

def readandprint():
	rh, t = read()
	print "Humidity:", rh, "% RH"
	print "Temperature:", t, "°C"

if __name__ == "__main__":
	readandprint()
	
