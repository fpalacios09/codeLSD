import numpy as np 
import cv2
import math
from cv2 import equalizeHist

def normalize(img, min, max):
    img2 = img.copy()
    img2 = (max - min) * ((img2 - img2.min()) / (img2.max() - img2.min())) + min
    img2 = img2.astype(np.uint8)

    return img2

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------

img_cv = cv2.VideoCapture(0)       #0 por defecto a una camara, si hay mas camaras se cambia a 1,2,etc

while True:
    ret, frame = img_cv.read()     #con esto se muestra la imagen, el video es una secuencia de imagenes
    # son frames y cada imagen o frame se puede tratar por separado
    
    #--------------------------------------------------------------------------------------------
    imgbw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # FGaussian Filtering
    s      = 51
    kernel = cv2.getGaussianKernel(s, s/8.5)        # Gaussian s x 1  (s = size, s/8.5 = sigma)
    window = np.outer(kernel, kernel.transpose())   # Gaussian s x s pixels

    imgL = cv2.filter2D(imgbw, -1, window)

    # High Pass Filtering

    imgH = np.abs(imgL.astype(int) - imgbw.astype(int))
    imgH = normalize(imgH, 0, 255)

    imgbin = cv2.threshold(imgH, 25, 255, cv2.THRESH_BINARY)[1]    # accede al elemento 1 xq el elemento 0 es el umbral

    #--------------------------------------------------------------------------------------------

    # Escalar la imagen para mostrarla más grande
    escala = 1.0  # Ajusta este valor según sea necesario para aumentar el tamaño de la imagen
    img_resize = cv2.resize(imgbin, (0, 0), fx=escala, fy=escala)

    cv2.imshow('frame', img_resize)

    if cv2.waitKey(1) & 0xFF==ord('q'):
        break   #si se presiona la letra q se cierra la ventana   

img_cv.release()
cv2.destroyAllWindows()

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------