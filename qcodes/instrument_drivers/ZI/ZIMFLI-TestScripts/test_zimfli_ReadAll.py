# -*- coding: utf-8 -*-
"""
File: test_zimfli_ReadAll.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to read all parameters from all modules
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
from qcodes.instrument.channel import ChannelList
import time
import re
import json

# List to collect all not readable parameters
notreadlist = []

# helper function to go through all parameters of one module
def helper( mod, params ):
    global notreadlist
    for p in params:
        par = params[p]
        try:
            val = str( par() ) + " " + par.unit
        except:
            val = "** not readable **"
            notreadlist.append( mod + "." + p )
        if hasattr(par, 'label'):
            print( p, " | ", par.label, ": ", val )
        elif p == "Scope":
            continue
        else:
            print( mod + "." + p + ": ", val )
        if par.__doc__ is not None:
            if par.__doc__[:9] != "Parameter" and par.__doc__[:9] != "MultiPara":
                tmp = re.sub(' {2,}', ' ', par.__doc__)
                print( tmp[:tmp.index('Parameter class:')].strip() )

# all t_* variables are used to measure the time
t_startall = time.time()

# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )
t_open = time.time()

# First read all version informatione
print( "==========  Version informations  ==========" )
print( json.dumps( zidev.version(), indent=4 ) )
t_version = time.time()

# Seconds read all parameters from the main device class
print( "\n==========  Main Device  ==========" )
helper( "Main", zidev.parameters )
t_mainpar = time.time()

# then read all parameters for all submodules
for m in zidev.submodules:
    mod = zidev.submodules[m]
    if not isinstance( mod, ChannelList ):
        print( "\n========== ", m, " ==========" )
        helper( m, mod.parameters )
t_endall = time.time()

# last print the times and the list of not readable parameters
print( "\n==========  Statistics  ==========" )
print( "times: overall = ", t_endall - t_startall, " sec" )
print( "       Connect = ", t_open - t_startall, " sec" )
print( "       Version = ", t_version - t_open, " sec" )
if len(notreadlist) > 0:
    print( "\nNot readable: ", notreadlist )

zidev.close()
