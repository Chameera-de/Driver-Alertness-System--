
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
import urllib.request

print("Imports Done")

#Mobile Camera IP
url = "http://192.168.43.1:8080/shot.jpg"


#
beginSecond = time.time()
notClosed = 0
yawnCount = 0
not_yawn = 0
abc=0

#Marking Regions for Distraction
allowable_x = 450//7		
allowable_y = 337//7
lower_x = allowable_x*2
upper_x = allowable_x*5
#lower_y = allowable_y*2
lower_y = 0
#upper_y = allowable_y*5
upper_y = 337
inside = 0

#Counters

FrameCounter = 0
foundBefore=False
EarFound = False
earFrameCounter = 0
earFoundThreshold = 10    
img = 0
face_present = 0
no_face_present = 0

#Ratio of width and height of eye
eye_thresh = 0.3

#Number of frames eye should be closed
drowsyFrames = 25

COUNTER = 0
counter_pos = 0

count = 0

#Call IP Webcam Android App
def getImage():
	imgResponse = urllib.request.urlopen(url)
	imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
	img = cv2.imdecode(imgNp,-1)
	return img


#Detect Ears
def haar_ear(gray):
	global foundBefore, beginSecond, EarFound, earFrameCounter, earFoundThreshold, img
	flipgray= cv2.flip(gray,1)
	
	
	

	#Call the Haar Cascade for Left ear
	l_ear_cascade = cv2.CascadeClassifier('haarcascade_mcs_leftear_3rdparty.xml')
	
	
	
	mLear = l_ear_cascade.detectMultiScale(gray)

    #Take flipped version of left ear
	mRear = l_ear_cascade.detectMultiScale(flipgray)

    #Draw box around the ears
	for (x,y,w,h) in mLear:
		cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

	for (x,y,w,h) in mRear:
		cv2.rectangle(frame, (450-x,y), (450-x-w,y+h), (0,255,0), 2)



	now = time.time()
		
	if(foundBefore):
        #Ears were found, and is still found
        #If Ears were detected for too long, report Looking Away. Distracted
		EarFound = True
		cv2.putText(frame, "Ear found", (10, 60),	cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 120, 255), 2)
		cv2.putText(frame, "Looking Away. Distracted", (200, 300),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	if(now - beginSecond < (2 if foundBefore else 1)):
			
		if(len(mLear) > 0 or len(mRear) > 0):
			earFrameCounter += 1
						
					
			
	else:
			#Ears should be detected atleast "earFoundThreshold" number of times before reporting
			beginSecond = time.time()

			if(earFrameCounter > earFoundThreshold):
				foundBefore = True
				
				earFrameCounter = 0
			else:
				foundBefore = False
				
	return [EarFound, frame]
			

	

def eye_widthByHeight(eye):
	
	x = dist.euclidean(eye[1], eye[5])
	y = dist.euclidean(eye[2], eye[4])
	z = dist.euclidean(eye[0], eye[3])
	eyeWidthByHeight = (x + y) / (2.0 * z)
	return eyeWidthByHeight
 

def mouth_widthByHeight(mouth):
	l_r = dist.euclidean(mouth[0], mouth[6])
	u_d_1 = dist.euclidean(mouth[2], mouth[10])
	u_d_2 = dist.euclidean(mouth[3], mouth[9])
	u_d_3 = dist.euclidean(mouth[4], mouth[8])
	avg = (u_d_1+u_d_2+u_d_3) / 3
	mar=avg/l_r
	
	return mar







print("Imports done. Starting...")

#Get a instance of dlib frontal face detector object
detector = dlib.get_frontal_face_detector()

#Link the face landmark weights to the instance
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#Points on the image that map to face features
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]


#Wait to initialize Model
time.sleep(1.0)

#Code starts here

