#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Johannes Dresen (jo.dressen@fz-juelich.de)
#         Michael Wagener (m.wagener@fz-juelich.de)
#         Lukas Lankes (l.lankes@fz-juelich.de)
#         all ZEA-2 at Forschungszentrum Jülich GmbH
# Date:   July 2018


from typing import Dict, Tuple
from qcodes import  InstrumentChannel, ChannelList, BufferedSweepableParameter, SweepFixedValues
from qcodes.utils import validators as vals
from qcodes.instrument.visa import VisaInstrument

import numpy as np

import warnings

class DACException(BaseException):

    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)


class DacBase(object):

    # Switch position values
    SWITCH_LEFT  = -1 # -10 <= U <=  0 [V]
    SWITCH_MID   = 0  #   0 <= U <= 10 [V]
    SWITCH_RIGHT = 1  # -10 <= U <= 10 [V]

    _SWITCH_POS_TO_RANGE = {SWITCH_LEFT:  (-10., 0.),
                            SWITCH_MID:   (0.,    10.),
                            SWITCH_RIGHT: (-10., 10.)}

    # Slot mode values
    SLOT_MODE_OFF    = 0 # Channel outputs are disconnected from the input, grounded with 10MOhm.
    SLOT_MODE_FINE   = 1 # 2-channel mode. Channels 0 and 1 are output, use 2 and 3 for fine adjustment of Channels 0 and 1 respectively
    SLOT_MODE_COARSE = 2 # All 4 channels are used as output

    # Trigger mode values
    TRIG_UPDATE_ALWAYS               = 0
    TRIG_UPDATE_NEVER                = 8
    TRIG_1_UPDATE_IF_LOW             = 2
    TRIG_1_UPDATE_IF_HIGH            = 10
    TRIG_1_UPDATE_UNTIL_RISING_EDGE  = 4
    TRIG_1_UPDATE_UNTIL_FALLING_EDGE = 6
    TRIG_1_UPDATE_AFTER_RISING_EDGE  = 12
    TRIG_1_UDPATE_AFTER_FALLING_EDGE = 14
    TRIG_2_UPDATE_IF_LOW             = 3
    TRIG_2_UPDATE_IF_HIGH            = 11
    TRIG_2_UPDATE_UNTIL_RISING_EDGE  = 5
    TRIG_2_UPDATE_UNTIL_FALLING_EDGE = 7
    TRIG_2_UPDATE_AFTER_RISING_EDGE  = 13
    TRIG_2_UPDATE_AFTER_FALLING_EDGE = 15

    # Validators
    _CHANNEL_VAL   = vals.Ints(0, 3)
    _SWITCH_VAL    = vals.Ints(SWITCH_LEFT, SWITCH_RIGHT)
    _MODE_VAL      = vals.Ints(SLOT_MODE_OFF, SLOT_MODE_COARSE)
    _SLOT_VAL      = vals.Ints(0, 4)
    _TRIG_MODE_VAL = vals.Enum(0, 2,3,4,5,6,7,8, 10,11,12,13,14,15) # The trigger modes 1 and 9 are undefined

    # Default values of the parameters
    _DEFAULT_VOLT          = 0
    _DEFAULT_SWITCH_POS    = SWITCH_MID
    _DEFAULT_LOWER_LIMIT   = 0
    _DEFAULT_UPPER_LIMIT   = 65536
    _DEFAULT_UPDATE_PERIOD = 1000
    _DEFAULT_SLOPE         = 0
    _DEFAULT_TRIG_MODE     = TRIG_UPDATE_ALWAYS
    _DEFAULT_SLOT_MODE     = SLOT_MODE_COARSE

    # Commands to send to the device (set parameters)
    _COMMAND_SET_SLOT          = "B{};"
    _COMMAND_SET_CHANNEL       = "C{};"
    _COMMAND_SET_VOLT          = "D{};"
    _COMMAND_SET_UPPER_LIMIT   = "U{};"
    _COMMAND_SET_LOWER_LIMIT   = "L{};"
    _COMMAND_SET_TRIG_MODE     = "G{};"
    _COMMAND_SET_SLOPE         = "S{};"
    _COMMAND_SET_UPDATE_PERIOD = "T{};"
    _COMMAND_SET_SLOT_MODE     = "M{};"

    # Commands to send to the device (get parameters) others are not gettable
    _COMMAND_GET_VOLT          = "d;"
    _COMMAND_GET_SLOPE         = "s;"
    _COMMAND_GET_SLOT_MODE     = "m;"

    @staticmethod
    def _dac_v_to_code(volt, min_volt, max_volt):
        """
        Convert a voltage to the internal dac code (number between 0-65536)
        based on the minimum/maximum values of a given channel.
        Midrange is 32768.

        Arguments:
            volt (float): voltage in V to convert
            min_volt (float): minimum voltage
            max_volt (float): maximum voltage

        Returns:
            (int): dac-code
        """
        if volt < min_volt or volt > max_volt:
            raise ValueError("Cannot convert voltage {} V to a voltage code, value out of range ({} V - {} V).".format(volt, min_volt, max_volt))

        frac = (volt - min_volt) / (max_volt - min_volt)
        val = int(round(frac * 65535))

        # extra check to be absolutely sure that the instrument does nothing
        # receive an out-of-bounds value
        if val > 65535 or val < 0:
            raise ValueError("Voltage ({} V) resulted in the voltage code {}, which is not within the allowed range.".format(volt, val))

        return val


    @staticmethod
    def _dac_code_to_v(code, min_volt, max_volt):
        """
        Convert the internal dac code (number between 0-65536) to the voltage value
        based on the minimum/maximum values of a given channel.

        Arguments:
            code (int): dac-code to convert
            min_volt (float): minimum voltage
            max_volt (float): maximum voltage

        Returns:
            (float): voltage in V
        """
        frac = code / 65535.0

        return (frac * (max_volt - min_volt)) + min_volt


    @staticmethod
    def _evaluate_switchpos(pos):
        """
        Returns the minimum and maximum voltages by the switch position

        Arguments:
            pos (int): switch position
                       {SWITCH_LEFT = -1, SWITCH_MID = 0, SWITCH_RIGHT = 1}

        Returns:
            (float, float): minimum and maximum voltage in V
        """
        min_volt = 0.
        max_volt = 0.

        if(pos == DacBase.SWITCH_LEFT):
            min_volt = -10.
        elif(pos == DacBase.SWITCH_MID):
            max_volt = 10.
        elif(pos == DacBase.SWITCH_RIGHT):
            min_volt = -10.
            max_volt = 10.
        else:
            raise ValueError("No valid switch position given.")

        return min_volt, max_volt


