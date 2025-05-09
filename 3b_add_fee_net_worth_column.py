import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct
import os


def main(enriched_situation_path, enriched_situation_with_fees_worth_path):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """

    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()
    crypto_prices_files = pipeline_fct.get_kraken_price_files_name()


    # Get and set df
    esdf = pd.read_csv(enriched_situation_path, sep=',')
    enriched_situation = esdf.copy(deep=True)




# File path
enriched_situation_path = 'Data/3_enriched_as/as_with_crypto_prices.csv'
enriched_situation_with_fees_worth_path = 'Data/3_enriched_as/es_with_fees_worth.csv'


main(enriched_situation_path, enriched_situation_with_fees_worth_path)
