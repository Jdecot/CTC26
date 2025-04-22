import pandas as pd
import numpy as np
import os


def main(csv_files_list, all_trades_ready_for_ingest_filepath):
    
    ready_for_ingest_folder = "Data/1_ready_for_ingest/"
    # Lisez et fusionnez les fichiers CSV dans un seul DataFrame
    df_list = []
    for file in csv_files_list:
        file_path = os.path.join(ready_for_ingest_folder, file)
        df = pd.read_csv(file_path)

        if file == "cryptocom_2023_ready_for_ingest_date_reworked.csv":
            df['platform'] = "cryptocom_2023"
        if file == "kraken_2023_ready_for_ingest.csv":
            df['platform'] = "kraken_2023"
        if file == "kraken_2024_ready_for_ingest.csv":
            df['platform'] = "kraken_2024"

        df_list.append(df)

    df_merged = pd.concat(df_list, ignore_index=True)

    # Trie et export
    df_sorted = df_merged.sort_values(by='Date')
    df_sorted.to_csv(all_trades_ready_for_ingest_filepath, index=False)

csv_files_list = [
    "cryptocom_2023_ready_for_ingest_date_reworked.csv",
    "kraken_2023_ready_for_ingest.csv",
    "kraken_2024_ready_for_ingest.csv"
]
all_trades_ready_for_ingest_filepath = "Data/1_ready_for_ingest/all_trades_ready_for_ingest.csv"
main(csv_files_list, all_trades_ready_for_ingest_filepath)