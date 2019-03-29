import ctypes
import os

#
# List of error types
#

NCB_Ok = 0              #/**< No error                              */
NCB_Error = -1             #/**< Unspecified error                     */
NCB_NotConnected = -2             # /**< No active connection to device        */
NCB_DriverError = -3              #/**< Error in comunication with driver     */
NCB_NetworkError = -4              #/**< Network error when connecting to AMC  */
BAD_IP_ADDRESS = -5
CONNECTION_TIMEOUT = -6
NO_DEVICE_FOUND_ERR = -7
NCB_InvalidParam = -9              #/**< Parameter out of range                */
NCB_FeatureNotAvailable = 10              #/**< Feature only available in pro version */

#checks the errors returned from the dll
def checkError(code,func,args):
    if code == NCB_Ok:
        return
    elif code == NCB_Error:             
        raise Exception("Error: unspecific in"+str(func.__name__)+"with parameters:"+str(args))
    elif code == CONNECTION_TIMEOUT:           
        raise Exception("Error: connection timeout")
    elif code == NCB_NotConnected:      
        raise Exception("Error: not connected") 
    elif code == NCB_DriverError:       
        raise Exception("Error: driver error") 
    elif code == NCB_NetworkError:      
        raise Exception("Error: network error")
    elif code == BAD_IP_ADDRESS:
        raise Exception("Error: invalid IP address")
    elif code == NO_DEVICE_FOUND_ERR:
        raise Exception("Error: no device found")
    elif code == NCB_InvalidParam:
        raise Exception("Error: invalid parameter")
    elif code == NCB_FeatureNotAvailable:
        raise Exception("Error: feature not available")
    else:                    
        raise Exception("Error: unknown in"+str(func.__name__)+"with parameters:"+str(args))
    return code
	
# import dll - have to change directories so it finds libusb0.dll
directory_of_this_module_and_dlls = os.path.dirname(os.path.realpath(__file__))
current_directory = os.getcwd()
os.chdir(directory_of_this_module_and_dlls)
amc_100 = ctypes.windll.LoadLibrary(directory_of_this_module_and_dlls+'\\amc.dll')

os.chdir(current_directory)

#aliases for the strangely-named functions from the dll
connect = getattr(amc_100,"AMC_Connect")
connect.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int32)]

close = getattr(amc_100,"AMC_Close")
close.argtypes = [ctypes.c_int32]

getLockStatus = getattr(amc_100,"AMC_getLockStatus")
getLockStatus.argtypes =  [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]

lock = getattr(amc_100,"AMC_lock")
lock.argtypes = [ctypes.c_int32, ctypes.c_char_p]

grantAccess = getattr(amc_100,"AMC_grantAccess")
grantAccess.argtypes = [ctypes.c_int32, ctypes.c_char_p]

errorNumberToString = getattr(amc_100,"AMC_errorNumberToString")
errorNumberToString.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]

unlock = getattr(amc_100,"AMC_unlock")
unlock.argtypes = [ctypes.c_int32]

controlOutput = getattr(amc_100,"AMC_controlOutput")
controlOutput.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAmplitude = getattr(amc_100,"AMC_controlAmplitude")
controlAmplitude.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlFrequency = getattr(amc_100,"AMC_controlFrequency")
controlFrequency.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlActorSelection = getattr(amc_100,"AMC_controlActorSelection")
controlActorSelection.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

getActorName = getattr(amc_100,"AMC_getActorName")
getActorName.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getActorType = getattr(amc_100,"AMC_getActorType")
getActorType.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

setReset = getattr(amc_100,"AMC_setReset")
setReset.argtypes = [ctypes.c_int32, ctypes.c_int32]

controlMove = getattr(amc_100,"AMC_controlMove")
controlMove.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

setNSteps = getattr(amc_100,"AMC_setNSteps")
setNSteps.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

getNSteps = getattr(amc_100,"AMC_getNSteps")
getNSteps.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

