# -*- coding: utf-8 -*-
"""
File: test_zimfli_Scope.py
Date: Feb / Mar 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Program to check the scope function.
         NOT FINISHED YET!
"""


from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
import zhinst.utils
import time
import numpy as np


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

scope = zidev.parameters['Scope']

# Im folgenden wird das ZI-Beispiel example_scope.py so umgesetzt, dass es
# mit dem Treiber arbeitet.

# Zum Test sind die Signalausgänge 1 und 2 auf die Signaleingänge 1 und 2 gelegt

# Die Parameter des Beispiels sind hier lokale Variablen:
do_plot=False
scope_inputselect=0
scope_length=2**12
scope_trigholdoff=0.050
sigouts_amplitude=0.5
sigouts_range=1.5
module_averager_weight=1
module_historylength=20
min_num_records=20

# Reset device and disable all
zhinst.utils.disable_everything( zidev.daq, zidev.device )

# Determine the sigin/sigout channels to configure based on the specified scope inputselect.
if scope_inputselect == 0:
    # inputselect 0 corresponds to signal input 1
    out_channel = 0
    in_channel = 0
    scope_inputstring = 'Signal Input 1'
elif scope_inputselect == 1:
    # inputselect 0 corresponds to signal input 2
    out_channel = 1
    in_channel = 1
    scope_inputstring = 'Signal Input 2'
else:
    raise Exception("This example only supports signal inputs; it does not support scope inputselect {}. "
                    "Use 0 or 1 instead.".format(scope_inputselect))

# Get the value of the instrument's default Signal Output mixer channel.
out_mixer_channel = zhinst.utils.default_output_mixer_channel( zidev.props,
                                                              output_channel=out_channel )
print( "out mixer =", out_mixer_channel )

osc_index = 0
scope_in_channel = 0  # scope input channel
frequency = 100.0e3 # Wir haben die F5M Option installiert, geht also bis 5MHz
# exp_settings = [...]
sigout = zidev.submodules['signal_out{}'.format(out_channel+1)]
sigin  = zidev.submodules['signal_in{}'.format(in_channel+1)]

sigout.on( 'ON' )                     # ['/%s/sigouts/%d/on'             % (device, out_channel), 1],
sigout.range( sigouts_range )         # ['/%s/sigouts/%d/range'          % (device, out_channel), sigouts_range],
sigout.amplitude( sigouts_amplitude ) # ['/%s/sigouts/%d/amplitudes/%d'  % (device, out_channel, out_mixer_channel), sigouts_amplitude],
sigout.enable( 'ON' )                 # ['/%s/sigouts/%d/enables/%d'     % (device, out_channel, out_mixer_channel), 1],
sigin.impedance( 'ON' )               # ['/%s/sigins/%d/imp50'           % (device, in_channel), 1],
sigin.ac( 'OFF' )                     # ['/%s/sigins/%d/ac'              % (device, in_channel), 0],
        # We will use autorange to adjust the sigins range.
        # ['/%s/sigins/%d/range'           % (device, in_channel), 2*sigouts_amplitude],
zidev.oscillator1_freq( frequency )   # ['/%s/oscs/%d/freq'              % (device, osc_index), frequency]]
#    node_branches = daq.listNodes('/{}/'.format(device), 0)
#    if 'DEMODS' in node_branches:
        # NOTE we don't need any demodulator data for this example, but we need
        # to configure the frequency of the output signal on out_mixer_c.
demod = zidev.submodules['demod{}'.format(out_mixer_channel)]
demod.oscselect( osc_index )
# exp_setting.append(['/%s/demods/%d/oscselect' % (device, out_mixer_channel), osc_index])
#    daq.set(exp_setting)


# Perform a global synchronisation between the device and the data server:
# Ensure that the signal input and output configuration has taken effect
# before calculating the signal input autorange.
#daq.sync()
zidev.daq.sync()

# Perform an automatic adjustment of the signal inputs range based on the
# measured input signal's amplitude measured over approximately 100 ms.
# This is important to obtain the best bit resolution on the signal inputs
# of the measured signal in the scope.
zhinst.utils.sigin_autorange( zidev.daq, zidev.device, in_channel )

scchan  = zidev.submodules['scope_channel{}'.format(in_channel+1)]
subchan = scchan.submodules['channel1']

####################################################################################################################
# Configure the scope and obtain data with triggering disabled.
####################################################################################################################

# Configure the instrument's scope via the /devx/scopes/0/ node tree branch.
# 'length' : the length of each segment
# daq.setInt('/%s/scopes/0/length' % device, scope_length)
scchan.length( scope_length )

