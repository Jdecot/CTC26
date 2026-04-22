import pandas as pd
import numpy as np
import os


def main(csv_files_dict, all_trades_ready_for_ingest_filepath):
    
    ready_for_ingest_folder = "Data/1_ready_for_ingest/"
    # Lisez et fusionnez les fichiers CSV dans un seul DataFrame
    df_list = []
    for file in csv_files_dict:
        print(file)
        file_path = os.path.join(ready_for_ingest_folder, file)
        
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas. Création d'un fichier vide.")
            # Créer un DataFrame vide avec les bonnes colonnes
            empty_df = pd.DataFrame(columns=["Date", "Type", "Received Currency", "Received Amount", 
                                              "Received Net Worth", "Sent Currency", "Sent Amount", 
                                              "Sent Net Worth", "Fee Currency", "Fee Amount", "Fee Net Worth"])
            empty_df.to_csv(file_path, sep=',', index=False)

        df = pd.read_csv(file_path)
        if csv_files_dict[file] == 'bitmart_2024' :
            print('bitmart !!!')
        
        # Skip empty dataframes
        if df.empty:
            print(f"Le fichier {file} est vide, ignoré.")
            continue
        
        df['platform'] = csv_files_dict[file]

        df_list.append(df)

    df_merged = pd.concat(df_list, ignore_index=True)

    # Trie et export - éviter la notation scientifique pour les petits nombres
    df_sorted = df_merged.sort_values(by='Date')
    df_sorted.to_csv(all_trades_ready_for_ingest_filepath, index=False, float_format='%.14f')


csv_files_dict = {
    "cryptocom_2023_ready_for_ingest_date_reworked.csv" : "cryptocom_2023",
    "kraken_all_trades_ready_for_ingest.csv" : "kraken_all",
    "bitmart_2024.csv" : "bitmart_2024"
}
    

all_trades_ready_for_ingest_filepath = "Data/1_ready_for_ingest/all_trades.csv"

main(csv_files_dict, all_trades_ready_for_ingest_filepath)