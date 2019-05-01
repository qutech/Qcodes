# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 19:13:36 2019

@author: PLlab
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Numbers
from pyPIE871 import PIController

'''
NOTES: FOR SOME REASONS, THE OPEN LOOP MODE DOES NOT WORK -> THE RESPECTIVE FUNCTIONS HAVE BEEN DISABLED

Workflow:
    
    Note: following QCoDes codes are based on single connected stage. For multiple stages case, arguement such as pbValueArray, pdValueArray
    should be generalized to the matched dimension array form.
    
# connect to the controller and initialize the stage
    
    from PIE871QCoDes import PIE871
    pic=PIE871('PI')
    
    pic.status()
    axis_id = pic.axis_name() # important 
    
    pic.axis_range(axis_id)
    pic.ref(axis_id, 0) # important
    
# closed-loop mode motion
    
    pic.mode()
    pic.mode(1) # set the closed-loop mode
    pic.pos()   # get the current position
    pic.cl_tar_pos()  # get the target position for closed-loop mode motiion
    pic.cl_tar_pos(0.1)  # set the target position for the closed-loop mode as 0.1mm and start to move
    pic.pos()   # read the current position 
    pic.cl_tar_pos(0.2)  # set the target position for the closed-loop mode as 0.2mm and start to move
    pic.pos()   # read the current position 
    
    pic.mode(0)  # change the mode to the open-loop
    
'''

class PIE871(Instrument):
    def __init__(self, name, **kwargs):
              
        super().__init__( name, **kwargs)

        self.pic = PIController(PIController.list_usb_devices()[0].split()[-1])
        
        """ useful parameters """     
        self.add_parameter('mode',
                           get_cmd = self.get_control_mode,
                           set_cmd = self.set_control_mode,
                           get_parser = int,
                           docstring = '1 for the closed-loop mode, 0 for the open-loop mode')
        
        """self.add_parameter('pos',
                           get_cmd = self.get_position,
                           set_cmd = self.set_position,
                           get_parser = float,
                           label = 'Current positions of szAxis',
                           unit = 'mm',
                           docstring = ' Note that the current positiion has been set initially on 0mm ')"""
        
        """self.add_parameter('ol_tar_pos',
                           get_cmd = self.get_ol_tar_pos,
                           set_cmd = self.set_ol_tar_pos,
                           get_parser = float,
                           label = 'Target positions of szAxis for open-loop mode',
                           unit = 'mm')"""
        
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
            id = self.pic.IDN()
            return 'The stage is connected by the controller with the id: ' +id
        else:
            return "ERROR: The stage cannot been connected!"
        
    def axis_name(self):
        return self.pic.qSAI_All()
    
    def axis_range(self, axis_id):
        rValue = []
        rValue.append(self.pic.qTMN(axis_id))
        rValue.append(self.pic.qTMX(axis_id))
        return rValue
    
    def ref(self, axis_id, cur_pos):
        if self.pic.qFRF(axis_id):
            return 'The given axis is referenced'
        else:
            if self.pic.qRON(axis_id):
                self.pic.RON(axis_id, 0)
                self.pic.POS(axis_id, cur_pos)
                return 'The given axis is referenced, the current posotion is set on the given value'
            else:
                self.pic.POS(axis_id, cur_pos)
                return 'The given axis is referenced, the current posotion is set on the given value'
            
    def is_Moving(self, axis_id):
        return self.pic.is_Moving(axis_id)
    
    def qCST(self, axis_id):
        return self.pic.qCST(axis_id)
    
    def qSST(self, axis_id):
        return self.pic.qSST(axis_id)
    
    def STP(self):
        return self.pic.STP()
        
#    def qRON(self):
#        axis_id = self.axis_name()
#        return self.pic.qRON(axis_id)
#    
#    def RON(self, value):
#        axis_id = self.axis_name()        
#        self.pic.RON(axis_id, value)
#        
        
    def get_control_mode(self):
        axis_id = self.axis_name()
        return self.pic.qSVO(axis_id)
    
    def set_control_mode(self, value):
        axis_id = self.axis_name()
        self.pic.SVO(axis_id, value)
        
    """def get_position(self):
        axis_id = self.axis_name()
        return self.pic.qPOS(axis_id)
    
    def set_position(self, value):
        axis_id = self.axis_name()
        self.pic.POS(axis_id, value)
        
    def get_ol_tar_pos(self):
        axis_id = self.axis_name()
        return self.pic.qOMA(axis_id)
    
    def set_ol_tar_pos(self, value):
        axis_id = self.axis_name()
        self.pic.OMA(axis_id, value)"""
        
    def get_cl_tar_pos(self):
        axis_id = self.axis_name()
        return self.pic.qMOV(axis_id)
    
    def set_cl_tar_pos(self, value):
        axis_id = self.axis_name()
        self.pic.MOV(axis_id, value)
        
    
        
       
        
    
        
        
    

    
    
        
        