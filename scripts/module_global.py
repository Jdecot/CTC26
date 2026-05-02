import pandas as pd
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
import time
import config
from pathlib import Path

def convert_csv_to_excel(csv_input_path, excel_output_path):
    """
    Converts a single CSV file to an Excel file.
    Ensures the destination directory exists before writing.
    """
    try:
        # Create parent directory if it does not exist
        Path(excel_output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Read CSV data and export to Excel format
        # Standard comma separator used by default
        data_frame = pd.read_csv(csv_input_path, sep=',')
        data_frame.to_excel(excel_output_path, index=False)
        return True
    except Exception as error:
        print(f"  ✗ Error during conversion of {csv_input_path}: {error}")
        return False
    

def get_crypto_list_from_all_trades():
    
    # On utilise le fichier normalisé pour obtenir la liste propre des cryptos
    all_trades_path = config.FILE_ALL_TRADES_NORMALIZED
    if not os.path.exists(all_trades_path):
        all_trades_path = config.FILE_ALL_TRADES
        
    all_trades = pd.read_csv(all_trades_path, sep=',')
    
    # On se base sur les colonnes normalisées (doivent exister pour la sécurité)
    unique_received_currency = all_trades['Normalized Received Currency'].dropna().unique().tolist()
    unique_sent_currency = all_trades['Normalized Sent Currency'].dropna().unique().tolist()

    combined_currencies = unique_received_currency + unique_sent_currency

    # Obtenir les valeurs uniques de la liste combinée
    all_unique_currencies = list(set(combined_currencies))

    # Enlever 'EUR' et 'USD' de la liste
    currencies_to_remove = ['EUR', 'USD']
    filtered_currencies = [currency for currency in all_unique_currencies if currency not in currencies_to_remove]

    return filtered_currencies


def get_kraken_price_files_name():
    crypto_prices_files = {
        'ETH'   : 'ETHEUR',
        'BTC'   : 'XBTEUR',
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
        'USDC'  : 'USDCEUR',
        'PEPE'  : 'PEPEEUR',
        'JUP'   : 'JUPEUR',
        'DOGE'  :'DOGEEUR',
        'TAO'   : 'TAOEUR',
        'SUI'   : 'SUIEUR',
        'CRO'   : 'CROEUR',
    }
    return crypto_prices_files

    
#     Exemple d'utilisation
#     date_time_str = '2023-10-27 15:30:00'
#     unix_nanoseconds = date_time_to_unix_nanoseconds(date_time_str)
#     print(f'Nanosecondes Unix : {unix_nanoseconds}')
#     """

#     time_struct = time.strptime(date_time_str, format_str)
#     unix_seconds = int(time.mktime(time_struct))
#     unix_nanoseconds = unix_seconds * 1000000000  # Multiplier par 1 milliard

#     return unix_nanoseconds




"""
****************************
3 - Enrich account situation
****************************
"""

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


def load_prices_file_as_df(filename):

    kraken_data_price = config.DIR_KRAKEN_PRICES / f"{filename}.csv"
    price_to_use = pd.DataFrame()
    print(f"{kraken_data_price},  existe and loading : ", os.path.exists(kraken_data_price))

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


def get_start_and_end_date_of_the_day(date) :  
    date_obj = pd.to_datetime(date)
    day_start = date_obj.strftime("%Y-%m-%d 00:00:00")
    day_end = date_obj.strftime("%Y-%m-%d 23:59:59")
    return day_start, day_end


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


def trade_date_to_cap_unix_nanoseconds(trade_date):

    day_start, day_end = get_start_and_end_date_of_the_day(trade_date)
    # Convertir en timstamp format utilisé par le fichier .csv des prix
    day_start_unix_nanoseconds = date_time_to_unix_nanoseconds(day_start)
    day_end_unix_nanoseconds = date_time_to_unix_nanoseconds(day_end)

    return day_start_unix_nanoseconds, day_end_unix_nanoseconds

def show_holdings():
    """Lit la dernière ligne de account_situation.csv et affiche les holdings triés."""
    csv_path = config.FILE_ACCOUNT_SITUATION
    
    if not csv_path.exists():
        print(f"⚠️  Fichier non trouvé : {csv_path}")
        return
    
    df = pd.read_csv(csv_path, dtype=str)
    if df.empty:
        print("⚠️  Le fichier account_situation.csv est vide")
        return
    
    last_row = df.iloc[-1]
    
    # Colonnes techniques ou de transaction à ne pas afficher comme des holdings
    cols_to_ignore = [
        "Date", "platform", "Platform", "refid", "subtype", "Type", "Detected Type", 
        "Received Currency", "Normalized Received Currency", "Received Amount", "Received Net Worth",
        "Sent Currency", "Normalized Sent Currency", "Sent Amount", "Sent Net Worth", 
        "Fee Currency", "Normalized Fee Currency", "Fee Amount", "Fee Net Worth",
        "Balance", "Money_movement", "wallet_value_eur", "wallet_value_eur_m1", "EUR", "USD"
    ]

    holdings = {}
    for col in df.columns:
        if col in cols_to_ignore:
            continue
        try:
            raw_val = str(last_row[col]).strip()
            # On ignore les colonnes vides ou contenant 'nan' pour éviter les erreurs de tri
            if raw_val == "" or raw_val.lower() == "nan":
                continue
                
            val = Decimal(raw_val)
            # On ne garde que les nombres finis (pas NaN, pas Infini) et non nuls
            if not val.is_finite():
                continue
            if val != Decimal('0'):
                holdings[col] = val
        except (ValueError, TypeError, InvalidOperation):
            # Ignore les colonnes non numériques ou valeurs non convertibles
            pass
    
    sorted_holdings = dict(sorted(holdings.items(), key=lambda x: x[1], reverse=True))
    
    print("\n" + "="*40)
    print("📊 HOLDINGS (dernière ligne)")
    print("="*40)
    for crypto, qty in sorted_holdings.items():
        # Formate en décimal avec 18 chiffres max après la virgule, en supprimant les zéros inutiles à la fin
        print(f"  {crypto}: {qty:.18f}".rstrip('0').rstrip('.'))

def reorder_columns(df):
    """Réorganise les colonnes pour mettre les métadonnées et montants au début."""
    cols_prioritaires = [
        "Date", "refid", "subtype", "Type", "Detected Type", 
         "Normalized Received Currency", "Normalized Sent Currency",
        "Sent Currency", "Sent Amount",  
        "Received Currency", "Received Amount",
        "Balance"
    ]

    cols_existantes = [c for c in cols_prioritaires if c in df.columns]
    autres_cols = [c for c in df.columns if c not in cols_existantes]
    return df[cols_existantes + autres_cols]
