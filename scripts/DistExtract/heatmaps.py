import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def generate_heatmaps(dist_matrix_path, labels_path, output_dir):
    """
    Carga una matriz de distancias y etiquetas para generar y guardar
    múltiples heatmaps, uno por cada capa de la matriz.
    """
    
    # --- 1. Cargar los datos desde los archivos .npy ---
    try:
        dist_matrix = np.load(dist_matrix_path)
        labels = np.load(labels_path)
        print("Archivos de datos cargados correctamente.")
    except FileNotFoundError:
        print(f"Error: No se encontraron los archivos en las rutas especificadas: {dist_matrix_path}, {labels_path}")
        return

    # --- 2. Crear un directorio para guardar las imágenes ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Directorio '{output_dir}' creado para guardar las imágenes.")

    # --- 3. Iterar a través de cada capa y generar un heatmap ---
    num_heatmaps = dist_matrix.shape[2]
    
    print(f"Iniciando la generación de {num_heatmaps} heatmaps...")

    for i in range(num_heatmaps):
        plt.figure(figsize=(12, 10))
        current_slice = dist_matrix[:, :, i]
        
        sns.heatmap(
            current_slice,
            xticklabels=labels,
            yticklabels=labels,
            cmap='viridis'
        )

        plt.title(f"Heatmap - d {i}", fontsize=20)
        
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)

        plt.tight_layout()

        # --- 4. Guardar el heatmap como archivo .png ---
        file_name = os.path.join(output_dir, f"heatmap_d_{i}.png")

        plt.savefig(file_name, dpi=480)
        
        print(f" -> Guardado: {file_name}")

        plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python heatmaps.py <ruta_matriz_distancias> <ruta_etiquetas> <directorio_salida>")
        sys.exit(1)
    
    dist_matrix_path = sys.argv[1]
    labels_path = sys.argv[2]
    output_dir = sys.argv[3]
    
    generate_heatmaps(dist_matrix_path, labels_path, output_dir)