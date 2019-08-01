# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 14:35:14 2019

@author: m.wagener
"""


#import numpy as np

#import qcodes as qc
#from qcodes.instrument.parameter import BufferedSweepableParameter
#from qcodes.utils.validators import Numbers
from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI

zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# Configure a Sweeper-Channel the same way as done with the GUI
# (parameters are used in order of parameter-coding in driver)
sc = zidev.submodules['sweeper_channel']
# Select the sweep parameter. Possible values (for tested Lock-In) are:
#  'Aux Out 1 Offset', 'Aux Out 2 Offset', 'Aux Out 3 Offset', 'Aux Out 4 Offset',
#  'Demod 1 Phase Shift', 'Demod 2 Phase Shift', 'Osc 1 Frequency',
#  'Output 1 Amplitude 2', 'Output 1 Offset'
sc.param('Osc 1 Frequency')

sc.start(   1000.0)
sc.stop(   50000.0)
sc.samplecount(16)
sc.endless('OFF')
sc.averaging_samples(1)
sc.averaging_tc(0.0)
sc.averaging_time(0.0)
sc.bandwidth_mode('fixed') # {'auto', 'fixed', 'current'}
#sc.bandwidth_overlap('OFF')
sc.bandwidth(1000.0)
sc.order(4)
sc.max_bandwidth(1250000.0)
sc.omega_suppression(40.0)
sc.loopcount(1)
#sc.phaseunwrap() # on/off
#sc.sinc_filter() # on/off
sc.mode('sequential') # {'sequential', 'binary', 'biderectional', 'reverse'}
sc.settling_time(1e-6)
sc.settling_inaccuracy(0.0001)
sc.xmapping('linear') # {'linear': 0, 'logarithmic': 1}
sc.history_length(100)

# Add all signals of interest to the list to generate the return list of arrays
#  'X', 'Y', 'R', 'phase',              => the sample measurements
#  'Xrms', 'Yrms', 'Rrms', 'phasePwr',  => the square values
#  'Freq', 'FreqPwr',                   => Frequency and its square
#  'In1', 'In2', 'In1Pwr', 'In2Pwr'     => Aux-Inputs and the squares
zidev.add_signal_to_sweeper( 1, 'X' )
zidev.add_signal_to_sweeper( 1, 'Freq' )

sw = zidev.Sweep
sw.build_sweep()

zidev.print_sweeper_settings()

print( "Est. Sweep Time", sc.sweeptime() )

data = sw.get()
print(data)

zidev.close()
