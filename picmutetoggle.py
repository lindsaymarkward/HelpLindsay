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

import os
import serial
import time

# setup serial port
COMMAND_MUTE_OFF = "kd 0 0\r"
COMMAND_MUTE_ON = "kd 0 1\r"
serial_connection = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

os.chdir("/home/lindsay/scripts")
in_file = open("picmutestatus.txt", 'r')
status = in_file.readline().strip()
in_file.close()

out_file = open("picmutestatus.txt", 'w')
if status == "off":
    # send serial command for TV picture mute on
    serial_connection.write(COMMAND_MUTE_ON)
    out_file.write("on")
else:
    # send serial command for TV picture mute off
    serial_connection.write(COMMAND_MUTE_OFF)
    out_file.write("off")

time.sleep(0.1)
out_file.close()
serial_connection.close()
