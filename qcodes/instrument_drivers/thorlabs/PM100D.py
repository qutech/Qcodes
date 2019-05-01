# -*- coding: utf-8 -*-
"""
Created on Wed May  1 17:51:31 2019

@author: Thomas
"""

from qcodes import VisaInstrument

class PM100D(VisaInstrument):
    
    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\n', **kwargs)
        
        self.add_parameter('wav',
                           get_cmd='CORR:WAV?',
                           set_cmd='CORR:WAV {:f}',
                           label='wavelength',
                           unit='nm')
        
        self.add_parameter('pow',
                           get_cmd='READ?',
                           label='power',
                           unit='Watt')