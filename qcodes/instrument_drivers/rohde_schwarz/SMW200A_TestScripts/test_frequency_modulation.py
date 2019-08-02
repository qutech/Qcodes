# -*- coding: utf-8 -*-
"""
File: test_frequency_modulation.py
Date: Tue May 28 12:46:54 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of FrequencyModulation
"""

from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

fm1 = dev.submodules['fm_channels'][0]
fm2 = dev.submodules['fm_channels'][1]

#Testing the state parameter
print("State (channel 1):", fm1.state())
fm1.state('ON')
print("State (channel 1):", fm1.state())
fm1.state('OFF')

#Testing the deviation parameter
print("Deviation (channel 1):", fm1.deviation())
fm1.deviation(20000)
print("Deviation (channel 1):", fm1.deviation())
fm2.deviation(20000)
print("Deviation (channel 2):", fm2.deviation())

#Testing the source parameter
print("Source (channel 1):", fm1.source())
fm1.source('INT')
print("Source (channel 1):", fm1.source())
fm1.source('EXT')
print("Source (channel 1):", fm1.source())
print("Source (channel 2):", fm2.source())

#Testing the coupling parameter
#print(fm1.coupling_mode())

#Testing the total_deviation parameter
#print(fm1.total_deviation())

#Testing the deviation_ratio parameter
print("Deviation ratio:", fm1.deviation_ratio())
fm1.deviation_ratio(50)
print("Deviation ratio:", fm1.deviation_ratio())

#Testing the mode parameter
print("Mode:", fm1.mode())
fm1.mode('LNO')
print("Mode:", fm1.mode())

#Testing the sensitivity parameter
print("Sensitivity:", fm1.sensitivity())

dev.close()