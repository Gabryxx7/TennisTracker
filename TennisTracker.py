import cv2
import numpy as np

def nothing(x):
    pass;

videoFileName = 'sunday.mp4';  #Nome del file video
history = 450   #Learning rate del metodo di sottrazione del background MOG
bgRate = 0.001; #Learning rate del metodo di sottrazione del background MOG2

camera = cv2.VideoCapture("Video/"+videoFileName) #Apro lo stream video dal file
#camera = cv2.VideoCapture(0);  #Apro lo stream video dalla webcam

#Creo una finestra con delle trackbar per calibrare l'applicazione
cv2.namedWindow("Offset");
cv2.createTrackbar("Offset X", "Offset", 0, 500, nothing); #Offset per il centro del campo
cv2.createTrackbar("Offset Y", "Offset", 0, 500, nothing);#Offset per il centro del campo
cv2.createTrackbar("Size P1", "Offset", 2500, 5000, nothing); #Calibra la dimensoine del giocatore 1
cv2.createTrackbar("Size P2", "Offset", 300, 5000, nothing); #Calibra la dimensione del giocatore 2

cameraShaking = False;   #Variabile che mi dice quando il background cambia troppo
useMOG = False; #Decide quale dei due metodi usare, MOG o MOG 2

#Mi creo il background subtractor
if(useMOG):
    fgbg = cv2.BackgroundSubtractorMOG();
else:
    fgbg = cv2.BackgroundSubtractorMOG2(500, 180, False);   

#E ciclo infinitamente finche non finisce il video
while True:  
    (grabbed, frame) = camera.read(); #Prendo il frame
       
    if(frame == None):
        print("No image");
        break;
                
    frameOrig = frame.copy();
    #Trasformo il frame in scala di grigi e lo sfoco un po per togliere il rumore
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);
    
    #Applico il metodo di sottrazione del background
    if(useMOG):
        grayBlur = cv2.medianBlur(gray, 3);
        fgmask = fgbg.apply(grayBlur, learningRate=1.0/history)
    else:
        grayBlur = cv2.medianBlur(gray, 1);
        fgmask = fgbg.apply(grayBlur, None, bgRate);
        
    #IF utile per capire quando cambia troppo il background, se i pixels bianchi sono piu'
    #del 40% del totale allora sta cambiando troppo l'immagine
    #if(cv2.countNonZero(fgmask) > (grayBlur.size * 40) / 100):
        #print("Camera shaking");
        #fgbg.initialize(grayBlur.size(), grayBlur.type());
        
    #Applico una opening (erosion e successiva dilatazione), per togliere rumore ed aumentare l'area trovata
    kernel = np.ones((2,2), np.uint8);
    fgmaskEroded = cv2.erode(fgmask, kernel, iterations=1)
    fgmaskDilated = cv2.dilate(fgmaskEroded, None, iterations=13); 
    
    #Trovo i bordi dell'area in movimento
    cnts, _ = cv2.findContours(fgmaskDilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE);  

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
                      
    #Mostro a video i risultati
    cv2.imshow("Match", frame);
    cv2.imshow('MOG',fgmask);
    cv2.imshow('MOGDilated',fgmaskDilated);
    
    key = cv2.waitKey(40) & 0xFF #Controllo eventuali input

	#Premendo s si ha una istantanea del video, premendo p invece si mette in pausa il processo
    if key == 27:
        break
    elif key == ord("s"):
        cv2.imwrite("Gray.jpg", gray)
        cv2.imwrite("GrayBlur.jpg", grayBlur)
        cv2.imwrite("Match.jpg", frameOrig)
        cv2.imwrite("MatchContour.jpg", frame)
        cv2.imwrite("MOG.jpg", fgmask)
        cv2.imwrite("MOGDilated.jpg", fgmaskDilated)
    elif key == ord('p'):
        cv2.waitKey(10000)

camera.release()
cv2.destroyAllWindows()