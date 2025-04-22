# Documents officiels

### Calcul de la plus value officiel
https://www.economie.gouv.fr/cedef/regime-fiscal-cryptomonnaies

Fichier data Kraken : 
https://support.kraken.com/hc/fr/articles/360047543791-Downloadable-historical-market-data-time-and-sales-
https://drive.google.com/drive/folders/188O9xQjZTythjyLNes_5zfMEFaMbTT22
https://drive.google.com/file/d/1MsMtaVdTF1lET3C8LiSFPjg-hH76fTgo/view?pli=1


# Les fichiers data
    ledgers.csv : liste des transactions Kraken, fichier original
    kraken_ready_for_ingest.csv : liste des transactions Kraken, transformé par le premier ETL (kraken_convert.py)
    cryptocom_2023_ready_for_ingest.csv : liste des transactions crypto.com, fichier transformé
    export_for_check.csv : fichier peu important, utilisé pour débug
    deposit_withdrawal.csv : fichier recensant la liste des dépots et retraits effectués auprès des plateforms d'échange. 

# Les fichiers du programme
1_kraken_convert.py : 
Premier ETL, utilisé pour transformer un fichier de transactions Kraken (ledgers) en fichier ready_for_ingest.csv

kraken_convert_fct.py : 
fichier contenant les fonctions utilisées par kraken_convert.py

2_Create_account_situation.py :
Créer un fichier account situation avec la liste des cryptomonnaies détennus en portefeuille.
In : Prends en entrée un fichier ready_to_ingest, exemple : cryptocom_2023_ready_for_ingest.csv
Out : exporte un fichier account_situation : account_situation.csv

3_enrich_account_situation.py : 
Enrichis le fichier account_situation avec la valeur en euros des cryptomonnaies déténus à l'instant T. 

4_compute_situation.py : 
Va calculer la valeur en euro de chaque position à chaque instant de transaction. 
Calcule également la valeur totale du portefeuille à l'instant T. 

# Pipeline évolution des fichiers de data

1 - ledgers.csv : 
fichier brut des transactions kraken, tel que téléchargé directement sur kraken.com

2 - kraken_ready_for_ingest.csv : 
fichier ledgers.csv après transformation par 1_kraken_convert.py
Permet de réorganiser les lignes. 
Par exemple deux lignes représentant la même transaction (vendu BTC et reçu EUR), seront réunis en une ligne

3 - account_situation.csv : 
fichier kraken_ready_for_ingest après transformation par create_account_situation.py. 
Permet d'avoir une vision du compte à un instant T

4 - enriched_account_situation : 
fichier account_situation.csv après transformation par enrich_account_situation.py. 
Ajoute le prix des crypto détenus en portefeuille à chaque moment faisant l'objet d'une transaction. 
