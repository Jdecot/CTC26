import pandas as pd
import config
from module_1a import *


def treat_row_v2(ledger_df, row):
    transaction_kind = row['type']
    refid = row['refid']
    currency = row['asset']
    new_rows = []
    global treated_lines, treated_ref_id

    if transaction_kind == 'deposit' and  currency not in ['EUR', 'USD']:
        new_rows.append(Convert_kraken_deposit(row).to_dict())
        treated_lines["deposit_in_crypto"] += 1
    
    elif transaction_kind == 'deposit' and  currency in ['EUR', 'USD']:
        treated_lines["deposit_in_fiat"] += 1

    elif transaction_kind == 'withdrawal' and  currency not in ['EUR', 'USD'] :
        new_rows.append(Convert_kraken_withdrawal(row).to_dict())
        treated_lines["withdrawal_crypto"] += 1

    elif  transaction_kind == 'withdrawal' and  currency in ['EUR', 'USD'] :
        treated_lines["withdrawal_eur_ignored"] += 1

    elif transaction_kind == 'transfer' :
        treated_lines["transfert_line_ignored"] += 1
        if float(row['fee']) > 0 : # fl
            print("Transfer - corriger : fee supérieur à 0 pas prise en compte : ",  row)

    # All buy or send appears in two lines, one for the currency sold and one for the currency bought
    # It's necessary to merge them. The two lines shares the same refid.
    elif transaction_kind in ['spend', 'receive'] and refid not in treated_ref_id and row['subtype'] != 'dustsweeping':
        # Find the two row with refid and create a df with only them
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        new_rows.append(Create_one_row_from_two(same_refid_df))
        treated_ref_id.append(refid)
        treated_lines["send_and_receive"] += 1

    elif transaction_kind in ['spend', 'receive'] and refid in treated_ref_id and row['subtype'] != 'dustsweeping':
        treated_lines["send_and_receive"] += 1

    elif row['subtype'] == 'dustsweeping' :
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        if refid not in treated_ref_id :
            new_rows.extend(Convert_dustsweeping_into_several_rows(same_refid_df))
            treated_ref_id.append(refid)
        treated_lines["dustsweeping"] += 1

    elif transaction_kind == 'staking' :
        new_rows.append(Convert_reward_stack_or_other(row).to_dict())
        treated_lines["staking"] += 1

    elif transaction_kind == 'trade' and refid not in treated_ref_id :
        same_refid_df = ledger_df.loc[ledger_df['refid'] == refid]
        new_rows.append(Convert_two_trade_row(same_refid_df))
        treated_lines["trade"] += 1
        treated_ref_id.append(refid)

    elif transaction_kind == 'trade' and refid in treated_ref_id :
        treated_lines["trade"] += 1

    else:
        # Ligne déjà traitée (refid déjà dans treated_ref_id) ou type non géré
        if refid in treated_ref_id:
            pass  # Déjà comptabilisé lors du premier traitement
        else:
            treated_lines["unprocessed_lines"] += 1
            print(f"Ligne non traitée : type={transaction_kind}, refid={refid}, asset={currency}")

    return new_rows


def export_deposit_withdraw_csv(df):
    depo_width_filepath = config.FILE_DEPOSIT_WITHDRAWAL
    filtered_df = df.loc[(df['type'] == 'deposit') | (df['type'] == 'withdrawal')]
    filtered_df.to_csv(depo_width_filepath, sep=',', index=False)


# def convert_columns_to_positive_values(df, cols_to_modify):
#     """
#     Convertit les colonnes spécifiées en valeurs positives.
#     Affiche les détails en cas d'erreur de conversion.
#     """
#     for column in cols_to_modify:
#         if column in df.columns:
#             # On utilise une boucle plus classique pour accéder facilement à l'index et aux autres colonnes
#             for index, row in df.iterrows():
#                 val = row[column]
                
#                 # On ignore les valeurs déjà vides
#                 if pd.isna(val) or str(val).strip() == "":
#                     continue
                
#                 try:
#                     # Tentative de conversion
#                     df.at[index, column] = abs(Decimal(str(val)))
#                 except Exception:
#                     # Affichage des détails si ça plante
#                     date_val = row.get('Date', 'N/A')
#                     print(f"⚠️ Erreur de conversion !")
#                     print(f"   - Colonne : {column}")
#                     print(f"   - Index   : {index}")
#                     print(f"   - Date    : {date_val}")
#                     print(f"   - Valeur  : '{val}'")
#                     print(f"-------------------------")
#                     # On laisse la valeur telle quelle pour ne pas bloquer le script
    
#     return df


def convert_ledger_to_rfi(ledger_df):
    """
    Cette fonction lis le fichier exporté depuis kraken.com et le met en ordre pour être ingéré par l'app en ligne
    """
        
    rfi_df = pd.DataFrame(columns=[
        "Date", "refid", "Detected Type", "Type", "subtype",
        "Received Currency", "Received Amount", "Received Net Worth", 
        "Sent Currency", "Sent Amount", "Sent Net Worth", 
        "Fee Currency", "Fee Amount", "Fee Net Worth"
    ])
    
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
    
    # Loop, treat each ledger row and add result to RFI
    for index in ledger_df.index:
        row = ledger_df.loc[index]
        processed_rows = treat_row_v2(ledger_df, row)
        for row_data in processed_rows:
            rfi_df.loc[len(rfi_df)] = row_data


    print("lignes traités : ", treated_lines)
    print("total lignes traités : ", sum(treated_lines.values()))
    print("taille new df : ", len(rfi_df))



    return rfi_df


def improve_rfi_quality(rfi_df):
    # rfi_df = convert_columns_to_positive_values(rfi_df.copy(), [])
    # Plus besoin de convertir les colonnes en positif, on gère les signes naturellement

    # Convert timestamp to datetime format if Date column contains numeric timestamps
    if 'Date' in rfi_df.columns:
            # On repasse en numérique le temps d'une seconde pour que Pandas comprenne le timestamp
            rfi_df['Date'] = pd.to_datetime(pd.to_numeric(rfi_df['Date'], errors='coerce'), unit='s')
            
            # Formatage final en texte propre pour le CSV
            rfi_df['Date'] = rfi_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return rfi_df


def main():


    print(f"----------- kraken_all_trades ------------")
    ledger_filepath = config.DIR_0_ORIGINAL / f"kraken_all_trades.csv"
    ready_for_ingest_filepath = config.DIR_1_RFI / f'kraken_all_trades_ready_for_ingest.csv'
    ledger_df = pd.read_csv(ledger_filepath, sep=',', dtype=str)
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