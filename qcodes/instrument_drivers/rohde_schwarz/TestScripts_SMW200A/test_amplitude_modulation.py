# -*- coding: utf-8 -*-
"""
File: test_amplitude_modulation
Date: Tue May 28 13:03:20 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of AmplitudeModulation
"""

from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

am1 = dev.submodules['am_channels'][0]
am2 = dev.submodules['am_channels'][1]

#Testing the state parameter
print("State (channel 1):", am1.state())
am1.state('ON')
print("State (channel 1):", am1.state())
am1.state('OFF')
print("State (channel 2):", am2.state())
am2.state('ON')
print("State (channel 2):", am2.state())
am2.state('OFF')

#Testing the source parameter
print("Source (channel 1):", am1.source())
am1.source('EXT')
print("Source (channel 1):", am1.source())
am1.source('INT')
print("Source (channel 1):", am1.source())
print("Source (channel 2):", am2.source())
am2.source('EXT2')
print("Source (channel 2):", am2.source())
am2.source('LF1')
print("Source (channel 2):", am2.source())

#Testing the depth parameter
print("Depth (channel 1):", am1.depth())
am1.depth(50)
print("Depth (channel 1):", am1.depth())
print("Depth (channel 2):", am2.depth())
am2.depth(50)
print("Depth (channel 2):", am2.depth())

#Testing parameter total_depth
#print("Total depth:", am1.total_depth())

#Testing the coupling_mode parameter
#print("Coupling mode:", am1.coupling_mode())

#Testing the deviation_ratio parameter
print("Deviation ratio:", am1.deviation_ratio())
am1.deviation_ratio(50)
print("Deviation ratio:", am1.deviation_ratio())

#Testing the sensitivity parameter
print("Sensitivity:", am1.sensitivity())

dev.close()