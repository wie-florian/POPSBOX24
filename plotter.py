#Source Matplotlib: https://matplotlib.org/ --- AccessDate: 03.04.2024
#Source Matplotlib: https://medium.com/@basubinayak05/python-data-visualization-day-2-fcce236549ba --- AccessDate: 15.05.2024
#Source tkinter: https://www.python-lernen.de/tkinter-gui.htm --- AccessDate: 10.04.2024
#Source tkinter: https://www.activestate.com/resources/quick-reads/how-to-position-widgets-in-tkinter/ --- AccessDate: 11.04.2024
#Source tkinter: https://www.tutorialspoint.com/creating-a-browse-button-with-tkinter --- AccessDate: 17.04.2024
#Source tkinter: https://www.activestate.com/resources/quick-reads/how-to-add-images-in-tkinter/ --- AccessDate: 23.04.2024
#Source tkinter: https://www.tutorialspoint.com/python/tk_radiobutton.htm --- AccessDate: 25.04.2024
#Source Pandas: https://pandas.pydata.org/ --- AccessDate: 11.04.2024
#written by: Peter Pallnstorfer

### All values in csv:
### Date,Time,BME680-Temperature[C],BME680-Humidity[%],Pressure[hPa],Gas[Ohm],
### PM1.0[mug/m3],PM2.5[mug/m3],PM4.0[mug/m3],PM10.0[mug/m3],SEN55-Humidity[%],
### SEN55-Temperature[C],VOC,NOx,CO2[ppm],TVOC[ppb],Latitude,N/S,Longitude,E/W,
### Altitude,Speed,POPS-DataPath,Datetime,Status,DataStatus,PartCt,HistSum,PartCon,
### BL,BLTH,STD,MaxSTD,P,TofP,PumpLife_hrs,WidthSTD,AveWidth,POPS_Flow,PumpFB,LDTemp,
### LaserFB,LD_Mon,Temp,BatV,Laser_Current,Flow_Set,BL_start,TH_Mult,nbins,logmin,
### logmax,Skip_Save,MinPeakPts,MaxPeakPts,RawPts,b0,b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm, Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import sys
import matplotlib.dates as mdates
import math

#path csv files
#csv_path = "data/13_29_37_Dornbach.csv"
csv_path = ""
#drone_path = "data/DJIFlightRecord_2024-03-22_aircraft.csv"
drone_path = ""
#Bool variable for Visualize Button
visual = False
#Bool variable for Drone File
drone = False

#Number of ticks on X and Y axis
numTicksX = 10
numTicksY = 7
#Rotation in degrees of time ticks
rot = 45

############################################################################ Read data functions
def readColumn(string):
    #Get single column from box CSV file
    try:
        data = pd.read_csv(csv_path)
        col = data[string]
        return col
    except pd.errors.ParserError:
        print("Data file in wrong format!")
        sys.exit()
    
def readDroneData(index1, index2):
    #Get data from drone CSV file (time and height)
    time = []
    height = []
    with open(drone_path, 'r') as file:
        for line in file:
            row = line.strip().split(';')
            try:
                time.append(row[index1])
                height.append(row[index2])
            except IndexError:
                print("Drone file in wrong format!")
                sys.exit()
    return time, height

############################################################################ Callback functions from Buttons
def getFilePath():
    #Get file path for box csv from user
    global csv_path
    csv_path = filedialog.askopenfilename()
    label_path.config(text=csv_path)
    
def getFilePath2():
    #Get file path for drone csv from user
    global drone_path
    drone_path = filedialog.askopenfilename()
    label_path2.config(text=drone_path)
    
def visButton():
    root.destroy()
    global visual
    visual = True

############################################################################ Function to get the mean of data over a stepsize in seconds
def avgData(time, data, step):
    avg_data = []
    avg_time = []
    cnt = 0
    sum_avgT = 0
    sum_avgD = 0
    start = time[0]
    end = time[-1]
    for i in range(len(time)):
        stop = start + step
        sum_avgT += time[i]
        sum_avgD += data[i]
        cnt += 1
        if time[i] > stop:
            avg_time.append(sum_avgT / cnt)
            avg_data.append(sum_avgD / cnt)
            start = stop
            cnt = 0
            sum_avgT = 0
            sum_avgD = 0
    return avg_time, avg_data
