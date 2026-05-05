import pandas as pd
import config

def main():
    dfs = []
    
    # 1. Chargement des prix Yahoo Finance
    if config.FILE_GET_YFINANCE_PRICES.exists():
        df_yf = pd.read_csv(config.FILE_GET_YFINANCE_PRICES)
        dfs.append(df_yf)
        print(f"✅ Chargé : {config.FILE_GET_YFINANCE_PRICES.name} ({len(df_yf)} lignes)")
    else:
        print(f"⚠️ Non trouvé : {config.FILE_GET_YFINANCE_PRICES.name} (Attendu dans {config.DIR_5_GET_PRICES})")
    
    # 2. Chargement des prix manuels (s'ils existent)
    if config.FILE_GET_MANUAL_PRICES.exists():
        df_manual = pd.read_csv(config.FILE_GET_MANUAL_PRICES)
        dfs.append(df_manual)
        print(f"✅ Chargé : {config.FILE_GET_MANUAL_PRICES.name} ({len(df_manual)} lignes)")
    else:
        print(f"⚠️ Non trouvé : {config.FILE_GET_MANUAL_PRICES.name}")

    if not dfs:
        print("❌ Aucun fichier de prix (Yahoo ou Manuel) n'a été trouvé.")
        return

    # 3. Merge et nettoyage
    df_merged = pd.concat(dfs, ignore_index=True)
    
    # 4. Tri simple
    # On ne supprime plus les doublons ici pour que le script 6a puisse les analyser
    df_merged = df_merged.sort_values(by=['Date', 'Asset'], ascending=[True, True])
    
    # 5. Export
    config.DIR_5_GET_PRICES.mkdir(parents=True, exist_ok=True)
    df_merged.to_csv(config.FILE_MERGED_PRICES, index=False)
    
    print(f"💾 Succès : {len(df_merged)} prix consolidés dans {config.FILE_MERGED_PRICES}")

if __name__ == "__main__":
    main()