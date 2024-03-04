import osmnx as ox
import folium
import pandas as pd
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt

class Visualizacion:
    def __init__(self, archivo_nodos, ruta_solucion):
        self.archivo_nodos = archivo_nodos.set_index('nodo')
        self.ruta_solucion = ruta_solucion
        
        
        ox.settings.log_console=True
        self.G = ox.graph_from_place('Granada, Spain', network_type='walk')
        self.G = ox.speed.add_edge_speeds(self.G)
        self.G = ox.speed.add_edge_travel_times(self.G)



    def visualizar_ruta_en_mapa(self, nodos_df):
        nodos_df_filtrado = nodos_df[nodos_df['nodo'].isin(self.ruta_solucion)].copy()
        
        
        if not nodos_df_filtrado.empty:
            
            lat = []
            lon = []
            name = []
            interes = []
            
            
    
            for i in self.ruta_solucion:
                lat.append(self.archivo_nodos.loc[i, 'lat'])
                lon.append(self.archivo_nodos.loc[i, 'lon'])
             
                
                name.append(self.archivo_nodos.loc[i, 'name'])
                interes.append(str(self.archivo_nodos.loc[i, 'interes']))

            print('tamaño longitudes' + str(len(lon)))
            print('tamaño latitudes' + str(len(lat))) 
            print('tamaño nombres' + str(len(name))) 
                           

            routes = []
           
            for i in range(len(self.ruta_solucion) - 1):
                nodo_origen = self.ruta_solucion[i]
                nodo_destino = self.ruta_solucion[i + 1]
                orig_point = nodos_df_filtrado.loc[nodos_df_filtrado['nodo'] == nodo_origen].iloc[0]
                dest_point = nodos_df_filtrado.loc[nodos_df_filtrado['nodo'] == nodo_destino].iloc[0]
                orig_node = ox.nearest_nodes(self.G, X=orig_point['lon'],Y=orig_point['lat'])
                dest_node = ox.nearest_nodes(self.G, X=dest_point['lon'], Y=dest_point['lat'])
                route = ox.shortest_path(self.G, orig_node, dest_node, weight='travel_time')
                routes.append(route)
                
                
            
         
            nodes, edges = ox.graph_to_gdfs(self.G)
            #gdfs = (ox.utils_graph.route_to_gdf(self.G, route, weight='travel_time') for route in routes)
            gdfs = []
            for route in routes:
                try:
                    route_gdf = ox.utils_graph.route_to_gdf(self.G, route, weight='travel_time')
                    gdfs.append(route_gdf)
                except ValueError as e:
                    print(f"Error al convertir la ruta en GeoDataFrame: {e}")
               
            
            mapa = edges.explore(color="#222222", tiles="cartodbdarkmatter")
            
            if lat is not None and lon is not None:
                
                marker_gdf = gpd.GeoDataFrame({
                    'geometry': gpd.points_from_xy(lon, lat),
                    'name': name,
                    'interes': interes # Añade la lista 'info' como una columna en 'marker_gdf'
                })
                
                  # Convertir a GeoDataFrame
                #marker_gdf = gpd.GeoDataFrame(nodos_df_filtrado, geometry=gpd.points_from_xy(lon, lat))

                #marker_gdf.explore(m=mapa, color='red', symbol='triangle', edgecolor='black', size=10)
        
                cols = ["name", "interes"]
                marker_gdf.explore(m=mapa, color='red', marker_type='circle', marker_kwds={'radius': 10}, tooltip=cols)

           
         
            for route_edges in gdfs:
                mapa = route_edges.explore(m=mapa, color="cyan", style_kwds={"weight": 15, "opacity": 0.1})
             
          
         
            return mapa
        else:
            print("No hay nodos filtrados para visualizar.")
            return None
