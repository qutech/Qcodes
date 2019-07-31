# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 14:35:14 2019

@author: m.wagener

Test: qc.loop over the amplitude of the signal out channel
      and sweep the qscillator frequency at each point
"""


# Imports
import qcodes as qc
from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI

# Create device and connect to the hardware
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# Configure a Sweeper-Channel the same way as done with the GUI
sc = zidev.submodules['sweeper_channel']

# Select the sweep parameter. Possible values (for tested Lock-In) are:
#  'Aux Out 1 Offset', 'Aux Out 2 Offset', 'Aux Out 3 Offset', 'Aux Out 4 Offset',
#  'Demod 1 Phase Shift', 'Demod 2 Phase Shift', 'Osc 1 Frequency',
#  'Output 1 Amplitude 2', 'Output 1 Offset'
sc.param('Osc 1 Frequency')

# Select the start and stop value for the sweep
sc.start(1000.0)
sc.stop( 5000.0)

# Set the number of sweep-steps
sc.samplecount(16)
sc.loopcount(1)

# we make only one sweep
sc.endless('OFF')

# set some other parameters - here espacially for the frequency sweep
sc.averaging_samples(1)
sc.averaging_tc(0.0)
sc.averaging_time(0.0)
sc.bandwidth_mode('fixed') # {'auto', 'fixed', 'current'}
#sc.bandwidth_overlap('OFF')
sc.bandwidth(1000.0)
sc.order(4)
sc.max_bandwidth(1250000.0)
sc.omega_suppression(40.0)
#sc.phaseunwrap() # on/off
#sc.sinc_filter() # on/off

# Set the sweep mode and the timing
sc.mode('sequential') # {'sequential', 'binary', 'biderectional', 'reverse'}
sc.settling_time(1e-6)
sc.settling_inaccuracy(0.0001)
sc.xmapping('linear') # {'linear': 0, 'logarithmic': 1}
sc.history_length(100)

# Add all signals of interest for the resultant data set
#  'X', 'Y', 'R', 'phase',              => the sample measurements
#  'Xrms', 'Yrms', 'Rrms', 'phasePwr',  => the square values
#  'Freq', 'FreqPwr',                   => Frequency and its square
#  'In1', 'In2', 'In1Pwr', 'In2Pwr'     => Aux-Inputs and the squares
# The first parameter is the demodulator number
zidev.add_signal_to_sweeper( 1, 'In1'  )
#zidev.add_signal_to_sweeper( 1, 'Freq' )

# generate the internal sweep data structure
sw = zidev.Sweep
sw.build_sweep()
print( "Estimated Sweep Time", sc.sweeptime() )

zidev.print_sweeper_settings()


# Setup the loop of the output voltage
out_channel = 0
sigout= zidev.submodules['signal_out{}'.format(out_channel+1)]
parsigout = sigout.amplitude # loop over the amplitude
sigout.differential( 'OFF' )
sigout.range( 1 )
sigout.on( 'ON' )
sigout.enable( 'ON' )

# On the ZIMFLI: connect "Signal Output +V" with "Aux Input 1"

# define the loop and run it ...
loop = qc.Loop( parsigout.sweep(0.1, 1.0, 0.1), delay=0.1 ).each( sw )
data = loop.run()
# the resultant data will be printed automatically...
#print('----------------------------------------------')
#print(data)
#print('----------------------------------------------')

# close the device to restart easily
zidev.close()
