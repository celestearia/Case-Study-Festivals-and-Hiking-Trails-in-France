import pandas as pd
import unidecode

def extract_months_from_period(period):
    months = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
    ]
    start_month, end_month = None, None
    for month in months:
        if month in period:
            if start_month is None:
                start_month = month
                period = period.replace(month, '', 1)
            else:
                end_month = month
                break
    if end_month is None:
        end_month = start_month
    return start_month, end_month

def clean_column_name(column_name):
    return unidecode.unidecode(column_name).replace(' ', '_')

def clean_festival_data(input_file_path, output_file_path):
    try:
        df = pd.read_csv(input_file_path, delimiter=';')
    except Exception as e:
        print(f"Error reading input file: {e}")
        return None

    df.columns = df.columns.str.replace('\ufeff', '').str.strip()

    columns_to_keep = [
        'Nom du festival',
        'Code postal (de la commune principale de déroulement)',
        'Commune principale de déroulement',
        'Région principale de déroulement',
        'Année de création du festival',
        'Discipline dominante',
        'Période principale de déroulement du festival',
        'Site internet du festival',
        'Géocodage xy'
    ]

    for column in columns_to_keep:
        if column not in df.columns:
            print(f"Missing column: {column}")
            return None

    df = df[columns_to_keep].drop_duplicates().dropna()

    cleaned_df = df.rename(columns=lambda x: clean_column_name(x))

    cleaned_df['Nom_du_festival'] = cleaned_df['Nom_du_festival'].str.title()

    geo_split = cleaned_df['Geocodage_xy'].str.split(',', expand=True)
    cleaned_df['Latitude'] = geo_split[0].astype(float)
    cleaned_df['Longitude'] = geo_split[1].astype(float)

    start_months, end_months = [], []
    for period in cleaned_df['Periode_principale_de_deroulement_du_festival']:
        start_month, end_month = extract_months_from_period(period)
        start_months.append(start_month)
        end_months.append(end_month)

    cleaned_df['Debut'] = start_months
    cleaned_df['Fin'] = end_months

    cleaned_df = cleaned_df.drop(columns=[
        'Periode_principale_de_deroulement_du_festival', 'Geocodage_xy'
    ])

    try:
        cleaned_df.to_csv(output_file_path, index=False, sep=',')
    except Exception as e:
        print(f"Error saving output file: {e}")
        return None

    return cleaned_df

# Define file paths
input_file_path = 'festivals-global-festivals-_-pl.csv'
output_file_path = 'cleaned_festivals.csv'

# Clean the data using the provided function
cleaned_df = clean_festival_data(input_file_path, output_file_path)
output_file_path
