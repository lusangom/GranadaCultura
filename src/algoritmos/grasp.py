# Algoritmo GRASP

import pandas as pd
import math
import random
import funciones
import time


class Grasp:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad, MAX_ITERACIONES = 300, MAX_ITERACIONES_BL = 50000, RANDOM_SEED = None, cantidad_candidatos = 0.05):
        """
        Inicializa la clase GRASP.
        """
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.velocidad = velocidad
        self.visitados = []
        self.MAX_ITERACIONES = MAX_ITERACIONES
        self.MAX_ITERACIONES_BL = MAX_ITERACIONES_BL
        self.cantidad_candidatos = cantidad_candidatos
        if RANDOM_SEED is not None:
            random.seed(RANDOM_SEED)
        else: #Para que no se repitan los resultados
            semilla_actual = int(time.time())
            random.seed(semilla_actual)
        

  
    def aplicar_grasp(self):
        """Función algoritmo GRASP ciclico.

        Función para aplicar el algoritmo GRASP.
        
        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        
        # Seleccionar el nodo inicial basado en el mayor interés añadirlo a la solución e inicializar las variables
        nodo_inicial = self.nodos_df['interes'].idxmax()
        self.visitados.append(nodo_inicial)
        distancia_total = 0
        tiempo_actual = 0
        beneficio = 0
        iter = 0
        
        tiempo_actual = self.nodos_df.loc[nodo_inicial, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_inicial, 'interes']
     
        # Mientras que haya tiempo y mientras que no hayamos llegado al maximo de iteraciones
        while tiempo_actual <= self.tiempo_max and iter < self.MAX_ITERACIONES:
            
            # Calculamos el fitness de todos los nodos que no esten en la solucion
            fitness_nodos = []
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = funciones.calcular_fitness(self.distancias_df,self.visitados[-1], i, self.velocidad, self.nodos_df)
                    fitness_nodos.append((fitness,i))
                    
            # Ordenar los nodos por fitness y obtenemos la lista de candidatos según un porcentaje de la población de candidatos
            fitness_nodos.sort(reverse=True)
            candidatos = fitness_nodos[:max(1, math.ceil(len(fitness_nodos) * self.cantidad_candidatos))]

            # Iteramos sobre la lista de candidatos
            candidatos_fallidos = []
            while candidatos:
                # Seleccionar un nodo aleatorio de la lista de candidatos
                fitness, nodo = random.choice(candidatos)
          
                # Calculamos el tiempo necesario para visitar ese candidato
                tiempo_viaje = (self.distancias_df.loc[self.visitados[-1], str(nodo)])/self.velocidad                
                tiempo_visita = self.nodos_df.loc[nodo, 'tiempo_de_visita']
                tiempo_total = tiempo_actual + tiempo_viaje + tiempo_visita
                distancia = self.distancias_df.loc[self.visitados[-1],str(nodo)]
                
                # Si se puede añadir, añadir el nodo a la solución lo añadimos y actualizamos las variables correspondientes 
                if tiempo_total <= self.tiempo_max:
                    self.visitados.append(nodo)
                    tiempo_actual += tiempo_viaje + tiempo_visita
                    distancia_total += distancia
                    beneficio += self.nodos_df.loc[nodo, 'interes']
                    
                    #Salir del bucle while una vez que se añade un nodo
                    break
                else:
                    # Si no se puede añadir el nodo, eliminarlo de la lista de candidatos y continuamos con el siguiente nodo
                    candidatos_fallidos.append(nodo)
                    candidatos.remove((fitness, nodo))
                    break
                    
            # Aplicamos a nuesta solución una busqueda local y actualizamos las variables
            self.visitados, tiempo_actual = self.buscar_local_dlb()
            distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
            beneficio = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
                                 
            iter=iter+1
            
        tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
        distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
        beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
    
    def buscar_local(self):
        """Función Busqueda Local sin DLB.

        Función para aplicar un busqueda local a nuestra solución donde el objetivo es minimizar las distancias 
        entre nuestros nodos.
        
        Returns:
            Array: Ruta solución actualizada por la búsqueda local.
            Float: Número que representa el tiempo de nuestra solución actual
        """
        # Hacer una copia de la solución actual y calcular su tiempo
        mejor_solucion = self.visitados[:]
        mejor_tiempo = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

        # Iterar a través de pares de nodos e intentar intercambiarlos para encontrar una solución mejor
        for i in range(0, len(mejor_solucion) - 1):  
            for j in range(i + 1, len(mejor_solucion)):
                # Intercambiar nodos para ver si el intercambio reduce el tiempo de nuestra ruta
                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                tiempo_actual = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

                # Si no se encuentra una mejora, revertir el intercambio
                if tiempo_actual >= mejor_tiempo:
                    mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                else:
                    # Actualizamos el tiempo si hay mejora
                    mejor_tiempo = tiempo_actual

        return mejor_solucion, mejor_tiempo
    
    
    
    def buscar_local_dlb(self):
        """Función Busqueda Local con DLB.

        Función para aplicar un busqueda local a nuestra solución donde el objetivo es minimizar las distancias 
        entre nuestros nodos. Se utiliza una máscara DLB (Don't Look Bits) para reducir el tiempo de ejecución
        
        Returns:
            Array: Ruta solución actualizada por la búsqueda local.
            Float: Número que representa el tiempo de nuestra solución actual
        """
        
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)
        dlb = [0] * len(mejor_solucion)  # Inicializar la máscara DLB
        
        mejor_encontrada = True
        j=0
      
        # Iterar a través de los nodos de la solución
        while j < self.MAX_ITERACIONES_BL and mejor_encontrada:
        
            mejor_encontrada = False
            
            for i in range(0, len(mejor_solucion) - 1): 
                if dlb[i] == 0:  # Solo considerar este nodo si su DLB está en 0
                    improve_flag = False
                    for k in range(1, len(mejor_solucion)):  # Considerar todos los otros nodos
                        if i != k:  # Asegurarse de no intercambiar el nodo consigo mismo
                            # Intercambiar nodos
                            mejor_solucion[i], mejor_solucion[k] = mejor_solucion[k], mejor_solucion[i]
                            tiempo_actual = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

                            # Si no se encuentra una mejora, revertir el intercambio
                            if tiempo_actual < mejor_tiempo:
                                mejor_tiempo = tiempo_actual  # Actualizar el mejor tiempo
                                mejor_encontrada = True;
                                improve_flag = True  # Indicar que hubo una mejora
                                dlb[i] = dlb[k] = 0  # Restablecer los bits DLB ya que hubo una mejora
                                break  # Salir del bucle for interno
                            else:
                                # Revertir el intercambio si no mejora
                                mejor_solucion[i], mejor_solucion[k] = mejor_solucion[k], mejor_solucion[i]

                    # Si no se encontró ninguna mejora, establecer el bit DLB en 1
                    if not improve_flag:
                        dlb[i] = 1
            
            j = j+1            
                    

        return mejor_solucion, mejor_tiempo

   
    

    def aplicar_grasp_ciclico(self, nodo_ciclico):
        """Función algoritmo GRASP ciclico.

        Función para aplicar el algoritmo GRASP ciclico.
        
        Args:
            nodo_ciclico (int): Número que representa el nodo ciclico

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        
        # El procedimiento de ejecución es igual que el algoritmo GRASP pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
       
        self.visitados = [nodo_ciclico]
        distancia_total = 0
        tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
        beneficio_actual = self.nodos_df.loc[nodo_ciclico, 'interes']
        iter = 0
        vuelta = False
        
        while tiempo_actual <= self.tiempo_max and iter < self.MAX_ITERACIONES:
            
            #Calculamos el fitness de todos los nodos
            fitness_nodos = []
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = funciones.calcular_fitness(self.distancias_df,self.visitados[-1], i, self.velocidad, self.nodos_df)
                    fitness_nodos.append((fitness,i))
                    
            # Ordenar los nodos por fitness y obtenemos la lista de candidatos según un porcentaje de la población de candidatos
            fitness_nodos.sort(reverse=True)
            candidatos = fitness_nodos[:max(1, math.ceil(len(fitness_nodos) * self.cantidad_candidatos))]
       
            # Iterar sobre la lista de candidatos
            candidatos_fallidos = []
            while candidatos:
                # Seleccionar un nodo aleatorio de la lista de candidatos
                fitness, nodo = random.choice(candidatos)
                
                # Para los tiempos hay que tener en cuenta el tiempo de vuelta al nodo ciclico
                tiempo_viaje = (self.distancias_df.loc[self.visitados[-1], str(nodo)])/self.velocidad                
                tiempo_visita = self.nodos_df.loc[nodo, 'tiempo_de_visita']
                tiempo_vuelta = (self.distancias_df.loc[nodo, str(nodo_ciclico)])/self.velocidad          
                tiempo_total = tiempo_actual + tiempo_viaje + tiempo_visita + tiempo_vuelta
                
                distancia = self.distancias_df.loc[self.visitados[-1],str(nodo)]
                
                if tiempo_total <= self.tiempo_max:
                    # Si se puede añadir, añadir el nodo a la solución y actualizar el tiempo actual y otros parámetros
                    self.visitados.append(nodo)
                    tiempo_actual += tiempo_viaje + tiempo_visita
                    distancia_total += distancia
                    beneficio_actual += self.nodos_df.loc[nodo, 'interes']
                    vuelta = False
                   
                    
                    #Salir del bucle while una vez que se añade un nodo
                    break
                else:
                   
                    if(tiempo_vuelta <= (self.tiempo_max - tiempo_actual)):
                        vuelta = True
                        break
                    
                    # Si no se puede añadir el nodo, eliminarlo de la lista de candidatos y continuar con el siguiente nodo
                    candidatos_fallidos.append(nodo)
                    candidatos.remove((fitness, nodo))
                    break
                        
                        
            self.visitados = self.buscar_local_dlb_ciclico()
            tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
            distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
            beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
              
                                 
            iter=iter+1
           
            # Cuando se llega al final añadir el nodo ciclico y actualizar las variables. El interes no se tiene 
            # en cuenta 2 veces
            if(vuelta):
                self.visitados.append(nodo_ciclico)
                distancia_total += self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)]
                tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)])/self.velocidad
                if self.visitados[0] == nodo_ciclico and self.visitados[-1] == nodo_ciclico:
                    break
        
        # Aplicamos una comprobacion adicional
        if self.visitados[-1] != nodo_ciclico:
            self.visitados[-1] = nodo_ciclico
            tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
            distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
            beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
            beneficio_actual = beneficio_actual - self.nodos_df.loc[self.visitados[0], 'interes'] #El interes del nodo ciclico no se tiene en cuenta dos veces
              

        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
        # Devolver la solución y la información asociada a ella
      
    
    def buscar_local_ciclico(self):
        """Función Busqueda Local ciclica sin DLB.

        Función para aplicar un busqueda local ciclica a nuestra solución donde el objetivo es minimizar las distancias 
        entre nuestros nodos.
        
        Returns:
            Array: Ruta solución actualizada por la búsqueda local.
            Float: Número que representa el tiempo de nuestra solución actual
        """
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo, tmp = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

        # Iterar a través de pares de nodos e intentar intercambiarlos para encontrar una solución mejor
        for i in range(1, len(mejor_solucion) - 1):  # El nodo inicial se mantiene fijo
            for j in range(i + 1, len(mejor_solucion)):
                # Intercambiar nodos
                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                tiempo_actual, tmp_vuelta = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

                # Si no se encuentra una mejora, revertir el intercambio
                if tiempo_actual >= mejor_tiempo:
                    mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                else:
                    # Restamos el tiempo de vuelta al nodo ciclico ya que este solo se tiene en cuenta al final
                    mejor_tiempo = tiempo_actual
                    mejor_tiempo = mejor_tiempo - tmp_vuelta
    
       
        return mejor_solucion, mejor_tiempo
    
    
    
    def buscar_local_dlb_ciclico(self):
        """Función Busqueda Local ciclica con DLB.

        Función para aplicar un busqueda local ciclica a nuestra solución donde el objetivo es minimizar las distancias 
        entre nuestros nodos. Se utiliza una máscara DLB (Don't Look Bits) para reducir el tiempo de ejecución
        
        Returns:
            Array: Ruta solución actualizada por la búsqueda local.
            Float: Número que representa el tiempo de nuestra solución actual
        """
        
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo, tmp = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)
        dlb = [0] * len(mejor_solucion)  # Inicializar la máscara DLB
        
        mejor_encontrada = True
        j=0
      
        # Iterar a través de los nodos de la solución
        while j < self.MAX_ITERACIONES_BL and mejor_encontrada:
        
            mejor_encontrada = False
            
            for i in range(1, len(mejor_solucion) - 1):  # El nodo inicial se mantiene fijo
                if dlb[i] == 0:  # Solo considerar este nodo si su DLB está en 0
                    improve_flag = False
                    for k in range(1, len(mejor_solucion)-1):  # Considerar todos los otros nodos
                        if i != k:  # Asegurarse de no intercambiar el nodo consigo mismo
                            # Intercambiar nodos
                            mejor_solucion[i], mejor_solucion[k] = mejor_solucion[k], mejor_solucion[i]
                            tiempo_actual, tmp_vuelta = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)


                            # Si no se encuentra una mejora, revertir el intercambio
                            if tiempo_actual < mejor_tiempo:
                                
                                mejor_tiempo = tiempo_actual
                                # Restamos el tiempo de vuelta al nodo ciclico ya que este solo se tiene en cuenta al final
                                mejor_tiempo = mejor_tiempo - tmp_vuelta
                              
                                mejor_encontrada = True;
                                improve_flag = True  # Indicar que hubo una mejora
                                dlb[i] = dlb[k] = 0  # Restablecer los bits DLB ya que hubo una mejora
                                break  # Salir del bucle for interno
                            else:
                                # Revertir el intercambio si no mejora
                                mejor_solucion[i], mejor_solucion[k] = mejor_solucion[k], mejor_solucion[i]

                    # Si no se encontró ninguna mejora, establecer el bit DLB en 1
                    if not improve_flag:
                        dlb[i] = 1
            
            j = j+1
                     
                    

        return mejor_solucion

   

        