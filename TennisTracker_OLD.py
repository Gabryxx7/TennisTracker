import BackgroundExtraction as bExt 
import cv2
import numpy as np
import os.path

def nothing(arg):
    pass

checkBackground = True;
bgRate = 0.001;
videoFileName = 'myvideo3.h264';
videoTitle = os.path.splitext(videoFileName)[0];

print("Background/"+ videoTitle +"_bg.jpg");

if not os.path.exists("Background/"+videoTitle+"_bg.jpg") and checkBackground == True:
    bExt.backgroundExtraction(videoTitle, videoFileName, numOfFrames = 1000, lRate = 0.002);
    print("No background image found, creating a new one from the source video")

camera = cv2.VideoCapture("Video/"+videoFileName)

if(checkBackground == True):
    firstFrame = cv2.GaussianBlur(cv2.cvtColor(cv2.imread("Background/"+ videoTitle +"_bg.jpg"), cv2.COLOR_BGR2GRAY), (21, 21), 0); 
    bgRate = 0.0002;
else:
    firstFrame = cv2.cvtColor(camera.read()[1], cv2.COLOR_BGR2GRAY);
    bgRate = 0.009;   
        
avg2 = np.float32(firstFrame);

# loop over the frames of the video
while True:  
    (grabbed, frame) = camera.read();# grab the current frame and initialize the occupied/unoccupied
    
    if(frame is None):
        break;
          
    frameOrig = frame.copy();

	# resize the frame, convert it to grayscale, and blur it
    gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (11, 11), 0);    

	# if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray;
        continue
    
    cv2.accumulateWeighted(gray, avg2, bgRate);
    res2 = cv2.convertScaleAbs(avg2);

	# compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(res2, gray);
    threshOrig = cv2.threshold(frameDelta, 8.5, 255, cv2.THRESH_BINARY)[1];

	# dilate the thresholded image to fill in holes, then find contours on thresholded image
    eroded = cv2.erode(threshOrig, None, iterations=3);
    dilated = cv2.dilate(eroded, None, iterations=9);
    cnts, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);
        
  #Lista di variabile utilizzate per discernere tra players ed eventuale pallina
    p1 = (0,0,0,0);
    p2 = (0,0,0,0);
    ball = (0,0,0,0);
    p1Distancex = 10000;
    p2Distancex = 10000;
    p1Distancey = 10000;
    p2Distancey = 10000;
    p1TotalDistance= 10000;
    p2TotalDistance = 10000;
    ballDistance = 20000;
    p1Size = 0;
    p2Size = 0;
    ballSize = 0;
    offX = cv2.getTrackbarPos("Offset X", "Offset")-100;
    offY = cv2.getTrackbarPos("Offset Y", "Offset")-100;
    trackSizeP1 = cv2.getTrackbarPos("Size P1", "Offset");
    trackSizeP2 = cv2.getTrackbarPos("Size P2", "Offset");
    fH, fW, _ = frame.shape;
    
    #Disegno una croce sul video per calibrare la camera
    cv2.line(frame, (fW/2-20+offX, fH/2+offY), (fW/2+20+offX, fH/2+offY), (0,0,0), 1);
    cv2.line(frame, (fW/2+offX, fH/2+offY-20), (fW/2+offX, fH/2+offY+20), (0,0,0), 1);
    
    for c in cnts:
        #Calcolo il bounding box di tutte le aree bianche trovate e ne calcolo la distanza del loro centroide
        #Dal centro del campo
        (x, y, w, h) = cv2.boundingRect(c);
        xDistance = np.abs(fW/2 - x+w/2);
        yDistance = np.abs(fH/2 +offY - y+h/2);
        totalDistance = yDistance + xDistance;
        #In base all'area trovata e la sua posizione e distanza dal centro cerco di capire che giocatore e' o se e' un falso positivo
        if cv2.contourArea(c) > trackSizeP1 and y+h >= fH/2+offY:            
            if(xDistance < p1Distancex and cv2.contourArea(c) > p1Size):
                p1Distancex = xDistance;
                p1Distancey = yDistance;
                p1TotalDistance = totalDistance;
                p1 = (x, y, w, h);
                p1Size = cv2.contourArea(c);
        elif cv2.contourArea(c) > trackSizeP2 and y+h < fH/2+offY:
             if(xDistance < p2Distancex and cv2.contourArea(c) > p2Size ):
                p2Distancex = xDistance;
                p2Distancey = yDistance;
                p2TotalDistance = totalDistance;
                p2 = (x, y, w, h);
                p2Size = cv2.contourArea(c);
        #Eventuale if per riconoscere la pallina
#        elif cv2.contourArea(c) < 800:
#            if(totalDistance < ballDistance):
#                ball = (x,y,w,h);
#                ballDistance = totalDistance;
#
#    (x, y, w, h) = ball;
#    cv2.rectangle(frame, (x, y), (x + w, y + h), (255,0,0), 2)
#    cv2.putText(frame,'Ball',(x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,0,0),2) 
       
    
    (x, y, w, h) = p1;
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(frame,'P1',(x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,255,0),2)
 
    #Disegno il rettangolo del giocatore 2
    (x, y, w, h) = p2;
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    cv2.putText(frame,'P2',(x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,255),2)

    
	# show the frame and record if the user presses a key
    cv2.imshow("Match", frame)
    cv2.imshow("Dilated", dilated);
    cv2.imshow("Frame Delta", frameDelta);
    cv2.imshow("Gray", gray);
    cv2.imshow("Eroded", eroded);
    #cv2.imshow("firstFrame", firstFrame);
    cv2.imshow("Res", res2);
    
    key = cv2.waitKey(40) & 0xFF

    if key == 27:
        break
    elif key == ord("s"):
        cv2.imwrite("MatchContour.jpg", frame)
#        cv2.imwrite("MatchOrig.jpg", frameOrig)
        cv2.imwrite("ThreshDilated.jpg", thresh)
#        cv2.imwrite("ThreshOrig.jpg", threshOrig)
#        cv2.imwrite("Frame Delta.jpg", frameDelta)
#        cv2.imwrite("firstFrame.jpg", firstFrame)
        cv2.imwrite("firstFrameGray.jpg", cv2.cvtColor(cv2.imread('background.jpg'), cv2.COLOR_BGR2GRAY))
        cv2.imwrite("Court.jpg", court)
    elif key == ord('p'):
        cv2.waitKey(10000)

camera.release()
cv2.destroyAllWindows()