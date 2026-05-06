import pandas as pd
import config
import module_global

def identify_taxable_events(df):
    # Liste des monnaies Fiat
    fiat_currencies = module_global.FIAT_CURRENCIES
    
    def check_row(row):
        sent_cur = str(row['Normalized Sent Currency']).strip().upper()
        recv_cur = str(row['Normalized Received Currency']).strip().upper()
        
        # CAS 1 : Vente de Crypto contre Fiat
        # On vérifie qu'on reçoit du Fiat ET que ce qu'on a envoyé n'était PAS du fiat
        # ET qu'on a bien envoyé quelque chose (pour exclure les dépôts de cash)
        if recv_cur in fiat_currencies and sent_cur not in fiat_currencies and sent_cur not in ['', 'NAN']:
            if pd.to_numeric(row['Received Amount'], errors='coerce') > 0:
                return True
            
        return False

    # Création de la colonne
    df['is_taxable_event'] = df.apply(check_row, axis=1)
    
    return df

def main():
    # 1. Chargement de la situation de compte
    if not config.FILE_ACCOUNT_SITUATION.exists():
        print(f"❌ Erreur : Le fichier {config.FILE_ACCOUNT_SITUATION} est introuvable.")
        return

    print(f"🔍 Analyse des événements imposables dans : {config.FILE_ACCOUNT_SITUATION}")
    df = pd.read_csv(config.FILE_ACCOUNT_SITUATION, dtype=str)
    
    # 2. Identification des événements
    df = identify_taxable_events(df)
    
    # Réorganisation des colonnes (is_taxable_event sera placé avant les cryptos)
    df = module_global.reorder_columns(df)
    
    # 3. Création du dossier de sortie et export
    config.DIR_3_TAXABLE_EVENT.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.FILE_TAXABLE_EVENT, index=False)
    
    count = df['is_taxable_event'].sum()
    print(f"✅ Terminé : {count} événements imposables détectés.")
    print(f"📂 Fichier créé : {config.FILE_TAXABLE_EVENT}")

if __name__ == "__main__":
    main()