class DacChannel(InstrumentChannel, DacBase):

    def __init__(self, parent, name, channel, default_switch_pos=DacBase._DEFAULT_SWITCH_POS):
        """
        Initialize the channel

        Arguments:
            parent (DacSlot):         DacSlot object, the channel belongs to
            name (String):            name of the channel
            channel (int):            number of the channel
            switch_pos (int):         switch position of the channel

        Attributes:
            name (str):               name of the channel
            volt (float):             voltage of the channel
            lower_ramp_limit (float): used to sweep dac voltages
            upper_ramp_limit (float): used to sweep dac voltages
            update_period (int):      time between two refreshes in us (mircoseconds)
            slope (int):              ramp slope
            switch_pos (int):         position of the channel switch for the voltage range {SWITCH_LEFT, SWITCH_MID, SWITCH_RIGHT}
            trig_mode (int):          trigger mode {TRIG_UPDATE_*, TRIG_1_UPDATE_*, TRIG_2_UPDATE_*}
        """
        InstrumentChannel.__init__(self, parent, name)

        DacChannel._CHANNEL_VAL.validate(channel)
        self.number = channel

        # Validators
        self._volt_val = DacVoltValidator(self)
        self._volt_raw_val = vals.Ints(0, 65535)
        self._ramp_val = vals.Numbers(0, 10)

        self._default_switch_pos = default_switch_pos

        # these are pure software parameters
        self._max_ramp_rate = None

        # internal setting whether to set via ramping
        # there is no (public) set functionality yet
        self._set_volt_via_ramp = True

        # Channel parameters
        # Voltage
        self.add_parameter("volt", parameter_class=BufferedSweepableParameter,
                           sweep_parameter_cmd=self._sweep_parameter, send_buffer_cmd=self._send_buffer, run_program_cmd=self._run_program,
                           get_cmd=self._get_volt, get_parser=self._dac_code_to_v, set_cmd=self._set_volt, set_parser=self._dac_v_to_code, vals=self._volt_val, label="Voltage", unit="V")
        self.add_parameter("volt_raw", get_cmd=self._get_volt, set_cmd=self._set_volt, vals=self._volt_raw_val, label="Voltage (raw data)")

        # Slope
        self.add_parameter("slope",
                           get_cmd=self._get_slope, get_parser=int,
                           set_cmd=self._set_slope, set_parser=int,
                           vals=vals.Ints(-(2 ** 32), 2 ** 32), label="Ramp Slope (bin/s)")

        # The following parameters cannot read out from the device
        # The limit commands are used to sweep dac voltages. They are not safety features.
        self.add_parameter("lower_ramp_limit", get_parser=self._dac_code_to_v, set_cmd=self._set_lower_limit, set_parser=self._dac_v_to_code, vals=self._volt_val, label="Lower Ramp Limit", unit="V")
        self.add_parameter("upper_ramp_limit", get_parser=self._dac_code_to_v, set_cmd=self._set_upper_limit, set_parser=self._dac_v_to_code, vals=self._volt_val, label="Upper Ramp Limit", unit="V")
        self.add_parameter("lower_ramp_limit_raw", set_cmd=self._set_lower_limit, vals=self._volt_raw_val, label="Lower Ramp Limit (raw data)")
        self.add_parameter("upper_ramp_limit_raw", set_cmd=self._set_upper_limit, vals=self._volt_raw_val, label="Upper Ramp Limit (raw data)")

        # Ramping parameters
        self.add_parameter("update_period", get_parser=int, set_cmd=self._set_update_period, set_parser=int, vals=vals.Ints(50, 65535), label="Update Period", unit="us")

        self.add_parameter("switch_pos", set_cmd=None, get_cmd=None,
                           vals=self._SWITCH_VAL, label="Switch Position")
        self.add_parameter("trig_mode", set_cmd=self._set_trig_mode, vals=self._TRIG_MODE_VAL, label="Trigger Mode")

        # inferred from the switch position: not settable
        self.add_parameter("voltage_range", get_cmd=self._get_voltage_range, set_cmd=False,
                           label="Full output range",
                           docstring="Output range. Depends on the switch position.")

        # Add ramp function to the list of functions
        self.add_function("ramp", call_cmd=self._ramp, args=(self._volt_val, self._ramp_val))
        self.add_function("ramp_wait", call_cmd=self._ramp_wait, args=(self._volt_val, self._ramp_val))

    def _sweep_parameter(self, parameter, sweep_values, layer) -> None:
        """
        Adds the sweep information to a list, to build up a single buffer later

        Args:
            parameter: Parameter to sweep
            sweep_values: Values the parameter should be swept over.
            layer: nnumber of nested loop (most outer loop: 0)
        """
        self._parent._sweep_parameter(self, parameter, sweep_values, layer)

    def _get_voltage_range(self) -> Tuple[float, float]:
        """Return the minimal and maximal output voltage in Volts.
        Raises a Value error if the switch position is not set yet."""
        switch_pos = self.switch_pos.get()

        if switch_pos is None:
            raise ValueError("Switch position has not been set")
        else:
            return DacBase._SWITCH_POS_TO_RANGE[switch_pos]

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
        return self._parent._send_buffer(self, layer)

    def _run_program(self, layer):
        """
        Runs the waveform program on the awg as soon as this function was
        called for the last (buffered) loop
        """
        return self._parent._run_program(self, layer)

    def reset(self):
        """
        Resets all parameters to default
        """
        raise NotImplementedError("Reset logic is not sound")

        self.volt.set(DacBase._DEFAULT_VOLT)
        self.lower_limit.set(DacBase._DEFAULT_LOWER_LIMIT)
        self.upper_limit.set(DacBase._DEFAULT_UPPER_LIMIT)
        self.update_period.set(DacBase._DEFAULT_UPDATE_PERIOD)
        self.slope.set(DacBase._DEFAULT_SLOPE)
        self.trig_mode.set(DacBase._DEFAULT_TRIG_MODE)

        self.switch_pos.set(self._default_switch_pos)

        warnings.warn('All parameters of the Dacadac "{}" have been reset to their defaults.'.format(self.name))

        return (DacBase._COMMAND_SET_UPPER_LIMIT.format(self._upper_limit)
              + DacBase._COMMAND_SET_LOWER_LIMIT.format(self._lower_limit)
              + DacBase._COMMAND_SET_VOLT.format(self._volt)
              + DacBase._COMMAND_SET_TRIG_MODE.format(self._trig_mode)
              + DacBase._COMMAND_SET_SLOPE.format(self._slope)
              + DacBase._COMMAND_SET_UPDATE_PERIOD.format(self._update_period))

    def _get_volt(self) -> int:
        """
        Reads out the voltage of the channel as dac-code
        """
        buf = self._parent._write(self, DacBase._COMMAND_GET_VOLT)
        return int(buf[1:-1])

    def _set_volt(self, volt: int):
        """
        Sets the voltage for the channel as dac-code
        """
        #self._ramp_help_dac_units(volt, )
        self._parent._write(self, DacBase._COMMAND_SET_VOLT.format(volt))

    def _set_lower_limit(self, lower_limit):
        """
        Sets the lower ramp limit as dac-code
        """
        self._parent._write(self, DacBase._COMMAND_SET_LOWER_LIMIT.format(lower_limit))

    def _set_upper_limit(self, upper_limit):
        """
        Sets the upper ramp limit as dac-code
        """
        self._parent._write(self, DacBase._COMMAND_SET_UPPER_LIMIT.format(upper_limit))

    def _set_trig_mode(self, trig_mode):
        """
        Sets the update trigger mode
        """
        self._parent._write(self, DacBase._COMMAND_SET_TRIG_MODE.format(trig_mode))

    def _set_update_period(self, update_period):
        """
        Sets the update period (time between to refreshs in us)
        """
        self._parent._write(self, DacBase._COMMAND_SET_UPDATE_PERIOD.format(update_period))

    def _get_slope(self) -> int:
        """
        Gets the ramp slope
        """
        buf = self._parent._write(self, DacBase._COMMAND_GET_SLOPE)
        return int(buf[1:-1])

    def _set_slope(self, slope):
        """
        Sets the ramp slope
        """
        self._parent._write(self, DacBase._COMMAND_SET_SLOPE.format(slope))

    def _ramp_help_dac_units(self, target: int, rate: float, wait: bool):
        """
        Ramp the DAC to a given voltage. And eventually wait until it's done.

        Params:
            val (int):  The voltage to ramp to in DAC units
            rate (float): The ramp rate in units of (DAC Units)/s
            wait (bool):  True if the function should wait until the ramp is done
        """
        current_voltage = self.volt_raw.get()

        if current_voltage == target:
            return

        # Number of refreshes per second
        t_rate = 1e6 / self.update_period.get()

        # ramp duration in seconds
        ramp_duration = abs((target - current_voltage) / rate)

        # The formula to calculate the slope is:
        # Number of DAC steps divided by the number of time steps in the ramp multiplied by 65536
        slope = int((target - current_voltage) / (t_rate * ramp_duration) * 2**16)

        # wait with command execution until all commands are sent
        self.trig_mode.set(DacBase.TRIG_UPDATE_NEVER)

        # Now let's set up our limits and ramp slope
        self.slope.set(slope)

        if slope > 0:
            self.upper_ramp_limit_raw.set(target)
        else:
            self.lower_ramp_limit_raw.set(target)

        # start execution
        self.trig_mode.set(DacBase.TRIG_UPDATE_ALWAYS)

        # Block until the ramp is complete is block is True
        if wait:
            while self.volt_raw.get() != target:
                pass

    def _ramp_help_volts(self, val: float, rate: float, wait: bool):
        """
        Ramp the DAC to a given voltage. And eventually wait until it's done.

        Params:
            val (float):  The voltage to ramp to in V
            rate (float): The ramp rate in units of V/s
            wait (bool):  True if the function should wait until the ramp is done
        """

        dac_val = self._dac_v_to_code(val) # Endpoint in DAC units
        dac_rate = rate * (2**16 - 1) / float.__sub__(*self.voltage_range.get()) # Endpoint in (DAC Units)/s
        self._ramp_help_dac_units(target=dac_val, rate=dac_rate, wait=wait)

    def _ramp(self, val, rate):
        """
        Ramp the DAC to a given voltage.

        Params:
            val (float):  The voltage to ramp to in V
            rate (float): The ramp rate in units of V/s
        """
        self._ramp_help_volts(val, rate, False)

    def _ramp_wait(self, val, rate):
        """
        Ramp the DAC to a given voltage and wait until it's done

        Params:
            val (float):  The voltage to ramp to in V
            rate (float): The ramp rate in units of V/s
        """
        self._ramp_help_volts(val, rate, True)

    def _dac_v_to_code(self, volt):
        """
        Convert a voltage to the internal dac code (number between 0-65536)
        based on the minimum/maximum values of a given channel.
        Midrange is 32768.

        Arguments:
            volt (float): voltage in V to convert

        Returns:
            (int): dac-code
        """
        return DacBase._dac_v_to_code(volt, *self.voltage_range.get())

    def _dac_code_to_v(self, code):
        """
        Convert the internal dac code (number between 0-65536) to the voltage value
        based on the minimum/maximum values of a given channel.

        Arguments:
            code (int): dac-code to convert

        Returns:
            (float): voltage in V
        """
        if code is None:
            raise ValueError("Voltage code is None (this hints to an unset value that cannot be read from the device)")
        return DacBase._dac_code_to_v(code, *self.voltage_range.get())


