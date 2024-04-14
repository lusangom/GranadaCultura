import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse  # Importa argparse
import ast
from math import pi


def cargar_datos(ruta_archivo):
    """Carga los datos desde un archivo CSV.

    Args:
        ruta_archivo (str): La ruta del archivo CSV.

    Returns:
        pandas.DataFrame: Los datos cargados desde el archivo CSV.
    """
    return pd.read_csv(ruta_archivo)


def graficar_dispersion(resultados, x, y, titulo_comun="", hue='ALGORITMO'):
    """Genera un gráfico de dispersión.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        x (str): El nombre de la columna para el eje x.
        y (str): El nombre de la columna para el eje y.
        titulo_comun (str, optional): El título común para el gráfico. Por defecto, "".
        hue (str, optional): El nombre de la columna para agrupar colores. Por defecto, 'ALGORITMO'.
    """
    plt.figure()
    sns.scatterplot(data=resultados, x=x, y=y, hue=hue)
    plt.title(f'{titulo_comun}\nDispersión de {x} vs {y}')


def graficar_bigotes(resultados, y, x='ALGORITMO', titulo_comun=""):
    """Genera un diagrama de caja.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        y (str): El nombre de la columna para el eje y.
        x (str, optional): El nombre de la columna para agrupar en el eje x. Por defecto, 'ALGORITMO'.
        titulo_comun (str, optional): El título común para el gráfico. Por defecto, "".
    """
    plt.figure()
    sns.boxplot(x=x, y=y, data=resultados)
    plt.title(f'{titulo_comun}\nDiagrama de caja de {y}')
    plt.xticks(rotation=45)


def graficar_matriz_correlacion(resultados):
    """Genera una matriz de correlación entre variables.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
    """
    plt.figure()
    corr = resultados.select_dtypes(include=['float64', 'int']).corr()
    sns.heatmap(data=corr, annot=True, cmap='coolwarm')
    plt.title('Matriz de Correlación')


def graficar_diagrama_araña(resultados, titulo_comun=""):
    """Genera un diagrama de araña.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        titulo_comun (str, optional): El título común para el gráfico. Por defecto, "".
    """
    categorias = ['NUMERO DE POIS VISITADOS', 'INTERÉS', 'DISTANCIA TOTAL', 'TIEMPO TOTAL ALGORITMO', 'MARGEN', 'TIEMPO EJECUCION ALGORITMO']
    N = len(categorias)
    
    valores_maximos = resultados[categorias].max()
    resultados_normalizados = resultados[categorias] / valores_maximos
    
    promedios_por_algoritmo = resultados_normalizados.groupby(resultados['ALGORITMO']).mean().reset_index()
    
    angulos = [n / float(N) * 2 * pi for n in range(N)]
    angulos += angulos[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    for index, row in promedios_por_algoritmo.iterrows():
        valores = row.drop('ALGORITMO').values.flatten().tolist()
        valores += valores[:1]
        ax.plot(angulos, valores, linewidth=1, linestyle='solid', label=row['ALGORITMO'])
        ax.fill(angulos, valores, alpha=0.1)
    
    ax.set_thetagrids([n * 360.0 / N for n in range(N)], categorias)
    plt.title(titulo_comun + '\nDiagrama de Araña por Algoritmo')
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))


def graficar_matriz_pois(resultados, tamaño_bbdd, titulo_comun=""):
    """Genera una matriz de POIs visitados.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        tamaño_bbdd (int): El tamaño de la base de datos de POIs.
        titulo_comun (str, optional): El título común para el gráfico. Por defecto, "".
    """
    plt.figure()
    max_pois_visitados = resultados['POIS VISITADOS'].apply(lambda x: len(ast.literal_eval(x))).max()

    pois = range(1, tamaño_bbdd + 1)
    matriz_pois = pd.DataFrame(0, index=pois, columns=range(1, max_pois_visitados + 1))
    
    for index, row in resultados.iterrows():
        pois_visitados = ast.literal_eval(row['POIS VISITADOS'])
        for idx, poi in enumerate(pois_visitados, start=1):
            if poi in pois:
                matriz_pois.loc[poi, idx] += 1

    sns.heatmap(matriz_pois, cmap='Greys', cbar=True)
    plt.title(titulo_comun + '\nMatriz de POIs Visitados')
    plt.xlabel('Posición en la Solución')
    plt.ylabel('ID del POI')


def main(ruta_archivo):
    """Función principal para el análisis de resultados de algoritmos.

    Args:
        ruta_archivo (str): La ruta del archivo CSV con los resultados para análisis.
    """
    resultados = cargar_datos(ruta_archivo)
    tamaño_bbdd = resultados['TAMAÑO BBDD'].iloc[0] if 'TAMAÑO BBDD' in resultados.columns else 'Desconocido'
    tiempo_max = resultados['TIEMPO MAX'].iloc[0] if 'TIEMPO MAX' in resultados.columns else 'Desconocido'
    ciclica = resultados['RUTA CICLICA'].iloc[0] if 'RUTA CICLICA' in resultados.columns else 'Desconocido'
    edad = resultados['EDAD'].iloc[0] if 'EDAD' in resultados.columns else 'Desconocido'
    titulo_comun = f'BASE DE DATOS: {tamaño_bbdd} POIS. TIEMPO MAXIMO: {tiempo_max}. CICLICA: {ciclica}. EDAD: {edad}'

    graficar_dispersion(resultados, 'DISTANCIA TOTAL', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'NUMERO DE POIS VISITADOS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO TOTAL ALGORITMO', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO EJECUCION ALGORITMO', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO TOTAL ALGORITMO', 'DISTANCIA TOTAL', titulo_comun)
    
    graficar_bigotes(resultados, 'TIEMPO TOTAL ALGORITMO', 'ALGORITMO', titulo_comun)
    graficar_bigotes(resultados, 'INTERÉS', 'ALGORITMO', titulo_comun)
    graficar_bigotes(resultados, 'DISTANCIA TOTAL', 'ALGORITMO', titulo_comun)

    graficar_diagrama_araña(resultados, titulo_comun)
    graficar_matriz_pois(resultados, int(tamaño_bbdd), titulo_comun)
    graficar_matriz_correlacion(resultados)

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de resultados de algoritmos.")
    parser.add_argument('ruta_archivo', type=str, help='Ruta del archivo CSV con los resultados para análisis.')

    args = parser.parse_args()
    main(args.ruta_archivo)
