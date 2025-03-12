Lab on a Drone - ReadMe

Inhalt:
	Materialien
	Verwendung
	Libraries
	Konfiguration
	RTC Modul kalibrieren

-----------------------------------------------------------------------------------------
-) Materialien:

Raspberry Pi 4
SEN55 (Sensirion)
BME680 (Joy-It)
CCS811 
DS1307-RTC (Seeed)
LCD-Modul 16x2 (Joy-It)
SIM7600E 4G HAT (Waveshare)
Portable Optical Particle Spectrometer (Handix Scientific)
-----------------------------------------------------------------------------------------
-) Verwendung:

Das main.py Programm wird gestartet um eine Erfassung von Aerosol- und Umweltdaten durchzuführen.
Nach dem Start des Programms, dauert es einige Zeit bis die Sensorik bereit ist (nähere Informationen am LCD-Modul).
Sobald das System bereit ist, wird mit einem Button ein GPIO-Input gesetzt und alle erhobenen Daten werden in ein CSV-File geschrieben.
Die Daten befinden sich dann in der folgenden Ordnerstruktur: data/TAG/UHRZEIT.csv

Die erfassten Daten können danach mit dem plotter.py Skript visualisiert werden.
Beim Start des Visualisierungsprogramms öffnet sich eine Benutzeroberfläche in der das CSV-file der "Lab on a Drone"-Box und das CSV-file der DJI Matrice 300 RTK Drohne ausgewählt werden sollen. Optional kann eine Schrittweite (stepsize) gewählt werden, mit der die Daten gemittelt werden.
-----------------------------------------------------------------------------------------
-) Libraries:

main.py: time, RPi.GPIO, busio, sensirion_i2c_driver, sensirion_i2c_sen5x, os
plotter.py: matplotlib, tkinter, pandas

manche libraries konnten nicht einfach mit "pip3 install package_name" installiert werden
Grund --> error: externally-managed-environment
Lösung--> "pip3 install package_name --break-system-packages" oder virtual environment
-----------------------------------------------------------------------------------------
-) Konfiguration:

I2C baudrate wurde auf 10000 gesetzt, da sonst der CCS811 falsche Werte (außerhalb des Bereichs) liefert

sudo nano /boot/config.txt
dtparam=i2c_arm_baudrate=10000
-----------------------------------------------------------------------------------------
-) RTC Modul kalibrieren:

sudo timedatectl

ODER:

1)RTC modul aktiv? falls ja: --> 2)
lsmod    --> rtc_ds1307 in liste vorhanden, dann aktiv, falls nein:
sudo modprobe rtc-ds1307

Dies kann beim booten automatisch aktiviert werden mit:
sudo nano /boot/config.txt
unten folgendes hinzufügen und speichern: dtoverlay=i2c-rtc,ds1307
im nano editor gilt generell: Ctrl+O <--- Änderungen speichern
			      Ctrl+X <--- Nano editor beenden

2)Um die RTC Zeit mit der Systemzeit zu synchronisieren muss ein weiteres file bearbeitet werden
sudo nano /etc/rc.local
vor exit 0 werden folgende 2 Zeilen hinzugefügt:
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
hwclock -s
---> Ctrl+O ---> Ctrl+X

3)Raspberry Pi neustarten!

4)Nun steht bei i2cdetect UU statt 68 in der i2c Liste und es können hwclock commands verwendet werden
sudo i2cdetect -y 1
sudo hwclock -r   <--- zeigt die aktuelle Zeit im Terminal
sudo hwclock -w   <--- überschreibt die RTC Zeit mit der aktuellen Systemzeit und die Uhr ist wieder genau

5)ACHTUNG: nun kann das RTC modul über I2C nicht verwendet werden, wenn UU statt 68 bei i2cdetect aufscheint, daher:
sudo nano /etc/rc.local
die beiden Zeilen aus Punkt 2) werden entfernt oder mit # auskommentiert
#echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
#hwclock -s
---> Ctrl+O ---> Ctrl+X

6)Raspberry Pi neustarten! PiRTC sollte nun wieder genau und auch über I2C ansprechbar sein
-----------------------------------------------------------------------------------------
