# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 19:13:36 2019

@author: PLlab
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Numbers
from pyPIE871 import PIController

'''
NOTES: FOR SOME REASONS, THE OPEN LOOP FUNCTIONS OMA and qOMA DON'T WORK 
'''

class PIE871(Instrument):
    
    @classmethod
    def list_devices(cls) -> list:
        l = PIController.list_usb_devices()
        PI = []
        for i in range(0,len(l)):
            if l[i].split()[0] == b'PI':
                PI.append(l[i].split()[-1])
        return PI
                    
    def __init__(self, name, serial, **kwargs):
              
        super().__init__( name, **kwargs)

        self.pic = PIController(serial)
#        self.pic = PIController(PIController.list_usb_devices()[0].split()[-1])
        self.axis_id = self.axis_name()
        
        """ useful parameters """     
        self.add_parameter('mode',
                           get_cmd = self.get_control_mode,
                           set_cmd = self.set_control_mode,
                           get_parser = int,
                           docstring = '1 for the closed-loop mode, 0 for the open-loop mode')
        
        self.add_parameter('pos',
                           get_cmd = self.get_position,
                           get_parser = float,
                           label = 'Current positions of szAxis',
                           unit = 'mm',
                           docstring = ' Note that the current positiion has been set initially on 0mm ')
                
        self.add_parameter('cl_tar_pos',
                           get_cmd = self.get_cl_tar_pos,
                           set_cmd = self.set_cl_tar_pos,
                           get_parser = float,
                           label = 'Target positions of szAxis for closed-loop mode',
                           unit = 'mm')

    """ functions """
    def disconnect(self):
        self.pic.disconnect()
    
    def status(self):       
        if self.pic.is_Connected():
            idn = self.pic.IDN()
            return 'Actuator connected to the controller: ' + idn
        else:
            return "ERROR: The stage cannot been connected!"
        
    def axis_name(self):
        return self.pic.qSAI_All()
    
    def axis_range(self):
        rValue = []
        rValue.append(self.pic.qTMN(self.axis_id))
        rValue.append(self.pic.qTMX(self.axis_id))
        return rValue
    
    def ref(self, cur_pos):
        if self.pic.qFRF(self.axis_id):
            return 'The given axis is referenced'
        else:
            if self.pic.qRON(self.axis_id):
                self.pic.RON(self.axis_id, 0)
                self.pic.POS(self.axis_id, cur_pos)
                return 'The given axis is referenced, the current posotion is set on the given value'
            else:
                self.pic.POS(self.axis_id, cur_pos)
                return 'The given axis is referenced, the current position is set on the given value'
            
    def is_Moving(self):
        return self.pic.is_Moving(self.axis_id)
    
    def qCST(self):
        return self.pic.qCST(self.axis_id)
    
    def qSST(self):
        return self.pic.qSST(self.axis_id)
    
    def STP(self):
        return self.pic.STP()
                       
    def get_control_mode(self):
        return self.pic.qSVO(self.axis_id)
    
    def set_control_mode(self, value):
        self.pic.SVO(self.axis_id, value)
        
    def get_position(self):
        axis_id = self.axis_name()
        return self.pic.qPOS(axis_id)
        
    def get_cl_tar_pos(self):
        if self.get_control_mode():
            return self.pic.qMOV(self.axis_id)
        else:
            raise Exception('Set mode to 1 to use close loop functions')
    
    def set_cl_tar_pos(self, value):
        if self.get_control_mode():
            self.pic.MOV(self.axis_id, value)
        else:
            raise Exception('Set mode to 1 to use close loop functions')
            
    #    def get_ol_tar_pos(self):
#        if self.get_control_mode() == 0:
#            return self.pic.qOMA(self.axis_id)
#        else:
#             raise Exception('Set mode to 0 to use open loop functions')
#    
#    def set_ol_tar_pos(self, value):
#        if self.get_control_mode() == 0:
#            self.pic.OMA(self.axis_id, value)
#        else:
#             raise Exception('Set mode to 0 to use open loop functions')
        
    
        
       
        
    
        
        
    

    
    
        
        