# Old mean function, takes mean over stepsize in cells
#     cnt = 0
#     cnt_elem = 0
#     sum_avg = 0
#     avg_data = []
#     for element in data:
#         sum_avg += element
#         cnt += 1
#         if cnt == step:
#             avg_data.append(sum_avg/cnt)
#             cnt_elem += 1
#             sum_avg = 0
#             cnt = 0
#     if cnt > 0:
#         avg_data.append(sum_avg/cnt)    
#     return avg_data

############################################################################ Functions to convert data into the desired format
#Takes a time string (HH:MM:SS) as an argument, calculates and returns the total seconds
def timeToSeconds(time):
    #Convert into list if time is a single string
    if type(time) == str:
        time = [time]
    seconds = []
    for element in time:
        hour, minute, second = element.split(':')
        hour = float(hour)
        minute = float(minute)
        second = float(second)
        seconds.append(hour*3600 + minute*60 + second)
    return seconds

#Takes total seconds as an argument, calculates and returns it as time string (HH:MM:SS)
def secondsToTime(time):
    #Convert into list if time is a single string
    if type(time) == str:
        time = [time]
    times = []
    for element in time:
        hour = int(element/3600)
        minute = int((element%3600)/60)
        second = round(element%60)
        if hour < 10:
            hour = str(hour)
            hour = "0"+hour
        if minute < 10:
            minute = str(minute)
            minute = "0"+minute
        if second < 10:
            second = str(second)
            second = "0"+second
        times.append(str(hour)+":"+str(minute)+":"+str(second))
    return times

#Converts DroneTime from "H:MM:SS,SS PM" to "HH:MM:SS" and returns it as string
def convertDroneTime(time):
    times = []
    for element in time:
        _time, pm_am = element.split(' ')
        hour, minute, sec_hun = _time.split(':')
        second, hundredth = sec_hun.split(',')
        hour = int(hour)
        minute = int(minute)
        second = int(second)
        if 'PM' in pm_am:
            hour += 12
        if hour < 10:
            hour = str(hour)
            hour = "0"+hour
        if minute < 10:
            minute = str(minute)
            minute = "0"+minute
        if second < 10:
            second = str(second)
            second = "0"+second
        times.append(str(hour)+":"+str(minute)+":"+str(second))
    return times

#Converts DroneHeight to have . as comma and not ,
#Returns it as a string
def convertDroneHeight(height):
    heights = []
    for element in height:
        if ',' in element:
            meter, mm = element.split(',')
        else:
            meter = element
            mm = 0
        heights.append(float(str(meter)+"."+str(mm)))
    return heights

#Takes a time array and corrects the time (for example from UTC to UTC+1)
def correctTime(time, time_add):
    time = timeToSeconds(time)
    times = []
    for element in time:
        times.append(element + (3600*time_add))
    times = secondsToTime(times)
    return times

#Subtract out lower PM values from higher ones
#Takes PM1, PM2.5, PM4 and PM10 as argument
#Returns PM1, PM2.5-1, PM4-2.5, PM10-4
def correctPM(pm1, pm2, pm4, pm10):
    _pm1 = []
    _pm2 = []
    _pm4 = []
    _pm10 = []
    for i in range(len(pm1)):
        pm10[i] -= pm4[i]
        pm4[i] -= pm2[i]
        pm2[i] -= pm1[i]
        _pm1.append(pm1[i])
        _pm2.append(pm2[i])
        _pm4.append(pm4[i])
        _pm10.append(pm10[i])
    return _pm1, _pm2, _pm4, _pm10

#Takes POPS time as argument which is in the format of total seconds of the day
#Returns the time as string in the format "HH:MM:SS"
#Also corrects the time with offset
def convertPOPSTime(time):
    times = []
    for element in time:
        element = int(element) - 14 #POPS time correction (-14 seconds)
        hour = int(element/3600)
        minute = int((element%3600)/60)
        second = int(element%60)
        times.append(str(hour)+":"+str(minute)+":"+str(second))
    return times
    
