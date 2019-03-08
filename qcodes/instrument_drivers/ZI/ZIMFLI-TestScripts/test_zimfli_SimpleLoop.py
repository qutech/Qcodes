# -*- coding: utf-8 -*-
"""
File: test_zimfli_SimpleLoop.py
Date: Feb 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program for the example from Chapter 3.1 of the ziMFLI User Manual
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import time

# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

#print( "--- Version informations: ---" )
#print( zidev.version() )

# Oscillator to 300kHz with readback
print("current freuqency oscillator1:", zidev.oscillator1_freq())
zidev.oscillator1_freq( 300000.0 )
time.sleep( 0.1 )
print("freuqency of oscillator1 now:", zidev.oscillator1_freq())

# Configure SignalOutput
sigout = zidev.submodules["signal_out1"]
sigout.amplitude(0.5)  # Amplitude set to 500mV
sigout.enable('ON')    # Output set to enabled
sigout.range(1)        # set range to 1V
sigout.offset(0)       # set offset to 0V
sigout.on('ON')        # Turn output on

# Configure the SignalInput
sigin = zidev.submodules["signal_in1"]
sigin.range(1)   # set range to 1V
sigin.AC('OFF')  # set AC off
sigin.impedance('OFF')  # set 50 Ohm off
sigin.diff('OFF')       # set differential mode off
sigin.float('OFF')      # set floating off

# the visualization with the Scope will be done via Webinterface
print("Finished. See Webinterface -> Scope.")
