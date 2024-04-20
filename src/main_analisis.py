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
        titulo_comun (str): El título común para el gráfico.
        hue (str): El nombre de la columna para agrupar colores. 
    """
    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(data=resultados, x=x, y=y, hue=hue, style=hue, s=100)

    plt.title(f'{titulo_comun}\nDispersión de {x} vs {y}', fontsize=14, fontweight='bold') 
    plt.xlabel(x, fontsize=13) 
    plt.ylabel(y, fontsize=13) 
    plt.legend(loc='best', title='Algoritmo', frameon=False, fontsize=12, title_fontsize=13)
    
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind, ax, annot, scatter):
        pos = scatter.get_offsets()[ind["ind"][0]]
        row_id = ind["ind"][0]
        x_val, y_val = pos
        algo_name = resultados.iloc[row_id][hue]  # Acceso al nombre del algoritmo
        annot.xy = pos
        text = f"Algoritmo: {algo_name}\n{x}: {x_val:.2f}, {y}: {y_val:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                update_annot(ind, ax, annot, scatter)
                annot.set_visible(True)
                plt.draw()
            else:
                if vis:
                    annot.set_visible(False)
                    plt.draw()

    scatter = ax.collections[0]  # Acceso a la colección de puntos creada por sns.scatterplot
    plt.gcf().canvas.mpl_connect("motion_notify_event", hover)


def graficar_bigotes(resultados, y, x='ALGORITMO', titulo_comun=""):
    """Genera un diagrama de caja.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        y (str): El nombre de la columna para el eje y.
        x (str): El nombre de la columna para agrupar en el eje x.
        titulo_comun (str): El título común para el gráfico.
    """
    plt.figure(figsize=(10, 8))
   
    paleta_colores = sns.color_palette("viridis", n_colors=len(resultados[x].unique()))  
    
    sns.boxplot(x=x, y=y, data=resultados, palette=paleta_colores)
    plt.title(f'{titulo_comun}\nDiagrama de caja de {y}', fontsize=14, fontweight='bold')
    plt.xticks(fontsize=13) 
    plt.yticks(fontsize=13)  
    plt.xlabel('')  
    plt.ylabel(y, fontsize=13) 
    plt.grid(True, linestyle='--', alpha=0.6) 

    plt.tight_layout()  

def graficar_diagrama_araña(resultados, titulo_comun=""):
    """Genera un diagrama de araña.

    Args:
        resultados (pandas.DataFrame): El DataFrame que contiene los datos.
        titulo_comun (str): El título común para el gráfico. 
    """
    categorias = ['NUMERO DE POIS VISITADOS', 'INTERÉS', 'DISTANCIA TOTAL', 'TIEMPO RUTA', 'MARGEN', 'TIEMPO EJECUCION ALGORITMO']
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
        titulo_comun (str): El título común para el gráfico. 
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

    """
    graficar_dispersion(resultados, 'DISTANCIA TOTAL', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'NUMERO DE POIS VISITADOS', titulo_comun)
    graficar_dispersion(resultados, 'MARGEN', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO RUTA', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO EJECUCION ALGORITMO', 'INTERÉS', titulo_comun)
    graficar_dispersion(resultados, 'TIEMPO RUTA', 'DISTANCIA TOTAL', titulo_comun)
    
    
    graficar_bigotes(resultados, 'TIEMPO RUTA', 'ALGORITMO', titulo_comun)
   
    graficar_bigotes(resultados, 'INTERÉS', 'ALGORITMO', titulo_comun)
    graficar_bigotes(resultados, 'DISTANCIA TOTAL', 'ALGORITMO', titulo_comun)
    graficar_bigotes(resultados, 'MARGEN', 'ALGORITMO', titulo_comun)
    """
    graficar_diagrama_araña(resultados, titulo_comun)
    
    """
    graficar_matriz_pois(resultados, int(tamaño_bbdd), titulo_comun)
    """

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de resultados de algoritmos.")
    parser.add_argument('ruta_archivo', type=str, help='Ruta del archivo CSV con los resultados para análisis.')

    args = parser.parse_args()
    main(args.ruta_archivo)
