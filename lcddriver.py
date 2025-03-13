#Source LCD-Module: https://joy-it.net/de/products/SBC-LCD16x2 (Anleitung: https://joy-it.net/files/files/Produkte/SBC-LCD16x2/SBC-LCD16x2_Anleitung_2023-09-19.pdf) --- AccessDate: 07.03.2024
#Source: http://tutorials-raspberrypi.de/wp-content/uploads/scripts/hd44780_i2c.zip --- AccessDate: 07.03.2024
#     <lcddriver.py is used to control a LCD-module via I2C communication>
#     Copyright (C) <2024>  <Peter Pallnstorfer>
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import sys
# todo why do we need this?
sys.path.append("./lib")

#import i2c_lib
from time import sleep

# LCD Address
ADDRESS = 0x27

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

En = 0b00000100 # Enable bit
Rw = 0b00000010 # Read/Write bit
Rs = 0b00000001 # Register select bit

class lcd:
    #initializes objects and lcd
    def __init__(self):
         
        self.lcd_device = i2c_lib.i2c_device(ADDRESS)

        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)

        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        sleep(0.2)

    # clocks EN to latch command
    def lcd_strobe(self, data):
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        sleep(.0005)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))
        sleep(.0001)

    def lcd_write_four_bits(self, data):
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))
      
    #turn on/off the lcd backlight
    def lcd_backlight(self, state):
        if state in ("on","On","ON"):
            self.lcd_device.write_cmd(LCD_BACKLIGHT)
        elif state in ("off","Off","OFF"):
            self.lcd_device.write_cmd(LCD_NOBACKLIGHT)
        else:
            logging.error("Invalid LCD backlight state")
            print("Unknown State!")

    # Writes a string to the LCD
    def lcd_display_string(self, display_text: str, line_nr: int):
        if line_nr < 1 or line_nr > 4:
            logging.error("The line_nr passed is invalid, only numbers from 1-4 are allowed")

        if line_nr == 1:
            self.lcd_write(0x80)
        elif line_nr == 2:
            self.lcd_write(0xC0)
        elif line_nr == 3:
            self.lcd_write(0x94)
        elif line_nr == 4:
            self.lcd_write(0xD4)

        for char in display_text:
            # what does 'Rs' mean?
            self.lcd_write(ord(char), Rs)

    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)
