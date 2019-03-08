# -*- coding: utf-8 -*-
"""
File: test_zimfli_SampleSync.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to read the demod Parameters to check synchronisation of
         the sample, x, y, R, phi values.
"""

from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import time

# helper function to go through all parameters of one module
def helper( mod, params ):
    global notreadlist
    for p in params:
        par = params[p]
        try:
            val = str( par() ) #+ " " + par.unit
        except:
            val = "** not readable **"
            notreadlist.append( mod + "." + p )
        #print( "wrhelper( '" + mod + "', '" + p + "', " + val + " )" )
        if hasattr(par, 'label'):
            print( par.label, ": ", val )
        elif p == "Scope":
            continue
        else:
            print( mod + "." + p + ": ", val )

# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

dmod1 = zidev.submodules['demod1']

print( "Config-Timout = ", dmod1.cfgTimeout() )
dmod1.cfgTimeout( 0.15 )
print( "Config-Timout = ", dmod1.cfgTimeout() )

t_start = time.time()

# damit es keine print() Verzögerungen gibt, werden erstmal alle Daten
# abgefragt und lokal gespeichert
sam_val = dmod1.sample()
t_sam = time.time()
sam_tim = zidev.lastsampletime / zidev.clockbase

x_val = dmod1.x()
t_x = time.time()
x_tim = zidev.lastsampletime / zidev.clockbase

y_val = dmod1.y()
t_y = time.time()
y_tim = zidev.lastsampletime / zidev.clockbase

r_val = dmod1.R()
t_r = time.time()
r_tim = zidev.lastsampletime / zidev.clockbase

phi_val = dmod1.phi()
t_phi = time.time()
phi_tim = zidev.lastsampletime / zidev.clockbase

t_end = time.time()

print( "Sample value", sam_val )
print( "\nSam", sam_tim )
print( "  x", x_tim, x_val )
print( "  y", y_tim, y_val )
print( "  R", r_tim, r_val )
print( "phi", phi_tim, phi_val )

print( "\nT sam =", t_sam - t_start, "sec" )
print( "T x   =", t_x - t_sam, "sec,  dev =", x_tim - sam_tim )
print( "T y   =", t_y - t_x, "sec,  dev =", y_tim - x_tim )
print( "T r   =", t_r - t_y, "sec,  dev =", r_tim - y_tim )
print( "T phi =", t_phi - t_r, "sec,  dev =", phi_tim - r_tim )

print( "\noverall = ", t_end - t_start, " sec" )
