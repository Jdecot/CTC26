import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct


def main(computed_situation_path, taxable_trades_situation_path, account_situation_path):
    """
    """

    asdf_currency_used = pipeline_fct.get_crypto_list_from_asdf(account_situation_path)

    computed_situation = pd.read_csv(computed_situation_path, sep=',')
    
    taxable_trades_situation = computed_situation[computed_situation['Sell_crypto_for_currency'] == True]
    # taxable_trades_situation = computed_situation.copy(deep=True)
    taxable_trades_situation.to_csv(taxable_trades_situation_path, index=False)

# File path
computed_situation_path = 'Data/4_computed_as/all_trades_computed_situation.csv'
taxable_trades_situation_path = 'Data/5_taxable_trades_as/taxable_trades_situation.csv'
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'

main(computed_situation_path, taxable_trades_situation_path, account_situation_path)
