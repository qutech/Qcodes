# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 19:13:36 2019

@author: PLlab
"""

from qcodes import Instrument, Parameter
from qcodes.utils.validators import Numbers
from pyPIE871 import PIController

'''
Workflow:
    
    Note: following QCoDes codes are based on single connected stage. For multiple stages case, arguement such as pbValueArray, pdValueArray
    should be generalized to the matched dimension array form.
    
# connect to the controller and initialize the stage
    
    from PIE871QCoDes import PIE871
    PI=PIE871('PI')
    
    PI.status()
    axes_id = PI.axse_name() # important 
    
    PI.axes_range(axes_id)
    PI.ref(axes_id, 0)
    
# closed-loop mode motion
    
    PI.mode()
    PI.mode(1) # set the closed-loop mode
    PI.pos()   # get the current position
    PI.cl_tar_pos()  # get the target position for closed-loop mode motiion
    PI.cl_tar_pos(0.1)  # set the target position for the closed-loop mode as 0.1mm and start to move
    PI.pos()   # read the current position 
    PI.cl_tar_pos(0.2)  # set the target position for the closed-loop mode as 0.2mm and start to move
    PI.pos()   # read the current position 
    
    PI.mode(0)  # change the mode to the open-loop
    
    
    
'''

#%%
class PIE871(Instrument):
    def __init__(self, name, **kwargs):
              
        super().__init__( name, **kwargs)

        self.pic = PIController(PIController.list_usb_devices()[0].split()[-1])
        
#%% useful parameters       
        self.add_parameter('mode',
                           get_cmd = self.get_control_mode,
                           set_cmd = self.set_control_mode,
                           get_parser = int,
                           docstring = '1 for the closed-loop mode, 0 for the open-loop mode')
        
        self.add_parameter('pos',
                           get_cmd = self.get_position,
                           set_cmd = self.set_position,
                           get_parser = float,
                           label = 'Current positions of szAxes',
                           unit = 'mm',
                           docstring = ' Note that the current positiion has been set initially on 0mm ')
        
        self.add_parameter('ol_tar_pos',
                           get_cmd = self.get_ol_tar_pos,
                           set_cmd = self.set_ol_tar_pos,
                           get_parser = float,
                           label = 'Target positions of szAxes for open-loop mode',
                           unit = 'mm')
        
        self.add_parameter('cl_tar_pos',
                           get_cmd = self.get_cl_tar_pos,
                           set_cmd = self.set_cl_tar_pos,
                           get_parser = float,
                           label = 'Target positions of szAxes for closed-loop mode',
                           unit = 'mm')


#%% 
    def status(self):       
        if self.pic.is_Connected():
            id = self.pic.IDN()
            return 'The stage is connected by the controller with the id: ' +id
        else:
            return "ERROR: The stage cannot been connected!"
        
    def axse_name(self):
        return self.pic.qSAI_All()
    
    
    def axes_range(self, axes_id):
        rValue = []
        rValue.append(self.pic.qTMN(axes_id))
        rValue.append(self.pic.qTMX(axes_id))
        return rValue
    
    def ref(self, axes_id, cur_pos):
        if self.pic.qFRF(axes_id):
            return 'The given axis is referenced'
        else:
            if self.pic.qRON(axes_id):
                self.pic.RON(axes_id, 0)
                self.pic.POS(axes_id, cur_pos)
                return 'The given axis is referenced, the current posotion is set on the given value'
            else:
                self.pic.POS(axes_id, cur_pos)
                return 'The given axis is referenced, the current posotion is set on the given value'
            
    def is_Moving(self, axes_id):
        return self.pic.is_Moving(axes_id)
    
    def qCST(self, axes_id):
        return self.pic.qCST(axes_id)
    
    def qSST(self, axes_id):
        return self.pic.qSST(axes_id)
    
    def STP(self):
        return self.pic.STP()
        
#    def qRON(self):
#        axes_id = self.axse_name()
#        return self.pic.qRON(axes_id)
#    
#    def RON(self, value):
#        axes_id = self.axse_name()        
#        self.pic.RON(axes_id, value)
#        
        
    def get_control_mode(self):
        axes_id = self.axse_name()
        return self.pic.qSVO(axes_id)
    
    def set_control_mode(self, value):
        axes_id = self.axse_name()
        self.pic.SVO(axes_id, value)
        
    def get_position(self):
        axes_id = self.axse_name()
        return self.pic.qPOS(axes_id)
    
    def set_position(self, value):
        axes_id = self.axse_name()
        self.pic.POS(axes_id, value)
        
    def get_ol_tar_pos(self):
        axes_id = self.axse_name()
        return self.pic.qOMA(axes_id)
    
    def set_ol_tar_pos(self, value):
        axes_id = self.axse_name()
        self.pic.OMA(axes_id, value)
        
    def get_cl_tar_pos(self):
        axes_id = self.axse_name()
        return self.pic.qMOV(axes_id)
    
    def set_cl_tar_pos(self, value):
        axes_id = self.axse_name()
        self.pic.MOV(axes_id, value)
        
    
        
       
        
    
        
        
    

    
    
        
        