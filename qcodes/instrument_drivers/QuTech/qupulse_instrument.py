#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 10:17:25 2018

@author: l.lankes
"""

from typing import Callable
import numpy as np

from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ArrayParameter, BufferedParameter
import qcodes.utils.validators as vals
from qupulse.pulses.pulse_template import PulseTemplate
from qupulse.pulses import ForLoopPT, MappingPT, plotting
from qupulse.expressions import Expression
from qupulse.hardware.setup import HardwareSetup


class QuPulseArrayParameter(ArrayParameter):
    
    def __init__(self, name: str,
                 get_cmd: Callable, **kwargs):
        """
        """
        super().__init__(name, **kwargs)
        
        self.get_cmd = get_cmd
        
    def get_raw(self):
        """
        """
        return self.get_cmd()

class QuPulseParameters(Instrument):
    
    def __init__(self, name: str, **kwargs):
        """
        """
        super().__init__(name, **kwargs)
        
        self.sweep_values = None
        
    def set_parameters(self, pulse_parameters,
                       sweep_parameter_cmd=None,
                       send_buffer_cmd=None):
        """
        """
        self.parameters.clear()
        
        if pulse_parameters is not None:
            for p in pulse_parameters:
                self.add_parameter(p, parameter_class=BufferedParameter,
                                   vals=vals.Numbers(), set_cmd=None,
                                   sweep_parameter_cmd=sweep_parameter_cmd,
                                   send_buffer_cmd=send_buffer_cmd)
    
    def to_dict(self):
        result = {}
        
        for p in self.parameters:
            result[p] = self.parameters[p].get()
        
        return result


class QuPulseInstrument(Instrument):
    
    def __init__(self,
                 name: str,
                 pt: PulseTemplate,
                 hardware_setup: HardwareSetup,
                 **kwargs) -> None:
        """
        """
        super().__init__(name, **kwargs);
        
        self._hardware_setup = hardware_setup
        
        self.add_parameter("template",
                           get_cmd=self._get_template,
                           set_cmd=self._set_template,
                           vals=vals.ObjectTypeValidator(PulseTemplate),
                           label="Pulse template")
        self.add_parameter("output",
                           parameter_class=QuPulseArrayParameter,
                           shape=(1,),
                           get_cmd=self._get_output,
                           label="Output data")
        self.add_parameter("channel_mapping",
                           )
        self.add_submodule("template_parameters",
                           QuPulseParameters(self.name + "_template_parameters"))

        self.template.set(pt)
        
        self._output_counter = 0 # TODO Test
        self._send_counter = 0 # TODO Test
        self._build_counter = 0 # TODO Test
        self._reset_counter = 0 # TODO Test
        

    def _get_template(self):
        """
        Gets the PulseTemplate
        """
        return self._template
    
    
    def _set_template(self, value):
        """
        Sets the PulseTemplate and extracts its parameters
        
        template: PulseTemplate
        """
        self._template = value
        self._loops = []
        
        self.template_parameters.set_parameters(self._template.parameter_names,
                                                self._sweep_parameter,
                                                self._send_buffer)
        
        
    def _sweep_parameter(self, parameter, sweep_values):
        """
        
        """
        self._build_counter += 1 # TODO Test
        print("QuPulseTemplate._build_buffer({}, {}) called ({})".format(parameter, sweep_values, self._build_counter))
        
        for l in self._loops:
            if l['parameter'] == parameter.name:
                raise AttributeError('It is not supported to sweep the same parameter ({}) twice.'.format(parameter))

        loop = {
            "parameter"    : parameter.name,
            "iterator"     : "__" + parameter.name + "_it",
            "sweep_values" : sweep_values
        }
        self._loops.append(loop)
        
        
    def _send_buffer(self, parameter):
        """
        Sends the buffer to the device and the device waits for the trigger
        """
        self._send_counter += 1 # TODO Test
        print("QuPulseTemplate._send_buffer({}) called ({})".format(parameter, self._send_counter)) # TODO Test
        
        parameter_mapping = {}
        params = self.template_parameters.to_dict()
        
        for p in self.template.get().parameter_names:
            parameter_mapping[p] = p
        
        for loop in self._loops:
            parameter_mapping[loop['parameter']] = "{}[{}]".format(loop['parameter'], loop['iterator'])
            params[loop['parameter']] = loop['sweep_values']

        pt = MappingPT(self.template.get(), parameter_mapping=parameter_mapping)

        for loop in reversed(self._loops):
            pt = ForLoopPT(pt, loop['iterator'], range(len(loop['sweep_values'])))
        
        program = pt.create_program(parameters=params)
        
        print(program.get_measurement_windows())
        
        # Test
        plotting.plot(pt, params, sample_rate=100)
        
        program_name = self.name + "_program"
        
        self._hardware_setup.register_program(program_name, program, update=True)
        self._hardware_setup.run_program(program_name)
        
        # resetting loops because the buffer is already at the hardware
        self._loops.clear()
        print("   --> Reset") # TODO Test
        
        
    def _get_output(self):
        """
        """
        self._output_counter += 1 # TODO Test
        print("QuPulseTemplate._get_output() called ({}); parameters: {}.".format(self._output_counter, self.template_parameters.to_dict())) # TODO Test
        
        # TODO
        # first call: measure all values and resturn the first
        # next calls: return next values until the list of return values is empty
        # empty list: -> first call because it has to be a new measure
        
        return 0 #np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]])
