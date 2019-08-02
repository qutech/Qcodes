# -*- coding: utf-8 -*-
"""
File: test_phase_modulation
Date: June 3 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of PhaseModulation
"""
from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

pm1 = dev.submodules['pm_channels'][0]
pm2 = dev.submodules['pm_channels'][1]

#Testing the state parameter
print("State (channel 1):", pm1.state())
pm1.state('ON')
print("State (channel 1):", pm1.state())
pm1.state('OFF')
print("State (channel 2):", pm2.state())
pm2.state('ON')
print("State (channel 2):", pm2.state())
pm2.state('OFF')

#Testing the deviation parameter
print("Deviation (channel 1):", pm1.deviation())
pm1.deviation(4)
print("Deviation (channel 1):", pm1.deviation())
pm2.deviation(3)
print("Deviation (channel 2):", pm2.deviation())

#Testing the source parameter
print("Source (channel 1):", pm1.source())
pm1.source('EXT')
print("Source (channel 1):", pm1.source())
pm1.source('INT')
print("Source (channel 1):", pm1.source())
print("Source (channel 2):", pm2.source())
pm2.source('EXT2')
print("Source (channel 2):", pm2.source())

#Testing the mode parameter
print("Mode:", pm1.mode())
pm1.mode('LNO')
print("Mode:", pm1.mode())
pm1.mode('HDEV')
print("Mode:", pm1.mode())

#Testing the coupling_mode parameter
#print("Coupling mode:", pm1.coupling_mode())
#pm1.coupling_mode('TOT')
#print("Coupling mode:", pm1.coupling_mode())

#Testing the total_deviation parameter
#print("Total deviation:", pm1.total_deviation())
#pm1.total_deviation(15)
#print("Total deviation:", pm1.total_deviation())

#Testing the ratio parameter
print("Ratio:", pm1.ratio())
pm1.ratio(30)
print("Ratio:", pm1.ratio())

#Testing th sensitivity parameter
print("Sensitivity:", pm1.sensitivity())


dev.close()