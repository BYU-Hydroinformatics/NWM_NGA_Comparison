import pandas as pd
import geopandas as gpd
import numpy as np
import requests
from matplotlib import pyplot as plt
import os
import json

version = 'v1.2'

vpus = ['01', '02', '03N', '03S', '03W', '04', '05', '06', '07', '08', '09', '10L', '10U', '11', '12', '13', '14', '15',
        '16', '17', '18']

# Get NWM Data
stream_order_file_path = f'metadata/nextgen_orders.json'
area_path = f'metadata/nextgen_areas.json'
length_path = f'metadata/nextgen_lengths.json'
number_path = f'metadata/nextgen_numbers.json'
stream_order_col = 'order'
area_col = 'tot_drainage_areasqkm'
length_col = 'lengthkm'
order_obj = []
length_obj = []
area_obj = []
if len(os.listdir('metadata')) == 0:
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
        order_obj.append({vpu: gdf[stream_order_col].tolist()})
        length_obj.append({vpu: gdf[length_col].tolist()})
        area_obj.append({vpu: gdf[area_col].tolist()})
    for (file, obj) in zip([stream_order_file_path, length_path, area_path],[order_obj, length_obj, area_obj]):
        with open(file, "w") as f:
            f.write(json.dumps(obj))
else:
    print('here')
    with open(stream_order_file_path) as f:
        order_obj = json.load(f)

    with open(length_path) as f:
        length_obj = json.load(f)

    with open(area_path) as f:
        area_obj = json.load(f)


# Get NGA Data
nga_dir = 'NorthAmericaStreams'
stream_order_file_path = f'nga_metadata/nga_orders.json'
area_path = f'nga_metadata/nga_areas.json'
length_path = f'nga_metadata/nga_lengths.json'
number_path = f'nga_metadata/nga_numbers.json'
stream_order_col = 'strmOrder'
area_col = 'USContArea'
length_col = 'Length'
nga_order_obj = []
nga_length_obj = []
nga_area_obj = []
if len(os.listdir('nga_metadata')) == 0:
    for file in os.listdir(nga_dir):
        if os.path.splitext(file)[1] == '.gpkg':
            gdf = gpd.read_file(os.path.join(nga_dir, file))
            print(gdf.columns)
            code = file.split('_')[2]
            nga_order_obj.append({code: gdf[stream_order_col].tolist()})
            nga_length_obj.append({code: gdf[length_col].tolist()})
            nga_area_obj.append({code: gdf[area_col].tolist()})
    for (path, obj) in zip([stream_order_file_path, length_path, area_path], [order_obj, length_obj, area_obj]):
        with open(path, "w") as f:
            f.write(json.dumps(obj))
else:
    with open(stream_order_file_path) as f:
        nga_order_obj = json.load(f)

    with open(length_path) as f:
        nga_length_obj = json.load(f)

    with open(area_path) as f:
        nga_area_obj = json.load(f)


#Stream Orders
stream_orders = np.array([])
nga_stream_orders = np.array([])
for obj in order_obj:
    stream_orders = np.append(stream_orders, obj[list(obj.keys())[0]])
for obj in nga_order_obj:
    nga_stream_orders = np.append(nga_stream_orders, obj[list(obj.keys())[0]])

unique, counts = np.unique(stream_orders, return_counts=True)
Proportions = counts/len(stream_orders)
# Create histograms
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
ax1.hist(stream_orders, bins=len(unique) - 1, density=True, cumulative=False)
ax2.hist(nga_stream_orders, bins=len(np.unique(nga_stream_orders)) - 1, density=True, cumulative=False)

# Set the y-axis label to show Proportion
ax1.set_ylabel('Proportion')
ax1.set_xlabel('Stream Order')
ax2.set_xlabel('Stream Order')
fig.suptitle('Distribution of Stream Orders')
ax1.set_title('NWM')
ax2.set_title('NGA')
# Set the y-axis limits for both subplots to be the same
max_val = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
ax1.set_ylim(0, max_val)
ax2.set_ylim(0, max_val)


# Display the histogram
plt.show()

#Average Catchment Area
area_avgs = np.array([])
nga_area_avgs = np.array([])
areas = np.array([])
nga_areas = np.array([])
for obj in area_obj:
    area = np.array([obj[list(obj.keys())[0]]])
    area_avgs = np.append(area_avgs, area.mean())
    areas = np.append(areas, area)
for obj in nga_area_obj:
    area = np.array([obj[list(obj.keys())[0]]])
    nga_area_avgs = np.append(nga_area_avgs, area.mean())
    nga_areas = np.append(nga_areas, area)

