import pandas as pd
import config

def get_crypto_columns(df):
    """
    Identifie les colonnes d'actifs cryptos (celles qui contiennent les soldes).
    On exclut les colonnes de métadonnées et les colonnes de prix.
    """
    technical_cols = [
        'Date', 'refid', 'subtype', 'Type', 'Detected Type', 
        'Normalized Received Currency', 'Normalized Sent Currency', 
        'Sent Currency', 'Sent Amount', 'Received Currency', 
        'Received Amount', 'Balance', 'platform', 'Received Net Worth', 
        'Sent Net Worth', 'Fee Currency', 'Fee Amount', 'Fee Net Worth', 
        'Normalized Fee Currency', 'is_taxable_event', 'EUR', 'USD', 'ZEUR', 'ZUSD', 'USDT', 'USDC'
    ]
    # On ne garde que les colonnes qui ne sont pas dans la liste technique et qui ne finissent pas par _price
    return [col for col in df.columns if col not in technical_cols and not col.endswith('_price')]

def main():
    print(f"🔍 Vérification de la complétude des prix pour les événements imposables...")

    if not config.FILE_TAXABLE_EVENT_WITH_PRICES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PRICES} n'existe pas.")
        return

    # Chargement en string pour la précision, conversion sélective après
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PRICES, dtype=str)
    
    # Identification des cryptos présentes dans le fichier
    crypto_assets = get_crypto_columns(df)
    
    # Filtre sur les événements imposables
    mask_taxable = df['is_taxable_event'].astype(str).str.upper() == 'TRUE'
    df_taxable = df[mask_taxable]

    if df_taxable.empty:
        print("✅ Aucun événement imposable détecté dans le fichier.")
        return

    alert_count = 0
    found_count = 0
    
    for idx, row in df_taxable.iterrows():
        date_str = row['Date']
        
        for crypto in crypto_assets:
            # Récupération du solde et du prix
            val_str = row.get(crypto, "0")
            price_str = row.get(f"{crypto}_price", "")

            # Conversion numérique pour test
            try:
                amount = float(val_str) if val_str and val_str != "" else 0.0
            except ValueError:
                amount = 0.0

            try:
                # Un prix vide, NaN ou "0" est considéré comme manquant/invalide
                price = float(price_str) if price_str and price_str != "" else 0.0
            except ValueError:
                price = 0.0

            # Si on détient la crypto (> 0) mais que le prix est absent ou nul
            if amount > 0 and price <= 0:
                print(f"⚠️ PRIX MANQUANT | {date_str} | Crypto: {crypto} (Solde: {amount}) | Colonne prix: '{price_str}'")
                alert_count += 1
            elif amount > 0 and price > 0:
                found_count += 1

    print("-" * 60)
    if alert_count == 0:
        print(f"✅ Validation réussie : {found_count} prix trouvés ({len(df_taxable)} lignes analysées).")
    else:
        print(f"❌ ÉCHEC : {alert_count} prix manquants détectés ({found_count} prix valides trouvés).")
        print("💡 Action : Complétez 'get_manual_prices.csv' et relancez la fusion (5b) puis l'enrichissement (6c).")
    print("-" * 60)

if __name__ == "__main__":
    main()