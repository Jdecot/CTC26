import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct

def create_column_position_value(computed_situation, crypto):
    currency_amount_eur_column = f"{crypto}_position_value"
    crypto_price_column = f"{crypto}_price"

    computed_situation[currency_amount_eur_column] = 0
    computed_situation[currency_amount_eur_column] = computed_situation[currency_amount_eur_column].astype('float64')
    
    # for row_index in range(0, 2) : 
    for row_index in range(0, len(computed_situation)) : 

        # if computed_situation.loc[row_index, crypto] < 0 :
        #     print(f"Alerte - Une quantité de {crypto} est inférieur à 0")
        if computed_situation.loc[row_index, crypto] <= 0 : 
            computed_situation.loc[row_index, currency_amount_eur_column] = 0
        else : 
            crypto_qtt = computed_situation.loc[row_index, crypto]
            crypto_price = computed_situation.loc[row_index, crypto_price_column]
            crypto_amount_in_eur = crypto_qtt*crypto_price
            computed_situation.loc[row_index, currency_amount_eur_column] = crypto_amount_in_eur
    

def compute_df(enriched_situation_df):
    """
    Pour chaque crypto on va créer une colonne crypto position value
    Puis on va crée une colonne total_eur et obtenir ses valeurs en additionant toutes les crypto_position_value

    """

    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()

    # Pour chaque position, on va calculer sa valeur en euro 
    # quantité de crypto X sa valeur en euro = valeur de la position

    enriched_situation_df["wallet_value_eur"] = 0 
    enriched_situation_df["wallet_value_eur"]  = enriched_situation_df["wallet_value_eur"].astype('float64')
    enriched_situation_df["before_trade_wallet_value_eur"] = 0 
    enriched_situation_df["before_trade_wallet_value_eur"]  = enriched_situation_df["before_trade_wallet_value_eur"].astype('float64')
    enriched_situation_df['plus_value_du_sell'] = 0
    enriched_situation_df['plus_value_du_sell'] = enriched_situation_df['plus_value_du_sell'].astype('float64')

    for crypto in crypto_used_list :
        create_column_position_value(enriched_situation_df, crypto)
        crypto_amount_eur_column = f"{crypto}_position_value"
        enriched_situation_df["wallet_value_eur"] += enriched_situation_df[crypto_amount_eur_column].fillna(value=0)


    
    # enriched_situation_df["before_trade_EUR_spent"] = enriched_situation_df["EUR_spent"].shift(1)


    enriched_situation_df['prix_cession'] = enriched_situation_df['EUR_spent'].diff() * -1
    enriched_situation_df["before_trade_wallet_value_eur"] = enriched_situation_df["wallet_value_eur"].shift(1)
    enriched_situation_df['before_trade_EUR_spent'] = enriched_situation_df['EUR_spent'].shift(1)
    enriched_situation_df['plus_value_du_sell'] = enriched_situation_df['prix_cession'] - (enriched_situation_df['before_trade_EUR_spent']*enriched_situation_df['prix_cession']/enriched_situation_df["before_trade_wallet_value_eur"])

    # Pv = Prix de cession – (Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille)

    return enriched_situation_df

    

# File path
computed_situation_path = 'Data/4_computed_as/computed_situation.csv'
enriched_situation_path = 'Data/3_enriched_as/as_with_crypto_prices.csv'

enriched_situation = pd.read_csv(enriched_situation_path, sep=',')
computed_situation = compute_df(enriched_situation.copy(deep=True))



# print(computed_situation.head())
# for row_index in [4]: 
#     print("row_index : ", row_index)
#     print(f"plus_value_du_sell : {computed_situation.loc[row_index, 'plus_value_du_sell']}")
#     print(f"prix_cession : {computed_situation.loc[row_index, 'prix_cession']}")
#     print(f"EUR_spent : {computed_situation.loc[row_index, 'EUR_spent']}")
#     print(f"wallet_value_eur : {computed_situation.loc[row_index, 'wallet_value_eur']}")
#     print(f"previous_wallet_value_eur : {computed_situation.loc[row_index, 'previous_wallet_value_eur']}")

computed_situation.to_csv(computed_situation_path, index=False)