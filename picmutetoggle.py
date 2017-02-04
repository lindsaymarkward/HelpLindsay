"""
LG TV Picture Mute toggle - Serial version
Lindsay Ward, 30/03/2014

open serial port
open file for reading
read line from file
close file
open file for writing
if line is 'on'
    send serial command for mute off
    write 'off' to file
else
    send serial command for mute on
    write 'on' to file
close file
close serial port
"""

import serial, os, time

#setup serial port
serial_connection = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

os.chdir("/home/lindsay/scripts")
inFile = open("picmutestatus.txt", 'r')
status = inFile.readline().strip()
inFile.close()

outFile = open("picmutestatus.txt", 'w')
if status == "off":
    # send serial command for TV picture mute on
    serial_connection.write("kd 0 1\r")
    outFile.write("on")
else:
    # send serial command for TV picture mute off
    serial_connection.write("kd 0 0\r")
    outFile.write("off")

time.sleep(0.1)
outFile.close()
serial_connection.close()

