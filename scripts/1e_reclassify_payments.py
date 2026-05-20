import pandas as pd
import config
from decimal import Decimal

def main():
    """
    Script 1e : Reclasse les retraits (transferts) qui sont en réalité des paiements (ventes).
    S'appuie sur le dictionnaire config.PAYMENTS_RECLASSIFICATION défini dans config.py.
    Ce script transforme un retrait crypto en une vente (Detected Type = 'sell') avec une contrepartie fiat.
    """
    print(f"🚀 Reclassification des paiements en cours...")

    # Chemins des fichiers basés sur config.py
    input_file = config.FILE_ALL_TRADES_NORMALIZED
    output_file = config.FILE_ALL_TRADES_RECLASSIFIED

    if not input_file.exists():
        print(f"❌ Erreur : Fichier source introuvable ({input_file})")
        return

    # Chargement des transactions normalisées (dtype=str pour préserver la précision Decimal)
    df = pd.read_csv(input_file, dtype=str).fillna("")

    # Récupération de la configuration de reclassification
    # Format attendu dans config.py : 
    # PAYMENTS_RECLASSIFICATION = { "REFID_ICI": {"Received Currency": "EUR", "Received Amount": "15.50"} }
    reclass_map = getattr(config, 'PAYMENTS_RECLASSIFICATION', {})

    if not reclass_map:
        print("ℹ️ Aucun dictionnaire PAYMENTS_RECLASSIFICATION trouvé ou dictionnaire vide dans config.py.")
        # On génère quand même le fichier pour maintenir la chaîne du pipeline
        df.to_csv(output_file, index=False)
        return

    reclassified_count = 0

    for idx, row in df.iterrows():
        refid = row.get('refid', '')
        
        if refid in reclass_map:
            payment_info = reclass_map[refid]
            
            # On change le type détecté en 'sell' pour que les scripts suivants le traitent comme imposable
            df.at[idx, 'Detected Type'] = 'sell'
            df.at[idx, 'Normalized Received Currency'] = 'EUR'
            df.at[idx, 'Type'] = 'spend'
            df.at[idx, 'subtype'] = 'tradespot'

            # On injecte les valeurs de la contrepartie reçue (ex: la valeur de l'achat en EUR)
            if isinstance(payment_info, dict):
                df.at[idx, 'Received Currency'] = str(payment_info.get('Received Currency', 'EUR'))
                df.at[idx, 'Received Amount'] = str(payment_info.get('Received Amount', '0'))
            
            # Pour une vente (sell), le montant envoyé (la crypto) doit être positif dans le format RFI
            try:
                sent_amt = Decimal(row['Sent Amount'])
                if sent_amt < 0:
                    df.at[idx, 'Sent Amount'] = str(abs(sent_amt))
            except (ValueError, Exception):
                pass
                
            reclassified_count += 1
            print(f"✅ [RECLASSIFIED] {refid} : Transfert -> Vente ({df.at[idx, 'Received Amount']} {df.at[idx, 'Received Currency']})")

    # Sauvegarde du nouveau fichier RFI
    df.to_csv(output_file, index=False)
    print(f"\n🏁 Terminé. {reclassified_count} transaction(s) reclassée(s).")
    print(f"📂 Fichier créé : {output_file}")

if __name__ == "__main__":
    main()