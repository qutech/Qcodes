#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 10:17:25 2018

@author: l.lankes
"""

from typing import Callable, Union, Iterable, Optional, Dict, Sequence, Tuple
from collections import defaultdict
import numpy as np
import warnings

from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import BufferedSweepableParameter, BufferedReadableArrayParameter
import qcodes.utils.validators as vals
from qcodes.utils.helpers import full_class

from qupulse.pulses import MappingPT, ForLoopPT, RepetitionPT
from qupulse.pulses.pulse_template import PulseTemplate
from qupulse.hardware.dacs import DAC
from qupulse.hardware.setup import ChannelID, _SingleChannel, PlaybackChannel, MarkerChannel, MeasurementMask
from qupulse._program._loop import MultiChannelProgram

from atsaverage.operations import OperationDefinition, Downsample


class QuPulseTemplateParameter(BufferedSweepableParameter):
    """
    A parameter that creates buffered sweeps in the instrument.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Creates a QuPulseTemplateParameter that creates buffered sweeps in
        the instrument.
        """
        super().__init__(*args, **kwargs)


class QuPulseTemplateParameters(Instrument):
    """
    Submodule for the QuPulseAWGInstrument. It automatically generates
    QCoDeS-parameters from qupulse-template-parameters.
    
    Parameters:
        All parameters of the parent-instruments PulseTemplate-parameters.
    """

    def __init__(self, name: str, **kwargs) -> None:
        """
        Creates the a QuPulseTemplateParameters object.
        
        QuPulseTemplateParameters is a submodule for the QuPulseAWGInstrument.
        It automatically generates QCoDeS-parameters from qupulse-template-
        parameters.
        
        Args:
            name: The name of this instrument
        """
        super().__init__(name, **kwargs)


    def set_parameters(self, pulse_parameters: Iterable[str],
                       sweep_parameter_cmd: Optional[Callable]=None,
                       repeat_parameter_cmd: Optional[Callable]=None,
                       send_buffer_cmd: Optional[Callable]=None,
                       run_program_cmd: Optional[Callable]=None,
                       get_meas_windows: Optional[Callable[[], Dict]]=None) -> None:
        """
        Adds sweepable QCoDeS-parameters from qupulse-template-parameters.
        
        Args:
            pulse_parameters: A set of all parameters of the PulseTemplate.
            sweep_parameter_cmd: Function that should be called when a
                parameter should be sweept in a buffered loop.
            send_buffer_cmd: Function that should be called when all buffered
                sweeps are set. This function sends the complete buffer to the
                AWG.
        """
        self.parameters.clear()
        
        if pulse_parameters is not None:
            for p in pulse_parameters:
                self.add_parameter(p, parameter_class=QuPulseTemplateParameter,
                                   vals=vals.Numbers(), set_cmd=None,
                                   sweep_parameter_cmd=sweep_parameter_cmd,
                                   repeat_parameter_cmd=repeat_parameter_cmd,
                                   send_buffer_cmd=send_buffer_cmd,
                                   run_program_cmd=run_program_cmd,
                                   get_meas_windows=get_meas_windows)


    def to_dict(self) -> Dict:
        """
        Translates the parameters to a parameter-dictionary which can be used
        to create the waveform program.
        
        Returns:
            Dictionary of parameter names and values.
        """
        result = {}
        
        for p in self.parameters:
            result[p] = self.parameters[p].get()
        
        return result


class QuPulseAWGInstrument(Instrument):
    """
    An instrument that wraps an qupulse-PulseTemplate and uses qupulse to send
    it to an AWG.
    
    Parameters:
        template: PulseTemplate taht is handled by this instrument.
        program_name: Name of the program which will be send to the AWG.
        channel_mapping: Channel-mapping for the PulseTemplate.
        measurement_mapping: Channel-mapping for the measurement channels of
            the PulseTemplate.
        registered_channels: A dictionary of all channels on the AWG hardware.
    
    Submodules:
        template_parameters: Automatically generated parameters from the
            PulseTemplate
    """
    
    def __init__(self, name: str,
                 run_program_cmd: Optional[Callable]=None,
                 **kwargs) -> None:
        """
        Creates an QuPulseAWGInstrument that wraps an qupulse-PulseTemplate and
        uses qupulse to send it to an AWG.
        
        Args:
            name: Name of the instrument
        """
        super().__init__(name, **kwargs);
        
        self.add_parameter("template",
                           get_cmd=self._get_template,
                           set_cmd=self._set_template,
                           vals=vals.MultiType(vals.ObjectType(PulseTemplate), vals.NoneType()),
                           label="Pulse template")
        self.add_parameter("program_name",
                           set_cmd=None,
                           vals=vals.Strings(),
                           label="Program name")
        self.add_parameter("channel_mapping",
                           set_cmd=None,
                           vals=vals.MultiType(vals.ObjectType(Dict), vals.NoneType()),
                           label="Channel mapping")
        self.add_parameter("measurement_mapping",
                           set_cmd=None,
                           vals=vals.MultiType(vals.ObjectType(Dict), vals.NoneType()),
                           label="Measurement mapping")
        self.add_parameter("registered_channels",
                           get_cmd=self._get_registered_channels,
                           label="Registered channels")
        self.add_submodule("template_parameters",
                           QuPulseTemplateParameters(self.name + "_template_parameters"))

        self.program_name.set(self.name + "_program")
        
        self.run_program_cmd = run_program_cmd
        self._channel_map = {}
        self._loops = []
        self.template.set(None)
        
        
    def _get_template(self) -> PulseTemplate:
        """
        Returns:
            PulseTemplate
        """
        return self._template
    
    
    def _set_template(self, value: PulseTemplate) -> None:
        """
        Sets the PulseTemplate and extracts its parameters
        
        Args:
            value: PulseTemplate
        """
        self._template = value
        self._loops.clear()
        
        if self._template:
            self.template_parameters.set_parameters(self._template.parameter_names,
                                                    self._sweep_parameter,
                                                    self._repeat_parameter,
                                                    self._send_buffer,
                                                    self._run_program,
                                                    self._get_meas_windows)
        else:
            self.template_parameters.set_parameters(None, None, None)

        
    def set_channel(self, identifier: ChannelID,
                    single_channel: Union[_SingleChannel, Iterable[_SingleChannel]]) -> None:
        """
        Adds a hardware channel to the instrument.
        
        Args:
            identifier: Channel name
            single_channel: Object (or set of objects) that represents the hardware channel
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

        for ch_id, channel_set in self._channel_map.items():
            if single_channel & channel_set:
                raise ValueError('Channel already registered as {} for channel {}'.format(
                    type(self._channel_map[ch_id]).__name__, ch_id))

        for s_channel in single_channel:
            if not isinstance(s_channel, (PlaybackChannel, MarkerChannel)):
                raise TypeError('Channel must be (a list of) either a playback or a marker channel')

        self._channel_map[identifier] = single_channel
        
        
    def remove_channel(self, identifier: ChannelID) -> None:
        """
        Removes an existing hardware channel from the instrument object.
        
        Args:
            identifier: Channel name
        """
        self._channel_map.pop(identifier)
        
        
    def _get_registered_channels(self) -> Dict:
        """
        Returns:
            A dictionary of all hardware channels.
        """
        return self._channel_map


    def _sweep_parameter(self, parameter, sweep_values, layer) -> None:
        """
        Adds the sweep information to a list, to build up a single buffer later
        
        Args:
            parameter: Parameter to sweep
            sweep_values: Values the parameter should be swept over.
            layer: nnumber of nested loop (most outer loop: 0)
        """
        for l in self._loops:
            if l['layer'] == layer:
                raise AttributeError('It is not possible to define multiple loops per layer (layer={}).'.format(layer))
            if 'parameter' in l and l['parameter'] == parameter.name:
                raise AttributeError('It is not supported to sweep the same parameter ({}) more than once.'.format(parameter))

        loop = {
            'layer'        : layer,
            'parameter'    : parameter.name,
            'iterator'     : '__' + parameter.name + '_it',
            'sweep_values' : sweep_values,
            'is_sent'      : False,
            'is_run'       : False
        }
        self._loops.append(loop)
    
    
    def _repeat_parameter(self, repetition_count, layer) -> None:
        """
        Adds the repetition information to a list to build up a single buffer later
        
        Args:
            repetition_count: number of repetitions
            layer: nnumber of nested loop (most outer loop: 0)
        """
        for l in self._loops:
            if l['layer'] == layer:
                raise AttributeError('It is not possible to define multiple loops per layer (layer={}).'.format(layer))

        loop = {
            'layer'        : layer,
            'repetitions'  : repetition_count,
            'is_sent'      : False,
            'is_run'       : False
        }
        self._loops.append(loop)
        
        
    def _send_buffer(self, layer) -> Dict:
        """
        Waits until this function is called for all swept parameters. Then the 
        buffer will be built and sent to the device.
        
        Args:
            layer: nnumber of nested loop (most outer loop: 0)
            
        Returns:
            Dictionary of the measurement windows if the function was called
            the last parameter. If not it returns None.
        """
        if self._loops:
            send = True
            
            for loop in self._loops:
                if loop['layer'] == layer:
                    loop['is_sent'] = True
                elif not loop['is_sent']:
                    send = False
            
            if send:
                return self._really_send_buffer()
            else:
                return None


    def _really_send_buffer(self) -> Dict:
        """
        Builts up and sends the buffer to the device and makes the device wait
        for the trigger
        
        Returns:
            Dictionary of the measurement windows.
        """
        mcp = self._build_program()
        measurement_windows = _calc_measurement_windows(mcp)

        self._upload_program(mcp)
        
        return measurement_windows

    def _get_meas_windows(self) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        return _calc_measurement_windows(self._build_program())

    def _build_program(self) -> MultiChannelProgram:
        """Build a program based on the current template parameter values and loop structure

        TODO: implement caching

        Returns:
            Multi channel program
            Dictionary of the measurement windows.
        """
        parameter_mapping = {}
        params = self.template_parameters.to_dict()

        for p in self.template.get().parameter_names:
            parameter_mapping[p] = p

        for loop in self._loops:
            if 'sweep_values' in loop:
                parameter_mapping[loop['parameter']] = "{}[{}]".format(loop['parameter'], loop['iterator'])
                params[loop['parameter']] = loop['sweep_values']

        pt = MappingPT(self.template.get(), parameter_mapping=parameter_mapping)

        for loop in reversed(self._loops):
            if 'sweep_values' in loop:
                pt = ForLoopPT(pt, loop['iterator'], range(len(loop['sweep_values'])))
            elif 'repetitions' in loop:
                pt = RepetitionPT(pt, loop['repetitions'])

        program = pt.create_program(parameters=params,
                                 channel_mapping=self.channel_mapping.get(),
                                 measurement_mapping=self.measurement_mapping.get())

        # this is legacy complex multi channeling support
        mcp = MultiChannelProgram(program)
        if mcp.channels - set(self._channel_map.keys()):
            raise KeyError('The following channels are unknown to the HardwareSetup: {}'.format(
                mcp.channels - set(self._channel_map.keys())))

        return mcp
        
    def _upload_program(self, mcp, update=True):
        """
        Sends the buffer to the device and arms it.
        
        Args:
            program: Program object
        """
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

    def _run_program(self, layer):
        """
        Runs the waveform program on the awg as soon as this function was
        called for the last (buffered) loop
        """
        if self._loops:
            run = True
            
            for loop in self._loops:
                if loop['layer'] == layer:
                    loop['is_run'] = True
                elif not loop['is_run']:
                    run = False
            
            if run:
                return self._really_run_program()
            else:
                return None


    def _really_run_program(self):
        """
        Runs the program on the awg by calling the configured
        callback.
        """
        if self.run_program_cmd is not None:
            self.run_program_cmd()
        
        self.reset_programs()
    
    
    def reset_programs(self):
        """
        Resets all previously defined parameter-sweeps. In case of an error
        while running a program this can be used before running a new program.
        """
        self._loops.clear()
    
    
    def remove_programs(self):
        """
        Removes all defined parameter-sweeps, channels and programs
        """
        self.reset_programs()
        self._channel_map.clear()


    def snapshot_base(self, update: bool=False,
                      params_to_skip_update: Sequence[str]=None):
        """
        State of the instrument as a JSON-compatible dict.

        Args:
            update: If True, update the state by querying the
                instrument. If False, just use the latest values in memory.
            params_to_skip_update: List of parameter names that will be skipped
                in update even if update is True. This is useful if you have
                parameters that are slow to update but can be updated in a
                different way (as in the qdac)

        Returns:
            dict: base snapshot
        """
        if params_to_skip_update is None:
            params_to_skip_update = []
        
        params_to_skip_update = list(params_to_skip_update)
        params_to_skip_update.append(self.template.name)
        
        metadata = super().snapshot_base(update, params_to_skip_update)
        
        template_dict = self.template.get().get_serialization_data()
        
        metadata['parameters'][self.template.name]['value'] = template_dict
        metadata['parameters'][self.template.name]['raw_value'] = template_dict
        
        return metadata


