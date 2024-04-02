# algoritmo_enfriamientosimulado.py

import pandas as pd
import random
import math
import numpy as np

MU = 0.3
PHI = 0.2
T_FINAL = 0.0001 # 10⁻⁴
RANDOM_SEED = 36
MAX_EVALUACIONES = 50000
BETA = 0.2 

class EnfriamientoSimulado:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad):
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.velocidad = velocidad
        self.visitados = []
        random.seed(RANDOM_SEED)
        
    def calcular_fitness(self, nodo_origen, nodo_destino):
        tiempo_viaje = (self.distancias_df.loc[nodo_origen, str(nodo_destino)])/self.velocidad
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
                    if fitness > mejor_fitness and tiempo_actual + (self.distancias_df.loc[self.visitados[-1], str(i)])/self.velocidad + self.nodos_df.loc[i, 'tiempo_de_visita'] <= self.tiempo_max:
                        mejor_fitness = fitness
                        mejor_nodo = i
                        #distancia_total += self.distancias_df.loc[self.visitados[-1], str(i)]
                      
                        
            
            if mejor_nodo is None:
                break  # No se encontraron más nodos para visitar sin superar el tiempo máximo
            
            self.visitados.append(mejor_nodo)
            tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)])/self.velocidad + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
            distancia_total += self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)] 
            beneficio += self.nodos_df.loc[mejor_nodo,'interes']
            
        # Devolver la lista de nodos visitados y el tiempo total
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def generar_solucion_inicial_greedy_ciclico(self, nodo_ciclico):
            self.visitados = [nodo_ciclico]
            distancia_total = 0
            tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
            beneficio = self.nodos_df.loc[nodo_ciclico, 'interes']

            while True:
                mejor_fitness = -float('inf')
                mejor_nodo = None
                
                for i, nodo in self.nodos_df.iterrows():
                    if i not in self.visitados and i != nodo_ciclico:
                        tiempo_vuelta = (self.distancias_df.loc[i, str(nodo_ciclico)])/self.velocidad               # Asegurarse de tener en cuenta el tiempo de visita en el nodo final
                        tiempo_necesario = tiempo_actual + self.nodos_df.loc[i, 'tiempo_de_visita'] + tiempo_vuelta + self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
                        
                        if tiempo_necesario <= self.tiempo_max:
                            fitness = self.calcular_fitness(self.visitados[-1], i)
                            if fitness > mejor_fitness:
                                mejor_fitness = fitness
                                mejor_nodo = i
                
                if mejor_nodo is None:
                    break

                tiempo_viaje = (self.distancias_df.loc[self.visitados[-1], str(mejor_nodo)])/self.velocidad
                tiempo_actual += tiempo_viaje + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
                distancia_total += self.distancias_df.loc[self.visitados[-1], str(mejor_nodo)]
                beneficio += self.nodos_df.loc[mejor_nodo, 'interes']
                self.visitados.append(mejor_nodo)

            if tiempo_actual + (self.distancias_df.loc[self.visitados[-1], str(nodo_ciclico)])/self.velocidad <= self.tiempo_max:
                self.visitados.append(nodo_ciclico)
                distancia_total += self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)]
                tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)])/self.velocidad
                # No se añade beneficio porque el nodo cíclico ya fue considerado al inicio

            return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def calcular_tiempo_total(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += (self.distancias_df.loc[solucion[i], str(solucion[i + 1])])/self.velocidad
            
        return tiempo_total

    def calcular_distancia_total(self, solucion):   
        distancia_total = 0 
        for i in range(len(solucion) - 1):
            distancia_total += self.distancias_df.loc[solucion[i], str(solucion[i + 1])]
        return distancia_total

    def calcular_beneficio_total(self, solucion):
        beneficio_total = 0
        for i in range(len(solucion)):
            nodo = solucion[i]
            beneficio_total += self.nodos_df.loc[nodo, 'interes']
        return beneficio_total
    
    
    def generar_vecino(self, solucion):
        
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

        

        tiempo_total = self.calcular_tiempo_total(vecino_potencial)
    

            # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            #print("En solucion original:",nodo_a_reemplazar)
            #print("Insertamos:",nuevo_nodo)
            #print("En posicion:",index_a_reemplazar)
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
           
    
        return solucion
    
    def generar_vecino_ciclico(self, solucion):
        # Asegurarse de que hay al menos tres nodos en la solución para excluir el primero y el último
        if len(solucion) <= 3:
            return solucion  # Devolver la solución actual sin cambios si no es posible excluir ambos

        # Seleccionar un nodo aleatorio de la solución actual para ser reemplazado, excluyendo el primero y el último
        nodo_a_reemplazar = random.choice(solucion[1:-1])

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
        tiempo_total = self.calcular_tiempo_total(vecino_potencial)

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            return vecino_potencial  # Devolver la solución propuesta si es válida

        return solucion

    
    def aplicar_enfriamiento_simulado(self):
        self.visitados, tiempo_actual, distancia_total, beneficio_actual = self.generar_solucion_inicial_greedy()
        
        t_actual = (MU * beneficio_actual) / (-math.log(PHI))
        
        

        iteracion = 0
        while t_actual > T_FINAL and iteracion < MAX_EVALUACIONES:
            vecino = self.generar_vecino(self.visitados)
            beneficio_vecino = self.calcular_beneficio_total(vecino)
            tmp_act = self.calcular_tiempo_total(self.visitados)
            tmp_vec = self.calcular_tiempo_total(vecino)
            tmp_act = tmp_act*0.1
            tmp_vec = tmp_vec*0.1
            delta_beneficio = (beneficio_vecino - tmp_vec)  - (beneficio_actual - tmp_act)
            if delta_beneficio > 0 or np.random.rand() < math.exp(delta_beneficio / t_actual):
                #print("HACEMOS CAMBIO")
                self.visitados = vecino
                beneficio_actual = beneficio_vecino
                tiempo_actual = self.calcular_tiempo_total(self.visitados)
                distancia_total = self.calcular_distancia_total(self.visitados)
            #print(t_actual)    
            t_actual = t_actual / (1 + BETA * t_actual)
            iteracion += 1
        
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
    
    
    def aplicar_enfriamiento_simulado_ciclico(self, nodo_ciclico):
        self.visitados, tiempo_actual, distancia_total, beneficio_actual = self.generar_solucion_inicial_greedy_ciclico(nodo_ciclico=nodo_ciclico)
        
        t_actual = (MU * beneficio_actual) / (-math.log(PHI))
        
        

        iteracion = 0
        while t_actual > T_FINAL and iteracion < MAX_EVALUACIONES:
            vecino = self.generar_vecino_ciclico(self.visitados)
            beneficio_vecino = self.calcular_beneficio_total(vecino)
            tmp_act = self.calcular_tiempo_total(self.visitados)
            tmp_vec = self.calcular_tiempo_total(vecino)
            tmp_act = tmp_act*0.1
            tmp_vec = tmp_vec*0.1
            delta_beneficio = (beneficio_vecino - tmp_vec)  - (beneficio_actual - tmp_act)
            if delta_beneficio > 0 or np.random.rand() < math.exp(delta_beneficio / t_actual):
                #print("HACEMOS CAMBIO")
                self.visitados = vecino
                beneficio_actual = beneficio_vecino
                tiempo_actual = self.calcular_tiempo_total(self.visitados)
                distancia_total = self.calcular_distancia_total(self.visitados)
            #print(t_actual)    
            t_actual = t_actual / (1 + BETA * t_actual)
            iteracion += 1
        
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual