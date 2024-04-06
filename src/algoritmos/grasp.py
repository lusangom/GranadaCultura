# Algoritmo GRASP

import pandas as pd
import math
import random
import funciones


class Grasp:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad, MAX_ITERACIONES = 300, MAX_ITERACIONES_BL = 50000, RANDOM_SEED = None, cantidad_candidatos = 0.03):
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
     
      
        while tiempo_actual <= self.tiempo_max and iter < self.MAX_ITERACIONES:
            
            #Calculamos el fitness de todos los nodos que no esten en la solucion
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
                
                 
                if tiempo_total <= self.tiempo_max:
                    # Si se puede añadir, añadir el nodo a la solución lo añadimos y actualizamos las variables correspondientes
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
            
        # Devolver la lista de nodos visitados y la información asociada
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def buscar_local(self):
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

        # Iterar a través de pares de nodos e intentar intercambiarlos para encontrar una solución mejor
        for i in range(0, len(mejor_solucion) - 1):  
            for j in range(i + 1, len(mejor_solucion)):
                # Intercambiar nodos
                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                tiempo_actual = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

                # Si no se encuentra una mejora, revertir el intercambio
                if tiempo_actual >= mejor_tiempo:
                    mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                else:
                    mejor_tiempo = tiempo_actual

        return mejor_solucion, mejor_tiempo
    
    
    
    def buscar_local_dlb(self):
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
                    for j in range(1, len(mejor_solucion)):  # Considerar todos los otros nodos
                        if i != j:  # Asegurarse de no intercambiar el nodo consigo mismo
                            # Intercambiar nodos
                            mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                            tiempo_actual = funciones.calcular_tiempo_total(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

                            # Si no se encuentra una mejora, revertir el intercambio
                            if tiempo_actual < mejor_tiempo:
                                mejor_tiempo = tiempo_actual  # Actualizar el mejor tiempo
                                mejor_encontrada = True;
                                improve_flag = True  # Indicar que hubo una mejora
                                dlb[i] = dlb[j] = 0  # Restablecer los bits DLB ya que hubo una mejora
                                break  # Salir del bucle for interno
                            else:
                                # Revertir el intercambio si no mejora
                                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]

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
       
        self.visitados = [nodo_ciclico]
        distancia_total = 0
        tiempo_actual = self.nodos_df.loc[nodo_ciclico, 'tiempo_de_visita']
        beneficio = self.nodos_df.loc[nodo_ciclico, 'interes']
        iter = 0
        vuelta = False;
        
        #print("NODO INICIO ES:", str(nodo_ciclico))
        #print("TIENE BENEFICIO DE:", str(self.nodos_df.loc[nodo_ciclico, 'interes']))
        
     
        while tiempo_actual <= self.tiempo_max and iter < self.MAX_ITERACIONES:
            
            #Calculamos el fitness de todos los nodos
            fitness_nodos = []
            for i, nodo in self.nodos_df.iterrows():
                if i not in self.visitados:
                    fitness = funciones.calcular_fitness(self.distancias_df,self.visitados[-1], i, self.velocidad, self.nodos_df)
                    fitness_nodos.append((fitness,i))
                    
            # Ordenar los nodos por fitness y obtenemos la lista de candidatos
            fitness_nodos.sort(reverse=True)
            candidatos = fitness_nodos[:max(1, math.ceil(len(fitness_nodos) * self.cantidad_candidatos))]
            
            
            
            #print("Candidatos:", candidatos)   
            #print("Tamanio", str(math.ceil(len(fitness_nodos) * 0.01)))
            #print("Iteracion:", str(iter))
            
           

            # Iterar sobre la lista de candidatos
            candidatos_fallidos = []
            while candidatos:
                # Seleccionar un nodo aleatorio de la lista de candidatos
                fitness, nodo = random.choice(candidatos)
                
                print("CANDIDATO ES:", str(nodo))
                #print("NODO INICIO ES:", str(nodo_ciclico))
                
                tiempo_viaje = (self.distancias_df.loc[self.visitados[-1], str(nodo)])/self.velocidad                
                tiempo_visita = self.nodos_df.loc[nodo, 'tiempo_de_visita']
                tiempo_vuelta = (self.distancias_df.loc[nodo, str(nodo_ciclico)])/self.velocidad          
                tiempo_total = tiempo_actual + tiempo_viaje + tiempo_visita + tiempo_vuelta
                
                distancia = self.distancias_df.loc[self.visitados[-1],str(nodo)]
                
                #print("tiempo vuelta:", str(tiempo_vuelta)) 
                #print("tiempo viaje:", str(tiempo_viaje)) 
                #print("tiempo visita", str(tiempo_visita))
                #print("tiempo total", str(tiempo_total))
                #print("distancia", str(distancia))
                       
                 
                if tiempo_total <= self.tiempo_max:
                    # Si se puede añadir, añadir el nodo a la solución y actualizar el tiempo actual y otros parámetros
                    self.visitados.append(nodo)
                    #print("AÑADIDO ES:", str(nodo))
                    #print("Solucion es:", self.visitados)  
                    #tiempo_viaje = (self.distancias_df.loc[self.visitados[-1], str(nodo)]
