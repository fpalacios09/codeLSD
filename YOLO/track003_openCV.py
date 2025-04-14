from ultralytics import YOLO
import torch

print('Disponibilidad de CUDA con torch: ', torch.cuda.is_available())  # Verificar si CUDA está disponible

# Cargar el modelo YOLO
model = YOLO("yolov8n.pt")  # Cambia a otro modelo si es necesario (yolov8m.pt, yolov8l.pt)

# Ruta del video de entrada
video_path = '0'  # Cambia esta ruta por la del video .mp4

# Configuración del tracker
tracker_config = {
    'tracker': "bytetrack.yaml",  # Usa 'botsort.yaml' o 'bytetrack.yaml'
    'show': True,                 # Mostrar resultados en tiempo real
    'save': False,                # No guardar resultados
    'save_txt': False,            # No guardar detecciones en archivos .txt
    'imgsz': 640,                 # Tamaño de la imagen
    'conf': 0.4,                  # Umbral de confianza
    'iou': 0.5,                   # Umbral de IOU para el tracking
    'agnostic_nms': True,        # NMS agnóstico de clase
    'device': '0',                # Usar la GPU
    'stream': True               # Usar streaming en tiempo real
}

# Realizar el seguimiento de objetos en el video
for result in model.track(source=video_path, **tracker_config):  # Iterar sobre los resultados de cada fotograma
    for det in result.boxes:  # Las detecciones están en result.boxes
        # Detalles de la caja delimitadora: coordenadas (x1, y1, x2, y2), confianza y clase
        xyxy = det.xyxy[0].cpu().numpy()  # Coordenadas del cuadro (x1, y1, x2, y2)
        confidence = det.conf[0].cpu().numpy()  # Confianza de la detección
        class_id = det.cls[0].cpu().numpy()  # ID de la clase detectada

        # Mostrar las coordenadas, confianza y clase en tiempo real
        print(f"Coordenadas del bbox: {xyxy}, Confianza: {confidence}, Clase: {class_id}")

        # También puedes agregar lógica para dibujar los cuadros sobre la imagen, si lo deseas
        # Ejemplo: usar OpenCV para dibujar los cuadros, si prefieres visualizar las coordenadas gráficamente

    # Si necesitas realizar alguna acción específica para cada fotograma, puedes hacerlo aquí


