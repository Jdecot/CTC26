import pandas as pd
import numpy as np
import os
import pipeline_fct


def fichier_existe(chemin_fichier):
  """
  Vérifie si un fichier existe au chemin spécifié.

  Args:
    chemin_fichier (str): Le chemin complet ou relatif du fichier à vérifier.

  Returns:
    bool: True si le fichier existe, False sinon.
  """
  return os.path.exists(chemin_fichier) and os.path.isfile(chemin_fichier)


def sort_and_deduplicate(df):
    df_triee = df.sort_values(by='timestamp')
    df_sans_doublons = df_triee.drop_duplicates()
    return df_sans_doublons 

csv_fodler_list = [
    'D:/Data_crypto_tax_calculator/Kraken_Trading_History/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q3_2023/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q4_2023/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q1_2024/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q2_2024/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q3_2024/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q4_2024/',
    'D:/Data_crypto_tax_calculator/Kraken_Trading_Update/Kraken_Trading_History_Q1_2025/'
]

# Get all files available in kraken history and update
liste_elements = []
for folder in csv_fodler_list :
    liste_elements += os.listdir(folder)

valeurs_uniques = list(set(liste_elements))
# print(valeurs_uniques)


# Get crypto list used and find filename 
crypto_list = pipeline_fct.get_crypto_list_from_all_trades()

kraken_price_files_name = pipeline_fct.get_kraken_price_files_name()

for crypto in crypto_list : 

    file = str(kraken_price_files_name[crypto])
    df = pd.DataFrame()
    print(f"crypto : {crypto} : {file}, len file : {len(df)}")
    for folder in csv_fodler_list :
        print(f"{folder}/{file}.csv")
        existe = fichier_existe(f"{folder}/{file}.csv")
        if existe == True :
            # print(f"{folder}/{file} existe")
            df_file = pd.read_csv(f"{folder}/{file}.csv", names=["timestamp","price","quantity"], sep=',')
            print(f"folder - {folder} :  {file} - len file : {len(df_file)}")
            df = pd.concat([df, df_file], ignore_index=True)
            print(f"len def : {len(df)}")
            # print(df.head())
        else : 
            print(f"{folder}/{file}.csv nexiste pas")
    print(len(df))

    if len(df) > 0 :
        df = sort_and_deduplicate(df.copy())
        print(f"apres deduplicate : ", len(df))
        df.to_csv(f'D:/Data_crypto_tax_calculator/Kraken_History_Update_merged/{file}.csv', index=False, header=False)
    
    else :
        print(f"Pas de fichier de prix pour {crypto}")