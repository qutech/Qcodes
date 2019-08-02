# -*- coding: utf-8 -*-
"""
File: test_iq_modulation
Date: June 7 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of IQModulation
"""
from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

iqm = dev.submodules['IQmod1']

#Testing the source parameter
print("Source:", iqm.source())
iqm.source('ANAL')
print("Source:", iqm.source())

#Testing the state parameter
print("State:", iqm.state())
iqm.state('ON')
print("State:", iqm.state())

#Testing the gain parameter
print("Gain:", iqm.gain())
iqm.gain('DBM4')
print("Gain:", iqm.gain())
iqm.gain('DBM2')
print("Gain:", iqm.gain())
iqm.gain('DB0')
print("Gain:", iqm.gain())
iqm.gain('DB2')
print("Gain:", iqm.gain())
iqm.gain('DB4')
print("Gain:", iqm.gain())
iqm.gain('DB8')
print("Gain:", iqm.gain())
iqm.gain('DB6')
print("Gain:", iqm.gain())
iqm.gain('DBM3')
print("Gain:", iqm.gain())
iqm.gain('DB3')
print("Gain:", iqm.gain())
iqm.gain('AUTO')
print("Gain:", iqm.gain())

#Testing the crest_factor parameter
print("Crest factor:", iqm.crest_factor())
iqm.crest_factor(20.5)
print("Crest factor:", iqm.crest_factor())

#Testing the swap parameter
print("Swap:", iqm.swap())
iqm.swap('ON')
print("Swap:", iqm.swap())

#Testing the wideband parameter
print("Wideband:", iqm.wideband())
iqm.wideband('ON')
print("Wideband:", iqm.wideband())

dev.close()