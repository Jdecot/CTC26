import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🚀 Calcul du PTA Sell Ratio (Ratio de cession)...")

    if not config.FILE_TAXABLE_EVENT_WITH_WALLET_VALUES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_WALLET_VALUES} n'existe pas.")
        return

    # Chargement des données (en string pour la précision Decimal)
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_WALLET_VALUES, dtype=str).fillna("")
    
    def calculate_pta_ratio(row):
        # On ne traite que les événements imposables
        if str(row.get('is_taxable_event', '')).strip().upper() != 'TRUE':
            return ""

        try:
            # Récupération des valeurs
            # Received Amount est le montant Fiat (Prix de cession)
            rec_amount_raw = str(row.get('Received Amount', '0')).strip()
            rec_amount = Decimal(rec_amount_raw) if rec_amount_raw else Decimal('0')
            
            # wallet_value_before est la valeur globale du portefeuille avant cession
            wallet_before_raw = str(row.get('wallet_value_before', '0')).strip()
            wallet_before = Decimal(wallet_before_raw) if wallet_before_raw else Decimal('0')
            
            if wallet_before == 0:
                return "0"
            
            # Formule officielle : Prix de cession / Valeur globale du portefeuille
            ratio = rec_amount / wallet_before
            return f"{ratio:f}"
            
        except (InvalidOperation, ValueError, ZeroDivisionError):
            return ""

    # Application du calcul ligne par ligne
    df['PTA_sell_ratio'] = df.apply(calculate_pta_ratio, axis=1)

    # Réorganisation des colonnes (PTA_sell_ratio sera placé avant les cryptos via module_global)
    df = module_global.reorder_columns(df)

    # Sauvegarde
    config.DIR_9_PTA.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT_WITH_PTA, index=False)
    
    count = (df['PTA_sell_ratio'] != "").sum()
    print(f"✅ Calcul terminé pour {count} événements imposables.")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_PTA}")

if __name__ == "__main__":
    main()