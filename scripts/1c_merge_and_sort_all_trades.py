import pandas as pd
import os
import config


def main(csv_files_dict, all_trades_ready_for_ingest_filepath):
    
    ready_for_ingest_folder = config.DIR_1_RFI
    # Lisez et fusionnez les fichiers CSV dans un seul DataFrame
    df_list = []
    for file in csv_files_dict:
        print(file)
        file_path = os.path.join(ready_for_ingest_folder, file)
        
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas. Création d'un fichier vide.")
            # Créer un DataFrame vide avec les bonnes colonnes
            empty_df = pd.DataFrame(columns=["Date", "refid", "Detected Type", "Type", "subtype",
            "Received Currency", "Received Amount", "Received Net Worth", 
            "Sent Currency", "Sent Amount", "Sent Net Worth", 
            "Fee Currency", "Fee Amount", "Fee Net Worth"])
            empty_df.to_csv(file_path, sep=',', index=False)

        df = pd.read_csv(file_path, sep=',')
        if csv_files_dict[file] == 'bitmart_2024' :
            print('bitmart !!!')
        
        # Skip empty dataframes
        if df.empty:
            print(f"Le fichier {file} est vide, ignoré.")
            continue
        
        # Insertion de la plateforme après la Date
        df.insert(1, 'platform', csv_files_dict[file])

        df_list.append(df)

    df_merged = pd.concat(df_list, ignore_index=True)

    # Trie et export - éviter la notation scientifique pour les petits nombres
    df_sorted = df_merged.sort_values(by='Date')
    df_sorted.to_csv(all_trades_ready_for_ingest_filepath, index=False, float_format='%.18f')


csv_files_dict = config.MERGE_CONFIG
    

all_trades_ready_for_ingest_filepath = config.FILE_ALL_TRADES

main(csv_files_dict, all_trades_ready_for_ingest_filepath)
