import pandas as pd
import time
from datetime import datetime, timedelta
import pipeline_fct
import config


def formater_date(date_str):
    from datetime import datetime
    if pd.isna(date_str)  : 
        return 
    else : 
        date_obj = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    

def roundColumns(df, col_list_to_round):

    # Itérer sur la liste des colonnes et arrondir
    for col_name in col_list_to_round:
        
        if df[col_name].dtype == 'float64':  # Vérifier si la colonne est de type float
            print("round : ", col_name)
            # df[col_name] = df[col_name].round(1).astype(int)
            df[col_name] = df[col_name].apply(lambda x: round(x, 0))
    return df


def lastModification(df): 

    # Supprimer la première ligne qui est vide
    df = df[1:]

    # Convertir le format de date pour ingestion par le site des impôts
    df["Date"] = df["Date"].apply(formater_date)

    col_list_to_round =  ["wallet_value_eur_m1", "Money_movement", "PTA", "wallet_value_eur", "plus_value", "fraction_capital_initial"]
    df = roundColumns(df, col_list_to_round)
    # Liste des colonnes à mettre au début (dans l'ordre souhaité)
    colonnes_debut = ["Date", "wallet_value_eur_m1", "Money_movement", "PTA",  "plus_value", "Platform", "Type", "fraction_capital_initial", "wallet_value_eur"]
    # colonnes_restantes = [col for col in df.columns if col not in colonnes_debut]
    # nouvel_ordre_colonnes = colonnes_debut + colonnes_restantes
    new_df = df[colonnes_debut]

    return new_df

def main(computed_situation_path, taxable_trades_situation_path):
    """
    """
    computed_situation = pd.read_csv(computed_situation_path, sep=',')
    
    computed_situation = lastModification(computed_situation.copy())

    # taxable_trades_situation = computed_situation[(computed_situation['Type'] == 'sell') | (computed_situation['Type'] == 'buy')]
    taxable_trades_situation = computed_situation[(computed_situation['Type'] == 'sell')]
    # taxable_trades_situation = computed_situation.copy(deep=True)

    # col_to_keep = ['Date', 'EUR_spent', 'before_trade_EUR_spent', 'wallet_value_eur', 'before_trade_wallet_value_eur', 'prix_cession', 'plus_value_du_sell']
    # taxable_trades_situation_filtered = taxable_trades_situation[col_to_keep]
    taxable_trades_situation_filtered = taxable_trades_situation

    # Export to CSV
    taxable_trades_situation_filtered.to_csv(config.FILE_TAXABLE_TRADES, index=False)
    # Export Excel via fonction commune (décommenter si besoin)
    # pipeline_fct.export_to_excel(taxable_trades_situation_filtered, taxable_trades_situation_path + ".xlsx", sheet_name='TaxableTrades')

# File path
computed_situation_path = config.FILE_COMPUTED_PV
taxable_trades_situation_path = config.FILE_TAXABLE_TRADES


main(computed_situation_path, taxable_trades_situation_path)
