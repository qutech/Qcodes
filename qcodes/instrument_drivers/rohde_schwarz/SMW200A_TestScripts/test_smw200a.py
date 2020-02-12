# -*- coding: utf-8 -*-
"""
File: test_smw200a.py
Date: Mai 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: First steps to get in touch with the instrument
"""


from qcodes.instrument_drivers.rohde_schwarz.SMW200A import RohdeSchwarz_SMW200A as smw200a

#dev = smw200a( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' ) # ohne Pulsgen
# ID: Rohde&Schwarz,SMW200A,1412.0000K02/105578,04.30.005.29 SP2
# Options: ['SMW-B13T', 'SMW-B22', 'SMW-B120', 'SMW-K22', 'SMW-K23']

dev = smw200a( name='SMW200A', address='TCPIP::134.61.7.60::hislip0::INSTR' ) # mit PulsGen
# ID: Rohde&Schwarz,SMW200A,1412.0000K02/102499,4.65.007.30 32 Bit
# Options: ['SMW-B13T', 'SMW-B22', 'SMW-B120', 'SMW-K22', 'SMW-K23']

print( "ID:", dev.get_id() )
print( "Options:", dev.get_options() )

#print( dev.getall() )

dev.close()
