# -*- coding: utf-8 -*-
"""
File: used_rwth_commands.py
Date: Juni 2019
Author: Michael Wagener, ZEA-2, m.wagener@fz-juelich.de
Purpose: Usage of the same commands as the RWTH MatLAB script
"""


from qcodes.instrument_drivers.rohde_schwarz.SMW200A import RohdeSchwarz_SMW200A as smw200a
import time

dev = smw200a( name='SMW200A', address='TCPIP::134.61.7.134::hislip0::INSTR' )

#print( "--- device informations ---" )
#print( "ID:", dev.get_id() )
#print( "Options:", dev.get_options() )
#print()

print( "--- set commands ---" )

"""
Please uncomment a group if you want to test this special set command.
"""

## fprintf(RSVec,['SOUR:FREQ:CENT ' num2str(19.9e9) 'Hz']);
#print( "'SOUR:FREQ:CENT '  -> OutputChannel::sweep_center(...)" )
#dev.submodules['rfoutput1'].sweep_center( 19.9e9 )
#print( dev.get_error()[0] ) -> Data out of range

## fprintf(RSVec,'SOUR:FREQ:SPAN 200000000 Hz');
#print( "'SOUR:FREQ:SPAN ... Hz' -> OutputChannel::sweep_span(...)" )
#dev.submodules['rfoutput1'].sweep_span( 200000000 )
#print( dev.get_error()[0] )

## fprintf(RSVec,'SOUR:SWE:FREQ:STEP:LIN 2000000 Hz');
#print( "'SOUR:SWE:FREQ:STEP:LIN ... Hz' -> OutputFrequencySweep::lin_step(...)" )
#dev.submodules['freq_sweep1'].lin_step( 2000000 )
#print( dev.get_error()[0] )

## fprintf(RSVec,'SOUR1:FREQ:MODE CW');
#print( "'SOUR1:FREQ:MODE CW' -> OutputChannel::mode(...)" )
#dev.submodules['rfoutput1'].mode( 'CW' )
#print( dev.get_error()[0] )

## fprintf(RSVec,'SOUR1:SWE:RES:ALL');
#print( "'SOUR1:SWE:RES:ALL' -> OutputFrequencySweep::reset" )
#dev.submodules['freq_sweep1'].reset
#print( dev.get_error()[0] )

## fprintf(RSVec,'SOUR1:IQ:STAT 0');
#dev.submodules['IQmod1'].state('ON') # activate first, so that it can be deactivated afterwards
#print( "'SOUR1:IQ:STAT 0' -> IQModulation::state(...)" )
#dev.submodules['IQmod1'].state('OFF')
#print( dev.get_error()[0] )

## fprintf(RSVec,'SOUR1:FM1:STAT 1');
#print( "'SOUR1:FM1:STAT 1' -> FrequencyModulation::state(...)" )
#dev.submodules['fm1_1'].state( "ON" )
#print( dev.get_error()[0] )
#time.sleep(0.5)
#dev.submodules['fm1_1'].state( 'OFF' ) # for this test only

## fprintf(RSVec,'SOUR1:FM1:DEV 160000000');
#print( "'SOUR1:FM1:DEV ...' -> FrequencyModulation::deviation(...)" )
#dev.submodules['fm1_1'].deviation( 160000000 )
#print( dev.get_error()[0] )


print()
print( "--- query commands ---" )

print( "query(RSVec,'SOUR:POW?')        -> OutputChannel::level()        ", \
      dev.submodules['rfoutput1'].level() )

print( "query(RSVec,'SOUR:PULM:STATE?') -> PulseModulation::state()      ", \
      dev.submodules['pulsemod1'].state() )

print( "query(RSVec,'SOUR:FREQ?')       -> OutputChannel::frequency()    ", \
      dev.submodules['rfoutput1'].frequency() )

print( "query(RSVec,'SOUR:FREQ:STOP?')  -> OutputChannel::sweep_stop()   ", \
      dev.submodules['rfoutput1'].sweep_stop() )

print( "query(RSVec,'SOUR:FREQ:STAR?')  -> OutputChannel::sweep start()  ", \
      dev.submodules['rfoutput1'].sweep_start() )

print( "query(RSVec,'SOUR:FREQ:CENT?')  -> OutputChannel::sweep center() ", \
      dev.submodules['rfoutput1'].sweep_center() )

print( "query(RSVec,'SOUR:FREQ:SPAN?')  -> OutputChannel::sweep span()   ", \
      dev.submodules['rfoutput1'].sweep_span() )

dev.close()
