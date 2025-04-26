import pandas as pd

def get_crypto_list_from_asdf(account_situation_path):
    
    account_situation_columns = pd.read_csv(account_situation_path, sep=',').columns.tolist()
    account_situation_columns.remove('Date')
    account_situation_columns.remove('EUR')
    account_situation_columns.remove('USD')
    account_situation_columns.remove('Platform')
    account_situation_columns.remove('Sell_crypto_for_currency')
    return account_situation_columns





# import time

# target_datetime = "2025-03-29 18:19:00"  # Date et heure au format AAAA-MM-JJ HH:MM:SS
# target_timestamp = int(time.mktime(time.strptime(target_datetime, '%Y-%m-%d %H:%M:%S')))
# date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(target_timestamp))

# print(target_datetime)
# print(target_timestamp)
# print(date)

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