#)/self.velocidad                    
                    tiempo_actual += tiempo_viaje + tiempo_visita
                    distancia_total += distancia
                    beneficio += self.nodos_df.loc[nodo, 'interes']
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
                        
                

            
            self.visitados, tiempo_actual = self.buscar_local_dlb_ciclico()
            distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
            beneficio = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
              
            
                    
                                 
            iter=iter+1
            #print("FIN ITERACION:", str(tiempo_actual))
              # Verificar si se puede añadir el nodo de inicio al final para cerrar el ciclo
            if(vuelta):
                self.visitados.append(nodo_ciclico)
                distancia_total += self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)]
                tiempo_actual += (self.distancias_df.loc[self.visitados[-2], str(nodo_ciclico)])/self.velocidad
                break
            
        # Devolver la lista de nodos visitados y el tiempo total
        return self.visitados, tiempo_actual, distancia_total, beneficio
    
    def buscar_local_ciclico(self):
        # Hacer una copia de la solución actual
        mejor_solucion = self.visitados[:]
        mejor_tiempo, tmp = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

        # Iterar a través de pares de nodos e intentar intercambiarlos para encontrar una solución mejor
        for i in range(1, len(mejor_solucion) - 1):  # Empezar desde 1 para mantener el nodo inicial fijo
            for j in range(i + 1, len(mejor_solucion)):
                # Intercambiar nodos
                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                tiempo_actual, tmp_vuelta = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)

            

                # Si no se encuentra una mejora, revertir el intercambio
                if tiempo_actual >= mejor_tiempo:
                    mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                else:
                    mejor_tiempo = tiempo_actual
                    mejor_tiempo = mejor_tiempo - tmp_vuelta
    
       
        return mejor_solucion, mejor_tiempo
    
    
    
    def buscar_local_dlb_ciclico(self):
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
                    for j in range(1, len(mejor_solucion)):  # Considerar todos los otros nodos
                        if i != j:  # Asegurarse de no intercambiar el nodo consigo mismo
                            # Intercambiar nodos
                            mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                            tiempo_actual, tmp_vuelta = funciones.calcular_tiempo_total_ciclico(mejor_solucion, self.nodos_df, self.distancias_df, self.velocidad)


                            # Si no se encuentra una mejora, revertir el intercambio
                            if tiempo_actual < mejor_tiempo:
                                mejor_tiempo = tiempo_actual  # Actualizar el mejor tiempo
                                
                                #print("ANTES:", str(mejor_tiempo))
                                
                                #tiempo_vuelta = (self.distancias_df.loc[mejor_solucion[-1],str(mejor_so)/self.velocidadlucion[0])]    
                                mejor_tiempo = mejor_tiempo - tmp_vuelta
                                
                                #print("MEJJOR FINAL ES:", str(mejor_solucion[-1]))
                                #print("MEJOR NODO INICIO ES:", str(mejor_solucion[0]))
                                #print("MEJOR tiempo ES:", str(tiempo_vuelta))
                                #print("DESPUES:", str(mejor_tiempo))
                                
                                mejor_encontrada = True;
                                improve_flag = True  # Indicar que hubo una mejora
                                dlb[i] = dlb[j] = 0  # Restablecer los bits DLB ya que hubo una mejora
                                break  # Salir del bucle for interno
                            else:
                                # Revertir el intercambio si no mejora
                                mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]

                    # Si no se encontró ninguna mejora, establecer el bit DLB en 1
                    if not improve_flag:
                        dlb[i] = 1
            
            j = j+1
                     
                    

        return mejor_solucion, mejor_tiempo

   

        