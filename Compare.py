import pandas as pd
import geopandas as gpd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
import os
import json

version = 'v1.2'

vpus = ['01', '02', '03N', '03S', '03W', '04', '05', '06', '07', '08', '09', '10L', '10U', '11', '12', '13', '14', '15',
        '16', '17', '18']

stream_order_file_path = f'metadata/nextgen.json'
stream_order_col = 'stream_order'

for vpu in vpus:
    file_path = f'NWM_files/nextgen_{vpu}.gpkg'
    print(f'Attempting to write {file_path}...')
    if not os.path.exists(file_path):
        url = f'https://s3.amazonaws.com/nextgen-hydrofabric/{version}/nextgen_{vpu}.gpkg'
        response = requests.get(url)
        gdf = gpd.read_file(response.content)
        print(response)
        with open(file_path, "wb") as f:
            f.write(response.content)
    else:
        print('Path already exists')
        gdf = gpd.read_file(file_path)
    print(gdf.columns)
    # with open(file_path, "a+") as f:
    #     f.seek(0)
    #     contents = f.read()
    #     if vpu not in contents:
    #         obj = {'vpu': gdf[stream_order_col].tolist()}
    #         f.write(json.dumps(obj))
