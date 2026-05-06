import pandas as pd
import module_global
import config

from decimal import Decimal, getcontext
getcontext().prec = 50 

def get_mapped_currency(currency):
    """Utilise ton dictionnaire de config pour unifier les noms (ex: XXBT -> BTC)"""
    if pd.isna(currency) or currency == "":
        return ""
    return config.KRAKEN_CRYPTO_ID.get(currency, currency)

def test_if_trade_EURvsUSD(row):
    # On utilise les versions mappées pour le test
    rec_mapped = get_mapped_currency(row["Received Currency"])
    sent_mapped = get_mapped_currency(row["Sent Currency"])
    
    received_eur_usd = rec_mapped in ['EUR', 'USD']
    sent_eur_usd = sent_mapped in ['EUR', 'USD']

    return received_eur_usd and sent_eur_usd


def add_amount_to_curreny_in_row(row, currency, amount_to_add):
    curr = get_mapped_currency(currency) # ON MAPPE ICI
    current_ammount = Decimal(str(row[curr]))
    new_amount = current_ammount + Decimal(str(amount_to_add))
    row[curr] = new_amount
    return row

def remove_amount_to_currency_in_row(row, currency, amount_to_remove):
    curr = get_mapped_currency(currency) # ON MAPPE ICI
    current_ammount = Decimal(str(row[curr]))
    
    # En soustrayant la valeur absolue, on gère à la fois les montants positifs (CRO) 
    # et négatifs (Kraken) pour garantir une diminution du solde.
    row[curr] = current_ammount - abs(Decimal(str(amount_to_remove)))
    return row


def remove_fee_from_currency_in_row(row, currency, amount_to_remove):
    curr = get_mapped_currency(currency) # ON MAPPE ICI
    current_ammount = Decimal(str(row[curr]))
    new_amount = current_ammount - Decimal(str(amount_to_remove))
    row[curr] = new_amount
    return row


def add_row_to_asdf_from_transaction_row(row_ready_for_ingest, asdf_last_row):

    new_row = asdf_last_row.copy()

    rec_amount = row_ready_for_ingest["Received Amount"]
    sent_amount = row_ready_for_ingest["Sent Amount"]
    fee_amount = row_ready_for_ingest["Fee Amount"]
    
    rec_curr = row_ready_for_ingest["Received Currency"]
    sent_curr = row_ready_for_ingest["Sent Currency"]
    fee_curr = row_ready_for_ingest["Fee Currency"]

    if pd.notna(rec_curr) and rec_curr != '' and row_ready_for_ingest['Detected Type'] :
        new_row = add_amount_to_curreny_in_row(new_row, rec_curr, rec_amount)
    
    if pd.notna(sent_curr) and sent_curr != '' and row_ready_for_ingest['Detected Type'] :
        new_row = remove_amount_to_currency_in_row(new_row, sent_curr, sent_amount)

    if pd.notna(fee_curr) and fee_curr != '' and Decimal(str(fee_amount)) != 0:
        new_row = remove_fee_from_currency_in_row(new_row, fee_curr, fee_amount)

    # Recopie de toutes les colonnes de détails de la transaction (Metadata + Amounts + Balance)
    for col in row_ready_for_ingest.index:
        new_row[col] = row_ready_for_ingest[col]

    return new_row


# --- MAIN ---

ready_for_ingest = pd.read_csv(config.FILE_ALL_TRADES_NORMALIZED, dtype=str)

# Création des colonnes UNIQUEMENT avec les noms mappés (BTC, ETH, etc.)
all_currencies_raw = set(ready_for_ingest["Received Currency"].dropna()) | \
                     set(ready_for_ingest["Sent Currency"].dropna()) | \
                     set(ready_for_ingest["Fee Currency"].dropna())

all_currencies_mapped = set([get_mapped_currency(c) for c in all_currencies_raw if c != ""])

# Ensure 'Balance' column is included in asdf, along with other RFI columns and mapped currencies
asdf_columns = list(ready_for_ingest.columns) + list(all_currencies_mapped)
asdf = pd.DataFrame(columns=asdf_columns)

# Initialisation ligne 0
init_row = {col: "" for col in asdf.columns}
for curr in all_currencies_mapped:
    init_row[curr] = Decimal('0')
asdf.loc[0] = init_row


# Iterate over rfi
for index, row in ready_for_ingest.iterrows():
    row_ready_for_ingest = ready_for_ingest.loc[index]

    if row_ready_for_ingest['Detected Type'] in ['buy', 'sell', 'trade', 'fiat_to_fiat', 'transfer', 'reward', 'deposit', 'withdrawal', 'delisting', 'migration-fusion', 'transfer-staking', 'autoallocation']:
        if test_if_trade_EURvsUSD(row_ready_for_ingest) :
            asdf_last_row = asdf.iloc[-1].copy()
            # On recopie les détails même pour les échanges FIAT/FIAT
            for col in row_ready_for_ingest.index:
                asdf_last_row[col] = row_ready_for_ingest[col]
            asdf_last_row['Detected Type'] = 'trade_between_currency'
        else : 
            asdf_last_row = asdf.iloc[-1].copy()
            new_row = add_row_to_asdf_from_transaction_row(row_ready_for_ingest, asdf_last_row)
            asdf.loc[len(asdf)] = new_row

# Réorganisation des colonnes
asdf = module_global.reorder_columns(asdf)

# Suppression des colonnes Net Worth (plus nécessaires à partir de cette étape)
cols_to_drop = ["Sent Net Worth", "Received Net Worth", "Fee Net Worth"]
asdf = asdf.drop(columns=[c for c in cols_to_drop if c in asdf.columns])

asdf.to_csv(config.FILE_ACCOUNT_SITUATION, index=False)
module_global.show_holdings()