import folium
import pandas as pd
import osmnx as ox
import ast
from datos import lectura_datos
from datos import visualizacion
import argparse  # Importa argparse

def main(archivo_rutas, archivo_html):
    # Leer los archivos correspondientes 
    ruta_archivo_nodos = 'data/pois_158.csv'
    ruta_archivo_distancias = 'data/distancias_158.csv'
    ruta_archivo_tiempos = 'data/tiempos_158.csv'
   
    
    # Cargar datos
    datos = lectura_datos.Datos(ruta_archivo_nodos, ruta_archivo_distancias, ruta_archivo_tiempos)
    nodos_df = datos.cargar_nodos()
    rutas_df = pd.read_csv(archivo_rutas)
    
    #print(nodos_df.columns)
    vista = visualizacion.Visualizacion(nodos_df)
    
    vista.visualizar_varias_rutas(nodos_df, rutas_df, archivo_html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizar rutas en un mapa interactivo.")
    parser.add_argument('--archivo_rutas', type=str, help='Archivo CSV con las rutas solución.')
    parser.add_argument('--archivo_html', type=str, help='Archivo HTML para guardar el mapa interactivo.')
    
    args = parser.parse_args()
    main(args.archivo_rutas, args.archivo_html)