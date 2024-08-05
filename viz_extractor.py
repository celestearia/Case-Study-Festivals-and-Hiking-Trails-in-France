import pandas as pd
from geopy.distance import distance
from scipy.spatial import cKDTree
import numpy as np

# Load the datasets
festivals_df = pd.read_csv('cleaned_festivals.csv')
trails_df = pd.read_csv('cleaned_trails.csv')

# Filter out invalid latitude and longitude values
festivals_df = festivals_df[(festivals_df['Latitude'] <= 90) & (festivals_df['Latitude'] >= -90) &
                            (festivals_df['Longitude'] <= 180) & (festivals_df['Longitude'] >= -180)]

trails_df = trails_df[(trails_df['Latitude'] <= 90) & (trails_df['Latitude'] >= -90) &
                      (trails_df['Longitude'] <= 180) & (trails_df['Longitude'] >= -180)]

# Create an array of the trail coordinates
trail_coords = trails_df[['Latitude', 'Longitude']].values

# Create a k-d tree for fast spatial queries
trail_tree = cKDTree(trail_coords)

# Function to count number of trails within a 10km radius of a festival using the k-d tree
def count_trails_near_festival(festival_lat, festival_lon, tree, radius_km=10):
    # Query the k-d tree for trails within the radius
    count = len(tree.query_ball_point([festival_lat, festival_lon], radius_km / 111))  # convert km to degrees
    return count

# Add a column to the festivals DataFrame with the number of trails within 10km
festivals_df['Trails_nearby'] = festivals_df.apply(
    lambda row: count_trails_near_festival(row['Latitude'], row['Longitude'], trail_tree), axis=1
)

# Extract data needed for visualization

# 1. Top 20 Festivals with the most trails within a 10km radius
top_20_festivals = festivals_df.nlargest(20, 'Trails_nearby')[['Nom_du_festival', 'Commune_principale_de_deroulement', 'Trails_nearby']]

# 2. Top 10 Communes with Festivals with the most trails within a 10km radius
commune_trails = festivals_df.groupby('Commune_principale_de_deroulement')['Trails_nearby'].sum().nlargest(10).reset_index()

# 3. Rank of Regions with the most festivals
region_festivals = festivals_df['Region_principale_de_deroulement'].value_counts().reset_index()
region_festivals.columns = ['Region', 'Number_of_Festivals']

# 4. Rank of Regions with the most trails
region_trails = festivals_df.groupby('Region_principale_de_deroulement')['Trails_nearby'].sum().reset_index()
region_trails.columns = ['Region', 'Number_of_Trails']
region_trails = region_trails.sort_values(by='Number_of_Trails', ascending=False).reset_index(drop=True)

# Save results to CSV for further analysis in R
top_20_festivals.to_csv('top_20_festivals.csv', index=False)
commune_trails.to_csv('commune_trails.csv', index=False)
region_festivals.to_csv('region_festivals.csv', index=False)
region_trails.to_csv('region_trails.csv', index=False)
