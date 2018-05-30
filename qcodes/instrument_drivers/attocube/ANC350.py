from ANC350_Python_library.PyANC350v4 import Positioner
from qcodes import (Instrument, Parameter)


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
                               label='Frequency in {}'.format(direction),
                               unit='Hz')
            self.add_parameter('amp_{}'.format(direction),
                               positioner=self.positioner,
                               parameter_class=AttocubeAmplitudeParameter,
                               direction=direction,
                               label='Amplitude in {}'.format(direction),
                               unit='V')


class AttocubeParameter(Parameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
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
                raise TypeError('Direction "{}" not a valid axis!'.format(direction))
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

    def get(self):
        return self._positioner.getPosition(self.direction)

    def set(self, value, mode=0):
        if mode != 0:
            if isinstance(mode, str):
                if mode == 'relative':
                    mode = 1
                elif mode == 'absolute':
                    mode = 0
                else:
                    raise ValueError('Mode "{}" not a valid mode!'.format(mode))
            elif isinstance(mode, int):
                if mode == 1:
                    pass
                else:
                    raise ValueError('Mode "{}" not a valid mode!'.format(mode))
            else:
                raise TypeError('Mode "{}" not a valid mode!'.format(mode))

        self._positioner.setTargetPosition(self.direction, value)
        self._positioner.startAutoMove(self.direction, 1, mode)


class AttocubeFrequencyParameter(AttocubeParameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        print(direction, positioner)
        # Initialize the parent AttocubeParameter instance
        super().__init__(positioner=positioner, direction=direction, **kwargs)

    def get(self):
        return self._positioner.getFrequency(self.direction)

    def set(self, value):
        self._positioner.setFrequency(self.direction, value)


class AttocubeAmplitudeParameter(AttocubeParameter):
    def __init__(self, positioner=None, direction=None, **kwargs):
        # Initialize the parent AttocubeParameter instance
        super().__init__(positioner=positioner, direction=direction, **kwargs)

    def get(self):
        return self._positioner.getAmplitude(self.direction)

    def set(self, value):
        self._positioner.setAmplitude(self.direction, value)



if __name__ == '__main__':
    ANC = Attocube_ANC350('AlfaNovemberCharlie')
    for pos in ('x', 'y', 'z'):
        print('{} position:'.format(pos), ANC.get('pos_{}'.format(pos)))
        print('{} frequency:'.format(pos), ANC.get('freq_{}'.format(pos)))
        print('{} amplitude:'.format(pos), ANC.get('amp_{}'.format(pos)))
        # print(ANC.set('pos_{}'.format(pos), 1e-7))
        # print('{} position:'.format(pos), ANC.get('pos_{}'.format(pos)))

    ANC.positioner.disconnect()
    ANC.close()