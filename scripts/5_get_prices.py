import pandas as pd
import yfinance as yf
from datetime import timedelta
import os
import config

# --- CONFIGURATION ---
INPUT_FILE = config.FILE_REQUIRED_PRICES
OUTPUT_FILE = config.FILE_GET_YFINANCE_PRICES
MAX_DATE_OFFSET_DAYS = 1 # Sécurité : écart max toléré avec la date Yahoo

def main():
    config.DIR_5_GET_PRICES.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        print(f"❌ Erreur : {INPUT_FILE} introuvable.")
        return

    # 1. Chargement des besoins
    df_req = pd.read_csv(INPUT_FILE)
    df_req['Date'] = pd.to_datetime(df_req['Date'], format='ISO8601')
    
    # 2. Gestion du CACHE (ne pas redemander ce qu'on a déjà)
    existing_data = pd.DataFrame()
    if OUTPUT_FILE.exists():
        existing_data = pd.read_csv(OUTPUT_FILE, dtype=str)
        existing_data['Date'] = pd.to_datetime(existing_data['Date'], format='ISO8601')
        print(f"📦 Cache chargé : {len(existing_data)} prix déjà connus.")

    results = []

    # 3. Groupement par Asset
    for asset, group in df_req.groupby('Asset'):
        ticker_symbol = f"{asset}-EUR"
        
        # Filtrer pour ne garder que les dates qu'on n'a pas déjà en cache
        if not existing_data.empty:
            already_done = existing_data[existing_data['Asset'] == asset]['Date']
            group_to_fetch = group[~group['Date'].isin(already_done)]
        else:
            group_to_fetch = group

        if group_to_fetch.empty:
            print(f"✅ {asset} est déjà à jour (Cache).")
            continue

        print(f"🔍 Récupération Yahoo Finance pour : {ticker_symbol} ({len(group_to_fetch)} nouvelles dates)...")
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            # Marge de sécurité pour les weekends/jours fériés
            start_date = group_to_fetch['Date'].min() - timedelta(days=3)
            end_date = group_to_fetch['Date'].max() + timedelta(days=3)
            
            hist = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d'
            )
            
            if hist.empty:
                print(f"⚠️ Aucun prix trouvé pour {ticker_symbol}")
                continue
                
            hist.index = hist.index.tz_localize(None)

            for _, row in group_to_fetch.iterrows():
                target_date = row['Date'].normalize()
                
                # Trouver la date la plus proche dans l'historique Yahoo
                if target_date in hist.index:
                    found_date = target_date
                else:
                    # On cherche la date la plus proche (passée ou future)
                    diffs = abs(hist.index - target_date)
                    found_date = hist.index[diffs.argmin()]
                
                # SECURITÉ : Vérification de l'écart
                offset = abs((found_date - target_date).days)
                if offset > MAX_DATE_OFFSET_DAYS:
                    print(f"❌ Écart trop grand pour {asset} le {row['Date']} (écart: {offset} jours). Ignoré.")
                    price = None
                else:
                    price = hist.loc[found_date, 'Close']

                if price is not None:
                    results.append({
                        'Date': row['Date'],
                        'Asset': asset,
                        'Price_EUR': price,
                        'Currency': 'EUR',
                        'Source': 'YahooFinance'
                    })
                
        except Exception as e:
            print(f"❌ Erreur sur {asset}: {e}")

    # 4. Fusion avec le cache et sauvegarde (toujours sauvegarder pour garantir l'existence du fichier)
    df_new = pd.DataFrame(results)
    if not df_new.empty or not existing_data.empty:
        df_final = pd.concat([existing_data, df_new])
        # Normalisation des dates pour le dédoublonnage
        df_final['Date'] = pd.to_datetime(df_final['Date'], format='ISO8601', utc=True)
        df_final = df_final.drop_duplicates(subset=['Date', 'Asset'])
        df_final.to_csv(OUTPUT_FILE, index=False)
        if not df_new.empty:
            print(f"💾 Mise à jour terminée : {len(df_new)} prix ajoutés. Total : {len(df_final)} prix en base.")
        else:
            print("☕ Tout est déjà synchronisé (Cache à jour).")

if __name__ == "__main__":
    main()