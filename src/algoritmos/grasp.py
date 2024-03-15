# algoritmo_grasp.py

import pandas as pd
import math
import random

class Grasp:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max):
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.visitados = []
        
    def calcular_fitness(self, nodo_origen, nodo_destino):
        tiempo_viaje = self.tiempos_df.loc[nodo_origen, str(nodo_destino)]
        tiempo_viaje = tiempo_viaje * 0.1
        beneficio = self.nodos_df.loc[nodo_destino, 'interes']
       
        fitness = beneficio - tiempo_viaje
        return fitness

    
   
    def aplicar_grasp(self, max_iteraciones=300):
        # Seleccionar el nodo inicial basado en el mayor interés
        nodo_inicial = self.nodos_df['interes'].idxmax()
        self.visitados.append(nodo_inicial)
        distancia_total = 0
        tiempo_actual = 0
        beneficio = 0
        iter = 0
        
        tiempo_actual = self.nodos_df.loc[nodo_inicial, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_inicial, 'interes']
     
        # Establecemos semilla para poder repetir el proceso
        random.seed(36)
     
        while tiempo_actual <= self.tiempo_max and iter < max_iteraciones:
            
            #Calculamos el fitness de todos los nodos
            fitness_nodos = []
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = self.calcular_fitness(self.visitados[-1], i)
                    fitness_nodos.append((fitness,i))
                    
            # Ordenar los nodos por fitness y obtenemos la lista de candidatos
            fitness_nodos.sort(reverse=True)
            candidatos = fitness_nodos[:max(1, math.ceil(len(fitness_nodos) * 0.05))]
            
            
            
            #print("Candidatos:", candidatos)   
            #print("Tamanio", str(math.ceil(len(fitness_nodos) * 0.05)))
            #print("Iteracion:", str(iter))
            
           

            # Iterar sobre la lista de candidatos
            candidatos_fallidos = []
            while candidatos:
                # Seleccionar un nodo aleatorio de la lista de candidatos
                fitness, nodo = random.choice(candidatos)
                
                print("CANDIDATO ES:", str(nodo))
                
                tiempo_viaje = self.tiempos_df.loc[self.visitados[-1], str(nodo)]
                tiempo_visita = self.nodos_df.loc[nodo, 'tiempo_de_visita']
                tiempo_total = tiempo_actual + tiempo_viaje + tiempo_visita
                distancia = self.distancias_df.loc[self.visitados[-1],str(nodo)]
                
                #print("tiempo viaje:", str(tiempo_viaje)) 
                #print("tiempo visita", str(tiempo_visita))
                #print("tiempo total", str(tiempo_total))
                #print("distancia", str(distancia))
                       
                 
                if tiempo_total <= self.tiempo_max:
                    # Si se puede añadir, añadir el nodo a la solución y actualizar el tiempo actual y otros parámetros
                    self.visitados.append(nodo)
                    #print("AÑADIDO ES:", str(nodo))
                    #print("Solucion es:", self.visitados)  
                    #tiempo_viaje = self.tiempos_df.loc[self.visitados[-1], str(nodo)]
                    tiempo_actual += tiempo_viaje + tiempo_visita
                    distancia_total += distancia
                    beneficio += self.nodos_df.loc[nodo, 'interes']
                    
                    #Salir del bucle while una vez que se añade un nodo
                    break
                else:
                    # Si no se puede añadir el nodo, eliminarlo de la lista de candidatos y continuar con el siguiente nodo
                    candidatos_fallidos.append(nodo)
                    candidatos.remove((fitness, nodo))    
                
                # Comprobar si ya no hay candidatos viables
                if set(candidatos_fallidos) == set([nodo for _, nodo in candidatos]):
                    break
            
            self.visitados, tiempo_actual = self.buscar_local_dlb()
                                 
            iter=iter+1
            
        # Devolver la lista de nodos visitados y el tiempo total
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def buscar_local(self):
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo = self.calcular_tiempo_total(mejor_solucion)

        # Iterar a través de pares de nodos e intentar intercambiarlos para encontrar una solución mejor
        for i in range(1, len(mejor_solucion) - 1):  # Empezar desde 1 para mantener el nodo inicial fijo
            for j in range(i + 1, len(mejor_solucion)):
                # Intercambiar nodos
                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                tiempo_actual = self.calcular_tiempo_total(mejor_solucion)

                # Si no se encuentra una mejora, revertir el intercambio
                if tiempo_actual >= mejor_tiempo:
                    mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                else:
                    mejor_tiempo = tiempo_actual

        return mejor_solucion, mejor_tiempo
    
    def buscar_local_dlb(self):
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo = self.calcular_tiempo_total(mejor_solucion)
        dlb = [0] * len(mejor_solucion)  # Inicializar la máscara DLB

        # Iterar a través de los nodos de la solución
        for i in range(1, len(mejor_solucion) - 1):  # El nodo inicial se mantiene fijo
            if dlb[i] == 0:  # Solo considerar este nodo si su DLB está en 0
                improve_flag = False
                for j in range(1, len(mejor_solucion)):  # Considerar todos los otros nodos
                    if i != j:  # Asegurarse de no intercambiar el nodo consigo mismo
                        # Intercambiar nodos
                        mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                        tiempo_actual = self.calcular_tiempo_total(mejor_solucion)

                        # Si no se encuentra una mejora, revertir el intercambio
                        if tiempo_actual < mejor_tiempo:
                            mejor_tiempo = tiempo_actual  # Actualizar el mejor tiempo
                            improve_flag = True  # Indicar que hubo una mejora
                            dlb[i] = dlb[j] = 0  # Restablecer los bits DLB ya que hubo una mejora
                            break  # Salir del bucle for interno
                        else:
                            # Revertir el intercambio si no mejora
                            mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]

                # Si no se encontró ninguna mejora, establecer el bit DLB en 1
                if not improve_flag:
                    dlb[i] = 1

        return mejor_solucion, mejor_tiempo

    def calcular_tiempo_total(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += self.tiempos_df.loc[solucion[i], str(solucion[i + 1])]
        return tiempo_total
    
    
    def aplicar_greedy_ciclico(self, nodo_ciclico):
            self.visitados = [nodo_ciclico]
            distancia_total = 0
            tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
            beneficio = self.nodos_df.loc[nodo_ciclico, 'interes']

            while True:
                mejor_fitness = -float('inf')
                mejor_nodo = None
                
                for i, nodo in self.nodos_df.iterrows():
                    if i not in self.visitados and i != nodo_ciclico:
                        tiempo_vuelta = self.tiempos_df.loc[i, str(nodo_ciclico)]
                        # Asegurarse de tener en cuenta el tiempo de visita en el nodo final
                        tiempo_necesario = tiempo_actual + self.nodos_df.loc[i, 'tiempo_de_visita'] + tiempo_vuelta + self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
                        
                        if tiempo_necesario <= self.tiempo_max:
                            fitness = self.calcular_fitness(self.visitados[-1], i)
                            if fitness > mejor_fitness:
                                mejor_fitness = fitness
                                mejor_nodo = i
                
                if mejor_nodo is None:
                    break

                tiempo_viaje = self.tiempos_df.loc[self.visitados[-1], str(mejor_nodo)]
                tiempo_actual += tiempo_viaje + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
                distancia_total += self.distancias_df.loc[self.visitados[-1], str(mejor_nodo)]
                beneficio += self.nodos_df.loc[mejor_nodo, 'interes']
                self.visitados.append(mejor_nodo)

            if tiempo_actual + self.tiempos_df.loc[self.visitados[-1], str(nodo_ciclico)] <= self.tiempo_max:
                self.visitados.append(nodo_ciclico)
                distancia_total += self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)]
                tiempo_actual += self.tiempos_df.loc[self.visitados[-2], str(nodo_ciclico)]
                # No se añade beneficio porque el nodo cíclico ya fue considerado al inicio

            return self.visitados, tiempo_actual, distancia_total, beneficio