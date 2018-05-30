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
            name = 'pos_{}'.format(direction)
            label = 'Position in {}'.format(direction)
            self.add_parameter(name, positioner=self.positioner,
                               parameter_class=AttocubePositionParameter,
                               direction=direction, label=label, unit='m')


class AttocubePositionParameter(Parameter):
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
                raise TypeError('Direction "{}" is not a valid axis!'.format(direction))
        else:
            raise ValueError('No direction provided!')

        if positioner is not None:
            self._positioner = positioner
        else:
            raise ValueError('No positioner provided!')

    def get(self):
        return self._positioner.getPosition(self.direction)

    def set(self, value):
        return self._positioner.setTargetPosition(self.direction, value)


if __name__ == '__main__':
    ANC = Attocube_ANC350('AlfaNovemberCharlie')
    for pos in ('x', 'y', 'z'):
        print('{} position:'.format(pos), ANC.get('pos_{}'.format(pos)))
        print(ANC.set('pos_{}'.format(pos), 1e-8))
        print('{} position:'.format(pos), ANC.get('pos_{}'.format(pos)))

    ANC.close()