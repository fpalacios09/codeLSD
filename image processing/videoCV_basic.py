import cv2
import argparse

# Configurar el parser de argumentos
parser = argparse.ArgumentParser(description='Escalar el video en tiempo real.')
parser.add_argument('escala', type=float, nargs='?', default=1.0, help='Factor de escala para redimensionar el video (por defecto es 1.0)')

# Parsear los argumentos
args = parser.parse_args()
escala = args.escala

# Inicializar la captura de video
img_cv = cv2.VideoCapture(0)

while True:
    ret, frame = img_cv.read()
    if not ret:
        break

    # Redimensionar la imagen
    img_resize = cv2.resize(frame, (0, 0), fx=escala, fy=escala)

    # Mostrar la imagen redimensionada
    cv2.imshow('frame', img_resize)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar los recursos y cerrar las ventanas
img_cv.release()
cv2.destroyAllWindows()