############################################################################ Plot function BME680
def plotBME(sensor, string1, time1, data1, string2, time2, data2, string3, time3, data3, string4, time4, data4, string_alt, time_drone, height_drone):
    if drone:
        subp = 3
    else:
        subp = 2
    fig, ax = plt.subplots(subp, 1, sharex=True)
    #Plot Temperature and Humidity of BME680 over Time
    ax[0].set_title(sensor)
    ax[0].set_ylabel(string1)
    ax[0].plot(time1, data1, label=string1)
    ax[0].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[0].yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show second y axis
    ax0 = ax[0].twinx()
    ax0.set_ylabel(string2)
    ax0.plot(time2, data2, label=string2, color="C1")
    ax0.yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show common legend
    h00, l00 = ax[0].get_legend_handles_labels()
    h01, l01 = ax0.get_legend_handles_labels()
    ax[0].legend(h00+h01, l00+l01, loc="lower right")
    
    #Plot Pressure and Gas Resistance of BME680 over Time
    ax[1].set_ylabel(string3)
    ax[1].plot(time3, data3, label=string3)
    ax[1].tick_params(axis="x", rotation=rot)
    ax[1].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[1].yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show second y axis
    ax1 = ax[1].twinx()
    ax1.set_ylabel(string4)
    ax1.plot(time4, data4, label=string4, color="C1")
    ax1.yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show common legend
    h10, l10 = ax[1].get_legend_handles_labels()
    h11, l11 = ax1.get_legend_handles_labels()
    ax[1].legend(h10+h11, l10+l11, loc="lower right")
    if not drone:
        ax[1].set_xlabel("Time")
    
    #Plot Drone Altitude over Time
    if drone:
        ax[2].set_xlabel("Time")
        ax[2].set_ylabel(string_alt)
        ax[2].plot(time_drone, height_drone, label=string_alt)
        ax[2].tick_params(axis="x", rotation=rot)
        ax[2].xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax[2].yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax[2].legend(loc="lower right")
        
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))


############################################################################ Plot function SEN55 and POPS
def plotSEN_POPS(sensor, string1, time1, data1, string2, time2, data2, string3, time3, data3, string_alt, time_drone, height_drone):
    if drone:
        subp = 3
    else:
        subp = 2
    fig, ax = plt.subplots(subp, 1, sharex=True)
    #Plot Data over Time
    ax[0].set_title(sensor)
    ax[0].set_ylabel(string1)
    ax[0].plot(time1, data1, label=string1)
    ax[0].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[0].yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show second y axis
    ax0 = ax[0].twinx()
    ax0.set_ylabel(string2)
    ax0.plot(time2, data2, label=string2, color="C1")
    ax0.yaxis.set_major_locator(MaxNLocator(numTicksY))
    #Show common legend
    h00, l00 = ax[0].get_legend_handles_labels()
    h01, l01 = ax0.get_legend_handles_labels()
    ax[0].legend(h00+h01, l00+l01, loc="lower right")
    
    #Plot Data over Time
    ax[1].set_ylabel(string3)
    ax[1].plot(time3, data3, label=string3)
    ax[1].tick_params(axis="x", rotation=rot)
    ax[1].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[1].yaxis.set_major_locator(MaxNLocator(numTicksY))
    ax[1].legend(loc="lower right")
    
    if not drone:
        ax[1].set_xlabel("Time")
        
    #Plot Drone Altitude over Time
    if drone:
        ax[2].set_xlabel("Time")
        ax[2].set_ylabel(string_alt)
        ax[2].plot(time_drone, height_drone, label=string_alt)
        ax[2].tick_params(axis="x", rotation=rot)
        ax[2].xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax[2].yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax[2].legend(loc="lower right")
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

