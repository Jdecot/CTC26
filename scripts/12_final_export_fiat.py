import pandas as pd
import config
from pathlib import Path

def main():
    print(f"🚀 Génération de l'export final (Fiat)...")

    if not config.FILE_TAXABLE_EVENT_WITH_PV.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PV} n'existe pas.")
        return

    # Chargement des données (en string pour préserver les formats numériques)
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PV, dtype=str).fillna("")

    # 1. Conversion de la date et filtrage
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='ISO8601', utc=True)
        
        # Diagnostic : voir quelles années sont présentes
        years_in_data = df['Date'].dt.year.unique()
        print(f"📊 Années détectées dans le fichier source : {sorted(list(years_in_data))}")
        
        # Filtrage : Uniquement 2025 et événements imposables
        # Note : On peut changer 2025 par une autre année si besoin
        mask = (df['Date'].dt.year == 2025) & (df['is_taxable_event'].astype(str).str.upper() == 'TRUE')
        
        count_before = len(df)
        df = df[mask].copy()
        
        if df.empty:
            print(f"⚠️ Aucun événement imposable trouvé pour l'année 2025 (sur {count_before} lignes analysées).")
            return

        # 2. Formatage de la date pour l'export (jj/mm/aaaa)
        df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
    except Exception as e:
        print(f"❌ Erreur lors du traitement chronologique : {e}")
        return

    # 3. Sélection et ordonnancement des colonnes demandées
    columns_to_keep = [
        "Date", 
        "wallet_value_before",
        "Received Amount", 
        "Fee Amount", 
        "PTA_before_tx",
        "PTA_to_deduct", 
        "PTA", 
        "plus_value",
        "Net Received Amount",
        "wallet_value_after",
        "PTA_sell_ratio"
    ]
    
    # Vérification de la présence des colonnes critiques
    missing_cols = [c for c in columns_to_keep if c not in df.columns]
    if missing_cols:
        print(f"⚠️ Colonnes manquantes dans la source : {missing_cols}")

    df_final = df[[c for c in columns_to_keep if c in df.columns]]

    # Sauvegarde
    config.DIR_12_FINAL.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(config.FILE_FINAL_EXPORT_FIAT, index=False)
    
    print(f"✅ Export terminé : {len(df_final)} événements exportés.")
    print(f"📂 Fichier créé : {config.FILE_FINAL_EXPORT_FIAT}")

if __name__ == "__main__":
    main()