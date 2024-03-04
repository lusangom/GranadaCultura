from datos import lectura_datos
from algoritmos import greedy 
from datos import visualizacion

def main():
    ruta_archivo_nodos = 'data/pois_5.csv'
    ruta_archivo_distancias = 'data/distancias_5.csv'
    ruta_archivo_tiempos = 'data/tiempos_5.csv'
    
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
        
       
        vista = visualizacion.Visualizacion(nodos_df, ruta_solucion)
        #nodos_df = vista.cargar_nodos()
        
        # Visualizar la ruta en el mapa, si nodos_df no es None
        if nodos_df is not None:
            mapa = vista.visualizar_ruta_en_mapa(nodos_df)
            print('guardo')
            mapa.save('ruta_solucion.html')  # Guarda el mapa en un archivo HTML
                
   
if __name__ == "__main__":
    main()
