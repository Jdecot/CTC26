import pandas as pd
import config
import module_global
from decimal import Decimal, InvalidOperation

def main():
    print(f"🚀 Calcul des valeurs en EUR pour chaque actif...")

    if not config.FILE_TAXABLE_EVENT_WITH_PRICES.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_TAXABLE_EVENT_WITH_PRICES} n'existe pas.")
        return

    # Chargement des données (tout en string pour Decimal)
    df = pd.read_csv(config.FILE_TAXABLE_EVENT_WITH_PRICES, dtype=str).fillna("")
    
    # Récupération des colonnes d'actifs via le module global
    crypto_cols = module_global.get_crypto_columns(df, include_stables=True)
    total_calculations = 0

    for crypto in crypto_cols:
        price_col = f"{crypto}_price"
        eur_col = f"{crypto}_eur"

        # On ne crée la colonne _eur que si on a une colonne de prix correspondante
        if price_col not in df.columns:
            continue

        def calculate_row_value(row):
            # On ne calcule la valeur que pour les événements imposables
            if str(row.get('is_taxable_event', '')).strip().upper() != 'TRUE':
                return ""

            qty_raw = str(row[crypto]).strip()
            price_raw = str(row[price_col]).strip()

            # Si l'une des deux cellules est vide ou NaN, on laisse vide
            if not qty_raw or qty_raw.lower() == "nan" or not price_raw or price_raw.lower() == "nan":
                return ""

            try:
                qty = Decimal(qty_raw)
                price = Decimal(price_raw)
                # Calcul : Quantité * Prix
                res = qty * price
                # Formatage sans notation scientifique
                return f"{res:f}"
            except (InvalidOperation, ValueError):
                return ""

        df[eur_col] = df.apply(calculate_row_value, axis=1)
        # On compte combien de valeurs ont été calculées (cellules non vides) dans cette colonne
        total_calculations += (df[eur_col] != "").sum()

    # Sauvegarde du résultat
    config.DIR_7_CALCULATE_FIAT_VALUES.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT_WITH_FIAT_VALUES, index=False)
    print(f"✅ Calcul terminé. {total_calculations} valeurs de positions calculées.")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT_WITH_FIAT_VALUES}")

if __name__ == "__main__":
    main()