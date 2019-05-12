
import ctypes
import math
import ipaddress
from collections import namedtuple

import qcodes.instrument_drivers.attocube.AMC100lib as AMC


LockStatus = namedtuple('LockStatus', ['locked', 'authorized'])
ActorParametersByName = namedtuple('ActorParametersByName', ['paramName', 'paramValue'])
ActorParameters = namedtuple('ActorParameters', ['actor_name', 'actorname_size', 'actorType', 'fmax', 'amax', 'sensor_dir', 'actor_dir', 'pitchOfGrading', 'sensivity', 'stepsize'])

class MotionController:
    MAXIMAL_NAME_LENGTH = 256

    def __init__(self, ip_address=None):



        self.ip_address = ip_address
        self._handle = None
        self.connect

    def connect(self, ip_address=None):#, deviceAddress = '192.168.1.1', deviceHandle = 0):
        '''

        '''
        if ip_address is None:
            ip_address = self.ip_address

        # check valid IPAddress
        ipaddress.IPv4Address(ip_address)

        handle = ctypes.c_int32()
        AMC.connect(ip_address.encode(), ctypes.byref(handle))

        self._handle = handle

    def close(self):
        '''
        Closes the connection to the device. The device handle becomes invalid.

        Parameters
            None
        Returns
            None
        '''
        if self._handle is not None:
            AMC.close(self._handle)
            self._handle = None

    def getSerialNumber(self):
        MAX_LEN = 256
        buffer = ctypes.create_string_buffer(MAX_LEN)

        AMC.getSerialNumber(self._handle, buffer, len(buffer))

        return buffer.value.decode()

    def getDeviceName(self):
        buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        AMC.getDeviceName(self._handle, buffer, len(buffer))

        return buffer.value.decode()

    def setDeviceName(self, new_name: str):
        new_name = new_name.encode()

        if len(new_name) >= self.MAXIMAL_NAME_LENGTH:
            raise RuntimeError('Name is too long:', new_name)

        AMC.setDeviceName(self._handle, new_name)

    def getControlOutput(self, axis: int) -> bool:
        enable = ctypes.c_int32()
        AMC.controlOutput(self._handle, axis, ctypes.byref(enable), 0)
        return bool(enable.value)

    def setControlOutput(self, axis: int, enable: bool):
        enable = ctypes.c_int32(enable)
        AMC.controlOutput(self._handle, axis, ctypes.byref(enable), 1)

    def getLockStatus(self):
        locked = ctypes.c_int32()
        authorized = ctypes.c_int32()

        AMC.getLockStatus(self._handle, ctypes.byref(locked), ctypes.byref(authorized))

        return LockStatus(bool(locked.value),bool(authorized.value))

    def __del__(self):
        self.close()

#%%

    def Lock(self, pass_wd: str):
        pass_wd = pass_wd.encode()

        if len(pass_wd) >= self.MAXIMAL_NAME_LENGTH:
            raise RuntimeError('Password is too long:', pass_wd)

        AMC.lock(self._handle, pass_wd)

    def GrantAccess(self, pass_wd: str):
        pass_wd = pass_wd. encode()

        AMC.grantAccess(self._handle, pass_wd)

        return print('The device can be accessed now.')

    def ErrorNumberToString(self, lang, errcode):
        '''
        Meaning not clear...
        '''

        error_buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)


        AMC.errorNumberToString(self._handle, lang, errcode, error_buffer)

        return error_buffer.value.decode()

    def Unlock(self):

        AMC.unlock(self._handle)

        return print('The device is unlocked now (it will not be necessary to execute the grantAccess function to run any VI).')
