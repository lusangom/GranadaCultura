# Algoritmo Enfriamiento Simulado

import pandas as pd
import random
import math
import numpy as np
import funciones as funciones
import time

class EnfriamientoSimulado:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad, MU = 0.3, PHI = 0.2, T_FINAL = 0.0001, RANDOM_SEED = None, MAX_EVALUACIONES = 50000, BETA = 0.2 ):
        """
        Inicializa la clase Enfriamiento Simulado.
        """
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.velocidad = velocidad
        self.visitados = []
        self.MU = MU
        self.PHI = PHI
        self.T_FINAL = T_FINAL
        self.MAX_EVALUACIONES = MAX_EVALUACIONES
        self.BETA = BETA
        if RANDOM_SEED is not None:
            random.seed(RANDOM_SEED)
        else: #Para que no se repitan los resultados
            semilla_actual = int(time.time())
            random.seed(semilla_actual)
        
   
    def generar_solucion_inicial_greedy(self):
        """Función genera solución inicial greedy.

        Función usada para generar la solución inicial del algoritmo, el modo de creación
        es un algoritmo Greedy, por lo que el funcionamiento es igual que dicho algoritmo.
        

        Returns:
            Array: Ruta inicial Greedy y la información asociada a ella.
        """
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
                    fitness = funciones.calcular_fitness(self.distancias_df, self.visitados[-1], i, self.velocidad, self.nodos_df)
                    if fitness > mejor_fitness and tiempo_actual + (self.distancias_df.loc[self.visitados[-1], str(i)])/self.velocidad + self.nodos_df.loc[i, 'tiempo_de_visita'] <= self.tiempo_max:
                        mejor_fitness = fitness
                        mejor_nodo = i
                        
                      
            if mejor_nodo is None:
                break  # No se encontraron más nodos para visitar sin superar el tiempo máximo
            
            self.visitados.append(mejor_nodo)
            tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)])/self.velocidad + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
            distancia_total += self.distancias_df.loc[self.visitados[-2], str(mejor_nodo)] 
            beneficio += self.nodos_df.loc[mejor_nodo,'interes']
            
        
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def generar_solucion_inicial_greedy_ciclico(self, nodo_ciclico):
        """Función genera solución inicial greedy ciclica.

        Función usada para generar la solución inicial del algoritmo, el modo de creación
        es un algoritmo Greedy ciclico, por lo que el funcionamiento es igual que dicho algoritmo.

        Returns:
            Array: Ruta inicial Greedy ciclica y la información asociada a ella.
        """
        self.visitados = [nodo_ciclico]
        distancia_total = 0
        tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_ciclico, 'interes']

        while True:
            mejor_fitness = -float('inf')
            mejor_nodo = None

            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados and i != nodo_ciclico:
                    tiempo_vuelta = self.distancias_df.loc[i, str(nodo_ciclico)] / self.velocidad
                    tiempo_necesario = tiempo_actual + self.nodos_df.loc[i, 'tiempo_de_visita'] + tiempo_vuelta

                    if tiempo_necesario <= self.tiempo_max:
                        fitness = funciones.calcular_fitness(self.distancias_df, self.visitados[-1], i, self.velocidad, self.nodos_df)
                        if fitness > mejor_fitness:
                            mejor_fitness = fitness
                            mejor_nodo = i

            if mejor_nodo is None:
                break

            tiempo_viaje = self.distancias_df.loc[self.visitados[-1], str(mejor_nodo)] / self.velocidad
            tiempo_actual += tiempo_viaje + self.nodos_df.loc[mejor_nodo, 'tiempo_de_visita']
            distancia_total += self.distancias_df.loc[self.visitados[-1], str(mejor_nodo)]
            beneficio += self.nodos_df.loc[mejor_nodo, 'interes']
            self.visitados.append(mejor_nodo)

        # Añadir el nodo inicial al final de la ruta
        tiempo_viaje_final = self.distancias_df.loc[self.visitados[-1], str(nodo_ciclico)] / self.velocidad
        tiempo_actual += tiempo_viaje_final
        distancia_total += self.distancias_df.loc[self.visitados[-1], str(nodo_ciclico)]

        self.visitados.append(nodo_ciclico)

        # Verificar si se excede el tiempo máximo
        if tiempo_actual > self.tiempo_max:
            # Si excede el tiempo, remover el último nodo visitado antes de regresar al inicio
            ultimo_nodo = self.visitados[-2]
            self.visitados.pop(-2)
            distancia_total -= self.distancias_df.loc[ultimo_nodo, str(nodo_ciclico)]
            tiempo_actual -= (self.distancias_df.loc[ultimo_nodo, str(nodo_ciclico)] / self.velocidad + self.nodos_df.loc[ultimo_nodo, 'tiempo_de_visita'])
            beneficio -= self.nodos_df.loc[ultimo_nodo, 'interes']

            # Agregar el nodo inicial de nuevo para cerrar el ciclo
            tiempo_viaje_final = self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)] / self.velocidad
            tiempo_actual += tiempo_viaje_final
            distancia_total += self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)]

        return self.visitados, tiempo_actual, distancia_total, beneficio

        
    
    
    def generar_vecino(self, solucion):
        """Función generar vecino.

        Función usada para generar un vecino en nuestra solución actual, es decir intercambia
        un nodo de nuestra solución actual con otro que todavia no este y comprueba si este
        intercambio es factible en terminos de tiempo.

        Returns:
            Array: Ruta con intercambio realizado si es factible.
        """
        
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
        
        # Calculamos el tiempo requerido para recorrer esta solución potencial
        tiempo_total = funciones.calcular_tiempo_total(vecino_potencial, self.nodos_df, self.distancias_df, self.velocidad)
    

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
          
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
           
        # Si no es factible el intercambio devuelve la solución pasada por parámetro
        return solucion
    
    def generar_vecino_ciclico(self, solucion):
        """Función generar vecino ciclico.

        Función usada para generar un vecino ciclico en nuestra solución actual, es decir intercambia
        un nodo de nuestra solución actual con otro que todavia no este y comprueba si este
        intercambio es factible en terminos de tiempo.

        Returns:
            Array: Ruta ciclica con intercambio realizado si es factible.
        """
        
        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        # Asegurarse de que hay al menos tres nodos en la solución para excluir el primero y el último
        
        if len(solucion) <= 3:
            return solucion

        nodo_a_reemplazar = random.choice(solucion[1:-1])
        nodos_posibles = [nodo for nodo in self.nodos_df.index if nodo not in solucion and nodo != solucion[0]]

        if not nodos_posibles:
            return solucion

        nuevo_nodo = random.choice(nodos_posibles)
       
      
        vecino_potencial = solucion[:]
        index_a_reemplazar = solucion.index(nodo_a_reemplazar)
        
      
      
        vecino_potencial[index_a_reemplazar] = nuevo_nodo
      
        tiempo_total, _ = funciones.calcular_tiempo_total_ciclico(vecino_potencial, self.nodos_df, self.distancias_df, self.velocidad)

        if tiempo_total <= self.tiempo_max:
            return vecino_potencial

        return solucion

    
    def aplicar_enfriamiento_simulado(self):
        """Función algoritmo enfriamiento simulado.

        Función para aplicar el algoritmo de enfriamiento simulado.

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        
        # Generamos la solución incial
        self.visitados, tiempo_actual, distancia_total, beneficio_actual = self.generar_solucion_inicial_greedy()
        
        # Calculamos el tiempo actual
        t_actual = (self.MU * beneficio_actual) / (-math.log(self.PHI))
        
        iteracion = 0
        while t_actual > self.T_FINAL and iteracion < self.MAX_EVALUACIONES:
            # Generamos la solución vecina y comprobamos si el intercambio merece la pena
            vecino = self.generar_vecino(self.visitados)
            beneficio_vecino = funciones.calcular_beneficio_total(vecino, self.nodos_df)
            beneficio_solucion_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
          
            delta_beneficio = (beneficio_vecino - beneficio_solucion_actual)
            # Si merece la pena el intercambio o si queremos empeorar la solución para explorar nuevos campos
            # se realiza el intercambio
            if delta_beneficio > 0 or np.random.rand() < math.exp(delta_beneficio / t_actual):
                tiempo_vecino =  funciones.calcular_tiempo_total(vecino, self.nodos_df, self.distancias_df, self.velocidad)
                if(tiempo_vecino <= self.tiempo_max):
                 
                    self.visitados = vecino
                    beneficio_actual = beneficio_vecino
                    tiempo_actual = tiempo_vecino
                    distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
            # Actualizamos la temperatura y la solución
            t_actual = t_actual / (1 + self.BETA * t_actual)
            iteracion += 1
        
        tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
        distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
        beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
    
    
    def aplicar_enfriamiento_simulado_ciclico(self, nodo_ciclico):
        """Función algoritmo enfriamiento simulado ciclico.

        Función para aplicar el algoritmo de enfriamiento simulado ciclico.
        
        Args:
            nodo_ciclico (int): Número que representa el nodo ciclico

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        
        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        
        self.visitados, tiempo_actual, distancia_total, beneficio_actual = self.generar_solucion_inicial_greedy_ciclico(nodo_ciclico=nodo_ciclico)
        t_actual = (self.MU * beneficio_actual) / (-math.log(self.PHI))

        iteracion = 0
        while t_actual > self.T_FINAL and iteracion < self.MAX_EVALUACIONES and tiempo_actual < self.tiempo_max:
            vecino = self.generar_vecino_ciclico(self.visitados)

            beneficio_vecino = funciones.calcular_beneficio_total(vecino, self.nodos_df)
            beneficio_vecino -= self.nodos_df.loc[vecino[0], 'interes']
            beneficio_solucion_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
            beneficio_solucion_actual -= self.nodos_df.loc[self.visitados[0], 'interes']
            delta_beneficio = beneficio_vecino - beneficio_solucion_actual

            if delta_beneficio > 0 or np.random.rand() < math.exp(delta_beneficio / t_actual):
                tiempo_vecino, _ = funciones.calcular_tiempo_total_ciclico(vecino,self.nodos_df, self.distancias_df,self.velocidad)
                if tiempo_vecino <= self.tiempo_max:
                
                    self.visitados = vecino
                    beneficio_actual = beneficio_vecino
                    tiempo_actual = tiempo_vecino
                    distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)

            t_actual = t_actual / (1 + self.BETA * t_actual)
            iteracion += 1

        tiempo_actual, _ = funciones.calcular_tiempo_total_ciclico(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
        distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
        beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
        beneficio_actual -= self.nodos_df.loc[self.visitados[0], 'interes']

        return self.visitados, tiempo_actual, distancia_total, beneficio_actual