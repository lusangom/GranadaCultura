import pandas as pd
import numpy as np
import random

MAX_ITERACIONES = 50000

class AlgoritmoMemetico:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad, poblacion_size=50):
        """
        Inicializa la clase Algoritmo Memetico.
        """
        self.nodos_df = nodos_df.set_index('nodo') 
        self.distancias_df = distancias_df.set_index('nodo')
        self.tiempos_df = tiempos_df.set_index('nodo')
        self.tiempo_max = tiempo_max
        self.velocidad = velocidad
        self.poblacion_size = poblacion_size
        self.poblacion = []
        self.fitness = []
        self.visitados = []
        random.seed(42)

    #Inicializacion de las poblaciones. Generamos 50 poblaciones aleatorias
    def inicializar_poblacion(self):
        while len(self.poblacion) < self.poblacion_size:
            cromosoma = self.generar_cromosoma()
            if cromosoma:
                self.poblacion.append(cromosoma)
                
    #Inicializacion de las poblaciones. Generamos 50 poblaciones aleatorias
    def inicializar_poblacion_ciclico(self,nodo_ciclico):
        while len(self.poblacion) < self.poblacion_size:
            cromosoma = self.generar_cromosoma_ciclico(nodo_ciclico)
            if cromosoma:
                self.poblacion.append(cromosoma)
                
   

      
    def generar_cromosoma(self):
        cromosoma = []
        tiempo_actual = 0
        
        nodo_inicial = self.nodos_df['interes'].idxmax()
        cromosoma.append(nodo_inicial)
        
        nodos_disponibles =  [nodo for nodo in self.nodos_df.index if nodo not in cromosoma]
       
        
        tiempo_actual += self.nodos_df.at[nodo_inicial, 'tiempo_de_visita']

        while nodos_disponibles:
            nodo_siguiente = random.choice(nodos_disponibles)
            
            tiempo_siguiente=(self.distancias_df.loc[cromosoma[-1], str(nodo_siguiente)])/self.velocidad
            tiempo_visita_siguiente = self.nodos_df.loc[nodo_siguiente, 'tiempo_de_visita']
            if tiempo_actual + tiempo_siguiente + tiempo_visita_siguiente >= self.tiempo_max: #Solo se añaden si hay suficiente tiempo disponible
                break  # No se puede añadir más nodos sin superar el tiempo máximo
           
            cromosoma.append(nodo_siguiente)
            nodos_disponibles.remove(nodo_siguiente)
            tiempo_actual += tiempo_siguiente + tiempo_visita_siguiente
        
       
        return cromosoma
    
    def generar_cromosoma_ciclico(self, nodo_ciclico):
        cromosoma = [nodo_ciclico]
        tiempo_actual = 0
        
        nodo_inicial = nodo_ciclico
       
        
        nodos_disponibles =  [nodo for nodo in self.nodos_df.index if nodo not in cromosoma]
       
        
        tiempo_actual += self.nodos_df.at[nodo_inicial, 'tiempo_de_visita']

        while nodos_disponibles:
            nodo_siguiente = random.choice(nodos_disponibles)
            
            tiempo_siguiente=(self.distancias_df.loc[cromosoma[-1], str(nodo_siguiente)])/self.velocidad
            tiempo_visita_siguiente = self.nodos_df.loc[nodo_siguiente, 'tiempo_de_visita']
            tiempo_vuelta=(self.distancias_df.loc[nodo_siguiente,str(nodo_ciclico)])/self.velocidad         
            if tiempo_actual + tiempo_siguiente + tiempo_visita_siguiente + tiempo_vuelta >= self.tiempo_max: #Solo se añaden si hay suficiente tiempo disponible
                cromosoma.append(nodo_ciclico)
                break  # No se puede añadir más nodos sin superar el tiempo máximo
           
            cromosoma.append(nodo_siguiente)
            nodos_disponibles.remove(nodo_siguiente)
            tiempo_actual += tiempo_siguiente + tiempo_visita_siguiente
        
             
       
        return cromosoma
    
    
    

    def calcular_fitness_cromosoma(self, cromosoma):
        fitness_total = 0
        for i, nodo in enumerate(cromosoma[:-1]):
            tiempo_viaje = (self.distancias_df.loc[cromosoma[i], str(cromosoma[i+1])])/self.velocidad      
            fitness_total += self.nodos_df.loc[nodo, 'interes'] - tiempo_viaje*0.1
        return fitness_total
    
    def calcular_beneficio_cromosoma(self, cromosoma):
        fitness_total = 0
       
        for i, nodo in enumerate(cromosoma[:-1]):
            fitness_total += self.nodos_df.loc[nodo, 'interes']
        return fitness_total

    def seleccion_torneo(self):
        # Selecciona dos padres mediante torneo. En el esquema estacionario, se aplicará dos veces el torneo para elegir los dos padres que serán posteriormente recombinados (cruzados).
        padres = []
        for _ in range(2):
            candidatos = random.choices(self.poblacion, k=2)
            candidato_fitness = [self.calcular_fitness_cromosoma(c) for c in candidatos]
            padres.append(candidatos[np.argmax(candidato_fitness)])
     
        return padres

    def cruce(self, padre1, padre2):
        mejor_padre = padre1 if self.calcular_fitness_cromosoma(padre1) > self.calcular_fitness_cromosoma(padre2) else padre2
        intentos = 0
        while intentos < 10:  # Máximo de 10 intentos para generar un hijo válido
            hijo = [None] * max(len(padre1), len(padre2))  # Selecciona el tamaño máximo entre los dos padres
            # Mantener posiciones iguales
            for i in range(min(len(padre1), len(padre2))):
                if padre1[i] == padre2[i]:
                    hijo[i] = padre1[i]

            posiciones_restantes = [i for i, v in enumerate(hijo) if v is None]
            # Seleccionar nodos restantes de ambos padres que no estén en el hijo
            nodos_restantes_padre1 = [n for n in padre1 if n not in hijo]
            nodos_restantes_padre2 = [n for n in padre2 if n not in hijo]
            # Mezclar los nodos restantes de ambos padres y eliminar duplicados
            nodos_restantes = list(set(nodos_restantes_padre1 + nodos_restantes_padre2))
            random.shuffle(nodos_restantes)

            contador = 0
            # Insertar los nodos restantes en las posiciones vacías del hijo
            for pos in posiciones_restantes:
                if nodos_restantes:
                    hijo[pos] = nodos_restantes.pop(0)
                    contador += 1
                    if contador == len(posiciones_restantes):
                        break  # Si el tamaño del hijo se ha completado, paramos
                else:
                    break  # No hay más nodos restantes para insertar

            # Verificar si el hijo generado cumple con el tiempo máximo permitido
            if self.verificar_tiempo_hijo(hijo):
                return hijo
            intentos += 1

        # Si después de 10 intentos no se genera un hijo válido, se devuelve el mejor padre
        return mejor_padre
    
    def cruce_ciclico(self, padre1, padre2):
        mejor_padre = padre1 if self.calcular_fitness_cromosoma(padre1) > self.calcular_fitness_cromosoma(padre2) else padre2
        intentos = 0
        while intentos < 10:  # Máximo de 10 intentos para generar un hijo válido
            hijo = [None] * max(len(padre1), len(padre2))  # Selecciona el tamaño máximo entre los dos padres
            # Mantener posiciones iguales
            for i in range(min(len(padre1), len(padre2))):
                if padre1[i] == padre2[i]:
                    hijo[i] = padre1[i]

            posiciones_restantes = [i for i, v in enumerate(hijo) if v is None]
            # Seleccionar nodos restantes de ambos padres que no estén en el hijo
            nodos_restantes_padre1 = [n for n in padre1 if n not in hijo]
            nodos_restantes_padre2 = [n for n in padre2 if n not in hijo]
            # Mezclar los nodos restantes de ambos padres y eliminar duplicados
            nodos_restantes = list(set(nodos_restantes_padre1 + nodos_restantes_padre2))
            random.shuffle(nodos_restantes)

            contador = 0
            # Insertar los nodos restantes en las posiciones vacías del hijo
            for pos in posiciones_restantes:
                if nodos_restantes:
                    hijo[pos] = nodos_restantes.pop(0)
                    contador += 1
                    if contador == len(posiciones_restantes):
                        break  # Si el tamaño del hijo se ha completado, paramos
                else:
                    break  # No hay más nodos restantes para insertar
            
            #Es ciclico
            hijo[0]=padre1[0]
            hijo[-1]=padre1[0]

            # Verificar si el hijo generado cumple con el tiempo máximo permitido
            if self.verificar_tiempo_hijo(hijo):
                return hijo
            intentos += 1

        # Si después de 10 intentos no se genera un hijo válido, se devuelve el mejor padre
        return mejor_padre


    def verificar_tiempo_hijo(self, hijo):
        
        #if len(hijo) <= 3:
        #    return self.nodos_df.at[hijo[0], 'tiempo_de_visita'] 
        
        tiempo_total = 0
        for i, nodo in enumerate(hijo[:-1]):
            tiempo_viaje = (self.distancias_df.loc[hijo[i], str(hijo[i + 1])])/self.velocidad
            tiempo_total += tiempo_viaje + self.nodos_df.at[nodo, 'tiempo_de_visita']
        # Incluir el tiempo de visita del último nodo
        tiempo_total += self.nodos_df.loc[hijo[-1], 'tiempo_de_visita']
        return tiempo_total <= self.tiempo_max

    
    def mutacion_intercambio(self, solucion):
            
     
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
    
    def mutacion_intercambio_ciclico(self, solucion):
        
        if len(solucion) <= 3:
            return solucion  # Devolver la solución actual sin cambios si no es posible excluir ambos

            
        # Seleccionar un nodo aleatorio de la solución actual para ser reemplazado
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

        

        tiempo_total = self.calcular_tiempo_total(vecino_potencial)
    

            # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            #print("En solucion original:",nodo_a_reemplazar)
            #print("Insertamos:",nuevo_nodo)
            #print("En posicion:",index_a_reemplazar)
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
        return solucion
    
    def mutacion_añado(self, solucion):

      
            # Lista de nodos posibles para el reemplazo, excluyendo los ya presentes en la solución
        nodos_posibles = [nodo for nodo in self.nodos_df.index if nodo not in solucion]

            # Si no hay nodos disponibles para el reemplazo, devolver la solución actual sin cambios
        if not nodos_posibles:
            return solucion

            # Seleccionar un nuevo nodo de los nodos posibles para reemplazar en la solución
        nuevo_nodo = random.choice(nodos_posibles)

          
        vecino_potencial = solucion[:]
        vecino_potencial.append(nuevo_nodo)
       

        tiempo_total = self.calcular_tiempo_total(vecino_potencial)
    

            # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            #print("En solucion original:",nodo_a_reemplazar)
            #print("Insertamos:",nuevo_nodo)
            #print("En posicion:",index_a_reemplazar)
         
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
        return solucion
    
    def mutacion_añado_ciclico(self, solucion):
        # Lista de nodos posibles para el reemplazo, excluyendo los ya presentes en la solución
        nodos_posibles = [nodo for nodo in self.nodos_df.index if nodo not in solucion]

        # Si no hay nodos disponibles para el reemplazo, devolver la solución actual sin cambios
        if not nodos_posibles:
            return solucion

        # Seleccionar un nuevo nodo de los nodos posibles para reemplazar en la solución
        nuevo_nodo = random.choice(nodos_posibles)

        vecino_potencial = solucion[:]
        # Insertar el nuevo nodo en la penúltima posición
        vecino_potencial.insert(-1, nuevo_nodo)

        tiempo_total = self.calcular_tiempo_total(vecino_potencial)

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            return vecino_potencial  # Devolver la solución propuesta si es válida
        
        return solucion

    
    def calcular_tiempo_total(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += (self.distancias_df.loc[solucion[i], str(solucion[i + 1])])/self.velocidad      
        return tiempo_total
    
    def calcular_tiempo_beneficio_distancia_total(self, solucion):
        tiempo_actual = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        distancia_total = 0
        beneficio_actual = self.nodos_df.loc[solucion[0], 'interes']
        
     
        for i in range(len(solucion) - 1):
            tiempo_actual += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_actual += (self.distancias_df.loc[solucion[i], str(solucion[i + 1])])/self.velocidad     
            distancia_total += self.distancias_df.loc[solucion[i], str(solucion[i + 1])]
            beneficio_actual += self.nodos_df.loc[solucion[i + 1], 'interes']
            
        return tiempo_actual, distancia_total, beneficio_actual


    def aplicar_algoritmo_memetico(self, max_iteraciones=500):
        self.inicializar_poblacion()
        generaciones = 0
        while generaciones < max_iteraciones:  # Criterio de terminación simplificado
            padres = self.seleccion_torneo()
            #print("Padres: ", padres)
            # Realizamos dos cruces ya que el tamaño de los padres no tiene porque ser el mismo 
            hijo1 = self.cruce(padres[0], padres[1])
            hijo2 = self.cruce(padres[1], padres[0])
            #print("Hijo 1: ", hijo1)
            #print("Hijo 2: ", hijo2)
            # Aplicar mutación con cierta probabilidad
            if random.random() < 0.1:
                hijo1 = self.mutacion_intercambio(hijo1)
                #print("Hijo 1 mutado: ", hijo1)
                hijo1 = self.mutacion_añado(hijo1)
                #print("Hijo 1 mutado: ", hijo1)
            if random.random() < 0.1:
                hijo2 = self.mutacion_intercambio(hijo2)
                #print("Hijo 2 mutado: ", hijo2)
                hijo2 = self.mutacion_añado(hijo2)
                #print("Hijo 2 mutado: ", hijo1)
            # Evaluar y seleccionar para la próxima generación
            self.poblacion += [hijo1, hijo2]
            # Ordenamos segun el valor de fitness
            self.poblacion = sorted(self.poblacion, key=self.calcular_fitness_cromosoma, reverse=True)[:self.poblacion_size]
            generaciones += 1
            
            if generaciones % 10 == 0:
                mejores = self.poblacion[:int(np.ceil(self.poblacion_size * 0.1))]
                #print("Mejores cromosomas seleccionados para búsqueda local:")
                #print(mejores)
                for cromosoma in mejores:
                    cromosoma_mejorado = self.buscar_local_dlb(cromosoma)
                    self.poblacion.append(cromosoma_mejorado)

            
        self.visitados =  max(self.poblacion, key=self.calcular_beneficio_cromosoma)  # Devuelve el mejor cromosoma, aunque antes hayamos usado el fitness ahora usamos el beneficio por que es lo que hemos hecho en el resto de algoritmos
        tiempo_actual, distancia_total, beneficio_actual = self.calcular_tiempo_beneficio_distancia_total(self.visitados)
        
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
    
    def buscar_local_dlb(self, solucion):
        # Hacer una copia de la solución actual
        mejor_solucion = solucion[:]
        mejor_tiempo = self.calcular_tiempo_total(mejor_solucion)
        dlb = [0] * len(mejor_solucion)  # Inicializar la máscara DLB
        
        mejor_encontrada = True
        j=0
      
        # Iterar a través de los nodos de la solución
        while j < MAX_ITERACIONES and mejor_encontrada:
        
            mejor_encontrada = False
            
            for i in range(0, len(mejor_solucion) - 1): 
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
                    

        return mejor_solucion

    def calcular_tiempo_total(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += (self.distancias_df.loc[solucion[i], str(solucion[i + 1])])/self.velocidad 
        return tiempo_total
    
   
    def aplicar_algoritmo_memetico_ciclico(self, nodo_ciclico, max_iteraciones=500):
        self.inicializar_poblacion_ciclico(nodo_ciclico)
        generaciones = 0
        while generaciones < max_iteraciones: 
            padres = self.seleccion_torneo()
            #print("Padres: ", padres)
            # Realizamos dos cruces ya que el tamaño de los padres no tiene porque ser el mismo 
            hijo1 = self.cruce_ciclico(padres[0], padres[1])
            hijo2 = self.cruce_ciclico(padres[1], padres[0])
            #print("Hijo 1: ", hijo1)
            #print("Hijo 2: ", hijo2)
            # Aplicar mutación con cierta probabilidad
            if random.random() < 0.1:
                hijo1 = self.mutacion_intercambio_ciclico(hijo1)
                #print("Hijo 1 mutado: ", hijo1)
                hijo1 = self.mutacion_añado_ciclico(hijo1)
                #print("Hijo 1 mutado: ", hijo1)
            if random.random() < 0.1:
                hijo2 = self.mutacion_intercambio_ciclico(hijo2)
                #print("Hijo 2 mutado: ", hijo2)
                hijo2 = self.mutacion_añado_ciclico(hijo2)
                #print("Hijo 2 mutado: ", hijo1)
            # Evaluar y seleccionar para la próxima generación
            self.poblacion += [hijo1, hijo2]
            # Ordenamos segun el valor de fitness
            self.poblacion = sorted(self.poblacion, key=self.calcular_fitness_cromosoma, reverse=True)[:self.poblacion_size]
            generaciones += 1
            
            if generaciones % 10 == 0:
                mejores = self.poblacion[:int(np.ceil(self.poblacion_size * 0.1))]
                #print("Mejores cromosomas seleccionados para búsqueda local:")
                #print(mejores)
                for cromosoma in mejores:
                    cromosoma_mejorado = self.buscar_local_dlb_ciclico(cromosoma)
                    self.poblacion.append(cromosoma_mejorado)

        self.visitados =  max(self.poblacion, key=self.calcular_beneficio_cromosoma)  # Devuelve el mejor cromosoma, aunque antes hayamos usado el fitness ahora usamos el beneficio por que es lo que hemos hecho en el resto de algoritmos
        tiempo_actual, distancia_total, beneficio_actual = self.calcular_tiempo_beneficio_distancia_total(self.visitados)
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual

  
    def buscar_local_dlb_ciclico(self, solucion):
        # Hacer una copia de la solución actual
        mejor_solucion = solucion[:]
        mejor_tiempo, tmp = self.calcular_tiempo_total_ciclico(mejor_solucion)
        dlb = [0] * len(mejor_solucion)  # Inicializar la máscara DLB
        
        mejor_encontrada = True
        j=0
      
        # Iterar a través de los nodos de la solución
        while j < MAX_ITERACIONES and mejor_encontrada:
        
            mejor_encontrada = False
            
            for i in range(1, len(mejor_solucion) - 1):  # El nodo inicial se mantiene fijo
                if dlb[i] == 0:  # Solo considerar este nodo si su DLB está en 0
                    improve_flag = False
                    for j in range(1, len(mejor_solucion)):  # Considerar todos los otros nodos
                        if i != j:  # Asegurarse de no intercambiar el nodo consigo mismo
                            # Intercambiar nodos
                            mejor_solucion[i], mejor_solucion[j] = mejor_solucion[j], mejor_solucion[i]
                            tiempo_actual, tmp_vuelta = self.calcular_tiempo_total_ciclico(mejor_solucion)

                            # Si no se encuentra una mejora, revertir el intercambio
                            if tiempo_actual < mejor_tiempo:
                                mejor_tiempo = tiempo_actual  # Actualizar el mejor tiempo
                                
                                #print("ANTES:", str(mejor_tiempo))
                                
                                #tiempo_vuelta = (self.distancias_df.loc[mejor_solucion[-1],str(mejor_solucvelocidadon[0])]    
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
                     
                    

        return mejor_solucion

    def calcular_tiempo_total_ciclico(self, solucion):
        tiempo_total = self.nodos_df.loc[solucion[0], 'tiempo_de_visita']
        for i in range(len(solucion) - 1):
            tiempo_total += self.nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
            tiempo_total += (self.distancias_df.loc[solucion[i], str(solucion[i + 1])])/self.velocidad
        tiempo_vuelta = (self.distancias_df.loc[solucion[-1],str(solucion[0])])/self.velocidad
        tiempo_total = tiempo_total + tiempo_vuelta
        #print("FINAL ES:", str(solucion[-1]))
        #print("NODO INICIO ES:", str(solucion[0]))
        #print("tiempo ES:", str(tiempo_vuelta))
               
        
        return tiempo_total, tiempo_vuelta
    

           