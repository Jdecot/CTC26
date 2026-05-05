import pandas as pd
import config

def load_normalized_csv(file_path):
    """
    Charge un CSV et normalise la colonne Date et Asset pour comparaison.
    """
    if not file_path.exists():
        return None
    
    # Lecture brute en string pour éviter les problèmes de formatage automatique
    df = pd.read_csv(file_path, dtype=str)

    # On s'assure que Date et Asset sont des chaînes propres pour le groupement
    df['Date'] = df['Date'].astype(str).str.strip()
    if 'Asset' in df.columns:
        df['Asset'] = df['Asset'].astype(str).str.strip().str.upper()
    
    # Conversion du prix en numérique pour les calculs
    if 'Price_EUR' in df.columns:
        df['Price_EUR'] = pd.to_numeric(df['Price_EUR'].str.replace(',', '.'), errors='coerce')
        
    return df

def check_multiple_sources(df_db):
    """
    Identifie les couples (Date, Asset) qui possèdent plus d'une source unique.
    """
    if df_db is None or 'Source' not in df_db.columns:
        print("⚠️  Colonne 'Source' manquante dans price_db.csv. Impossible de vérifier les sources multiples.")
        return []

    # On groupe par date et actif, et on compte le nombre de sources uniques pour chaque groupe
    source_counts = df_db.groupby(['Date', 'Asset'])['Source'].nunique()
    
    # On filtre les groupes qui ont plus d'une source
    multi_source = source_counts[source_counts > 1]
    count = len(multi_source)

    if count > 0:
        print(f"ℹ️  Nombre de prix (Date/Asset) ayant plusieurs sources : {count}")
    else:
        print("✅ Aucun prix n'a de sources multiples (chaque date/actif n'a qu'une seule source).")
    
    return multi_source.index.tolist()


def check_price_consistency(df_db, duplicate_keys):
    """
    Alerte si plusieurs prix pour le même actif/date ont un écart > 5%.
    """
    if df_db is None or df_db.empty or not duplicate_keys:
        return

    # On groupe directement par Date et Asset pour analyser chaque "point de prix"
    grouped = df_db.dropna(subset=['Price_EUR']).groupby(['Date', 'Asset'])
    
    alert_count = 0
    for key in duplicate_keys:
        if key not in grouped.groups:
            continue
            
        group = grouped.get_group(key)
        date_str, asset = key

        p_min = group['Price_EUR'].min()
        p_max = group['Price_EUR'].max()
        
        diff_pct = (p_max - p_min) / p_min if p_min > 0 else 0
        
        if diff_pct > 0.05:
            print(f"⚖️  ALERTE {asset} | {date_str} | Écart {diff_pct:.1%} (Min: {p_min:,.2f} / Max: {p_max:,.2f})")
            alert_count += 1

    if alert_count == 0:
        print("✅ Tous les prix en double sont cohérents (écart < 5%).")
    else:
        print(f"⚠️ TOTAL : {alert_count} alertes de cohérence (>5%) détectées.")

def main():
    """
    Analyse la qualité des données de prix avant l'enrichissement final.
    """
    print(f"\n{'='*60}")
    print(f"🔍 ANALYSE QUALITÉ DES PRIX")
    print(f"{'='*60}")

    df_db = load_normalized_csv(config.FILE_MERGED_PRICES)

    if df_db is None:
        print("❌ Erreur : Base de prix (price_db.csv) introuvable.")
        return

    print("\n--- 1. Analyse des sources de données ---")
    duplicates = check_multiple_sources(df_db)

    print("\n--- Vérification de la cohérence des prix (Écart < 5%) ---")
    check_price_consistency(df_db, duplicates)

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()