# Auteur : Rémy Wilson
# Programme : Filtre pour garder les valeurs valides de la colonne 'originreportzone'.
# Date: 29 Décembre 2025

import pandas as pd

def filter_csv(input_file, output_file, column_name, values_to_keep):

    df = pd.read_csv(input_file)
    values_as_strings = [str(value) for value in values_to_keep]
    filtered_df = df[df[column_name].astype(str).isin(values_as_strings)]
    
    filtered_df.to_csv(output_file, index=False)
    
    print(f"Lignes originales: {len(df)}")
    print(f"Lignes conservées: {len(filtered_df)}")
    print(f"Lignes supprimées: {len(df) - len(filtered_df)}")

values_to_keep = [
    1, 50, 100, 120, 140, 180, 200, 240, 260, 300, 350, 360, 400,
    425, 450, 500, 560, 600, 625, 650, 700, 750, 800, 820, 840, 845
]

input_filename = "TRANSOD2022.csv"
output_filename = "filtered_zoneorigin.csv"
column_to_filter = "originreportzone"

filter_csv(input_filename, output_filename, column_to_filter, values_to_keep)