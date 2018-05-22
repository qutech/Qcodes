# from qcodes.instrument.base import Instrument
# from qcodes.instrument.parameter import Parameter
# from qcodes.utils.validators import Numbers

try:
    import thorlabs_apt as apt

except ImportError as err:
    raise ImportError('This driver requires thorlabs_apt. You can find it at https://github.com/qpit/thorlabs_apt')

# devices = apt.list_available_devices()
# print(devices)
#
# if (50, 55001014) not in devices:
#     raise RuntimeError('Could not find device')

# motor = apt.Motor(55001014)
#
# # set default values
# motor.acceleration = 10.
# motor.move_home_velocity = 10.
#
# motor.move_to(30, True)
# # motor.move_home(True)

def getHWList():
    return apt.list_available_devices()

def getHWinfo(serial_number):
    return apt.hardware_info(serial_number)

class RotaryMount(Instrument):

    def __init__(self, name, serial_number, blocking = True, reference = 'absolute', **kwargs):

        super().__init__(name, **kwargs)
        self.serial_number = serial_number
        self.blocking = blocking
        self.reference = reference

        #Initialize Motor
        self.mt = apt.Motor(self.serial_number)
        self.mt.acceleration = 10.
        self.mt.move_home_velocity = 10.
        # self.mt.minimum_velocity = 0. #does not seem necessary, the speed is adjusted depending on the angle to travel
        # self.mt.maximum_velocity = 10.

        #Create parameters
        self.add_parameter('angle',
                           get_cmd = self._get_angle,
                           set_cmd = self._set_angle,
                           unit = '°',
                           label = 'Rotary Mount Angle',
                           vals = Numbers(min_value = -360, max_value = 360),
                           docstring = 'Round ND filter')

    @property
    def blocking(self):
        return self._blocking
    @blocking.setter
    def blocking(self, value):
        if not isinstance(value, bool):
            raise TypeError('blocking must be a bool')
        self._blocking = value

    @property
    def reference(self):
        return self._reference
    @reference.setter
    def reference(self, value):
        if not isinstance(value, str):
            raise TypeError('reference must be an str')
        self._reference = value

    @property
    def is_moving(self):
        return self.mt.is_in_motion

    @property
    def homing_completed(self):
        return self.mt.has_homing_been_completed

    def _get_angle(self):
        return self.mt.position

    def _set_angle(self, value):
        if self.reference not in ['absolute', 'relative']:
            raise Exception("reference should either be 'absolute' or 'relative'")
        if self.reference == 'absolute':
            self.mt.move_to(value, self.blocking)
        if self.reference == 'relative':
            self.mt.move_by(value, self.blocking)

    def enable(self):
        self.mt.enable()

    def disable(self):
        self.mt.disable()

    def move_home(self):
        self.mt.move_home(self.blocking)


mount = RotaryMount('mount13', 55001014)