############################################################################ Plot function SEN55 - PM Values
def plotPM(sensor, string1, time1, data1, string2, time2, data2, string3, time3, data3, string4, time4, data4, string_alt, time_drone, height_drone):
    if drone:
        fig, ax = plt.subplots(2, 1, sharex=True)
        #Plot PM Values over Time
        ax[0].set_title(sensor)
        ax[0].set_ylabel("PM[mug/m3]")
        ax[0].plot(time1, data1, label=string1)
        ax[0].plot(time2, data2, label=string2)
        ax[0].plot(time3, data3, label=string3)
        ax[0].plot(time4, data4, label=string4)
        ax[0].xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax[0].yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax[0].legend(loc="lower right")
        
        #Plot Drone Altitude over Time
        ax[1].set_xlabel("Time")
        ax[1].set_ylabel(string_alt)
        ax[1].plot(time_drone, height_drone, label=string_alt)
        ax[1].tick_params(axis="x", rotation=rot)
        ax[1].xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax[1].yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax[1].legend(loc="lower right")
        
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
    else:
        fig, ax = plt.subplots()
        #Plot PM Values over Time
        ax.set_title(sensor)
        ax.set_ylabel("PM[mug/m3]")
        ax.set_xlabel("Time")
        ax.plot(time1, data1, label=string1)
        ax.plot(time2, data2, label=string2)
        ax.plot(time3, data3, label=string3)
        ax.plot(time4, data4, label=string4)
        ax.tick_params(axis="x", rotation=rot)
        ax.xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax.yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax.legend(loc="lower right")
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        
############################################################################ Plot function CCS811
def plotCCS(sensor, string1, time1, data1, string2, time2, data2, string_alt, time_drone, height_drone):
    if drone:
        subp = 3
    else:
        subp = 2
    fig, ax = plt.subplots(subp, 1, sharex=True)
    #Plot CO2 over Time
    ax[0].set_title(sensor)
    ax[0].set_ylabel(string1)
    ax[0].plot(time1, data1, label=string1)
    ax[0].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[0].yaxis.set_major_locator(MaxNLocator(numTicksY))
    ax[0].legend(loc="lower right")
    
    #Plot TVOC over Time
    ax[1].set_ylabel(string2)
    ax[1].plot(time2, data2, label=string2)
    ax[1].tick_params(axis="x", rotation=rot)
    ax[1].xaxis.set_major_locator(MaxNLocator(numTicksX))
    ax[1].yaxis.set_major_locator(MaxNLocator(numTicksY))
    ax[1].legend(loc="lower right")
    
    #Plot Drone Altitude over Time
    if drone:
        ax[2].set_xlabel("Time")
        ax[2].set_ylabel(string_alt)
        ax[2].plot(time_drone, height_drone, label=string_alt)
        ax[2].tick_params(axis="x", rotation=rot)
        ax[2].xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax[2].yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax[2].legend(loc="lower right")
        
    if not drone:
        ax[1].set_xlabel("Time")
        
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

