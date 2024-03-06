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



    def visualizar_ruta_en_mapa_folium(self, nodos_df):
        
        if not self.ruta_solucion:
            print("La ruta de solución está vacía.")
            return None

        # Filtra nodos_df utilizando self.ruta_solucion para asegurar consistencia
        nodos_df_filtrado = nodos_df[nodos_df['nodo'].isin(self.ruta_solucion)].copy()

        # Inicializa el mapa de Folium con la ubicación del primer nodo en nodos_df_filtrado
        primer_nodo = nodos_df_filtrado.iloc[0]
        mapa = folium.Map(location=[primer_nodo['lat'], primer_nodo['lon']], zoom_start=15)

        for idx, nodo_id in enumerate(self.ruta_solucion, start=1):
            row = nodos_df_filtrado[nodos_df_filtrado['nodo'] == nodo_id].iloc[0]
            icon = folium.DivIcon(html=f'<div style="font-size: 12pt; color : black; background-color:white; border-radius:50%; padding: 5px;">{idx}</div>')
            folium.Marker(location=[row['lat'], row['lon']], 
                        popup=f'Nodo {idx}: {row["name"]} - Interés: {row["interes"]}', 
                        icon=icon).add_to(mapa)

        # Añade las rutas entre nodos consecutivos
        for i in range(len(self.ruta_solucion) - 1):
            nodo_origen = self.ruta_solucion[i]
            nodo_destino = self.ruta_solucion[i + 1]
            # Asegura la consistencia utilizando nodos_df_filtrado para encontrar nodos originales y destinos
            orig_point = nodos_df_filtrado[nodos_df_filtrado['nodo'] == nodo_origen].iloc[0]
            dest_point = nodos_df_filtrado[nodos_df_filtrado['nodo'] == nodo_destino].iloc[0]

            # Calcula y dibuja la ruta real entre nodos originales y destinos
            orig_node = ox.nearest_nodes(self.G, X=orig_point['lon'], Y=orig_point['lat'])
            dest_node = ox.nearest_nodes(self.G, X=dest_point['lon'], Y=dest_point['lat'])
            try:
                route = ox.shortest_path(self.G, orig_node, dest_node, weight='travel_time')
                route_map = ox.plot_route_folium(self.G, route, route_map=mapa, weight=5, color="#3186cc", opacity=0.7)
            except ValueError as e:
                print(f"No se pudo encontrar una ruta entre {nodo_origen} y {nodo_destino}")

        return mapa


    def visualizar_ruta_en_mapa_explore(self, nodos_df):
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

    def exportar_indicaciones_ruta_v1(self, ruta_archivo):
            if not self.ruta_solucion:
                print("La ruta de solución está vacía. No hay indicaciones para exportar.")
                return

            with open(ruta_archivo, 'w') as f:
                f.write("Indicaciones de la Ruta:\n\n")
                f.write("Nodos Visitados:\n")
                for idx, nodo_id in enumerate(self.ruta_solucion, start=1):
                    row = self.archivo_nodos.loc[nodo_id]
                    f.write(f"Nodo {idx}: {row['name']} - Interés: {row['interes']}\n")
                
                f.write("\nRuta a Seguir:\n")
                for i in range(len(self.ruta_solucion) - 1):
                    nodo_origen = self.ruta_solucion[i]
                    nodo_destino = self.ruta_solucion[i + 1]
                    orig_point = self.archivo_nodos.loc[nodo_origen]
                    dest_point = self.archivo_nodos.loc[nodo_destino]
                    orig_node = ox.nearest_nodes(self.G, X=orig_point['lon'], Y=orig_point['lat'])
                    dest_node = ox.nearest_nodes(self.G, X=dest_point['lon'], Y=dest_point['lat'])
                    try:
                        route = ox.shortest_path(self.G, orig_node, dest_node, weight='travel_time')
                        f.write(f"Desde {orig_point['name']} ({orig_point['lat']}, {orig_point['lon']}) hasta {dest_point['name']} ({dest_point['lat']}, {dest_point['lon']})\n")
                        f.write(f"Ruta: {route}\n\n")
                    except ValueError as e:
                        print(f"No se pudo encontrar una ruta entre {nodo_origen} y {nodo_destino}: {e}")     

                        
    def exportar_indicaciones_ruta_v2(self, ruta_archivo):
            if not self.ruta_solucion:
                print("La ruta de solución está vacía. No hay indicaciones para exportar.")
                return

            # Obtener DataFrame de nodos y aristas del grafo
            nodes, edges = ox.graph_to_gdfs(self.G)

            with open(ruta_archivo, 'w') as f:
                f.write("Indicaciones de la Ruta:\n\n")
                f.write("Nodos Visitados:\n")
                for idx, nodo_id in enumerate(self.ruta_solucion, start=1):
                    row = self.archivo_nodos.loc[nodo_id]
                    f.write(f"Nodo {idx}: {row['name']} - Interés: {row['interes']}\n")
                
                f.write("\nRuta a Seguir:\n")
                for i in range(len(self.ruta_solucion) - 1):
                    nodo_origen = self.ruta_solucion[i]
                    nodo_destino = self.ruta_solucion[i + 1]
                    orig_point = self.archivo_nodos.loc[nodo_origen]
                    dest_point = self.archivo_nodos.loc[nodo_destino]
                    orig_node = ox.nearest_nodes(self.G, X=orig_point['lon'], Y=orig_point['lat'])
                    dest_node = ox.nearest_nodes(self.G, X=dest_point['lon'], Y=dest_point['lat'])
                    try:
                        route = ox.shortest_path(self.G, orig_node, dest_node, weight='travel_time')
                        f.write(f"Desde {orig_point['name']} ({orig_point['lat']}, {orig_point['lon']}) hasta {dest_point['name']} ({dest_point['lat']}, {dest_point['lon']})\n")
                        f.write("Ruta: ")
                        for i in range(len(route) - 1):
                            edge_data = self.G.get_edge_data(route[i], route[i+1])
                            street_name = edge_data[0]['name'] if 'name' in edge_data[0] else f"Calle sin nombre ({route[i]} - {route[i+1]})"
                            f.write(f"{street_name}")
                            if i < len(route) - 2:
                                f.write(" -> ")
                        f.write("\n\n")
                    except ValueError as e:
                        print(f"No se pudo encontrar una ruta entre {nodo_origen} y {nodo_destino}: {e}")