import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct

def create_column_position_value(computed_situation, crypto):
    currency_amount_eur_column = f"{crypto}_position_value"
    currency_price_column = f"{crypto}_price"
    computed_situation[currency_amount_eur_column] = computed_situation[crypto]*computed_situation[currency_price_column]

def main(computed_situation_path, enriched_situation_path, account_situation_path):
    """
    """

    asdf_currency_used = pipeline_fct.get_crypto_list_from_asdf(account_situation_path)

    # Pour chaque position, on va calculer sa valeur en euro 
    # quantité de crypto X sa valeur en euro = valeur de la position
    enriched_situation = pd.read_csv(enriched_situation_path, sep=',')
    computed_situation = enriched_situation.copy(deep=True)
    for crypto in asdf_currency_used :
        create_column_position_value(computed_situation, crypto)

    # Ajout de la colonne valeur total du portefeuille 
    computed_situation["total_eur"] = 0  
    for currency in asdf_currency_used :
        currency_amount_eur_column = f"{currency}_position_value"
        computed_situation["total_eur"] += computed_situation[currency_amount_eur_column] 

    # Ajout de la colonne diff_eur qui permet de savoir combien d'euro on été encaissé ou dépensé
    computed_situation['diff_eur'] = computed_situation['EUR'].diff()
    computed_situation['diff_usd'] = computed_situation['USD'].diff()
    
    computed_situation.to_csv(computed_situation_path, index=False)

# File path
computed_situation_path = 'Data/4_computed_as/all_trades_computed_situation.csv'
enriched_situation_path = 'Data/3_enriched_as/all_trades_enriched_as.csv'
account_situation_path = 'Data/2_account_situation/all_trades_account_situation.csv'

main(computed_situation_path, enriched_situation_path, account_situation_path)
