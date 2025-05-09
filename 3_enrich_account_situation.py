import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct
import os


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


def get_average_price_from_kraken_file(df_filtre):

    time_col='timestamp'
    quantity_col='quantity'


    # print(f"df_filtre len : {len(df_filtre)}")

    # Calcul de la moyenne pondéré
    produit_somme = (df_filtre[quantity_col] * df_filtre['price']).sum()
    quantite_somme = df_filtre[quantity_col].sum()

    if quantite_somme == 0:
        return None  
    
    average_price = produit_somme / quantite_somme
    return average_price


def load_prices_file_as_df(crypto_prices_files, crypto):
    filename = str(crypto_prices_files[crypto])

    kraken_data_price = f'D:/Data_crypto_tax_calculator/Kraken_History_Update_merged/{filename}.csv'
    price_to_use = pd.DataFrame()
    print(f"{kraken_data_price},  existe : ", os.path.exists(kraken_data_price))

    if os.path.exists(kraken_data_price):
        try:
            price_to_use = pd.read_csv(kraken_data_price, names=["timestamp","price","quantity"], sep=',')
            print(f"Le fichier '{kraken_data_price}' a été chargé avec succès.")
        except FileNotFoundError:
            # Cette exception ne devrait pas se produire car on a déjà vérifié l'existence du fichier
            print(f"Erreur inattendue : Le fichier '{kraken_data_price}' n'a pas été trouvé.")
        except Exception as e:
            print(f"Une erreur s'est produite lors de la lecture du fichier '{kraken_data_price}': {e}")
    else:
        print(f"Le fichier '{kraken_data_price}' n'existe pas. Impossible de le lire.")

    return price_to_use


def find_average_price_with_kraken_file(kraken_prices_file_df, trade_date, crypto):


    if len(kraken_prices_file_df) == 0 :
        # print("On sort de la boucle pour cette crypto et on passe à la suivante")
        # print(f"les prix resteront à chaine vide pour {crypto} ")
        average_price = 0
        return average_price, "break"

    day_start_unix_nanoseconds, day_end_unix_nanoseconds = trade_date_to_cap_unix_nanoseconds(trade_date)
    masque = (kraken_prices_file_df['timestamp'] >= day_start_unix_nanoseconds) & (kraken_prices_file_df['timestamp'] <= day_end_unix_nanoseconds)
    df_filtre = kraken_prices_file_df.loc[masque]
    if len(df_filtre) == 0 :
        # print(f"Pas de data de prix pour {crypto} date : {trade_date} dans le fichier data kraken")
        average_price = 0
        return average_price, "null"
    else : 
        # print(f"Presence de Data de prix pour {crypto} date : {trade_date} dans le fichier data kraken")
        
        average_price = get_average_price_from_kraken_file(df_filtre)
        # print(f"get average price for {crypto} {trade_date} : {average_price}")
        return average_price, "ok"


def main(enriched_situation_path, account_situation_path):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """

    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()
    crypto_prices_files = pipeline_fct.get_kraken_price_files_name()


    # Get and set df
    asdf = pd.read_csv(account_situation_path, sep=',')
    enriched_situation = asdf.copy(deep=True)
    enriched_situation = add_price_columns(enriched_situation, crypto_used_list)

    price_db = f'Data/3_enriched_as/price_db.csv'
    price_db_df = pd.read_csv(price_db, sep=',')

    kraken_prices_file_df = pd.DataFrame()


    # # Fill price columns with average price for the day
    for crypto in crypto_used_list :
        print(f"recherche des prix de {crypto}")
        # for row_index in range(1, 2) :   
        for row_index in range(1, len(enriched_situation)):
            # print(f"recherche des prix de {crypto}, ligne {row_index}")  
            trade_date = enriched_situation.loc[row_index, "Date"]
            # print(f"trade_date : {trade_date}")  
            status = "null"
            lignes_trouvees_in_price_db = price_db_df[price_db_df['Date'] == trade_date]
            if len(lignes_trouvees_in_price_db) > 0:
                # print(f"On a trouvé une ligne dans price_db pour cette date : {trade_date}")
                if lignes_trouvees_in_price_db[f"{crypto}_price"].isnull().any() :
                    # print(f"Cellule trouvé dans la ligne pour {crypto}_price : {lignes_trouvees_in_price_db[f"{crypto}_price"]}")
                    # Si le prix trouvé dans price_db_df est inexploitable, on tente dans kraken file
                    if len(kraken_prices_file_df)  > 0 :  # On cherche le prix dans le fichier kraken, qui a déjà été ouvert
                        average_price, status = find_average_price_with_kraken_file(kraken_prices_file_df, trade_date, crypto)
                    else : 
                        # print(f"chargement du fichier des prix kreaken pour {crypto}")
                        kraken_prices_file_df = load_prices_file_as_df(crypto_prices_files, crypto) 
                        if len(kraken_prices_file_df)  > 0 :
                            average_price, status = find_average_price_with_kraken_file(kraken_prices_file_df, trade_date, crypto)
                    
                else : 
                    # print(f"Cellule trouvé dans la ligne pour {crypto}_price : {lignes_trouvees_in_price_db[f'{crypto}_price']}")
                    average_price = lignes_trouvees_in_price_db[f"{crypto}_price"]
                    # print(f"Prix trouvé dans price_db_df pour {crypto} - {trade_date} soit {average_price} eur")

            else :
                # print(f"pas de lignes trouvé à la date {trade_date} pour {crypto} dans price_db_df ")
                # print("recherche dans le fichier kraken")

                average_price, status = find_average_price_with_kraken_file(kraken_prices_file_df, trade_date, crypto)

            # print(f"status de la ligne : {status}")
            if status == "ok":
                # print(f"La variable '{average_price}' est un nombre")
                # print(f"old average price in enriched situation :  {enriched_situation.loc[row_index, f"{crypto}_price"]}")
                # print(f"nouveau prix moyen pour {crypto} - {trade_date} : {average_price}")
                enriched_situation.loc[row_index, f"{crypto}_price"] = average_price


            elif status == 'break':
                break
            # elif status == 'null':
            #     print(f"null pour {crypto} : {trade_date}")
            elif status == "unknown case" :
                print("unknown case !!!!!")  

        kraken_prices_file_df = pd.DataFrame()
            
    print(enriched_situation.head())
    export(enriched_situation, enriched_situation_path)



# File path
enriched_situation_path = 'Data/3_enriched_as/as_with_crypto_prices.csv'
account_situation_path = 'Data/2_account_situation/account_situation.csv'


main(enriched_situation_path, account_situation_path)




        # if crypto in ['CRO']: 
        #     print("cro")
        #     enriched_situation[f"{crypto}_price"] = ''
        #     continue  