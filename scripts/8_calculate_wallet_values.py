import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🚀 Calcul de la valeur globale du portefeuille (Before/After)...")

    if not config.FILE_TAXABLE_EVENT_WITH_FIAT_VALUES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_FIAT_VALUES} n'existe pas.")
        return

    # Chargement des données
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_FIAT_VALUES, dtype=str).fillna("")
    
    # Identification des colonnes de valeurs en EUR
    eur_cols = [col for col in df.columns if col.endswith('_eur')]
    
    def process_wallet_values(row):
        # Initialisation par défaut
        res = {'wallet_value_after': "", 'wallet_value_before': ""}
        
        # On ne traite que les événements imposables
        if str(row.get('is_taxable_event', '')).strip().upper() != 'TRUE':
            return pd.Series(res)

        # --- VERIFICATION SECURITÉ ---
        recv_cur = str(row.get('Normalized Received Currency', '')).strip().upper()
        if recv_cur != 'EUR':
            print(f"⚠️  ALERTE : Vente détectée sans EUR reçu | Date: {row['Date']} | Reçu: {row['Received Amount']} {recv_cur} | Refid: {row['refid']}")

        # --- CALCUL VALUE AFTER ---
        total_after = Decimal('0')
        for col in eur_cols:
            val_raw = str(row[col]).strip()
            if val_raw and val_raw.lower() != "nan":
                try:
                    total_after += Decimal(val_raw)
                except (InvalidOperation, ValueError):
                    pass
        
        # --- CALCUL VALUE BEFORE ---
        # Valeur Before = Valeur After + Montant de la vente (Received Amount)
        try:
            rec_amount_raw = str(row.get('Received Amount', '0')).strip()
            rec_amount = Decimal(rec_amount_raw) if rec_amount_raw else Decimal('0')
            total_before = total_after + rec_amount
        except (InvalidOperation, ValueError):
            total_before = total_after

        res['wallet_value_after'] = f"{total_after:f}"
        res['wallet_value_before'] = f"{total_before:f}"
        return pd.Series(res)

    # Application du calcul
    wallet_results = df.apply(process_wallet_values, axis=1)
    df['wallet_value_after'] = wallet_results['wallet_value_after']
    df['wallet_value_before'] = wallet_results['wallet_value_before']

    # Réorganisation des colonnes (wallet_values seront placées avant les cryptos)
    df = module_global.reorder_columns(df)

    # Sauvegarde
    config.DIR_8_WALLET_VALUES.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT_WITH_WALLET_VALUES, index=False)
    
    count = (df['wallet_value_after'] != "").sum()
    print(f"✅ Calcul terminé pour {count} événements imposables.")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_WALLET_VALUES}")

if __name__ == "__main__":
    main()