sort_areas = np.sort(areas)
sort_nga_areas = np.sort(nga_areas)
sort_areas_2 = np.gradient(np.gradient(sort_areas))
sort_nga_areas_2 = np.gradient(np.gradient(sort_nga_areas))
# Find the index of the inflection point
max_deriv = 0.01
inflection_idx = int(np.where(sort_areas_2 >= max_deriv)[0][0])
p = np.percentile(sort_nga_areas, 80)
# max_deriv = 10
# nga_inflection_idx = int(np.where(sort_nga_areas_2 >= max_deriv)[0][0])
nga_inflection_idx = int(np.where(sort_nga_areas >= p)[0][0])
#todo add tiered map of all the catchments above this area threshold, do same for long streams

# Set all values after the inflection point to the value at the inflection point
sort_areas[inflection_idx+1:] = sort_areas[inflection_idx]
sort_nga_areas[nga_inflection_idx+1:] = sort_nga_areas[nga_inflection_idx]

# Create scatter plots
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
ax1.scatter(np.arange(len(areas)), sort_areas)
ax2.scatter(np.arange(len(nga_areas)), sort_nga_areas)

# Set the y-axis label to show Proportion
ax1.set_ylabel('Area')
fig.suptitle('Distribution of Areas')
ax1.set_title('NWM')
ax2.set_title('NGA')
# Set the y-axis limits for both subplots to be the same
# max_val = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
# ax1.set_ylim(0, max_val)
# ax2.set_ylim(0, max_val)

plt.show()

# Create histograms
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
ax1.hist(sort_areas, density=True, cumulative=False)
ax2.hist(sort_nga_areas, density=True, cumulative=False)

# Set the y-axis label to show Proportion
ax1.set_ylabel('Proportion')
ax1.set_xlabel('Area')
ax2.set_xlabel('Area')
fig.suptitle('Distribution of Areas')
ax1.set_title('NWM')
ax2.set_title('NGA')
# Set the y-axis limits for both subplots to be the same
# max_val = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
# ax1.set_ylim(0, max_val)
# ax2.set_ylim(0, max_val)

plt.show()

#Average Stream Length
length_avgs = np.array([])
nga_length_avgs = np.array([])
lengths = np.array([])
nga_lengths = np.array([])
for obj in length_obj:
    length = np.array([obj[list(obj.keys())[0]]])
    length_avgs = np.append(length_avgs, length.mean())
    lengths = np.append(lengths, length)
for obj in nga_length_obj:
    length = np.array([obj[list(obj.keys())[0]]])
    nga_length_avgs = np.append(nga_length_avgs, length.mean())
    nga_lengths = np.append(nga_lengths, length)

sort_lengths = np.sort(lengths)
sort_nga_lengths = np.sort(nga_lengths)
sort_lengths_2 = np.gradient(np.gradient(sort_lengths))
sort_nga_lengths_2 = np.gradient(np.gradient(sort_nga_lengths))
# Find the index of the inflection point
max_deriv = 0.00328
inflection_idx = int(np.where(sort_lengths_2 >= max_deriv)[0][0])
max_deriv = 0.00328
p = np.percentile(sort_nga_lengths, 95)
nga_inflection_idx = int(np.where(sort_nga_lengths >= p)[0][0])

# Set all values after the inflection point to the value at the inflection point
sort_lengths[inflection_idx+1:] = sort_lengths[inflection_idx]
sort_nga_lengths[nga_inflection_idx+1:] = sort_nga_lengths[nga_inflection_idx]

# Create scatter plots
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
ax1.scatter(np.arange(len(lengths)), sort_lengths)
ax2.scatter(np.arange(len(nga_lengths)), sort_nga_lengths)

# Set the y-axis label to show Proportion
ax1.set_ylabel('Length')
fig.suptitle('Distribution of Lengths')
ax1.set_title('NWM')
ax2.set_title('NGA')
# Set the y-axis limits for both subplots to be the same
# max_val = max(ax1.get_ylim()[1], ax2.get_ylim()[1])
# ax1.set_ylim(0, max_val)
# ax2.set_ylim(0, max_val)

plt.show()

# Create histograms
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
ax1.hist(sort_lengths, density=True, cumulative=False)
ax2.hist(sort_nga_lengths, density=True, cumulative=False)

# Set the y-axis label to show Proportion
ax1.set_ylabel('Proportion')
ax1.set_xlabel('Length')
ax2.set_xlabel('Length')
fig.suptitle('Distribution of Lengths')
ax1.set_title('NWM')
ax2.set_title('NGA')

plt.show()
