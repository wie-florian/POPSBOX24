#Source SEN55: https://sensirion.github.io/python-i2c-sen5x/index.html --- AccessDate: 07.03.2024
#Source BME680: https://github.com/adafruit/Adafruit_CircuitPython_BME680 --- AccessDate: 07.03.2024
#Source RTC-DS1307: https://github.com/Jesse201147/DS1307_RTC_Driver_I2C --- AccessDate: 07.03.2024
#Source LCD-Module: https://joy-it.net/de/products/SBC-LCD16x2 (Anleitung: https://joy-it.net/files/files/Produkte/SBC-LCD16x2/SBC-LCD16x2_Anleitung_2023-09-19.pdf) --- AccessDate: 07.03.2024
#Source LCD-Module download (i2c_lib.py, lcddriver.py): http://tutorials-raspberrypi.de/wp-content/uploads/scripts/hd44780_i2c.zip --- AccessDate: 07.03.2024
#Source CCS811: https://github.com/adafruit/Adafruit_CircuitPython_CCS811 --- AccessDate: 12.03.2024
#Source UDP-POPS: https://www.aranacorp.com/en/setting-up-a-udp-server-on-raspberry-pi --- AccessDate: 12.03.2024
#Source SIM7600E-H 4G HAT: https://www.waveshare.com/wiki/SIM7600E-H_4G_HAT --- AccessDate: 19.03.2024
#written by: Peter Pallnstorfer


import os
import logging
import time
from datetime import datetime

from developer_mock import (busio, GPIO,
                           I2cConnection, LinuxI2cTransceiver, Sen5xI2cDevice,
                           adafruit_bme680, adafruit_ccs811,
                           udp_pops, lcddriver, SIM7600_GPS)


# Flags and States
POPS = True
SIM = True
exit_flag = False
csv_flag = False
sanity_flag = False

#I2C bus initialization
i2c = busio.I2C(3, 2) #SCL = GPIO3 ... SDA = GPIO2

#BME680 initialization
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)
#CCS811 initialization
ccs811 = adafruit_ccs811.CCS811(i2c)


# LCD Initialization
lcd = lcddriver.lcd()
lcd.lcd_clear()


# Function to write strings to the LCD module
def writeLCD(string1, string2):
    lcd.lcd_clear()
    lcd.lcd_display_string(string1, 1)
    lcd.lcd_display_string(string2, 2)


#Callback functions for buttons
def green_callback(channel):
    global csv_flag
    if not csv_flag:
        csv_flag = True


def red_callback(channel):
    global csv_flag
    if csv_flag:
        csv_flag = False


def yellow_callback(channel):
    global sanity_flag
    sanity_flag = True


def blue_callback(channel):
    global exit_flag
    exit_flag = True


#Exit flag to terminate the while loop in main
exit_flag = False
#Flag to control, if data is written to CSV file
csv_flag = False
#Flag to activate SanityCheck
sanity_flag = False

