import pandas as pd


def Identify_transaction_type(sent_row, receive_row):
    """
    Fonction pour définir le type de transaction en fonction des actifs envoyés et reçus.

    Args:
    sent_row: Une ligne du DataFrame contenant les informations sur l'actif envoyé.
    receive_row: Une ligne du DataFrame contenant les informations sur l'actif reçu.

    Returns:
    Le type de transaction ("trade", "buy" ou "sell").
    """

    sent_row_asset = sent_row['asset']
    receive_row_asset = receive_row['asset']

    if (sent_row_asset != 'EUR') & (receive_row_asset != 'EUR'):
        transaction_type = 'trade'
    elif (sent_row_asset == 'EUR') & (receive_row_asset != 'EUR'):
        transaction_type = 'buy'
    elif (sent_row_asset != 'EUR') & (receive_row_asset == 'EUR'):
        transaction_type = 'sell'
    else:
    # Lever une exception si aucune des conditions n'est remplie
        raise ValueError("Impossible de définir le type de transaction. Valeurs d'actifs non valides.")

    return transaction_type


def Identify_fees(sent_row, receive_row) :
    """
    Cette fonction reçoit deux lignes correspondant à une même transaction (elles partagent le même refid)
    Une seule de ces deux lignes a payé des fees (soit au moment de l'envoi, soit de la reception)
    La fonction identifie laquelle des deux lignes a payé les fees et renvoi les infos sur ces fees
    Si les deux lignes ont payé des fees ce n'est pas normal (à priori)
    """
    # Identify the fee amount of each provided row
    sent_row_fee = sent_row['fee']
    receive_row_fee = receive_row['fee']

    # Raise error if both row have paid fees
    if (sent_row_fee != 0) & (receive_row_fee != 0) :
       raise ValueError("Deux lignes ayant le même refid ont des fees (wtf ?), attention modifier le code")


    # Define fees data that will be returned, empty by default
    # We include the row which pays the fees
    fees_dict = {
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : '',
        'Fee Row' : ''
    }

    # Define fees amount according to the row that paid fees
    if sent_row_fee != 0 :
        fees_dict['Fee Currency'] = sent_row['asset']
        fees_dict['Fee Amount'] = abs(sent_row['fee'])
        fees_dict['Fee Row'] = 'sent_row'
    if receive_row_fee != 0 :
        fees_dict['Fee Currency'] = receive_row['asset']
        fees_dict['Fee Amount'] = abs(receive_row['fee'])
        fees_dict['Fee Row'] = 'receive_row'
     
    return fees_dict


def Compute_amounts_according_fees(sent_row, receive_row, fees_data, transaction_type):
    """
    To correspond to kraken we have to : 

    Achat en euros, fees en crypto : Enlever les fees au received amount, si c'est la ligne receive qui paye les fees
    Achat en euros, fees en euros : Ajouter les fees au sent amount, si c'est la ligne sent qui paye les fees

    Trade crypto vers crypto : Ajouter les fees au sent amount, si c'est la ligne sent qui paye les fees

    Vente en euros, fees en euros : Enlever les fees au received amount, si c'est la ligne receive qui paye les fees
    """

    # Case when buy crypto, fees in crypto, remove fees from received amount (fees has been convert to positive value) to get total received amount
    if (transaction_type == 'buy') & (fees_data['Fee Currency'] != 'EUR') & (fees_data['Fee Row'] == 'receive_row'):
        receive_row['amount'] += fees_data['Fee Amount']

    # Case when buy crypto, fees in euros, add fees to sent amount (fees has been convert to positive value) to get total sent amount
    elif (transaction_type == 'buy') & (fees_data['Fee Currency'] == 'EUR') & (fees_data['Fee Row'] == 'sent_row'):
        sent_row['amount'] += fees_data['Fee Amount']

    # Case when sell crypto, fees in euros, remove fees from received amount (fees has been convert to positive value) to get total received amount
    elif (transaction_type == 'sell') & (fees_data['Fee Currency'] == 'EUR') & (fees_data['Fee Row'] == 'receive_row') :
        pass

    # Case when trade crypto for another one, fees in the sent row, add fees to sent amount to get total amount sent
    elif (transaction_type == 'trade') & (fees_data['Fee Row'] == 'sent_row') :
        sent_row['amount'] += fees_data['Fee Amount']
    
    # Case when trade crypto for another one, fees in the receive row, remove fees from received amount to get total amount received
    elif (transaction_type == 'trade') & (fees_data['Fee Row'] == 'receive_row') :
        receive_row['amount'] += fees_data['Fee Amount']


    else : 
        print("error sent row : ", sent_row)
        print("error receive_row : ", receive_row)
        print("error fees_data : ", fees_data)
        print("error transaction_type : ", transaction_type)
        raise ValueError("Nous n'avons pas pu identifier qui paye les fees")
    
    return sent_row, receive_row


