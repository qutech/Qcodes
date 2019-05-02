from qcodes.instrument.base import Instrument
from qcodes.utils.validators import Numbers, Enum, Ints

try:
    import thorlabs_apt as apt

except ImportError as err:
    raise ImportError('This driver requires thorlabs_apt. You can find it at https://github.com/qpit/thorlabs_apt')


def getHWList():
    return apt.list_available_devices()

def getHWinfo(serial_number):
    return apt.hardware_info(serial_number)

class RotaryMount(Instrument):

    def __init__(self, name, serial_number, blocking = 1, reference = 'absolute', **kwargs):

        super().__init__(name, **kwargs)
        self.serial_number = serial_number
        self._blocking = blocking
        self._reference = reference

        #### Initialize Motor
        self.mt = apt.Motor(self.serial_number)
        self.mt.acceleration = 10.
        self.mt.move_home_velocity = 10.
#         self.mt.minimum_velocity = 0. #does not seem necessary, the speed is adjusted depending on the angle to travel
#         self.mt.maximum_velocity = 10.

        #### Create parameter
        self.add_parameter('angle',
                           get_cmd = self._get_angle,
                           set_cmd = self._set_angle,
                           unit = '°',
                           label = 'Motor angle',
                           vals = Numbers(min_value = -360, max_value = 360),
                           docstring = 'Round ND filter')
        
        self.add_parameter('ref',
                           get_cmd = self._get_reference,
                           set_cmd = self._set_reference,
                           label = 'type of motion',
                           vals = Enum('absolute','relative'),
                           docstring = 'Absolute or relative motion')
        
        self.add_parameter('output',
                           get_cmd = self._get_output_status,
                           set_cmd = self._set_output_status,
                           label = 'motor output',
                           vals = Enum('ON','OFF',1,0),
                           docstring = 'Enable or disable motor')
        
        self.add_parameter('acceleration',
                           get_cmd = self._get_motor_acceleration,
                           set_cmd = self._set_motor_acceleration,
                           label = 'motor acceleration',
                           vals = Ints(0,10))
        
        self.add_parameter('block',
                           get_cmd = self._get_blocking,
                           set_cmd = self._set_blocking,
                           label = 'motor blocking',
                           docstring = 'block any actions until end of motion')

        
    def _get_blocking(self):
        return self._blocking
    
    def _set_blocking(self, value):
        self._blocking = value
    
    def _get_motor_acceleration(self):
        return self.mt.acceleration
    
    def _set_motor_acceleration(self,acc):
        self.mt.acceleration = acc
        self.mt.move_home_velocity = acc

    def _get_reference(self):
        return self._reference
    
    def _set_reference(self, ref):
        self._reference = ref

    def _get_angle(self):
        return self.mt.position

    def _set_angle(self, value):
        if self._reference not in ['absolute', 'relative']:
            raise Exception("reference should either be 'absolute' or 'relative'")
        if self._reference == 'absolute':
            self.mt.move_to(value, self._blocking)
        if self._reference == 'relative':
            self.mt.move_by(value, self._blocking)
        
    def _set_output_status(self, status):
        if status == 1 or status == 'ON':
            self.mt.enable()
        if status == 0 or status == 'OFF':
            self.mt.disable()
            
    def _get_output_status(self):
        if self.mt.is_channel_enabled:
            return('ON')
        else:
            return('OFF')

    def is_moving(self):
        return self.mt.is_in_motion

    def is_homing_completed(self):
        return self.mt.has_homing_been_completed
            
    def move_home(self):
        self.mt.move_home(self._blocking)