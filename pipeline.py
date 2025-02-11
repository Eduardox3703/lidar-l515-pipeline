import pyrealsense2 as rs
import numpy as np
import pandas as pd
import open3d as o3d
import boto3
import csv

import os

# Configuración de AWS S3
s3 = boto3.client('s3')  # Usa el archivo ~/.aws/credentials o variables de entorno
bucket_name = 'bucketdinamita'  # Nombre de tu bucket

# Función para subir archivos a S3
def upload_to_s3(file_path, s3_key):
    try:
        with open(file_path, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, s3_key)
        print(f"Archivo {file_path} subido a S3 en {bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error al subir {file_path} a S3: {e}")

# Función para iniciar el pipeline y obtener los fotogramas
def get_frames(bag_file_path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(bag_file_path)
    pipeline.start(config)
    
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    
    if not depth_frame or not color_frame:
        print("Error: No se pudo leer el fotograma.")
        pipeline.stop()
        exit()
    
    return pipeline, depth_frame, color_frame

# Función para convertir los datos de profundidad a una nube de puntos
def depth_to_point_cloud(depth_frame):
    depth_image = np.asanyarray(depth_frame.get_data())
    intrinsic = depth_frame.profile.as_video_stream_profile().intrinsics
    
    points = []
    for y in range(depth_image.shape[0]):
        for x in range(depth_image.shape[1]):
            depth = depth_image[y, x]
            if depth > 0:  # Ignorar puntos con profundidad 0
                point = rs.rs2_deproject_pixel_to_point(intrinsic, [x, y], depth)
                points.append(point)
    
    return points

# Función para guardar los puntos en un archivo CSV
def save_points_to_csv(points, output_csv_path):
    df = pd.DataFrame(points, columns=['x', 'y', 'z'])
    df.to_csv(output_csv_path, index=False)
    print(f"Datos guardados en {output_csv_path}")

# Función para convertir CSV a PLY
def csv_to_ply(input_csv_path, output_ply_path):
    points = []
    with open(input_csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Omitir la primera fila (encabezados)
        for row in reader:
            point = [float(coord) for coord in row]
            points.append(point)
    
    points = np.array(points)
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)
    o3d.io.write_point_cloud(output_ply_path, point_cloud)
    print(f"Archivo '{output_ply_path}' guardado correctamente con {len(points)} puntos.")

# Ruta del archivo .bag
bag_file_path = r'C:\\Users\\eduar\\Desktop\\Lidar\\20250208_223958.bag'

# Obtener los fotogramas
pipeline, depth_frame, color_frame = get_frames(bag_file_path)

# Convertir los datos de profundidad a una nube de puntos
points = depth_to_point_cloud(depth_frame)

# Guardar los puntos en un archivo CSV
output_csv_path = r'C:\\Users\\eduar\\Desktop\\Lidar\\output.csv'
save_points_to_csv(points, output_csv_path)

# Subir el archivo CSV a S3
s3_csv_key = 'CSV y PLY/output.csv'  # Ruta dentro del bucket
upload_to_s3(output_csv_path, s3_csv_key)

# Detener el pipeline
pipeline.stop()

# Convertir CSV a PLY
ply_file_path = r'C:\\Users\\eduar\\Desktop\\Lidar\\coordenadas.ply'
csv_to_ply(output_csv_path, ply_file_path)

# Subir el archivo PLY a S3
s3_ply_key = 'CSV y PLY/coordenadas.ply'  # Ruta dentro del bucket
upload_to_s3(ply_file_path, s3_ply_key)