def Create_one_row_from_two(same_refid_df) :
    """
    Only two row in the provided df, we are going to merge them as a new_row
    """

    sent_row = same_refid_df.loc[same_refid_df['type'] == 'spend'].to_dict(orient='records')[0]
    receive_row = same_refid_df.loc[same_refid_df['type'] == 'receive'].to_dict(orient='records')[0]

    # # Identify transaction type
    transaction_type = Identify_transaction_type(sent_row, receive_row)


    fees_data = Identify_fees(sent_row, receive_row)
    sent_row, receive_row = Compute_amounts_according_fees(sent_row, receive_row, fees_data, transaction_type)



    new_row = {
        'Date' : sent_row['time'], 
        'Type' : transaction_type, 
        'Received Currency' : receive_row['asset'], 
        'Received Amount' : receive_row['amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : sent_row['asset'], 
        'Sent Amount' : sent_row['amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : fees_data['Fee Currency'], 
        'Fee Amount' : fees_data['Fee Amount'], 
        'Fee Net Worth' : fees_data['Fee Net Worth']
    }

    return new_row


def Convert_two_trade_row(same_refid_df):

    for index, row in same_refid_df.iterrows() : 
        # Convert negative amount value to positive and set type as spend
        if row["amount"] < 0:
            same_refid_df.at[index, "type"] = 'spend'
        elif row["amount"] > 0:
            same_refid_df.at[index, "type"] = 'receive'
        else : 
            raise ValueError("Une transaction ne peut pas avoir un amount de 0")

    new_row = Create_one_row_from_two(same_refid_df)

    return new_row


def Convert_reward_stack_or_other(row):
    """
    Received Currency and Received Amount must be filled
    Sent Currency and Sent Amount must be empty
    Input the net worth amount in Received Net worth (leave them blank if none)
    There should be no fees associated with any receive transactions, but we advise that you double check the transaction details
    """

    convert_asset_dict = {
    'ADA.S' : 'ADA',
    'ADA' : 'ADA',
    'MATIC04.S' : 'MATIC',
    'MATIC.S' : 'MATIC',
    'MATIC' : 'MATIC',
    'SOL03.S' : 'SOL',
    'SOL.S' : 'SOL',
    'SOL' : 'SOL',
    # Crypto-monnaies principales
    "XXBT": "BTC",
    "XXRP": "XRP",
    "XETH": "ETH",
    "XXDG": "DOGE",
    # Variantes de staking (B=bonded, F=flexible) → currency de base
    "XXBT.B": "BTC",
    "XXBT.F": "BTC",
    "XETH.B": "ETH",
    "XETH.F": "ETH",
    # Fiats
    "ZEUR": "EUR",
    "ZUSD": "USD",
    # Margin
    "XBT.M": "BTC",
    # Variantes numérotées (staking ancien/nouveau)
    "SOL03": "SOL",
    "MATIC04": "MATIC",
    # ETH2 staking (avant et après le merge)
    "ETH2": "ETH",
    "ETH2.S": "ETH",
    "TRX":"TRX",
    "INJ.F": "INJ",
    "SOL.F": "SOL",
    'TRX.F': 'TRX',
    'ADA.F': 'ADA',
    'EIGEN': 'EIGEN',
    'USDC' : 'USDC',
    'USDC.F' : 'USDC',
    'USDC.M' : 'USDC',
    'USDT.F': 'USDT',
    'INJ' : 'INJ',
    'INJ.B' : 'INJ'
    }

    # Compute the real value received, fee is a negative value so we add
    value_received_minus_fees = row['amount'] + row['fee']
    asset =  convert_asset_dict[row['asset']]

    new_row = pd.Series({
        'Date' : row['time'], 
        'Type' : 'reward', 
        'Received Currency' : asset, 
        'Received Amount' : value_received_minus_fees, 
        'Received Net Worth' : '', 
        'Sent Currency' : '', 
        'Sent Amount' : '' ,
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row
    

def Convert_kraken_withdrawal(row):
    new_row = pd.Series({
        'Date' : row['time'], 
        'Type' : 'transfer', 
        'Received Currency' : row['asset'], 
        'Received Amount' : row['amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['asset'], 
        'Sent Amount' : row['amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : row['asset'], 
        'Fee Amount' : row['fee'], 
        'Fee Net Worth' : ''
    })
    return new_row


def Convert_kraken_deposit(row):
    """
    Chaque ligne déposit apparaît en double dans le fichier Kraken
    Le doublon a un montant dans la colonne balance
    Les deux ont le même refid
    Il faudra changer le Type de ces lignes de deposit à transfert
    Il faudra ajouter les fee, en effet elles n’apparaissent pas dans le fichier Kraken


    """
    new_row = pd.Series({
        'Date' : row['time'], 
        'Type' : 'transfer', 
        'Received Currency' : row['asset'], 
        'Received Amount' : row['amount'], 
        'Received Net Worth' : '', 
        'Sent Currency' : row['asset'], 
        'Sent Amount' : row['amount'], 
        'Sent Net Worth' : '', 
        'Fee Currency' : '', 
        'Fee Amount' : '', 
        'Fee Net Worth' : ''
    })
    return new_row


# def Convert_kraken_widthdraw(row):
#     """
#     Type must be transfer
#     Received Currency, Received Amount, Sent Currency and Sent Amount must be filled
#     Values in Received Currency and Received Amount must match those in Sent Currency and Sent Amount (excluding the fee)
#     Input the associated transaction fee in Fee Currency and Fee Amount (leave them blank if none)
#     Input the net worth amount in Fee Net Worth (leave them blank if none)

#     Note : 14/04/2024 I had to add the columns Fee Currency & Fee Amount in the crypto app source dataset
#     """
#     new_row = pd.Series({
#         'Date' : row['Timestamp (UTC)'], 
#         'Type' : 'transfer', 
#         'Received Currency' : row['Currency'], 
#         'Received Amount' : row['Amount'], 
#         'Received Net Worth' : '', 
#         'Sent Currency' : row['Currency'], 
#         'Sent Amount' : row['Amount'], 
#         'Sent Net Worth' : '', 
#         'Fee Currency' : row['Fee Currency'], 
#         'Fee Amount' : row['Fee Amount'], 
#         'Fee Net Worth' : ''
#     })
#     return new_row


def Convert_dustsweeping_into_several_rows(same_refid_df):
    """
    Convertit un groupe de lignes dustsweeping (N spend, 1 receive) 
    en plusieurs lignes formatées en utilisant un actif pivot DUST_VIRTUAL.
    """
    new_rows = []
    
    # Séparation des lignes selon le type
    spend_rows = same_refid_df.loc[same_refid_df['type'] == 'spend'].to_dict(orient='records')
    receive_row = same_refid_df.loc[same_refid_df['type'] == 'receive'].to_dict(orient='records')[0]

    # 1. Pour chaque ligne 'spend' (poussière), on crée un échange vers DUST_VIRTUAL
    for s_row in spend_rows:
        dust_part_row = {
            'Date': s_row['time'],
            'Type': 'Trade', # On le traite comme un trade pour le pipeline suivant
            'Received Currency': 'DUST_VIRTUAL',
            'Received Amount': 0.0, # On pourra mettre 1.0 ou laisser 0 car c'est neutre
            'Received Net Worth': '',
            'Sent Currency': s_row['asset'],
            'Sent Amount': abs(float(s_row['amount'])), # On passe en positif pour le format cible
            'Sent Net Worth': '',
            'Fee Currency': s_row['asset'], # Souvent 0 sur Kraken pour les dusts
            'Fee Amount': float(s_row['fee']),
            'Fee Net Worth': ''
        }
        new_rows.append(dust_part_row)

    # 2. On crée la ligne finale : Conversion du DUST_VIRTUAL vers la monnaie reçue (ex: ZEUR)
    # Cette ligne est la seule potentiellement imposable dans le futur (si Received est du FIAT)
    final_receive_row = {
        'Date': receive_row['time'],
        'Type': 'Trade',
        'Received Currency': receive_row['asset'],
        'Received Amount': float(receive_row['amount']),
        'Received Net Worth': '',
        'Sent Currency': 'DUST_VIRTUAL',
        'Sent Amount': 0.0, # Équilibrage virtuel
        'Sent Net Worth': '',
        'Fee Currency': receive_row['asset'],
        'Fee Amount': float(receive_row['fee']),
        'Fee Net Worth': ''
    }
    new_rows.append(final_receive_row)

    return new_rows