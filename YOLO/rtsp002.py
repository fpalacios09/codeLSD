import cv2

# URL RTSP de la cámara IP
rtsp_url = "rtsp://admin:E10ADC3949BA59ABBE56E057F20F883E@192.168.20.251:554/mpeg4"

# Factor de escala (puedes ajustar este valor)
scale_factor = 0.35  # 0.5 es el 50% del tamaño original, 1.0 es el tamaño original, 2.0 es el doble de tamaño

# Abrir la cámara con OpenCV
cap = cv2.VideoCapture(rtsp_url)

# Verificar si la cámara se ha abierto correctamente
if not cap.isOpened():
    print("Error: No se pudo conectar a la cámara RTSP")
    exit()

# Mostrar el video en una ventana
while True:
    # Leer un fotograma de la cámara
    ret, frame = cap.read()

    if not ret:
        print("Error: No se pudo recibir el fotograma.")
        break

    # Redimensionar el fotograma según el factor de escala
    height, width = frame.shape[:2]
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Mostrar el fotograma redimensionado
    cv2.imshow('Cámara IP RTSP', resized_frame)

    # Salir si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()


