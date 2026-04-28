import pandas as pd
import module_global
import os
import config

from module_global import trade_date_to_cap_unix_nanoseconds
from module_global import get_kraken_price_files_name
from module_global import load_prices_file_as_df
from module_global import get_average_price_from_kraken_file

def add_price_columns(enriched_situation, asdf_crypto_used):
    # Add price columns
    for crypto in asdf_crypto_used :
        crypto_price_column = f"{crypto}_price"
        enriched_situation[crypto_price_column] = None
    return enriched_situation
    

def export_es_and_price_db(enriched_situation, enriched_situation_path):
    # Export as enriched_situation.csv
    enriched_situation.to_csv(enriched_situation_path, index=False)

    # Export crypto_price_list
    crypto_price_list = [col for col in enriched_situation.columns if col.endswith('_price')]
    columns_for_price_db = crypto_price_list + ['Date']
    enriched_situation[columns_for_price_db].to_csv(config.FILE_PRICE_DB, index=False)


def export_price_db(price_db):
    price_db.to_csv(config.FILE_PRICE_DB, index=False)


def find_average_price_with_kraken_file(trade_date, crypto):

    global kraken_prices_file_df

    if len(kraken_prices_file_df) == 0 :
        print("kraken_prices_file_df est vide, on le charge")
        crypto_prices_files = get_kraken_price_files_name()
        filename = str(crypto_prices_files[crypto])
        kraken_prices_file_df = load_prices_file_as_df(filename) 
        print("kraken_prices_file_df est chargé")

    if len(kraken_prices_file_df) == 0 : 
        print("Taille de kraken_prices_file_df est 0, le fichier n'a pas pu être lu")
        average_price = -2
        return average_price
    else : 
        day_start_unix_nanoseconds, day_end_unix_nanoseconds = trade_date_to_cap_unix_nanoseconds(trade_date)
        masque = (kraken_prices_file_df['timestamp'] >= day_start_unix_nanoseconds) & (kraken_prices_file_df['timestamp'] <= day_end_unix_nanoseconds)
        df_filtre = kraken_prices_file_df.loc[masque]

    if len(df_filtre) == 0 :
        print("Taile de kraken_prices_file_df filtré est 0 après chargement (On a pas de prix pour la période de temps voulu)")
        average_price = -1
        return average_price
    else : 
        average_price = get_average_price_from_kraken_file(df_filtre)
        return average_price
    

def main(enriched_situation_path, account_situation_path):
    """
    Il faut
    ok : Une fonction qui charge price_db
    ok : Le loop sur crypto puis row_index
    ok : On test si on trouve le prix à trade_date dans price_db
    ok : Si ce n'est pas possible on charge kraken_prices_df, sauf s'il est déjà chargé
    ok :    On prends le prix dans kraken_prices_df
    ok : On renvoi le prix
    On inscrit le prix dans price_db si price_db ne l'a pas déjà ou a un prix différent de kraken_file
    """

    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """

    crypto_used_list = module_global.get_crypto_list_from_all_trades()
    

    # Get and set df
    asdf = pd.read_csv(account_situation_path, sep=',', dtype=str)
    enriched_situation = asdf.copy(deep=True)
    enriched_situation = add_price_columns(enriched_situation, crypto_used_list)


    price_db = config.FILE_PRICE_DB
    print("avant if")
    if not os.path.exists(price_db):
        print("pendant if")
        print(f"crypto_used_list : {crypto_used_list}")
        col_list = [col_name + '_price' for col_name in crypto_used_list]
        col_list.append('Date')
        print(f"col_list : {col_list}")
        print(col_list)
        df = pd.DataFrame(columns=col_list)
        
        print(df.head())
        df.to_csv(config.FILE_PRICE_DB, index=False)

    print("apres if")
    price_db_df = pd.read_csv(price_db, sep=',')

    global kraken_prices_file_df


    # # Fill price columns with average price for the day
    for crypto in crypto_used_list :
        kraken_prices_file_df = pd.DataFrame()
        
        print(f"recherche des prix de {crypto}")
        for row_index in range(1, len(enriched_situation)):

            trade_date = enriched_situation.loc[row_index, "Date"]
            price_found = False
            price_found_in_kraken_file = False
            
            # Try to find the price in price_db
            lignes_trouvees_in_price_db = price_db_df[price_db_df['Date'] == trade_date]
            if len(lignes_trouvees_in_price_db) > 0:
                price_from_price_db = lignes_trouvees_in_price_db[f'{crypto}_price'].iloc[0]
                if not pd.isna(price_from_price_db) : 
                    average_price = price_from_price_db
                    price_found = True

            # Try to find the price in kraken file
            if price_found == False : 
                average_price = find_average_price_with_kraken_file(trade_date, crypto)
                if average_price >= 0 :
                    price_found = True
                    price_found_in_kraken_file = True

            if price_found == True :
                # Cool, write the price in enriched situation and then save it in price_db for next use
                enriched_situation.loc[row_index, f"{crypto}_price"] = average_price
                if price_found_in_kraken_file : 
                    price_db_df.loc[price_db_df['Date'] == trade_date, f"{crypto}_price"] = average_price
            
            if price_found == False :
                print("prix non trouvé")
        export_price_db(price_db_df)
    export_es_and_price_db(enriched_situation, enriched_situation_path)



# File path
enriched_situation_path = config.FILE_AS_WITH_PRICES
account_situation_path = config.FILE_ACCOUNT_SITUATION

kraken_prices_file_df = pd.DataFrame()
main(enriched_situation_path, account_situation_path)
