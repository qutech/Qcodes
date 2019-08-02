# -*- coding: utf-8 -*-
"""
File: test_pulse_modulation
Date: June 4 2019
Author: Sarah Fleitmann, ZEA-2, s.fleitmann@fz-juelich.de
Purpose: Testing the parameters of PulseModulation
"""
from SMW200A import RohdeSchwarz_SMW200A

dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )
dev.reset()

pm = dev.pulsemod1

#Testing the mode parameter
#print(pm.mode())

#Testing the trigger_mode parameter
#print(pm.trigger_mode())

#Testing the period parameter
#print(pm.period())

#Testing the width parameter
#print(pm.width())

#Testing the delay parameter
#print(pm.delay())

#Testing the state parameter
print("State:", pm.state())
pm.state('ON')
print("State:", pm.state())

#Testing the source parameter
print("Source:", pm.source())

#Testing the transition_type parameter
print("Transition type:", pm.transition_type())
pm.transition_type('SMO')
print("Transition type:", pm.transition_type())

#Testing the video_polarity parameter
print("Video polarity:", pm.video_polarity())
pm.video_polarity('INV')
print("Video polarity:", pm.video_polarity())

#Testing the polarity parameter
print("Polarity:", pm.polarity())
pm.polarity('INV')
print("Polarity:", pm.polarity())

#Testing the impedance parameter
print("Impedance:", pm.impedance())
pm.impedance('G50')
print("Impedance:", pm.impedance())

#Testing the trigger_impedance parameter
print("Trigger impedance:", pm.trigger_impedance())
pm.trigger_impedance('G10K')
print("Trigger impedance:", pm.trigger_impedance())

dev.close()