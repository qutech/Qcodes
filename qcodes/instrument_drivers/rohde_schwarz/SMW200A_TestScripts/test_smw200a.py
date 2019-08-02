# -*- coding: utf-8 -*-
"""
File: test_smw200a.py
Date: Mai 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: First steps to get in touch with the instrument
"""


from qcodes.instrument_drivers.rohde_schwarz.SMW200A import RohdeSchwarz_SMW200A as smw200a

dev = smw200a( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )

print( "ID:", dev.get_id() )
print( "Options:", dev.get_options() )

print( dev.getall() )

dev.close()
