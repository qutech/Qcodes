
import numpy as np
import matplotlib.pyplot as plt

from qcodes import Instrument, Parameter, ArrayParameter, MultiParameter, validators

try:
    from iDus_python_library.Camera.andor import Andor
except ImportError:
    raise ImportError('This driver requires the pyandor library. You can ' +
                      'find it at https://github.com/hamidohadi/pyandor.')


# %%

class Andor_iDus(Instrument):
    """
    Driver for the Andor iDus 416 CCD
    """
    def __init__(self, name: str, dll_path: str=None, **kwargs):
        # Initialize the parent Instrument instance
        super().__init__(name, **kwargs)

        # Initialize the andor instance using the pyandor module
        self.andor = Andor(dll_path=dll_path)

        self.add_parameter('acquisition_mode',
                           label='Camera Acquisition Mode',
                           unit=None,
                           get_cmd=lambda: self.andor._AcquisitionMode,
                           set_cmd=self.andor.SetAcquisitionMode,
                           get_parser=lambda x: self._generic_parser('_AcquisitionMode'),
                           val_mapping={'Unset': -1,
                                        'Single': 1,
                                        'Accumulate': 2,
                                        'Kinetic': 3,
                                        'Fast Kinetics': 4,
                                        'Run till abort': 5},
                           docstring=("Set the acquisition mode to 'Single'," +
                                      "'Accumulate', 'Kinetic', 'Fast " +
                                      "Kinetics', or 'Run till abort'."))
        self.add_parameter('read_mode',
                           label='Camera Read Mode',
                           unit=None,
                           get_cmd=lambda: self.andor._ReadMode,
                           set_cmd=self.andor.SetReadMode,
                           get_parser=lambda x: self._generic_parser('_ReadMode'),
                           val_mapping={'Unset': -1,
                                        'FVB': 0,
                                        'Multi-Track': 1,
                                        'Random-Track': 2,
                                        'Single-Track': 3,
                                        'Image': 4},
                           docstring=("Set the read mode to 'FVB' (full " +
                                      "vertical binning), 'Multi-Track', " +
                                      "'Random-Track', 'Single-Track', or " +
                                      "'Image'."))

        self.add_parameter('trigger_mode',
                           label='Camera Trigger Mode',
                           unit=None,
                           get_cmd=lambda: self.andor._TriggerMode,
                           set_cmd=self.andor.SetTriggerMode,
                           get_parser=lambda x: self._generic_parser('_TriggerMode'),
                           val_mapping={'Unset': -1,
                                        'Internal': 0,
                                        'External': 1,
                                        'External Start': 6,
                                        'External Exposure (Bulb)': 7,
                                        'External FVB EM (only valid for EM Newton models in FVB mode)': 9,
                                        'Software Trigger': 10,
                                        'External Charge Shifting': 12},
                           docstring=("Set the trigger mode to 'Internal', " +
                                      "'External', 'External Start', " +
                                      "'External Exposure (Bulb)', " +
                                      "'External FVB EM (only valid for EM " +
                                      "Newton models in FVB mode)', " +
                                      "'Software Trigger', or 'External " +
                                      "Charge Shifting'."))
                                      
        self.add_parameter('status',
                           label='Camera Status',
                           unit=None,
                           get_cmd=self.andor.GetStatus)
        
        self.add_parameter('exposure_time',
                           label='Camera Exposure Time',
                           unit='s',
                           get_cmd=lambda: self.andor._exposure,
                           set_cmd=self.andor.SetExposureTime,
                           vals=validators.Numbers())
        
        self.add_parameter('accumulation_cycle_time',
                           label='Camera Accumulation Cycle Time',
                           unit='s',
                           get_cmd=lambda: self.andor._accumulate,
                           set_cmd=self.andor.SetAccumulationCycleTime,
                           vals=validators.Numbers(min_value=0))
        
        self.add_parameter('kinetic_cycle_time',
                           label='Camera Kinetic Cycle Time',
                           unit='s',
                           get_cmd=lambda: self.andor._kinetic,
                           set_cmd=self.andor.SetKineticCycleTime,
                           vals=validators.Numbers(min_value=0))
        
        self.add_parameter('number_accumulations',
                           label='Number of Accumulations',
                           unit=None,
                           get_cmd=lambda: self.andor._accumulations,
                           set_cmd=self.andor.SetNumberAccumulations,
                           vals=validators.Ints(min_value=1))
        
        self.add_parameter('number_kinetics',
                           label='Number of Scans',
                           unit=None,
                           get_cmd=lambda: self.andor._scans,
                           set_cmd=self.andor.SetNumberKinetics,
                           vals=validators.Ints(min_value=1))
        
        self.add_parameter('acquisition_timings',
                           label='"Valid" Acquisition Timings',
                           unit='s')
        
        self.add_parameter('number_preamp_gains',
                           label='Number of Pre-Amplifier Gains',
                           unit=None,
                           get_cmd=self.andor.GetNumberPreAmpGains)
        
        self.add_parameter('preamp_gain',
                           label='Pre-Amplifier Gain',
                           unit=None,
                           get_cmd=self.andor.GetPreAmpGain,
                           set_cmd=self.andor.SetPreAmpGain)
        
        self.add_parameter('n_images',
                           label='Number of New Images',
                           unit=None,
                           get_cmd=self.andor.GetNumberNewImages)
        
        self.add_parameter('h_shift_speed',
                           label='Horizontal Shift Speed',
                           unit=None,
                           get_cmd=self.andor.GetHSSpeed,
                           set_cmd=self.andor.SetHSSpeed)
                           
        
        self.connect_message()

    def _generic_parser(self, attr: str):
        """
        A generic get parser for the various mode settings to accomodate the
        parameter not being set yet.
        """
        val = getattr(self.andor, attr)
        if val is None:
            return -1
        else:
            return int(val)

    def get_idn(self):
        """
        Gets the most relevant information about this instrument.
        
        Returns a dictionary containing
            - 'vendor': instrument vendor
            - 'model': model number
            - 'serial': serial number
            - 'firmware': tuple of firmware version and firmware build
        """
        firmware_version, firmware_build = self.andor.GetHardwareVersion()
        serial = self.andor.GetCameraSerialNumber()
        
        return {'vendor': 'Andor', 'model': 'iDus 416',
                'serial': serial,
                'firmware': (firmware_version, firmware_build)}
        
    def abort_acquisition(self):
        """
        Description     This function aborts the current acquisition if one is
                        active. 
        Parameters      NONE 
        Return          unsigned int    
                        DRV_SUCCESS         Acquisition aborted.  
                        DRV_NOT_INITIALIZED System not initialized. 
                        DRV_IDLE            The system is not currently
                                            acquiring. 
                        DRV_VXDNOTINSTALLED VxD not loaded. 
                        DRV_ERROR_ACK       Unable to communicate with card. 
        
        See also        GetStatus StartAcquisition 
        """
        return self.andor.AbortAcquisition()

    def start_acquisition(self):
        """
        Description This function starts an acquisition. The status of the
                    acquisition can be monitored via GetStatus(). 
        Parameters  NONE 
        Return      unsigned int    
                    DRV_SUCCESS         Acquisition started. 
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_ACQUIRING       Acquisition in progress. 
                    DRV_VXDNOTINSTALLED VxD not loaded. 
                    DRV_ERROR_ACK       Unable to communicate with card. 
                    DRV_INIERROR        Error reading “DETECTOR.INI”. 
                    DRV_ACQERROR        Acquisition settings invalid. 
                    DRV_ERROR_PAGELOCK  Unable to allocate memory.  
                    DRV_INVALID_FILTER  Filter not available for current
                                        acquisition. 
                    DRV_BINNING_ERROR   Range not multiple of horizontal
                                        binning. 
                    DRV_SPOOLSETUPERROR Error with spool settings. 
        
        See also    GetStatus, GetAcquisitionTimings, SetAccumulationCycleTime,
                    SetAcquisitionMode, 
                    SetExposureTime, SetHSSpeed, SetKineticCycleTime,
                    SetMultiTrack, SetNumberAccumulations, SetNumberKinetics,
                    SetReadMode, SetSingleTrack, SetTriggerMode, SetVSSpeed  
        """
        return self.andor.StartAcquisition()

    def wait_for_acquisition(self):
        """
        Description WaitForAcquisition can be called after an acquisition is
                    started using  StartAcquisition to put the calling thread
                    to sleep until an Acquisition Event occurs. This can be
                    used as a simple alternative to the functionality provided
                    by the SetDriverEvent function, as all Event creation and
                    handling is performed internally by the SDK library.  
                    Like the SetDriverEvent functionality it will use less
                    processor resources than continuously polling with the
                    GetStatus function. If you wish to restart the calling
                    thread without waiting for an Acquisition event, call the
                    function CancelWait. An Acquisition Event occurs each time
                    a new image is acquired during an Accumulation, Kinetic
                    Series or Run-Till-Abort acquisition or at the end of a
                    Single Scan Acquisition. If a second event occurs before
                    the first one has been acknowledged, the first one will be 
                    ignored. Care should be taken in this case, as you may have
                    to use CancelWait to exit the function. 
        Parameters  NONE 
        Return      unsigned int    
                    DRV_SUCCESS         Acquisition Event occurred  
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_NO_NEW_DATA     Non-Acquisition Event occurred.(e.g.
                                        CancelWait() called) 
        
        See also    StartAcquisition, CancelWait  
        """
        self.andor.WaitForAcquisition()

    def acquire(self):
        """
        A wrapper to start the acquisition of data and wait for it to finish.
        """
        self.start_acquisition()
        self.wait_for_acquisition()

    def get_acquisition_timings(self):
        """
        Description This function will return the current “valid” acquisition
                    timing information. This function should be used after all
                    the acquisitions settings have been set, e.g.
                    SetExposureTime, SetKineticCycleTime and SetReadMode etc.
                    The values returned are the actual times used in subsequent
                    acquisitions.  
                    This function is required as it is possible to set the
                    exposure time to 20ms, accumulate cycle time to 30ms and
                    then set the readout mode to full image. As it can take
                    250ms to read out an image it is not possible to have a
                    cycle time of 30ms. 
        Parameters  float* exposure: valid exposure time in seconds 
                    float* accumulate: valid accumulate cycle time in seconds 
                    float* kinetic: valid kinetic cycle time in seconds 
        Return      unsigned int   
                    DRV_SUCCESS         Timing information returned. 
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_ACQUIRING       Acquisition in progress. 
                    DRV_INVALID_MODE    Acquisition or readout mode is not
                                        available. 
        
        See also    SetAccumulationCycleTime, SetAcquisitionMode,
                    SetExposureTime, SetHSSpeed, SetKineticCycleTime,
                    SetMultiTrack, SetNumberAccumulations, SetNumberKinetics, 
                    SetReadMode, SetSingleTrack, SetTriggerMode, SetVSSpeed  
        """
        return self.andor.GetAcquisitionTimings()
        
    def get_status(self):
        """
        Description  This function will return the current status of the Andor
        SDK system. This function should be called before an acquisition is
        started to ensure that it is IDLE and during an acquisition to monitor
        the process. 

        Parameters  int* status: current status  
                    DRV_IDLE                    IDLE waiting on instructions. 
                    DRV_TEMPCYCLE               Executing temperature cycle. 
                    DRV_ACQUIRING               Acquisition in progress. 
                    DRV_ACCUM_TIME_NOT_MET      Unable to meet Accumulate cycle
                                                time. 
                    DRV_KINETIC_TIME_NOT_MET    Unable to meet Kinetic cycle
                                                time. 
                    DRV_ERROR_ACK               Unable to communicate with
                                                card. 
                    DRV_ACQ_BUFFER              Computer unable to read the
                                                data via the ISA slot at the
                                                required rate.  
                    DRV_ACQ_DOWNFIFO_FULL       Computer unable to read data
                                                fast enough to stop camera
                                                memory going full. 
                    DRV_SPOOLERROR              Overflow of the spool buffer. 
         
        Return      unsigned int    
                    DRV_SUCCESS                 Status returned 
                    DRV_NOT_INITIALIZED         System not initialized 
        
        See also    SetTemperature, StartAcquisition 
        NOTE: If the status is one of the following: 
            -  DRV_ACCUM_TIME_NOT_MET 
            -  DRV_KINETIC_TIME_NOT_MET  
            -  DRV_ERROR_ACK   
            -  DRV_ACQ_BUFFER 
            -  DRV_ACQ_DOWNFIFO_FULL 
        then the current acquisition will be aborted automatically. 
        """
        return self.andor.GetStatus()
    
    def get_single_track_settings(self):
        """
        Get current single track settings.
        
        Return      (centre, height)
        See also    set_single_track
        """
        centre = self.andor._st_centre
        height = self.andor._st_height
        return (centre, height)
    
    def set_single_track(self, centre: int, height: int):
        """
        Description This function will set the single track parameters. The
                    parameters are validated in the following order: centre row
                    and then track height. 
        Parameters  int centre: centre row of track 
                        Valid range 1 to number of vertical pixels. 
                    int height: height of track 
                        Valid range > 1 (maximum value depends on centre row
                        and number of vertical pixels). 
        Return      unsigned int    
                    DRV_SUCCESS         Parameters set. 
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_ACQUIRING       Acquisition in progress.  
                    DRV_P1INVALID       Center row invalid. 
                    DRV_P2INVALID       Track height invalid. 
        
        See also    SetReadMode 
        """
        return self.andor.SetSingleTrack(centre, height)
    
    def get_multi_track_settings(self):
        """
        Get current multi track settings.
        
        Return      (centre, height, offset, gap, bottom)
        See also    set_multi_track
        """
        number = self.andor._mt_number
        height = self.andor._mt_height
        offset = self.andor._mt_offset
        gap = self.andor._mt_gap
        bottom = self.andor._mt_bottom
        return (number, height, offset, gap, bottom)
    
    def set_multi_track(self, number: int, height: int, offset: int):
        """
        Description     This function will set the multi-Track parameters.
                        The tracks are automatically spread evenly over the
                        detector. Validation of the parameters is carried
                        out in the following order:  
                            - Number of tracks,  
                            - Track height 
                            - Offset.  
                        The first pixels row of the first track is returned
                        via ‘bottom’. The number of rows between each track
                        is returned via ‘gap’. 
        Parameters      int number: number tracks 
                            Valid values 1 to number of vertical pixels 
                        int height: height of each track 
                            Valid values >0 (maximum depends on number of
                            tracks) 
                        int offset: vertical displacement of tracks 
                            Valid values depend on number of tracks and
                            track height 
                        int* bottom: first pixels row of the first track 
                        int* gap: number of rows between each track (could
                             be 0) 
        Return          unsigned int    
                        DRV_SUCCESS         Parameters set.  
                        DRV_NOT_INITIALIZED System not initialized. 
                        DRV_ACQUIRING       Acquisition in progress.  
                        DRV_P1INVALID       Number of tracks invalid. 
                        DRV_P2INVALID       Track height invalid. 
                        DRV_P3INVALID       Offset invalid. 

        See also  SetReadMode, StartAcquisition SetRandomTracks 
        """
        return self.andor.SetMultiTrack(number, height, offset)
    
    def get_acquired_data(self, data=[]):
        """
        Description This function will return the data from the last
                    acquisition and append it to *data*. The data are returned
                    as long integers (32-bit signed integers). The “array” must
                    be large enough to hold the complete data set. 
        Parameters  at_32* arr: pointer to data storage allocated by the user. 
                    unsigned long size: total number of pixels. 
        Return      unsigned int   
                    DRV_SUCCESS         Data copied.  
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_ACQUIRING       Acquisition in progress. 
                    DRV_ERROR_ACK       Unable to communicate with card. 
                    DRV_P1INVALID       Invalid pointer (i.e. NULL). 
                    DRV_P2INVALID       Array size is incorrect. 
                    DRV_NO_NEW_DATA     No acquisition has taken place 
        
        See also  GetStatus, StartAcquisition, GetAcquiredData16  
        """
        self.andor.GetAcquiredData(data)
        return self.andor._imageArray
    
    def get_images(self, data=[]):
        """
        Description This function will update the data array with the specified 
                    series of images from the circular buffer. If the specified
                    series is out of range (i.e. the images have been
                    overwritten or have not yet been acquired then an error
                    will be returned. 
        Parameters  long first: index of first image in buffer to retrieve. 
                    long last: index of last image in buffer to retrieve. 
                    at_32* arr: pointer to data storage allocated by the user. 
                    unsigned long size: total number of pixels. 
                    long* validfirst: index of the first valid image. 
                    long* validlast: index of the last valid image. 
        Return      unsigned int    
                    DRV_SUCCESS         Images have been copied into array. 
                    DRV_NOT_INITIALIZED System not initialized. 
                    DRV_ERROR_ACK       Unable to communicate with card.
                    DRV_GENERAL_ERRORS  The series is out of range. 
                    DRV_P3INVALID       Invalid pointer (i.e. NULL). 
                    DRV_P4INVALID       Array size is incorrect. 
                    DRV_NO_NEW_DATA     There is no new data yet. 
        
        See also    GetImages16, GetNumberNewImages  
        """
        validfirst, validlast = self.andor.GetImages(data)
        return self.andor._imageArray, validfirst, validlast
    
    def take_spectrum(self, data=[]):
        """
        Description Starts acquisition of data and retrieves it from the buffer.
        
        Parameters  data: array to store the acquired data in
        Returns     data
        """
        self.acquire()
        return self.get_acquired_data(data)
            