#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ready_to_range.py - Tutorial intended to show how to perform ranging between two Pozyx devices.

It is planned to make a tutorial on the Pozyx site as well just like there is now
one for the Arduino, but their operation is very similar.
You can find the Arduino tutorial here:
    https://www.pozyx.io/Documentation/Tutorials/ready_to_range
"""
from pypozyx import *

from pypozyx.definitions.registers import *


port = get_serial_ports()[-1][0]
p = PozyxSerial(port)
remote_id = 0x6830           # the network ID of the remote device
remote = False               # whether to use the given remote device for ranging
if not remote:
    remote_id = None

destination_id = 0x685C      # network ID of the ranging destination
range_step_mm = 1000         # distance that separates the amount of LEDs lighting up.


device_range = DeviceRange()
status = p.doRanging(destination_id, device_range, remote_id)
if status:
    list_offset = range(0, 1015, 49)
    data_length = 49
    cir_buffer = Buffer([0] * 98 * len(list_offset), size=2, signed=1)
    status_cir = p.getDeviceCir(list_offset, data_length, cir_buffer, remote_id)
    if status_cir:
        try:
            import matplotlib.pyplot as plt
            import numpy as np
    #         get real and imaginarypart of the cir buffer
            real = np.array(cir_buffer.data[0::2])
            imag = np.array(cir_buffer.data[1::2])
            # create an image of the CIR
            cira = real + 1j*imag
    #       That plots the CIR contains in the buffer.
    #       It still requires post-procesing to
    #       re-align delay and received power level.
            cira=cira[:-36]
            ciradb = 20*np.log10(abs(cira))
            plt.plot(ciradb)
            plt.show()
        except:
            print cir_buffer
    else:
        print 'error in getting cir'
else:
    print 'Ranging failed'


th = np.mean(ciradb)+3*np.std(ciradb)

uth = np.where(ciradb>th)

dt = device_range.distance/300.
time_step = 1.0016



io =  uth - int(round(dt/time_step))

# recal power
maxcira = abs(cira[io:]).max()
fGHz = 6.489
FSPL = 32.4+20*np.log10(fGHz)+20*np.log10(device_range.distance/1000.)

Palpha = pow(10,-FSPL/20.)/(1.*maxcira)

cira = Palpha * cira 

plt.plot(20*np.log10(abs(cira[io:350])))
