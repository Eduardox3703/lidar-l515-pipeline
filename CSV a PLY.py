import open3d as o3d
import numpy as np
import csv

# Ruta al archivo CSV
csv_file = 'output.csv'  # Cambia esto por la ruta de tu archivo CSV

# Lista para almacenar los puntos
points = []

# Leer el archivo CSV
with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Convertir cada fila a un array de floats
        point = [float(coord) for coord in row]
        points.append(point)

# Convertir la lista de puntos a un array de numpy
points = np.array(points)

# Crear un objeto PointCloud de Open3D
point_cloud = o3d.geometry.PointCloud()
point_cloud.points = o3d.utility.Vector3dVector(points)

# Guardar como archivo .ply
o3d.io.write_point_cloud("coordenadas.ply", point_cloud)

print(f"Archivo 'coordenadas.ply' guardado correctamente con {len(points)} puntos.")