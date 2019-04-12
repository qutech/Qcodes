"""
This module implements a driver for the attocube ANC350 nanopositioner in
qcodes using the ANC350-python-library found at
https://github.com/Laukei/attocube-ANC350-Python-library.

The main functions are the get- and set methods for amplitude (voltage),
frequency, and position in all three directions. The latter first sets the
target position and then initiates the start_auto_move method (both of which
can also be done manually). The corresponding set method has an additional
keyword argument mode which toggles relative or absolute movement.

An example workflow:

>>> from qcodes.instrument_drivers.attocube.ANC350 import Attocube_ANC350
>>> ANC = Attocube_ANC350('foo')    # device named foo
>>> ANC.pos_x()                     # gets the current x-position
>>> ANC.pos_z(1e-7)                 # sets y-pos. to 100nm and starts movement
>>> ANC.freq_y()                    # gets the current y-frequency
>>> ANC.amp_x(2)                    # sets the voltage in x-direction to 2V
>>> ANC.disconnect()                # only one ANC can be connected at a time
>>> ANC.close()                     # tidy up
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Numbers

try:
    from attocube_ANC350_Python_library.PyANC350v4 import Positioner
except ImportError:
    raise ImportError('This driver requires the ANC350-Python-library. ' +
                      'You can find it at https://github.com/Laukei/' +
                      'attocube-ANC350-Python-library.')

__all__ = ["Attocube_ANC350", "AttocubePositionParameter",
           "AttocubeFrequencyParameter", "AttocubeAmplitudeParameter"]

class Attocube_ANC350(Instrument):
    def __init__(self, name, **kwargs):
        # Initialize the parent Instrument instance
        super().__init__(name, **kwargs)

        # Initialize the nanopositioner instance using the PyANC350 module
        self.positioner = Positioner()

        # Add x-, y-, and z-direction as gettable and settable parameters
        for direction in ('x', 'y', 'z'):
            self.add_parameter('pos_{}'.format(direction),
                               positioner=self.positioner,
                               parameter_class=AttocubePositionParameter,
                               direction=direction,
                               label='Position in {}'.format(direction),
                               unit='m')
            self.add_parameter('freq_{}'.format(direction),
                               positioner=self.positioner,
                               parameter_class=AttocubeFrequencyParameter,
                               direction=direction,
                               vals=Numbers(1, 2e3),
                               label='Frequency in {}'.format(direction),
                               unit='Hz')
            self.add_parameter('amp_{}'.format(direction),
                               positioner=self.positioner,
                               parameter_class=AttocubeAmplitudeParameter,
                               direction=direction,
                               vals=Numbers(0, 70),
                               label='Amplitude in {}'.format(direction),
                               unit='V')

    def _parse_direction_arg(self, direction):
        """
        A convenience function to allow for strings such as 'x' as arguments
        for the direction (instead of just the axis numbers 0, 1, 2)

        Parameters
            direction   One of {'x', 'y', 'z', 0, 1, 2}
        Returns
            axis_no     The axis id, e.g 0 if input was 'x'
        """
        from string import ascii_lowercase

        if direction is not None:
            if isinstance(direction, int):
                # direction correct format
                axis_no = direction
            elif isinstance(direction, str) and len(direction) == 1:
                # direction string, convert to int (x is 23rd in the alphabet)
                axis_no = ascii_lowercase.index(direction) - 23
            else:
                raise TypeError('Direction "{}" not a valid axis!'.format(
                        direction))
        else:
            raise ValueError('No direction provided!')
        return axis_no

    def get_device_info(self):
        """
        Returns available information about a device. The function can not be
        called before ANC_discover but the devices don't have to be connected.
        All Pointers to output parameters may be zero to ignore the respective
        value.

        Parameters
            dev_no  Sequence number of the device. Must be smaller than the
                    dev_count from the last ANC_discover call. Default: 0
        Returns
            dev_type    Output: Type of the ANC350 device. {0: Anc350Res,
                                1:Anc350Num, 2:Anc350Fps, 3:Anc350None}
            id          Output: programmed hardware ID of the device
            serial_no   Output: The device's serial number. The string buffer
                                should be NULL or at least 16 bytes long.
            address	   Output: The device's interface address if applicable.
                                Returns the IP address in dotted-decimal
                                notation or the string "USB", respectively. The
                                string buffer should be NULL or at least 16
                                bytes long.
            connected	Output: If the device is already connected
        """
        return self.positioner.getDeviceInfo()

    def get_axis_status(self, direction):
        """
        Reads status information about an axis of the device.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
        Returns
            connected   Output: If the axis is connected to a sensor.
            enabled     Output: If the axis voltage output is enabled.
            moving      Output: If the axis is moving.
            target      Output: If the target is reached in automatic
                                positioning
            eot_fwd     Output: If end of travel detected in forward direction.
            eot_bwd     Output: If end of travel detected in backward
                                direction.
            error	       Output: If the axis' sensor is in error state.
        """
        axis_no = self._parse_direction_arg(direction)
        return self.positioner.getAxisStatus(axis_no)

    def set_axis_output(self, direction, enable, auto_disable):
        """
        Enables or disables the voltage output of an axis.

        Parameters
            direction       Axis number (0 ... 2) or string ('x', 'y', 'z')
            enable          Enables (1) or disables (0) the voltage output.
            auto_disable    If the voltage output is to be deactivated
                            automatically when end of travel is detected.
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.setAxisOutput(axis_no, enable, auto_disable)

    def set_dc_voltage(self, direction, voltage):
        """
        Sets the DC level on the voltage output when no sawtooth based motion
        is active.

            Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            voltage     DC output voltage [V], internal resolution is 1 mV
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.setDcVoltage(axis_no, voltage)

    def start_single_step(self, direction, backward):
        """
        Triggers a single step in desired direction.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            backward    If the step direction is forward (0) or backward (1)
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.startSingleStep(axis_no, backward)

    def start_continuous_move(self, direction, start, backward):
        """
        Starts or stops continous motion in forward direction. Other kinds of
        motions are stopped.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            start       Starts (1) or stops (0) the motion
            backward    If the move direction is forward (0) or backward (1)
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.startContinuousMove(axis_no, start, backward)

    def start_auto_move(self, direction, enable, relative):
        """
        Switches automatic moving (i.e. following the target position) on or
        off

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            enable      Enables (1) or disables (0) automatic motion
            relative    If the target position is to be interpreted absolute
                        (0) or relative to the current position (1)
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.startAutoMove(axis_no, enable, relative)

    def set_target_position(self, direction, target):
        """
        Sets the target position for automatic motion, see start_auto_move. For
        linear type actuators the position unit is m, for goniometers and
        rotators it is degree.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            target      Target position [m] or [°]. Internal resulution is 1 nm or
                        1 µ°.
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.setTargetPosition(axis_no, target)

    def set_target_range(self, direction, target_rg):
        """
        Defines the range around the target position where the target is
        considered to be reached.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            target_rg   Target range [m] or [°]. Internal resulution is 1 nm or
                        1 µ°.
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.setTargetRange(axis_no, target_rg)

    def select_actuator(self, direction, actuator):
        """
        Selects the actuator to be used for the axis from actuator presets.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
            actuator    Actuator selection (0 ... 255)
                0: ANPg101res
                1: ANGt101res
                2: ANPx51res
                3: ANPx101res
                4: ANPx121res
                5: ANPx122res
                6: ANPz51res
                7: ANPz101res
                8: ANR50res
                9: ANR51res
                10: ANR101res
                11: Test
        Returns
            None
        """
        axis_no = self._parse_direction_arg(direction)
        self.positioner.selectActuator(axis_no, actuator)

    def get_actuator_name(self, direction):
        """
        Get the name of the currently selected actuator

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
        Returns
            name    Name of the actuator
        """
        axis_no = self._parse_direction_arg(direction)
        return self.positioner.getActuatorName(axis_no)

    def measure_capacitance(self, direction):
        """
        Performs a measurement of the capacitance of the piezo motor and
        returns the result. If no motor is connected, the result will be 0.
        The function doesn't return before the measurement is complete; this
        will take a few seconds of time.

        Parameters
            direction   Axis number (0 ... 2) or string ('x', 'y', 'z')
        Returns
            cap     Output: Capacitance [F]
        """
        axis_no = self._parse_direction_arg(direction)
        return self.positioner.measureCapacitance(axis_no)

    def save_params(self):
        """
        Saves parameters to persistent flash memory in the device. They will be
        present as defaults after the next power-on. The following parameters
        are affected: Amplitude, frequency, actuator selections as well as
        Trigger and quadrature settings.

        Parameters
            None
        Returns
            None
        """
        self.positioner.saveParams()

    def disconnect(self):
        """
        Closes the connection to the device. The device handle becomes invalid.

        Parameters
            None
        Returns
            None
        """
        self.positioner.disconnect()