controlContinousFwd = getattr(amc_100,"AMC_controlContinousFwd")
controlContinousFwd.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlContinousBkwd = getattr(amc_100,"AMC_controlContinousBkwd")
controlContinousBkwd.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlTargetPosition = getattr(amc_100,"AMC_controlTargetPosition")
controlTargetPosition.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

getStatusReference = getattr(amc_100,"AMC_getStatusReference")
getStatusReference.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

getStatusMoving = getattr(amc_100,"AMC_getStatusMoving")
getStatusMoving.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

getStatusConnected = getattr(amc_100,"AMC_getStatusConnected")
getStatusConnected.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

getReferencePosition = getattr(amc_100,"AMC_getReferencePosition")
getReferencePosition.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

getPosition = getattr(amc_100,"AMC_getPosition")
getPosition.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

controlReferenceAutoUpdate = getattr(amc_100,"AMC_controlReferenceAutoUpdate")
controlReferenceAutoUpdate.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAutoReset = getattr(amc_100,"AMC_controlAutoReset")
controlAutoReset.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlTargetRange = getattr(amc_100,"AMC_controlTargetRange")
controlTargetRange.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

getStatusTargetRange = getattr(amc_100,"AMC_getStatusTargetRange")
getStatusTargetRange.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

#getFirmwareVersion = getattr(amc_100,"AMC_getFirmwareVersion")
#getFirmwareVersion.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

#getFpgaVersion = getattr(amc_100,"AMC_getFpgaVersion")
#getFpgaVersion.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

#rebootSystem = getattr(amc_100,"AMC_rebootSystem")
#rebootSystem.argtypes = [ctypes.c_int32]

factoryReset = getattr(amc_100,"AMC_factoryReset")
factoryReset.argtypes = [ctypes.c_int32]

#getMacAddress = getattr(amc_100,"AMC_getMacAddress")
#getMacAddress.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]
#
#getIpAddress = getattr(amc_100,"AMC_getIpAddress")
#getIpAddress.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getDeviceType = getattr(amc_100,"AMC_getDeviceType")
getDeviceType.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getSerialNumber = getattr(amc_100,"AMC_getSerialNumber")
getSerialNumber.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getDeviceName = getattr(amc_100,"AMC_getDeviceName")
getDeviceName.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

setDeviceName = getattr(amc_100,"AMC_setDeviceName")
setDeviceName.argtypes = [ctypes.c_int32, ctypes.c_char_p]

#controlDeviceId = getattr(amc_100,"AMC_controlDeviceId")
getStatusEotFwd = getattr(amc_100,"AMC_getStatusEotFwd")
getStatusEotFwd.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

getStatusEotBkwd = getattr(amc_100,"AMC_getStatusEotBkwd")
getStatusEotBkwd.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]

controlEotOutputDeactive = getattr(amc_100,"AMC_controlEotOutputDeactive")
controlEotOutputDeactive.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlFixOutputVoltage = getattr(amc_100,"AMC_controlFixOutputVoltage")
controlFixOutputVoltage.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAQuadBInResolution = getattr(amc_100,"AMC_controlAQuadBInResolution")
controlAQuadBInResolution.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAQuadBOut = getattr(amc_100,"AMC_controlAQuadBOut")
controlAQuadBOut.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAQuadBOutResolution = getattr(amc_100,"AMC_controlAQuadBOutResolution")
controlAQuadBOutResolution.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlAQuadBOutClock = getattr(amc_100,"AMC_controlAQuadBOutClock")
controlAQuadBOutClock.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

setActorParametersByName = getattr(amc_100,"AMC_setActorParametersByName")
setActorParametersByName.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p]

setActorParameters = getattr(amc_100,"AMC_setActorParameters")
setActorParameters.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,\
                               ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]

setActorParametersByParamNameBoolean = getattr(amc_100,"AMC_setActorParametersByParamNameBoolean")
setActorParametersByParamNameBoolean.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