class DacVoltValidator(vals.Validator):

    is_numeric = True


    def __init__(self, parent: DacChannel) -> None:
        """
        Initialize the voltage validator

        Arguments:
            parent (DacChannel): channel this validator belongs to
        """
        self._parent = parent


    def validate(self, value, context=""):
        """
        Checking if the voltage is in a valid range (_min_volt and _max_volt of the parent channel)

        Arguments:
            value (float): voltage to check
            context (str): context of the function call for error handling
        """
        if not isinstance(value, vals.Numbers.validtypes):
            raise TypeError("{} is not an int or float.\n{}".format(repr(value), context))

        if self._parent.switch_pos.get() is None:
            raise ValueError("No voltage interval is given for the Decadac instrument. Please set the switch_pos parameter.\n{}".format(context))

        min_volt, max_volt = self._parent.voltage_range.get()
        if not (min_volt <= value <= max_volt):
            raise ValueError("DacVoltValidator is invalid: must be between {} and {} inclusive.\n{}".format(min_volt, max_volt, context))


class DacSlot(InstrumentChannel, DacBase):

    def __init__(self, parent, name, slot, default_switch_pos=DacBase._DEFAULT_SWITCH_POS):
        """
        Initialize the slot

        Arguments:
            parent (Decadac):       Decadac object this slot belongs to
            name (str):             name of the slot
            slot (int):             number of the slot
            switch (int):           switch position of all channels of this slot
            mode (int):             slot mode (MODE_OFF, MODE_FINE, MODE_COARSE)

        Attributes:
            name (str):             name of the slot
            channels (ChannelList): list of channels in this slot
            mode (int):             slot mode (MODE_OFF, MODE_FINE, MODE_COARSE)
        """
        InstrumentChannel.__init__(self, parent, name)

        DacSlot._SLOT_VAL.validate(slot)
        self.number = slot

        channels = ChannelList(self, "Slot_Chans", DacChannel)

        for channel in range(4):
            channels.append(DacChannel(self, "Chan{}".format(channel), channel, default_switch_pos=default_switch_pos))

        self.add_submodule("channels", channels)

        self.add_parameter("mode", get_cmd=self._get_mode, set_cmd=self._set_mode, vals=self._MODE_VAL, label="Slot Mode")

    def _sweep_parameter(self, obj, parameter, sweep_values, layer) -> None:
        """
        Adds the sweep information to a list, to build up a single buffer later

        Args:
            parameter: Parameter to sweep
            sweep_values: Values the parameter should be swept over.
            layer: nnumber of nested loop (most outer loop: 0)
        """
        self._parent._sweep_parameter(obj, parameter, sweep_values, layer)

    def _send_buffer(self, obj, layer) -> Dict:
        """
        Waits until this function is called for all swept parameters. Then the
        buffer will be built and sent to the device.

        Args:
            layer: nnumber of nested loop (most outer loop: 0)

        Returns:
            Dictionary of the measurement windows if the function was called
            the last parameter. If not it returns None.
        """
        return self._parent._send_buffer(obj, layer)

    def _run_program(self, obj, layer):
        """
        Runs the waveform program on the awg as soon as this function was
        called for the last (buffered) loop
        """
        return self._parent._run_program(obj, layer)

    def reset(self):
        """
        Resets all parameters to default
        """
        self._mode = DacBase._DEFAULT_SLOT_MODE

        return (DacBase._COMMAND_SET_SLOT_MODE).format(self._mode)


    def _get_mode(self):
        """
        Gets the slot mode
        """
        return self._mode


    def _set_mode(self, mode):
        """
        Sets the slot mode
        """
        self._parent._write(self, DacBase._COMMAND_SET_SLOT_MODE.format(mode))
        self._mode = mode


    def _write(self, obj, cmd):
        """
        Forward the write method of the Decadac class
        """
        return self._parent._write(obj, cmd)


