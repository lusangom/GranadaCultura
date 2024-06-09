import json
import pandas as pd
import time
from datos import lectura_datos
from algoritmos import greedy, grasp, enfriamientosimulado, algoritmogenetico, algoritmomemetico


def leer_configuracion_json(ruta_archivo):
    with open(ruta_archivo, 'r') as archivo:
        config = json.load(archivo)
    return config

def escribir_resultados_a_archivo(ruta_archivo, resultados):
    with open(ruta_archivo, 'w') as archivo:
        for resultado in resultados:
            archivo.write(resultado + '\n')
            
def escribir_resultados_a_archivo_df(ruta_archivo, resultados_df):
    resultados_df.index.name = 'RUTA:'
    resultados_df.to_csv(ruta_archivo, index=True)

def mostrar_resultados_a_lista(algoritmo, ejecucion, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica, tiempo_ejecucion):
    resultados = [
        f"\nAlgoritmo: {algoritmo}",
        f"Ejecucion nº: {ejecucion}",
        f"Tiempo ejecucion algoritmo: {tiempo_ejecucion} segundos",
        f"Ruta solución: {ruta_solucion}",
        f"Tiempo total: {tiempo_total}",
        f"Distancia total: {distancia_total}",
        f"Interes total: {beneficio}",
        f"Margen: {tiempo_max - tiempo_total}",
        f"Ruta ciclica: {es_ciclica}"
    ]
    if es_ciclica:
        if len(ruta_solucion) > 1:
            resultados.append(f"Porcentaje interes: {(beneficio/(len(ruta_solucion)-1))*10}")
            resultados.append(f"Numero de nodos visitados: {len(ruta_solucion)-1}")
        else:
            resultados.append(f"Porcentaje interes: {(beneficio/len(ruta_solucion))*10}")
            resultados.append(f"Numero de nodos visitados: {len(ruta_solucion)}")
    else:
        resultados.append(f"Numero de nodos visitados: {len(ruta_solucion)}")
        resultados.append(f"Porcentaje interes: {(beneficio/len(ruta_solucion))*10}")
        
    
    return resultados

def resultados_a_tabla(edad, tamaño_bbdd, algoritmo, ejecucion, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, es_ciclica, tiempo_ejecucion):
    numero_pois_visitados = len(ruta_solucion) - 1 if es_ciclica else len(ruta_solucion)
    porcentaje_interes = (beneficio / numero_pois_visitados) * 10
    
    # Creamos un DataFrame con una sola fila con los resultados
    resultados_df = pd.DataFrame([{
        "EDAD": edad,
        "TAMAÑO BBDD": tamaño_bbdd,
        "TIEMPO MAX": tiempo_max,
        "ALGORITMO": algoritmo,
        "EJECUCION Nº": ejecucion,
        "RUTA CICLICA": es_ciclica,
        "POIS VISITADOS": ruta_solucion,
        "INTERÉS": beneficio,
        "DISTANCIA TOTAL": distancia_total,
        "TIEMPO RUTA": tiempo_total,
        "MARGEN": tiempo_max - tiempo_total,
        "NUMERO DE POIS VISITADOS": numero_pois_visitados,
        "PORCENTAJE INTERES": porcentaje_interes,
        "TIEMPO EJECUCION ALGORITMO": tiempo_ejecucion
    }])
    
    
    return resultados_df

