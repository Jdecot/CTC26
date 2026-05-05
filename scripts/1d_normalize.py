import pandas as pd
import config



def strict_normalize(asset, platform):
    """
    Normalise l'actif. 
    Si Kraken : utilise le dictionnaire. Si manquant, print une alerte.
    Si autre (Crypto.com) : retourne l'actif tel quel.
    """
    if not asset or pd.isna(asset) or str(asset).strip() == "":
        return asset
    
    asset_clean = str(asset).strip().upper()
    
    if "kraken" in platform.lower():
        if asset_clean in config.KRAKEN_CRYPTO_ID:
            return config.KRAKEN_CRYPTO_ID[asset_clean]
        else:
            # SÉCURITÉ : On alerte l'utilisateur si une monnaie Kraken est inconnue
            print(f"⚠️ ALERTE : L'actif '{asset_clean}' est inconnu dans le mapping Kraken.")
            return asset_clean
            
    # Pour Crypto.com et les autres, on retourne tel quel (déjà standard)
    return asset_clean

def process_normalization(input_file, output_file):
    # On force la lecture en string (dtype=str) pour éviter que Pandas ne convertisse 
    # les montants en flottants et n'introduise de la notation scientifique.
    df = pd.read_csv(input_file, dtype=str)
    
    # Création des nouvelles colonnes normalized tout en gardant les originales
    mapping_tasks = {
        'Received Currency': 'Normalized Received Currency',
        'Sent Currency': 'Normalized Sent Currency',
        'Fee Currency': 'Normalized Fee Currency'
    }
    
    for original, new in mapping_tasks.items():
        df[new] = df.apply(
            lambda row: strict_normalize(row[original], row['platform']), axis=1
        )

    # Sauvegarde
    df.to_csv(output_file, index=False)
    print(f"\n✅ Normalisation terminée. Fichier sauvegardé : {output_file}")

# Utilisation
if __name__ == "__main__":
    process_normalization(config.FILE_ALL_TRADES, config.FILE_ALL_TRADES_NORMALIZED)