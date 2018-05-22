from qcodes.instrument.base import Instrument
from qcodes.instrument.parameter import Parameter
from qcodes.utils.validators import Numbers
import ctypes as ct
import os
import _error_codes
import _APTAPI

def _get_error_text(error_code):
    if (error_code == 0):
        return "Command successful."
    else:
        try:
            return _error_codes.error_message[error_code]
        except:
            return "Invalid error code."

class RotaryMount(Instrument):

    def __init__(self, name, serial_number, **kwargs):

        super().__init__(name, **kwargs)
        self._serial_number = serial_number

        #Load the library
        filename = "%s/APT.dll" % os.path.dirname(__file__)
        self.lib = ct.windll.LoadLibrary(filename)
        _APTAPI.set_ctypes_argtypes(self.lib)
        err_code = self.lib.APTInit()
        if (err_code == 0):
            print('Library imported')
        else:
            raise Exception("Thorlabs APT Initialization failed: " \
                            "%s" % _get_error_text(err_code))
        if (self.lib.EnableEventDlg(False) != 0):
            raise Exception("Couldn't disable event dialog.")

        #Initialize the device
        err_code = self.lib.InitHWDevice(self._serial_number)
        if (err_code != 0):
            raise Exception("Could not initialize device: %s" %
                    _get_error_text(err_code))
        else:
            print('Device initialization successful !')

        #Create parameters
        self.add_parameter('angle',
                           get_cmd = self._current_angle,
                           set_cmd = self._move_angle,
                           unit = '°',
                           label = 'Rotary Mount Angle',
                           vals = Numbers(min_value = 0, max_value = 360),
                           docstring = 'Round ND filter')

    def _current_angle(self):
        pos = ct.c_float()
        err_code = self.lib.MOT_GetPosition(self._serial_number,
                ct.byref(pos))
        if (err_code != 0):
            raise Exception("Getting position failed: %s" %
                    _get_error_text(err_code))
        return pos.value

    def _move_angle(self, angle, reference = 'absolute', blocking = False):
        #blocking: bool (wait until homed)
        if reference not in ['absolute', 'reference']:
            raise Exception("reference should either be 'absolute' or 'relative'")
        if reference == 'absolute':
            err_code = self.lib.MOT_MoveAbsoluteEx(self._serial_number, angle,
                                               blocking)
            if (err_code != 0):
                raise Exception("Setting absolute position failed: %s" %
                                _get_error_text(err_code))
        if reference == 'relative':
            err_code = self.lib.MOT_MoveRelativeEx(self._serial_number, angle,
                                               blocking)
            if (err_code != 0):
                raise Exception("Setting relative position failed: %s" %
                                _get_error_text(err_code))

    def move_home(self, blocking = False):
        #blocking: bool (wait until homed)
        err_code = self.lib.MOT_MoveHome(self._serial_number, blocking)
        if (err_code != 0):
            raise Exception("Moving home failed: %s" %
                    _get_error_text(err_code))

    def enable(self):
        err_code = self.lib.MOT_EnableHWChannel(self._serial_number)
        if (err_code != 0):
            raise Exception("Enabling channel failed: %s" %
                    _get_error_text(err_code))

    def disable(self):
        err_code = self.lib.MOT_DisableHWChannel(self._serial_number)
        if (err_code != 0):
            raise Exception("Disabling channel failed: %s" %
                    _get_error_text(err_code))

    def list_available_devices(self):
        devices = []
        count = ct.c_long()
        for hwtype in range(100):
            if (self.lib.GetNumHWUnitsEx(hwtype, ct.byref(count)) == 0):
                # found an existing hardware type
                if (count.value > 0):
                    # get its serial number
                    serial_number = ct.c_long()
                    for ii in range(count.value):
                        if (self.lib.GetHWSerialNumEx(hwtype, ii,
                                                  ct.byref(serial_number)) == 0):
                            devices.append((hwtype, serial_number.value))
        return devices

    def hardware_info(self):
        model = ct.c_buffer(255)
        swver = ct.c_buffer(255)
        hwnotes = ct.c_buffer(255)
        err_code = self.lib.GetHWInfo(self._serial_number, model, len(model),
                                  swver, len(swver), hwnotes, len(hwnotes))
        if (err_code != 0):
            raise Exception("Getting hardware info failed: %s" %_get_error_text(err_code))
        return (model.value, swver.value, hwnotes.value)

mount = RotaryMount('mount', 55001014)
devices = mount.list_available_devices()
print(devices)
info = mount.hardware_info()
print(info)
# print(mount.angle())
# mount.angle()
# mount._move_angle(50, blocking=True)
# mount.move_home(False)
pos = mount._current_angle()
print(pos)
# mount.enable()
# mount.move_home()