import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct
import config

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
    enriched_situation_df["wallet_value_eur_m1"] = 0 
    enriched_situation_df["wallet_value_eur_m1"]  = enriched_situation_df["wallet_value_eur_m1"].astype('float64')

    for crypto in crypto_used_list :
        create_column_position_value(enriched_situation_df, crypto)
        crypto_amount_eur_column = f"{crypto}_position_value"
        enriched_situation_df["wallet_value_eur"] += enriched_situation_df[crypto_amount_eur_column].fillna(value=0)

    # enriched_situation_df["wallet_value_eur_m1"] = enriched_situation_df["wallet_value_eur"].shift(1)

    # Pv = Prix de cession – (Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille)

    # col_to_debug = ["Date", "Platform", "Type", "EUR_spent", "EUR_received", "wallet_value_eur",	"wallet_value_eur_m1","PTA","fraction_capital_initial", "plus_value", "Money_movement", "Fee Currency","Fee Amount","Fee Net Worth"]
    # # col_to_debug = ["Date", "Type", "wallet_value_eur",	"wallet_value_eur_m1","PTA","fraction_capital_initial", "plus_value", "Money_movement", "Fee Currency","Fee Amount","Fee Net Worth"]
    # print(enriched_situation_df[col_to_debug].head(10))
    # Export Excel via fonction commune (décommenter si besoin)
    # pipeline_fct.export_to_excel(enriched_situation_df, 'Data/4_computed_as/debug_computed_situation.xlsx')
    # pipeline_fct.export_to_excel(enriched_situation_df[col_to_debug].head(10), 'Data/4_computed_as/debug_filtered_computed_situation.xlsx')
    
    # Liste des colonnes à mettre au début (dans l'ordre souhaité)
    colonnes_debut = ["Date", "Platform", "Type", "wallet_value_eur", "wallet_value_eur_m1", "Money_movement", "Fee Currency","Fee Amount","Fee Net Worth"]
    colonnes_restantes = [col for col in enriched_situation_df.columns if col not in colonnes_debut]
    nouvel_ordre_colonnes = colonnes_debut + colonnes_restantes
    computed_situation_df_reordonne = enriched_situation_df[nouvel_ordre_colonnes]

    # Export Excel via fonction commune (décommenter si besoin)
    # pipeline_fct.export_to_excel(computed_situation_df_reordonne, 'Data/4_computed_as/debug_crypto_positions.xlsx')
    computed_situation_df_reordonne.to_csv(computed_situation_path, index=False)

    return computed_situation_df_reordonne

    

# File path
computed_situation_path = config.FILE_CRYPTO_POSITIONS
enriched_situation_path = config.FILE_ES_WITH_FEES_WORTH

enriched_situation = pd.read_csv(enriched_situation_path, sep=',')
computed_situation = compute_df(enriched_situation.copy(deep=True))
