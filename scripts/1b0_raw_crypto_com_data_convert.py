import pandas as pd
import numpy as np
import openpyxl
import config

dict_transaction_kind_to_type = {
    'crypto_exchange' : 'trade', 
    'crypto_viban_exchange' : 'sell', 
    'crypto_withdrawal' : 'transfer', 
    'dust_conversion_credited' : 'trade', 
    'dust_conversion_debited' : 'trade', 
    'finance.dpos.compound_interest.crypto_wallet' : 'reward', 
    'finance.dpos.non_compound_interest.crypto_wallet' : 'reward', 
    'finance.dpos.staking.crypto_wallet' : 'transfer', 
    'finance.dpos.unstaking.crypto_wallet' : 'transfer', 
    'rewards_platform_deposit_credited' : 'reward', 
    'trading.crypto_purchase.google_pay' : 'buy', 
    'trading.limit_order.fiat_wallet.sell_lock' : 'open a sell order', 
    'trading.limit_order.fiat_wallet.sell_unlock' : 'cancel a sell order', 
    'viban_purchase' : 'buy'
}

def Convert_crypto_exchange(row):
    """
    exchange one currency with another (both crypto or fiat currencies)
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Received Net worth, Sent Net Worth and Fee Net Worth (leave them blank if none)
    """

    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'trade', 
        'Received Currency' : row['To Currency'], 
        'Received Amount' : row['To Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row


def Convert_crypto_viban_exchange(row):
    """
    sell for fiat currencies
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Received Net worth, Sent Net Worth and Fee Net Worth (leave them blank if none)
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'sell', 
        'Received Currency' : row['To Currency'], 
        'Received Amount' : row['To Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row

def Convert_crypto_withdrawal(row):
    """
    Type must be transfer
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Values in Received Currency and Received Amount must match those in Sent Currency and Sent Amount (excluding the fee)
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Fee Net Worth (leave them blank if none)

    Dans crpyto tax, les fees viennent s'aditionner au montant du transfert
    J'ai fais un transfert de 296,95 MATIC, pour cela j'ai payé 0,02 de fees, donc 296,93 envoyé à Kraken

    Quand je mets un transfert de 296,95 MATIC avec 0,02 de fees dans le csv ready to ingest
    Crypto tax comprends que le transfert fait 296,95 + 0,02
    Alors qu'en fait les 0,02 sont compris dans les 296,95
    Il faut donc les enlever au montant du transfert et déclarer à crypto tax un transfert de 296,93
    Comme ça il ajoute les fees et tombe sur le bon montant de transfert soit : 296,95, et il a bien l'info pour les 0,02 fees


    Note : 14/04/2024 I had to add the columns Fee Currency & Fee Amount in the crypto app source dataset
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'transfer', 
        'Received Currency' : row['Currency'], 
        'Received Amount' : row['Amount'] + row['Fee Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'] + row['Fee Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : row['Fee Currency'], 
        'Fee Amount' : row['Fee Amount'], 
        'Fee Net Worth' : ''
    })
    return new_row

