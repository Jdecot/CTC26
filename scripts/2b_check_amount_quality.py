import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🔍 Vérification des soldes négatifs dans : {config.FILE_ACCOUNT_SITUATION}")

    if not config.FILE_ACCOUNT_SITUATION.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_ACCOUNT_SITUATION} n'existe pas.")
        return

    # Chargement en string pour la précision avec Decimal
    df = pd.read_csv(config.FILE_ACCOUNT_SITUATION, dtype=str)
    
    # Identification des colonnes d'actifs via le module global
    # On inclut les stables car un solde négatif sur l'USDT est tout aussi problématique
    crypto_cols = module_global.get_crypto_columns(df, include_stables=True)
    
    negative_alerts = 0
    
    for _, row in df.iterrows():
        date_val = row.get('Date', 'Inconnue')
        
        for crypto in crypto_cols:
            val_raw = row.get(crypto, "0")
            
            try:
                # Utilisation de Decimal pour éviter les erreurs d'arrondi des floats
                balance = Decimal(str(val_raw)) if val_raw and str(val_raw).lower() != 'nan' else Decimal('0')
            except (InvalidOperation, ValueError):
                balance = Decimal('0')

            # Alerte si le solde est strictement inférieur à 0
            if balance < 0:
                print(f"❌ SOLDE NÉGATIF | {date_val} | {crypto:10} | Solde: {balance}")
                negative_alerts += 1

    print("-" * 60)
    if negative_alerts == 0:
        print("✅ Validation terminée : Aucun solde négatif détecté.")
    else:
        print(f"⚠️  Attention : {negative_alerts} soldes négatifs trouvés.")
        print("💡 Ces erreurs sont souvent dues à des frais d'échange non répertoriés ou des arrondis (dust).")
        print("💡 Action : Vérifiez les transactions précédant ces dates dans le fichier normalisé.")
    print("-" * 60)

if __name__ == "__main__":
    main()