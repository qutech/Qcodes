#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 10:17:25 2018

@author: l.lankes
"""

from typing import Callable, Union, Iterable
from collections import defaultdict
import numpy as np

from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import ArrayParameter, BufferedSweepableParameter, BufferedReadableParameter
import qcodes.utils.validators as vals
from qupulse.pulses.pulse_template import PulseTemplate
from qupulse.pulses import ForLoopPT, MappingPT, plotting
from qupulse.hardware.awgs.base import AWG
from qupulse.hardware.dacs import DAC
from qupulse.hardware.setup import HardwareSetup, ChannelID, _SingleChannel, PlaybackChannel, MarkerChannel, MeasurementMask
from qupulse._program._loop import MultiChannelProgram, Loop
import warnings


class QuPulseTemplateParameters(Instrument):

    def __init__(self, name: str, **kwargs):
        """
        """
        super().__init__(name, **kwargs)


    def set_parameters(self, pulse_parameters,
                       sweep_parameter_cmd=None,
                       send_buffer_cmd=None):
        """
        """
        self.parameters.clear()
        
        if pulse_parameters is not None:
            for p in pulse_parameters:
                self.add_parameter(p, parameter_class=BufferedSweepableParameter,
                                   vals=vals.Numbers(), set_cmd=None,
                                   sweep_parameter_cmd=sweep_parameter_cmd,
                                   send_buffer_cmd=send_buffer_cmd)


    def to_dict(self):
        result = {}
        
        for p in self.parameters:
            result[p] = self.parameters[p].get()
        
        return result


class QuPulseDACChannel(BufferedReadableParameter):

    def __init__(self, name: str, get_buffered_cmd: Callable, config_meas_cmd: Callable,
                 measurement_mask: Union[MeasurementMask, Iterable[MeasurementMask]],
                 **kwargs):
        super().__init__(name, get_buffered_cmd=get_buffered_cmd, config_meas_cmd=config_meas_cmd, **kwargs)
        
        self.measurement_mask = measurement_mask
        self.ready = False


class QuPulseDACInstrument(Instrument):

    def __init__(self, name: str,
                 **kwargs):
        """
        """
        super().__init__(name, **kwargs)
        
        self.add_parameter("program_name",
                           set_cmd=None,
                           vals=vals.Strings(),
                           label="Program name")
        
        self.program_name.set(self.name + "_program")
        
        self._measurements = defaultdict(dict)
        self._data = None


    def add_measurement(self, name: str,
                        measurement_mask: Union[MeasurementMask, Iterable[MeasurementMask]]):
        
        if isinstance(measurement_mask, MeasurementMask):
            if name in self.parameters:
                warnings.warn(
                    "You add a measurement mask to an already registered measurement name. This is deprecated and will be removed in a future version. Please add all measurement masks at once.",
                    DeprecationWarning)
                measurement_mask = self.parameters[name].measurement_mask | {measurement_mask}
            else:
                measurement_mask = {measurement_mask}
        else:
            try:
                measurement_mask = set(measurement_mask)
            except TypeError:
                raise TypeError('Mask must be (a list) of type MeasurementMask')

        for old_name, parameter in self.parameters.items():
            if isinstance(parameter, QuPulseDACChannel) and (measurement_mask & parameter.measurement_mask):
                raise ValueError('Measurement mask already registered for measurement "{}"'.format(old_name))
        
        if name in self.parameters:
            self.parameters[name].measurement_mask = measurement_mask
        else:
            self.add_parameter(name, parameter_class=QuPulseDACChannel, get_buffered_cmd=self._get_buffered, config_meas_cmd=self._configure_measurement, arm_meas_cmd=self._arm_measurement, measurement_mask=measurement_mask)


    def _configure_measurement(self, parameter, measurement_window):
        print("QuPulseDACInstrument._configure_measurement({}, {})".format(parameter, measurement_window))
        
        if not parameter.ready:
            self._measurements[parameter.measurement_mask.dac][parameter.name] = measurement_window
        else:
            raise AttributeError("It is not possible to define multiple measurement windows on one measurement channel ({}).".format(parameter.name))


    def _arm_measurement(self, parameter):
        parameter.ready = True
        all_ready = True
        
        for p in self.parameters:
            if not p.ready:
                all_ready = False
                break
        
        if all_ready:
            for dac, dac_windows in self._measurements.items():
                dac.register_window_measurement(self.program_name, dac_windows)
            
            for dac in self._measurements.keys():
                dac.arm_program(self.program_name)


    def _get_buffered(self, parameter):
        if not self._data:
            self._data = {}
            for dac, dac_windows in self._measurements.items():
                data = dac.measure_program()
                if data:
                    self._data = {**self._data, **data}
        
        # TODO
        n = 1 # Count of measurement values, depends on Operation (e.g. Downsampling only produces one measurement per measurement-window)
        
        values = self._data[parameter.measurement_mask.mask_name][:n]
        del self._data[parameter.measurement_mask.mask_name][:n]
        
        return values


class QuPulseAWGInstrument(Instrument):
    
    def __init__(self, name: str,
                 pulse_template: PulseTemplate=None,
                 **kwargs) -> None:
        """
        """
        super().__init__(name, **kwargs);
        
        self.add_parameter("template",
                           get_cmd=self._get_template,
                           set_cmd=self._set_template,
                           vals=vals.ObjectTypeValidator(PulseTemplate, type(None)),
                           label="Pulse template")
        self.add_parameter("program_name",
                           set_cmd=None,
                           vals=vals.Strings(),
                           label="Program name")
        self.add_parameter("channel_mapping",
                           set_cmd=None,
                           vals=vals.ObjectTypeValidator(dict, type(None)),
                           label="Channel mapping")
        self.add_parameter("measurement_mapping",
                           set_cmd=None,
                           vals=vals.ObjectTypeValidator(dict, type(None)),
                           label="Measurement mapping")
        self.add_parameter("registered_channels",
                           get_cmd=self._get_registered_channels,
                           label="Registered channels")
        self.add_submodule("template_parameters",
                           QuPulseTemplateParameters(self.name + "_template_parameters"))

        if pulse_template:
            self.template.set(pulse_template)
        
        self.program_name.set(self.name + "_program")
        
        self._channel_map = {}
        
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
        
        
    def set_channel(self, identifier: ChannelID,
                    single_channel: Union[_SingleChannel, Iterable[_SingleChannel]],
                    allow_multiple_registration: bool=False) -> None:
        """
        """
        if isinstance(single_channel, (PlaybackChannel, MarkerChannel)):
            if identifier in self._channel_map:
                warnings.warn(
                    "You add a single hardware channel to an already existing channel id. This is deprecated and will be removed in a future version. Please add all channels at once.",
                    DeprecationWarning)
                single_channel = self._channel_map[identifier] | {single_channel}
            else:
                single_channel = {single_channel}
        else:
            try:
                single_channel = set(single_channel)
            except TypeError:
                raise TypeError('Channel must be (a list of) either a playback or a marker channel')

        if not allow_multiple_registration:
            for ch_id, channel_set in self._channel_map.items():
                if single_channel & channel_set:
                    raise ValueError('Channel already registered as {} for channel {}'.format(
                        type(self._channel_map[ch_id]).__name__, ch_id))

        for s_channel in single_channel:
            if not isinstance(s_channel, (PlaybackChannel, MarkerChannel)):
                raise TypeError('Channel must be (a list of) either a playback or a marker channel')

        self._channel_map[identifier] = single_channel
        
        
    def remove_channel(self, identifier: ChannelID):
        """
        """
        self._channel_map.pop(identifier)
        
        
    def _get_registered_channels(self):
        """
        """
        return self._channel_map


    def _sweep_parameter(self, parameter, sweep_values):
        """
        
        """
        self._build_counter += 1 # TODO Test
        print("QuPulseTemplate._build_buffer({}, {}) called ({})".format(parameter, sweep_values, self._build_counter))
        
        for l in self._loops:
            if l['parameter'] == parameter.name:
                raise AttributeError('It is not supported to sweep the same parameter ({}) more than once.'.format(parameter))

        loop = {
            'parameter'    : parameter.name,
            'iterator'     : '__' + parameter.name + '_it',
            'sweep_values' : sweep_values,
            'is_sent'      : False
        }
        self._loops.append(loop)
        
        
    def _send_buffer(self, parameter):
        """
        Sends the buffer to the device and the device waits for the trigger
        """
        self._send_counter += 1 # TODO Test
        print("QuPulseTemplate._send_buffer({}) called ({})".format(parameter, self._send_counter)) # TODO Test
        
        send = True
        
        for loop in self._loops:
            if loop['parameter'] == parameter.name:
                loop['is_sent'] = True
            elif not loop['is_sent']:
                send = False
        
        if send:
            return self._really_send_buffer()
        else:
            return None
        
    def _really_send_buffer(self):
        """
        """
        print("   --> Send") # TODO Test
        
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
        
        program = pt.create_program(parameters=params, channel_mapping=self.channel_mapping.get())
        
        measurement_windows = self._run_program(program)
#        self._hardware_setup.register_program(self.program_name.get(), program, update=True)
#        
#        awg = next(iter(self._hardware_setup.known_awgs)) # TODO
#        dac = next(iter(self._hardware_setup.known_dacs)) # TODO
#        
#        awg._device.set_chan_state([False, False, True, True])
#        
#        self._hardware_setup.arm_program(self.program_name.get())
#        
#        awg.run_current_program()
#        
#        self.scanline_data = dac.card.extractNextScanline()
#        
#        for measurement in self._hardware_setup._measurement_map:
#            
#            self.DS_C = self.scanline_data.operationResults['DS_C'].getAsVoltage(dac.config.inputConfiguration[2].inputRange)
#            self.DS_D = self.scanline_data.operationResults['DS_D'].getAsVoltage(dac.config.inputConfiguration[2].inputRange)
#        
#        self.DS_C = self.DS_C.reshape((40, 40))
#        self.DS_D = self.DS_D.reshape((40, 40))
#        
#        # resetting loops because the buffer is already at the hardware
#        self._loops.clear()
#        print("   --> Reset") # TODO Test
        return measurement_windows
        
        
    def _run_program(self, program, update=False):
        """
        """
        mcp = MultiChannelProgram(program)
        if mcp.channels - set(self._channel_map.keys()):
            raise KeyError('The following channels are unknown to the HardwareSetup: {}'.format(
                mcp.channels - set(self._channel_map.keys())))

        temp_measurement_windows = defaultdict(list)
        for program in mcp.programs.values():
            for mw_name, begins_lengths in program.get_measurement_windows().items():
                temp_measurement_windows[mw_name].append(begins_lengths)

        measurement_windows = dict()
        while temp_measurement_windows:
            mw_name, begins_lengths_deque = temp_measurement_windows.popitem()

            begins, lengths = zip(*begins_lengths_deque)
            measurement_windows[mw_name] = (
                np.concatenate(begins),
                np.concatenate(lengths)
            )

        handled_awgs = set()
        for channels, program in mcp.programs.items():
            awgs_to_channel_info = dict()

            def get_default_info(awg):
                return ([None] * awg.num_channels,
                        [None] * awg.num_channels,
                        [None] * awg.num_markers)

            for channel_id in channels:
                for single_channel in self._channel_map[channel_id]:
                    playback_ids, voltage_trafos, marker_ids = \
                        awgs_to_channel_info.setdefault(single_channel.awg, get_default_info(single_channel.awg))

                    if isinstance(single_channel, PlaybackChannel):
                        playback_ids[single_channel.channel_on_awg] = channel_id
                        voltage_trafos[single_channel.channel_on_awg] = single_channel.voltage_transformation
                    elif isinstance(single_channel, MarkerChannel):
                        marker_ids[single_channel.channel_on_awg] = channel_id

            for awg, (playback_ids, voltage_trafos, marker_ids) in awgs_to_channel_info.items():
                if awg in handled_awgs:
                    raise ValueError('AWG has two programs')
                else:
                    handled_awgs.add(awg)
                awg.upload(self.program_name.get(),
                           program=program,
                           channels=tuple(playback_ids),
                           markers=tuple(marker_ids),
                           force=update,
                           voltage_transformation=tuple(voltage_trafos))

        known_awgs = {single_channel.awg
                      for single_channel_set in self._channel_map.values()
                      for single_channel in single_channel_set}
        
        for awg in known_awgs:
            if awg in handled_awgs:
                awg.arm(self.program_name.get())
            else:
                # The other AWGs should ignore the trigger
                awg.arm(None)
        
        return measurement_windows
        
    def _get_output(self):
        """
        """
        self._output_counter += 1 # TODO Test
        #print("QuPulseTemplate._get_output() called ({}); parameters: {}.".format(self._output_counter, self.template_parameters.to_dict())) # TODO Test
        
        # TODO
        # first call: measure all values and resturn the first
        # next calls: return next values until the list of return values is empty
        # empty list: -> first call because it has to be a new measure
        
        return 0 #np.array([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]])
