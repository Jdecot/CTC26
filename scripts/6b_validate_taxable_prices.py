import pandas as pd
import config
import module_global

def main():
    print(f"🔍 Vérification de la complétude des prix pour les événements imposables...")

    if not config.FILE_TAXABLE_EVENT_WITH_PRICES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PRICES} n'existe pas.")
        return

    # Chargement en string pour la précision, conversion sélective après
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PRICES, dtype=str)
    
    # Identification des cryptos présentes dans le fichier
    crypto_assets = module_global.get_crypto_columns(df, include_stables=True)
    
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