import pandas as pd
import config

def extract_price_requirements(df_situation):
    taxable_df = df_situation[df_situation['is_taxable_event'].astype(str).str.upper() == 'TRUE'].copy()
    
    non_crypto_cols = [
        'Date', 'refid', 'subtype', 'Type', 'Detected Type', 
        'Normalized Received Currency', 'Normalized Sent Currency', 
        'Sent Currency', 'Sent Amount', 'Received Currency', 
        'Received Amount', 'Balance', 'platform', 'Received Net Worth', 
        'Sent Net Worth', 'Fee Currency', 'Fee Amount', 'Fee Net Worth', 
        'Normalized Fee Currency', 'is_taxable_event', 'EUR', 'USD', 'ZEUR', 'ZUSD'
    ]
    crypto_columns = [col for col in df_situation.columns if col not in non_crypto_cols]
    
    requirements = []
    for _, row in taxable_df.iterrows():
        for crypto in crypto_columns:
            balance = pd.to_numeric(row[crypto], errors='coerce')
            # On ne demande le prix que si on détient l'actif au moment du calcul
            if balance and abs(balance) > 0: 
                requirements.append({
                    'Date': row['Date'],
                    'Asset': crypto,
                    'Currency': 'EUR' # On simplifie la colonne Pair en Currency
                })
    return pd.DataFrame(requirements).drop_duplicates()

def main():
    if not config.FILE_TAXABLE_EVENT.exists():
        print(f"❌ Erreur : {config.FILE_TAXABLE_EVENT} introuvable.")
        return

    df_situation = pd.read_csv(config.FILE_TAXABLE_EVENT, dtype=str)
    df_all_needs = extract_price_requirements(df_situation)
    
    config.DIR_4_REQUIRED_PRICES.mkdir(parents=True, exist_ok=True)
    df_all_needs.to_csv(config.FILE_REQUIRED_PRICES, index=False)
    
    print(f"✅ Terminé : {len(df_all_needs)} besoins identifiés.")
    print(f"📂 Export : {config.FILE_REQUIRED_PRICES}")

if __name__ == "__main__":
    main()