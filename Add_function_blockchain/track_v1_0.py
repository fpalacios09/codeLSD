


from ultralytics import YOLO
import torch
import cv2

# Verificar si CUDA está disponible
print('Disponibilidad de CUDA con torch: ', torch.cuda.is_available())

# Cargar el modelo YOLO
model = YOLO("yolov8n.pt")  # Cambia a otro modelo si es necesario (yolov8m.pt, yolov8l.pt)

# Ruta del video de entrada (puede ser '0' para cámara en vivo o ruta de un video .mp4)
video_path = '0'

# ID de la clase para automóviles (en el conjunto de datos COCO, los automóviles tienen ID 2)
car_class_id = 2

# Configuración del tracker
tracker_config = {
    'tracker': "bytetrack.yaml",  # Usa 'botsort.yaml' o 'bytetrack.yaml'
    'show': False,                 # Mostrar resultados en tiempo real
    'save': False,                # No guardar resultados
    'save_txt': False,            # No guardar detecciones en archivos .txt
    'imgsz': 640,                 # Tamaño de la imagen
    'conf': 0.4,                  # Umbral de confianza
    'iou': 0.5,                   # Umbral de IOU para el tracking
    'agnostic_nms': True,         # NMS agnóstico de clase
    'device': '0',                # Usar la GPU
    'stream': True                # Usar streaming en tiempo real
}

# Realizar el seguimiento de objetos en el video
for result in model.track(source=video_path, **tracker_config):  # Iterar sobre los resultados de cada fotograma
    image = result.orig_img  # Imagen original del frame
    for det in result.boxes:  # Las detecciones están en result.boxes
        # Detalles de la caja delimitadora: coordenadas (x1, y1, x2, y2), confianza y clase
        xyxy = det.xyxy[0].cpu().numpy()  # Coordenadas del cuadro (x1, y1, x2, y2)
        confidence = det.conf[0].cpu().numpy()  # Confianza de la detección
        class_id = int(det.cls[0].cpu().numpy())  # ID de la clase detectada, asegurándonos de que sea un número entero
        # track_id = int(det.id[0].cpu().numpy())

        # print(f"Coordenadas del bbox: {xyxy}, Confianza: {confidence}, Clase: {class_id}")

        # Si la clase detectada es un automóvil (ID 2 en COCO)
        if class_id == car_class_id:
            print(f"Automóvil detectado: Coordenadas del bbox: {xyxy}, Confianza: {confidence}, Clase: {class_id} (Automóvil)")     
            # Aquí es donde podrías agregar lógica adicional, como dibujar cuadros con OpenCV o hacer seguimiento

            cv2.rectangle(image, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
            cv2.putText(image, f"Car: {confidence:.2f}", (int(xyxy[0]), int(xyxy[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Si no es un automóvil, puedes dejar el bloque vacío o agregar alguna acción adicional si lo prefieres
        else:
            pass  # Puedes realizar alguna otra acción si lo deseas

    cv2.imshow("Tracking", image)
    cv2.waitKey(1)  # Mantener la ventana de OpenCV abierta
