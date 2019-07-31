# -*- coding: utf-8 -*-
"""
File: test_zimfli_Buffered.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to check the poll functtion (blocking call to get data)
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import zhinst.utils
import time


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
zhinst.utils.disable_everything( zidev.daq, zidev.device )

# Now configure the instrument for this experiment. The following channels
# and indices work on all device configurations. The values below may be
# changed if the instrument has multiple input/output channels and/or either
# the Multifrequency or Multidemodulator options installed.
amplitude=0.5
out_channel = 0
in_channel = 0
in_chanstring = 'Sig In 1'
demod_index = 0 # zero based!
osc_index = 0
demod_rate = 1e3
time_constant = 0.01
frequency = 400e3
# out_mixer_channel = zhinst.utils.default_output_mixer_channel(zidev.props)

sigin = zidev.submodules['signal_in{}'.format(in_channel+1)]
demod = zidev.submodules['demod{}'.format(demod_index+1)]
sigout= zidev.submodules['signal_out{}'.format(out_channel+1)]

# exp_setting = 
sigin.ac( 'OFF' )             # ['/%s/sigins/%d/ac'             % (device, in_channel), 0],
sigin.range( 2*amplitude )    # ['/%s/sigins/%d/range'          % (device, in_channel), 2*amplitude],
demod.streaming( 'ON' )       # ['/%s/demods/%d/enable'         % (device, demod_index), 1],
demod.samplerate( demod_rate ) # ['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
demod.signalin( in_chanstring ) # ['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
demod.order( 4 )              # ['/%s/demods/%d/order'          % (device, demod_index), 4],
demod.timeconstant( time_constant ) # ['/%s/demods/%d/timeconstant'   % (device, demod_index), time_constant],
demod.oscselect( osc_index )  # ['/%s/demods/%d/oscselect'      % (device, demod_index), osc_index],
demod.harmonic( 1 )           # ['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
zidev.oscillator1_freq( frequency ) # ['/%s/oscs/%d/freq'             % (device, osc_index), frequency],
sigout.on( 'ON' )             # ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
sigout.enable( 'ON' )         # ['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1],
sigout.range( 1 )             # ['/%s/sigouts/%d/range'         % (device, out_channel), 1],
sigout.amplitude( amplitude ) # ['/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), amplitude]
#daq.set(exp_setting)

# Unsubscribe any streaming data.
zidev.daq.unsubscribe('*')

# Wait for the demodulator filter to settle.
time.sleep(10*time_constant)

# Perform a global synchronisation between the device and the data server:
# Ensure that 1. the settings have taken effect on the device before issuing
# the poll() command and 2. clear the API's data buffers. Note: the sync()
# must be issued after waiting for the demodulator filter to settle above.
zidev.daq.sync()

total_time = 5 # sec
sample = zidev.bufferedReader( demod_index+1, total_time, dolog=True, copyFreq=True,
                       copyPhase=True, copyDIO=True, copyTrigger=True, copyAuxin=True )
#    def bufferedReader( self, demod_index, total_time, dolog=False, copyFreq=False,
#                       copyPhase=False, copyDIO=False, copyTrigger=False, copyAuxin=False ):

print( len(sample['x']) )
print( sample.keys() )
