    
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