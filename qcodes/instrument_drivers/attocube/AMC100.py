# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 20:40:35 2019

@author: PLlab
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Numbers
from qcodes.instrument_drivers.attocube.PyAMC100 import MotionController

'''
Workflow: use axis 3 as an example

from AMC100Qcodes import Attocube_AMC100
amc = Attocube_AMC100('amc')

amc.get_actor_type(2) # get the actor type connected to axis 3, so that the parameter units can be determindd

amc.get_axis_output(2) # get output axis 3
amc.set_axis_output(2, 1) # enable axis 3 before doing anything
amc.pos_3() # get real position of axis 3
amc.get_move_status(2) # get move status of axis 3

amc.pos_3(500) #moves axis 3 to 500 u°
amc.pos_3() #get real position ->500
amc.pos_3(600) #moves axis 3 to 600 u°
amc.pos_3() #get real position ->600
amc.pos_3(700) #moves axis 3 to 700 u°

amc.set_move_status(2,0) # at the end of the travel, manually stop motion of axis 3

amc.freq_3() # get freqency of axis 3 (mHz)
amc.freq_3(8000) # set freqency of axis 3 (mHz)

amc.amp_3() #get amplitude of axis 3 (mV)
amc.amp_3(10000) #set amplitude of axis 3 (mV)

amc.set_axis_output(2, 0) # disable axis 3

amc.close() # disconnect



'''

#%%
class Attocube_AMC100(Instrument):
    def __init__(self, name, **kwargs):

        super().__init__(name, **kwargs)

        self.mc= MotionController('192.168.1.19')
        self.mc.connect()

#%%

        self.add_parameter('pos_1',
                           get_cmd = self.get_position1,
                           set_cmd = self.set_position1,
                           get_parser = int,
                           label = 'Position Axis 1',
                           unit = 'u° or nm',
                           docstring = " Note that the unit depends on the actor type.")

        self.add_parameter('pos_2',
                           get_cmd = self.get_position2,
                           set_cmd = self.set_position2,
                           get_parser = int,
                           label = 'Position Axis 2',
                           unit = 'u° or nm',
                           docstring = " Note that the unit depends on the actor type.")

        self.add_parameter('pos_3',
                           get_cmd = self.get_position3,
                           set_cmd = self.set_position3,
                           get_parser = int,
                           label = 'Position Axis 3',
                           unit = 'u° or nm',
                           docstring = " Note that the unit depends on the actor type.")

#%%

        self.add_parameter('freq_1',
                           get_cmd = self.get_frequency1,
                           set_cmd = self.set_frequency1,
                           get_parser = int,
                           label = 'Frequency Axis 1',
                           unit = 'mHz')

        self.add_parameter('freq_2',
                           get_cmd = self.get_frequency2,
                           set_cmd = self.set_frequency2,
                           get_parser = int,
                           label = 'Frequency Axis 2',
                           unit = 'mHz')

        self.add_parameter('freq_3',
                           get_cmd = self.get_frequency3,
                           set_cmd = self.set_frequency3,
                           get_parser = int,
                           label = 'Frequency Axis 3',
                           unit = 'mHz')

#%%

        self.add_parameter('amp_1',
                           get_cmd = self.get_amplitude1,
                           set_cmd = self.set_amplitude1,
                           get_parser = int,
                           label = 'Amplitude Axis 1',
                           unit = 'mV')

        self.add_parameter('amp_2',
                           get_cmd = self.get_amplitude2,
                           set_cmd = self.set_amplitude2,
                           get_parser = int,
                           label = 'Amplitude Axis 2',
                           unit = 'mV')

        self.add_parameter('amp_3',
                           get_cmd = self.get_amplitude3,
                           set_cmd = self.set_amplitude3,
                           get_parser = int,
                           label = 'Amplitude Axis 3',
                           unit = 'mV')


#%%
    def close(self):

        self.mc.close()

    def get_axis_output(self, axis):

        return self.mc.getControlOutput(axis)

    def set_axis_output(self, axis, enable):

        self.mc.setControlOutput(axis, enable)

    def get_move_status(self, axis):

        return self.mc.getControlMove(axis)

    def set_move_status(self, axis, enable):

        self.mc.setControlMove(axis, enable)

    def get_control_continous_fwd(self, axis):

        return self.mc.getControlContinousFwd(axis)

    def set_control_continous_fwd(self, axis, enable):

        self.mc.setControlContinousFwd(axis, enable)

    def get_control_continous_bkwd(self, axis):

        return self.mc.getControlContinousBkwd(axis)

    def set_control_continous_bkwd(self, axis, enable):

        self.mc.setControlContinousBkwd(axis, enable)

    def get_actor_type(self, axis):

        return self.mc.getActorType(axis)

#%%

    def _get_control_target_position(self, axis):

        return self.mc.getControlTargetPosition(axis)

    def _set_control_target_position(self, axis, target):

        self.mc.setControlTargetPosition(axis, target)

    def _get_control_amplitude(self, axis):

        return self.mc.getControlAmplitude(axis)

    def _set_control_amplitude(self, axis, amplitude):

        self.mc.setControlAmplitude(axis, amplitude)

    def _get_control_frequency(self, axis):

        return self.mc.getControlFrequency(axis)

    def _set_control_frequency(self, axis, frequency):

        self.mc.setControlFrequency(axis, frequency)

    def _getPosition(self, axis):

        return self.mc.getPosition(axis)


#    def get_output2(self):
#        return self.get_control_output(2)

#%%

    def get_position1(self):
        return self._getPosition(0)

    def get_position2(self):
        return self._getPosition(1)

    def get_position3(self):
        return self._getPosition(2)

    def set_position1(self, value):
        self._set_control_target_position(0, value)
        self.set_move_status(0,1)

    def set_position2(self, value):
        self._set_control_target_position(1, value)
        self.set_move_status(1,1)

    def set_position3(self, value):
        self._set_control_target_position(2, value)
        self.set_move_status(2,1)


#%%

    def get_frequency1(self):
        return self._get_control_frequency(0)

    def get_frequency2(self):
        return self._get_control_frequency(1)

    def get_frequency3(self):
        return self._get_control_frequency(2)

    def set_frequency1(self, value):
        self._set_control_frequency(0, value)

    def set_frequency2(self, value):
        self._set_control_frequency(1, value)

    def set_frequency3(self, value):
        self._set_control_frequency(2, value)


#%%

    def get_amplitude1(self):
        return self._get_control_amplitude(0)

    def get_amplitude2(self):
        return self._get_control_amplitude(1)

    def get_amplitude3(self):
        return self._get_control_amplitude(2)

    def set_amplitude1(self, value):
        self._set_control_amplitude(0, value)

    def set_amplitude2(self, value):
        self._set_control_amplitude(1, value)

    def set_amplitude3(self, value):
        self._set_control_amplitude(2, value)


