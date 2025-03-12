#Source LCD-Module: https://joy-it.net/de/products/SBC-LCD16x2 (Anleitung: https://joy-it.net/files/files/Produkte/SBC-LCD16x2/SBC-LCD16x2_Anleitung_2023-09-19.pdf) --- AccessDate: 07.03.2024
#Source: http://tutorials-raspberrypi.de/wp-content/uploads/scripts/hd44780_i2c.zip --- AccessDate: 07.03.2024

#     <i2c_lib.py is used to set up a communication with an I2C device>
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

import smbus
from time import *

# This is a wrapper to interact with the LCD display
class i2c_device:
   def __init__(self, addr, port=1):
      self.addr = addr
      self.bus = smbus.SMBus(port)

   # Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

   # Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

   # Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

   # Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)

   # Read
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)

   # Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)