#%%
    def getControlAmplitude(self, axis: int):
        '''
        unit: mV

        '''

        amplitude = ctypes.c_int32()

        AMC.controlAmplitude(self._handle, axis, ctypes.byref(amplitude), 0)

        return int(amplitude.value)

    def setControlAmplitude(self, axis: int, amplitude: int):
        '''
        unit: mV

        '''

        amplitude = ctypes.c_int32(amplitude)

        AMC.controlAmplitude(self._handle, axis, ctypes.byref(amplitude), 1)

    def getControlFrequency(self, axis: int):
        '''
        unit: mHz

        '''

        frequency = ctypes.c_int32()

        AMC.controlFrequency(self._handle, axis, ctypes.byref(frequency), 0)

        return int(frequency.value)

    def setControlFrequency(self, axis: int, frequency: int):
        '''
        unit: mHz

        '''

        frequency = ctypes.c_int32(frequency)

        AMC.controlFrequency(self._handle, axis, ctypes.byref(frequency), 1)

    def getControlActorSelection(self, axis: int):
        '''
        Meaning not clear ...
        '''
        actor = ctypes.c_int32()

        AMC.controlActorSelection(self._handle, axis, ctypes.byref(actor), 0)

        return int(actor.value)

    def setControlActorSelection(self, axis: int, actor: int):
        '''
        Meaning not clear...
        '''
        actor = ctypes.c_int32(actor)

        AMC.controlActorSelection(self._handle, axis, ctypes.byref(actor), 1)

    def getActorName(self, axis: int):

        actor_buffer = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)

        AMC.getActorName(self._handle, axis, actor_buffer, len(actor_buffer))

        return actor_buffer.value.decode()

    def getActorType(self, axis: int):
        '''
        Actor type:
            AMC_actorLinear = 0
            AMC_actorGonio  = 1
            AMC_actorRot    = 2

        '''

        actor_type = ctypes.c_int32()

        AMC.getActorType(self._handle, axis, ctypes.byref(actor_type))

        return int(actor_type.value)

    def setReset(self, axis: int):

        AMC.setReset(self._handle, axis)

    def getControlMove(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlMove(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlMove(self, axis: int, enable: bool):

        enable = ctypes.c_int32(enable)

        AMC.controlMove(self._handle, axis, ctypes.byref(enable), 1)

    def setNSteps(self, axis: int, n: int, backwards: bool): ##

        '''
        Feature not available with current controller
        '''

        AMC.setNSteps(self._handle, axis, backwards, n)

    def getNSteps(self, axis: int):

        n = ctypes.c_int32()

        AMC.getNSteps(self._handle, axis, ctypes.byref(n))

        return int(n.value)

    def getControlContinousFwd(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlContinousFwd(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlContinousFwd(self, axis: int, enable: bool):
        enable = ctypes.c_int32(enable)

        AMC.controlContinousFwd(self._handle, axis, ctypes.byref(enable), 1)

    def getControlContinousBkwd(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlContinousBkwd(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlContinousBkwd(self, axis: int, enable: bool):
        enable = ctypes.c_int32(enable)

        AMC.controlContinousBkwd(self._handle, axis, ctypes.byref(enable), 1)

    def getControlTargetPosition(self, axis: int):
        '''
        unit: u° or nm, depending on actor type

        '''

        target = ctypes.c_int32()

        AMC.controlTargetPosition(self._handle, axis, ctypes.byref(target), 0)

        return int(target.value)

    def setControlTargetPosition(self, axis: int, target: int):
        '''
        unit: u° or nm, depending on actor type

        '''

        target = ctypes.c_int32(target)

        AMC.controlTargetPosition(self._handle, axis, ctypes.byref(target), 1)

    def getStatusReference(self, axis: int):
        status_reference = ctypes.c_int32()

        AMC.getStatusReference(self._handle, axis, ctypes.byref(status_reference))

        return bool(status_reference.value)

    def getStatusMoving(self, axis: int):
        status_moving = ctypes.c_int32()

        AMC.getStatusMoving(self._handle, axis, ctypes.byref(status_moving))

        return int(status_moving.value)

    def getStatusConnected(self, axis: int):
        status_connected = ctypes.c_int32()

        AMC.getStatusConnected(self._handle, axis, ctypes.byref(status_connected))

        return bool(status_connected.value)

    def getReferencePosition(self, axis: int):
        reference_position = ctypes.c_int32()

        AMC.getReferencePosition(self._handle, axis, ctypes.byref(reference_position))

        return int(reference_position.value)

    def getPosition(self, axis: int):
        '''
        unit: u° or nm, depending on actor type

        '''

        position = ctypes.c_int32()

        AMC.getPosition(self._handle, axis, ctypes.byref(position))

        return int(position.value)

    def getControlReferenceAutoUpdate(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlReferenceAutoUpdate(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlReferenceAutoUpdate(self, axis: int, enable: bool):
        enable = ctypes.c_int32(enable)

        AMC.controlReferenceAutoUpdate(self._handle, axis, ctypes.byref(enable), 1)

    def getControlAutoReset(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlAutoReset(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlAutoReset(self, axis: int, enable: bool):
        enable = ctypes.c_int32(enable)

        AMC.controlAutoReset(self._handle, axis, ctypes.byref(enable), 1)

    def getControlTargetRange(self, axis: int):
        '''
        unit: u° or nm, depending on actor type

        '''

        target_range = ctypes.c_int32()

        AMC.controlTargetRange(self._handle, axis, ctypes.byref(target_range), 0)

        return int(target_range.value)

    def setControlTargetRange(self, axis: int, target_range: int):
        target_range = ctypes.c_int32(target_range)

        AMC.controlTargetRange(self._handle, axis, ctypes.byref(target_range), 1)

    def getStatusTargetRange(self, axis: int):
        statue_target_range = ctypes.c_int32()

        AMC.getStatusTargetRange(self._handle, axis, ctypes.byref(statue_target_range))

        return bool(statue_target_range.value)

    def factoryReset(self):

        AMC.factoryReset(self._handle)

    def getDeviceType(self):
        device_type = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)

        AMC.getDeviceType(self._handle, device_type, len(device_type))

        return device_type.value.decode()

    def getStatusEotFwd(self, axis: int):

        end_of_travel_detected = ctypes.c_int32()

        AMC.getStatusEotFwd(self._handle, axis, ctypes.byref(end_of_travel_detected))

        return bool(end_of_travel_detected.value)

    def getStatusEotBkwd(self, axis: int):
        end_of_travel_detected = ctypes.c_int32()

        AMC.getStatusEotBkwd(self._handle, axis, ctypes.byref(end_of_travel_detected))

        return bool(end_of_travel_detected.value)

    def getControlEotOutputDeactive(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlEotOutputDeactive(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlEotOutputDeactive(self, axis: int, enable: bool):
        '''
        can be changed only from 1 to 0: can only be deactivated (model limitation)

        '''

        enable = ctypes.c_int32(enable)

        AMC.controlEotOutputDeactive(self._handle, axis, ctypes.byref(enable), 1)

    def getControlFixOutputVoltage(self, axis: int):
        '''
        unit: mV

        '''

        voltage = ctypes.c_int32()

        AMC.controlFixOutputVoltage(self._handle, axis, ctypes.byref(voltage), 0)

        return int(voltage.value)

    def setControlFixOutputVoltage(self, axis: int, voltage: int):
        '''
        unit: mV

        '''

        voltage = ctypes.c_int32(voltage)

        AMC.controlFixOutputVoltage(self._handle, axis, ctypes.byref(voltage), 1)

    def getControlAQuadBInResolution(self, axis: int):
        '''
        unit: nm

        '''

        resolution = ctypes.c_int32()

        AMC.controlAQuadBInResolution(self._handle, axis, ctypes.byref(resolution), 0)

        return int(resolution.value)

    def setControlAQuadBInResolution(self, axis: int, resolution: int):
        '''
        unit: nm

        '''

        resolution = ctypes.c_int32(resolution)

        AMC.controlAQuadBInResolution(self._handle, axis, ctypes.byref(resolution), 1)

    def getControlAQuadBOut(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlAQuadBOut(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlAQuadBOut(self, axis: int, enable: bool):
        '''
        Feature not available with current controller
        '''

        enable = ctypes.c_int32(enable)

        AMC.controlAQuadBOut(self._handle, axis, ctypes.byref(enable), 1)

    def getControlAQuadBOutResolution(self, axis: int):
        '''
        unit: nm

        '''

        resolution = ctypes.c_int32()

        AMC.controlAQuadBOutResolution(self._handle, axis, ctypes.byref(resolution), 0)

        return int(resolution.value)

    def setControlAQuadBOutResolution(self, axis: int, resolution: int):
        '''
        Feature not available with current controller

        '''

        resolution = ctypes.c_int32(resolution)

        AMC.controlAQuadBOutResolution(self._handle, axis, ctypes.byref(resolution), 1)

    def getControlAQuadBOutClock(self, axis: int):
        '''
        Clock in multiples of 20 ns. Minimum 2 (40ns), maximum 65535 (1,310700ms)

        '''

        clock = ctypes.c_int32()

        AMC.controlAQuadBOutClock(self._handle, axis, ctypes.byref(clock), 0)

        return int(clock.value)

    def setControlAQuadBOutClock(self, axis: int, clock: int):
        '''
        Feature not available with current controller
        Clock in multiples of 20 ns. Minimum 2 (40ns), maximum 65535 (1,310700ms)

        '''

        clock = ctypes.c_int32(clock)

        AMC.controlAQuadBOutClock(self._handle, axis, ctypes.byref(clock), 1)

    def setActorParametersByName(self, axis: int, actor_name: str):
        '''
        Feature not available with current controller
        '''

        actor_name = actor_name.encode()

        if len(actor_name) >= self.MAXIMAL_NAME_LENGTH:
            raise RuntimeError('Name is too long:', actor_name)

        AMC.setActorParametersByName(self._handle, axis, actor_name)

    def setActorParameters(self, axis: int, actor_name: str, actor_type: int, fmax: int, amax: int, sensor_dir: bool, actor_dir: bool, pitchOfGrading: int, sensivity: int, stepsize: int):
        '''
        Feature not available with current controller
        '''

        actor_name = actor_name.encode()

        AMC.setActorParameters(self._handle, axis, actor_name, actor_type, fmax, amax, sensor_dir, actor_dir, pitchOfGrading, sensivity, stepsize)

    def getActorParametersByParamName(self, axis: int, paramName):
        '''
        Feature not available with current controller
        '''

#        paramName = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
#        paramValue = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
#
#        AMC.getActorParametersByParamName(self._handle, axis, paramName, paramValue, 256)
#        return paramName.value.decode()

#        MAX_LEN = 256
#        buffer = ctypes.create_string_buffer(MAX_LEN)
#        AMC.getSerialNumber(self._handle, buffer, len(buffer))
#        return buffer.value.decode()

#        new_name = new_name.encode()
#
#        if len(new_name) >= self.MAXIMAL_NAME_LENGTH:
#            raise RuntimeError('Name is too long:', new_name)
#
#        AMC.setDeviceName(self._handle, new_name)

        paramName = paramName.encode()

#        paramName = ctypes.create_string_buffer(256)
        paramValue = ctypes.create_string_buffer(256)

        AMC.getActorParametersByParamName(self._handle, axis, paramName, paramValue, len(paramValue))

        #return paramName.value.#ActorParametersByName(paramName.value.decode(), paramValue.value.decode())

    def setActorParametersByParamName(self, axis: int, paramName: str, paramValue: int):
        '''
        Feature not available with current controller
        '''

        paramName = paramName.encode()

        if len(paramName) >= self.MAXIMAL_NAME_LENGTH:
            raise RuntimeError('Name is too long:', paramName)

        AMC.setActorParametersByParamName(self._handle, axis, paramName, paramValue)

    def setActorParametersByParamNameBoolean(self, axis: int, paramName: str, paramValue: bool):
        '''
        Feature not available with current controller
        '''

        paramName = paramName.encode()

        if len(paramName) >= self.MAXIMAL_NAME_LENGTH:
            raise RuntimeError('Name is too long:', paramName)

        AMC.setActorParametersByParamNameBoolean(self._handle, axis, paramName, paramValue)

    def getActorParameters(self, axis: int):
        '''
        Feature not available with current controller
        '''

        actor_name = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)
        actorname_size = ctypes.c_size_t()
        actorType = ctypes.c_int32()
        fmax = ctypes.c_int32()
        amax = ctypes.c_int32()
        sensor_dir = ctypes.c_int32()
        actor_dir = ctypes.c_int32()
        pitchOfGrading = ctypes.c_int32()
        sensivity = ctypes.c_int32()
        stepsize = ctypes.c_int32()

        AMC.getActorParameters(self._handle, axis, actor_name, actorname_size, ctypes.byref(actorType), ctypes.byref(fmax), ctypes.byref(amax), ctypes.byref(sensor_dir), ctypes.byref(actor_dir), ctypes.byref(pitchOfGrading), ctypes.byref(sensivity), ctypes.byref(stepsize))

        return ActorParameters(actor_name.value.decode(), int(actorname_size.value), int(actorType.value), int(fmax.value), int(amax.value), bool(sensor_dir.value), bool(actor_dir.value), int(pitchOfGrading.value), int(sensivity.value), int(stepsize.value))

    def getPositionersList(self):
        positioner_list = ctypes.create_string_buffer(self.MAXIMAL_NAME_LENGTH)

        AMC.getPositionersList(self._handle, positioner_list, len(positioner_list))

        return positioner_list.value.decode()

    def getControlRtOutSignalMode(self):
        '''
        0 = AquadB (LVTTL), 1 = AquadB (LVDS)

        '''

        mode = ctypes.c_int32()

        AMC.controlRtOutSignalMode(self._handle, ctypes.byref(mode), 0)

        return int(mode.value)

    def setControlRtOutSignalMode(self, mode: int):
        '''
        0 = AquadB (LVTTL), 1 = AquadB (LVDS)

        '''

        mode = ctypes.c_int32(mode)

        AMC.controlRtOutSignalMode(self._handle, ctypes.byref(mode), 1)

    def getControlRealtimeInputMode(self, axis: int):
        '''
        0 = Aquadb (LVTTL),    1 = AquadB (LVDS), 8 = Stepper (LVTTL),   9 = Stepper(LVDS), 10 = Trigger (LVTTL), 11 = Trigger (LVDS), 15 = disable

        '''

        mode = ctypes.c_int32()

        AMC.controlRealtimeInputMode(self._handle, axis, ctypes.byref(mode), 0)

        return int(mode.value)

    def setControlRealtimeInputMode(self, axis: int, mode: int):
        '''
        Feature not available with current controller

        0 = = Aquadb (LVTTL),   1 = AquadB (LVDS), 8 = Stepper (LVTTL),   9 = Stepper(LVDS), 10 = Trigger (LVTTL), 11 = Trigger (LVDS), 15 = disable

        '''

        mode = ctypes.c_int32(mode)

        AMC.controlRealtimeInputMode(self._handle, axis, ctypes.byref(mode), 1)

    def getControlRealtimeInputLoopMode(self, axis: int):
        '''
        Realtime Input mode 0 = open-loop, 1 = closed-loop

        '''

        mode = ctypes.c_int32()

        AMC.controlRealtimeInputLoopMode(self._handle, axis, ctypes.byref(mode), 0)

        return int(mode.value)

    def setControlRealtimeInputLoopMode(self, axis: int, mode: int):
        '''

        Feature not available with current controller
        Realtime Input mode 0 = open-loop, 1 = closed-loop

        '''

        mode = ctypes.c_int32(mode)

        AMC.controlRealtimeInputLoopMode(self._handle, axis, ctypes.byref(mode), 1)

    def getControlRealtimeInputChangePerPulse(self, axis: int):
        '''
        get realtime input change per pulse in closed loop mode: in nm

        '''

        change_per_pulse = ctypes.c_int32()

        AMC.controlRealtimeInputChangePerPulse(self._handle, axis, ctypes.byref(change_per_pulse), 0)

        return int(change_per_pulse.value)

    def setControlRealtimeInputChangePerPulse(self, axis: int, change_per_pulse: int):
        '''
        Feature not available with current controller
        set realtime input change per pulse in closed loop mode: in nm

        '''

        change_per_pulse = ctypes.c_int32(change_per_pulse)

        AMC.controlRealtimeInputChangePerPulse(self._handle, axis, ctypes.byref(change_per_pulse), 1)

    def getControlRealtimeInputStepsPerPulse(self, axis: int):
        '''
        get realtime input steps per pulse in open loop mode

        '''

        step_per_pulse = ctypes.c_int32()

        AMC.controlRealtimeInputStepsPerPulse(self._handle, axis, ctypes.byref(step_per_pulse), 0)

        return int(step_per_pulse.value)

    def setControlRealtimeInputStepsPerPulse(self, axis: int, step_per_pulse: int):
        '''
        Feature not available with current controller
        set realtime input steps per pulse in open loop mode

        '''

        step_per_pulse = ctypes.c_int32(step_per_pulse)

        AMC.controlRealtimeInputStepsPerPulse(self._handle, axis, ctypes.byref(step_per_pulse), 1)

    def getControlRealtimeInputMove(self, axis: int):
        enable = ctypes.c_int32()

        AMC.controlRealtimeInputMove(self._handle, axis, ctypes.byref(enable), 0)

        return bool(enable.value)

    def setControlRealtimeInputMove(self, axis: int, enable: bool):
        '''
        Should be used during the actor moving
        '''

        enable = ctypes.c_int32(enable)

        AMC.controlRealtimeInputMove(self._handle, axis, ctypes.byref(enable), 1)
















