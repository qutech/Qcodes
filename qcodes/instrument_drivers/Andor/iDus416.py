from iDus_python_library.Camera import andor

cam = andor.Andor()
cam.SetDemoReady()
cam.StartAcquisition()
data = []
cam.GetAcquiredData(data)
cam.SaveAsTxt('raw.txt')
cam.ShutDown()
# %%