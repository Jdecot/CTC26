import pandas as pd
import os
import config

def main(ready_for_ingest_filepath, reworked_df):
    
    # Vérifier si le fichier source existe, sinon le créer vide
    if not os.path.exists(ready_for_ingest_filepath):
        print(f"Le fichier {ready_for_ingest_filepath} n'existe pas. Création d'un fichier vide.")
        # Créer un DataFrame vide avec les colonnes attendues
        empty_df = pd.DataFrame(columns=["Date", "Type", "Received Currency", "Received Amount", 
                                          "Received Net Worth", "Sent Currency", "Sent Amount", 
                                          "Sent Net Worth", "Fee Currency", "Fee Amount", "Fee Net Worth"])
        empty_df.to_csv(ready_for_ingest_filepath, sep=',', index=False)
    
    # Définir filepath to read and filepath to export
    cryptocom_2023_ready_for_ingest = pd.read_csv(ready_for_ingest_filepath, sep=',')

    # Convert date column (seulement si le DataFrame n'est pas vide)
    if not cryptocom_2023_ready_for_ingest.empty:
        cryptocom_2023_ready_for_ingest['Date'] = pd.to_datetime(cryptocom_2023_ready_for_ingest['Date'], format='%m/%d/%Y %H:%M:%S')

    # export - éviter la notation scientifique pour les petits nombres
    # 14 décimales pour conserver toute la précision (certains nombres en ont jusqu'à 13)
    cryptocom_2023_ready_for_ingest.to_csv(reworked_df, index=False, float_format='%.14f')
    print(f"Fichier exporté vers {reworked_df}")


ready_for_ingest_filepath = config.FILE_CRYPTOCOM_2023
reworked_df = config.DIR_1_RFI / 'cryptocom_2023_ready_for_ingest_date_reworked.csv'

main(ready_for_ingest_filepath, reworked_df)
