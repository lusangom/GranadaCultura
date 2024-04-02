from datos import lectura_datos
from algoritmos import greedy, grasp, enfriamientosimulado, algoritmogenetico, algoritmomemetico
from datos import visualizacion
import pandas as pd


def mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica):
        print("Ruta solución:", ruta_solucion)
        print("Tiempo total:", tiempo_total)   
        print("Distancia total:", distancia_total) 
        print("Interes total:", beneficio) 
        print("Margen:", tiempo_max - tiempo_total)
        if(es_ciclica):
            
            if(len(ruta_solucion)>1):
                print("Porcentaje interes: ",(beneficio/(len(ruta_solucion)-1))*10)
                print("Numero de nodos visitados:", len(ruta_solucion)-1)
            else:
                print("Porcentaje interes: ",(beneficio/(len(ruta_solucion)))*10)
                print("Numero de nodos visitados:", len(ruta_solucion))
           
        else:
            print("Numero de nodos visitados:", len(ruta_solucion)-1)
            print("Porcentaje interes: ",(beneficio/len(ruta_solucion))*10)
            
        print("Ruta ciclica:", es_ciclica)

def main():
    ruta_archivo_nodos = 'data/pois_158.csv'
    ruta_archivo_distancias = 'data/distancias_158.csv'
    ruta_archivo_tiempos = 'data/tiempos_158.csv'
    ruta_archivo_edad_velocidad = 'data/edadvelocidad.csv'
    
    # Leer el archivo edad_velocidad.csv
    edad_velocidad_df = pd.read_csv(ruta_archivo_edad_velocidad)
    
    # Solicitar la edad al usuario
    edad = int(input("Introduce la edad (entre 0 y 99): "))
    
    # Obtener la velocidad correspondiente a la edad introducida
    velocidad = edad_velocidad_df[(edad_velocidad_df['Edad_inicio'] <= edad) & (edad_velocidad_df['Edad_fin'] >= edad)]['Velocidad(m/min)'].iloc[0]
    print("Velocidad correspondiente a la edad:", velocidad)
    
    # Cargar datos
    datos = lectura_datos.Datos(ruta_archivo_nodos, ruta_archivo_distancias, ruta_archivo_tiempos)
    nodos_df = datos.cargar_nodos()
    distancias_df = datos.cargar_distancias()
    tiempos_df = datos.cargar_tiempos()

    tiempo_max = int(input("Introduce el tiempo máximo: "))
    print("Tiempo máximo:", tiempo_max)
    alg_greedy = greedy.Greedy(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad) 
    alg_grasp = grasp.Grasp(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad)
    alg_es = enfriamientosimulado.EnfriamientoSimulado(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad)
    alg_ag = algoritmogenetico.AlgoritmoGeneticoEstacionario(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad)
    alg_mm = algoritmomemetico.AlgoritmoMemetico(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad)
        
    print("¿Qué algoritmo(s) deseas ejecutar?")
    print("1. Greedy")
    print("2. GRASP")
    print("3. Enfriamiento Simulado")
    print("4. Algoritmo Genético")
    print("5. Algoritmo Memético")
    print("6. Todos")
    eleccion = input("Introduce el número correspondiente a tu elección, separados por coma si son varios (ejemplo: 1,2): ")

    elecciones = [int(e.strip()) for e in eleccion.split(",")]

    es_ciclica = input("¿Deseas que la ruta sea cíclica? (si/no): ").strip().lower() == 'si'
    nodo_origen = None
    if es_ciclica:
        print("Lista de POIs:")
        for nodo, row in nodos_df.iterrows():
            print(f"{nodo}: {row['name']}")
        nodo_origen = int(input("Selecciona el número de nodo para el punto de origen: "))

    # Ejecutar los algoritmos seleccionados
    if 1 in elecciones or 6 in elecciones: #greedy
        if(es_ciclica):
            print("ALGORITMO GREEDY")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_greedy.aplicar_greedy_ciclico(nodo_ciclico=nodo_origen)
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        else:
            print("ALGORITMO GREEDY")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_greedy.aplicar_greedy()
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
    if 2 in elecciones or 6 in elecciones: #grasp
       
        if(es_ciclica):
            print("ALGORITMO GRASP")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_grasp.aplicar_grasp_ciclico(nodo_ciclico=nodo_origen)
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        else:
            print("ALGORITMO GRASP")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_grasp.aplicar_grasp()
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        
    if 3 in elecciones or 6 in elecciones: #es
        
        if(es_ciclica):
            print("ALGORITMO ENFRIAMIENTO SIMULADO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_es.aplicar_enfriamiento_simulado_ciclico(nodo_ciclico=nodo_origen)
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        else:
            print("ALGORITMO ENFRIAMIENTO SIMULADO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_es.aplicar_enfriamiento_simulado()
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
      
    if 4 in elecciones or 6 in elecciones: #genetico
        if(es_ciclica):
            print("ALGORITMO GENETICO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_ag.aplicar_algoritmo_genetico_ciclico(nodo_ciclico=nodo_origen)
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        else:
            print("ALGORITMO GENETICO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_ag.aplicar_algoritmo_genetico()
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
    if 5 in elecciones or 6 in elecciones: #memetico
        if(es_ciclica):
            print("ALGORITMO MEMETICO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_mm.aplicar_algoritmo_memetico_ciclico(nodo_ciclico=nodo_origen)
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
        else:
            print("ALGORITMO MEMETICO")
            ruta_solucion, tiempo_total, distancia_total, beneficio = alg_mm.aplicar_algoritmo_memetico()
            mostrar_resultados(ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica)
      
    #vista = visualizacion.Visualizacion(nodos_df, ruta_solucion)
        #if nodos_df is not None:
        

            #mapa_folium = vista.visualizar_ruta_en_mapa_folium(nodos_df)
            #mapa_explore = vista.visualizar_ruta_en_mapa_explore(nodos_df)
            #vista.exportar_indicaciones_ruta_v1('indicaciones_ruta.txt')


            #mapa_folium.save('ruta_solucion_folium.html')  # Guarda el mapa en un archivo HTML
            #mapa_explore.save('ruta_solucion_explore.html')   



if __name__ == "__main__":
    main()
