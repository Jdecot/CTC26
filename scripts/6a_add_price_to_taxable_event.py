import pandas as pd
import config

def get_crypto_columns(df):
    """
    Identifie les colonnes d'actifs cryptos en excluant les colonnes techniques et fiat.
    """
    non_crypto_cols = [
        'Date', 'refid', 'subtype', 'Type', 'Detected Type', 
        'Normalized Received Currency', 'Normalized Sent Currency', 
        'Sent Currency', 'Sent Amount', 'Received Currency', 
        'Received Amount', 'Balance', 'platform', 'Received Net Worth', 
        'Sent Net Worth', 'Fee Currency', 'Fee Amount', 'Fee Net Worth', 
        'Normalized Fee Currency', 'is_taxable_event', 'EUR', 'USD', 'ZEUR', 'ZUSD', 'USDT', 'USDC'
    ]
    return [col for col in df.columns if col not in non_crypto_cols]

def load_dataframes():
    """
    Charge le fichier des événements imposables (source) et le fichier des prix consolidés.
    """
    # On charge le fichier généré à l'étape 3/4 qui contient les soldes et le flag taxable
    df_taxable = pd.read_csv(config.FILE_TAXABLE_EVENT, dtype=str)
    
    # On charge les prix récupérés et fusionnés à l'étape 5b
    df_prices = pd.read_csv(config.FILE_MERGED_PRICES)
    
    # Normalisation des dates pour permettre la jointure précise
    df_taxable['Date'] = pd.to_datetime(df_taxable['Date'], format='ISO8601', utc=True)
    df_prices['Date'] = pd.to_datetime(df_prices['Date'], format='ISO8601', utc=True)
    
    return df_taxable, df_prices

def build_price_map(df_prices):
    """
    Crée un dictionnaire de recherche rapide : {(Date, Asset): Prix}.
    """
    price_map = {}
    
    # Sécurité : si le fichier de prix est vide ou mal formé
    if 'Price_EUR' not in df_prices.columns or 'Asset' not in df_prices.columns:
        print("⚠️ Attention : La colonne 'Price_EUR' est absente de la base de prix.")
        return price_map

    for _, row in df_prices.iterrows():
        key = (row['Date'], str(row['Asset']).upper())
        price_map[key] = row['Price_EUR']
    return price_map

def initialize_price_columns(df, crypto_cols):
    """
    Crée les colonnes de prix vides pour chaque actif crypto identifié.
    """
    for crypto in crypto_cols:
        df[f"{crypto}_price"] = ""
    return df

def fill_crypto_prices(df, price_map, crypto_cols):
    """
    Remplit les cellules de prix pour les événements identifiés comme imposables.
    """
    # Filtre sur les événements imposables uniquement
    is_taxable_mask = df['is_taxable_event'].astype(str).str.upper() == 'TRUE'
    
    for idx, row in df[is_taxable_mask].iterrows():
        current_date = row['Date']
        for crypto in crypto_cols:
            price = price_map.get((current_date, crypto.upper()))
            if price is not None:
                # Conversion en string obligatoire car df_taxable est en dtype=str
                df.at[idx, f"{crypto}_price"] = str(price)

    return df

def main():
    """
    Point d'entrée principal pour enrichir le fichier des événements imposables avec les prix.
    """
    print(f"🔍 Début de l'enrichissement des prix...")
    
    if not config.FILE_TAXABLE_EVENT.exists() or not config.FILE_MERGED_PRICES.exists():
        print("❌ Erreur : Fichiers sources manquants (Taxable Events ou Merged Prices).")
        return

    df_taxable, df_prices = load_dataframes()
    crypto_columns = get_crypto_columns(df_taxable)
    price_map = build_price_map(df_prices)
    
    df_enriched = initialize_price_columns(df_taxable, crypto_columns)
    df_enriched = fill_crypto_prices(df_enriched, price_map, crypto_columns)
    
    # Sauvegarde du résultat dans le dossier de l'étape 6
    config.DIR_6_TAXABLE_EVENT_WITH_PRICES.mkdir(parents=True, exist_ok=True)
    df_enriched.to_csv(config.FILE_TAXABLE_EVENT_WITH_PRICES, index=False)
    
    print(f"✅ Enrichissement terminé. Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_PRICES}")

if __name__ == "__main__":
    main()