    
def calcular_fitness(distancias_df, nodo_origen, nodo_destino, velocidad, nodos_df):
    """Calcular fitness entre dos nodos.

    Esta función calcula el fitness entre dos nodos: nodo origen y nodo destino. Este fitness viene dado por 
    el beneficio de visitar el nodo destino menos el tiempo que se tarda en llegar a ese nodo desde el nodo
    origen multiplicado por 0.1

    Args:
        distancias_df (matrix): Matriz con las distancias entre todos los nodos de la BBDD.
        nodo_origen (int): Entero que representa el nodo de origen en nuestra BBDD.
        nodo_destino (int): Entero que representa el nodo de destino en nuestra BBDD.
        velocidad (int): Entero que representa la velocidad a la que anda el usuario según la edad.
        nodos_df (matrix): Matriz con la información del interes de los nodos.

    Returns:
        float: Número que representa el fitness entre los nodos.
    """
    tiempo_viaje = (distancias_df.loc[nodo_origen, str(nodo_destino)])/velocidad
    tiempo_viaje = tiempo_viaje * 0.1
    beneficio = nodos_df.loc[nodo_destino, 'interes']
       
    fitness = beneficio - tiempo_viaje
    return fitness


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
        float: Número que representa el tiempo total para recorrer la funcion en minutos.
    """
    tiempo_total = nodos_df.loc[solucion[0], 'tiempo_de_visita']
        
    for i in range(len(solucion) - 1):
        tiempo_total += nodos_df.loc[solucion[i + 1], 'tiempo_de_visita']
        tiempo_total += (distancias_df.loc[solucion[i], str(solucion[i + 1])])/velocidad
            
    return tiempo_total


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
        float: Número que representa la distancia total de una solución en metros.  
    """
    beneficio_total = 0
    for i in range(len(solucion)):
        nodo = solucion[i]
        beneficio_total += nodos_df.loc[nodo, 'interes']
    return beneficio_total
    
    