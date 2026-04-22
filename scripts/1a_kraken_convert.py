import pandas as pd
import numpy as np
import config
from module_1a import *


def treat_row_v2(ledger_df, row):
    transaction_kind = row['type']
    refid = row['refid']
    currency = row['asset']
    new_row = None
    global treated_lines, treated_ref_id

    # print(f"***********  treat row : {row} ***************")
    if transaction_kind == 'deposit' and  currency not in ['EUR', 'USD']:
        # Il faut modifier chaque ligne deposit directement dans tax.crypto.com pour ajouter le wallet destination
        new_row = Convert_kraken_deposit(row)
        treated_lines["deposit_in_crypto"] += 1
        # print("Treated as deposit in crypto")
    
    elif transaction_kind == 'deposit' and  currency in ['EUR', 'USD']:
        treated_lines["deposit_in_fiat"] += 1
        # print("Treated as deposit in currency")

    elif transaction_kind == 'withdrawal' and  currency not in ['EUR', 'USD'] :
        # print("transaction_kind : ", transaction_kind)
        new_row = Convert_kraken_withdrawal(row)
        treated_lines["withdrawal_crypto"] += 1
        # print("Treated as withdrawal in crypto")

    elif  transaction_kind == 'withdrawal' and  currency in ['EUR', 'USD'] :
        treated_lines["withdrawal_eur_ignored"] += 1
        # print("Treated as withdrawal in currency")

    elif transaction_kind == 'transfer' :
        treated_lines["transfert_line_ignored"] += 1
        if row['fee'] > 0 :
            print("Transfer - corriger : fee supérieur à 0 pas prise en compte : ",  row)

    # All buy or send appears in two lines, one for the currency sold and one for the currency bought
    # It's necessary to merge them. The two lines shares the same refid.
    elif transaction_kind in ['spend', 'receive'] and refid not in treated_ref_id and row['subtype'] != 'dustsweeping':
        # Find the two row with refid and create a df with only them
        # print("************ Row spend and receive ************")
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        new_row = Create_one_row_from_two(same_refid_df)
        treated_ref_id.append(refid)
        treated_lines["send_and_receive"] += 1
        # print(f"******* date : {new_row['Date']} *************")
        # print(f"{new_row['Type']} : reçu {new_row['Received Amount']} {new_row['Received Currency']}, sent {new_row['Sent Amount']} {new_row['Sent Currency']} ")
        # print(f"Frais de transaction : {new_row['Fee Amount']} {new_row['Fee Currency']} ")
        # print("Treated as spend receive")

    elif transaction_kind in ['spend', 'receive'] and refid in treated_ref_id and row['subtype'] != 'dustsweeping':
        treated_lines["send_and_receive"] += 1

    elif row['subtype'] == 'dustsweeping' :
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        # print("dustsweeping same ref if : ", len(same_refid_df))
        if refid not in treated_ref_id :
            # new_rows = Convert_dustsweeping_into_several_rows(same_refid_df)
            treated_ref_id.append(refid)
        treated_lines["dustsweeping"] += 1

    elif transaction_kind == 'staking' :
        new_row = Convert_reward_stack_or_other(row)
        treated_lines["staking"] += 1
        # print("Treated as staking")

    elif transaction_kind == 'trade' and refid not in treated_ref_id :
        # print("************ Row trade ************")
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        # print(same_refid_df)
        new_row = Convert_two_trade_row(same_refid_df)
        treated_lines["trade"] += 1
        treated_ref_id.append(refid)
        # print(f"new row : {new_row['Date']}")

    elif transaction_kind == 'trade' and refid in treated_ref_id :
        treated_lines["trade"] += 1

    else:
        # Ligne déjà traitée (refid déjà dans treated_ref_id) ou type non géré
        if refid in treated_ref_id:
            pass  # Déjà comptabilisé lors du premier traitement
        else:
            treated_lines["unprocessed_lines"] += 1
            print(f"Ligne non traitée : type={transaction_kind}, refid={refid}, asset={currency}")

    return new_row


def export_deposit_withdraw_csv(df):
    depo_width_filepath = config.FILE_DEPOSIT_WITHDRAWAL
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
        'deposit_in_crypto' : 0,
        'deposit_in_fiat' : 0,
        'withdrawal_crypto' : 0,
        'withdrawal_eur_ignored' : 0,
        'send_and_receive' : 0,
        'staking' : 0,
        'trade' : 0,
        'dustsweeping' : 0,
        'unprocessed_lines' : 0
    }

    print(f"nombre de lignes dans ledger : {len(ledger_df)}")
    filtered_df = filter_on_specifiq_dates(ledger_df)

    
    # Loop, treat each ledger row and add result to RFI
    for index in ledger_df.index:
        row = ledger_df.loc[index]
        # rfi_df, treated_ref_id, treated_lines = treat_row(ledger_df, rfi_df, row, index, treated_ref_id, treated_lines)
        new_rows = treat_row_v2(ledger_df, row)
        if new_rows is not None:
            if isinstance(new_rows, list):
                # Si treat_row_v2 renvoie une liste de lignes, on les ajoute toutes
                for row_data in new_rows:
                    rfi_df.loc[len(rfi_df)] = row_data
            else:
                # Si treat_row_v2 renvoie une seule ligne (dict/Series)
                rfi_df.loc[len(rfi_df)] = new_rows


    print("lignes traités : ", treated_lines)
    print("total lignes traités : ", sum(treated_lines.values()))
    print("taille new df : ", len(rfi_df))



    return rfi_df


def improve_rfi_quality(rfi_df):
    rfi_df = convert_columns_to_positive_values(rfi_df.copy(), ['Received Amount', 'Sent Amount', 'Fee Amount'])

    # Convert timestamp to datetime format if Date column contains numeric timestamps
    if 'Date' in rfi_df.columns:
        rfi_df['Date'] = pd.to_datetime(rfi_df['Date'], errors='coerce', unit='s')
        # Format as string for CSV export
        rfi_df['Date'] = rfi_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return rfi_df


def main():

    ledger_filename = [
        "kraken_all_trades",
    ]

    for ledger_filename in ledger_filename : 
        print(f"----------- {ledger_filename} ------------")
        ledger_filepath = config.DIR_0_ORIGINAL / f"{ledger_filename}.csv"
        ready_for_ingest_filepath = config.DIR_1_RFI / f'{ledger_filename}_ready_for_ingest.csv'
        ledger_df = pd.read_csv(ledger_filepath, sep=',')
        rfi_df = convert_ledger_to_rfi(ledger_df)
        rfi_df = improve_rfi_quality(rfi_df)

        # Export to csv
        rfi_df.to_csv(ready_for_ingest_filepath, sep=',', index=False)


treated_ref_id = []
treated_lines = {
    'transfert_line_ignored' : 0,
    'deposit_in_crypto' : 0,
    'deposit_in_fiat' : 0,
    'withdrawal_crypto' : 0,
    'withdrawal_eur_ignored' : 0,
    'send_and_receive' : 0,
    'staking' : 0,
    'trade' : 0,
    'dustsweeping' : 0,
    'unprocessed_lines' : 0
}
main()