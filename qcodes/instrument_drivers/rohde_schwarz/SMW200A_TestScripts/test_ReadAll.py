# -*- coding: utf-8 -*-
"""
File: test_ReadAll.py
Date: Nai 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to read all parameters from all modules
"""


from qcodes.instrument_drivers.rohde_schwarz.SMW200A import RohdeSchwarz_SMW200A
from qcodes.instrument.channel import ChannelList
import re

notreadlist = [] # List to collect all not readable parameters
nodoclist = [] # List to collect all not documented parameters (docstring)

# helper function to go through all parameters of one module
def helper( mod, params ):
    global notreadlist
    for p in params:
        par = params[p]
        try:
            val = str( par() ).strip() + " " + par.unit
        except:
            val = "** not readable **"
            notreadlist.append( mod + "." + p )
        if hasattr(par, 'label'):
            print( p, " | ", par.label, ": ", val )
        else:
            print( mod + "." + p + ": ", val )
        if par.__doc__ is not None:
            if par.__doc__[:9] != "Parameter" and par.__doc__[:9] != "MultiPara":
                tmp = re.sub(' {2,}', ' ', par.__doc__)
                print( "DOC: ", tmp[:tmp.index('Parameter class:')].strip(), "\n" )
            else:
                nodoclist.append( mod + "." + p )
        else:
            nodoclist.append( mod + "." + p )

#                tmp = re.sub(' {2,}', ' ', par.__doc__)
#                tmp = tmp[:tmp.index('Parameter class:')].split('\n')
#                tmp2 = ['  '+s for s in tmp if len(s)>2]
#                print( '\n'.join(tmp2) )

# Open Device. Be sure that the device-id is correct
dev = RohdeSchwarz_SMW200A( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )

# First read all version informatione
print( "==========  Version informations  ==========" )
print( "ID:", dev.get_id() )
print( "Options:", dev.get_options() )

# Seconds read all parameters from the main device class
print( "\n==========  Main Device  ==========" )
helper( "Main", dev.parameters )

# then read all parameters for all submodules
for m in dev.submodules:
    mod = dev.submodules[m]
    if not isinstance( mod, ChannelList ):
        print( "\n========== ", m, " ==========" )
        helper( m, mod.parameters )

if len(notreadlist) > 0:
    print( "\nNot readable: ", notreadlist )
if len(nodoclist) > 0:
    print( "\nNot documented: ", nodoclist )

dev.close()
