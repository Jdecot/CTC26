import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct

def get_trade_info(selected_row):
    timestamp = selected_row['timestamp']
    price = selected_row['price']
    unknown = selected_row['unknown']
    return timestamp, price, unknown


def get_average_price(df, start_timestamp, end_timestamp):
    masque = (df['timestamp'] >= start_timestamp) & (df['timestamp'] <= end_timestamp)
    df_filtre = df.loc[masque]
    average_price = (df_filtre['unknown'] * df_filtre['price']).sum() / df_filtre['unknown'].sum()

    produit_somme = (df_filtre['unknown'] * df_filtre['price']).sum()
    quantite_somme = df_filtre['unknown'].sum()
    # print(f"Débogage : produit_somme = {produit_somme}, quantite_somme = {quantite_somme}")
    if quantite_somme == 0:
        print("Avertissement : Division par zéro détectée !")
        return None  # Ou une autre valeur par défaut
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
    unix_nanoseconds = unix_seconds   # Multiplier par 1 milliard

    return unix_nanoseconds


def main(enriched_situation_path, account_situation_path, currency_prices_files):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column currency in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """
    # Read required currency to enrich
    asdf_currency_used = pipeline_fct.get_currency_list_from_asdf(account_situation_path)

    # Get and set df
    asdf = pd.read_csv(account_situation_path, sep=',')
    enriched_situation = asdf.copy(deep=True)

    # Add price columns
    for currency in asdf_currency_used :
        currency_price_column = f"{currency}_price"
        enriched_situation[currency_price_column] = 'null'

    # Fill price columns
    for currency in asdf_currency_used :

        if currency in ['USD', 'CRO']: 
            enriched_situation[f"{currency}_price"] = 0
            continue  

        print("go for currency : ", currency)
        # Ouvrir le fichier contenant les prix
        filename = currency_prices_files[currency]
        kraken_data_price = f'D:/Data_Kraken/Kraken_Trading_History/{filename}.csv'
        kraken_data__price_df = pd.read_csv(kraken_data_price, names=["timestamp","price","unknown"], sep=',')

        # ------------------------------------------
        # -----  Info sur le fichier des prix  -----
        # ------------------------------------------
        # print("Recherche des prix pour cette journée")
        # print("fichier des prix de : ", currency)
        # print("longueur du fichier : ", len(kraken_data__price_df))
        # timestamp_first_row = kraken_data__price_df.loc[0]["timestamp"]
        # timestamp_last_row = kraken_data__price_df.loc[len(kraken_data__price_df)-1]["timestamp"]
        # date_first_row = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_first_row))
        # date_last_row = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp_last_row))
        # print(f"Le fichier des prix commence à : {timestamp_first_row} --> date_first_row : {date_first_row}")
        # print(f"Le fichier des prix termine à  : {timestamp_last_row} --> date_last_row : {date_last_row}")


        # Pour une currency donné, pour chaque ligne de enriched_situation, on va trouver le prix de la currency au moment du trade
        print("début de la boucle")
        for index in range(1, len(enriched_situation)) : 
        # for index in range(0, 2) : 
            # print(f"--------------------- enriched_situation : ligne {index} ---------------------")
            # Identifier la journée du trade (déterminer timestamp de départ et timestamp de fin)
            trade_date = enriched_situation.loc[index]["Date"]
            date_obj = datetime.strptime(trade_date, "%Y-%m-%d %H:%M:%S")
            day_start = str(date_obj.replace(hour=0, minute=0, second=0))
            day_end = str(date_obj.replace(hour=23, minute=59, second=59))
            # print("observed trade date : ", trade_date)
            # print(f"observed trade, day start : {day_start} --> day end : {day_end}")

            # Convertir en timstamp format utilisé par le fichier .csv des prix
            day_start_unix_nanoseconds = date_time_to_unix_nanoseconds(day_start)
            day_end_unix_nanoseconds = date_time_to_unix_nanoseconds(day_end)
            # print(f"observed trade, day start : {day_start_unix_nanoseconds} --> day end : {day_end_unix_nanoseconds}")

            # Dans le fichier contenant les prix, faire la moyenne pour la journée qui concerne le trade
            average_price = get_average_price(kraken_data__price_df, day_start_unix_nanoseconds, day_end_unix_nanoseconds)
            # print("prix moyen de la journée de trade : ", average_price)
            enriched_situation.loc[index, f"{currency}_price"] = average_price

            # Passer à la ligne suivante de la colonne


    # Export as enriched_situation.csv
    enriched_situation.to_csv(enriched_situation_path, index=False)
    # print(enriched_situation)



# File path
enriched_situation_path = 'Data/3_enriched_as/all_trades_enriched_as.csv'
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'
currency_prices_files = {
    'ETH' : 'ETHEUR',
    'BTC' : 'XBTEUR',
    'CRO' : 'CROEUR',
    'ADA' : 'ADAEUR',
    'XRP' : 'XRPEUR',
    'SOL' : 'SOLEUR',
    'DOT' : 'DOTEUR',
    'ORCA' : 'ORCAEUR',
    'SEI' : 'SEIEUR',
    'LINK' : 'LINKEUR',
    'ARB' : 'ARBEUR',
    'QNT' : 'QNTEUR',
    'MATIC' : 'MATICEUR',
    'INJ' : 'INJEUR',
    'IMX' : 'IMXEUR',
    'OP' : 'OPEUR',
    'USDT' : 'USDTEUR',
    'AVAX' : 'AVAXEUR',
    'ICP' : 'ICPEUR',
    'NEAR' : 'NEAREUR',
    'ASTR' : 'ASTREUR',
    'RNDR' : 'RNDREUR',
    'FET' : 'FETEUR',
    'GRT' : 'GRTEUR',
    'FIL' : 'FILEUR',
    'TRX' : 'TRXEUR',
    'ALGO' : 'ALGOEUR',
    'BIT' : 'BITEUR',
    'PYTH' : 'PYTHEUR',
    'ANKR' : 'ANKREUR',
    'GALA' : 'GALAEUR',
    'ATOM' : 'ATOMEUR',
    'ONDO' : 'ONDOEUR',
    'USDC' : 'USDCEUR'
}

main(enriched_situation_path, account_situation_path, currency_prices_files)
