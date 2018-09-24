import warnings
from typing import Union, List, Tuple, Dict

from qcodes import Instrument
import qcodes.utils.validators as validators

try:
    from vaunix_api import lsg
except ImportError:
    lsg = None


__all__ = ['LabBrickLSG']


class LabBrickLSG(Instrument):
    _vnx_api = None

    @classmethod
    def set_api(cls, vnx_lsg_api: 'lsg.VNX_LSG_API'):
        cls._vnx_api = vnx_lsg_api

    @classmethod
    def get_vnx_library(cls) -> 'lsg.VNX_LSG_API':
        if cls._vnx_api is None:
            cls.set_api(lsg.VNX_LSG_API.default())
        return cls._vnx_api

    @property
    def vnx_api(self) -> 'lsg.VNX_LSG_API':
        return self.get_vnx_library()

    def get_model_name(self) -> str:
        if self._model is None:
            try:
                self._model = self.vnx_api.get_model_name(self._device_id)
            except lsg.VNXError:
                warnings.warn('Could not retreive model %f' % self)
                return 'unknown'
        return self._model

    def get_idn(self) -> Dict[str, str]:
        return {'vendor': 'vaunix',
                'model': self.get_model_name(),
                'serial': self._serial_number,
                'firmware': str(self.vnx_api.get_dll_version())}

    def init_device(self):
        self.vnx_api.init_device(self._device_id)

    @classmethod
    def list_active_devices(cls) -> Tuple[List[int], List[int]]:
        """Return a list of the serial numbers and deviceids
        of all active devices"""

        # necessary to refresh the device ist
        cls.get_vnx_library().get_num_devices()

        device_ids = cls.get_vnx_library().get_dev_info()

        serial_numbers = [cls.get_vnx_library().get_serial_number(device_id)
                          for device_id in device_ids]
        return serial_numbers, device_ids

    def __init__(self, name, serial_number=None, **kwargs):
        super().__init__(name, **kwargs)

        serial_numbers, device_ids = self.list_active_devices()

        if serial_number is None and len(serial_numbers) == 1:
            serial_number = serial_numbers[0]

        try:
            device_id = device_ids[serial_numbers.index(serial_number)]
        except ValueError:
            raise RuntimeError('{} is not in the list of'
                               ' known serial numbers'.format(serial_number),
                               serial_numbers)

        self._device_id = device_id
        self._serial_number = serial_number
        self._model = None

        status = self.get_device_status()
        if not status.is_open():
            self.init_device()

        self.add_parameter('frequency',
                           set_cmd=self._set_frequency,
                           get_cmd=self._get_frequency,
                           unit='Hz',
                           vals=validators.PermissiveMultiples(100e3))

        self.add_parameter('power',
                           set_cmd=self._set_power,
                           get_cmd=self._get_power,
                           unit='dBm',
                           vals=validators.PermissiveMultiples(.25))

        self.add_parameter('rf_on',
                           vals=validators.Enum('on', 'off',
                                                True, False,
                                                0, 1),
                           set_cmd=self._set_rf_on,
                           get_cmd=self._get_rf_on)

    def get_device_status(self) -> 'lsg.LSGStatus':
        return lsg.LSGStatus(self.vnx_api.get_device_status(self._device_id))

    def _get_frequency(self) -> float:
        return self.vnx_api.get_frequency(self._device_id) * 100e3

    def _set_frequency(self, frequency: float):
        self.vnx_api.set_frequency(self._device_id, int(frequency // 100e3))

    def _get_power(self) -> float:
        return self.vnx_api.get_power_level(self._device_id) * .25

    def _set_power(self, power: float):
        self.vnx_api.set_power_level(self._device_id, int(power / .25))

    def _set_rf_on(self, rf_on: Union[str, int, bool]):
        # There has to be a better way
        rf_on = {'on': True,
                 'off': False,
                 1: True,
                 0: False,
                 False: False,
                 True: True}[rf_on]
        self.vnx_api.set_rf_on(self._device_id, rf_on)

    def _get_rf_on(self) -> bool:
        return bool(self.vnx_api.get_rf_on(self._device_id))

    def close(self):
        super().close()
        try:
            self.vnx_api.close_device(self._device_id)
        except lsg.VNXError:
            warnings.warn('Error while closing device %f', self)

    def __repr__(self):
        return '<{}: name={}, serial_number={}>'.format(type(self).__name__, self.name, self._serial_number)