while True:
	#Get current frame from Android Device
	frame = getImage()
    
    #Resize the image
	frame = imutils.resize(frame, width=450)

    #Boundary box in which driver should stay
	cv2.line(frame, (lower_x, lower_y), (lower_x, upper_y), (255,0,0), 1)
	cv2.line(frame, (upper_x, upper_y), (lower_x, upper_y), (255,0,0), 1)
	cv2.line(frame, (upper_x, lower_y), (upper_x, upper_y), (255,0,0), 1)
	cv2.line(frame, (upper_x, lower_y), (lower_x, lower_y), (255,0,0), 1)


    #Convert to grayscale 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	[Haar_check, frame] = haar_ear(gray)
	
	rects = detector(gray, 0)
	

    #If no face AND ear detected, then driver is not present
    if(len(rects)==0 and Haar_check==0):
		count += 1
		if(count>5):
			cv2.putText(frame, "Driver Face not detected", (300, 300),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			count = 0
	
	elif(len(rects)==0 and Haar_check):
		count +=1
        
		if(count>10):
			cv2.putText(frame, ".", (300, 300),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			count = 0
        
	#Store start time of loop
    now = time.time()



	if(len(rects) == 0): #If no faces
		no_face_present += 1 #If no face present for this frame, incremenet count

		if(no_face_present >= 60):  #If no face was detected for more than 60 frames, we can concluded that no driver is there
			cv2.putText(frame, "Driver face not detected", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 120, 255), 2)

	for rect in rects: #For every face detected
		no_face_present = 0
		face_present += 1

		abc=rect.top()-rect.bottom()
		#print(abc)
	
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)
		#print("Shape",shape)
        
        #get the contours of the eyes
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		
        #get the contours of the mouth
        mouth = shape[mStart:mEnd]
		
		#get relative location of eye 
		leftEyeLoc = leftEye[0]
		rightEyeLoc = rightEye[0]
		avgPosEye = (leftEyeLoc + rightEyeLoc)//2

	
        #If eyes arent inside a region given, then it can be said that the driver isnt looking front
		if((avgPosEye[0] not in range(lower_x, upper_x)) or (avgPosEye[1]) not in range(lower_y, upper_y)):
					counter_pos += 1
				  

					if(counter_pos > 15):
						cv2.putText(frame, "Distracted", (30, 300),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		else:
					inside += 1
					if(inside > 10):
						counter_pos = 0
						inside = 0
				   
	

		leftEAR = eye_widthByHeight(leftEye)
		rightEAR = eye_widthByHeight(rightEye)
		mouthass = mouth_widthByHeight(mouth)
		
		ear = (leftEAR + rightEAR) / 2.0
		
	
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		mouthHull = cv2.convexHull(mouth)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
		
        # cv2.circle(frame,(mouth[0][0],mouth[0][1]),1,(0,0,255),-1)
		# cv2.circle(frame,(mouth[6][0],mouth[6][1]),1,(0,100,100),-1)
		# cv2.circle(frame,(mouth[2][0],mouth[2][1]),1,(0,255,255),-1)
		# cv2.circle(frame,(mouth[10][0],mouth[10][1]),1,(255,0,255),-1)
		# cv2.circle(frame,(mouth[3][0],mouth[3][1]),1,(0,0,255),-1)
		# cv2.circle(frame,(mouth[9][0],mouth[9][1]),1,(0,0,255),-1)
		# cv2.circle(frame,(mouth[4][0],mouth[4][1]),1,(0,0,255),-1)
		# cv2.circle(frame,(mouth[8][0],mouth[8][1]),1,(0,0,255),-1)
		
		
        if ear < eye_thresh:
			COUNTER += 1
			
			if COUNTER >= drowsyFrames:
				
				cv2.putText(frame, "Drowsy", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 120, 255), 2)


		else:
						notClosed += 1
					   
						if(notClosed > 10):
								COUNTER = 0
								notClosed = 0
								ALARM_ON = False
		
			


		
		if mouthass > 0.6 :
			yawnCount += 1
		
        	#print(yawnCount)
            
			if(yawnCount > 8):
							if(ear<0.4): #Take into consideration the eye width by height ratio also while checking for yawning
								cv2.putText(frame, "Yawning", (10, 60),	cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 120, 255), 2)

		else:
			not_yawn += 1
			if(not_yawn > 4):
				yawnCount = 0
				not_yawn = 0	

		
    #Show frames
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 

	if key == ord("q"):
		break


cv2.destroyAllWindows()

