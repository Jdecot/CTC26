import pandas as pd
import config
from decimal import Decimal

def main():
    print(f"🕵️  Audit approfondi du flux BTC...")

    if not config.FILE_ACCOUNT_SITUATION.exists():
        print(f"❌ Erreur : {config.FILE_ACCOUNT_SITUATION} introuvable.")
        return

    # Lecture du fichier de situation
    df = pd.read_csv(config.FILE_ACCOUNT_SITUATION, dtype=str)
    
    # Liste des variantes BTC à auditer
    btc_variants = ["BTC", "XXBT", "XXBT.F", "XXBT.B", "XBT.M", "XBT"]
    cols_found = [c for c in btc_variants if c in df.columns]
    
    if not cols_found:
        print("⚠️  Aucune colonne BTC trouvée dans le fichier.")
        return

    print(f"🔍 Colonnes analysées : {cols_found}")
    
    # On parcourt les lignes pour trouver où le solde (individuel ou total) blesse
    negative_found = False
    
    for idx, row in df.iterrows():
        total_btc = Decimal('0')
        details = []
        has_negative_variant = False
        
        for col in cols_found:
            val = Decimal(row[col]) if row[col] and row[col] != 'nan' else Decimal('0')
            total_btc += val
            if val < 0:
                has_negative_variant = True
            details.append(f"{col}: {val}")
        
        # On alerte si le TOTAL est négatif ou si une variante l'est
        if total_btc < -Decimal('0.00000001') or has_negative_variant:
            negative_found = True
            print(f"\n🚩 Anomalie détectée à la ligne {idx}")
            print(f"📅 Date      : {row['Date']}")
            print(f"🆔 Refid     : {row.get('refid', 'N/A')}")
            print(f"ℹ️  Type      : {row.get('Detected Type', 'N/A')} ({row.get('subtype', 'N/A')})")
            print(f"💰 Total BTC : {total_btc}")
            print(f"📊 Détails   : {' | '.join(details)}")
            print(f"⚓ Balance   : {row.get('Balance', 'N/A')} (Balance brute Kraken)")
            
            if total_btc >= 0 and has_negative_variant:
                print("💡 Analyse : C'est un transfert interne. Le total est positif, mais une variante est à découvert.")
            elif total_btc < 0:
                print("🚨 Analyse : Le solde TOTAL est négatif. Il manque une entrée ou les frais sont mal déduits.")

    print("\n" + "="*60)
    if not negative_found:
        print("✅ Aucun solde BTC négatif (total ou variantes) détecté.")
    else:
        print("⚠️  Examine les 'Refid' ci-dessus dans ton fichier original pour comprendre l'origine.")

if __name__ == "__main__":
    main()