#Button setup with GPIO.BCM Pins
green = 26
red = 19
yellow = 20
blue = 16
GPIO.setup(green, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(red, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(yellow, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(blue, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(blue, GPIO.RISING, callback=blue_callback)
#LED GPIO Setup
led = 21
GPIO.setup(led, GPIO.OUT)


#Function to get current time from RTC module
def getTime():
    time=datetime.now()
    year=time.year
    month=time.month
    day=time.day
    hour=time.hour
    minute=time.minute
    second=time.second
    date=0
    return hour, minute, second, day, date, month, year


#Function to receive sensor values from BME680
def getBME680():
    temperature = bme680.temperature
    humidity = bme680.humidity
    pressure = bme680.pressure
    gas = bme680.gas
    return temperature, humidity, pressure, gas


#SEN55 readiness test function
def waitSEN55():
    values = device.read_measured_values()
    global exit_flag
    if exit_flag:
        return False
    if values.nox_index.available:
        writeLCD("SEN55 ready!", "")
        return False
    else:
        writeLCD("SEN55 not ready", "Waiting ...")
        return True


#Function to receive sensor values from SEN55
def getSEN55():
    values = device.read_measured_values()
    mc_1p0 = values.mass_concentration_1p0.physical
    mc_2p5 = values.mass_concentration_2p5.physical
    mc_4p0 = values.mass_concentration_4p0.physical
    mc_10p0 = values.mass_concentration_10p0.physical
    ambient_rh = values.ambient_humidity.percent_rh
    ambient_t = values.ambient_temperature.degrees_celsius
    voc_index = values.voc_index.scaled
    nox_index = values.nox_index.scaled
    return mc_1p0, mc_2p5, mc_4p0, mc_10p0, ambient_rh, ambient_t, voc_index, nox_index


#CCS811 readiness test function
def waitCCS811():
    global exit_flag
    if exit_flag:
        return False
    if ccs811.data_ready:
        writeLCD("CCS811 ready!", "")
        return False
    else:
        writeLCD("CCS811 not ready", "Waiting ...")
        return True


#Function to receive sensor values from CCS811
def getCCS811():
    try:
        cco2 = ccs811.eco2
        ttvoc = ccs811.tvoc
        return cco2, ttvoc
    except OSError as osErr:
        print("CCS811: OS error (errno {}): {}".format(osErr.errno, osErr))

    except RuntimeError as rtErr:
        print("CCS811: RuntimeError")


#Values of sensors and RTC can be checked on LCD for plausibility
def sanityCheck(strDate, strTime, temp680, hum680, pres, gas, mc1p0, mc2p5, mc4p0, mc10p0, hum55, temp55, voc, nox, co2, tvoc):
    logging.info("running sanity check")
    writeLCD("SanityCheck!", "Duration: +-25s")
    time.sleep(2)
    #RTC
    writeLCD("SanityCheck: Date", strDate)
    time.sleep(1)
    writeLCD("SanityCheck: Time", strTime)
    time.sleep(1)
    #BME680
    writeLCD("SanityCheck: BME", "Temp: "+str(temp680))
    time.sleep(1)
    writeLCD("SanityCheck: BME", "Hum: "+str(hum680))
    time.sleep(1)
    writeLCD("SanityCheck: BME", "Pres: "+str(pres))
    time.sleep(1)
    writeLCD("SanityCheck: BME", "Gas: "+str(gas))
    time.sleep(1)
    #SEN55
    writeLCD("SanityCheck: SEN", "MC1P0: "+str(mc1p0))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "MC2P5: "+str(mc2p5))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "MC4P0: "+str(mc4p0))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "MC10P0: "+str(mc10p0))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "Hum: "+str(hum55))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "Temp: "+str(temp55))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "VOC: "+str(voc))
    time.sleep(1)
    writeLCD("SanityCheck: SEN", "NOx: "+str(nox))
    time.sleep(1)
    #CCS811
    writeLCD("SanityCheck: CCS", "CO2: "+str(co2))
    time.sleep(1)
    writeLCD("SanityCheck: CCS", "TVOC: "+str(tvoc))
    time.sleep(1)
    #END
    global sanity_flag
    sanity_flag = False
    writeLCD("Sanity Check!", "Finished!")
    time.sleep(2)


def cleanPopsData(data):
    data_array = data.split(",")
    #rnd1 = data_array[0]
    #rnd2 = data_array[1]
    path = data_array[2]
    #rnd = data_array[3]
    datetime = data_array[3]
    status = data_array[5]
    data_status = data_array[6]
    part_ct = data_array[7]
    hist_sum = data_array[8]
    part_con = data_array[9]
    bl = data_array[10]
    blth = data_array[11]
    std = data_array[12]
    max_std = data_array[13]
    p = data_array[14]
    tof_p = data_array[15]
    pump_life = data_array[16]
    width_std = data_array[17]
    ave_width = data_array[18]
    pops_flow = data_array[19]
    pump_fb = data_array[20]
    ld_temp = data_array[21]
    laser_fb = data_array[22]
    ld_mon = data_array[23]
    temp = data_array[24]
    batV = data_array[25]
    laser_current = data_array[26]
    flow_set = data_array[27]
    bl_start = data_array[28]
    th_mult = data_array[29]
    nbins = data_array[30]
    logmin = data_array[31]
    logmax = data_array[32]
    skip_save = data_array[33]
    min_peak_pts = data_array[34]
    max_peak_pts = data_array[35]
    raw_pts = data_array[36]
    b0 = data_array[37]
    b1 = data_array[38]
    b2 = data_array[39]
    b3 = data_array[40]
    b4 = data_array[41]
    b5 = data_array[42]
    b6 = data_array[43]
    b7 = data_array[44]
    b8 = data_array[45]
    b9 = data_array[46]
    b10 = data_array[47]
    b11 = data_array[48]
    b12 = data_array[49]
    b13 = data_array[50]
    b14 = data_array[51]
    b15 = data_array[52]
    #rnd3 = data_array[53]
    #rnd4 = data_array[54]
    return path+','+datetime+','+status+','+data_status+','+part_ct+','+hist_sum+','+part_con+','+bl+','+blth+','+std+','+max_std+','+p+','+tof_p+','+pump_life+','+width_std+','+ave_width+','+pops_flow+','+pump_fb+','+ld_temp+','+laser_fb+','+ld_mon+','+temp+','+batV+','+laser_current+','+flow_set+','+bl_start+','+th_mult+','+nbins+','+logmin+','+logmax+','+skip_save+','+min_peak_pts+','+max_peak_pts+','+raw_pts+','+b0+','+b1+','+b2+','+b3+','+b4+','+b5+','+b6+','+b7+','+b8+','+b9+','+b10+','+b11+','+b12+','+b13+','+b14+','+b15


