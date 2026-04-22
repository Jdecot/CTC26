import pandas as pd
import numpy as np
import pipeline_fct
import config

def test_if_trade_EURvsUSD(row):
    # On test si on est pas en train d'échanger de l'EUR contre USD ou vice versa
    if row["Received Currency"] in ['EUR', 'USD'] :
        received_eur_usd = True
    else :
        received_eur_usd = False

    if row["Sent Currency"] in ['EUR', 'USD'] :
        sent_eur_usd = True
    else :
        sent_eur_usd = False

    # define if les deux conditions sont vraies en même temps
    ignore_condition = received_eur_usd & sent_eur_usd
    return ignore_condition


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
    row_asdf_last_row["Type"] = row_ready_for_ingest["Type"]

    row_asdf_last_row['Fee Currency'] = row_ready_for_ingest['Fee Currency']
    row_asdf_last_row['Fee Amount'] = row_ready_for_ingest['Fee Amount']
    row_asdf_last_row['Fee Net Worth'] = row_ready_for_ingest['Fee Net Worth']

    row_asdf_last_row['Money_movement'] = 0

    # Detection des trades impliquant une devise (qui devraient alors être sell ou buy plutôt que trade)
    if row_ready_for_ingest["Type"] == 'trade' and Received_Currency in ['EUR', 'USD']:
        row_asdf_last_row["Type"] = 'sell'
    if row_ready_for_ingest["Type"] == 'trade' and Sent_Currency in ['EUR', 'USD']:
        row_asdf_last_row["Type"] = 'buy'

    # Add received amount to update situation
    if Received_Currency not in ['EUR', 'USD'] : 
        row_asdf_last_row = add_amount_to_curreny_in_row(row_asdf_last_row.copy() , Received_Currency, Received_Amount)
    if Sent_Currency not in ['EUR', 'USD'] : 
        row_asdf_last_row = remove_amount_to_currency_in_row(row_asdf_last_row.copy() , Sent_Currency, Sent_Amount)


    # If transaction is taxable or used to compute "prix total d'acquisition du portefeuille",
    # then memorise how much has been received or sent in globality since the first trade
    if row_asdf_last_row["Type"] == 'buy' and Sent_Currency == 'EUR':
        # row_asdf_last_row['EUR_spent'] = row_asdf_last_row['EUR_spent'] + float(row_ready_for_ingest['Sent Amount'])
        row_asdf_last_row['Money_movement'] = float(row_ready_for_ingest['Sent Amount'])
    if row_asdf_last_row["Type"] == 'buy' and Sent_Currency == 'USD':
        # row_asdf_last_row['EUR_spent'] = row_asdf_last_row['EUR_spent'] + float(row_ready_for_ingest['Sent Amount'])*0.9222
        row_asdf_last_row['Money_movement'] = float(row_ready_for_ingest['Sent Amount'])*0.9222

    if row_asdf_last_row["Type"] == 'sell' and Received_Currency == 'EUR':
        # row_asdf_last_row['EUR_received'] = row_asdf_last_row['EUR_received'] + float(row_ready_for_ingest['Received Amount'])
        row_asdf_last_row['Money_movement'] = float(row_ready_for_ingest['Received Amount'])
    if row_asdf_last_row["Type"] == 'sell' and Received_Currency == 'USD':
        # row_asdf_last_row['EUR_received'] = row_asdf_last_row['EUR_received'] + float(row_ready_for_ingest['Received Amount'])*0.9222
        row_asdf_last_row['Money_movement'] = float(row_ready_for_ingest['Received Amount'])*0.9222




    return row_asdf_last_row


def main(ready_for_ingest_filepath,result_filepath):
    """
    Cette fonction lis un fichier ready_for_ingest et le met en ordre pour être ingéré par l'app en ligne
    """

    # Import data file and create empty export df (to be filled)
    ready_for_ingest = pd.read_csv(ready_for_ingest_filepath, sep=',')

    # Define columns
    crypto_used_list = pipeline_fct.get_crypto_list_from_all_trades()
    print("crypto_used_list : ", crypto_used_list)
    currency_situation_list = ['EUR_spent','EUR_received']
    fees_list = ['Fee Currency','Fee Amount','Fee Net Worth']
    combined_list = crypto_used_list + currency_situation_list + fees_list

    columns = ['Date'] + ['Platform'] + ['Type'] + ['Money_movement'] + combined_list

    # # Define first row (filled with 0 amount of each currency)
    data = {col: 0.0 if col in combined_list else '' for col in columns}

    # Create df
    asdf = pd.DataFrame(data, index=[0])
    for column in combined_list :
        asdf[column] = asdf[column].astype('float64')


    # Iterate on ready_for_ingest, convert each transaction into a new account situation row
    for index in range(0,len(ready_for_ingest)):
        # Define ready_for_ingest row to add, add a row to asdf
        row_ready_for_ingest = ready_for_ingest.loc[index]


        # If ready_for_ingest row is a transaction, add it to asdf
        if row_ready_for_ingest['Type'] in ['buy', 'sell', 'trade'] :
            if test_if_trade_EURvsUSD(row_ready_for_ingest) :
                print("Transaction EUR vs USD ignoré")
                asdf_last_row = asdf.loc[index].copy()
                asdf_last_row['Type'] = 'trade_between_currency'
                asdf_last_row["Date"] = row_ready_for_ingest["Date"]
                asdf_last_row["Platform"] = row_ready_for_ingest["platform"]
                asdf.loc[index+1] = asdf_last_row
            else : 
                asdf_last_row = asdf.iloc[-1].copy()
                new_row = add_row_to_asdf_from_transaction_row(row_ready_for_ingest, asdf_last_row)
                # print('new_row : ', new_row)
                asdf.loc[index+1] = new_row

    asdf.to_csv(result_filepath, index=False)


ready_for_ingest_filepath = config.FILE_ALL_TRADES
result_filepath = config.FILE_ACCOUNT_SITUATION
main(ready_for_ingest_filepath,result_filepath)
