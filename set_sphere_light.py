#!/usr/bin/env python
"""Set Spheramid underlight to brightness in command line parameter."""

import os
import sys

try:
    value = int(sys.argv[1])
    if value < 0:
        value = 0
    elif value > 100:
        value = 100
except (ValueError, IndexError):
    value = 0

os.system("mosquitto_pub -m '{{\"brightness\": {}}}' -t '$hardware/status/reset' -h ninjasphere.local".format(value))
