import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🚀 Calcul du PTA (Prix Total d'Acquisition)...")

    if not config.FILE_TAXABLE_EVENT_WITH_PTA.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PTA} n'existe pas.")
        return

    # Chargement des données
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PTA, dtype=str).fillna("")
    
    pta_running = Decimal('0')
    results_pta = []
    results_pta_to_deduct = []

    for idx, row in df.iterrows():
        is_buy = str(row.get('Detected Type', '')).strip().lower() == 'buy'
        is_sale = str(row.get('is_taxable_event', '')).strip().upper() == 'TRUE'
        
        # Alerte si une ligne semble être les deux à la fois
        if is_buy and is_sale:
            print(f"⚠️  ALERTE : Ligne {idx} détectée comme ACHAT et VENTE simultanément ! Refid: {row['refid']}")

        current_pta_to_deduct = Decimal('0')

        try:
            if is_buy:
                # PTA = PTA précédent + montant Fiat dépensé
                sent_amt_raw = str(row.get('Sent Amount', '0')).strip()
                sent_amt = abs(Decimal(sent_amt_raw)) if sent_amt_raw else Decimal('0')
                pta_running += sent_amt
                
            elif is_sale:
                # Calcul du PTA à déduire pour cette vente
                ratio_raw = str(row.get('PTA_sell_ratio', '0')).strip()
                ratio = Decimal(ratio_raw) if ratio_raw else Decimal('0')
                
                current_pta_to_deduct = pta_running * ratio
                
                # Mise à jour du PTA restant dans le portefeuille
                pta_running -= current_pta_to_deduct
            
            # Pour les autres lignes (trades crypto-crypto, rewards, transferts), 
            # pta_running reste inchangé.

        except (InvalidOperation, ValueError):
            print(f"⚠️  Erreur de calcul à la ligne {idx} (Refid: {row['refid']})")

        # Stockage des résultats formatés
        results_pta.append(f"{pta_running:f}")
        if current_pta_to_deduct > 0:
            results_pta_to_deduct.append(f"{current_pta_to_deduct:f}")
        else:
            results_pta_to_deduct.append("")

    # Ajout des colonnes au DataFrame
    df['PTA'] = results_pta
    df['PTA_to_deduct'] = results_pta_to_deduct

    # Réorganisation des colonnes
    df = module_global.reorder_columns(df)

    # Sauvegarde
    config.DIR_10_PTA.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT_WITH_PTA_VALUES, index=False)
    
    print(f"✅ Calcul du PTA terminé.")
    print(f"💰 PTA final du portefeuille : {pta_running:,.2f} EUR")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_PTA_VALUES}")

if __name__ == "__main__":
    main()