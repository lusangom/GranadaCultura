import pandas as pd
import numpy as np
import random
import funciones
import time

class AlgoritmoGeneticoEstacionario:
    def __init__(self, nodos_df, distancias_df, tiempos_df, tiempo_max, velocidad, poblacion_size=50, RANDOM_SEED=None, intentos_cruce=10, max_iteraciones=500, porcentaje_mutacion=0.2, max_intentos_poblacion=100):
        """
        Inicializa la clase Algoritmo Genetico Estacionario.
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
        self.intentos_cruce = intentos_cruce
        self.MAX_ITERACIONES = max_iteraciones
        self.porcentaje_mutacion = porcentaje_mutacion
        self.max_intentos_poblacion = max_intentos_poblacion
        if RANDOM_SEED is not None:
            random.seed(RANDOM_SEED)
        else: #Para que no se repitan los resultados
            semilla_actual = int(time.time())
            random.seed(semilla_actual)
           
    
    def inicializar_poblacion(self):
        """Función inicializa población.

        Función usada para generar la población inicial aleatoria de nuestro algoritmo.
        Se generan tantas soluciones como tamaño de población se indique en la inicialización.
        
       
        """
        intentos = 0
     
        while len(self.poblacion) < self.poblacion_size and intentos < self.max_intentos_poblacion:
            cromosoma = self.generar_cromosoma()
            tiempo_cromosoma = funciones.calcular_tiempo_total(cromosoma, self.nodos_df, self.distancias_df, self.velocidad)
            if tiempo_cromosoma <= self.tiempo_max:
                self.poblacion.append(cromosoma)
            else:
                intentos = intentos + 1
             
                
    def inicializar_poblacion_ciclico(self,nodo_ciclico):
        """Función inicializa población ciclica.

        Función usada para generar la población inicial aleatoria ciclica de nuestro algoritmo.
        Se generan tantas soluciones como tamaño de población se indique en la inicialización.
        
        Args:
            nodo_ciclico (int): Número que representa el nodo ciclico
        """
        intentos = 0
     
        while len(self.poblacion) < self.poblacion_size and intentos < self.max_intentos_poblacion:
            cromosoma = self.generar_cromosoma_ciclico(nodo_ciclico)
            tiempo_cromosoma = funciones.calcular_tiempo_total(cromosoma, self.nodos_df, self.distancias_df, self.velocidad)
            if tiempo_cromosoma <= self.tiempo_max:
                self.poblacion.append(cromosoma)
            else:
                intentos = intentos + 1
                
   

      
    def generar_cromosoma(self):
        """Función generar cromosoma.

        Función usada para generar un cromosoma en nuestra población. El cromosoma sera un array solución
        que cumpla los requisitos de tiempo.

        Returns:
            Array: Posible ruta solución.
        """
        
        # Inicializamos solución y variables correspondientes
        cromosoma = []
        tiempo_actual = 0
        nodo_inicial = self.nodos_df['interes'].idxmax()
        cromosoma.append(nodo_inicial)
        tiempo_actual += self.nodos_df.at[nodo_inicial, 'tiempo_de_visita']
        
        # Obtenemos la lista de nodos disponibles
        nodos_disponibles =  [nodo for nodo in self.nodos_df.index if nodo not in cromosoma]
       
        # Mientras que haya nodos disponibles que cumplan los requisitos de tiempo los añadimos a nuestro cromosoma
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
        """Función generar cromosoma ciclico.

        Función usada para generar un cromosoma ciclico en nuestra población. El cromosoma sera un array solución
        que cumpla los requisitos de tiempo.
        
        Args:
            nodo_ciclico (int): Número que representa el nodo ciclico

        Returns:
            Array: Posible ruta solución.
        """
        
        # El procedimiento de ejecución es igual que la función anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        cromosoma = [nodo_ciclico]
        tiempo_actual = 0
        nodo_inicial = nodo_ciclico
        tiempo_actual += self.nodos_df.at[nodo_inicial, 'tiempo_de_visita']
        
        nodos_disponibles =  [nodo for nodo in self.nodos_df.index if nodo not in cromosoma]
       
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
    
   
    def seleccion_torneo(self):
        """Función selección torneo.

        Función usada para selecciona dos padres mediante torneo. En el esquema estacionario, 
        se aplicará dos veces el torneo para elegir los dos padres que serán posteriormente recombinados (cruzados).
      
        Returns:
            Array de dos arrays: Los dos padres con una ruta solución.
        """
        padres = []
        for _ in range(2):
            candidatos = random.choices(self.poblacion, k=2)
            candidato_fitness = [funciones.calcular_fitness_total(c, self.distancias_df, self.velocidad, self.nodos_df) for c in candidatos]
            padres.append(candidatos[np.argmax(candidato_fitness)])
     
        return padres

    def cruce(self, padre1, padre2):
        """Función cruce.

        Función usada para cruzar dos padres.  El operador de cruce escogido es el operador de cruce basado 
        en posición en el cual, aquellas posiciones que contengan el mismo valor en ambos padres se mantienen 
        en el hijo (para preservar las asignaciones prometedoras). Las asignaciones restantes se seleccionan 
        en un orden aleatorio para completar el hijo

        Args:
            padre1 (array): Array con una posible ruta solución que representa el padre 1
            padre2 (array): Array con una posible ruta solución que representa el padre 2
            
        Returns:
            Array: Array hijo con el cruce de los dos padres
        """
        mejor_padre = padre1 if funciones.calcular_fitness_total(padre1, self.distancias_df, self.velocidad, self.nodos_df) > funciones.calcular_fitness_total(padre2, self.distancias_df, self.velocidad, self.nodos_df) else padre2
        intentos = 0
        while intentos < self.intentos_cruce:  # Máximo de 10 intentos para generar un hijo válido
            
            hijo = [None] * max(len(padre1), len(padre2))  # Selecciona el tamaño máximo entre los dos padres ya que los padres no tienen porque tener el mismo tamaño
            # Mantener posiciones iguales
            for i in range(min(len(padre1), len(padre2))):
                if padre1[i] == padre2[i]:
                    hijo[i] = padre1[i]

            # Miramos las posiciones que todavía no estan completas
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

            es_ciclico = False
            # Verificar si el hijo generado cumple con el tiempo máximo permitido
            if funciones.verificar_tiempo_hijo(hijo, self.distancias_df, self.velocidad, self.nodos_df, self.tiempo_max, es_ciclico):
                return hijo
            intentos += 1

        # Si después de 10 intentos no se genera un hijo válido, se devuelve el mejor padre
        return mejor_padre
    
    def cruce_ciclico(self, padre1, padre2):
        """Función cruce ciclico.

        Función usada para cruzar dos padres ciclicos.  El operador de cruce escogido es el operador de cruce basado 
        en posición en el cual, aquellas posiciones que contengan el mismo valor en ambos padres se mantienen 
        en el hijo (para preservar las asignaciones prometedoras). Las asignaciones restantes se seleccionan 
        en un orden aleatorio para completar el hijo

        Args:
            padre1 (array): Array con una posible ruta solución que representa el padre 1
            padre2 (array): Array con una posible ruta solución que representa el padre 2
            
        Returns:
            Array: Array hijo ciclico con el cruce de los dos padres
        """
        
        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        mejor_padre = padre1 if funciones.calcular_fitness_total(padre1, self.distancias_df, self.velocidad, self.nodos_df) > funciones.calcular_fitness_total(padre2, self.distancias_df, self.velocidad, self.nodos_df) else padre2
        intentos = 0
        while intentos < self.intentos_cruce:  # Máximo de 10 intentos para generar un hijo válido
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
            
            # Es ciclico por lo que establecemos la ultima y primera posición con el nodo ciclico
            hijo[0]=padre1[0]
            hijo[-1]=padre1[0]
            es_ciclico = True
            
            # Verificar si el hijo generado cumple con el tiempo máximo permitido
            if funciones.verificar_tiempo_hijo(hijo, self.distancias_df, self.velocidad, self.nodos_df, self.tiempo_max, es_ciclico):
                return hijo
            intentos += 1

        # Si después de 10 intentos no se genera un hijo válido, se devuelve el mejor padre
        return mejor_padre


  
    def mutacion_intercambio(self, solucion):
        """Función mutación intercambio.

        Función usada para mutar la solución. La mutacion consiste en intercambiar un nodo de nuestra solución 
        con uno que no este todavia. 
        El funcionamiento de esta función es análogo a la función generar vecino del algoritmo de Enfriamiento Simulado.
        
        Args:
            Solucion (Array): Ruta a la que se le va a realizar la mutación.
        
        Returns:
            Array: Ruta con mutación realizada si es factible.
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

        

        tiempo_total = funciones.calcular_tiempo_total(vecino_potencial,self.nodos_df, self.distancias_df,self.velocidad)
    

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
        return solucion
    
    def mutacion_intercambio_ciclico(self, solucion):
        """Función mutación intercambio ciclico.

        Función usada para mutar la solución ciclcia. La mutacion consiste en intercambiar un nodo de nuestra solución 
        con uno que no este todavia, manteniendo el nodo de inicial y final fijo. 
        El funcionamiento de esta función es análogo a la función generar vecino ciclico del algoritmo de Enfriamiento Simulado.
        
        Args:
            Solucion (Array): Ruta a la que se le va a realizar la mutación.
        
        Returns:
            Array: Ruta con mutación realizada si es factible.
        """
        
        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        
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


        tiempo_total = funciones.calcular_tiempo_total(vecino_potencial,self.nodos_df, self.distancias_df,self.velocidad)

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
        return solucion
    
    def mutacion_añado(self, solucion):
        """Función mutación añado.

        Función usada para mutar la solución. La mutacion consiste en añadir al final de nuestra solución
        un nodo que no este presente todavia en la solución
        
        Args:
            Solucion (Array): Ruta a la que se le va a realizar la mutación.
        
        Returns:
            Array: Ruta con mutación realizada si es factible.
        """
      
        # Lista de nodos posibles para el reemplazo, excluyendo los ya presentes en la solución
        nodos_posibles = [nodo for nodo in self.nodos_df.index if nodo not in solucion]

        # Si no hay nodos disponibles para el reemplazo, devolver la solución actual sin cambios
        if not nodos_posibles:
            return solucion

        # Seleccionar un nuevo nodo de los nodos posibles para reemplazar en la solución
        nuevo_nodo = random.choice(nodos_posibles)          
        vecino_potencial = solucion[:]
        vecino_potencial.append(nuevo_nodo)
       

        tiempo_total = funciones.calcular_tiempo_total(vecino_potencial,self.nodos_df, self.distancias_df,self.velocidad)


        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
         
            return vecino_potencial  # Devolver la solución propuesta si es válida
            
        return solucion
    
    def mutacion_añado_ciclico(self, solucion):
        """Función mutación añado ciclica.

        Función usada para mutar la solución ciclica. La mutacion consiste en añadir en la penúltima posición
        de nuestra solución un nodo que no este presente todavia en la solución.
        Manteniendo el nodo inicial y ultimo fijos.
        
        Args:
            Solucion (Array): Ruta a la que se le va a realizar la mutación.
        
        Returns:
            Array: Ruta con mutación realizada si es factible.
        """
      
        # El procedimiento de ejecución es igual que el anterior pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
      
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

        tiempo_total = funciones.calcular_tiempo_total(vecino_potencial,self.nodos_df, self.distancias_df,self.velocidad)
    

        # Comprobar si la solución propuesta cumple con el requisito de tiempo máximo
        if tiempo_total <= self.tiempo_max:
            return vecino_potencial  # Devolver la solución propuesta si es válida
        
        return solucion

  

    def aplicar_algoritmo_genetico(self):
        """Función algoritmo genetico.

        Función para aplicar el algoritmo genetico.

        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        # Inicializamos la población
        self.inicializar_poblacion()
        generaciones = 0
        
        # A nuestra población le aplicamos el cruce y las mutaciones correspondientes mientras queden generaciones
        while generaciones < self.MAX_ITERACIONES:  
            padres = self.seleccion_torneo() 
            
            # Realizamos dos cruces ya que esto aumenta la diversificación de nuestra población
            hijo1 = self.cruce(padres[0], padres[1])
            hijo2 = self.cruce(padres[1], padres[0])
            
            # Añadimos a la poblacion para aumentar diversidad
            tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
            if(tiempo_hijo1 <= self.tiempo_max):
                self.poblacion += [hijo1]
            tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
            if(tiempo_hijo2 <= self.tiempo_max):
                self.poblacion += [hijo2]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo1 = self.mutacion_intercambio(hijo1)
                tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
                if(tiempo_hijo1 <= self.tiempo_max):
                    self.poblacion += [hijo1]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo1 = self.mutacion_añado(hijo1)
                tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
                if(tiempo_hijo1 <= self.tiempo_max):
                    self.poblacion += [hijo1]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad  
            if random.random() < self.porcentaje_mutacion:
                hijo2 = self.mutacion_intercambio(hijo2)
                tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
                if(tiempo_hijo2 <= self.tiempo_max):
                    self.poblacion += [hijo2]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo2 = self.mutacion_añado(hijo2)
                tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
                if(tiempo_hijo2 <= self.tiempo_max):
                    self.poblacion += [hijo2]
              

            # Ordenamos segun el valor de fitness
            self.poblacion = sorted(self.poblacion, key=lambda c:funciones.calcular_fitness_total(c, distancias_df=self.distancias_df, velocidad=self.velocidad, nodos_df=self.nodos_df), reverse=True)[:len(self.poblacion)]
            generaciones += 1
            
        # Cuando acabemos todas las generaciones nos quedamos con la mejor generación 
        self.visitados =  max(self.poblacion, key=lambda c:funciones.calcular_beneficio_total(c, self.nodos_df))  # Devuelve el mejor cromosoma, aunque antes hayamos usado el fitness ahora usamos el beneficio por que es lo que hemos hecho en el resto de algoritmos
        tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
        distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
        beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
   
    def aplicar_algoritmo_genetico_ciclico(self, nodo_ciclico):
        """Función algoritmo genetico ciclico.

        Función para aplicar el algoritmo genetico ciclico.
        
        Args:
            nodo_ciclico (int): Número que representa el nodo ciclico


        Returns:
            Array: Ruta solución y la información asociada a ella.
        """
        
        # El procedimiento de ejecución es igual que el algoritmo GRASP pero esta vez, se considera un nodo cíclico.
        # Es decir se específica un nodo que tiene que ser el de inicio y el de fin.
        
        self.inicializar_poblacion_ciclico(nodo_ciclico)
        generaciones = 0
        while generaciones < self.MAX_ITERACIONES:
            padres = self.seleccion_torneo()
          
            # Realizamos dos cruces ya que esto aumenta la diversificación de nuestra población
            hijo1 = self.cruce_ciclico(padres[0], padres[1])
            hijo2 = self.cruce_ciclico(padres[1], padres[0])
            
            # Añadimos a la poblacion para aumentar diversidad ademas hacemos comprobaciones adicionales
            tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
            if tiempo_hijo1 <= self.tiempo_max and hijo1[0] == nodo_ciclico and hijo1[-1] == nodo_ciclico:
                self.poblacion += [hijo1]
            tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
            if tiempo_hijo2 <= self.tiempo_max and hijo2[0] == nodo_ciclico and hijo2[-1] == nodo_ciclico:
                self.poblacion += [hijo2]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo1 = self.mutacion_intercambio(hijo1)
                tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
                if tiempo_hijo1 <= self.tiempo_max and hijo1[0] == nodo_ciclico and hijo1[-1] == nodo_ciclico:
                    self.poblacion += [hijo1]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo1 = self.mutacion_añado(hijo1)
                tiempo_hijo1 = funciones.calcular_tiempo_total(hijo1, self.nodos_df, self.distancias_df, self.velocidad)
                if tiempo_hijo1 <= self.tiempo_max and hijo1[0] == nodo_ciclico and hijo1[-1] == nodo_ciclico:
                    self.poblacion += [hijo1]
            
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad  
            if random.random() < self.porcentaje_mutacion:
                hijo2 = self.mutacion_intercambio(hijo2)
                tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
                if tiempo_hijo2 <= self.tiempo_max and hijo2[0] == nodo_ciclico and hijo2[-1] == nodo_ciclico:
                    self.poblacion += [hijo2]
                    
            # Aplicar mutación con cierta probabilidad y añadimos a la poblacion para aumentar diversidad
            if random.random() < self.porcentaje_mutacion:
                hijo2 = self.mutacion_añado(hijo2)
                tiempo_hijo2 = funciones.calcular_tiempo_total(hijo2, self.nodos_df, self.distancias_df, self.velocidad)
                if tiempo_hijo2 <= self.tiempo_max and hijo2[0] == nodo_ciclico and hijo2[-1] == nodo_ciclico:
                    self.poblacion += [hijo2]
         
         
            # Ordenamos segun el valor de fitness
            self.poblacion = sorted(self.poblacion, key=lambda c:funciones.calcular_fitness_total(c, distancias_df=self.distancias_df, velocidad=self.velocidad, nodos_df=self.nodos_df), reverse=True)[:len(self.poblacion)]
            generaciones += 1
        self.visitados =  max(self.poblacion, key=lambda c:funciones.calcular_beneficio_total(c, self.nodos_df))  # Devuelve el mejor cromosoma, aunque antes hayamos usado el fitness ahora usamos el beneficio por que es lo que hemos hecho en el resto de algoritmos
        tiempo_actual = funciones.calcular_tiempo_total(self.visitados, self.nodos_df, self.distancias_df, self.velocidad)
        distancia_total = funciones.calcular_distancia_total(self.visitados, self.distancias_df)
        beneficio_actual = funciones.calcular_beneficio_total(self.visitados, self.nodos_df)
        return self.visitados, tiempo_actual, distancia_total, beneficio_actual
   