setActorParametersByParamName = getattr(amc_100,"AMC_setActorParametersByParamName")
setActorParametersByParamName.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getActorParametersByParamName = getattr(amc_100,"AMC_getActorParametersByParamName")
getActorParametersByParamName.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32]

getPositionersList = getattr(amc_100,"AMC_getPositionersList")
getPositionersList.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

getActorParameters = getattr(amc_100,"AMC_getActorParameters")
getActorParameters.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), \
                               ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]

controlRtOutSignalMode = getattr(amc_100,"AMC_controlRtOutSignalMode")
controlRtOutSignalMode.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlRealtimeInputMode = getattr(amc_100,"AMC_controlRealtimeInputMode")
controlRealtimeInputMode.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlRealtimeInputLoopMode = getattr(amc_100,"AMC_controlRealtimeInputLoopMode")
controlRealtimeInputLoopMode.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlRealtimeInputChangePerPulse = getattr(amc_100,"AMC_controlRealtimeInputChangePerPulse")
controlRealtimeInputChangePerPulse.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlRealtimeInputStepsPerPulse = getattr(amc_100,"AMC_controlRealtimeInputStepsPerPulse")
controlRealtimeInputStepsPerPulse.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

controlRealtimeInputMove = getattr(amc_100,"AMC_controlRealtimeInputMove")
controlRealtimeInputMove.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]

#set error checking & handling
connect.errcheck = checkError
close.errcheck = checkError
getLockStatus.errcheck = checkError
lock.errcheck = checkError
grantAccess.errcheck = checkError
errorNumberToString.errcheck = checkError
unlock.errcheck = checkError
controlOutput.errcheck = checkError
controlAmplitude.errcheck = checkError
controlFrequency.errcheck = checkError
controlActorSelection.errcheck = checkError
getActorName.errcheck = checkError
getActorType.errcheck = checkError
setReset.errcheck = checkError
controlMove.errcheck = checkError
setNSteps.errcheck = checkError
getNSteps.errcheck = checkError
controlContinousFwd.errcheck = checkError
controlContinousBkwd.errcheck = checkError
controlTargetPosition.errcheck = checkError
getStatusReference.errcheck = checkError
getStatusMoving.errcheck = checkError
getStatusConnected.errcheck = checkError
getReferencePosition.errcheck = checkError
getPosition.errcheck = checkError
controlReferenceAutoUpdate.errcheck = checkError
controlAutoReset.errcheck = checkError
controlTargetRange.errcheck = checkError
getStatusTargetRange.errcheck = checkError
#getFirmwareVersion.errcheck = checkError
#getFpgaVersion.errcheck = checkError
#rebootSystem.errcheck = checkError
factoryReset.errcheck = checkError
#getMacAddress.errcheck = checkError
#getIpAddress.errcheck = checkError
getDeviceType.errcheck = checkError
getSerialNumber.errcheck = checkError
getDeviceName.errcheck = checkError
setDeviceName.errcheck = checkError
#controlDeviceId.errcheck = checkError
getStatusEotFwd.errcheck = checkError
getStatusEotBkwd.errcheck = checkError
controlEotOutputDeactive.errcheck = checkError
controlFixOutputVoltage.errcheck = checkError
controlAQuadBInResolution.errcheck = checkError
controlAQuadBOut.errcheck = checkError
controlAQuadBOutResolution.errcheck = checkError
controlAQuadBOutClock.errcheck = checkError
setActorParametersByName.errcheck = checkError
setActorParameters.errcheck = checkError
setActorParametersByParamNameBoolean.errcheck = checkError
setActorParametersByParamName.errcheck = checkError
getActorParametersByParamName.errcheck = checkError
getPositionersList.errcheck = checkError
getActorParameters.errcheck = checkError
controlRtOutSignalMode.errcheck = checkError
controlRealtimeInputMode.errcheck = checkError
controlRealtimeInputLoopMode.errcheck = checkError
controlRealtimeInputChangePerPulse.errcheck = checkError
controlRealtimeInputStepsPerPulse.errcheck = checkError
controlRealtimeInputMove.errcheck = checkError



