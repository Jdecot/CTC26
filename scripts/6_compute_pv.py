import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct
import config


def main(taxable_trades_situation_path, ):
    """
    """

    df_loaded = pd.read_csv(taxable_trades_situation_path, sep=',')
    df_taxable_trades = df_loaded.copy()
    df_taxable_trades['PTA'] = float(0)
    df_taxable_trades['fcicpta'] = float(0)
    df_taxable_trades['plus_value'] = float(0)
    df_taxable_trades['fcicpta'] = float(0)
    for row_index in range(0,len(df_taxable_trades)):

        valeur_global_wallet_m1 = df_taxable_trades.loc[row_index, 'wallet_value_eur_m1']
        prix_cession = df_taxable_trades.loc[row_index, 'prix_cession']

        pta = df_taxable_trades.loc[row_index, 'EUR_spent']
        fraction_capital_initial = (pta * prix_cession / valeur_global_wallet_m1)
        plus_value = prix_cession - fraction_capital_initial

        df_taxable_trades.loc[row_index, 'PTA'] = pta
        df_taxable_trades.loc[row_index, 'fcicpta'] = fraction_capital_initial
        df_taxable_trades.loc[row_index, 'plus_value'] = plus_value

    print(df_taxable_trades[['EUR_spent', 'fcicpta', 'PTA','plus_value','wallet_value_eur_m1','plus_value_du_sell','prix_cession','Money_movement']].head())


# File path
taxable_trades_situation_path = config.FILE_TAXABLE_TRADES


main(taxable_trades_situation_path)
