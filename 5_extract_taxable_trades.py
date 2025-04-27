import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct


def main(computed_situation_path, taxable_trades_situation_path):
    """
    """
    computed_situation = pd.read_csv(computed_situation_path, sep=',')
    
    taxable_trades_situation = computed_situation[computed_situation['Type'] == 'sell']
    # taxable_trades_situation = computed_situation.copy(deep=True)

    col_to_keep = ['Date', 'EUR_spent', 'before_trade_EUR_spent', 'wallet_value_eur', 'before_trade_wallet_value_eur', 'prix_cession', 'plus_value_du_sell']
    taxable_trades_situation_filtered = taxable_trades_situation[col_to_keep]

    taxable_trades_situation_filtered.to_csv(taxable_trades_situation_path, index=False)

# File path
computed_situation_path = 'Data/4_computed_as/computed_situation.csv'
taxable_trades_situation_path = 'Data/5_taxable_trades_as/taxable_trades.csv'

main(computed_situation_path, taxable_trades_situation_path)
