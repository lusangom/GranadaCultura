import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse  # Importa argparse

def cargar_datos(ruta_archivo):
    return pd.read_csv(ruta_archivo)

def graficar_dispersion(resultados, x, y, hue='ALGORITMO'):
    sns.scatterplot(data=resultados, x=x, y=y, hue=hue)
    plt.title(f'Dispersión de {x} vs {y}')
    plt.show()

def graficar_bigotes(resultados, y, x='ALGORITMO'):
    sns.boxplot(x=x, y=y, data=resultados)
    plt.title(f'Diagrama de caja de {y}')
    plt.xticks(rotation=45)
    plt.show()

def main(ruta_archivo):
    resultados = cargar_datos(ruta_archivo)
    
    # Gráficas de dispersión
    graficar_dispersion(resultados, 'DISTANCIA TOTAL', 'INTERÉS')
    graficar_dispersion(resultados, 'MARGEN', 'NUMERO DE POIS VISITADOS')
    
    # Diagramas de bigotes
    graficar_bigotes(resultados, 'TIEMPO TOTAL ALGORITMO')
    graficar_bigotes(resultados, 'INTERÉS')

    # Histogramas y matriz de correlación como antes...
    # Otras visualizaciones sugeridas:
    # Histogramas de distribución del interés y tiempo total de los algoritmos
    sns.histplot(data=resultados, x='INTERÉS', hue='ALGORITMO', multiple="stack", kde=True)
    plt.title('Histograma de Interés por Algoritmo')
    plt.show()
    
    sns.histplot(data=resultados, x='TIEMPO TOTAL ALGORITMO', hue='ALGORITMO', multiple="stack", kde=True)
    plt.title('Histograma de Tiempo Total por Algoritmo')
    plt.show()

    # Matriz de correlación entre variables
    corr = resultados.select_dtypes(include=['float64', 'int']).corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title('Matriz de Correlación')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de resultados de algoritmos.")
    parser.add_argument('ruta_archivo', type=str, help='Ruta del archivo CSV con los resultados para análisis.')

    args = parser.parse_args()
    main(args.ruta_archivo)