def Convert_reward_stack_or_other(row):
    """
    Received Currency and Received Amount must be filled
    Sent Currency and Sent Amount must be empty
    Input the net worth amount in Received Net worth (leave them blank if none)
    There should be no fees associated with any receive transactions, but we advise that you double check the transaction details
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'reward', 
        'Received Currency' : row['Currency'], 
        'Received Amount' : row['Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : '', 
        'Sent Amount' : '' ,
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row
    

def Convert_stake_unstake(row):
    """
    Type must be transfer
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Values in Received Currency and Received Amount must match those in Sent Currency and Sent Amount (excluding the fee)
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Fee Net Worth (leave them blank if none)
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'transfer', 
        'Received Currency' : row['Currency'], 
        'Received Amount' : row['Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row


def Convert_buy(row):
    """
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Received Net worth, Sent Net Worth and Fee Net Worth (leave them blank if none)
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'buy', 
        'Received Currency' : row['To Currency'], 
        'Received Amount' : row['To Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row


def Convert_buy_google_pay(row):
    """
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Received Net worth, Sent Net Worth and Fee Net Worth (leave them blank if none)

    Note : Here, in the source dataset, the columns To curreny and To Amount are empty
    Also, the columns Currency and Amount are filled with the received currency instead of the spent currency
    We can use the values in the columns : 'Native Currency' and 'Native Amount', as 'Curreny' and 'Amount' columns in the new dataset
    """
    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'buy', 
        'Received Currency' : row['Currency'], 
        'Received Amount' : row['Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Native Currency'], 
        'Sent Amount' : row['Native Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row



def Convert_dust_conversion_debited(row):
    """
    exchange one currency with another (both crypto or fiat currencies)
    Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
    Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
    Input the net worth amount in Received Net worth, Sent Net Worth and Fee Net Worth (leave them blank if none)

    Note : I add to rework the source dataset
    Indeed, each conversion is splitted in two lines in the source dataset, I add to merge them
    I chose to keep dust_conversion_debited and remove dust_conversion_credited
    I took the columns values 'Currency' and 'Amount' from dust_conversion_credited and put them in dust_conversion_debited in columns 'To Currency' & 'To Amount'
    """

    new_row = pd.Series({
        'Date' : row['Timestamp (UTC)'], 
        'Type' : 'trade', 
        'Received Currency' : row['To Currency'], 
        'Received Amount' : row['To Amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['Currency'], 
        'Sent Amount' : row['Amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row



def main():
    """
    Cette fonction lis le fichier exporté depuis l'app crypto.com et le met en ordre pour être ingéré par l'app en ligne



    
    """

    # Utilisation de sep=None pour détecter automatiquement virgule ou point-virgule.
    # On nettoie les noms de colonnes (strip) pour supprimer les espaces invisibles.
    print(f"Chargement de la source : {config.FILE_CRYPTOCOM_REWORKED_SOURCE}")
    original_df = pd.read_csv(config.FILE_CRYPTOCOM_REWORKED_SOURCE, sep=None, engine='python')
    original_df.columns = original_df.columns.str.strip()
    original_df = original_df.fillna(0) # Sécurité pour les calculs de montants

    # print(original_df.head())
    new_df = pd.DataFrame(columns=["Date", "Type", "Received Currency",	"Received Amount", "Received Net Worth", "Sent Currency", "Sent Amount", "Sent Net Worth", "Fee Currency", "Fee Amount", "Fee Net Worth"])

    passed = 0
    for index, cryptoapp_row in original_df.iterrows():

        transaction_kind = cryptoapp_row['Transaction Kind']

        if transaction_kind == 'crypto_exchange' :
            new_row = Convert_crypto_exchange(cryptoapp_row)
            new_df.loc[index] = new_row

        if transaction_kind == 'crypto_viban_exchange' :
            new_row = Convert_crypto_viban_exchange(cryptoapp_row)
            new_df.loc[index] = new_row

        if transaction_kind == 'crypto_withdrawal' :
            new_row = Convert_crypto_withdrawal(cryptoapp_row)
            new_df.loc[index] = new_row

        if transaction_kind in ['finance.dpos.compound_interest.crypto_wallet', 'finance.dpos.non_compound_interest.crypto_wallet', 'rewards_platform_deposit_credited']:
            new_row = Convert_reward_stack_or_other(cryptoapp_row)
            new_df.loc[index] = new_row

        if transaction_kind in ['finance.dpos.staking.crypto_wallet', 'finance.dpos.unstaking.crypto_wallet']:
            passed = passed + 1
            pass
            # new_row = Convert_stake_unstake(cryptoapp_row)
            # new_df.loc[index] = new_row
        
        if transaction_kind == 'viban_purchase':
            new_row = Convert_buy(cryptoapp_row)
            new_df.loc[index] = new_row

        if transaction_kind == 'trading.crypto_purchase.google_pay':
            new_row = Convert_buy_google_pay(cryptoapp_row)
            new_df.loc[index] = new_row
        
        if transaction_kind in ['trading.limit_order.fiat_wallet.sell_lock', 'trading.limit_order.fiat_wallet.sell_unlock']:
            passed = passed + 1
            pass

        if transaction_kind == 'dust_conversion_credited':
            passed = passed + 1
            pass

        if transaction_kind == 'dust_conversion_debited':
            new_row = Convert_dust_conversion_debited(cryptoapp_row)
            new_df.loc[index] = new_row
            


        
    # Modify the datetime format of the column 
    current_date_format = '%d/%m/%Y %H:%M:%S'
    colonne_dates_formatee = pd.to_datetime(new_df['Date'], format=current_date_format).dt.strftime('%m/%d/%Y %H:%M:%S')
    new_df['Date'] = colonne_dates_formatee


    # Convert columns to positive values (because no negative values allowed)
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



    # Export to csv
    new_df.to_csv(config.FILE_CRYPTOCOM_RFI_V2, sep=',', index=False)


    # Print the total of buy
    # filtered_df = new_df.loc[new_df['Sent Currency'] == 'ETH']
    filtered_df = new_df.loc[(new_df['Sent Currency'] == 'BTC') | (new_df['Received Currency'] == 'BTC')]
    # filtered_df = new_df.loc[new_df['Type'] == 'transfer']
    print(filtered_df)
    filtered_df.to_excel('my_data.xlsx', index=False)
    # total_amount = filtered_df['Sent Amount'].sum()

    # print("Total amount of 'buy' transactions:", total_amount)


main()