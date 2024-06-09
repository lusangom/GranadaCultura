    
def calcular_factor_decision(distancias_df, nodo_origen, nodo_destino, velocidad, nodos_df):
    """Calcular factor de decision entre dos nodos.

    Esta función calcula el factor de decision entre dos nodos: nodo origen y nodo destino. Este factor de decision viene dado por 
    el beneficio de visitar el nodo destino menos el tiempo que se tarda en llegar a ese nodo desde el nodo
    origen multiplicado por 0.1

    Args:
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        nodo_origen (int): Entero que representa el nodo de origen en nuestra BBDD.
        nodo_destino (int): Entero que representa el nodo de destino en nuestra BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el factor entre los nodos.
    """
    tiempo_viaje = (distancias_df.loc[nodo_origen, str(nodo_destino)])/velocidad
    tiempo_viaje = tiempo_viaje * 0.1
    beneficio = nodos_df.loc[nodo_destino, 'interes']
       
    factor_decision = beneficio - tiempo_viaje
    return factor_decision

def calcular_factor_decision_total(cromosoma, distancias_df, velocidad, nodos_df):
    """Calcular factor de decision total de una solución.

    Esta función se encarga de calcular el factor de decision total de una solución. Este factor de decision viene dado por 
    el beneficio de visitar el nodo destino menos el tiempo que se tarda en llegar a ese nodo desde el nodo
    origen multiplicado por 0.1

    Args:
        cromosoma (array): Ruta solución actual
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el factor de decision total de la solución.
    """
    factor_decision_total = 0
    for i, nodo in enumerate(cromosoma[:-1]):
        tiempo_viaje = (distancias_df.loc[cromosoma[i], str(cromosoma[i+1])])/velocidad            
        factor_decision_total += nodos_df.loc[nodo, 'interes'] - tiempo_viaje*0.1
    return factor_decision_total

def calcular_tiempo_total(solucion, nodos_df, distancias_df, velocidad):
    """Calcular tiempo total de duracion de una solucion en minutos.

    Esta función se encarga de recorrer el array solución para calcular el tiempo total que se necesita
    para recorrerla teniendo en cuenta las distancias y la edad además del tiempo de visita

    Args:
        solucion (array): Array que representa la ruta solución.
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el tiempo total para recorrer la solucion en minutos.
    """
    tiempo_total = nodos_df.loc[solucion[0], 'tiempo_de_visita']
        
    for i in range(len(solucion) - 1):
        tiempo_total += nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
        tiempo_total += (distancias_df.loc[solucion[i], str(solucion[i + 1])])/velocidad
   
    return tiempo_total


def calcular_tiempo_total_ciclico(solucion, nodos_df, distancias_df, velocidad):
    """Calcular tiempo total de duracion de una solucion ciclica en minutos.

    Args:
        solucion (array): Array que representa la ruta solución.
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el tiempo total para recorrer la solucion ciclica en minutos.
        float: Número que representa el tiempo total para volver al nodo ciclico en minutos.
    """
  
    ultimo_nodo = 0
    tiempo_total =0   
    for i in range(len(solucion) - 1):
        tiempo_total += nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
        tiempo_total += (distancias_df.loc[solucion[i], str(solucion[i + 1])])/velocidad
        ultimo_nodo = solucion[i-1]
    
    tiempo_vuelta = (distancias_df.loc[ultimo_nodo,str(solucion[0])])/velocidad       
    
    tiempo_total = tiempo_total + tiempo_vuelta
        
    return tiempo_total, tiempo_vuelta


    

def calcular_distancia_total(solucion, distancias_df): 
    """Calcular distancia total de una solucion en metros.

    Esta función se encarga de recorrer el array solución para calcular la distancia total de la solución
    usando la matriz de información de distancias entre los nodos

    Args:
        solucion (array): Array que representa la ruta solución.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el interés total la solución.  
    """
    distancia_total = 0 
    for i in range(len(solucion) - 1):
        distancia_total += distancias_df.loc[solucion[i], str(solucion[i + 1])]
    return distancia_total

def calcular_beneficio_total(solucion, nodos_df):
    """Calcular el beneficio total de una solucion.

    Esta función se encarga de recorrer el array solución para calcular el interes total de la solucion
    usando la matriz de información de los POIS

    Args:
        solucion (array): Array que representa la ruta solución.
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.

    Returns:
        bool: Número que representa la distancia total de una solución en metros.  
    """
    beneficio_total = 0
    for i in range(len(solucion)):
        nodo = solucion[i]
        beneficio_total += nodos_df.loc[nodo, 'interes']
    return beneficio_total


def verificar_tiempo_hijo(hijo, distancias_df, velocidad, nodos_df, tiempo_max, es_ciclico):
    """Función verificar tiempo hijo.

    Función usada para comprobar si un hijo generado es correcto, es decir, que la solución 
    generada no sobrepasa los límites de tiempo.

    Args:
        hijo (array): Array que representa la ruta solución.
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.
        tiempo_max (int): Entero que representa el tiempo máximo del que disponemos para realizar la ruta.
        es_ciclico (bool): Booleano que representa si la ruta es ciclica o no

    Returns:
        float: Booleano que representa si el hijo es correcto (True) o no (False) en terminos de tiempo
            
    """
    tiempo_total = 0
    for i, nodo in enumerate(hijo[:-1]):
        try:
            tiempo_viaje = (distancias_df.at[hijo[i], str(hijo[i + 1])]) / velocidad
        except KeyError:
            return False
            
        tiempo_total += tiempo_viaje + nodos_df.at[nodo, 'tiempo_de_visita']
    # Si la ruta no es ciclica se incluye el tiempo de visita al ultimo nodo sino no
    if not es_ciclico: 
        tiempo_total += nodos_df.at[hijo[-1], 'tiempo_de_visita']
    return tiempo_total <= tiempo_max