# 'channel' : select the scope channel(s) to enable.
#  Bit-encoded as following:
#   1 - enable scope channel 0
#   2 - enable scope channel 1
#   3 - enable both scope channels (requires DIG option)
# NOTE we are only interested in one scope channel: scope_in_channel and leave
# the other channel unconfigured
#daq.setInt('/%s/scopes/0/channel' % device, 1)
scchan.scope_channels( 1 )

# 'channels/0/bwlimit' : bandwidth limit the scope data. Enabling bandwidth
# limiting avoids antialiasing effects due to subsampling when the scope
# sample rate is less than the input channel's sample rate.
#  Bool:
#   0 - do not bandwidth limit
#   1 - bandwidth limit
#daq.setInt('/%s/scopes/0/channels/%d/bwlimit' % (device, scope_in_channel), 1)
subchan.bw_limitation( 'ON' )

# 'channels/0/inputselect' : the input channel for the scope:
#   0 - signal input 1
#   1 - signal input 2
#   2, 3 - trigger 1, 2 (front)
#   8-9 - auxiliary inputs 1-2
#   The following inputs are additionally available with the DIG option:
#   10-11 - oscillator phase from demodulator 3-7
#   16-23 - demodulator 0-7 x value
#   32-39 - demodulator 0-7 y value
#   48-55 - demodulator 0-7 R value
#   64-71 - demodulator 0-7 Phi value
#   80-83 - pid 0-3 out value
#   96-97 - boxcar 0-1
#   112-113 - cartesian arithmetic unit 0-1
#   128-129 - polar arithmetic unit 0-1
#   144-147 - pid 0-3 shift value
#daq.setInt('/%s/scopes/0/channels/%d/inputselect' % (device, scope_in_channel), scope_inputselect)
subchan.input_select( scope_inputstring )

# 'time' : timescale of the wave, sets the sampling rate to clockbase/2**time.
#   0 - sets the sampling rate to 1.8 GHz
#   1 - sets the sampling rate to 900 MHz
#   ...
#   16 - sets the samptling rate to 27.5 kHz
scope_time = 0
#daq.setInt('/%s/scopes/0/time' % device, scope_time)
scchan.samplingrate( '7.5 MHz' )
print( "DBG: Samplingrate (time) =", scchan.samplingrate() )

# 'single' : only get a single scope record.
#   0 - acquire continuous records
#   1 - acquire a single record
#daq.setInt('/%s/scopes/0/single' % device, 0)
scchan.singleshot( 'OFF' )

# 'trigenable' : enable the scope's trigger (boolean).
#   0 - acquire continuous records
#   1 - only acquire a record when a trigger arrives
#daq.setInt('/%s/scopes/0/trigenable' % device, 0)
scchan.trig_enable( 'ON' ) # Manual says: ON=0, OFF=1

# 'trigholdoff' : the scope hold off time inbetween acquiring triggers (still relevant if triggering is disabled).
#daq.setDouble('/%s/scopes/0/trigholdoff' % device, scope_trigholdoff)
scchan.scope_trig_holdoffseconds( scope_trigholdoff )

# 'segments/enable' : Disable segmented data recording.
#daq.setInt('/%s/scopes/0/segments/enable' % device, 0)
scchan.scope_segments( 'OFF' )

