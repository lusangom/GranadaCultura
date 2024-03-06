from datos import lectura_datos
from algoritmos import greedy 
from datos import visualizacion

def main():
    ruta_archivo_nodos = 'data/pois_158.csv'
    ruta_archivo_distancias = 'data/distancias_158.csv'
    ruta_archivo_tiempos = 'data/tiempos_158.csv'
    
    datos = lectura_datos.Datos(ruta_archivo_nodos, ruta_archivo_distancias, ruta_archivo_tiempos)
    nodos_df = datos.cargar_nodos()
    distancias_df = datos.cargar_distancias()
    tiempos_df = datos.cargar_tiempos()
    
    
    if nodos_df is not None and distancias_df is not None:
        tiempo_max = int(input("Introduce el tiempo máximo: "))
        print("Tiempo máximo:", tiempo_max)
        
        # Crear una instancia de AlgoritmoGreedy y aplicar el algoritmo
        alg_greedy = greedy.Greedy(nodos_df, distancias_df, tiempos_df, tiempo_max)
        ruta_solucion, tiempo_total, distancia_total, beneficio = alg_greedy.aplicar_greedy()
        print("Ruta solución:", ruta_solucion)
        print("Tiempo total:", tiempo_total)   
        print("Distancia total:", distancia_total) 
        print("Interes total:", beneficio) 
        print("Numero de nodos visitados:", len(ruta_solucion))
        print("Margen:",tiempo_max-tiempo_total)
        
       
        vista = visualizacion.Visualizacion(nodos_df, ruta_solucion)
        
        # Visualizar la ruta en el mapa, si nodos_df no es None
        if nodos_df is not None:
            #mapa_folium = vista.visualizar_ruta_en_mapa_folium(nodos_df)
            #mapa_explore = vista.visualizar_ruta_en_mapa_explore(nodos_df)
            vista.exportar_indicaciones_ruta_v1('indicaciones_ruta.txt')


            #mapa_folium.save('ruta_solucion_folium.html')  # Guarda el mapa en un archivo HTML
            #mapa_explore.save('ruta_solucion_explore.html')     
   
if __name__ == "__main__":
    main()
