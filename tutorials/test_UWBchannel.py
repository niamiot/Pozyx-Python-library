# -*- coding: utf-8 -*-

from pypozyx import *

from pypozyx.definitions.registers import *

import matplotlib.pyplot as plt
import numpy as np
import time
port = get_serial_ports()[-1][0]
p = PozyxSerial(port)


anchors = [0x685C,0x6065]


# UWN_CHANNEL   Indicate the UWB channel. Possible values:
# 1 : Centre frequency 3494.4MHz, using the band(MHz): 3244.8 – 3744, bandwidth 499.2 MHz 
# 2 : Centre frequency 3993.6MHz, using the band(MHz): 3774 – 4243.2, bandwidth 499.2 MHz
# 3 : Centre frequency 4492.8MHz, using the band(MHz): 4243.2 – 4742.4 bandwidth 499.2 MHz
# 4 : Centre frequency 3993.6MHz, using the band(MHz): 3328 – 4659.2 bandwidth 1331.2 MHz (capped to 900MHz) 
# 5 : Centre frequency 6489.6MHz, using the band(MHz): 6240 – 6739.2 bandwidth 499.2 MHz # (default)
# 7 : Centre frequency 6489.6MHz, using the band(MHz): 5980.3 – 6998.9 bandwidth 1081.6 MHz (capped to 900MHz)

p.doDiscovery()

##setup 
UWB_channel = 7
print 'UWB_channel',UWB_channel
r = SingleRegister(UWB_channel)

## apply setup
p.setUWBChannel(r,remote_id=anchors[0])
p.setUWBChannel(r)

conf_local=SingleRegister()
conf_anchor0=SingleRegister()
p.getUWBChannel(conf_local)
time.sleep(1)
p.getUWBChannel(conf_anchor0,remote_id=anchors[0])

print 'local channel conf:' + str(conf_local)
print 'remote channel conf:' + str(conf_anchor0)

range7=[]
## ranging
device_range = DeviceRange()
range_status = p.doRanging(anchors[0], device_range, None)
# print device_range.distance
range7.append(device_range.distance)

# # # get cir 
# list_offset = range(600, 943, 49)
# data_length = 49
# cir_buffer = Buffer([0] * 98 , size=2, signed=1)
# if range_status:
#     status_cir = p.getDeviceCir(list_offset, data_length, cir_buffer, remote_id = None)
#     real = np.array(cir_buffer.data[0::2])
#     imag = np.array(cir_buffer.data[1::2])
#     cira = real + 1j*imag
#     cira=cira[:-36]
#     ciradb_1 = 20*np.log10(abs(cira))
# import ipdb
# ipdb.set_trace()


# # time.sleep(0.1)
# ###############################################################
# # setup
# UWB_channel = 5
# print 'UWB_channel',UWB_channel
# r = SingleRegister(UWB_channel)

# r# apply setup
# p.setUWBChannel(r,remote_id=anchors[0])
# p.setUWBChannel(r)


# conf_local=SingleRegister()
# conf_anchor0=SingleRegister()
# p.getUWBChannel(conf_local)
# p.getUWBChannel(conf_anchor0,remote_id=anchors[0])

# print 'local channel conf:' + str(conf_local)
# print 'remote channel conf:' + str(conf_anchor0)


# range5=[]
# ## ranging
# device_range = DeviceRange()
# range_status = p.doRanging(anchors[0], device_range, None)
# # print device_range.distance
# range5.append(device_range.distance)

# # # # get cir 
# # list_offset = range(600, 1015, 49)
# # data_length = 49
# # cir_buffer = Buffer([0] * 98 * len(list_offset), size=2, signed=1)

# # status_cir = p.getDeviceCir(list_offset, data_length, cir_buffer, None)
# # real = np.array(cir_buffer.data[0::2])
# # imag = np.array(cir_buffer.data[1::2])
# # cira = real + 1j*imag
# # cira=cira[:-36]
# # ciradb_1 = 20*np.log10(abs(cira))



# # plt.plot(ciradb_0,label='conf=7')
# # plt.plot(ciradb_0,label='conf=5')
# # plt.legend()
# # plt.show()