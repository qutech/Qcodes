# -*- coding: utf-8 -*-
"""
File: test_zimfli_BufferedParameter.py
Date: Aug 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: demonstrate the usage of BufferedParameter in qc.BufferedLoop
"""

import qcodes as qc
from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import zhinst.utils
import time


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
zhinst.utils.disable_everything( zidev.daq, zidev.device )

# Configure a Sweeper-Channel. All other settings are done via the BufferedLoop
sc = zidev.submodules['sweeper_channel']
sc.averaging_samples(1)
sc.averaging_tc(1.0)
sc.averaging_time(0.0)
sc.bandwidth_mode('fixed') # {'auto', 'fixed', 'current'}
#sc.bandwidth_overlap('OFF')
sc.bandwidth(1000.0)
sc.order(4)
sc.max_bandwidth(1250000.0)
sc.omega_suppression(40.0)
#sc.phaseunwrap() # on/off
#sc.sinc_filter() # on/off
sc.settling_time(1e-6)
sc.settling_inaccuracy(0.0001)
sc.history_length(100)

# Add all signals of interest for the resultant data set
#  'X', 'Y', 'R', 'phase',              => the sample measurements
#  'Xrms', 'Yrms', 'Rrms', 'phasePwr',  => the square values
#  'Freq', 'FreqPwr',                   => Frequency and its square
#  'In1', 'In2', 'In1Pwr', 'In2Pwr'     => Aux-Inputs and the squares
# The first parameter is the demodulator number and should be 1.
zidev.add_signal_to_sweeper( 1, 'In1'  )
zidev.add_signal_to_sweeper( 1, 'X' )
zidev.add_signal_to_sweeper( 1, 'Y' )
zidev.add_signal_to_sweeper( 1, 'R' )

# configure the rest of the device
amplitude=0.5
out_channel = 0
in_channel = 0
in_chanstring = 'Sig In {}'.format(in_channel+1)
demod_index = 0 # zero based!
osc_index = 0
demod_rate = 1e3
time_constant = 0.01
freq_start = 400e3
freq_stop  = 450e3
freq_step  =  10e3

sigin = zidev.submodules['signal_in{}'.format(in_channel+1)]
demod = zidev.submodules['demod{}'.format(demod_index+1)]
sigout= zidev.submodules['signal_out{}'.format(out_channel+1)]

# exp_setting = 
sigin.ac( 'OFF' )
sigin.range( 2*amplitude )
demod.streaming( 'ON' )
demod.samplerate( demod_rate )
demod.signalin( in_chanstring )
demod.order( 4 )
demod.timeconstant( time_constant )
demod.oscselect( osc_index )
demod.harmonic( 1 )
sigout.on( 'ON' )
sigout.enable( 'ON' )
sigout.range( 1 )
sigout.amplitude( amplitude )

# Wait for the demodulator filter to settle.
time.sleep(10*time_constant)

# Perform a global synchronisation between the device and the data server:
# Ensure that 1. the settings have taken effect on the device before issuing
# the poll() command and 2. clear the API's data buffers. Note: the sync()
# must be issued after waiting for the demodulator filter to settle above.
zidev.daq.sync()

# Possible sweep parameter:
# buffered_freq1, buffered_auxout1, buffered_auxout2, buffered_auxout3,
# buffered_auxout4, buffered_phase1, buffered_phase2, buffered_out1ampl2,
# buffered_out1off
# 'MD': buffered_phase3, buffered_phase4, buffered_freq2, buffered_out1ampl4,
#       buffered_out2ampl8, buffered_out2off

# build the qc loop object
#bf = zidev.buffered_freq1.sweep( freq_start, freq_stop, step=freq_step )
ba = zidev.buffered_auxout1.sweep( 0, 4, step=0.2 )
l  = qc.Repetition(2) \
       .buffered_loop(ba) \
       .each(zidev.buffered_result)

# run the loop and generate the data
data = l.run()

# print all informations about the internal sweep
zidev.buffered_freq1.debug()

# close the communication
zidev.close()
