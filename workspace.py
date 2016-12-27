#!/usr/bin/env python3

#Jordan Tick
#My own workspace B)
#Testing opencv and cozmo's camera
#check out ~/.local/lib/python3.5/site-packages/cozmo for camera.py to find how to get an RGB image?????
#opencv imshow assumes BGR color space

import cozmo
import time,sys,numpy as np
import cv2
WIN_NAME = "display"

#filter techniques discovered from
#http://stackoverflow.com/questions/12093594/how-to-implement-band-pass-butterworth-filter-with-scipy-signal-butter
import matplotlib.pyplot as plt
from scipy.signal import butter,lfilter,freqz
def butter_bandpass(lowcut, highcut, fs, order=5):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b, a = butter(order, [low, high], btype='band')
  return b, a


def butter_bandpass_filter(data, myfilter):
  (b,a) = myfilter
  y = lfilter(b, a, data)
  return y

def myProgram(robot):
  global count,start
  robot.camera.image_stream_enabled = True

  #vars for filter
  lowfreq = 1 #low heartrate in hz
  highfreq = 4 #high heartrate in hz

  #vars for sample frequency
  count = 0
  start = -1
  curFreq = -1

  #vars for memory
  dims = [-1,-1]
  imageSeq = None
  result = None
  NUM_IMS = 200
  cur_count = 0

  print("running program...")
  cv2.namedWindow(WIN_NAME)
  windowOpen=True
  while(windowOpen): #close program when window exited
    windowOpen= (cv2.getWindowProperty(WIN_NAME,0) >= 0)
    curim = robot.world.latest_image
    if curim is not None and windowOpen:
      #get image
      gray = np.array(curim.raw_image).astype(np.uint8)[:,:,0]

      #setup memory
      if(curFreq != -1 and dims[0] != -1 and imageSeq is None):
        dimensions = (dims[0],dims[1],NUM_IMS)
        print("allocating",dimensions)
        imageSeq = np.zeros(dimensions,np.uint8)
        result = np.zeros(dims,np.uint8) #the filtered result
        print(imageSeq.shape)
      if(imageSeq is not None):
        if(cur_count<NUM_IMS):
          imageSeq[:,:,cur_count] = gray
          cur_count+=1
        else: #process and restart
          #create filter
          bpfilter = butter_bandpass(lowfreq,highfreq,curFreq,order=9)
          #display filter on side cause why not
          (w,h) = freqz(bpfilter[0],bpfilter[1],worN=8000)
          plt.plot(0.5*curFreq*w/np.pi,np.abs(h),'b')
          plt.plot(highfreq,0.5*np.sqrt(2),'ko')
          plt.axvline(highfreq,color='k')
          plt.axvline(lowfreq,color='k')
          plt.xlim(0,0.5*curFreq)
          plt.title("Filter Frequency Response")
          plt.xlabel("Frequency (Hz)")
          plt.grid()

          #filter every pixel
          for i in range(dims[0]):
            for j in range(dims[1]):
              signal = imageSeq[i,j,:]
              filtered=butter_bandpass_filter(signal,bpfilter)
              result[i,j] = np.mean(filtered,axis=0)

          #show result
          cv2.imshow("result",result)
          cv2.waitKey(1)

          #restart vars
          imageSeq[:,:,0] = gray
          cur_count=1

      #monitor sampling frequency
      count += 1
      curtime = time.time()
      if(start==-1):
        start=curtime
      elif(curtime-start>1):
        curFreq = count/(curtime-start)
        print("freq is %.2f" % (curFreq))
        start=curtime
        count=0
      if(dims[0]==-1):
        dims = gray.shape

      #display image
      cv2.imshow(WIN_NAME,gray)
      cv2.waitKey(1)
  cv2.closeAllWindows()

#start program by establishing a connection with Cozmo
cozmo.robot.Robot.drive_off_charger_on_connect = False #stay on charger
cozmo.run_program(myProgram)
