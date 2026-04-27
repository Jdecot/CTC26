import pandas as pd
from decimal import Decimal
import os
import config

def main(ready_for_ingest_filepath, reworked_df):
    
    # Définir l'ordre des colonnes souhaité
    columns_order = [
        "Date", "refid", "Detected Type", "Type", "subtype",
        "Received Currency", "Received Amount", "Received Net Worth", 
        "Sent Currency", "Sent Amount", "Sent Net Worth", 
        "Fee Currency", "Fee Amount", "Fee Net Worth"
    ]

    cryptocom_2023_ready_for_ingest = pd.read_csv(ready_for_ingest_filepath, sep=',', dtype=str)
    # Convert date column (seulement si le DataFrame n'est pas vide)
    if not cryptocom_2023_ready_for_ingest.empty:
        cryptocom_2023_ready_for_ingest['Date'] = pd.to_datetime(cryptocom_2023_ready_for_ingest['Date'], format='%m/%d/%Y %H:%M:%S')

    # Ajout des nouvelles colonnes et renommage
    cryptocom_2023_ready_for_ingest['Detected Type'] = cryptocom_2023_ready_for_ingest['Type']
    cryptocom_2023_ready_for_ingest['Type'] = ""
    cryptocom_2023_ready_for_ingest['refid'] = ""
    cryptocom_2023_ready_for_ingest['subtype'] = ""

    # Réorganiser les colonnes selon l'ordre demandé
    cryptocom_2023_ready_for_ingest = cryptocom_2023_ready_for_ingest[columns_order]

    cryptocom_2023_ready_for_ingest.to_csv(reworked_df, index=False)
    print(f"Fichier exporté vers {reworked_df}")


ready_for_ingest_filepath = config.FILE_CRYPTOCOM_2023
reworked_df = config.DIR_1_RFI / 'cryptocom_2023_ready_for_ingest_date_reworked.csv'

main(ready_for_ingest_filepath, reworked_df)
