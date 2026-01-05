# Auteur : Rémy Wilson
# Programme : Filtre pour garder les valeurs valides de la colonne 'modeprimary'.
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

values_to_keep = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 18, 21, 22, 23, 24, 77]
input_filename = "filtered_trippurpose.csv"
output_filename = "filtered_modeprimary.csv"
column_to_filter = "modeprimary"

filter_csv(input_filename, output_filename, column_to_filter, values_to_keep)