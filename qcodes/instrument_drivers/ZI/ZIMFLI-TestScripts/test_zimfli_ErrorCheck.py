# -*- coding: utf-8 -*-
"""
File: test_zimfli_ErrorCheck.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to write all parameters from all modules, the values
         are from the readAll script, so we write the last read values.
         For testing more and more lines are commented out.
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import time


def wrhelper( mod, par, valarr ):
    for v in valarr:
        print( mod+"."+par, "=", v )
        try:
            zidev.submodules[mod].parameters[par]( v )
            time.sleep(3)
        except:
            print( "  --> Error." )


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# --- Main Device ---
#print( "========== Main Oscillator ==========" )
#freq = [ 0, 1e3, 100e3, 300e3, 1e6, 10e6, -10 ]
#for f in freq:
#    print( f, "Hz" )
#    try:
#        zidev.oscillator1_freq( f )
#        time.sleep(5)
#    except ValueError: # from parameter validator
#        print( "  -> Invalid value" )



# ---  demod1  ---
print( "========== Demodulator 1 ==========" )
#wrhelper( 'demod1', 'bypass', range(0,9) ) # range unclear
#wrhelper( 'demod1', 'phaseadjust', [-300, 0.0, +300, 0.0 ] ) # range unclear
#wrhelper( 'demod1', 'phaseshift', [-300, 0, +300 ] ) # clipped by instr. -180..+180
"""
wrhelper( 'demod1', 'timeconstant', 0.000815442472230643 )
wrhelper( 'demod1', 'samplerate', 1674.107177734375 )
wrhelper( 'demod1', 'sinc', 'OFF' ) validator
# ---  demod2  ---
wrhelper( 'demod2', 'bypass', 0 )
#wrhelper( 'demod2', 'frequency', 999999.99 )
wrhelper( 'demod2', 'order', 3 )
wrhelper( 'demod2', 'harmonic', 1.0 )
wrhelper( 'demod2', 'oscselect', 0 )
wrhelper( 'demod2', 'phaseadjust', 0 )
wrhelper( 'demod2', 'phaseshift', 0.0 )
wrhelper( 'demod2', 'timeconstant', 0.000815442472230643 )
wrhelper( 'demod2', 'samplerate', 1674.107177734375 )
wrhelper( 'demod2', 'sinc', 'OFF' )
wrhelper( 'demod2', 'signalin', 'Sig In 1' )
wrhelper( 'demod2', 'streaming', 'OFF' )
wrhelper( 'demod2', 'trigger', 'Continuous' )
# ---  signal_in1  ---
wrhelper( 'signal_in1', 'autorange', 0 )
wrhelper( 'signal_in1', 'range', 1.0 )
wrhelper( 'signal_in1', 'float', 'OFF' )
wrhelper( 'signal_in1', 'scaling', 1.0 )
wrhelper( 'signal_in1', 'AC', 'OFF' )
wrhelper( 'signal_in1', 'impedance', 'OFF' )
wrhelper( 'signal_in1', 'diff', 'OFF' )
wrhelper( 'signal_in1', 'max', 0.000946044921875 )
wrhelper( 'signal_in1', 'min', -0.000640869140625 )
wrhelper( 'signal_in1', 'on', 1 )
wrhelper( 'signal_in1', 'trigger', 0 )
# ---  aux_in1  ---
wrhelper( 'aux_in1', 'averaging', 15 ) validator
# ---  signal_out1  ---
wrhelper( 'signal_out1', 'add', 'OFF' )
wrhelper( 'signal_out1', 'autorange', 'OFF' )
wrhelper( 'signal_out1', 'differential', 'OFF' )
wrhelper( 'signal_out1', 'imp50', 'OFF' )
wrhelper( 'signal_out1', 'offset', 0.0 )
wrhelper( 'signal_out1', 'on', 'OFF' )
#wrhelper( 'signal_out1', 'overloaded', 0 )
wrhelper( 'signal_out1', 'range', 1.0 )
wrhelper( 'signal_out1', 'amplitude', 0.100006103515625 )
wrhelper( 'signal_out1', 'ampdef', 'Vpk' )
wrhelper( 'signal_out1', 'enable', 'ON' )
# ---  aux_out1  ---
wrhelper( 'aux_out1', 'scale', 1.0000041723251343 )
wrhelper( 'aux_out1', 'preoffset', 0.0 )
wrhelper( 'aux_out1', 'offset', 0.0 )
wrhelper( 'aux_out1', 'limitlower', -10.0 ) validator
wrhelper( 'aux_out1', 'limitupper', 10.0 ) validator
wrhelper( 'aux_out1', 'channel', 1 ) validator
wrhelper( 'aux_out1', 'output', 'Demod X' ) validator
#wrhelper( 'aux_out1', 'value', -8.349479321623221e-05 )
# ---  aux_out2  ---
wrhelper( 'aux_out2', 'scale', 0.9999821782112122 )
wrhelper( 'aux_out2', 'preoffset', 0.0 )
wrhelper( 'aux_out2', 'offset', 0.0 )
wrhelper( 'aux_out2', 'limitlower', -10.0 )
wrhelper( 'aux_out2', 'limitupper', 10.0 )
wrhelper( 'aux_out2', 'channel', 1 )
wrhelper( 'aux_out2', 'output', 'Demod Y' )
#wrhelper( 'aux_out2', 'value', 0.0 )
# ---  aux_out3  ---
wrhelper( 'aux_out3', 'scale', 1.0000007152557373 )
wrhelper( 'aux_out3', 'preoffset', 0.0 )
wrhelper( 'aux_out3', 'offset', 0.0 )
wrhelper( 'aux_out3', 'limitlower', -10.0 )
wrhelper( 'aux_out3', 'limitupper', 10.0 )
wrhelper( 'aux_out3', 'channel', 2 )
wrhelper( 'aux_out3', 'output', 'Demod X' )
#wrhelper( 'aux_out3', 'value', -8.350244024768472e-05 )
# ---  aux_out4  ---
wrhelper( 'aux_out4', 'scale', 1.0000072717666626 )
wrhelper( 'aux_out4', 'preoffset', 0.0 )
wrhelper( 'aux_out4', 'offset', 0.0 )
wrhelper( 'aux_out4', 'limitlower', -10.0 )
wrhelper( 'aux_out4', 'limitupper', 10.0 )
wrhelper( 'aux_out4', 'channel', 2 )
wrhelper( 'aux_out4', 'output', 'Demod Y' )
#wrhelper( 'aux_out4', 'value', 0.0 )
# ---  trigger_in1  ---
wrhelper( 'trigger_in1', 'autothreshold', 'OFF' )
wrhelper( 'trigger_in1', 'level', 0.4981684982776642 )
# ---  trigger_in2  ---
wrhelper( 'trigger_in2', 'autothreshold', 'OFF' )
wrhelper( 'trigger_in2', 'level', 0.4981684982776642 )
# ---  trigger_out1  ---
wrhelper( 'trigger_out1', 'pulsewidth', 5.000000058430487e-08 )
wrhelper( 'trigger_out1', 'source', 'disabled' )
# ---  trigger_out2  ---
wrhelper( 'trigger_out2', 'pulsewidth', 5.000000058430487e-08 )
wrhelper( 'trigger_out2', 'source', 'disabled' )
# ---  dio  ---
wrhelper( 'dio', 'decimation', 3000000 )
wrhelper( 'dio', 'drive', 15 )
wrhelper( 'dio', 'extclk', 'OFF' )
wrhelper( 'dio', 'mode', 'Manual' )
wrhelper( 'dio', 'output', 0 )
"""

