try:
    from SalsaPy import radarWrapper
    X2_DRIVER_AVAILABLE = True
except:
    X2_DRIVER_AVAILABLE = False
from pymoduleconnector import ModuleConnector
import time
import threading
import queue
import csv
import numpy as np
import sys
# from globalVars import *
from io import open
import multiprocessing


class CollectionThread(threading.Thread):
    def __init__(self, threadID, name, radarBuffer, stopEvent,radarSettings, radarIP='192.168.7.2', simulate = False, filePaths = None, fs=200, baseband=False,
                 nonRealTimeMode= False,resumeEvent = None):
        threading.Thread.__init__(self)
        self.name = name
        self.threadID = threadID
        self.radarBuffer = radarBuffer
        self.stopEvent = stopEvent
        self.resumeEvent = resumeEvent
        self.nonRealTimeMode = nonRealTimeMode
        self.radarIP = radarIP
        self.radarSettings = radarSettings
        self.simulate = simulate
        self.filePaths = filePaths
        print ('Collection thread initialized')
        
    def run(self):
       # global radarDataQ
        if self.simulate:
            prevTStamp = 0
            for file in self.filePaths:
                print(('Opening file: ', file))
                with open(file) as csvFile:
                    thisFileData = []
                    csvReader = csv.reader(csvFile)
                    times = []
                    for row in csvReader:
                        # print int(float(row[0]))
                        times.append(int(float(row[0])))
             
                        thisFileData.append(row)
                        if self.stopEvent.is_set():
                            break
              # thisFileDataNP = np.array(thisFileData, dtype=complex)
                # times = list(imap(int,thisFileDataNP[:,0]))
                # print times
                prevTStamp = times[0]  # prevTStamp is 0 for multiple files
                fileitr = 0
                for timestamp in times:
                    thisSleep = (timestamp - prevTStamp) / 1000
                    # print('Sleeping %f seconds'%thisSleep)
                    time.sleep(thisSleep)
                    self.radarBuffer.put(list(thisFileData[fileitr]))
                    fileitr += 1
                    prevTStamp = timestamp
                    if self.nonRealTimeMode:
                        if not self.resumeEvent.is_set():
                            print('Pausing till user response')
                            self.resumeEvent.wait()
                            print('Resuming')
                    if self.stopEvent.is_set():
                        break
                if self.stopEvent.is_set():
                    break
            print ('Simulation complete')

        elif X2_DRIVER_AVAILABLE:
            print ('Initializing radar')
            self.radarObject = self.initializeRadar()
            startTime = time.time()
            print ('Starting radar data collection')
            while not self.stopEvent.is_set():
                currentTime = time.time()
                radarFrame = self.radarObject.GetFrameRaw()
                self.radarBuffer.put([int((currentTime - startTime) * 1000)] + list(radarFrame))
            self.radarObject.Close()
        else:
            print('X2 DRIVER IS NOT AVAILABLE CAN NOT GET DATA FROM X2 RADAR. Only simulation mode is available, please re-run with simulation mode switched on')
            sys.exit(0)

    def initializeRadar(self):
        RADAR_OBJECT = radarWrapper.radarWrapper(self.radarIP)
        # Get a list of the connected radar modules
        modules = RADAR_OBJECT.ConnectedModules()

        # Open a connection to the radar module
        RADAR_OBJECT.Open(modules[0])
        result = RADAR_OBJECT.ExecuteAction('MeasureAll')
        print(result)
        print ('Module Opened')
        IterationsDefaultValue = RADAR_OBJECT.Item('Iterations')
        offsetdistance = RADAR_OBJECT.Item('OffsetDistanceFromReference')
        samplers = RADAR_OBJECT.Item('SamplersPerFrame')
        print(('Samplers %d' % samplers))

        for key in self.radarSettings:
            RADAR_OBJECT.TryUpdateChip(key,self.radarSettings[key])

        # check radar settings
        for key in self.radarSettings:
            currValue = RADAR_OBJECT.Item(key)
            if self.radarSettings[key]!=currValue:
                raise ValueError
            else:
                print((key+' : '+str(currValue)))

        return RADAR_OBJECT
        
class CollectionThreadX4MP(multiprocessing.Process):
    def __init__(self,threadID, name, stopEvent, radarSettings, baseband = False, fs = 200, radarPort='/dev/ttyACM0', dataQueue=None):
        multiprocessing.Process.__init__(self)
        self.name = name
        self.stopEvent = stopEvent
        self.radarDataQ = dataQueue
        self.radarPort = radarPort
        self.radarSettings = radarSettings
        self.fs = fs
        self.radarPort = radarPort
        self.baseband = baseband
        print ('Collection thread initialized')

    def run(self):
        print ('Initializing radar')
        self.reset(self.radarPort)
        self.mc = ModuleConnector(self.radarPort)
        self.radarObject = self.mc.get_xep()
        # Set DAC range
        self.radarObject.x4driver_set_dac_min(self.radarSettings['DACMin'])
        self.radarObject.x4driver_set_dac_max(self.radarSettings['DACMax'])

        # Set integration
        self.radarObject.x4driver_set_iterations(self.radarSettings['Iterations'])
        self.radarObject.x4driver_set_pulses_per_step(self.radarSettings['PulsesPerStep'])
        self.radarObject.x4driver_set_frame_area(self.radarSettings['FrameStart'],self.radarSettings['FrameStop'])
        if self.baseband:
            self.radarObject.x4driver_set_downconversion(1)
        self.radarObject.x4driver_set_fps(self.fs)

        frame = self.read_frame()
        if self.baseband:
            frame = abs(frame)
        self.clear_buffer()
        startTime = time.time()
        print((self.radarObject.get_system_info(0x07)))

        print ('Starting radar data collection')
        while True:
          #  print ('----------------')
            currentTime = time.time()
            radarFrame = self.read_frame()
            #print(radarFrame)
            rdDataRowstr = []
            for i in range(len(radarFrame)):
                rdDataRowstr.append(str(radarFrame[i]).replace('(','').replace(')',''))
                #print(str(radarFrame[i]).replace('(','').replace(')',''))
            self.radarDataQ.put([currentTime] + list(rdDataRowstr))

        self.radarObject.x4driver_set_fps(0) # stop the radar

    def reset(self,device_name):
        mc = ModuleConnector(device_name)
        r = mc.get_xep()
        r.module_reset()
        mc.close()
        time.sleep(5)

    def read_frame(self):
        """Gets frame data from module"""
        d = self.radarObject.read_message_data_float()
        frame = np.array(d.data)
        # print len(frame)
        # print frame

        # Convert the resulting frame to a complex array if downconversion is enabled
        if self.baseband:
            n = len(frame)
            # print type(n // 2)
            frame = frame[:n // 2] + 1j * frame[n // 2:]

        return frame

    def clear_buffer(self):
        """Clears the frame buffer"""
        while self.radarObject.peek_message_data_float():
           _ = self.radarObject.read_message_data_float()

