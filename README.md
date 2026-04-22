





# Documents officiels

### Calcul de la plus value officiel
https://www.economie.gouv.fr/cedef/regime-fiscal-cryptomonnaies

Détail (voir partie crypto en bas de la page): 
https://www.impots.gouv.fr/particulier/les-cessions-mobilieres

Plus ou moins-value brute = Prix de cession – [Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille]

Prix de cession : Prix réel perçu par le cédant lors de la cession. 
Le cas échéant, il doit être majoré de la soulte que le cédant a reçue lors de la cession ou minoré de la soulte qu’il a versée lors de cette même cession. Il est également réduit, sur justificatifs, des frais supportés par le cédant à l’occasion de cette cession.

les frais de transaction payés à la plateforme d’échange ou aux mineurs sont à considérer soit comme une réduction du prix de vente, soit comme une augmentation du prix d’acquisition.

Valeur globale du portefeuille au moment de la cession : 
La somme des valeurs, au moment de la cession, des différentes crypto détenus par le cédant AVANT de procéder à la cession. 

Le prix total d'acquisition :
Somme de tous les prix acquittés en monnaie ayant cours légal à l'occasion de l'ensemble des acquisitions de crypto réalisées avant la cession, et de la valeur des biens ou services, comprenant le cas échéant les soultes versées, fournis en contrepartie de ces acquisitions.

Vidéo youtube très bien expliqué sur la méthode de calcul : 
https://www.youtube.com/watch?v=yzjlPIZRPIQ&ab_channel=JulienGuilloux


Aide générale et non officiel :
https://www.blockpit.io/tax-guides/impot-crypto-france#:~:text=La%20vente%20de%20crypto%2Dactifs%20et%20de%20leurs%20droits%20en,agit%20d'un%20%C3%A9v%C3%A9nement%20imposable.

Fichier data Kraken : 
https://support.kraken.com/hc/fr/articles/360047543791-Downloadable-historical-market-data-time-and-sales-
https://drive.google.com/drive/folders/188O9xQjZTythjyLNes_5zfMEFaMbTT22
https://drive.google.com/file/d/1MsMtaVdTF1lET3C8LiSFPjg-hH76fTgo/view?pli=1

Fichier data Bitget pour CRO :
https://www.bitget.com/price/cronos/historical-data#download


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