class QuPulseDACChannel(BufferedReadableArrayParameter):
    """
    A parameter for an operation on a measurement mask. These parameters can be
    measured in a QCoDeS-loop.
    
    Parameters:
        measurement_window: Measurement windows for this parameter.
        operation: Operation that was executed on the measurement.
        configured: True, if a measurement was configured for this parameter.
        ready: True, if the parameter is ready to be armed and measured.
    """
    
    def __init__(self, name: str,
                 get_buffered_cmd: Callable,
                 config_meas_cmd: Callable,
                 arm_meas_cmd: Callable,
                 operation: OperationDefinition,
                 **kwargs) -> None:
        """
        Creates a QuPulseDACChannel parameter for an operation on a measurement
        mask. These parameters can be measured in a QCoDeS-loop.
        
        Args:
            name: Name of the parameter
            get_buffered_cmd: Function which is called when this parameter is
                measured.
            config_meas_cmd: Function which is called when a measurement is
                configured for this parameter.
            arm_meas_cmd: Function which is called when the parameter should be
                armed.
            operation: The operation which is executed on the measurement.
                (Only Downsample operations are supported yet)
        """
        if isinstance(operation, Downsample):
            shape = ()
        else:
            raise NotImplementedError('Operations of type {} are not supported yet.'.format(type(operation)))
            
        super().__init__(name,
                         get_buffered_cmd=get_buffered_cmd,
                         config_meas_cmd=config_meas_cmd,
                         arm_meas_cmd=arm_meas_cmd,
                         shape=shape,
                         **kwargs)
        
        self.operation = operation
        
        self.reset()
    
    
    def reset(self):
        """
        Reset the parameter to its default state, so it can be used for another
        measurement
        """
        self.measurement_window = None, None
        self.configured = False
        self.ready = False
    

    def snapshot_base(self, update: bool=False,
                      params_to_skip_update: Sequence[str]=None):
        """
        State of the instrument as a JSON-compatible dict.

        Args:
            update: If True, update the state by querying the
                instrument. If False, just use the latest values in memory.
            params_to_skip_update: List of parameter names that will be skipped
                in update even if update is True. This is useful if you have
                parameters that are slow to update but can be updated in a
                different way (as in the qdac)

        Returns:
            dict: base snapshot
        """
        metadata = super().snapshot_base(update, params_to_skip_update)
        
        metadata['operation'] = {'__class__': full_class(self.operation),
                                 'identifier': self.operation.identifier,
                                 'maskID': self.operation.maskID}
        
        return metadata
        

