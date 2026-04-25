import pandas as pd
import module_global
import config

def main(enriched_situation_path, enriched_situation_with_fees_worth_path):
    """
    Start from account_situation.csv to produce enriched_situation.csv
    For each column crypto in account_situation.csv, enriched_situation.csv adds a ccurency_price column
    """

    crypto_used_list = module_global.get_crypto_list_from_all_trades()
    crypto_prices_files = module_global.get_kraken_price_files_name()


    # Get and set df
    esdf = pd.read_csv(enriched_situation_path, sep=',')
    enriched_situation = esdf.copy(deep=True)


    enriched_situation[["Fee Net Worth"]] = float(0)


    price_db = config.FILE_PRICE_DB
    price_db_df = pd.read_csv(price_db, sep=',')


    for row_index in range(1, len(enriched_situation)):
        # On utilise la devise normalisée pour chercher le prix dans la base de données
        fee_currency = enriched_situation.loc[row_index, 'Normalized Fee Currency']
        fee_amount = enriched_situation.loc[row_index, 'Fee Amount']
        trade_date = enriched_situation.loc[row_index, "Date"]
        if not pd.isna(fee_currency) :

            if fee_currency not in ["EUR", "USD"]: 
                
                lignes_trouvees_in_price_db = price_db_df[price_db_df['Date'] == trade_date]
                if len(lignes_trouvees_in_price_db) > 0:
                    price_from_price_db = lignes_trouvees_in_price_db[f'{fee_currency}_price'].iloc[0]

                    if not pd.isna(price_from_price_db) : 
                        enriched_situation.loc[row_index, f"Fee Net Worth"] = enriched_situation.loc[row_index, f"Fee Amount"] * price_from_price_db
                    else :

                        print(f"ligne {row_index} : recherche du fee net worth de {fee_amount} {fee_currency}, date : {trade_date}")  
                        print("prix non trouvé")
                        enriched_situation.loc[row_index, f"Fee Net Worth"] = 0

            else : 
                enriched_situation.loc[row_index, f"Fee Net Worth"] = enriched_situation.loc[row_index, f"Fee Amount"]
        else : 
            print(f"ligne {row_index} : recherche du fee net worth de {fee_amount} {fee_currency}, date : {trade_date}")  
            print(f"ligne {row_index} : pas de fee currency pour {fee_currency}")
            enriched_situation.loc[row_index, f"Fee Net Worth"] = 0

    enriched_situation.to_csv(enriched_situation_with_fees_worth_path, index=False)

# File path
enriched_situation_path = config.FILE_AS_WITH_PRICES
enriched_situation_with_fees_worth_path = config.FILE_ES_WITH_FEES_WORTH


main(enriched_situation_path, enriched_situation_with_fees_worth_path)
