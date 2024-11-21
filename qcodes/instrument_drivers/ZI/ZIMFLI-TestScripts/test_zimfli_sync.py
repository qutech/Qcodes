# -*- coding: utf-8 -*-
"""
File: test_zimfli_sync.py
Date: Jan 2020
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: demonstrate the usage of sync w/o BufferedLoop
"""

# TODO docstrings: google-style

#import qcodes as qc
from qcodes.instrument_drivers.ZI.ZIMFLI import ZIMFLI
#import zhinst.utils
import time
from qcodes.instrument.sync import ExplicitSync # Sync, RepeatedSync
# for pretty print the data dict
import json

import numpy as np


# Open Device. Be sure that the device-id is correct
zidev = ZIMFLI( name='ZIMFLI', device_ID='DEV4039' )

# Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
#zhinst.utils.disable_everything( zidev.daq, zidev.device )

# Add all signals of interest for the resultant data set
#  'X', 'Y', 'R', 'phase',              => the sample measurements
#  'Xrms', 'Yrms', 'Rrms', 'phasePwr',  => the square values
#  'Freq', 'FreqPwr',                   => Frequency and its square
#  'In1', 'In2', 'In1Pwr', 'In2Pwr'     => Aux-Inputs and the squares
# The first parameter is the demodulator number and should be 1.
#zidev.add_signal_to_sweeper( 1, 'In1'  )
#zidev.add_signal_to_sweeper( 1, 'X' )
#zidev.add_signal_to_sweeper( 1, 'Y' )
#zidev.add_signal_to_sweeper( 1, 'R' ) # TODO: diese Parmeter . sync_get()

# Possible sweep parameter:
# buffered_freq1, buffered_auxout1, buffered_auxout2, buffered_auxout3,
# buffered_auxout4, buffered_phase1, buffered_phase2, buffered_out1ampl2,
# buffered_out1off
# 'MD': buffered_phase3, buffered_phase4, buffered_freq2, buffered_out1ampl4,
#       buffered_out2ampl8, buffered_out2off

# -1- Sync-Objekt anlegen und die Ausgabe definieren

mysync = ExplicitSync(np.array([0, 2, 4]),  # Time points of Sync
                      np.array([1, 1, 1]))  # Duration of each measurement

mysync = zidev.sync_auxout1.sync_set([0.0, 0.2, 0.4],  # Output values
                                     mysync )          # Sync object
"""
# Prüfe auf Lin/Log Achse für den Sweeper:
x = np.arange(30, dtype=float)
len(set(np.diff(a))) == 1  # -> äquidistant

dx=np.diff(a)
np.allclose(diff(dx))
"""

# Debugausgabe
mysync.debug()

get_x   = zidev.sync_x.sync_get(mysync)
get_phi = zidev.sync_phase.sync_get(mysync)

print("---- run ----")
mysync.execute()
# dieses execute() macht nur das prepare(). Es wird danach auf einen Trigger gewartet !!!!

zidev.run()

# print all informations about the internal sweep
#print("---- Sweeper settings ----")
#zidev.print_sweeper_settings()

print("---- experiment is running ----")
for i in range(20):
    time.sleep(2)
    if not zidev.sync_x.is_running():
        break

print("---- try to get the data ----")

data_x = get_x()
data_phi = get_phi()
#print(data)
print( 'X', json.dumps( data_x, indent=4 ) )
print( 'phase', json.dumps( data_phi, indent=4 ) )

# close the communication
zidev.close()


# TODO: loggimg-modul statt print()
# numba soll eine gute Alternative zu numpy sein ...


"""
sync = mfli.freq.sync_set([1,10,100])
get_x = mfli.x.sync_get(sync)
get_phi = mfli.phi.sync_get(sync)
sync.execute()
x = get_x()
phi = get_phi()

--- mit DecaDac als Sweeper muss der Lockin nur regelmäßig messen (DAQ-Modul)
sync = dac.channel1.sync_set([-1,0,1])
get_x = mfli.x.sync_get(sync)
get_phi = mfli.phi.sync_get(sync)
sync.execute()
x = get_x()
phi = get_phi()



GIT: RWTH im Branch featrue/sync_instruments pushen, Pull-Req. in RWTH Master ist angefragt vom Simon.
Als Draft markieren.
"""
