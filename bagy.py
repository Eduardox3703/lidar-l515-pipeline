import pyrealsense2 as rs
import numpy as np
import pandas as pd

# Configurar el pipeline de RealSense
pipeline = rs.pipeline()
config = rs.config()

# Especificar la ruta del archivo .bag
file_path = r'C:\\Users\\Kitar\\OneDrive\\Documentos\\workspace\\new format\\local\\LIDAR\\calis\\file.bag'
config.enable_device_from_file(file_path)

# Iniciar el pipeline
pipeline.start(config)

# Leer un fotograma
frames = pipeline.wait_for_frames()
depth_frame = frames.get_depth_frame()
color_frame = frames.get_color_frame()

if not depth_frame or not color_frame:
    print("Error: No se pudo leer el fotograma.")
    exit()

# Obtener los datos de profundidad
depth_image = np.asanyarray(depth_frame.get_data())

# Obtener los parámetros intrínsecos de la cámara
intrinsic = depth_frame.profile.as_video_stream_profile().intrinsics

# Crear una nube de puntos
points = []
for y in range(depth_image.shape[0]):
    for x in range(depth_image.shape[1]):
        depth = depth_image[y, x]
        if depth > 0:  # Ignorar puntos con profundidad 0
            point = rs.rs2_deproject_pixel_to_point(intrinsic, [x, y], depth)
            points.append(point)

# Convertir a un DataFrame de pandas
df = pd.DataFrame(points, columns=['x', 'y', 'z'])

# Guardar en un archivo CSV
output_csv_path = r'C:\\Users\\Kitar\\OneDrive\\Documentos\\workspace\\new format\\local\\LIDAR\\calis\\file.csv'
df.to_csv(output_csv_path, index=False)
print(f"Datos guardados en {output_csv_path}")

# Detener el pipeline
pipeline.stop()