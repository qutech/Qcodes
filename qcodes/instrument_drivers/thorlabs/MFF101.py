"""
Use ftd2xx.dll (pip install ftd2xx beforehand) instead of Thorlabs.APT.dll because the latter does not work for the flipper
Based on the discussion: https://github.com/qpit/thorlabs_apt/issues/3
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Enum
import ftd2xx
import ftd2xx.defines as constants
import time

class Thorlabs_MFF101(Instrument):

    def __init__(self, name, **kwargs):
        # Initialize the parent Instrument instance
        super().__init__(name, **kwargs)

        self.flipper = self.connect()

        self.add_parameter('position',
                           get_cmd = self.get_position,
                           set_cmd = self.set_position,
                           vals = Enum('open','close'),
                           label='Flipper mount position')

    def connect(self):

        serial = b"37000407"
        # Recommended d2xx setup instructions from Thorlabs.
        motor = ftd2xx.openEx(serial)
        print(motor.getDeviceInfo())
        motor.setBaudRate(115200)
        motor.setDataCharacteristics(constants.BITS_8, constants.STOP_BITS_1, constants.PARITY_NONE)
        time.sleep(.05)
        motor.purge()
        time.sleep(.05)
        motor.resetDevice()
        motor.setFlowControl(constants.FLOW_RTS_CTS, 0, 0)
        motor.setRts()

        return motor

    def getDeviceInfo(self):
        return self.flipper.getDeviceInfo()

    def set_position(self, position):
        if position == 'open':
            # Raw byte commands for "MGMSG_MOT_MOVE_JOG".
            up_position = b"\x6A\x04\x00\x01\x21\x01"
            self.flipper.write(up_position)
            time.sleep(2) # wait for the end of motion

        if position == 'close':
            # Raw byte commands for "MGMSG_MOT_MOVE_JOG".
            down_position = b"\x6A\x04\x00\x02\x21\x01"
            self.flipper.write(down_position)
            time.sleep(2) # wait for the end of motion

        if position not in ['close','open']:
            print('Shutter position can only be "close" or "open"')

    def get_position(self):
      #determine if motor is open or closed
      clsd_stat = b'*\x04\x06\x00\x81P\x01\x00\x02\x00\x00\x90' #closed byte status
      opn_stat  = b'*\x04\x06\x00\x81P\x01\x00\x01\x00\x00\x90' #open byte status
      st_bit = b"\x29\x04\x00\x00\x21\x01" #request status bits

      self.flipper.write(st_bit);
      mot_stat = self.flipper.read(12) #NOTE: EXACTLY 12 bits need to be read. If too many, python will freeze waiting for more. If too few, you won't get them all this time (but will get some next time you read)
      if mot_stat == opn_stat: #shutter appears to be open
        return 'open'
      elif mot_stat == clsd_stat: #shutter appears to be closed
        return 'closed'
      else:
        return 'unclear' #2 for confused

    def disconnect(self):
        self.flipper.close()
