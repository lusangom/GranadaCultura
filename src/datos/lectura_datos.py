import pandas as pd

class Datos:
    def __init__(self, archivo_nodos, archivo_distancias, archivo_tiempos):
        """
        Inicializa la clase con las rutas a los archivos CSV.
        """
        self.archivo_nodos = archivo_nodos
        self.archivo_distancias = archivo_distancias
        self.archivo_tiempos = archivo_tiempos

    def cargar_nodos(self):
        """
        Carga los datos de los nodos desde un archivo CSV.
        Retorna un DataFrame de pandas.
        """
        try:
            nodos_df = pd.read_csv(self.archivo_nodos)
            print("Datos de nodos cargados exitosamente.")
            return nodos_df
        except FileNotFoundError:
            print(f"Error: El archivo {self.archivo_nodos} no fue encontrado.")
            return None

    def cargar_distancias(self):
        """
        Carga la matriz de distancias entre nodos desde un archivo CSV.
        Retorna un DataFrame de pandas.
        """
        try:
            distancias_df = pd.read_csv(self.archivo_distancias)
            print("Matriz de distancias cargada exitosamente.")
            return distancias_df
        except FileNotFoundError:
            print(f"Error: El archivo {self.archivo_distancias} no fue encontrado.")
            return None

    def cargar_tiempos(self):
        """
        Carga la matriz de tiempos entre nodos desde un archivo CSV.
        Retorna un DataFrame de pandas.
        """
        try:
            tiempos_df = pd.read_csv(self.archivo_tiempos)
            print("Matriz de tiempos cargada exitosamente.")
            return tiempos_df
        except FileNotFoundError:
            print(f"Error: El archivo {self.archivo_tiempos} no fue encontrado.")
            return None

    def visualizar_nodos(self):
        """
        Muestra el contenido del DataFrame de nodos.
        """
        nodos_df = self.cargar_nodos()
        if nodos_df is not None:
            print('Puntos de interes \n')
            print(nodos_df)

    def visualizar_distancias(self):
        """
        Muestra el contenido del DataFrame de distancias.
        """
        distancias_df = self.cargar_distancias()
        if distancias_df is not None:
            print('Distancias \n')
            print(distancias_df)
            
    def visualizar_tiempos(self):
        """
        Muestra el contenido del DataFrame de tiempos.
        """
        tiempos_df = self.cargar_tiempos()
        if tiempos_df is not None:
            print('Tiempos \n')
            print(tiempos_df)
            
    #Funciones auxiliares       
    def calcula_tiempos(self, ruta_guardado):
        """
        Divide los datos de distancias entre 75.
        Muestra el resultado.
        """
        distancias_df = self.cargar_distancias()
        if distancias_df is not None:
            
            # Divide los datos de distancias entre 75
            distancias_divididas = distancias_df / 75.0
            
            # Muestra el resultado
            print("Datos de distancias divididos entre 75:")
            print(distancias_divididas)
          
            
              # Guarda el resultado en un nuevo archivo CSV
            try:
                distancias_divididas.to_csv(ruta_guardado, index=False)
                print(f"Datos de distancias divididos guardados exitosamente en {ruta_guardado}.")
            except Exception as e:
                print(f"Error al guardar los datos de distancias divididos: {e}")
    
     
  
    def int_to_float(self, ruta_guardado):
        """
        Comprueba los valores de las casillas de la matriz de distancias.
        Si el valor es mayor que 20000, divide esa casilla por 1000.
        Guarda el archivo generado.
        """
        distancias_df = self.cargar_distancias()
        if distancias_df is not None:
            # Copia la matriz de distancias para evitar cambios en el original
            distancias_modificadas = distancias_df.copy()

            # Itera sobre cada celda de la matriz de distancias
            for i in range(len(distancias_modificadas)):
                for j in range(len(distancias_modificadas.columns)):
                    valor = distancias_modificadas.iloc[i, j]
                    # Comprueba si el valor es mayor que 20000
                    if valor > 20000:
                        # Divide la casilla por 1000
                        distancias_modificadas.iloc[i, j] /= 1000

            # Guarda la matriz de distancias modificada en un nuevo archivo CSV
            try:
                distancias_modificadas.to_csv(ruta_guardado, index=False)
                print(f"Matriz de distancias modificada guardada exitosamente en {ruta_guardado}.")
            except Exception as e:
                print(f"Error al guardar la matriz de distancias modificada: {e}")
                
     
    def change_distances(self, ruta_guardado):
        """
        Comprueba los valores de las casillas de la matriz de distancias.
        Si el valor es mayor que 20000, divide esa casilla por 1000.
        Guarda el archivo generado.
        """
        distancias_df = self.cargar_distancias()
        if distancias_df is not None:
            # Copia la matriz de distancias para evitar cambios en el original
            distancias_modificadas = distancias_df.copy()

            # Itera sobre cada celda de la matriz de distancias
            for i in range(len(distancias_modificadas)):
                for j in range(len(distancias_modificadas.columns)):
                    valor = distancias_modificadas.iloc[i, j]
                    # Comprueba si el valor es mayor que 20000
                    if valor > 251:
                        # Divide la casilla por 1000
                        distancias_modificadas.iloc[i, j] /= 1000

            # Guarda la matriz de distancias modificada en un nuevo archivo CSV
            try:
                distancias_modificadas.to_csv(ruta_guardado, index=False)
                print(f"Matriz de distancias modificada guardada exitosamente en {ruta_guardado}.")
            except Exception as e:
                print(f"Error al guardar la matriz de distancias modificada: {e}")