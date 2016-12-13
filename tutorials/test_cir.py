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
from pypozyx.definitions.bitmasks import *
import numpy as np
import matplotlib.pyplot as plt
import time


class Tag(object):

    def __init__(self, anchors_id=[]):

        self.port = get_serial_ports()[-1][0]
        self.p = PozyxSerial(self.port)

        # check available anchors
        self.p.doDiscovery()
        list_size = SingleRegister()
        self.p.getDeviceListSize(list_size)
        device_list = DeviceList(list_size=list_size[0])
        self.p.getDeviceIds(device_list)
        if anchors_id == []:
            anchors_id = device_list.data
        else:
            for a in anchors_id:
                if not a in device_list.data:
                    raise AttributeError(
                        'device ' + str(hex(a)) + ' not in the network')

        # uwb channel check
        chan_UWB = SingleRegister()
        self.p.getUWBChannel(chan_UWB)
        self.channel = chan_UWB.data[0]

        if not isinstance(anchors_id, list):
            anchors_id = [anchors_id]

        self.anchors = {i: {'range': DeviceRange(), 'range_status': False,
                            'cir_status': False, 'cira': []} for i in anchors_id}

    def __repr__(self):

        s = 'UWB configuration:' + str(self.channel) + '\n'

        if self.channel == 1:
            s = s + \
                'Centre frequency: 3494.4MHz\nband(MHz): 3244.8 – 3744\nbandwidth 499.2 MHz'
        elif self.channel == 2:
            s = s + \
                'Centre frequency: 3993.6MHz\nband(MHz): 3774 – 4243.2\nbandwidth 499.2 MHz'

        elif self.channel == 3:
            s = s + \
                'Centre frequency: 4492.8MHz\nband(MHz): 4243.2 – 4742.4\nbandwidth 499.2 MHz'

        elif self.channel == 4:
            s = s + \
                'Centre frequency: 3993.6MHz\nband(MHz): 3328 – 4659.2\nbandwidth 1331.2 MHz (capped to 900MHz) '

        elif self.channel == 5:
            s = s + \
                'Centre frequency: 6489.6MHz\nband(MHz): 6240 – 6739.2\nbandwidth 499.2 MHz '

        elif self.channel == 7:
            s = s + \
                'Centre frequency: 6489.6MHz\nband(MHz): 5980.3 – 6998.9\nbandwidth 1081.6 MHz (capped to 900MHz)'

        s = s + '\n\n'

        s = s + '{0:6s} | {1:4s} | {2:9s} | {3:1s}'.format(
            'Anchor', 'rng', 'rng status', 'cir status')
        s = s + '\n'
        for a in self.anchors:
            s = s + '{0} | {1:4d} | {2:10d} | {3:1d}'.format(hex(a),
                                                             self.anchors[a][
                                                                 'range'].distance,
                                                             self.anchors[a][
                                                                 'range_status'],
                                                             self.anchors[a]['cir_status'])
            s = s + '\n'
        return s

    def range(self, anchors_id=[], trial=10):

        if not isinstance(anchors_id, list):
            anchors_id = [anchors_id]
        if anchors_id == []:
            anchors_id = self.anchors.keys()

        for a in anchors_id:

            for k in range(trial):
                self.anchors[a]['range_status'] = self.p.doRanging(
                    a, self.anchors[a]['range'], None)
                if self.anchors[a]['range_status']:
                    break
                else:
                    time.sleep(0.1)

    def get_cir(self, anchors_id=[], do_ranging=True):

        if not isinstance(anchors_id, list):
            anchors_id = [anchors_id]
        if anchors_id == []:
            anchors_id = self.anchors.keys()

        if do_ranging:
            self.range(anchors_id)

        for a in anchors_id:
            if self.anchors[a]['range_status']:
                list_offset = range(0, 1015, 49)
                data_length = 49
                cir_buffer = Buffer(
                    [0] * 98 * len(list_offset), size=2, signed=1)
                self.anchors[a]['cir_status'] = self.p.getDeviceCir(
                    list_offset, data_length, cir_buffer, None)

                if self.anchors[a]['cir_status']:
                    #         get real and imaginarypart of the cir buffer
                    real = np.array(cir_buffer.data[0::2])
                    imag = np.array(cir_buffer.data[1::2])
                    # create an image of the CIR
                    cira = real + 1j * imag
            #       That plots the CIR contains in the buffer.
            #       It still requires post-procesing to
            #       re-align delay and received power level.
                    cira = cira[:-36]
                    ciradb = 20 * np.log10(abs(cira))

                    self.anchors[a]['raw_cira'] = cira
                    self.anchors[a]['raw_ciradB'] = ciradb

                    th = np.mean(ciradb) + 3 * np.std(ciradb)
                    self.anchors[a]['threshold'] = th

                    uth = np.where(ciradb > th)[0][0]

                    dt = self.anchors[a]['range'].distance / 300.
                    time_step = 1.0016

                    # index leading edge
                    ule = uth - int(round(dt / time_step))
                    self.anchors[a]['ule'] = ule
                    # recal power
                    maxcira = abs(cira[ule:]).max()
                    fGHz = 6.489
                    FSPL = 32.4 + 20 * np.log10(fGHz) + 20 * \
                        np.log10(self.anchors[a]['range'].distance / 1000.)

                    Palpha = pow(10, -FSPL / 20.) / (1. * maxcira)

                    cira_recal = Palpha * cira
                    ciradb_recal = 20 * np.log10(abs(cira_recal))

                    self.anchors[a]['cira'] = cira_recal
                    self.anchors[a]['ciradB'] = ciradb_recal
                    # poisiton leading edge

    def change_channel(self, channel=5):
        """ Change UWB channel
        # UWN_CHANNEL   Indicate the UWB channel. Possible values:
        # 1 : Centre frequency 3494.4MHz, using the band(MHz): 3244.8 – 3744, bandwidth 499.2 MHz 
        # 2 : Centre frequency 3993.6MHz, using the band(MHz): 3774 – 4243.2, bandwidth 499.2 MHz
        # 3 : Centre frequency 4492.8MHz, using the band(MHz): 4243.2 – 4742.4 bandwidth 499.2 MHz
        # 4 : Centre frequency 3993.6MHz, using the band(MHz): 3328 – 4659.2 bandwidth 1331.2 MHz (capped to 900MHz) 
        # 5 : Centre frequency 6489.6MHz, using the band(MHz): 6240 – 6739.2 bandwidth 499.2 MHz # (default)
        # 7 : Centre frequency 6489.6MHz, using the band(MHz): 5980.3 – 6998.9 bandwidth 1081.6 MHz (capped to 900MHz)
        """

        if channel not in [1, 2, 3, 4, 5, 7]:
            raise AttributeError('Wrong Channel number (1,2,3,4,5,7)')

        chan = SingleRegister(channel)
        # verif because status of setUWBchannel is not reliable
        verif = SingleRegister()

        for a in self.anchors:
            self.p.setUWBChannel(chan, remote_id=a)



        
        self.p.setUWBChannel(chan)
        self.p.getUWBChannel(verif)

        if verif.data[0] == channel:
            print 'tag ' + ' is now on channel ' + str(channel)

        # check

        for a in self.anchors:
            self.p.getUWBChannel(verif, remote_id=a)
            if verif.data[0] == channel:
                print 'anchor ' + hex(a) + ' is now on channel ' + str(chan.data)


        self.channel = channel


    def plot(self, **kwargs):

        defaults = {"fig": [],
                    "ax": []}

        for k in defaults:
            if k not in kwargs:
                kwargs[k] = defaults[k]

        if kwargs['fig'] == []:
            fig = plt.figure()
        else:
            fig = kwargs['fig']
        if kwargs['ax'] == []:
            ax = fig.add_subplot(111)
        else:
            ax = kwargs['ax']

        for a in self.anchors:
            delay = self.anchors[a]['ule']
            plt.plot(self.anchors[a]['ciradB'][delay:], label=str(hex(a)))
        plt.legend()
        plt.show()


T = Tag()
T.change_channel(7)


# T.get_cir()
# T.plot()
