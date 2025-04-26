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

    # Calcul de la moyenne pondéré
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
    return unix_seconds


def add_price_columns(enriched_situation, asdf_crypto_used):
    # Add price columns
    for crypto in asdf_crypto_used :
        crypto_price_column = f"{crypto}_price"
        enriched_situation[crypto_price_column] = 'null'
    return enriched_situation
    

def trade_date_to_cap_unix_nanoseconds(trade_date):
    date_obj = datetime.strptime(trade_date, "%Y-%m-%d %H:%M:%S")
    day_start = str(date_obj.replace(hour=0, minute=0, second=0))
    day_end = str(date_obj.replace(hour=23, minute=59, second=59))

    # Convertir en timstamp format utilisé par le fichier .csv des prix
    day_start_unix_nanoseconds = date_time_to_unix_nanoseconds(day_start)
    day_end_unix_nanoseconds = date_time_to_unix_nanoseconds(day_end)

    return day_start_unix_nanoseconds, day_end_unix_nanoseconds


def main(enriched_situation_path, account_situation_path, crypto_prices_files):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """
    # Read required crypto to enrich
    asdf_crypto_used = pipeline_fct.get_crypto_list_from_asdf(account_situation_path)

    # Get and set df
    asdf = pd.read_csv(account_situation_path, sep=',')
    enriched_situation = asdf.copy(deep=True)

    # Add price columns : f"{crypto}_price"
    enriched_situation = add_price_columns(enriched_situation, asdf_crypto_used)

    # Fill price columns with average price for the day
    for crypto in asdf_crypto_used :

        if crypto in ['CRO']: 
            print("cro")
            enriched_situation[f"{crypto}_price"] = ''
            continue  

        print("go for crypto : ", crypto)
        # Ouvrir le fichier contenant les prix
        filename = crypto_prices_files[crypto]
        kraken_data_price = f'D:/Data_crypto_tax_calculator/Kraken_Trading_History/{filename}.csv'
        kraken_data__price_df = pd.read_csv(kraken_data_price, names=["timestamp","price","unknown"], sep=',')


        # Pour une crypto donné, pour chaque ligne de enriched_situation, on va chercher le prix de la crypto au moment du trade
        print("début de la boucle")
        for row_index in range(1, len(enriched_situation)) : 

            # Identifier la journée du trade (déterminer timestamp de départ et timestamp de fin)
            trade_date = enriched_situation.loc[row_index]["Date"]
            day_start_unix_nanoseconds, day_end_unix_nanoseconds = trade_date_to_cap_unix_nanoseconds(trade_date)

            # Dans le fichier contenant les prix, faire la moyenne pour la journée qui concerne le trade
            average_price = get_average_price(kraken_data__price_df, day_start_unix_nanoseconds, day_end_unix_nanoseconds)

            enriched_situation.loc[row_index, f"{crypto}_price"] = average_price
            # Passer à la ligne suivante de la colonne crypto qu'on est en train de fill

    # Export as enriched_situation.csv
    enriched_situation.to_csv(enriched_situation_path, index=False)



# File path
enriched_situation_path = 'Data/3_enriched_as/all_trades_enriched_as.csv'
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'
crypto_prices_files = {
    'ETH'   : 'ETHEUR',
    'BTC'   : 'XBTEUR',
    'CRO'   : 'CROEUR',
    'ADA'   : 'ADAEUR',
    'XRP'   : 'XRPEUR',
    'SOL'   : 'SOLEUR',
    'DOT'   : 'DOTEUR',
    'ORCA'  : 'ORCAEUR',
    'SEI'   : 'SEIEUR',
    'LINK'  : 'LINKEUR',
    'ARB'   : 'ARBEUR',
    'QNT'   : 'QNTEUR',
    'MATIC' : 'MATICEUR',
    'INJ'   : 'INJEUR',
    'IMX'   : 'IMXEUR',
    'OP'    : 'OPEUR',
    'USDT'  : 'USDTEUR',
    'AVAX'  : 'AVAXEUR',
    'ICP'   : 'ICPEUR',
    'NEAR'  : 'NEAREUR',
    'ASTR'  : 'ASTREUR',
    'RNDR'  : 'RNDREUR',
    'FET'   : 'FETEUR',
    'GRT'   : 'GRTEUR',
    'FIL'   : 'FILEUR',
    'TRX'   : 'TRXEUR',
    'ALGO'  : 'ALGOEUR',
    'BIT'   : 'BITEUR',
    'PYTH'  : 'PYTHEUR',
    'ANKR'  : 'ANKREUR',
    'GALA'  : 'GALAEUR',
    'ATOM'  : 'ATOMEUR',
    'ONDO'  : 'ONDOEUR',
    'USDC'  : 'USDCEUR'
}

main(enriched_situation_path, account_situation_path, crypto_prices_files)
