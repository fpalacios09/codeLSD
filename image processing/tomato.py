import cv2
import numpy as np

# Cargar la imagen
image = cv2.imread('tomate2.jpg')

# Convertir la imagen a escala de grises
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Aumentar el contraste de la imagen en escala de grises
clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(8, 8))
gray = clahe.apply(gray)

# Aplicar un umbral (threshold)
_, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

# Encontrar los contornos en la imagen threshold
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Dibujar los contornos en la imagen original (en verde)
cv2.drawContours(image, contours, -1, (0, 255, 0), 2)

# Mostrar la imagen original con los contornos dibujados
cv2.imshow('Contornos de tomate', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
