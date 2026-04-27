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

    if pd.notna(rec_curr) and rec_curr != '' and row_ready_for_ingest['Detected Type'] != 'transfer' :
        new_row = add_amount_to_curreny_in_row(new_row, rec_curr, rec_amount)
    
    if pd.notna(sent_curr) and sent_curr != '' and row_ready_for_ingest['Detected Type'] != 'transfer':
        new_row = remove_amount_to_currency_in_row(new_row, sent_curr, sent_amount)

    if pd.notna(fee_curr) and fee_curr != '' and Decimal(str(fee_amount)) != 0:
        new_row = remove_fee_from_currency_in_row(new_row, fee_curr, fee_amount)

    new_row["Date"] = row_ready_for_ingest["Date"]
    new_row["Platform"] = row_ready_for_ingest["platform"]
    new_row["refid"] = row_ready_for_ingest["refid"]
    new_row["subtype"] = row_ready_for_ingest["subtype"]
    new_row["Type"] = row_ready_for_ingest["Type"]
    new_row["Detected Type"] = row_ready_for_ingest['Detected Type']

    return new_row


# --- MAIN ---

ready_for_ingest = pd.read_csv(config.FILE_ALL_TRADES_NORMALIZED, dtype=str)

# Création des colonnes UNIQUEMENT avec les noms mappés (BTC, ETH, etc.)
all_currencies_raw = set(ready_for_ingest["Received Currency"].dropna()) | \
                     set(ready_for_ingest["Sent Currency"].dropna()) | \
                     set(ready_for_ingest["Fee Currency"].dropna())

all_currencies_mapped = set([get_mapped_currency(c) for c in all_currencies_raw if c != ""])

asdf = pd.DataFrame(columns=list(ready_for_ingest.columns) + list(all_currencies_mapped))

# Initialisation ligne 0
init_row = {col: "" for col in asdf.columns}
for curr in all_currencies_mapped:
    init_row[curr] = Decimal('0')
asdf.loc[0] = init_row


# Iterate over rfi
for index, row in ready_for_ingest.iterrows():
    row_ready_for_ingest = ready_for_ingest.loc[index]

    if row_ready_for_ingest['Detected Type'] in ['buy', 'sell', 'trade','transfer'] :
        if test_if_trade_EURvsUSD(row_ready_for_ingest) :
            asdf_last_row = asdf.iloc[-1].copy()
            asdf_last_row['Detected Type'] = 'trade_between_currency'
            asdf_last_row["Date"] = row_ready_for_ingest["Date"]
            asdf_last_row["Platform"] = row_ready_for_ingest["platform"]
            asdf_last_row["refid"] = row_ready_for_ingest["refid"]
            asdf_last_row["subtype"] = row_ready_for_ingest["subtype"]
            asdf_last_row["Type"] = row_ready_for_ingest["Type"]
            asdf.loc[len(asdf)] = asdf_last_row
        else : 
            asdf_last_row = asdf.iloc[-1].copy()
            new_row = add_row_to_asdf_from_transaction_row(row_ready_for_ingest, asdf_last_row)
            asdf.loc[len(asdf)] = new_row

asdf.to_csv(config.FILE_ACCOUNT_SITUATION, index=False)
module_global.show_holdings()