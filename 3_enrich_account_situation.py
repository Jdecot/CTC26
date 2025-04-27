import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct

# def get_trade_info(selected_row):
#     timestamp = selected_row['timestamp']
#     price = selected_row['price']
#     unknown = selected_row['unknown']
#     return timestamp, price, unknown




def get_average_price_price_db(df, time_col, quantity_col, start_time, end_time):
    masque = (df[time_col] >= start_time) & (df[time_col] <= end_time)
    df_filtre = df.loc[masque]

    # Calcul de la moyenne pondéré
    produit_somme = (df_filtre[quantity_col] * df_filtre['price']).sum()
    quantite_somme = df_filtre[quantity_col].sum()

    if quantite_somme == 0:
        return None  
    
    average_price = produit_somme / quantite_somme
    return average_price



def date_time_to_unix_nanoseconds(date_time_str, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Convertit une date et une heure en nanosecondes Unix.
    
    Exemple d'utilisation
    date_time_str = '2023-10-27 15:30:00'
    unix_nanoseconds = date_time_to_unix_nanoseconds(date_time_str)
    print(f'Nanosecondes Unix : {unix_nanoseconds}')
    """
    time_struct = time.strptime(date_time_str, format_str)
    unix_seconds = int(time.mktime(time_struct))
    return unix_seconds


def add_price_columns(enriched_situation, asdf_crypto_used):
    # Add price columns
    for crypto in asdf_crypto_used :
        crypto_price_column = f"{crypto}_price"
        enriched_situation[crypto_price_column] = 'null'
    return enriched_situation
    

def get_start_and_end_date_of_the_day(date) :  
    date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    day_start = str(date_obj.replace(hour=0, minute=0, second=0))
    day_end = str(date_obj.replace(hour=23, minute=59, second=59))
    return day_start, day_end


def trade_date_to_cap_unix_nanoseconds(trade_date):

    day_start, day_end = get_start_and_end_date_of_the_day(trade_date)
    # Convertir en timstamp format utilisé par le fichier .csv des prix
    day_start_unix_nanoseconds = date_time_to_unix_nanoseconds(day_start)
    day_end_unix_nanoseconds = date_time_to_unix_nanoseconds(day_end)

    return day_start_unix_nanoseconds, day_end_unix_nanoseconds


def export(enriched_situation, enriched_situation_path):
    # Export as enriched_situation.csv
    enriched_situation.to_csv(enriched_situation_path, index=False)

    # Export crypto_price_list
    crypto_price_list = [col for col in enriched_situation.columns if col.endswith('_price')]
    columns_for_price_db = crypto_price_list + ['Date']
    enriched_situation[columns_for_price_db].to_csv('Data/3_enriched_as/price_db.csv', index=False)


def get_average_price_from_kraken_file(df, trade_date):

    time_col='timestamp'
    quantity_col='quantity'
    day_start_unix_nanoseconds, day_end_unix_nanoseconds = trade_date_to_cap_unix_nanoseconds(trade_date)

    masque = (df[time_col] >= day_start_unix_nanoseconds) & (df[time_col] <= day_end_unix_nanoseconds)
    df_filtre = df.loc[masque]

    # Calcul de la moyenne pondéré
    produit_somme = (df_filtre[quantity_col] * df_filtre['price']).sum()
    quantite_somme = df_filtre[quantity_col].sum()

    if quantite_somme == 0:
        return None  
    
    average_price = produit_somme / quantite_somme
    return average_price


def load_prices_file_as_df(crypto_prices_files, crypto):
    filename = crypto_prices_files[crypto]
    kraken_data_price = f'D:/Data_crypto_tax_calculator/Kraken_Trading_History/{filename}.csv'
    price_to_use = pd.read_csv(kraken_data_price, names=["timestamp","price","quantity"], sep=',')
    return price_to_use


def main(enriched_situation_path, account_situation_path):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """

    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()
    print(crypto_used_list)
    crypto_prices_files = pipeline_fct.get_kraken_price_files_name()
    # Get and set df
    asdf = pd.read_csv(account_situation_path, sep=',')
    enriched_situation = asdf.copy(deep=True)

    # Add price columns : f"{crypto}_price"
    enriched_situation = add_price_columns(enriched_situation, crypto_used_list)

    date_debut = enriched_situation.loc[1,"Date"]
    date_fin = enriched_situation.loc[len(enriched_situation)-1,"Date"]

    price_db = f'Data/3_enriched_as/price_db.csv'
    price_db_df = pd.read_csv(price_db, sep=',')
    price_db_df_filtered = price_db_df[(price_db_df["Date"] >= date_debut) & (price_db_df["Date"] <= date_fin)].copy()



    # Fill price columns with average price for the day
    for crypto in crypto_used_list :

        if crypto in ['CRO']: 
            print("cro")
            enriched_situation[f"{crypto}_price"] = ''
            continue  

        # Pour chaque ligne, tenter d'aller lire dans price_db, sinon aller chercher dans le fichier de prix

        if price_db_df_filtered[f"{crypto}_price"].isnull().any() :

            print(f"nan presence in {crypto}, period : {date_debut} - {date_fin}, start reading kraken prices")
            # Ouvrir le fichier contenant les prix
            price_to_use = load_prices_file_as_df(crypto_prices_files, crypto)
            
            # Pour une crypto donné, pour chaque ligne de enriched_situation, on va chercher le prix de la crypto au moment du trade
            for row_index in range(1, len(enriched_situation)) : 
                trade_date = enriched_situation.loc[row_index]["Date"]
                enriched_situation.loc[row_index, f"{crypto}_price"] = get_average_price_from_kraken_file(price_to_use, trade_date)          
        else : 
            print(f"No nan in {crypto}, period : {date_debut} - {date_fin}, start from price_db")
            price_to_use = price_db_df_filtered

            for row_index in range(1, len(enriched_situation)) :                 
                trade_date = enriched_situation.loc[row_index]["Date"]
                print("trade_date : ", trade_date)
                if trade_date == '2025-01-27 00:31:41' :
                    print("HELLO FROM TRADEDATE")
                    print(price_to_use[price_to_use["Date"] == trade_date])
                row_target_date_in_price_to_use = price_to_use[price_to_use["Date"] == trade_date]
                print(len(row_target_date_in_price_to_use))

                # average_price_of_the_day = 0
                average_price_of_the_day = row_target_date_in_price_to_use[f"{crypto}_price"].values[0]
                # print(average_price_of_the_day)

                enriched_situation.loc[row_index, f"{crypto}_price"] = average_price_of_the_day      

    export(enriched_situation, enriched_situation_path)



# File path
enriched_situation_path = 'Data/3_enriched_as/as_with_crypto_prices.csv'
account_situation_path = 'Data/2_account_situation/account_situation.csv'


main(enriched_situation_path, account_situation_path)
