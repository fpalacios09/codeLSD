import cv2
from ultralytics import YOLO
import torch

# Cargar el modelo YOLOv8
model = YOLO("yolov8n.pt")  # Usar la GPU (si está disponible)

# Definir el flujo de entrada (puede ser un archivo de video o una cámara)
source = "citec017.mp4"  # Aquí puedes poner el archivo o URL del stream, o '0' para la cámara web

# Abrir el flujo de video con OpenCV
cap = cv2.VideoCapture(source)  # Si usas una cámara, 'source' puede ser 0 (cámara por defecto)

if not cap.isOpened():
    print("Error: No se pudo abrir el video.")
    exit()

while True:
    # Leer el siguiente frame
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame.")
        break

    # Realizar las predicciones (detección y tracking)
    results = model.track(frame, tracker="botsort.yaml", imgsz=640, conf=0.4, iou=0.5, device='0')

    # Obtener las coordenadas y las etiquetas de las detecciones (las predicciones son de tipo YOLO)
    # El objeto 'results' contiene las coordenadas de las cajas, las clases y las IDs de los objetos
    for result in results:
        # Desplegar los resultados en el frame
        for box in result.boxes:
            # Coordenadas del cuadro delimitador (bounding box)
            x1, y1, x2, y2 = box.xyxy[0]  # Coordenadas de la caja (x1, y1) - (x2, y2)
            conf = box.conf[0]  # Confianza de la predicción
            cls = int(box.cls[0])  # Clase del objeto (ejemplo: 0 para 'persona')

            # Dibujar el cuadro delimitador en el frame
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Escribir la clase y la confianza en el cuadro
            label = f"{model.names[cls]} {conf:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Mostrar el frame procesado
    cv2.imshow("YOLO Tracking", frame)

    # Salir si presionamos la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura y cerrar la ventana
cap.release()
cv2.destroyAllWindows()