class AttocubeParameter(Parameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        """Generic attocube parameter class for ANC350"""
        from string import ascii_lowercase

        # Initialize the parent Parameter instance
        super().__init__(**kwargs)

        # Check arguments
        if direction is not None:
            if isinstance(direction, int):
                # direction correct format
                self.direction = direction
            elif isinstance(direction, str) and len(direction) == 1:
                # direction string, convert to int (x is 23rd in the alphabet)
                self.direction = ascii_lowercase.index(direction) - 23
            else:
                raise TypeError('Direction "{}" not a valid axis!'.format(
                        direction))
        else:
            raise ValueError('No direction provided!')

        if positioner is not None:
            self._positioner = positioner
        else:
            raise ValueError('No positioner provided!')


class AttocubePositionParameter(AttocubeParameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        # Initialize the parent AttocubeParameter instance
        super().__init__(positioner=positioner, direction=direction, **kwargs)

    def get_raw(self):
        """
        Retrieves the current actuator position. For linear type actuators the
        position unit is m; for goniometers and rotators it is degree.

        Parameters
            None
        Returns
            position    Output: Current position [m] or [°]
        """
        return self._positioner.getPosition(self.direction)

    def set_raw(self, value, mode=0):
        """
        Starts automatic motion with the target position value. For linear type
        actuators the position unit is m, for goniometers and rotators it is
        degree.

        Parameters
            value   Target position [m] or [°]. Internal resulution is 1 nm or
                    1 µ°.
            mode    If the target position is to be interpreted absolute (0) or
                    relative to the current position (1). Also takes the
                    strings as argument.
        Returns
            None
        """
        if mode != 0:
            if isinstance(mode, str):
                if mode == 'relative':
                    mode = 1
                elif mode == 'absolute':
                    mode = 0
                else:
                    raise ValueError('Mode "{}" not a valid mode!'.format(
                            mode))
            elif isinstance(mode, int):
                if mode == 1:
                    pass
                else:
                    raise ValueError('Mode "{}" not a valid mode!'.format(
                            mode))
            else:
                raise TypeError('Mode "{}" not a valid mode!'.format(mode))

        self._positioner.setTargetPosition(self.direction, value)
        self._positioner.startAutoMove(self.direction, 1, mode)


class AttocubeFrequencyParameter(AttocubeParameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        # Initialize the parent AttocubeParameter instance
        super().__init__(positioner=positioner, direction=direction, **kwargs)

    def get_raw(self):
        """
        Reads back the frequency parameter of the axis.

        Parameters
            None
        Returns
            frequency   Output: Frequency in Hz
        """
        return self._positioner.getFrequency(self.direction)

    def set_raw(self, value):
        """
        Sets the frequency parameter for the axis

        Parameters
            value   Frequency in Hz, internal resolution is 1 Hz
        Returns
            None
        """
        self._positioner.setFrequency(self.direction, value)


class AttocubeAmplitudeParameter(AttocubeParameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        # Initialize the parent AttocubeParameter instance
        super().__init__(positioner=positioner, direction=direction, **kwargs)

    def get_raw(self):
        """
        Reads back the amplitude parameter of the axis.

        Parameters
            None
        Returns
            amplitude   Amplitude V
        """
        return self._positioner.getAmplitude(self.direction)

    def set_raw(self, value):
        """
        Sets the amplitude parameter for the axis

        Parameters
            value   Amplitude in V, internal resolution is 1 mV
        Returns
            None
        """
        self._positioner.setAmplitude(self.direction, value)
