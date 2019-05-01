import ctypes
import os

# import dll
directory_of_this_module_and_dlls = os.path.dirname(os.path.realpath(__file__))
current_directory = os.getcwd()
os.chdir(directory_of_this_module_and_dlls)
PIE = ctypes.windll.LoadLibrary(directory_of_this_module_and_dlls+'\\PI_GCS2_DLL_x64.dll')

#int	    PI_FUNC_DECL	PI_ConnectUSB(const char* szDescription);
#BOOL	PI_FUNC_DECL	PI_IsConnected(int ID);
#void	PI_FUNC_DECL	PI_CloseConnection(int ID);
#BOOL PI_FUNC_DECL PI_qIDN(int ID, char* szBuffer, int iBufferSize);

#aliases for the strangely-named functions from the dll
PI_EnumerateUSB = getattr(PIE,"PI_EnumerateUSB")
PI_EnumerateUSB.argtypes = [ctypes.c_char_p, ctypes.c_int32, ctypes.c_char_p]

PI_ConnectUSB = getattr(PIE,"PI_ConnectUSB")
PI_ConnectUSB.argtypes = [ctypes.c_char_p]

PI_IsConnected = getattr(PIE,"PI_IsConnected")
PI_IsConnected.argtypes = [ctypes.c_int32]

PI_CloseConnection = getattr(PIE,"PI_CloseConnection")
PI_CloseConnection.argtypes =  [ctypes.c_int32]

PI_qIDN = getattr(PIE, "PI_qIDN")
PI_qIDN.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

PI_qFRF = getattr(PIE, "PI_qFRF")
PI_qFRF.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_FRF = getattr(PIE, "PI_FRF")
PI_FRF.argtypes = [ctypes.c_int32, ctypes.c_char_p]

PI_IsMoving = getattr(PIE, "PI_IsMoving")
PI_IsMoving.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_qMOV = getattr(PIE, "PI_qMOV")
PI_qMOV.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_MOV = getattr(PIE, "PI_MOV")
PI_MOV.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_qCST = getattr(PIE, "PI_qCST")
PI_qCST.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int32]

PI_qPOS = getattr(PIE, "PI_qPOS")
PI_qPOS.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_qSAI_ALL = getattr(PIE, "PI_qSAI_ALL")
PI_qSAI_ALL.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_int32]

PI_SAI = getattr(PIE, "PI_SAI")
PI_SAI.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_char_p]

PI_qTMN = getattr(PIE, "PI_qTMN")
PI_qTMN.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_qTMX = getattr(PIE, "PI_qTMX")
PI_qTMX.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_qSVO = getattr(PIE, "PI_qSVO")
PI_qSVO.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_SVO = getattr(PIE, "PI_SVO")
PI_SVO.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_qSST = getattr(PIE, "PI_qSST")
PI_qSST.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_SST = getattr(PIE, "PI_SST")
PI_SST.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

#%%
PI_qRON = getattr(PIE, "PI_qRON")
PI_qRON.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_RON = getattr(PIE, "PI_RON")
PI_RON.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_bool*1]

PI_POS = getattr(PIE, "PI_POS")
PI_POS.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1] 

PI_STP = getattr(PIE, "PI_STP")
PI_STP.argtypes = [ctypes.c_int32] 

PI_qOMA = getattr(PIE, "PI_STP")
PI_qOMA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]

PI_OMA = getattr(PIE, "PI_STP")
PI_OMA.argtypes = [ctypes.c_int32, ctypes.c_char_p, ctypes.c_double*1]
