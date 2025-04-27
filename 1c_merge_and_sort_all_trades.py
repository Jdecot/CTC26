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
        df = pd.read_csv(file_path)
        if csv_files_dict[file] == 'bitmart_2024' :
            print('bitmart !!!')
        
        df['platform'] = csv_files_dict[file]

        df_list.append(df)

    df_merged = pd.concat(df_list, ignore_index=True)

    # Trie et export
    df_sorted = df_merged.sort_values(by='Date')
    df_sorted.to_csv(all_trades_ready_for_ingest_filepath, index=False)


csv_files_dict = {
    "cryptocom_2023_ready_for_ingest_date_reworked.csv" : "cryptocom_2023",
    "kraken_2023_ready_for_ingest.csv" : "kraken_2023",
    "kraken_2024_ready_for_ingest.csv" : "kraken_2024",
    "kraken_2025_ready_for_ingest.csv" : "kraken_2025",
    "bitmart_2024.csv" : "bitmart_2024"
}
    

all_trades_ready_for_ingest_filepath = "Data/1_ready_for_ingest/all_trades.csv"

main(csv_files_dict, all_trades_ready_for_ingest_filepath)