import osmnx as ox
import folium
import pandas as pd
import networkx as nx
import geopandas as gpd

class Visualizacion:
    def __init__(self, archivo_nodos, ruta_solucion):
        self.archivo_nodos = archivo_nodos.set_index('nodo')
        self.ruta_solucion = ruta_solucion
        # Configurar osmnx para usar la red de calles peatonales
        ox.settings.log_console=True
        self.G = ox.graph_from_place('Granada, Spain', network_type='walk')
        self.G = ox.speed.add_edge_speeds(self.G)
        self.G = ox.speed.add_edge_travel_times(self.G)

    def cargar_nodos(self):
        try:
            
            nodos_df = pd.read_csv(self.archivo_nodos)
            print("Datos de nodos cargados exitosamente.")
            return nodos_df
        except FileNotFoundError:
            print(f"Error: El archivo {self.archivo_nodos} no fue encontrado.")
            return None

    def visualizar_ruta_en_mapa(self, nodos_df):
        nodos_df_filtrado = nodos_df[nodos_df['nodo'].isin(self.ruta_solucion)].copy()
        if not nodos_df_filtrado.empty:
            
            #mapa = ox.plot_graph_folium(self.G, edge_color='gray', edge_width=2, edge_opacity=0.5)
            lat = []
            lon = []
            
            

            # for _, nodo in nodos_df_filtrado.iterrows():
            #     lat.append(nodo['lat'])
            #     lon.append(nodo('lon'))
            
            for i in self.ruta_solucion:
                lat.append(self.archivo_nodos.loc[i, 'lat'])
                lon.append(self.archivo_nodos.loc[i, 'lon'])


             # Añadir marcadores para cada nodo
      #  for _, nodo in nodos_df_filtrado.iterrows():
       #     folium.Marker([nodo['lat'], nodo['lon']], popup=nodo['name']).add_to(mapa)

           

            routes = []
            pois = []
            for i in range(len(self.ruta_solucion) - 1):
                nodo_origen = self.ruta_solucion[i]
                nodo_destino = self.ruta_solucion[i + 1]
                orig_point = nodos_df_filtrado.loc[nodos_df_filtrado['nodo'] == nodo_origen].iloc[0]
                dest_point = nodos_df_filtrado.loc[nodos_df_filtrado['nodo'] == nodo_destino].iloc[0]
                orig_node = ox.nearest_nodes(self.G, X=orig_point['lon'],Y=orig_point['lat'])
                dest_node = ox.nearest_nodes(self.G, X=dest_point['lon'], Y=dest_point['lat'])
                route = nx.shortest_path(self.G, orig_node, dest_node, weight='travel_time')
                routes.append(route)
                
                pois.append(orig_node)
                pois.append(dest_node)
             
            nodes, edges = ox.graph_to_gdfs(self.G)
            gdfs = (ox.utils_graph.route_to_gdf(self.G, route, weight='travel_time') for route in routes)
            mapa = edges.explore(color="#222222", tiles="cartodbdarkmatter")
            
            if lat is not None and lon is not None:
                # Convert to GeoDataFrame
                marker_gdf = gpd.GeoDataFrame({'geometry': gpd.points_from_xy(lon, lat)})
                marker_gdf.explore(m=mapa, color='red', symbol='triangle', edgecolor='black', size=10)
                
           
         
            for route_edges in gdfs:
                mapa = route_edges.explore(m=mapa, color="cyan", style_kwds={"weight": 15, "opacity": 0.1})
                
             
            return mapa
        else:
            print("No hay nodos filtrados para visualizar.")
            return None
