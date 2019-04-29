# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 20:40:35 2019

@author: PLlab
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Ints
from qcodes.instrument_drivers.attocube.PyAMC100 import MotionController

'''
Workflow: use axis 3 as an example

from AMC100Qcodes import Attocube_AMC100
amc = Attocube_AMC100('amc')

amc.get_actor_type(2) # get the actor type connected to axis 3, so that the parameter units can be determined

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

amc.freq_3() # get frequency of axis 3 (Hz)
amc.freq_3(8000) # set frequency of axis 3 (Hz)

amc.amp_3() #get amplitude of axis 3 (V)
amc.amp_3(10) #set amplitude of axis 3 (V)

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
                           unit = 'u°')

        self.add_parameter('pos_2',
                           get_cmd = self.get_position2,
                           set_cmd = self.set_position2,
                           get_parser = int,
                           label = 'Position Axis 2',
                           unit = 'u°')

        self.add_parameter('pos_3',
                           get_cmd = self.get_position3,
                           set_cmd = self.set_position3,
                           get_parser = int,
                           label = 'Position Axis 3',
                           unit = 'u°')

#%%

        self.add_parameter('freq_1',
                           get_cmd = self.get_frequency1,
                           set_cmd = self.set_frequency1,
                           get_parser = int,
                           label = 'Frequency Axis 1',
                           vals = Ints(0,5000),
                           unit = 'Hz')

        self.add_parameter('freq_2',
                           get_cmd = self.get_frequency2,
                           set_cmd = self.set_frequency2,
                           get_parser = int,
                           label = 'Frequency Axis 2',
                           vals = Ints(0,5000),
                           unit = 'Hz')

        self.add_parameter('freq_3',
                           get_cmd = self.get_frequency3,
                           set_cmd = self.set_frequency3,
                           get_parser = int,
                           label = 'Frequency Axis 3',
                           vals = Ints(0,5000),
                           unit = 'Hz')

#%%

        self.add_parameter('amp_1',
                           get_cmd = self.get_amplitude1,
                           set_cmd = self.set_amplitude1,
                           get_parser = int,
                           label = 'Amplitude Axis 1',
                           vals = Ints(0,45),
                           unit = 'V')

        self.add_parameter('amp_2',
                           get_cmd = self.get_amplitude2,
                           set_cmd = self.set_amplitude2,
                           get_parser = int,
                           label = 'Amplitude Axis 2',
                           vals = Ints(0,45),
                           unit = 'V')

        self.add_parameter('amp_3',
                           get_cmd = self.get_amplitude3,
                           set_cmd = self.set_amplitude3,
                           get_parser = int,
                           label = 'Amplitude Axis 3',
                           vals = Ints(0,45),
                           unit = 'V')


#%%
    def close(self):

        self.mc.close()

    def get_axis_output(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlOutput(axis)

    def set_axis_output(self, axis, enable):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlOutput(axis, enable)

    def get_move_status(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlMove(axis)

    def set_move_status(self, axis, enable):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlMove(axis, enable)

    def get_control_continous_fwd(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlContinousFwd(axis)

    def set_control_continous_fwd(self, axis, enable):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlContinousFwd(axis, enable)

    def get_control_continous_bkwd(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlContinousBkwd(axis)

    def set_control_continous_bkwd(self, axis, enable):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlContinousBkwd(axis, enable)

    def get_actor_type(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getActorType(axis)

#%%

    def _get_control_target_position(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlTargetPosition(axis)

    def _set_control_target_position(self, axis, target):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlTargetPosition(axis, target)

    def _get_control_amplitude(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlAmplitude(axis)*1e-3

    def _set_control_amplitude(self, axis, amplitude):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlAmplitude(axis, amplitude*1000)

    def _get_control_frequency(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getControlFrequency(axis)*1e-3

    def _set_control_frequency(self, axis, frequency):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        self.mc.setControlFrequency(axis, frequency*1000)

    def _getPosition(self, axis):
        axis = axis-1 # map axis 1,2,3 on the controller to the axis 0,1,2 in the driver
        return self.mc.getPosition(axis)


#    def get_output2(self):
#        return self.get_control_output(2)

#%%

    def get_position1(self):
        return self._getPosition(1)

    def get_position2(self):
        return self._getPosition(2)

    def get_position3(self):
        return self._getPosition(3)

    def set_position1(self, value):
        self._set_control_target_position(1, value)
        self.set_move_status(1,1)

    def set_position2(self, value):
        self._set_control_target_position(2, value)
        self.set_move_status(2,1)

    def set_position3(self, value):
        self._set_control_target_position(3, value)
        self.set_move_status(3,1)


#%%

    def get_frequency1(self):
        return self._get_control_frequency(1)

    def get_frequency2(self):
        return self._get_control_frequency(2)

    def get_frequency3(self):
        return self._get_control_frequency(3)

    def set_frequency1(self, value):
        self._set_control_frequency(1, value)

    def set_frequency2(self, value):
        self._set_control_frequency(2, value)

    def set_frequency3(self, value):
        self._set_control_frequency(3, value)


#%%

    def get_amplitude1(self):
        return self._get_control_amplitude(1)

    def get_amplitude2(self):
        return self._get_control_amplitude(2)

    def get_amplitude3(self):
        return self._get_control_amplitude(3)

    def set_amplitude1(self, value):
        self._set_control_amplitude(1, value)

    def set_amplitude2(self, value):
        self._set_control_amplitude(2, value)

    def set_amplitude3(self, value):
        self._set_control_amplitude(3, value)


