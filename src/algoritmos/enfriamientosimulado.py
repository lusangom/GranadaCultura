# algoritmo_enfriamientosimulado.py

import pandas as pd
import random
import math

MU = 0.3
PHI = 0.2
T_FINAL = 0.0001 # 10⁻⁴
RANDOM_SEED = 36
MAX_EVALUACIONES = 50000

class EnfriamientoSimulado:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max):
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.visitados = []
        random.seed(RANDOM_SEED)
        
    def calcular_fitness(self, nodo_origen, nodo_destino):
        tiempo_viaje = self.tiempos_df.loc[nodo_origen, str(nodo_destino)]
        tiempo_viaje = tiempo_viaje * 0.1
        beneficio = self.nodos_df.loc[nodo_destino, 'interes']
       
        fitness = beneficio - tiempo_viaje
        return fitness

    
   
    def generar_solucion_inicial_greedy(self):
        # Seleccionar el nodo inicial basado en el mayor interés
        nodo_inicial = self.nodos_df['interes'].idxmax()
        self.visitados.append(nodo_inicial)
        distancia_total = 0
        tiempo_actual = 0
        beneficio = 0
        
        tiempo_actual = self.nodos_df.loc[nodo_inicial, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_inicial, 'interes']
     
        while tiempo_actual <= self.tiempo_max:
            mejor_fitness = -float('inf')
            mejor_nodo = None
            
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = self.calcular_fitness(self.visitados[-1], i)
                    if fitness > mejor_fitness and tiempo_actual + self.tiempos_df.loc[self.visitados[-1], str(i)] + self.nodos_df.loc[i, 'tiempo_de_visita'] <= self.tiempo_max:
                        mejor_fitness = fitness
                        mejor_nodo = i
                        #distancia_total += self.distancias_df.loc[self.visitados[-1], str(i)]
                      
                        
            
            if mejor_nodo is None:
                break  # No se encontraron más nodos para visitar sin superar el tiempo máximo
            
            self.visitados.append(mejor_nodo)
            tiempo_actual += self.tiempos_df.loc[self.visitados[-2], str(mejor_nodo)] + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
            distancia_total += self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)] 
            beneficio += self.nodos_df.loc[mejor_nodo,'interes']
            
        # Devolver la lista de nodos visitados y el tiempo total
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def calcular_tiempo_distancia_total(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        distancia_total = 0 
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += self.tiempos_df.loc[solucion[i], str(solucion[i + 1])]
            distancia_total += self.distancias_df.loc[solucion[i], str(solucion[i + 1])]
        return tiempo_total, distancia_total

    def calcular_beneficio_total(self, solucion):
        beneficio_total = 0
        for i in range(len(solucion)):
            nodo = solucion[i]
            beneficio_total += self.nodos_df.loc[nodo, 'interes']
        return beneficio_total
    
    def generar_vecino(self, solucion):
        # Intentar encontrar un reemplazo válido que mantenga la solución dentro del tiempo máximo permitido
        for intento in range(1):  # Limitar el número de intentos para evitar un bucle infinito
        # Seleccionar un nodo aleatorio de la solución actual para ser reemplazado
            nodo_a_reemplazar = random.choice(solucion)

            # Lista de nodos posibles para el reemplazo, excluyendo los ya presentes en la solución
            nodos_posibles = [nodo for nodo in self.nodos_df.index if nodo not in solucion]

            # Si no hay nodos disponibles para el reemplazo, devolver la solución actual sin cambios
            if not nodos_posibles:
                return solucion

            # Seleccionar un nuevo nodo de los nodos posibles para reemplazar en la solución
            nuevo_nodo = random.choice(nodos_posibles)

            # Crear una copia de la solución actual para modificarla
            vecino_potencial = solucion[:]
            index_a_reemplazar = vecino_potencial.index(nodo_a_reemplazar)  # Encontrar el índice del nodo a reemplazar
            vecino_potencial[index_a_reemplazar] = nuevo_nodo  # Realizar el reemplazo

            # Calcular el tiempo total de la solución potencial
            tiempo_total = 0
            for i, nodo in enumerate(vecino_potencial):
                tiempo_total += self.nodos_df.loc[nodo, 'tiempo_de_visita']
                if i > 0:  # Añadir el tiempo de viaje entre nodos, excepto para el primer nodo
                    tiempo_total += self.tiempos_df.loc[vecino_potencial[i-1], str(nodo)]

            # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
            if tiempo_total <= self.tiempo_max:
                return vecino_potencial  # Devolver la solución propuesta si es válida
            
            intento=intento+1

        # Si no se encuentra un reemplazo válido después de varios intentos, devolver la solución original
        return solucion
    
    def aplicar_enfriamiento_simulado(self):
        self.visitados, tiempo_actual, distancia_total, beneficio_actual = self.generar_solucion_inicial_greedy()
        
        t_actual = (MU * beneficio_actual) / (-math.log(PHI))
        beta = 0.1  # Factor de enfriamiento

        iteracion = 0
        while t_actual > T_FINAL and iteracion < MAX_EVALUACIONES:
            vecino = self.generar_vecino(self.visitados)
            beneficio_vecino = self.calcular_beneficio_total(vecino)
            delta_beneficio = beneficio_vecino - beneficio_actual
            if delta_beneficio > 0 or random.random() < math.exp(delta_beneficio / t_actual):
                self.visitados = vecino
                beneficio_actual = beneficio_vecino
                tiempo_actual, distancia_total = self.calcular_tiempo_distancia_total(self.visitados)
            t_actual = t_actual / (1 + beta * t_actual)
            iteracion += 1
        
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual