import pandas as pd
import numpy as np

def add_amount_to_curreny_in_row(row, currency, amount_to_add):
    current_ammount = row[currency]
    new_amount = current_ammount + amount_to_add
    row[currency] = new_amount
    # print(f"Add amount : {current_ammount}{currency}")
    return row

def remove_amount_to_currency_in_row(row, currency, amount_to_remove):
    current_ammount = row[currency]
    new_amount = current_ammount - amount_to_remove
    row[currency] = new_amount
    # print(f"Remove amount : {current_ammount}{currency}")
    return row

def add_row_to_asdf_from_transaction_row(row_ready_for_ingest, row_asdf_last_row):

    # Observed transaction
    Received_Currency = row_ready_for_ingest["Received Currency"] 
    Received_Amount = row_ready_for_ingest["Received Amount"]
    Sent_Currency = row_ready_for_ingest["Sent Currency"] 
    Sent_Amount  = row_ready_for_ingest["Sent Amount"]

    row_asdf_last_row["Date"] = row_ready_for_ingest["Date"]
    row_asdf_last_row["Platform"] = row_ready_for_ingest["platform"]

    if Received_Currency in ['EUR', 'USD'] : row_asdf_last_row['Sell_crypto_for_currency'] = True
    else : row_asdf_last_row['Sell_crypto_for_currency'] = False
    
    # print(f"Spent {Sent_Amount} {Sent_Currency}, received {Received_Amount}{Received_Currency}")
    # print(f"Old amount : {row_asdf_last_row[Received_Currency]}{Received_Currency} and {row_asdf_last_row[Sent_Currency]}{Sent_Currency}")

    # Add received amount
    row_asdf_last_row = add_amount_to_curreny_in_row(row_asdf_last_row.copy() , Received_Currency, Received_Amount)
    row_asdf_last_row = remove_amount_to_currency_in_row(row_asdf_last_row.copy() , Sent_Currency, Sent_Amount)
    # print(f"New amount : {row_asdf_last_row[Received_Currency]}{Received_Currency} and {row_asdf_last_row[Sent_Currency]}{Sent_Currency}")

    return row_asdf_last_row


def main(ready_for_ingest_filepath,result_filepath):
    """
    Cette fonction lis un fichier ready_for_ingest et le met en ordre pour être ingéré par l'app en ligne
    """

    # Import data file and create empty export df (to be filled)
    ready_for_ingest = pd.read_csv(ready_for_ingest_filepath, sep=',')

    # Define columns
    unique_currency_list = ready_for_ingest['Received Currency'].unique().tolist()
    columns = ['Date'] + ['Platform'] + ['Sell_crypto_for_currency'] + unique_currency_list

    # Define first row (filled with 0 amount of each currency)
    data = {col: 0.0 if col in unique_currency_list else '' for col in columns}

    # Create df
    asdf = pd.DataFrame(data, index=[0])
    for currency in unique_currency_list:
        asdf[currency] = asdf[currency].astype('float64')

    # Iterate on ready_for_ingest, convert each transaction into a new account situation row
    for index in range(0,len(ready_for_ingest)):

        # Define ready_for_ingest row to add, add a row to asdf
        row_ready_for_ingest = ready_for_ingest.loc[index]
        asdf.loc[index+1] = asdf.loc[index]

        # If ready_for_ingest row is a transaction, add it to asdf
        if row_ready_for_ingest['Type'] in ['buy', 'sell', 'trade'] :
            asdf_last_row = asdf.loc[index].copy()
            asdf.loc[index+1] = add_row_to_asdf_from_transaction_row(row_ready_for_ingest, asdf_last_row)

    asdf.to_csv(result_filepath, index=False)


ready_for_ingest_filepath = 'Data/1_ready_for_ingest/all_trades_ready_for_ingest.csv'
result_filepath = 'Data/2_account_situation/all_trades_account_situation.csv'
main(ready_for_ingest_filepath,result_filepath)
