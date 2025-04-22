import pandas as pd
import numpy as np

from kraken_convert_fct import *


def export_to_excel_for_check(df_ready_to_ingest, checkfile_path):
    # Check with Excel
    # dates_cible = ["2023-12-14 11:03:44", "2024-04-17 21:25:49", "2024-04-17 21:26:17", "2024-03-19 23:48:06"]
    # dates_cible_datetime = [pd.to_datetime(date) for date in dates_cible]

    # filtered_df = df_ready_to_ingest.loc[(df_ready_to_ingest['Sent Currency'] == 'ETH') | (df_ready_to_ingest['Received Currency'] == 'ETH')]
    filtered_df = df_ready_to_ingest.loc[(df_ready_to_ingest['Type'] == 'transfer')]
    # filtered_df = filtered_df.loc[filtered_df['Date'].isin(dates_cible)]

    print(filtered_df)
    filtered_df.to_csv(checkfile_path, sep=',', index=False)
    # filtered_df.to_excel('my_data.xlsx', index=False)


def treat_row(original_df, new_df, row, index, transaction_kind, currency, refid, treated_ref_id, treated_lines):
    if transaction_kind == 'deposit' and  currency not in ['EUR', 'USD']:
        # Il faut modifier chaque ligne deposit directement dans tax.crypto.com pour ajouter le wallet destination
        new_row = Convert_kraken_deposit(row)
        new_df.loc[index] = new_row
        treated_lines["deposit_in_crypto"] += 1
    
    if transaction_kind == 'deposit' and  currency in ['EUR', 'USD']:
        treated_lines["deposit_in_fiat"] += 1

    if transaction_kind == 'withdrawal' and  currency not in ['EUR', 'USD'] :
        # print("transaction_kind : ", transaction_kind)
        new_row = Convert_kraken_withdrawal(row)
        new_df.loc[index] = new_row
        treated_lines["withdrawal_crypto"] += 1

    if  transaction_kind == 'withdrawal' and  currency in ['EUR', 'USD'] :
        treated_lines["withdrawal_eur_ignored"] += 1

    if transaction_kind == 'transfer' :
        treated_lines["transfert_line_ignored"] += 1

    # All buy or send appears in two lines, one for the currency sold and one for the currency bought
    # It's necessary to merge them. The two lines shares the same refid.
    if transaction_kind in ['spend', 'receive'] and refid not in treated_ref_id :
        # Find the two row with refid and create a df with only them
        same_refid_df = original_df.loc[original_df['refid'] == refid]
        # print("before corft")
        # print(same_refid_df)
        new_row = Create_one_row_from_two(same_refid_df)
        new_df.loc[index] = new_row
        treated_ref_id.append(refid)
        treated_lines["send_and_receive"] += 2

    if transaction_kind == 'staking' :
        new_row = Convert_reward_stack_or_other(row)
        new_df.loc[index] = new_row
        # print("new_row")
        # print(new_row)
        treated_lines["staking"] += 1

    if transaction_kind == 'earn' :
        treated_lines["earn_lines_ignored"] += 1

    if transaction_kind == 'trade' and refid not in treated_ref_id :
        # print("-------------------")
        # print(row)
        same_refid_df = original_df.loc[original_df['refid'] == refid]
        new_row = Convert_two_trade_row(same_refid_df)
        new_df.loc[index] = new_row
        treated_lines["trade"] += 2
        treated_ref_id.append(refid)
        # print("-------------------")

    return new_df, treated_ref_id, treated_lines


def main(ledgers_filepath, ready_for_ingest_filepath):
    """
    Cette fonction lis le fichier exporté depuis kraken.com et le met en ordre pour être ingéré par l'app en ligne

    
    """

    # File path
    checkfile_path = 'Data/other/export_for_check.csv'
    depo_width_filepath = 'Data/other/deposit_withdrawal.csv'


    # Import data file and create empty export file (to be filled)
    original_df = pd.read_csv(ledgers_filepath, sep=',')
    new_df = pd.DataFrame(columns=["Date", "Type", "Received Currency",	"Received Amount", "Received Net Worth", "Sent Currency", "Sent Amount", "Sent Net Worth", "Fee Currency", "Fee Amount", "Fee Net Worth"])

    filtered_df = original_df.loc[(original_df['type'] == 'deposit') | (original_df['type'] == 'withdrawal')]
    filtered_df.to_csv(depo_width_filepath, sep=',', index=False)
    

    print("nombre de lignes df original : ", len(original_df))

    treated_ref_id = []
    treated_lines = {
        'transfert_line_ignored' : 0,
        'earn_lines_ignored' : 0,
        'deposit_in_crypto' : 0,
        'deposit_in_fiat' : 0,
        'withdrawal_crypto' : 0,
        'withdrawal_eur_ignored' : 0,
        'send_and_receive' : 0,
        'staking' : 0,
        'trade' : 0
    }

    # Filter only certain dates to test 
    # dates_cible = ["2023-12-14 11:03:44", "2024-04-17 21:25:49", "2024-04-17 21:26:17", "2024-03-19 23:48:06"]
    # original_df = original_df.loc[original_df['time'].isin(dates_cible)]
    # print(original_df.head(10))


    for index in original_df.index:
        # print('index : ', index)
    # for index in range(0,8):

        # Get main datas from the currently observed row
        row = original_df.loc[index]

        transaction_kind = row['type']
        refid = row['refid']
        currency = row['asset']



        new_df, treated_ref_id, treated_lines = treat_row(original_df, new_df, row, index, transaction_kind, currency, refid, treated_ref_id, treated_lines)


    print("lignes traités")
    print(treated_lines)
    print("total : ", sum(treated_lines.values()))
    
    print("taille new df : ", len(new_df))


        
    # ---------- Modify the datetime format of the column 
    # current_date_format = '%d/%m/%Y %H:%M:%S'
    # colonne_dates_formatee = pd.to_datetime(new_df['Date'], format=current_date_format).dt.strftime('%m/%d/%Y %H:%M:%S')
    # new_df['Date'] = colonne_dates_formatee


    # ---------- Convert columns to positive values (because no negative values allowed)
    def format_value(x):
        if pd.isna(x):
            return ""  # Replace NaN with empty string
        else:
            return f"{x:.10f}" 
        
    pd.set_option('display.float_format', '{:.10f}'.format)
    for column_to_modify in ['Received Amount', 'Sent Amount', 'Fee Amount']:
        new_df[column_to_modify] = pd.to_numeric(new_df[column_to_modify], errors='coerce')
        new_df[column_to_modify] = np.abs(new_df[column_to_modify])
        new_df[column_to_modify] = new_df[column_to_modify].apply(format_value)

    print("new df : ", new_df.tail())

    # Export to csv
    new_df.to_csv(ready_for_ingest_filepath, sep=',', index=False)
    export_to_excel_for_check(new_df, checkfile_path)


ledgers_filepath = "Data/0_original_trade_files/kraken_2024.csv"
ready_for_ingest_filepath = 'Data/1_ready_for_ingest/kraken_2024_ready_for_ingest.csv'
main(ledgers_filepath, ready_for_ingest_filepath)