def main(configuracion):
    tamaño_db = configuracion["tamaño_db"]
    prefijo_ruta = 'data/'
    tam_ruta = f'_{tamaño_db}'
    ruta_archivo_nodos = prefijo_ruta + 'pois' + tam_ruta + '.csv'
    ruta_archivo_distancias = prefijo_ruta + 'distancias'+ tam_ruta + '.csv'
    ruta_archivo_tiempos = prefijo_ruta + 'tiempos' + tam_ruta + '.csv'
    ruta_archivo_edad_velocidad = 'data/edadvelocidad.csv'
    
    edad_velocidad_df = pd.read_csv(ruta_archivo_edad_velocidad)
    edad = configuracion["edad"]
    velocidad = edad_velocidad_df[(edad_velocidad_df['Edad_inicio'] <= edad) & (edad_velocidad_df['Edad_fin'] >= edad)]['Velocidad(m/min)'].iloc[0]
    tiempo_max = configuracion["tiempo_maximo"]
    
    config_genetico = configuracion["configuracion_algoritmos"]["genetico"]
    config_memetico = configuracion["configuracion_algoritmos"]["memetico"]
    config_enfriamiento_simulado = configuracion["configuracion_algoritmos"]["enfriamiento_simulado"]
    config_grasp = configuracion["configuracion_algoritmos"]["grasp"]
    
    
    datos = lectura_datos.Datos(ruta_archivo_nodos, ruta_archivo_distancias, ruta_archivo_tiempos)
    nodos_df, distancias_df, tiempos_df = datos.cargar_nodos(), datos.cargar_distancias(), datos.cargar_tiempos()
      
    
    resultados_fichero = []
    resultados_tabla = pd.DataFrame()
    algoritmos = {
        1: "Greedy",
        2: "GRASP",
        3: "Enfriamiento Simulado",
        4: "Algoritmo Genetico Estacionario",
        5: "Algoritmo Memetico"
    }

    for i in range(configuracion["numero_ejecuciones"]):
        print("ejecucion: ",i)
        # Ejecutamos los algoritmos
        for alg_id in configuracion["algoritmos"]:
            if alg_id == 1 or alg_id == 6: #greedy
                if(configuracion["es_ciclica"]):
                    alg_greedy = greedy.Greedy(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad) 
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_greedy.aplicar_greedy_ciclico(nodo_ciclico=configuracion["nodo_origen"])
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                else:
                    alg_greedy = greedy.Greedy(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad) 
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_greedy.aplicar_greedy()
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
            if alg_id == 2 or alg_id == 6: #grasp
                if(configuracion["es_ciclica"]):
                    alg_grasp = grasp.Grasp(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    MAX_ITERACIONES=config_grasp["MAX_ITERACIONES"],
                    MAX_ITERACIONES_BL=config_grasp["MAX_ITERACIONES_BL"],
                    #RANDOM_SEED=config_grasp["RANDOM_SEED"],
                    cantidad_candidatos=config_grasp["cantidad_candidatos"]
                    )
                    tiempo_ini = time.time() 
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_grasp.aplicar_grasp_ciclico(nodo_ciclico=configuracion["nodo_origen"])
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
                else:
                    alg_grasp = grasp.Grasp(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    MAX_ITERACIONES=config_grasp["MAX_ITERACIONES"],
                    MAX_ITERACIONES_BL=config_grasp["MAX_ITERACIONES_BL"],
                    #RANDOM_SEED=config_grasp["RANDOM_SEED"],
                    cantidad_candidatos=config_grasp["cantidad_candidatos"]
                    )
                    alg_grasp = grasp.Grasp(nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad=velocidad)
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_grasp.aplicar_grasp()
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                
            if alg_id == 3 or alg_id == 6: #es
                if(configuracion["es_ciclica"]):
                    alg_es = enfriamientosimulado.EnfriamientoSimulado(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    MU=config_enfriamiento_simulado["MU"],
                    PHI=config_enfriamiento_simulado["PHI"],
                    T_FINAL=config_enfriamiento_simulado["T_FINAL"],
                    #RANDOM_SEED=config_enfriamiento_simulado["RANDOM_SEED"],
                    MAX_EVALUACIONES=config_enfriamiento_simulado["MAX_EVALUACIONES"],
                    BETA=config_enfriamiento_simulado["BETA"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_es.aplicar_enfriamiento_simulado_ciclico(nodo_ciclico=configuracion["nodo_origen"])
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
                else:
                    alg_es = enfriamientosimulado.EnfriamientoSimulado(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    MU=config_enfriamiento_simulado["MU"],
                    PHI=config_enfriamiento_simulado["PHI"],
                    T_FINAL=config_enfriamiento_simulado["T_FINAL"],
                    #RANDOM_SEED=config_enfriamiento_simulado["RANDOM_SEED"],
                    MAX_EVALUACIONES=config_enfriamiento_simulado["MAX_EVALUACIONES"],
                    BETA=config_enfriamiento_simulado["BETA"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_es.aplicar_enfriamiento_simulado()
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                
            if alg_id == 4 or alg_id == 6: #genetico
                if configuracion["es_ciclica"]:
                    alg_ag = algoritmogenetico.AlgoritmoGeneticoEstacionario(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    poblacion_size=config_genetico["poblacion_size"],
                    #RANDOM_SEED=config_genetico["RANDOM_SEED"],
                    intentos_cruce=config_genetico["intentos_cruce"],
                    max_iteraciones=config_genetico["max_iteraciones"],
                    max_intentos_poblacion = config_genetico["max_intentos_poblacion"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_ag.aplicar_algoritmo_genetico_ciclico(nodo_ciclico=configuracion["nodo_origen"])
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
                else:
                    alg_ag = algoritmogenetico.AlgoritmoGeneticoEstacionario(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    poblacion_size=config_genetico["poblacion_size"],
                    #RANDOM_SEED=config_genetico["RANDOM_SEED"],
                    intentos_cruce=config_genetico["intentos_cruce"],
                    max_iteraciones=config_genetico["max_iteraciones"],
                    max_intentos_poblacion = config_genetico["max_intentos_poblacion"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_ag.aplicar_algoritmo_genetico()
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
            if alg_id == 5 or alg_id == 6: #memetico
                if(configuracion["es_ciclica"]):
                    alg_mm = algoritmomemetico.AlgoritmoMemetico(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    poblacion_size=config_memetico["poblacion_size"],
                    #RANDOM_SEED=config_memetico["RANDOM_SEED"],
                    intentos_cruce=config_memetico["intentos_cruce"],
                    max_iteraciones=config_memetico["max_iteraciones"],
                    max_iteraciones_bl=config_memetico["max_iteraciones_bl"],
                    tipo_hibridacion=config_memetico["tipo_hibridacion"],
                    aplica_bl = config_memetico["aplica_bl"],
                    porcentaje_best = config_memetico["porcentaje_best"],
                    max_intentos_poblacion = config_memetico["max_intentos_poblacion"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_mm.aplicar_algoritmo_memetico_ciclico(nodo_ciclico=configuracion["nodo_origen"])
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                    
                else:
                    alg_mm = algoritmomemetico.AlgoritmoMemetico(
                    nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad,
                    poblacion_size=config_memetico["poblacion_size"],
                    #RANDOM_SEED=config_memetico["RANDOM_SEED"],
                    intentos_cruce=config_memetico["intentos_cruce"],
                    max_iteraciones=config_memetico["max_iteraciones"],
                    max_iteraciones_bl=config_memetico["max_iteraciones_bl"],
                    tipo_hibridacion=config_memetico["tipo_hibridacion"],
                    aplica_bl = config_memetico["aplica_bl"],
                    porcentaje_best = config_memetico["porcentaje_best"],
                    max_intentos_poblacion = config_memetico["max_intentos_poblacion"]
                    )
                    tiempo_ini = time.time()
                    ruta_solucion, tiempo_total, distancia_total, beneficio = alg_mm.aplicar_algoritmo_memetico()
                    tiempo_fin = time.time()
                    tiempo_ejecucion = tiempo_fin - tiempo_ini
                    resultado_fichero = mostrar_resultados_a_lista(algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_fichero.extend(resultado_fichero)
                    resultado_tabla = resultados_a_tabla(edad, tamaño_db, algoritmos[alg_id], i+1, ruta_solucion, tiempo_total, distancia_total, beneficio, tiempo_max, configuracion["es_ciclica"], tiempo_ejecucion)
                    resultados_tabla = pd.concat([resultados_tabla,resultado_tabla], ignore_index=True)
                 
                    
    
    escribir_resultados_a_archivo('resultados.txt', resultados_fichero)
    escribir_resultados_a_archivo_df('tabla.csv', resultados_tabla)

if __name__ == "__main__":
    config = leer_configuracion_json('configuracion.json')
    main(config)
