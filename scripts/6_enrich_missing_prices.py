import pandas as pd
import pipeline_fct
import config


def main(taxable_trades_situation_path, ):
    """
    """

    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()

    taxable_trades_situation = pd.read_csv(taxable_trades_situation_path, sep=',')

    count = 0
    for row_index in range(0,len(taxable_trades_situation)):
        for crypto in crypto_used_list :
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
taxable_trades_situation_path = config.FILE_TAXABLE_TRADES


main(taxable_trades_situation_path)
