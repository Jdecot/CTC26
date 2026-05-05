import pandas as pd
import config

def load_normalized_csv(file_path):
    """
    Charge un CSV et normalise la colonne Date en datetime UTC pour comparaison.
    """
    if not file_path.exists():
        return None
    
    df = pd.read_csv(file_path)
    # Normalisation pour éviter les erreurs de format de chaîne (espace, ISO, etc.)
    df['Date'] = pd.to_datetime(df['Date'], format='ISO8601', utc=True)
    if 'Asset' in df.columns:
        df['Asset'] = df['Asset'].str.strip().str.upper()
    return df

def create_price_lookup_set(df_db):
    """
    Crée un set de tuples (Date, Asset) pour une recherche ultra-rapide.
    """
    if df_db is None or df_db.empty:
        return set()
    
    # On crée une collection de clés uniques (Date, Actif) présentes en base
    return set(zip(df_db['Date'], df_db['Asset']))

def find_missing_prices(df_required, lookup_set):
    """
    Identifie les lignes du fichier requis qui ne sont pas dans le lookup.
    """
    missing_items = []
    
    for _, row in df_required.iterrows():
        key = (row['Date'], row['Asset'])
        if key not in lookup_set:
            missing_items.append({
                'Date': row['Date'],
                'Asset': row['Asset']
            })
            
    return missing_items

def print_report(missing_list):
    """
    Affiche les alertes ou le succès de la vérification.
    """
    if not missing_list:
        print("✅ Tous les prix requis sont présents dans price_db.csv.")
        return

    print(f"⚠️  ALERTE : {len(missing_list)} prix sont manquants dans la base de données !")
    print("-" * 50)
    for item in missing_list:
        # Formatage lisible de la date pour le print
        date_str = item['Date'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"❌ Prix manquant : {date_str} | Crypto: {item['Asset']}")
    print("-" * 50)
    print("💡 Conseil : Vérifiez les tickers dans config.py ou complétez get_manual_prices.csv")

def main():
    """
    Point d'entrée pour la vérification de la qualité des prix récupérés.
    """
    print(f"🔍 Vérification de la qualité des prix...")

    df_req = load_normalized_csv(config.FILE_REQUIRED_PRICES)
    df_db = load_normalized_csv(config.FILE_MERGED_PRICES)

    if df_req is None:
        print(f"❌ Erreur : Fichier des besoins introuvable ({config.FILE_REQUIRED_PRICES})")
        return

    # Transformation de la DB en set pour comparaison performante
    lookup = create_price_lookup_set(df_db)
    
    missing = find_missing_prices(df_req, lookup)
    print_report(missing)

if __name__ == "__main__":
    main()