############################################################################ Plot function POPS for Aerosol HeatMap
def plotHeatMap(b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, flow, time, string_alt, time_drone, height_drone):
    #Units of variables
    #b0-b15   #/s
    #flow   cm3/s
    #c0-c15   #/cm3
    
    #Bin #   1   2   3   4   5   6   7   8   9  10  11   12   13   14   15   16
    #Lower 115 125 135 150 165 185 210 250 350 475 575  855 1220 1530 1990 2585 nm
    #Upper 125 135 150 165 185 210 250 350 475 575 855 1220 1530 1990 2585 3370 nm
    
    #Normalizing bin width with log function
    dlogDp0 = math.log(125) - math.log(115)
    dlogDp1 = math.log(135) - math.log(125) 
    dlogDp2 = math.log(150) - math.log(135) 
    dlogDp3 = math.log(165) - math.log(150) 
    dlogDp4 = math.log(185) - math.log(165) 
    dlogDp5 = math.log(210) - math.log(185) 
    dlogDp6 = math.log(250) - math.log(210) 
    dlogDp7 = math.log(350) - math.log(250) 
    dlogDp8 = math.log(475) - math.log(350) 
    dlogDp9 = math.log(575) - math.log(475) 
    dlogDp10 = math.log(855) - math.log(575) 
    dlogDp11 = math.log(1220) - math.log(855) 
    dlogDp12 = math.log(1530) - math.log(1220) 
    dlogDp13 = math.log(1990) - math.log(1530) 
    dlogDp14 = math.log(2585) - math.log(1990) 
    dlogDp15 = math.log(3370) - math.log(2585) 
    nc0 = []
    nc1 = []
    nc2 = []
    nc3 = []
    nc4 = []
    nc5 = []
    nc6 = []
    nc7 = []
    nc8 = []
    nc9 = []
    nc10 = []
    nc11 = []
    nc12 = []
    nc13 = []
    nc14 = []
    nc15 = []

    #Calculate normalized concentration for each bin (b/flow = particle concentration) (particle concentration/dlogDp = normalized concentration)
    #Normalized concentration is independet of the bin width
    for i in range(len(flow)):
        nc0.append((b0[i]/flow[i])/dlogDp0)
        nc1.append((b1[i]/flow[i])/dlogDp1)
        nc2.append((b2[i]/flow[i])/dlogDp2)
        nc3.append((b3[i]/flow[i])/dlogDp3)
        nc4.append((b4[i]/flow[i])/dlogDp4)
        nc5.append((b5[i]/flow[i])/dlogDp5)
        nc6.append((b6[i]/flow[i])/dlogDp6)
        nc7.append((b7[i]/flow[i])/dlogDp7)
        nc8.append((b8[i]/flow[i])/dlogDp8)
        nc9.append((b9[i]/flow[i])/dlogDp9)
        nc10.append((b10[i]/flow[i])/dlogDp10)
        nc11.append((b11[i]/flow[i])/dlogDp11)
        nc12.append((b12[i]/flow[i])/dlogDp12)
        nc13.append((b13[i]/flow[i])/dlogDp13)
        nc14.append((b14[i]/flow[i])/dlogDp14)
        nc15.append((b15[i]/flow[i])/dlogDp15)
    
    data = pd.DataFrame({
        'nc0': nc0,
        'nc1': nc1,
        'nc2': nc2,
        'nc3': nc3,
        'nc4': nc4,
        'nc5': nc5,
        'nc6': nc6,
        'nc7': nc7,
        'nc8': nc8,
        'nc9': nc9,
        'nc10': nc10,
        'nc11': nc11,
        'nc12': nc12,
        'nc13': nc13,
        'nc14': nc14,
        'nc15': nc15
    },)

    #Exchange data values that are 0 with 0.1 (to have no blank spaces in the heat map)
    for column in data:
        for index, value in enumerate(data[column]):
            if value == 0:
                data.at[index, column] = 0.1
    
    #Set time as index of pandas data frame
    data.index = time

    #Get matrix in to right shape, transpose and mirror rows
    data = data.transpose()
    data = data[::-1]
    
    #Get number of bins and timestamps
    num_bins = len(data)
    num_times = len(time)
    
    #Get equally distributed timestamps for the x axis of the HeatMap 
    timestamps = 8
    step_time = num_times//timestamps
    if step_time == 0:
        step_time = 1
    display_time = []
    for i in range(num_times):
        if i%step_time == 0:
            display_time.append(time[i])
    
    #Find min and max value of data to get log boundaries
    lower_log = data.values.min()
    upper_log = data.values.max()
    upper_log = int(upper_log / 1000)
    upper_log = (upper_log + 1) * 1000
    
    #Bins for y axis
    bins = ["115-125", "125-135", "135-150", "150-165", "165-185", "185-210", "210-250", "250-350", "350-475", "475-575", "575-855", "855-1220", "1220-1530", "1530-1990", "1990-2585", "2585-3370"]
    bins = bins[::-1]
    
    if drone:
        fig, ax1 = plt.subplots()
        
        #Show Aerosol Heat Map
        hmap = ax1.imshow(data, aspect='auto', cmap='RdYlBu_r', norm=LogNorm(lower_log, upper_log))

        #Set tick labels for x axis (not used, using time axis of drone altitude plot)
        #ax1.set_xticks(range(0, num_times, step_time), display_time, rotation=rot)
        #Set empty ticks to prevent showing indices
        ax1.set_xticks([])
        #Set tick labels for y axis
        ax1.set_yticks(range(num_bins), bins)
        #Set labels for x and y axis
        #ax1.set_xlabel('Time')
        ax1.set_ylabel('Aerosol Optical Diameters [nm]')
        #Set title, turn on colobar and grid
        ax1.set_title('Aerosol Heat Map')
        plt.colorbar(hmap, label='dN/dlogDp [#/cm3]')
        plt.grid(hmap)
        
        #Position drone graph exactly below
        divider = make_axes_locatable(ax1)
        ax2 = divider.append_axes("bottom", size="100%", pad=0.7)
        
        ################################################Align time axis - start
        start = str(time[0])
        end = str(time[-1])
        #Add height_drone zeros, if time_drone limits are outside time
        start = timeToSeconds(start)
        end = timeToSeconds(end)
        dts, start_drone = str(time_drone[0]).split(' ')
        dte, end_drone = str(time_drone[-1]).split(' ')
        start_drone = timeToSeconds(start_drone)
        end_drone = timeToSeconds(end_drone)
        if start[0] < start_drone[0]:
            #Add Datetimes and zeros in front
            diff = start_drone[0] - start[0]
            h_add = []
            t_add = []
            for i in range(int(diff)):
                h_add.append(0)
                t_add.append(start[0]+i)
            t_add = secondsToTime(t_add)
            t_add = pd.to_datetime(t_add, format='%H:%M:%S')
            t_add = pd.DatetimeIndex(t_add)
            
            #Add arrays together
            time_drone = t_add.append(time_drone)
            height_drone = h_add + height_drone
            
        if end[0] > end_drone[0]:
            #Add Datetimes and zeros behind
            diff = end[0] - end_drone[0]
            h_add = []
            t_add = []
            for i in range(int(diff)):
                h_add.append(0)
                t_add.append(end_drone[0]+i)
            t_add = secondsToTime(t_add)
            t_add = pd.to_datetime(t_add, format='%H:%M:%S')
            t_add = pd.DatetimeIndex(t_add)
            
            #Add arrays together
            time_drone = time_drone.append(t_add)
            height_drone = height_drone + h_add
            
        #Get time_drone limits, if they are inside time
        lim_start = 0
        lim_end = -1
        start = secondsToTime(start)
        end = secondsToTime(end)
        for i, timestamp in enumerate(time_drone):
            if start[0] in str(timestamp):
                lim_start = i
            if end[0] in str(timestamp):
                lim_end = i
        
        #Set lim_start to the right value, if start is later then end_drone
        if timeToSeconds(start[0]) > end_drone:
            for i, timestamp in enumerate(time_drone):
                if start[0] in str(timestamp):
                    lim_start = i

        #Set limits for time axis
        ax2.set_xlim(time_drone[lim_start], time_drone[lim_end])
        ################################################Align time axis - end
        
        #Standard settings for plot over time
        ax2.set_xlabel("Time")
        ax2.set_ylabel(string_alt)
        ax2.plot(time_drone, height_drone, label=string_alt)
        ax2.tick_params(axis="x", rotation=rot)
        ax2.xaxis.set_major_locator(MaxNLocator(numTicksX))
        ax2.yaxis.set_major_locator(MaxNLocator(numTicksY))
        ax2.legend(loc="lower right")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    
    else:
        fig, ax = plt.subplots(1, 1)
        #Show Aerosol Heat Map
        hmap = ax.imshow(data, aspect='auto', cmap='RdYlBu_r', norm=LogNorm(lower_log, upper_log))
        
        #Set tick labels for x axis
        ax.set_xticks(range(0, num_times, step_time), display_time, rotation=rot)
        
        #Set tick labels for y axis
        ax.set_yticks(range(num_bins), bins)

        #Set labels for x and y axis
        ax.set_xlabel('Time')
        ax.set_ylabel('Aerosol Optical Diameters [nm]')
        
        #Set title, turn on colobar and grid
        ax.set_title('Aerosol Heat Map')
        plt.colorbar(hmap, label='dN/dlogDp [#/cm3]')
        plt.grid(hmap)
    
