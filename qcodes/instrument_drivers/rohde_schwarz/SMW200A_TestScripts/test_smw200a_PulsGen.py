# -*- coding: utf-8 -*-
"""
File: test_smw200a_PulsGen.py
Date: Jan 2020
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Puls Generator (Mails Dec2019/Jan2020 with Tom Struck)
"""

from qcodes.instrument_drivers.rohde_schwarz.SMW200A import RohdeSchwarz_SMW200A as smw200a


def printpar(pgen, pmod, prmt):
    # Helper function to print some informations for the puls generation
    print( "-----", prmt, "-----")
    print( "PGEN: polarity:", pgen.polarity().rstrip() )
    print( "        output:", pgen.output() )
    print( "         state:", pgen.state() )
    print( "PMOD:     mode:", pmod.mode().rstrip() )
    print( "       trigger:", pmod.trigger_mode().rstrip() )
    print( "        period:", pmod.period() )
    print( "         width:", pmod.width() )
    print( "         delay:", pmod.delay() )

    

# Open the device
dev = smw200a( name='SMW200A', address='TCPIP::134.61.7.60::hislip0::INSTR' )

# print some informations
print( "ID:", dev.get_id() )
print( "Options:", dev.get_options() )

# to use the helper function above, we have to access two submodules
pgen = dev.submodules['pulsegen1']
pmod = dev.submodules['pulsemod1']
printpar(pgen, pmod, "Init")

# generate the trigger pulse
dev.genTriggerPulse( 0.0001 )

# print the informations again (to control the settings)
printpar(pgen, pmod, "After")

# close the device
dev.close()
