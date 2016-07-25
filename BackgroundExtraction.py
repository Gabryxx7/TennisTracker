# -*- coding: utf-8 -*-
"""
Script utilizzato per l'estrazione del background col primo metodo 
"""

import cv2
import numpy as np

#La funzione prende in ingresso il titolo del video, il nome intero del file, i frame da cui estrarre il background e il learning rate
def backgroundExtraction(videoTitle, videoFileName, numOfFrames, lRate):
    vc = cv2.VideoCapture("Video/"+videoFileName)
    i = 0;
    frameCounter = 0;
    
    #Se il video e' aperto cerco di prenderne il primo frame e lo includo nella media
    if vc.isOpened():
        rval, frame = vc.read()        
        avg2 = np.float32(frame)
    else:
        rval = False
    
    #Se si vogliono saltare dei frame iniziali
#    for x in range(0,200):
#        rval, frame = vc.read();
#        key = cv2.waitKey(20);
#        cv2.imshow('Source Video',frame);
#        print(x);
    
    #Ciclo finche' non raggiungo il numero di frame
    while frameCounter < numOfFrames:
        print(frameCounter);
        rval, frame = vc.read(); #Leggo un frame dal video
        
        if frame == None:        
            break
        
        cv2.accumulateWeighted(frame,avg2,lRate)     #Calcolo la media accumulata dei frames
        res2 = cv2.convertScaleAbs(avg2) #Questo serve ad evitare che la media salga fino a 255, avendo solo pixel bianchi   

    
        cv2.imshow('Source Video',frame)
        cv2.imshow('Background',res2)
        
        key = cv2.waitKey(20); #Necessario per aspettare il prossimo frame, altrimenti non parte proprio il programma
        
        if key == 27:
            break
        elif key == ord("s"):
            cv2.imwrite("Background/backSnapshot"+str(i)+".jpg", frame) #Se viene premuto s si salva un'istantanea del background
            i = i+1
            
        frameCounter = frameCounter + 1; #Incremento il contatore
            
    
    cv2.imwrite("Background/"+videoTitle +"_bg.jpg",res2) 
    vc.release()
    cv2.destroyAllWindows()
    
    return