###############################                    Start                    ###############################
###############################                    of                       ###############################
###############################                    the                      ###############################
###############################                    code                     ###############################

############################################################################ tkinter window
root = tk.Tk()
root.title("Lab on a Drone")
root.configure(bg="white")

#Labels
label_menu = tk.Label(root, text="Menü-Datenvisualisierung", fg="black", bg="white", font=('times', 35, 'bold'))
label_menu.place(x=10, y=10)
label_step = tk.Label(root, text="Stepsize:", fg="black", bg="white", font=('times', 18))
label_step.place(x=10, y=80)
label_path = tk.Label(root, text="no path", fg="black", bg="white", font=('times', 15, 'italic'))
label_path.place(x=175, y=130)
label_path2 = tk.Label(root, text="no path", fg="black", bg="white", font=('times', 15, 'italic'))
label_path2.place(x=175, y=180)

#Input field for stepsize
entry = tk.StringVar()
box = tk.Entry(root, textvariable=entry, font=('times', 15), justify="right").place(x=175, y=83)

#FilePath Buttons
button_path = tk.Button(root, text="Data-CSV Path:", font=('times', 15), command=getFilePath)
button_path.place(x=10, y=125)
button_path2 = tk.Button(root, text="Drone-CSV Path:", font=('times', 15), command=getFilePath2)
button_path2.place(x=10, y=175)

#Radiobuttons to choose time format
var = tk.IntVar()
r0 = tk.Radiobutton(root, text="UTC-1", variable=var, value=-1, command=None)
r0.place(x=10, y=275)
r1 = tk.Radiobutton(root, text="UTC-Time", variable=var, value=0, command=None)
r1.place(x=10, y=300)
r2 = tk.Radiobutton(root, text="UTC+1 (Winter)", variable=var, value=1, command=None)
r2.place(x=10, y=325)
r3 = tk.Radiobutton(root, text="UTC+2 (Summer)", variable=var, value=2, command=None)
r3.place(x=10, y=350)

