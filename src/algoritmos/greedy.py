# Algoritmo Greedy

import pandas as pd
import funciones 

class Greedy:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad):
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.velocidad = velocidad
        self.visitados = []
            
   
    def aplicar_greedy(self):
        """Función algoritmo greedy.

        Función para aplicar el algoritmo greedy.

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        # Empezamos con el nodo de mayor interés e inicializamos las variables
        nodo_inicial = self.nodos_df['interes'].idxmax()
        self.visitados.append(nodo_inicial)
        distancia_total = 0
        tiempo_actual = 0
        beneficio = 0
        tiempo_actual = self.nodos_df.loc[nodo_inicial, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_inicial, 'interes']
     
        # Añadimos nodos a nuestra ruta solución. El nodo que se añade es el que se encuentre con mejor fitness
        # Se añaden nodos siempre y cuando no superemos el tiempo máximo del que dispone el usuario.
        while tiempo_actual <= self.tiempo_max:
            mejor_fitness = -float('inf')
            mejor_nodo = None
            
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = funciones.calcular_fitness(self.distancias_df, self.visitados[-1], i, self.velocidad, self.nodos_df)
                    if fitness > mejor_fitness and tiempo_actual + (self.distancias_df.loc[self.visitados[-1], str(i)])/self.velocidad + self.nodos_df.loc[i, 'tiempo_de_visita'] <= self.tiempo_max:
                        mejor_fitness = fitness
                        mejor_nodo = i
            
            # Paramos la ejecución si no se encuentran más nodos 
            if mejor_nodo is None:
                break  
            
            #Actualizamos las variables
            self.visitados.append(mejor_nodo)
            tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)] )/self.velocidad + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
            distancia_total += self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)] 
            beneficio += self.nodos_df.loc[mejor_nodo,'interes']
            
        
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def aplicar_greedy_ciclico(self, nodo_ciclico):
        """Función algoritmo greedy ciclico.

        Función para aplicar el algoritmo greedy ciclico.

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        self.visitados = [nodo_ciclico]
        distancia_total = 0
        tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_ciclico, 'interes']

        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        while True:
            mejor_fitness = -float('inf')
            mejor_nodo = None
                
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados and i != nodo_ciclico:
                    # Asegurarse de tener en cuenta el tiempo de volver al nodo final
                    tiempo_vuelta = (self.distancias_df.loc[i, str(nodo_ciclico)])/self.velocidad              
                    tiempo_necesario = tiempo_actual + self.nodos_df.loc[i, 'tiempo_de_visita'] + tiempo_vuelta + self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
                        
                    if tiempo_necesario <= self.tiempo_max:
                        fitness = funciones.calcular_fitness(self.distancias_df, self.visitados[-1], i, self.velocidad, self.nodos_df)
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
            # No se añade beneficio del no final porque el nodo cíclico ya fue considerado al inicio

        return self.visitados, tiempo_actual, distancia_total, beneficio