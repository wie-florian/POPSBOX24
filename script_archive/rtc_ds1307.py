#!/usr/bin/env python

# Copyright (C) 2013 @XiErCh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#Source: https://github.com/Jesse201147/DS1307_RTC_Driver_I2C --- AccessDate: 07.03.2024
#modified by: Peter Pallnstorfer

import smbus

# I2C address of the DS1307 RTC
_REG_DS1307 = 0x68

# Register addresses of the DS1307 RTC
_REG_SECONDS = 0x00
_REG_MINUTES = 0x01
_REG_HOURS = 0x02
_REG_DAY = 0x03
_REG_DATE = 0x04
_REG_MONTH = 0x05
_REG_YEAR = 0x06
_REG_CONTROL = 0x07

# Open I2C bus
bus = smbus.SMBus(1)

# helper function to interact with clock
def _bcd_to_int(bcd):
    #Decode a 2x4bit BCD to a integer.
    out = 0
    for d in (bcd >> 4, bcd):
        for p in (1, 2, 4, 8):
            if d & 1:
                out += p
            d >>= 1
        out *= 10
    return int(out / 10)

# Reads current time from real time clock
def read_rtc():
    rtc_data = bus.read_i2c_block_data(_REG_DS1307, _REG_SECONDS, 7)
    second = _bcd_to_int(rtc_data[0])
    minute = _bcd_to_int(rtc_data[1])
    hour = _bcd_to_int(rtc_data[2])
    day = _bcd_to_int(rtc_data[3])
    date = _bcd_to_int(rtc_data[4])
    month = _bcd_to_int(rtc_data[5])
    year = _bcd_to_int(rtc_data[6]) + 2000 # + 2000 for 21st century
    return hour, minute, second, day, date, month, year

