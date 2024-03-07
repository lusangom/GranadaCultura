# algoritmo_greedy.py

import pandas as pd

class Greedy:
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

    
   
    def aplicar_greedy(self):
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