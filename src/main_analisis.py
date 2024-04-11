import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse  # Importa argparse
import ast
from math import pi


def cargar_datos(ruta_archivo):
    return pd.read_csv(ruta_archivo)

def graficar_dispersion(resultados, x, y, titulo_comun="", hue='ALGORITMO'):
    plt.figure()
    sns.scatterplot(data=resultados, x=x, y=y, hue=hue)
    plt.title(f'{titulo_comun}\nDispersión de {x} vs {y}')
    

def graficar_bigotes(resultados, y, x='ALGORITMO', titulo_comun=""):
    plt.figure()
    sns.boxplot(x=x, y=y, data=resultados)
    plt.title(f'{titulo_comun}\nDiagrama de caja de {y}')
    plt.xticks(rotation=45)
    
def graficar_matriz_correlacion(resultados):
    # Matriz de correlación entre variables
    plt.figure()
    corr = resultados.select_dtypes(include=['float64', 'int']).corr()
    sns.heatmap(data=corr, annot=True, cmap='coolwarm')
    plt.title('Matriz de Correlación')


def graficar_diagrama_araña(resultados, titulo_comun=""):
   
    # Seleccionar variables para el diagrama y normalizar
    categorias = ['NUMERO DE POIS VISITADOS', 'INTERÉS', 'DISTANCIA TOTAL', 'TIEMPO TOTAL ALGORITMO', 'MARGEN', 'TIEMPO EJECUCION ALGORITMO']
    N = len(categorias)
    
    # Normalizar datos
    valores_maximos = resultados[categorias].max()
    resultados_normalizados = resultados[categorias] / valores_maximos
    
    # Promedio por algoritmo
    promedios_por_algoritmo = resultados_normalizados.groupby(resultados['ALGORITMO']).mean().reset_index()
    
    # Preparar el diagrama de araña
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
    plt.figure()
    # Determinar el número máximo de POIs visitados en cualquier solución
    max_pois_visitados = resultados['POIS VISITADOS'].apply(lambda x: len(ast.literal_eval(x))).max()

    # Ajustar el rango de columnas basado en el tamaño máximo de la ruta de solución
    pois = range(1, tamaño_bbdd + 1)
    matriz_pois = pd.DataFrame(0, index=pois, columns=range(1, max_pois_visitados + 1))
    
    # Rellenar la matriz basada en los POIs visitados
    for index, row in resultados.iterrows():
        pois_visitados = ast.literal_eval(row['POIS VISITADOS'])  # Evalúa la cadena de la lista de manera segura
        for idx, poi in enumerate(pois_visitados, start=1):  # Asegura que el índice comienza en 1
            if poi in pois:  # Verifica si el POI está dentro del rango permitido
                matriz_pois.loc[poi, idx] += 1

    # Graficar la matriz de POIs Visitados
    #plt.figure(figsize=(10, 8))
    sns.heatmap(matriz_pois, cmap='Greys', cbar=True)  # Activar barra de colores para facilitar la interpretación
    plt.title(titulo_comun + '\nMatriz de POIs Visitados')
    plt.xlabel('Posición en la Solución')
    plt.ylabel('ID del POI')
  




def main(ruta_archivo):
   
    resultados = cargar_datos(ruta_archivo)
    tamaño_bbdd = resultados['TAMAÑO BBDD'].iloc[0] if 'TAMAÑO BBDD' in resultados.columns else 'Desconocido'
    tiempo_max = resultados['TIEMPO MAX'].iloc[0] if 'TIEMPO MAX' in resultados.columns else 'Desconocido'
    ciclica = resultados['RUTA CICLICA'].iloc[0] if 'RUTA CICLICA' in resultados.columns else 'Desconocido'
    edad = resultados['EDAD'].iloc[0] if 'EDAD' in resultados.columns else 'Desconocido'
    titulo_comun = f'BASE DE DATOS: {tamaño_bbdd} POIS. TIEMPO MAXIMO: {tiempo_max}. CICLICA: {ciclica}. EDAD: {edad}'

    # Asegúrate de que 'x' y 'y' sean nombres de columnas en tus DataFrame
    graficar_dispersion(resultados, 'DISTANCIA TOTAL', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'NUMERO DE POIS VISITADOS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'INTERES', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO TOTAL ALGORITMO', 'INTERES', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO EJECUCION ALGORITMO', 'INTERES', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO TOTAL ALGORITMO', 'DISTANCIA TOTAL', titulo_comun)
    
    graficar_bigotes(resultados, 'TIEMPO TOTAL ALGORITMO', 'ALGORITMO', titulo_comun)  # 'x' es el nombre de columna para agrupar
    graficar_bigotes(resultados, 'INTERÉS', 'ALGORITMO', titulo_comun)
    graficar_bigotes(resultados, 'DISTANCIA TOTAL', 'ALGORITMO', titulo_comun)

    graficar_diagrama_araña(resultados, titulo_comun)
    # Necesitas convertir el tamaño de la BBDD a int si viene como str
    graficar_matriz_pois(resultados, int(tamaño_bbdd), titulo_comun)
    graficar_matriz_correlacion(resultados)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de resultados de algoritmos.")
    parser.add_argument('ruta_archivo', type=str, help='Ruta del archivo CSV con los resultados para análisis.')

    args = parser.parse_args()
    main(args.ruta_archivo)
