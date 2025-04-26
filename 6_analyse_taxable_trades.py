import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct


def main(taxable_trades_situation_path, account_situation_path):
    """
    """

    asdf_crypto_used = pipeline_fct.get_crypto_list_from_asdf(account_situation_path)

    taxable_trades_situation = pd.read_csv(taxable_trades_situation_path, sep=',')

    count = 0
    for row_index in range(0,len(taxable_trades_situation)):
        for crypto in asdf_crypto_used :
            crypto_price = taxable_trades_situation.loc[row_index][crypto + "_price"]
            crypto_amount = taxable_trades_situation.loc[row_index][crypto]
            if pd.isna(crypto_price) and crypto_amount > 0 : 
            # if pd.isna(crypto_price)  : 
                Date = taxable_trades_situation.loc[row_index]["Date"]
                Platform = taxable_trades_situation.loc[row_index]["Platform"]
                print(f"{Date} - {Platform} - {crypto} value = {crypto_price}")
                count += 1
    print("count : ", count)

# File path
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'
taxable_trades_situation_path = 'Data/5_taxable_trades_as/taxable_trades_situation.csv'


main(taxable_trades_situation_path, account_situation_path)
