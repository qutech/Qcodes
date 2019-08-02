# -*- coding: utf-8 -*-
"""
File: test_iq_output_channel.py
Date: June 11 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of IQChannel
"""
from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

iq1 = dev.iqoutput_channels[0]
iq2 = dev.iqoutput_channels[1]

#Testing the state parameter
print("State (channel 1):", iq1.state())
iq1.state('ON')
print("State (channel 1):", iq1.state())
print("State (channel 2):", iq2.state())
iq2.state('ON')
print("State (channel 2):", iq2.state())

#Testing the type parameter
print("Type (channel 1):", iq1.type())
print("Type (channel 1):", iq1.type())

#Testing the mode parameter
print("Mode (channel 1):", iq1.mode())
print("Mode (channel 2):", iq2.mode())

#Testing the level parameter
print("Level (channel 1):", iq1.level())
print("Level (channel 2):", iq2.level())

#Testing the coupling parameter
print("Coupling (channel 1):", iq1.coupling())
iq1.coupling('ON')
print("Coupling (channel 1):", iq1.coupling())
print("Coupling (channel 2):", iq2.coupling())
iq2.coupling('ON')
print("Coupling (channel 2):", iq2.coupling())

#Testing the bias parameter for the I component
print("I bias (channel 1):", iq1.i_bias())
print("I bias (channel 2):", iq2.i_bias())

#Testing the bias parameter for the Q component
print("Q bias (channel 1):", iq1.q_bias())
print("Q bias (channel 2):", iq2.q_bias())

#Testing the offset parameter for the i component
print("I offset (channel 1):", iq1.i_offset())
print("I offset (channel 2):", iq2.i_offset())

#Testing the offset parameter for the q component
print("Q offset (channel 1):", iq1.q_offset())
print("Q offset (channel 2):", iq2.q_offset())

dev.close()