def getGPS():
    SIM7600_GPS.send_at('AT+CGPS=1,1', 'OK', 0.1)
    answer, gps_info = SIM7600_GPS.send_at('AT+CGPSINFO', '+CGPSINFO: ', 0.1)
    gps_data = str(gps_info)
    gps_array = gps_data.split(",")
    for i in range(len(gps_array)):
        if gps_array[i] == "":
            gps_array[i] = "N/A"
    info = gps_array[0]
    info_array = info.split(": ") #Get rid of text in front
    info = info_array[0]
    try:
        lat = info_array[1]
    except IndexError:
        print("SIM7600 - IndexError in info_array")
    if lat == "":
        lat = "N/A"
    else:
        lat = str(float(lat)/100)
    n_s = gps_array[1]
    log = gps_array[2]
    if log != "N/A":
        log = str(float(log)/100)
    e_w = gps_array[3]
    date = gps_array[4]
    utc_time = gps_array[5]
    alt = gps_array[6]
    speed = gps_array[7]
    course = gps_array[8]
    return info, lat, n_s, log, e_w, utc_time, alt, speed, course


#Main function
def main():
    #Get date and time from RTC for directory and csv file name
    csvhour, csvminute, csvsecond, csvday, csvdate, csvmonth, csvyear = getTime()
    #Format date and time to strings
    csvstrDate = f"{csvyear:04d}-{csvmonth:02d}-{csvday:02d}"
    csvstrTime = f"{csvhour:02d}{csvminute:02d}{csvsecond:02d}"
    #creating data directory and new directory inside for every day
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    dir_name = csvstrDate
    if not os.path.exists(data_dir+"/"+dir_name):
        os.makedirs(data_dir+"/"+dir_name)
    #creating CSV file with headline
    csv_name = data_dir+"/"+dir_name+"/"+csvstrTime+".csv"
    csvFile = open(csv_name, "a")
    logging.info("writing csv headers")
    if POPS:
        if SIM:
            csvFile.write('Date'+','+'Time'+','+'BME680-Temperature[C]'+','+'BME680-Humidity[%]'+','+'Pressure[hPa]'+','+'Gas[Ohm]'+','+'PM1.0[mug/m3]'+','+'PM2.5[mug/m3]'+','+'PM4.0[mug/m3]'+','+'PM10.0[mug/m3]'+','+'SEN55-Humidity[%]'+','+'SEN55-Temperature[C]'+','+'VOC'+','+'NOx'+','+'CO2[ppm]'+','+'TVOC[ppb]'+','+'Latitude'+','+'N/S'+','+'Longitude'+','+'E/W'+','+'Altitude'+','+'Speed'+','+'POPS-DataPath'+','+'Datetime'+','+'Status'+','+'DataStatus'+','+'PartCt'+','+'HistSum'+','+'PartCon'+','+'BL'+','+'BLTH'+','+'STD'+','+'MaxSTD'+','+'P'+','+'TofP'+','+'PumpLife_hrs'+','+'WidthSTD'+','+'AveWidth'+','+'POPS_Flow'+','+'PumpFB'+','+'LDTemp'+','+'LaserFB'+','+'LD_Mon'+','+'Temp'+','+'BatV'+','+'Laser_Current'+','+'Flow_Set'+','+'BL_start'+','+'TH_Mult'+','+'nbins'+','+'logmin'+','+'logmax'+','+'Skip_Save'+','+'MinPeakPts'+','+'MaxPeakPts'+','+'RawPts'+','+'b0'+','+'b1'+','+'b2'+','+'b3'+','+'b4'+','+'b5'+','+'b6'+','+'b7'+','+'b8'+','+'b9'+','+'b10'+','+'b11'+','+'b12'+','+'b13'+','+'b14'+','+'b15\n')
        else:
            csvFile.write('Date'+','+'Time'+','+'BME680-Temperature[C]'+','+'BME680-Humidity[%]'+','+'Pressure[hPa]'+','+'Gas[Ohm]'+','+'PM1.0[mug/m3]'+','+'PM2.5[mug/m3]'+','+'PM4.0[mug/m3]'+','+'PM10.0[mug/m3]'+','+'SEN55-Humidity[%]'+','+'SEN55-Temperature[C]'+','+'VOC'+','+'NOx'+','+'CO2[ppm]'+','+'TVOC[ppb]'+','+'POPS-DataPath'+','+'Datetime'+','+'Status'+','+'DataStatus'+','+'PartCt'+','+'HistSum'+','+'PartCon'+','+'BL'+','+'BLTH'+','+'STD'+','+'MaxSTD'+','+'P'+','+'TofP'+','+'PumpLife_hrs'+','+'WidthSTD'+','+'AveWidth'+','+'POPS_Flow'+','+'PumpFB'+','+'LDTemp'+','+'LaserFB'+','+'LD_Mon'+','+'Temp'+','+'BatV'+','+'Laser_Current'+','+'Flow_Set'+','+'BL_start'+','+'TH_Mult'+','+'nbins'+','+'logmin'+','+'logmax'+','+'Skip_Save'+','+'MinPeakPts'+','+'MaxPeakPts'+','+'RawPts'+','+'b0'+','+'b1'+','+'b2'+','+'b3'+','+'b4'+','+'b5'+','+'b6'+','+'b7'+','+'b8'+','+'b9'+','+'b10'+','+'b11'+','+'b12'+','+'b13'+','+'b14'+','+'b15\n')
    else:
        if SIM:
            csvFile.write('Date'+','+'Time'+','+'BME680-Temperature[C]'+','+'BME680-Humidity[%]'+','+'Pressure[hPa]'+','+'Gas[Ohm]'+','+'PM1.0[mug/m3]'+','+'PM2.5[mug/m3]'+','+'PM4.0[mug/m3]'+','+'PM10.0[mug/m3]'+','+'SEN55-Humidity[%]'+','+'SEN55-Temperature[C]'+','+'VOC'+','+'NOx'+','+'CO2[ppm]'+','+'TVOC[ppb]'+','+'Latitude'+','+'N/S'+','+'Longitude'+','+'E/W'+','+'Altitude'+','+'Speed'+'\n')
        else:
            csvFile.write('Date'+','+'Time'+','+'BME680-Temperature[C]'+','+'BME680-Humidity[%]'+','+'Pressure[hPa]'+','+'Gas[Ohm]'+','+'PM1.0[mug/m3]'+','+'PM2.5[mug/m3]'+','+'PM4.0[mug/m3]'+','+'PM10.0[mug/m3]'+','+'SEN55-Humidity[%]'+','+'SEN55-Temperature[C]'+','+'VOC'+','+'NOx'+','+'CO2[ppm]'+','+'TVOC[ppb]'+'\n')
    csvFile.close()   

    #SEN55 initialization (reading data of SEN55 MUST be in the with scope)
    logging.info("setting up sensors")
    with LinuxI2cTransceiver('/dev/i2c-1') as i2c_transceiver:
        global device, ccs811
        device = Sen5xI2cDevice(I2cConnection(i2c_transceiver))
        device.device_reset()
        device.start_measurement()
        # Initialize CCS811 sensor
        ccs811 = adafruit_ccs811  # Replace with mock or real implementation
        logging.info("initializing CCS811 sensor")
        while waitCCS811():
            time.sleep(1)
        logging.info("sensor CC811 initialized")
        #Waiting for SEN55 to be ready
        logging.info("initializing SEN55 sensor")
        while waitSEN55():
            time.sleep(1)
        logging.info("sensor SEN55 initialized")

        #Activating DAQ buttons
        logging.info("initializing DAQ buttons")
        GPIO.add_event_detect(green, GPIO.RISING, callback=green_callback)
        GPIO.add_event_detect(red, GPIO.RISING, callback=red_callback)
        GPIO.add_event_detect(yellow, GPIO.RISING, callback=yellow_callback)
        logging.info("initialized DAQ buttons")

        #Loop for receiving sensor data
        logging.info("starting sensor main loop")
        while not exit_flag:
            start_time = time.time()#######################################START-TIME
            #Set LED-GPIO LOW
            GPIO.output(led, GPIO.LOW)
            #Write menu to LCD
            if not csv_flag and not sanity_flag:
                writeLCD("G=Start - R=Stop", "Y=Sanity - B=End")
            #Get date and time from RTC
            hour, minute, second, day, date, month, year = getTime()
            #Format date and time to strings
            strDate = f"{year:04d}-{month:02d}-{day:02d}"
            strTime = f"{hour:02d}:{minute:02d}:{second:02d}"
            #Get sensor data from BME680
            temp680, hum680, pres, gas = getBME680()
            #Get sensor data from SEN55
            mc1p0, mc2p5, mc4p0, mc10p0, hum55, temp55, voc, nox = getSEN55()
            #Get sensor data from CCS811
            try:
                co2, tvoc = getCCS811()
            except TypeError as tyErr:
                logging.error(f"CCS811: TypeError: cannot unpack non-iterable NoneType object")
                print("CCS811: TypeError: cannot unpack non-iterable NoneType object")
            #Get sensor data from POPS and clean it
            if POPS:
                pops_data = udp_pops.getPOPS()
                clean_pops_data = cleanPopsData(pops_data)
            #Get GPS data from SIM7600
            if SIM:
                info, lat, n_s, log, e_w, utc_time, alt, speed, course = getGPS()
            
            if csv_flag:
                #LED on, when writing in CSV
                GPIO.output(led, GPIO.HIGH)
                writeLCD("DAQ running...", "Red to stop!")
                #Write data to csv file
                csvFile = open(csv_name, "a")
                if POPS:
                    if SIM:
                        csvFile.write(strDate+','+strTime+','+str(temp680)+','+str(hum680)+','+str(pres)+','+str(gas)+','+str(mc1p0)+','+str(mc2p5)+','+str(mc4p0)+','+str(mc10p0)+','+str(hum55)+','+str(temp55)+','+str(voc)+','+str(nox)+','+str(co2)+','+str(tvoc)+','+lat+','+n_s+','+log+','+e_w+','+alt+','+speed+','+clean_pops_data+'\n')
                    else:
                        csvFile.write(strDate+','+strTime+','+str(temp680)+','+str(hum680)+','+str(pres)+','+str(gas)+','+str(mc1p0)+','+str(mc2p5)+','+str(mc4p0)+','+str(mc10p0)+','+str(hum55)+','+str(temp55)+','+str(voc)+','+str(nox)+','+str(co2)+','+str(tvoc)+','+clean_pops_data+'\n')
                else:
                    if SIM:
                        csvFile.write(strDate+','+strTime+','+str(temp680)+','+str(hum680)+','+str(pres)+','+str(gas)+','+str(mc1p0)+','+str(mc2p5)+','+str(mc4p0)+','+str(mc10p0)+','+str(hum55)+','+str(temp55)+','+str(voc)+','+str(nox)+','+str(co2)+','+str(tvoc)+','+lat+','+n_s+','+log+','+e_w+','+alt+','+speed+'\n')
                    else:
                        csvFile.write(strDate+','+strTime+','+str(temp680)+','+str(hum680)+','+str(pres)+','+str(gas)+','+str(mc1p0)+','+str(mc2p5)+','+str(mc4p0)+','+str(mc10p0)+','+str(hum55)+','+str(temp55)+','+str(voc)+','+str(nox)+','+str(co2)+','+str(tvoc)+'\n')
                csvFile.close()
                
            if sanity_flag:
                GPIO.output(led, GPIO.LOW)
                sanityCheck(strDate, strTime, temp680, hum680, pres, gas, mc1p0, mc2p5, mc4p0, mc10p0, hum55, temp55, voc, nox, co2, tvoc)

            end_time = time.time()##########################################STOP-TIME
            elapsed_time = end_time-start_time
            #Sleep to make one loop last exactly 1.0 seconds
            if elapsed_time < 1:
                sleep_time = 1 - elapsed_time
                time.sleep(sleep_time)            


#Start of the code
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("starting main")
    #Enable SIM7600 GPS
    if SIM:
        writeLCD("SIM not ready", "Waiting ...")
        logging.info("running with SIM ")
        SIM7600_GPS.power_on(SIM7600_GPS.power_key)
    #Initialize POPS communication
    if POPS:
        logging.info("running with POPS ")
        udp_pops.init()
    #main program
    main()
    #Disable SIM7600 GPS
    if SIM:
        SIM7600_GPS.power_down(SIM7600_GPS.power_key)
    #End with Message on LCD
    writeLCD("Program", "terminated!")
    #Turn off LED
    GPIO.output(led, GPIO.LOW)