#Checkbox if drone file is used
boool = tk.BooleanVar()
checkbox = tk.Checkbutton(root, text="Using Drone file?", variable=boool, command=None)
checkbox.place(x=10, y=230)

#Visualize Button
button_vis = tk.Button(root, text="Visualize Data", fg="black", font=('times', 25), command=visButton)
button_vis.place(x=175, y=230)

#Image - Lab on a Drone
image_path = "popsbox.PNG"
try:
    image = Image.open(image_path)
    image = image.resize((217, 217))
    tk_image = ImageTk.PhotoImage(image)
    piclabel = tk.Label(image=tk_image)
    piclabel.place(x=175, y=310)
except FileNotFoundError:
    print("No image found with that name")

#Keeps GUI running
root.mainloop()

############################################################################ Get info from user input (tkinter)
#Stepsize from entry box
stepsize = 0
value = entry.get()
if str(value).isdigit():
    stepsize = int(entry.get())
if stepsize < 1:
    stepsize = 1
if stepsize > 2500:
    stepsize = 2500
#Time from radiobuttons
time_add = var.get()
#Is Drone file being used? Info from Checkbutton
drone = boool.get()

############################################################################ Get all important data from box csv
try:
    time_box = readColumn("Time")
    #Correct the box time based on user input UTC+0/1/2
    time_box = correctTime(time_box, time_add)
    time_box = timeToSeconds(time_box)
    #BME680
    bmeT = readColumn("BME680-Temperature[C]")
    bmeH = readColumn("BME680-Humidity[%]")
    bmeP = readColumn("Pressure[hPa]")
    bmeG = readColumn("Gas[Ohm]")
    #SEN55
    senT = readColumn("SEN55-Temperature[C]")
    senH = readColumn("SEN55-Humidity[%]")
    pm1_0 = readColumn("PM1.0[mug/m3]")
    pm2_5 = readColumn("PM2.5[mug/m3]")
    pm4_0 = readColumn("PM4.0[mug/m3]")
    pm10_0 = readColumn("PM10.0[mug/m3]")
    pm1_0, pm2_5, pm4_0, pm10_0 = correctPM(pm1_0, pm2_5, pm4_0, pm10_0)
    voc = readColumn("VOC")
    #CCS811
    co2 = readColumn("CO2[ppm]")
    tvoc = readColumn("TVOC[ppb]")
    #POPS
    time_pops = readColumn("Datetime")
    time_pops = convertPOPSTime(time_pops)
    time_pops = correctTime(time_pops, time_add)
    time_pops = timeToSeconds(time_pops)
    partCon = readColumn("PartCon")
    partCt = readColumn("PartCt")
    pressure_pops = readColumn("P")
    b0 = readColumn("b0")
    b1 = readColumn("b1")
    b2 = readColumn("b2")
    b3 = readColumn("b3")
    b4 = readColumn("b4")
    b5 = readColumn("b5")
    b6 = readColumn("b6")
    b7 = readColumn("b7")
    b8 = readColumn("b8")
    b9 = readColumn("b9")
    b10 = readColumn("b10")
    b11 = readColumn("b11")
    b12 = readColumn("b12")
    b13 = readColumn("b13")
    b14 = readColumn("b14")
    b15 = readColumn("b15")
    hist_pops = [b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15]
    flow_pops = readColumn("POPS_Flow")
except FileNotFoundError:
    print("No box file chosen!")
    sys.exit()

############################################################################ Get timestamps and height from drone csv file and format the data
time_index = 1
height_index = 6
if drone:
    try:
        time_drone, height_drone = readDroneData(time_index, height_index)
        #Get rid off headline
        time_drone = time_drone[1:]
        height_drone = height_drone[1:]
        #Get drone time into same format as box time
        time_drone = convertDroneTime(time_drone)
        time_drone = timeToSeconds(time_drone)
        #Convert drone times and heights and get mean to have 1 sec interval like box data
        height_drone = convertDroneHeight(height_drone)
        time_drone, height_drone = avgData(time_drone, height_drone, 1)
    except FileNotFoundError:
        print("No drone file chosen!")
        sys.exit()
else:
    time_drone = 0
    height_drone = 0

