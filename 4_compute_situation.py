import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct



def main(compute_situation_path, enriched_situation_path, account_situation_path):
    """
    """

    asdf_currency_used = pipeline_fct.get_currency_list_from_asdf(account_situation_path)

    enriched_situation = pd.read_csv(enriched_situation_path, sep=',')
    computed_situation = enriched_situation.copy(deep=True)
    for currency in asdf_currency_used :
        currency_amount_eur_column = f"{currency}_amount_eur"
        currency_price_column = f"{currency}_price"
        computed_situation[currency_amount_eur_column] = computed_situation[currency]*computed_situation[currency_price_column]


    computed_situation["total_eur"] = 0  # Initialise la colonne de somme à zéro
    for currency in asdf_currency_used :
        currency_amount_eur_column = f"{currency}_amount_eur"
        computed_situation["total_eur"] += computed_situation[currency_amount_eur_column] 
    
    computed_situation.to_csv(compute_situation_path, index=False)

# File path
compute_situation_path = 'Data/4_computed_as/all_trades_compute_situation.csv'
enriched_situation_path = 'Data/3_enriched_as/all_trades_enriched_as.csv'
# enriched_situation_path = 'Data/3_enriched_as/3_test.csv'
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'

main(compute_situation_path, enriched_situation_path, account_situation_path)
