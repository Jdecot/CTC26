import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🚀 Calcul de la Plus-Value (Gain/Perte)...")

    if not config.FILE_TAXABLE_EVENT_WITH_PTA_VALUES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PTA_VALUES} n'existe pas.")
        return

    # Chargement des données (en string pour la précision Decimal)
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PTA_VALUES, dtype=str).fillna("")
    
    def calculate_pv(row):
        # On ne traite que les événements imposables
        if str(row.get('is_taxable_event', '')).strip().upper() != 'TRUE':
            return ""

        try:
            # Received Amount est le Prix de cession
            rec_amount_raw = str(row.get('Net Received Amount', '0')).strip()
            rec_amount = Decimal(rec_amount_raw) if rec_amount_raw else Decimal('0')
            
            # PTA_to_deduct est la part du prix d'acquisition calculée à l'étape 10
            pta_deduct_raw = str(row.get('PTA_to_deduct', '0')).strip()
            pta_deduct = Decimal(pta_deduct_raw) if pta_deduct_raw else Decimal('0')
            
            # Plus-Value = Prix de cession - PTA à déduire
            pv = rec_amount - pta_deduct
            return f"{pv:f}"
            
        except (InvalidOperation, ValueError):
            return ""

    # Application du calcul ligne par ligne
    df['plus_value'] = df.apply(calculate_pv, axis=1)

    # Réorganisation des colonnes
    df = module_global.reorder_columns(df)

    # Sauvegarde
    config.DIR_11_PV.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT_WITH_PV, index=False)
    
    count = (df['plus_value'] != "").sum()
    print(f"✅ Calcul terminé pour {count} événements imposables.")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_PV}")

if __name__ == "__main__":
    main()