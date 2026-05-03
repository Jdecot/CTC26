import pandas as pd
from decimal import Decimal, InvalidOperation
import config
from pathlib import Path

def convert_csv_to_excel(csv_input_path, excel_output_path):
    """
    Converts a single CSV file to an Excel file.
    Ensures the destination directory exists before writing.
    """
    try:
        # Create parent directory if it does not exist
        Path(excel_output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Read CSV data and export to Excel format
        # Standard comma separator used by default
        data_frame = pd.read_csv(csv_input_path, sep=',')
        data_frame.to_excel(excel_output_path, index=False)
        return True
    except Exception as error:
        print(f"  ✗ Error during conversion of {csv_input_path}: {error}")
        return False
    

def show_holdings():
    """Lit la dernière ligne de account_situation.csv et affiche les holdings triés."""
    csv_path = config.FILE_ACCOUNT_SITUATION
    
    if not csv_path.exists():
        print(f"⚠️  Fichier non trouvé : {csv_path}")
        return
    
    df = pd.read_csv(csv_path, dtype=str)
    if df.empty:
        print("⚠️  Le fichier account_situation.csv est vide")
        return
    
    last_row = df.iloc[-1]
    
    # Colonnes techniques ou de transaction à ne pas afficher comme des holdings
    cols_to_ignore = [
        "Date", "platform", "Platform", "refid", "subtype", "Type", "Detected Type", 
        "Received Currency", "Normalized Received Currency", "Received Amount", "Received Net Worth",
        "Sent Currency", "Normalized Sent Currency", "Sent Amount", "Sent Net Worth", 
        "Fee Currency", "Normalized Fee Currency", "Fee Amount", "Fee Net Worth",
        "Balance", "Money_movement", "wallet_value_eur", "wallet_value_eur_m1", "EUR", "USD"
    ]

    holdings = {}
    for col in df.columns:
        if col in cols_to_ignore:
            continue
        try:
            raw_val = str(last_row[col]).strip()
            # On ignore les colonnes vides ou contenant 'nan' pour éviter les erreurs de tri
            if raw_val == "" or raw_val.lower() == "nan":
                continue
                
            val = Decimal(raw_val)
            # On ne garde que les nombres finis (pas NaN, pas Infini) et non nuls
            if not val.is_finite():
                continue
            if val != Decimal('0'):
                holdings[col] = val
        except (ValueError, TypeError, InvalidOperation):
            # Ignore les colonnes non numériques ou valeurs non convertibles
            pass
    
    sorted_holdings = dict(sorted(holdings.items(), key=lambda x: x[1], reverse=True))
    
    print("\n" + "="*40)
    print("📊 HOLDINGS (dernière ligne)")
    print("="*40)
    for crypto, qty in sorted_holdings.items():
        # Formate en décimal avec 18 chiffres max après la virgule, en supprimant les zéros inutiles à la fin
        print(f"  {crypto}: {qty:.18f}".rstrip('0').rstrip('.'))

def reorder_columns(df):
    """Réorganise les colonnes pour mettre les métadonnées et montants au début."""
    cols_prioritaires = [
        "Date", "refid", "subtype", "Type", "Detected Type", 
         "Normalized Received Currency", "Normalized Sent Currency",
        "Sent Currency", "Sent Amount",  
        "Received Currency", "Received Amount",
        "Balance"
    ]

    cols_existantes = [c for c in cols_prioritaires if c in df.columns]
    autres_cols = [c for c in df.columns if c not in cols_existantes]
    return df[cols_existantes + autres_cols]
