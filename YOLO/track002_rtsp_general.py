from ultralytics import YOLO

import torch

print('Disponibilidad de CUDA con torch: ', torch.cuda.is_available())  # Esto debería devolver True si la GPU está disponible

# Cargar el modelo YOLO (puedes elegir el modelo que más te convenga, por ejemplo, yolov8n, yolov8m, etc.)
model = YOLO("yolov8n.pt")  # Cambia a otro modelo si es necesario (yolov8m.pt, yolov8l.pt)

# Ruta del video de entrada
# video_path = '0'  # Cambia esta ruta por la del video .mp4
video_path = "rtsp://admin:E10ADC3949BA59ABBE56E057F20F883E@192.168.20.251:554/mpeg4"

# Iniciar el tracking de objetos en el video
model.track(
    source=video_path,          # Ruta del video .mp4
    stream=False,               # No es necesario streaming en tiempo real
    tracker="bytetrack.yaml",     # Usa 'botsort.yaml' o 'bytetrack.yaml' para la configuración del tracker
    show=True,                  # Mostrar resultados en tiempo real
    save=False,                  # Guardar los resultados con las detecciones
    save_txt=False,              # Guardar las detecciones en archivos .txt
    imgsz=640,                  # Tamaño de la imagen para el modelo (ajústalo si es necesario)
    conf=0.4,                   # Umbral de confianza para la detección
    iou=0.5,                    # Umbral de IOU para el tracking
    agnostic_nms=True,         # NMS agnóstico de clase
    device='0'               # Usar la GPU para acelerar el proceso (asegúrate de que tu modelo esté en CUDA)
)


