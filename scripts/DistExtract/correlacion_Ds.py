import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from skbio.stats.distance import mantel, DistanceMatrix
import os
import sys

def _correct_matrix(matrix):
    """
    Función auxiliar para limpiar y hacer simétrica una matriz.
    """
    matrix = np.nan_to_num(matrix)
    symmetric_matrix = (matrix + matrix.T) / 2
    np.fill_diagonal(symmetric_matrix, 0)
    return symmetric_matrix


def compare_distance_matrices(dist_matrix_path, output_dir):
    """
    Carga un conjunto de matrices de distancia y las compara estadísticamente
    utilizando el Test de Mantel por pares.
    """

    # --- 1. Cargar la matriz de distancias 3D ---
    try:
        dist_matrix_3d = np.load(dist_matrix_path)
        print(f"Archivo '{dist_matrix_path}' cargado correctamente.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta: {dist_matrix_path}")
        return

    # --- 2. Preparar matrices para el análisis ---
    num_matrices = dist_matrix_3d.shape[2]
    mantel_corr_matrix = np.zeros((num_matrices, num_matrices))
    mantel_p_matrix = np.zeros((num_matrices, num_matrices))
    matrix_labels = [f"d{i}" for i in range(num_matrices)]

    # --- 3. Realizar el Test de Mantel por pares ---
    print("\nIniciando el Test de Mantel por pares...")
    for i in range(num_matrices):
        for j in range(i, num_matrices):
            matrix1 = _correct_matrix(dist_matrix_3d[:, :, i])
            matrix2 = _correct_matrix(dist_matrix_3d[:, :, j])

            dm1 = DistanceMatrix(matrix1)
            dm2 = DistanceMatrix(matrix2)

            corr_coeff, p_value, _ = mantel(dm1, dm2)

            mantel_corr_matrix[i, j] = mantel_corr_matrix[j, i] = corr_coeff
            mantel_p_matrix[i, j] = mantel_p_matrix[j, i] = p_value

        print(f" -> Comparaciones para la matriz {matrix_labels[i]} completadas.")

    # --- 4. Visualizar los resultados en un heatmap ---
    print("\nGenerando el heatmap de correlaciones...")
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        mantel_corr_matrix,
        xticklabels=matrix_labels,
        yticklabels=matrix_labels,
        annot=True,
        cmap='coolwarm',
        fmt='.2f',
        linewidths=.5
    )
    plt.title("Correlación de Mantel entre Fórmulas de Distancia", fontsize=16)
    plt.xlabel("Fórmulas de Distancia", fontsize=12)
    plt.ylabel("Fórmulas de Distancia", fontsize=12)
    plt.tight_layout()

    # --- 5. Guardar y mostrar el gráfico ---
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = os.path.join(output_dir, "mantel_correlation_heatmap.png")
    plt.savefig(output_filename, dpi=300)
    print(f"\nHeatmap guardado en: {output_filename}")
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python correlacion_Ds.py <ruta_matriz_distancias> <directorio_salida>")
        sys.exit(1)

    dist_matrix_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    compare_distance_matrices(dist_matrix_path, output_dir)