class QuPulseDACInstrument(Instrument):
    """
    An instrument that represents a DAC which supports buffered measurements.
    
    Parameters:
        program_name: Name of the measurement program which will be sent to the
            device.
    """
    
    def __init__(self, name: str,
                 **kwargs) -> None:
        """
        Creates a QuPulseDACInstrument which represents a DAC which supports#
        buffered measurements.
        
        Args:
            name: Name of the instrument
        """
        super().__init__(name, **kwargs)
        
        self.add_parameter("program_name",
                           set_cmd=None,
                           vals=vals.Strings(),
                           label="Program name")
        self.add_parameter("measurement_masks",
                           get_cmd=self._get_measurement_masks,
                           label="Measurement masks")
        
        self.add_function("set_measurement",
                          call_cmd=self._set_measurement,
                          args=[vals.Strings(), vals.MultiType(vals.ObjectType(MeasurementMask), vals.ObjectType(Iterable))])
        self.add_function("register_operations",
                          call_cmd=self._register_operations,
                          args=[vals.ObjectType(DAC), vals.MultiType(vals.ObjectType(MeasurementMask), vals.ObjectType(Iterable))])
        
        self.program_name.set(self.name + "_program")
        
        self._measurement_masks = dict()
        self._affected_dacs = None
        self._data = None

    
    def _get_measurement_masks(self):
        """
        Returns:
            A dictionary with all measurement masks for each measurement window.
        """
        return self._measurement_masks
    

    def _set_measurement(self, name: str,
                         measurement_masks: Union[MeasurementMask, Iterable[MeasurementMask]]) -> None:
        """
        Adds a measurement mask (or a list of masks) to the instrument.
        
        Args:
            name: Name of the mask
            measurement_masks: MeasurementMask object (or a list of them)
        """
        if isinstance(measurement_masks, MeasurementMask):
            if name in self._measurement_masks:
                warnings.warn(
                    "You add a measurement mask to an already registered measurement name. This is deprecated and will be removed in a future version. Please add all measurement masks at once.",
                    DeprecationWarning)
                measurement_masks = self._measurement_masks[name] | {measurement_masks}
            else:
                measurement_masks = {measurement_masks}
        else:
            try:
                measurement_masks = set(measurement_masks)
            except TypeError:
                raise TypeError('Mask must be (a list) of type MeasurementMask')

        for old_name, mask_set in self._measurement_masks.items():
            if measurement_masks & mask_set:
                raise ValueError('Measurement mask already registered for measurement "{}"'.format(old_name))
        
        self._measurement_masks[name] = measurement_masks
        

    def _register_operations(self, dac: DAC,
                             operations: Union[OperationDefinition, Iterable[OperationDefinition]]) -> None:
        """
        Register operations to the device. Each operation creates a parameter
        which can be measured in a loop.
        
        Args:
            dac: DAC hardware object
            operations: Operations to add to the device.
        """
        if isinstance(operations, OperationDefinition):
            operations = [operations]
        
        for op in operations:
            if not op.identifier in self.parameters:
                self.add_parameter(op.identifier,
                                   parameter_class=QuPulseDACChannel,
                                   get_buffered_cmd=self._get_buffered,
                                   config_meas_cmd=self._configure_measurement,
                                   arm_meas_cmd=self._arm_measurement,
                                   operation=op)
            
        dac.register_operations(self.program_name, operations)


    def _configure_measurement(self, parameter: QuPulseDACChannel,
                               measurement_windows) -> None:
        """
        Configures a measurement to a parameter
        
        Args:
            parameter: Parameter to measure
            measurement_windows: Measurement windows
        """
        if parameter.configured:
            raise Exception('It is not allowed to measure the same parameter ({}) twice.'.format(parameter))
            
        mask_name = parameter.operation.maskID
        
        for window_name, masks in self._measurement_masks.items():
            for mask in masks:
                if mask.mask_name == mask_name:
                    if window_name in measurement_windows:
                        parameter.measurement_window = window_name, measurement_windows[window_name]
                        break
                    else:
                        raise Exception('Measurement window "{}" is not given.'.format(window_name))
            else:
                continue
            
            break
        
        parameter.configured = True


    def _arm_measurement(self, parameter: QuPulseDACChannel) -> None:
        """
        Arms the measurement of a parameter
        
        Args:
            parameter: Parameter whose measurements should be armed.
        """
        all_ready = True
        parameter.ready = True
        
        for name, p in self.parameters.items():
            if isinstance(p, QuPulseDACChannel) and p.configured:
                if not p.ready:
                    all_ready = False
                    break
        
        if all_ready:
            self._affected_dacs = defaultdict(dict)
            
            for p in self.parameters.values():
                if isinstance(p, QuPulseDACChannel) and p.ready:
                    window_name, window = p.measurement_window
                    mask_name = p.operation.maskID
                    masks = self._measurement_masks[window_name]
                    for mask in masks:
                        if mask.mask_name == mask_name:
                            self._affected_dacs[mask.dac][mask.mask_name] = window
                            break
            
            for dac, dac_windows in self._affected_dacs.items():
                dac.register_measurement_windows(self.program_name, dac_windows)
            
            for dac in self._affected_dacs.keys():
                dac.arm_program(self.program_name)


    def _get_buffered(self, parameter: QuPulseDACChannel):
        """
        Measures all parameters on the first call and returns the measurement
        value(s) of the current measurement step.
        
        Args:
            parameter:  Parameter to measure.
        
        Returns:
            The measurement value(s) of the current measurement step. The shape
            of the value(s) depends on the operation.
        """
        if not self._data:
            parameters = []
            for p in self.parameters.values():
                if isinstance(p, QuPulseDACChannel) and p.ready:
                    parameters.append(p.name)
                    p.reset()
            
            self._data = {}
            for dac in self._affected_dacs.keys():
                data = dac.measure_program(parameters)
                if data:
                    self._data = {**self._data, **data}
        
        # something "pop front"y
        (values,), remaining = np.split(self._data[parameter.name], [1])
        
        # why did you handle None here before? it would have thrown an error if it occured
        if remaining.size != 0:
            self._data[parameter.name] = remaining
        else:
            del self._data[parameter.name]
            
        # whats difference of data being None to an empty dict?
        if not self._data:
            # does not make sense to me
            self._data = None
            
        return values
    
    
    def reset_measurements(self):
        """
        Resets all previously defined measurements. In case of an error while
        measuring this can be used before starting a new measurement.
        """
        for p in self.parameters.values():
            if isinstance(p, QuPulseDACChannel):
                p.reset()
    
    
    def remove_measurements(self):
        """
        Removes all defined measurements, measurement-masks and operations
        """
        for p in self.parameters.values():
            if isinstance(p, QuPulseDACChannel):
                self.parameters.pop(p.name)
        
        self._measurement_masks.clear()


    def snapshot_base(self, update: bool=False,
                      params_to_skip_update: Sequence[str]=None):
        """
        State of the instrument as a JSON-compatible dict.

        Args:
            update: If True, update the state by querying the
                instrument. If False, just use the latest values in memory.
            params_to_skip_update: List of parameter names that will be skipped
                in update even if update is True. This is useful if you have
                parameters that are slow to update but can be updated in a
                different way (as in the qdac)

        Returns:
            dict: base snapshot
        """
        if params_to_skip_update is None:
            params_to_skip_update = []
        
        # Skip measurement_masks and add them manually
        params_to_skip_update = list(params_to_skip_update)
        params_to_skip_update.append(self.measurement_masks.name)
        
        metadata = super().snapshot_base(update, params_to_skip_update)
        
        # Add all measurement masks into a dictionary for the metadata
        masks_metadata = {name: [{'__class__': full_class(m), 'mask_name': m.mask_name, 'dac': repr(m.dac)} for m in masks] for name, masks in self._measurement_masks.items()}
        
        metadata['parameters'][self.measurement_masks.name]['value'] = masks_metadata
        metadata['parameters'][self.measurement_masks.name]['raw_value'] = masks_metadata
        
        return metadata


def _calc_measurement_windows(mcp: MultiChannelProgram) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    temp_measurement_windows = defaultdict(list)
    for program in mcp.programs.values():
        for mw_name, begins_lengths in program.get_measurement_windows().items():
            temp_measurement_windows[mw_name].append(begins_lengths)

    # this while loop allows the garbage collector to collect stuff we already iterated over
    measurement_windows = dict()
    while temp_measurement_windows:
        mw_name, begins_lengths_deque = temp_measurement_windows.popitem()

        begins, lengths = zip(*begins_lengths_deque)
        measurement_windows[mw_name] = (
            np.concatenate(begins),
            np.concatenate(lengths)
        )
    return measurement_windows
