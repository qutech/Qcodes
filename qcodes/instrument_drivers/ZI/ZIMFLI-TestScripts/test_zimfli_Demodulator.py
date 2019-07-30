# -*- coding: utf-8 -*-
"""
File: test_zimfli_Demodulator.py
Date: Feb 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to test the demodulator functionality
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import time

# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

#print( "--- Version informations: ---" )
#print( zidev.version() )

# "demod1" is the first line in the web interface
dm1 = zidev.submodules["demod1"]
dm1.oscselect(0)
print("freuqency of demodulator1:", dm1.frequency())
#dm1.signalin("Sig In 1")
#dm1.streaming("ON")

# "demod2" is the second line in the web interface with less parameters
dm2 = zidev.submodules["demod2"]
dm2.oscselect(0)
print("freuqency of demodulator2:", dm2.frequency())

#Select the Signal Input of the demodulator as constant input and print out a sample
dm1.signalin('Constant input')
#print("Sample of demodulator1:", dm1.sample())
print(" x  of demodualtor1:", dm1.x())
print(" y  of demodulator1:", dm1.y())
print(" R  of demodulator1:", dm1.R())
print("phi of demodualtor1:", dm1.phi())
#Set the harmonic factor of the demodulator to 2 and print out the frequency
dm1.harmonic(2)  # Ref freq multiplication factor
time.sleep(0.2)
print("frequency of demodulator1", dm1.frequency())

print(" x  of demodualtor1:", dm1.x())
print(" y  of demodulator1:", dm1.y())
print(" R  of demodulator1:", dm1.R())
print("phi of demodualtor1:", dm1.phi())

dm1.bypass(0)  # Use low-pass filter (1=bypass filter) ??
dm1.order(1)   # set the low-pass filter order value
print("Phaseadjust:", dm1.phaseadjust())
print(" Phaseshift:", dm1.phaseshift())
print("Filter time constant:", dm1.timeconstant())
print("Sampling rate:", dm1.samplerate())
print("SAMPLE:", dm1.sample())  # Read only
print("Sinc Flag:", dm1.sinc())
print("Streaming:", dm1.streaming())  # Enable-Command !
print("Trigger:", dm1.trigger())