############################################################################ Get the mean of data by stepsize
#BME680
t0, bmeT = avgData(time_box, bmeT, stepsize)
t1, bmeH = avgData(time_box, bmeH, stepsize)
t2, bmeP = avgData(time_box, bmeP, stepsize)
t3, bmeG = avgData(time_box, bmeG, stepsize)

#SEN55
t4, senT = avgData(time_box, senT, stepsize)
t5, senH = avgData(time_box, senH, stepsize)
t6, pm1_0 = avgData(time_box, pm1_0, stepsize)
t7, pm2_5 = avgData(time_box, pm2_5, stepsize)
t8, pm4_0 = avgData(time_box, pm4_0, stepsize)
t9, pm10_0 = avgData(time_box, pm10_0, stepsize)
t10, voc = avgData(time_box, voc, stepsize)

#CCS811
t11, co2 = avgData(time_box, co2, stepsize)
time_box, tvoc = avgData(time_box, tvoc, stepsize)

#POPS
t12, partCon = avgData(time_pops, partCon, stepsize)
t13, partCt = avgData(time_pops, partCt, stepsize)
t14, pressure_pops = avgData(time_pops, pressure_pops, stepsize)
t15, b0 = avgData(time_pops, b0, stepsize)
t16, b1 = avgData(time_pops, b1, stepsize)
t17, b2 = avgData(time_pops, b2, stepsize)
t18, b3 = avgData(time_pops, b3, stepsize)
t19, b4 = avgData(time_pops, b4, stepsize)
t20, b5 = avgData(time_pops, b5, stepsize)
t21, b6 = avgData(time_pops, b6, stepsize)
t22, b7 = avgData(time_pops, b7, stepsize)
t23, b8 = avgData(time_pops, b8, stepsize)
t24, b9 = avgData(time_pops, b9, stepsize)
t25, b10 = avgData(time_pops, b10, stepsize)
t26, b11 = avgData(time_pops, b11, stepsize)
t27, b12 = avgData(time_pops, b12, stepsize)
t28, b13 = avgData(time_pops, b13, stepsize)
t29, b14 = avgData(time_pops, b14, stepsize)
t30, b15 = avgData(time_pops, b15, stepsize)
time_pops, flow_pops = avgData(time_pops, flow_pops, stepsize)

############################################################################ Convert all times to a datetime object
time_box = secondsToTime(time_box)
time_pops = secondsToTime(time_pops)
time_box = pd.to_datetime(time_box, format='%H:%M:%S')
time_pops = pd.to_datetime(time_pops, format='%H:%M:%S')
if drone:
    time_drone = secondsToTime(time_drone)
    time_drone = pd.to_datetime(time_drone, format='%H:%M:%S')

############################################################################ Call plotting functions
#Plot BME680 Data
plotBME("BME680", "Temperature[C]", time_box, bmeT, "Humidity[%]", time_box, bmeH, "Pressure[hPa]", time_box, bmeP, "Gas[Ohm]", time_box, bmeG, "Drone-Altitude[m]", time_drone, height_drone)

#Plot SEN55 Data
plotSEN_POPS("SEN55", "Temperature[C]", time_box, senT, "Humidity[%]", time_box, senH, "VOC", time_box, voc, "Drone-Altitude[m]", time_drone, height_drone)
plotPM("SEN55", "PM1.0[mug/m3]", time_box, pm1_0, "PM2.5-1.0[mug/m3]", time_box, pm2_5, "PM4.0-2.5[mug/m3]", time_box, pm4_0, "PM10.0-4.0[mug/m3]", time_box, pm10_0, "Drone-Altitude[m]", time_drone, height_drone)

#Plot CCS811 Data
plotCCS("CCS811", "CO2[ppm]", time_box, co2, "TVOC[ppb]", time_box, tvoc, "Drone-Altitude[m]", time_drone, height_drone)

#Plot POPS Data
plotSEN_POPS("Portable Optical Particle Spectrometer", "Particle Concentration[#/cm3]", time_pops, partCon, "Particle Count[#/s]", time_pops, partCt, "Pressure[hPa]", time_pops, pressure_pops, "Drone-Altitude[m]", time_drone, height_drone)
time_pops = time_pops.time
plotHeatMap(b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, flow_pops, time_pops, "Drone-Altitude[m]", time_drone, height_drone)

#Show all figures
if visual:
    plt.show()
    
