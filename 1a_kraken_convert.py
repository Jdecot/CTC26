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

    filtered_df.to_csv(checkfile_path, sep=',', index=False)
    # filtered_df.to_excel('my_data.xlsx', index=False)


def treat_row_v2(ledger_df, row):
    transaction_kind = row['type']
    refid = row['refid']
    currency = row['asset']
    new_row = None
    global treated_lines, treated_ref_id

    if transaction_kind == 'deposit' and  currency not in ['EUR', 'USD']:
        # Il faut modifier chaque ligne deposit directement dans tax.crypto.com pour ajouter le wallet destination
        new_row = Convert_kraken_deposit(row)
        treated_lines["deposit_in_crypto"] += 1
    
    if transaction_kind == 'deposit' and  currency in ['EUR', 'USD']:
        treated_lines["deposit_in_fiat"] += 1

    if transaction_kind == 'withdrawal' and  currency not in ['EUR', 'USD'] :
        # print("transaction_kind : ", transaction_kind)
        new_row = Convert_kraken_withdrawal(row)
        treated_lines["withdrawal_crypto"] += 1

    if  transaction_kind == 'withdrawal' and  currency in ['EUR', 'USD'] :
        treated_lines["withdrawal_eur_ignored"] += 1

    if transaction_kind == 'transfer' :
        treated_lines["transfert_line_ignored"] += 1

    # All buy or send appears in two lines, one for the currency sold and one for the currency bought
    # It's necessary to merge them. The two lines shares the same refid.
    if transaction_kind in ['spend', 'receive'] and refid not in treated_ref_id :
        # Find the two row with refid and create a df with only them
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        new_row = Create_one_row_from_two(same_refid_df)
        treated_ref_id.append(refid)
        treated_lines["send_and_receive"] += 2

    if transaction_kind == 'staking' :
        new_row = Convert_reward_stack_or_other(row)
        treated_lines["staking"] += 1

    if transaction_kind == 'earn' :
        treated_lines["earn_lines_ignored"] += 1

    if transaction_kind == 'trade' and refid not in treated_ref_id :

        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        new_row = Convert_two_trade_row(same_refid_df)
        treated_lines["trade"] += 2
        treated_ref_id.append(refid)

    return new_row


def export_deposit_withdraw_csv(df):
    depo_width_filepath = 'Data/other/deposit_withdrawal.csv'
    filtered_df = df.loc[(df['type'] == 'deposit') | (df['type'] == 'withdrawal')]
    filtered_df.to_csv(depo_width_filepath, sep=',', index=False)


def filter_on_specifiq_dates(ledger_df): 
    # Filter only certain dates to test 
    dates_cible = ["2023-12-14 11:03:44", "2024-04-17 21:25:49", "2024-04-17 21:26:17", "2024-03-19 23:48:06"]
    ledger_df = ledger_df.loc[ledger_df['time'].isin(dates_cible)]
    return ledger_df


def convert_columns_to_positive_values(df, cols_to_modify):
    # ---------- Convert columns to positive values (because no negative values allowed)

    # Convert to float 
    def format_value(x):
        if pd.isna(x):
            return ""  # Replace NaN with empty string
        else:
            return f"{x:.10f}" 
        
    pd.set_option('display.float_format', '{:.10f}'.format)
    for column_to_modify in cols_to_modify :
        df[column_to_modify] = pd.to_numeric(df[column_to_modify], errors='coerce')
        df[column_to_modify] = np.abs(df[column_to_modify])
        df[column_to_modify] = df[column_to_modify].apply(format_value)
    
    return df


def convert_ledger_to_rfi(ledger_df):
    """
    Cette fonction lis le fichier exporté depuis kraken.com et le met en ordre pour être ingéré par l'app en ligne
    """
        
    rfi_df = pd.DataFrame(columns=["Date", "Type", "Received Currency",	"Received Amount", "Received Net Worth", "Sent Currency", "Sent Amount", "Sent Net Worth", "Fee Currency", "Fee Amount", "Fee Net Worth"])
    
    export_deposit_withdraw_csv(ledger_df)

    global treated_ref_id
    treated_ref_id = []
    global treated_lines
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

    print(f"nombre de lignes dans ledger : {len(ledger_df)}")
    filtered_df = filter_on_specifiq_dates(ledger_df)

    
    # Loop, treat each ledger row and add result to RFI
    for index in ledger_df.index:
        row = ledger_df.loc[index]
        # rfi_df, treated_ref_id, treated_lines = treat_row(ledger_df, rfi_df, row, index, treated_ref_id, treated_lines)
        new_row = treat_row_v2(ledger_df, row)
        if new_row is not None : rfi_df.loc[index] = new_row

    print("lignes traités : ", treated_lines)
    print("total : ", sum(treated_lines.values()))
    print("taille new df : ", len(rfi_df))

    rfi_df = convert_columns_to_positive_values(rfi_df.copy(), ['Received Amount', 'Sent Amount', 'Fee Amount'])

    return rfi_df


def main():

    ledger_filename = [
        "kraken_2023",
        "kraken_2024",
        "kraken_2025"
    ]

    for ledger_filename in ledger_filename : 
        print(f"----------- {ledger_filename} ------------")
        ledger_filepath = f"{"Data/0_original_trade_files"}/{ledger_filename}.csv"
        ready_for_ingest_filepath = f'Data/1_ready_for_ingest/{ledger_filename}_ready_for_ingest.csv'
        ledger_df = pd.read_csv(ledger_filepath, sep=',')
        rfi_df = convert_ledger_to_rfi(ledger_df)

        # Export to csv
        rfi_df.to_csv(ready_for_ingest_filepath, sep=',', index=False)
        export_to_excel_for_check(rfi_df, f'Data/other/export_for_check_{ledger_filename}.csv')


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
main()

