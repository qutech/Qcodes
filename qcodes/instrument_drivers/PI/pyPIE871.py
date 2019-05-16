from typing import Union

import ctypes
import PIE871lib as PIE

class PIController:
    MAXIMAL_NAME_LENGTH = 4096
    
    @classmethod
    def list_usb_devices(cls) -> list:
        out_buffer = ctypes.create_string_buffer(cls.MAXIMAL_NAME_LENGTH)
        n_devices = PIE.PI_EnumerateUSB(out_buffer, cls.MAXIMAL_NAME_LENGTH, None)
        return out_buffer.value.splitlines()
    
    def __init__(self, device_name: Union[str, bytes, None]):
        self.device_name = None
        self.device = None
        
        if device_name:
            self.connect(device_name)
        print(self.device)
            
    def connect(self, device_name: Union[str, bytes]):
        device_name = device_name.encode() if isinstance(device_name, str) else device_name
        
        buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        buffer.value = device_name
        self.device = PIE.PI_ConnectUSB(buffer)
        self.device_name = device_name
#        print(buffer.value.decode())
        return self.device

    def is_Connected(self) -> bool:
        status = PIE.PI_IsConnected(self.device)
        return bool(status)
    
    def disconnect(self):
        PIE.PI_CloseConnection(self.device)
        print('PIE871 connection closed')
    
    def IDN(self):
        '''
        Get identification string of the controller
        '''
        buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        status = PIE.PI_qIDN(self.device, buffer, len(buffer))      
        if status:
            return buffer.value.decode()
        else:
            return "ERROR: cannot get the identification string of the controller"
        
    def qFRF(self, szAxes: str):
        '''
        Indicates whether the given axis is referenced or not.
        An axis is considered as "referenced" when the current position value is set to a known position. 
        Depending on the controller, this is the case if a reference move was successfully executed with PI_FRF(), PI_FNL() or PI_FPL(),
        or if the position was set manually with PI_POS().
        
        pbValueArray array to receive, 1 if successful, 0 if axis is not referenced (e.g. referencing move failed or has not finished yet)
        szAxes string with axes, if "" or NULL all axes are affected
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1
        pbValueArray = array_type() 
        status = PIE.PI_qFRF(self.device, szAxes, pbValueArray)
        if status:
            return pbValueArray[0]
        else:
            return "ERROR: cannot execute the qFRF function"
        
    
    def FRF(self, szAxes: str) -> bool:
        '''
        Starts a reference move: Synchronous reference move of all axes szAxes,
        i.e. the given axis is moved to its physical reference point and the current position is set to the reference position.
        Note: Call PI_IsControllerReady() to find out if referencing is complete
        (the controller will be "busy" while referencing, so most other commands will cause a PI_CONTROLLER_BUSY error) 
        and PI_qFRF() to check whether the reference move was successful.
        
        return: TRUE if successful, FALSE otherwise
        '''
        szAxes = szAxes.encode()
        status = PIE.PI_FRF(self.device, szAxes)
        return bool(status)
    
    def is_Moving(self, szAxes: str) -> bool:
        '''
        Check if szAxes are moving. 
        If an axis is moving the corresponding element of the array will be TRUE, otherwise FALSE. 
        If no axes were specified, only one boolean value is returned and pbValarray[0] will contain a generalized state: TRUE if at least one axis is moving, FALSE if no axis is moving.
        
        szAxes string with axes, if "" or NULL all axes are affected.
        return: TRUE if successful, FALSE otherwise
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1
        pbValueArray = array_type() 
        status = PIE.PI_IsMoving(self.device, szAxes, pbValueArray)
        if status:
            return pbValueArray[0]
        else:
            return "ERROR: cannot execute the is_Moving function"
        
    def qMOV(self, szAxes: str):
        '''
        Read the commanded target positions for szAxes. Use PI_qPOS() to get the current positions

        Arguments:
        szAxes: string with axes, if "" or NULL all axes are queried.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type() 
        status = PIE.PI_qMOV(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]
        else:
            return "ERROR: cannot execute the qMOV function"
        
    def MOV(self, szAxes: str, pdValueArray):
        """
        Move szAxes to specified absolute positions. 
        Axes will start moving to the new positions if ALL given targets are within the allowed ranges and ALL axes can move. 
        All axes start moving simultaneously. 
        
        Servo must be enabled for all commanded axes prior to using this command !!!
        return TRUE if no error, FALSE otherwise
        """
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type(pdValueArray)
        PIE.PI_MOV(self.device, szAxes, pdValueArray)
        status = PIE.PI_MOV(self.device, szAxes, pdValueArray)
        return bool(status)

    def qCST(self, szAxes: str):
        '''
        Get the type names of the stages associated with szAxes. 
        The individual names are preceded by the one-character axis identifier followed by ”=” the stage name and a “\n” (line-feed). 
        The line-feed is preceded by a space on every line except the last.
        
        Arguments:
        szAxes :identifiers of the axes, if "" or NULL all axes are queried
        '''
        szAxes = szAxes.encode()
        buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        status = PIE.PI_qCST(self.device, szAxes, buffer, len(buffer))
        if status:
            return buffer.value.decode()
        else:
            return "ERROR: cannot execute the qCST function"
    
    def qPOS(self, szAxes:str):
        '''
        Get the current positions of szAxes. 
        If no position sensor is present in your system, the response to PI_qPOS() is not meaningful.
        To request the current position of input signal channels (sensors) in physical units, use PI_qTSP() instead.
        
        Arguments:
        szAxes :identifiers of the axes, if "" or NULL all axes are queried
        
        Unit:mm
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type() 
        status = PIE.PI_qPOS(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]#pdValue
        else:
            return "ERROR: cannot read the position"
    
    def qSAI_All(self):
        """
        Get the identifiers for all axes (configured and unconfigured axes). 
        Each character in the returned string is an axis identifier for one logical axis. 
        This function is provided for compatibility with controllers which allow for axis deactivation. 
        PI_qSAI_ALL() then ensures that the answer also includes the axes which are "deactivated".
        """
        buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        status = PIE.PI_qSAI_ALL(self.device, buffer, len(buffer))
        if status:
            return buffer.value.decode()
        else:
            return "ERROR: cannot execute the qSAI_All function"
        
    def SAI(self, szOldAxes: str, szNewAxes: str):
        '''
        Rename axes: szOldAxes will be set to szNewAxes. 
        The characters in szNewAxes must not be in use for any other existing axes and must each be one of the valid identifiers. 
        All characters in szNewAxes will be converted to uppercase letters. Only the last occurence of an axis identifier in szNewAxes will be used to change the name.
        '''
        szOldAxes = szOldAxes.encode()
        szNewAxes = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        status = PIE.PI_SAI(self.device, szOldAxes, szNewAxes)
        return bool(status)
    
    def qTMN(self, szAxes: str):
        '''
        Get the low end of the travel range of szAxes
        
        Arguments:
        szAxes: string with axes, if "" or NULL all axes are queried.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type() 
        status = PIE.PI_qTMN(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]
        else:
            return "ERROR: cannot execute the qTMN function"
        
    def qTMX(self, szAxes: str):
        '''
        Get the high end of the travel range of szAxes
        
        Arguments:
        szAxes: string with axes, if "" or NULL all axes are queried.
        
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type() 
        status = PIE.PI_qTMX(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]
        else:
            return "ERROR: cannot execute the qTMN function"
        
    def qSVO(self, szAxes: str):
        '''
        Get the servo-control mode for szAxes
        
        Arguments:
        szAxes: string with axes, if "" or NULL all axes are queried
        pbValueArray: array to receive the servo modes of the specified axes, TRUE for "on", FALSE for "off"
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1
        pbValueArray = array_type() 
        status = PIE.PI_qSVO(self.device, szAxes, pbValueArray)
        if status:
            return pbValueArray[0]
        else:
            return "ERROR: cannot execute the qSVO function"
        
        
    def SVO(self, szAxes: str, pbValueArray):
        '''
        Set servo-control "on" or "off" (closed-loop/open-loop mode).
        
        Arguments:
        pbValueArray:    
        TRUE  for servo-control on: closed-loop mode;
        FALSE for servo-control off: open-loop mode
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1        
        pbValueArray = array_type(pbValueArray)
        PIE.PI_SVO(self.device, szAxes, pbValueArray)
        status = PIE.PI_SVO(self.device, szAxes, pbValueArray)
        return bool(status)
    
    def qSST(self, szAxes: str):
        '''
        Gets the distance ("step size") for motions of the given axis that are triggered by a manual control unit.
        Arguments:
        szAxes axes of the controller, if "" or NULL all axes are queried.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type() 
        status = PIE.PI_qSST(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]
        else:
            return "ERROR: cannot execute the qSST function"
        
    def SST(self, szAxes: str, pdValueArray):
        '''
        Sets the distance ("step size") for motions of the given axis that are triggered by a manual control unit.
        
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type(pdValueArray)
        status = PIE.PI_qSST(self.device, szAxes, pdValueArray)
        return bool(status)
    
    def qRON(self, szAxes: str):
        '''
        Gets reference mode for given axes.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1        
        pbValueArray = array_type() 
        status = PIE.PI_qRON(self.device, szAxes, pbValueArray)
        if status:
            return pbValueArray[0]
        else:
            return "ERROR: cannot execute the qRON function"
        
    def RON(self, szAxes: str, pbValueArray):
        '''
        Sets referencing mode for given axes. Determines how to reference axes measured by incremental sensors.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_bool*1        
        pbValueArray = array_type(pbValueArray)
        PIE.PI_RON(self.device, szAxes, pbValueArray)
        status = PIE.PI_RON(self.device, szAxes, pbValueArray)
        return bool(status)
    
    def POS(self, szAxes: str, pdValueArray):
        '''
        Set current position for given axis (does not cause motion).
        An axis is considered as "referenced" when the position was set with PI_POS(), so that PI_qFRF() replies "1". 
        Setting the current position with PI_POS() is only possible when the referencing mode is set to "0", see PI_RON().
        
        CAUTION:
            The "software-based" travel range limits (PI_qTMN() and PI_qTMX()) and the "software-based" home position (PI_qDHF()) are not adapted when a position value is set with PI_POS(). This may result in
            • target positions which are inside the range limits but can not be reached by the hardware—the mechanics is at the hardstop but tries to move further and must be stopped with PI_STP()
            • target positions which can be reached by the hardware but are outside of the range limits—e.g. the mechanics is at the negative hardstop and physically could move to the positive hardstop, but due to the software based-travel range limits the target position is not accepted and no motion is possible
            • a home position which is outside of the travel range.
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type(pdValueArray)
        status = PIE.PI_POS(self.device, szAxes, pdValueArray)
        return bool(status)
    
    def STP(self):
        '''
        Stops the motion of all axes instantaneously. Sets error code to 10.
        PI_STP() also stops macros.
        After the axes are stopped, their target positions are set to their current positions.
        '''
        status = PIE.STP(self.device)
        return bool(status)
    
    def OMA(self, szAxes: str, pdValueArray):
        '''
        Commands szAxes to the given absolute position. Motion is realized in open-loop nanostepping mode.
        Servo must be disabled for the commanded axis prior to using this function (open-loop operation).
        With PI_OMA() there is no position control (i.e. the target position is not maintained by any control loop).
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type(pdValueArray)
        status = PIE.PI_OMA(self.device, szAxes, pdValueArray)
        return bool(status)
    
    def qOMA(self, szAxes: str):
        '''
        Reads last commanded open-loop target pdValueArray of given szAxes
        '''
        szAxes = szAxes.encode()
        array_type = ctypes.c_double*1
        pdValueArray = array_type()
        status = PIE.PI_qOMA(self.device, szAxes, pdValueArray)
        if status:
            return pdValueArray[0]
        else:
            return "ERROR: cannot execute the qOMA function"
        
        

