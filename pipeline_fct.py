import pandas as pd

# def get_crypto_list_from_asdf(account_situation_path):
    
#     account_situation_columns = pd.read_csv(account_situation_path, sep=',').columns.tolist()
#     account_situation_columns.remove('Date')
#     account_situation_columns.remove('Type')
#     account_situation_columns.remove('EUR')
#     account_situation_columns.remove('USD')
#     account_situation_columns.remove('Platform')
#     return account_situation_columns

def get_crypto_list_from_all_trades():
    
    all_trades_path = 'Data/1_ready_for_ingest/all_trades.csv'
    all_trades = pd.read_csv(all_trades_path, sep=',')
    
    unique_received_currency = all_trades['Received Currency'].dropna().unique().tolist()
    unique_sent_currency = all_trades['Sent Currency'].dropna().unique().tolist()

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

# import time

# target_datetime = "2025-03-29 18:19:00"  # Date et heure au format AAAA-MM-JJ HH:MM:SS
# target_timestamp = int(time.mktime(time.strptime(target_datetime, '%Y-%m-%d %H:%M:%S')))
# date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target_timestamp))

# print(target_datetime)
# print(target_timestamp)
# print(date)

# *************    Get date from timestamp    *************
# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1559347203)))


# def date_time_to_unix_nanoseconds(date_time_str, format_str='%Y-%m-%d %H:%M:%S'):
#     """
#     Convertit une date et une heure en nanosecondes Unix.
    
#     Exemple d'utilisation
#     date_time_str = '2023-10-27 15:30:00'
#     unix_nanoseconds = date_time_to_unix_nanoseconds(date_time_str)
#     print(f'Nanosecondes Unix : {unix_nanoseconds}')
#     """

#     time_struct = time.strptime(date_time_str, format_str)
#     unix_seconds = int(time.mktime(time_struct))
#     unix_nanoseconds = unix_seconds * 1000000000  # Multiplier par 1 milliard

#     return unix_nanoseconds