class Decadac(VisaInstrument):

    _DEFAULT_RESET    = False
    _DEFAULT_BAUDRATE = 9600
    _DEFAULT_TIMEOUT  = 5


    _device_connected = False
    enable_output = False

    def __init__(self, name, address,
                 reset=None,
                 timeout=None,
                 default_switch_pos=None,
                 terminator='\n',
                 run_buffered_cmd=None,
                 **kwargs):
        """
        Initialize the device

        Args:
            name (str):               name of the device
            address (str):            address of the device (e.g. /dev/ttyUSB0)
            reset (bool):             if "True", set all voltages to zero, set trigger mode to "always update" and stop ramps. If "False" only the upper and lower limit is reset.
            baudrate (int):           baud rate of ASCII protocol
            timeout (int):            seconds to allow for responses. Default 5
            default_switch_pos (int): default switch position (-1, 0 or 1) that is set when reset is called (default: 0)

        Attributes:
            name (str):               name
            slots (ChannelList):      list of all slots
            channels (ChannelList):   list of all channels
        """
        if reset is None:
            reset = self._DEFAULT_RESET

        if timeout is None:
            timeout = self._DEFAULT_TIMEOUT

        if default_switch_pos is None:
            default_switch_pos = DacBase._DEFAULT_SWITCH_POS

        super().__init__(name, address, timeout=timeout, terminator=terminator,
                         **kwargs)

        self.current_slot = None
        self.current_channel = None

        channels = ChannelList(self, "Channels", DacChannel)
        slots = ChannelList(self, "Slots", DacSlot)

        for slot in range(5):
            slots.append(DacSlot(self, "Slot{}".format(slot), slot, default_switch_pos=default_switch_pos))
            channels.extend(slots[slot].channels)

        slots.lock()
        channels.lock()

        self.add_submodule("slots", slots)
        self.add_submodule("channels", channels)

        self.run_buffered_cmd = run_buffered_cmd
        self._buffered_loop = None

        if reset:
            self.reset()


    def close(self):
        """
        Close the device connection
        """
        self.current_slot = None
        self.current_channel = None

        self.submodules.clear()

        super().close()


    def reset(self):
        """
        Reset all parameters to default
        """
        self.reset_programs()

        cmd = ""

        for slot in self.slots:
            cmd += DacBase._COMMAND_SET_SLOT.format(slot.number)
            cmd += slot.reset()

            for channel in self.channels:
                cmd += DacBase._COMMAND_SET_CHANNEL.format(channel.number)
                cmd += channel.reset()

        cmd += DacBase._COMMAND_SET_SLOT.format(0) + DacBase._COMMAND_SET_CHANNEL.format(0) # Select first slot and channel

        self._write(self, cmd)

    def reset_programs(self):
        """
        Resets all buffered loop actions
        """
        self._buffered_loop = None

    def _sweep_parameter(self, obj, parameter, sweep_values, layer) -> None:
        """
        Adds the sweep information to a list, to build up a single buffer later

        Args:
            parameter: Parameter to sweep
            sweep_values: Values the parameter should be swept over.
            layer: nnumber of nested loop (most outer loop: 0)
        """
        if self._buffered_loop is not None:
            raise NotImplementedError('It is not supported by the Decadac to nest multiple buffered loops.')

        ramp_start = sweep_values[0]
        ramp_stop  = sweep_values[-1]
        ramp_num   = len(sweep_values)

        if list(SweepFixedValues(obj, start=ramp_start, stop=ramp_stop, num=ramp_num)) != list(sweep_values) or ramp_start == ramp_stop:
            raise NotImplementedError('It is not supported by the Decadac to sweep parameters in a non-linear order.')

        self._buffered_loop = {
            'parameter'  : parameter.name,
            'ramp_start' : ramp_start,
            'ramp_stop'  : ramp_stop,
            'ramp_num'   : ramp_num
        }

    def _send_buffer(self, obj, layer) -> Dict:
        """
        Waits until this function is called for all swept parameters. Then the
        buffer will be built and sent to the device.

        Args:
            obj: Channel -> Caller of the function
            layer: Number of nested loop (most outer loop: 0)

        Returns:
            Dictionary of the measurement windows if the function was called
            the last parameter. If not it returns None.
        """
        if self._buffered_loop is not None:
            param_name = self._buffered_loop['parameter']

            if param_name == obj.volt.name:
                v_start = self._buffered_loop['ramp_start']
                v_stop = self._buffered_loop['ramp_stop']
                num = self._buffered_loop['ramp_num']

                # Convert voltages to dac-codes
                c_start = obj._dac_v_to_code(v_start)
                c_stop = obj._dac_v_to_code(v_stop)
            elif param_name == obj.volt_raw.name:
                c_start = self._buffered_loop['ramp_start']
                c_stop = self._buffered_loop['ramp_stop']
                num = self._buffered_loop['ramp_num']
            else:
                raise NotImplementedError('Only the volt-parameters can be used in a buffered loop with the Dacadac.')

            # Calculate the slope
            slope = int((c_stop - c_start) / (num - 1) * 65536)

            meas_length = obj.update_period.get () * 1000. # Microseconds to nanoseconds

            window_begins  = np.linspace(0, meas_length * (num-1), num=num)
            window_lengths = np.array([meas_length] * num)

            measurement_windows = { 'M' : (window_begins, window_lengths) }

            # Now let's set up our limits and ramp slope
            if c_start < c_stop:
                obj.lower_ramp_limit_raw.set(c_start)
                obj.upper_ramp_limit_raw.set(c_stop)
            else:
                obj.upper_ramp_limit_raw.set(c_start)
                obj.lower_ramp_limit_raw.set(c_stop)

            obj.volt_raw.set(c_start)

            obj.slope.set(slope)

            return measurement_windows

        return None

    def _run_program(self, obj, layer):
        """
        Runs the waveform program on the awg as soon as this function was
        called for the last (buffered) loop
        """
        if self.run_buffered_cmd is not None:
            self.run_buffered_cmd()

        self.reset_programs()

    def _set_slot(self, slot: DacSlot):
        """
        Sets the current used slot

        Arguments:
            slot (DacSlot): number of the current slot
        """
        if self.current_slot == None or self.current_slot.number != slot.number:
            self._write(self, DacBase._COMMAND_SET_SLOT.format(slot.number))
            self.current_slot = slot

            return True

        return False


    def _set_channel(self, slot: DacSlot, channel: DacChannel):
        """
        Sets the current used channel

        Arguments:
            slot (DacSlot):       number of the current slot
            channel (DacChannel): number of the current channel in this slot
        """

        if self._set_slot(slot) or self.current_channel == None or self.current_channel.number != channel.number:
            self._write(self, DacBase._COMMAND_SET_CHANNEL.format(channel.number))
            self.current_channel = channel

            return True

        return False


    def _write(self, obj, cmd):
        """
        Send a command to the device

        Arguments:
            obj (object): object that wants to write something (needed to set the current slot and channel)
            cmd (str):    command
        """
        if obj != None:
            # do not use isinstance due to autoreload
            if type(obj).__name__ == 'DacSlot':
                self._set_slot(obj)
            elif type(obj).__name__ == 'DacChannel':
                self._set_channel(obj._parent, obj)

        buf = super().ask_raw(cmd)

        # Check if write and read run successfully
        # The first letter of query and answer has to be equal otherwise the answer does not belong to the write-query. Maybe the device buffer is damaged.
        # The last letter of the answer has to be an exclamation mark ("!"). This means the write-query was handled successfully.
        if buf[0] != cmd[0]:
            raise DACException("Could not write \"{}\" to the device. Please check the device buffer.".format(cmd))
        elif buf[-1] != '!':
            raise DACException("Could not write \"{}\" to the device.".format(cmd))

        if Decadac.enable_output:
            print("Decadac._write(\"{}\") = {}".format(cmd, buf))

        return buf