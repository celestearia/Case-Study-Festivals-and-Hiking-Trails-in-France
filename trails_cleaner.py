import pandas as pd
import unicodedata

def clean_column_name(column_name):
    # Remove accents
    nfkd_form = unicodedata.normalize('NFKD', column_name)
    only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    # Replace spaces with underscores
    return only_ascii.replace(' ', '_')

def clean_data(input_file_path, output_file_path):
    try:
        df = pd.read_csv(input_file_path, delimiter=',')
    except Exception as e:
        print(f"Error reading input file: {e}")
        return None
    
    df.columns = df.columns.str.replace('\ufeff', '').str.strip()
    df.columns = [clean_column_name(col) for col in df.columns]
    
    columns_to_keep = [
        'Nom_du_POI',
        'Latitude',
        'Longitude',
        'Adresse_postale',
        'Code_postal_et_commune',
        'Description'
    ]
    
    for column in columns_to_keep:
        if column not in df.columns:
            print(f"Column missing: {column}")
            return None
    
    filtered_df = df[columns_to_keep].drop_duplicates().dropna(subset=['Latitude', 'Longitude']).copy()
    
    filtered_df[['code_postal', 'commune']] = filtered_df['Code_postal_et_commune'].str.split('#', expand=True)
    
    filtered_df['Nom_du_POI'] = filtered_df['Nom_du_POI'].str.title()
    
    cleaned_df = filtered_df.drop(columns=['Code_postal_et_commune'])
    
    try:
        cleaned_df.to_csv(output_file_path, index=False, sep=',')
    except Exception as e:
        print(f"Error saving output file: {e}")
        return None
    
    return cleaned_df

# Example usage
input_file_path = 'datatourisme-tour.csv'
output_file_path = 'cleaned_trails.csv'
cleaned_df = clean_data(input_file_path, output_file_path)
output_file_path
