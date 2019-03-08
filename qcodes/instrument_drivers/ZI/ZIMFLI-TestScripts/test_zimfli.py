# -*- coding: utf-8 -*-
"""
File: test_zimfli.py
Date: Feb 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: First steps to get in touch with the instrument
"""


#import qcodes as qc
from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import time

zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

#print( "--- Version informations: ---" )
#print( zidev.version() )

#print("freuqency oscillator1:", zidev.oscillator1_freq())
#zidev.oscillator1_freq( 75000.0 )
#time.sleep( 0.1 )
#print("freuqency oscillator1:", zidev.oscillator1_freq())

#demodulator = zidev.submodules["demod1"]
#demodulator.oscselect(0)
#print("freuqency of demodulator1:", demodulator.frequency())

#demodulator2 = zidev.submodules["demod2"]
#demodulator2.oscselect(0)
#print("freuqency of demodulator2:", demodulator2.frequency())

#Select the Signal Input of the demodulator as constant input and print out a sample
#demodulator.signalin('Constant input')
#print("Sample of demodulator1:", demodulator.sample())
#print("x of demodualtor1:", demodulator.x())
#print("y of demodulator1:", demodulator.y())
#print("R of demodulator1:", demodulator.R())
#print("phi of demodualtor1:", demodulator.phi())
#Set the harmonic factor of the demodulator to 2 and print out the frequency
#demodulator.harmonic(2)
#print("frequency of demodulator1", demodulator.frequency())

"""
Program for the example from Chapter 3.1 of the ziMFLI User Manual
"""
# Oscillator to 300kHz with readback
print("current freuqency oscillator1:", zidev.oscillator1_freq())
zidev.oscillator1_freq( 300000.0 )
time.sleep( 0.1 )
print("freuqency of oscillator1 now:", zidev.oscillator1_freq())

# Output Amplitude set to 500mV and output enabled
sigout = zidev.submodules["signal_out1"]
sigout.amplitude(0.5)
sigout.enable('ON')

# Range to 1V and Offset to 0V
sigout.range(1)
sigout.offset(0)

# Turn output on
sigout.on('ON')