"""
# Now initialize and configure the Scope Module.
scopeModule = daq.scopeModule()
# 'scopeModule/mode' : Scope data processing mode.
# 0 - Pass through scope segments assembled, returned unprocessed, non-interleaved.
# 1 - Moving average, scope recording assembled, scaling applied, averaged, if averaging is enabled.
# 2 - Not yet supported.
# 3 - As for mode 1, except an FFT is applied to every segment of the scope recording.
scopeModule.set('scopeModule/mode', 1)
# 'scopeModule/averager/weight' : Averager behaviour.
#   weight=1 - don't average.
#   weight>1 - average the scope record shots using an exponentially weighted moving average.
scopeModule.set('scopeModule/averager/weight', module_averager_weight)
# 'scopeModule/historylength' : The number of scope records to keep in the Scope Module's memory, when more records
#   arrive in the Module from the device the oldest records are overwritten.
scopeModule.set('scopeModule/historylength', module_historylength)

# Subscribe to the scope's data in the module.
wave_nodepath = '/{}/scopes/0/wave'.format(device)
scopeModule.subscribe(wave_nodepath)

# Enable the scope and read the scope data arriving from the device.
data_no_trig = get_scope_records(device, daq, scopeModule, min_num_records)
assert wave_nodepath in data_no_trig, "The Scope Module did not return data for {}.".format(wave_nodepath)
print('Number of scope records with triggering disabled: {}.'.format(len(data_no_trig[wave_nodepath])))
check_scope_record_flags(data_no_trig[wave_nodepath])

####################################################################################################################
# Configure the scope and obtain data with triggering enabled.
####################################################################################################################

# Now configure the scope's trigger to get aligned data
# 'trigenable' : enable the scope's trigger (boolean).
#   0 - acquire continuous records
#   1 - only acquire a record when a trigger arrives
daq.setInt('/%s/scopes/0/trigenable' % device, 1)

# Specify the trigger channel, we choose the same as the scope input
daq.setInt('/%s/scopes/0/trigchannel' % device, in_channel)

# Trigger on rising edge?
daq.setInt('/%s/scopes/0/trigrising' % device, 1)

# Trigger on falling edge?
daq.setInt('/%s/scopes/0/trigfalling' % device, 0)

# Set the trigger threshold level.
daq.setDouble('/%s/scopes/0/triglevel' % device, 0.00)

# Set hysteresis triggering threshold to avoid triggering on noise
# 'trighysteresis/mode' :
#  0 - absolute, use an absolute value ('scopes/0/trighysteresis/absolute')
#  1 - relative, use a relative value ('scopes/0trighysteresis/relative') of the trigchannel's input range
#      (0.1=10%).
daq.setDouble('/%s/scopes/0/trighysteresis/mode' % device, 1)
daq.setDouble('/%s/scopes/0/trighysteresis/relative' % device, 0.1)  # 0.1=10%

# Set the trigger hold-off mode of the scope. After recording a trigger event, this specifies when the scope should
# become re-armed and ready to trigger, 'trigholdoffmode':
#  0 - specify a hold-off time between triggers in seconds ('scopes/0/trigholdoff'),
#  1 - specify a number of trigger events before re-arming the scope ready to trigger ('scopes/0/trigholdcount').
daq.setInt('/%s/scopes/0/trigholdoffmode' % device, 0)
daq.setDouble('/%s/scopes/0/trigholdoff' % device, scope_trigholdoff)

# The trigger reference position relative within the wave, a value of 0.5 corresponds to the center of the wave.
daq.setDouble('/%s/scopes/0/trigreference' % device, 0.25)

# Set trigdelay to 0.: Start recording from when the trigger is activated.
daq.setDouble('/%s/scopes/0/trigdelay' % device, 0.0)

# Disable trigger gating.
daq.setInt('/%s/scopes/0/triggate/enable' % device, 0)

# Perform a global synchronisation between the device and the data server:
# Ensure that the settings have taken effect on the device before acquiring
# data.
daq.sync()

# Enable the scope and read the scope data arriving from the device. Note: The module is already configured and the
# required data is already subscribed from above.
data_with_trig = get_scope_records(device, daq, scopeModule, min_num_records)

assert wave_nodepath in data_with_trig, "The Scope Module did not return data for {}.".format(wave_nodepath)
print('Number of scope records returned with triggering enabled: {}.'.format(len(data_with_trig[wave_nodepath])))
check_scope_record_flags(data_with_trig[wave_nodepath])

####################################################################################################################
# Configure the Scope Module to calculate FFT data
####################################################################################################################

# Set the Scope Module's mode to return frequency domain data.
scopeModule.set('scopeModule/mode', 3)
# Use a Hann window function.
scopeModule.set('scopeModule/fft/window', 1)

# Enable the scope and read the scope data arriving from the device; the Scope Module will additionally perform an
# FFT on the data. Note: The other module parameters are already configured and the required data is already
# subscribed from above.
data_fft = get_scope_records(device, daq, scopeModule, min_num_records)
assert wave_nodepath in data_fft, "The Scope Module did not return data for {}.".format(wave_nodepath)
print("Number of scope records returned with triggering enabled (and FFT'd): {}.".format(
    len(data_fft[wave_nodepath])))
check_scope_record_flags(data_fft[wave_nodepath])

# We no longer need the module; we can now destroy it (stop its thread and remove it from memory):
scopeModule.clear()

return data_no_trig, data_with_trig, data_fft

"""

# Perform a global synchronisation between the device and the data server:
# Ensure that the settings have taken effect on the device before acquiring
# data.
zidev.daq.sync()






#scope.prepare_scope()
# Jetzt ist das Script in einer Version, dass der DataServer im Gerät
# abgeschossen worden ist.
