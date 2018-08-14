
from qcodes import Instrument, Parameter, validators

try:
    from iDus_python_library.Camera.andor import Andor
except ImportError:
    raise ImportError('This driver requires the pyandor library. You can ' +
                      'find it at https://github.com/hamidohadi/pyandor.')

"""
cam = Andor()
cam.SetDemoReady()
cam.StartAcquisition()
data = []
cam.GetAcquiredData(data)
cam.SaveAsTxt('raw.txt')
cam.ShutDown()
"""

# %%

class Andor_iDus(Instrument):
    def __init__(self, name, dll_path=None, **kwargs):
        # Initialize the parent Instrument instance
        super().__init__(name, **kwargs)

        # Initialize the andor instance using the pyandor module
        self.andor = Andor(dll_path=dll_path)

        self.add_parameter('acquisition_mode',
                           label='Camera Acquisition Mode',
                           unit=None,
                           get_cmd=lambda: self.andor.AcquisitionMode,
                           set_cmd=self.andor.SetAcquisitionMode,
                           get_parser=self.acquisition_mode_parser,
                           val_mapping={'Unset': 0,
                                        'Single': 1,
                                        'Accumulate': 2,
                                        'Kinetic': 3})

    def acquisition_mode_parser(self, *args, **kwargs):
        val = self.andor.AcquisitionMode
        if val is None:
            return 0
        else:
            return int(val)
