**Título:** GranadaCultura: Un Paquete Python para Optimizar Rutas Culturales en Granada, España

**Descripción:**

GranadaCultura es un paquete Python diseñado para optimizar rutas culturales en la ciudad de Granada, España. Proporciona un conjunto de algoritmos y herramientas para planificar rutas eficientes e interesantes desde el punto de vista del usuario y que además tengan en cuenta sus preferencias. Estas preferencias pueden ser: el tiempo disponible y los puntos de interés (POIs) que desea visitar. El paquete incluye:

* **Algoritmos:** Implementa diversos algoritmos de optimización para la planificación de rutas, incluyendo Greedy, GRASP, Simulación de Recocido, Algoritmo Genético y Algoritmo Memetic.
* **Procesamiento de Datos:** Proporciona funciones para cargar y procesar datos de OpenStreetMap, incluyendo nodos, aristas, POIs y matrices de distancia y tiempo.
* **Visualización:** Genera mapas interactivos utilizando Folium para visualizar rutas, POIs y otra información relevante.

**Instalación:**

Para instalar el paquete GranadaCultura hay que clonar el repositorio e instalar las dependencias necesarias:
```bash
git clone https://github.com/lusangom/GranadaCultura.git
cd GranadaCultura
pip install
"numpy == 1.23.5",
"pandas==1.5.2",
"matplotlib==3.8.2",
"folium==0.15.1",
"geopandas==0.14.3",
 "osmnx==1.9.1",
```


**Uso:**

El paquete proporciona varios scripts principales para diferentes casos de uso:

* **`main_analisis.py`:** Analiza los resultados de las ejecuciones del algoritmo, generando gráficos y tablas para comparar su rendimiento.
* **`main_fichero.py`:** Ejecuta los algoritmos en base a un archivo de configuración, generando resultados en formato de texto y CSV.
* **`main_interactivo.py`:** Permite la ejecución interactiva de los algoritmos, solicitando al usuario parámetros de entrada y visualizando los resultados.
* **`main_visualizacion.py`:** Visualiza rutas a partir de un archivo CSV en un mapa interactivo.

**Ejemplo de uso:**

Para ejecutar el algoritmo Greedy para un usuario de 30 años con 60 minutos disponibles, visitando todos los POIs posibles y comenzando en el nodo 1, ejecute el siguiente comando:

```bash
python3 main_fichero.py configuracion_greedy.json
```

Esto generará un archivo de resultados `resultados.txt` y un archivo CSV `tabla.csv` que contienen los detalles de la ruta.

* El paquete está diseñado con fines de investigación y educativos. 
* El paquete asume la precisión de los datos de OpenStreetMap. Se recomienda verificar los datos antes de usarlos.
* El rendimiento del paquete puede variar según la complejidad del problema y los recursos computacionales disponibles.
