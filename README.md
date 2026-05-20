
# 🪙 Calcul des Impôts Crypto - France (Méthode PTA)

Ce projet permet d'automatiser le calcul de la plus-value latente et imposable sur les actifs numériques selon la réglementation fiscale française.

### Calcul de la plus value officiel
La formule légale utilisée est :
**Plus ou moins-value brute = Prix de cession – [Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille]**

*   **Prix de cession** : Prix réel perçu lors de la vente, net de frais.
*   **Prix Total d'Acquisition (PTA)** : Somme des prix d'achats en monnaie fiat, ajustée après chaque vente.
*   **Valeur globale du portefeuille** : Somme des valeurs de tous les actifs détenus juste avant la cession.

---

## 🚀 Le Pipeline de Traitement

Le processus est décomposé en scripts numérotés exécutables via `main.py`.

### 1. Ingestion et Normalisation
*   **`1a_kraken_convert.py`** : Transforme le fichier `ledgers.csv` de Kraken en format standard (RFI). Il fusionne les lignes séparées (achat/vente) en une seule transaction.
*   **`1b0_raw_crypto_com_data_convert.py`** : ETL spécifique pour les exports de l'application Crypto.com.
*   **`1b_crypto_com_convert_date.py`** : Harmonise les formats de date pour les données Crypto.com.
*   **`1c_merge_and_sort_all_trades.py`** : Fusionne tous les fichiers de toutes les plateformes en un historique unique trié chronologiquement.
*   **`1d_normalize.py`** : Unifie les noms des actifs (ex: `XXBT` devient `BTC`) et nettoie les montants.

### 2. Situation du Portefeuille
*   **`2_create_account_situation.py`** : Calcule le solde de chaque actif après chaque transaction. Génère `account_situation.csv`.
*   **`2b_check_amount_quality.py`** : Vérifie la cohérence des soldes (détecte les soldes négatifs impossibles).

### 3. Identification Fiscale
*   **`3_identify_taxable_event.py`** : Marque les transactions qui constituent un événement imposable (échange Crypto vers Fiat).
*   **`4_list_required_prices.py`** : Liste tous les actifs et dates pour lesquels un prix en EUR est nécessaire pour calculer la valeur du portefeuille.

### 4. Collecte des Prix
*   **`5a_get_yfinance_prices.py`** : Récupère automatiquement les cours historiques via l'API Yahoo Finance.
*   **`5b_merge_prices.py`** : Fusionne les prix automatiques et les prix saisis manuellement.
*   **`5c_check_missing_price_in_price_db.py`** : Identifie les manques dans la base de données de prix.
*   **`5d_check_prices_quality_in_price_db.py`** : Vérifie la cohérence des prix (écarts anormaux entre sources).

### 5. Calcul des Valeurs et PTA
*   **`6a_add_price_to_taxable_event.py`** : Associe chaque actif détenu à son prix en EUR au moment des ventes.
*   **`6b_validate_taxable_prices.py`** : Valide que tous les actifs d'un événement imposable ont bien un prix.
*   **`7_calculate_fiat_values.py`** : Calcule la valeur en EUR de chaque ligne d'actif (Quantité * Prix).
*   **`8_calculate_wallet_values.py`** : Calcule la valeur globale du portefeuille avant et après chaque vente.
*   **`9_PTA_sell_ratio.py`** : Calcule le ratio de cession (Prix de cession / Valeur globale).
*   **`10_compute_PTA.py`** : Calcule le Prix Total d'Acquisition (PTA) courant et le montant du PTA à déduire pour la vente actuelle.
*   **`11_compute_pv.py`** : Calcule la plus value.

---

## 📁 Organisation des Données

Les données transitent par le dossier `/Data` suivant cette logique :
*   **`0_original_trade_files`** : Vos exports CSV bruts (Kraken, Crypto.com, etc.).
*   **`1_ready_for_ingest`** : Fichiers nettoyés et normalisés.
*   **`2_account_situation`** : L'historique des soldes par crypto.
*   **`3_taxable_event`** : Identification des ventes imposables.
*   **`5_get_prices`** : Base de données locale des prix EUR (`price_db.csv`).
*   **`10_compute_pta`** : Fichier final contenant tous les éléments pour la déclaration de plus-value.
*   **`excel`** : Export final formaté avec en-têtes colorés pour révision manuelle.

---

## 📚 Ressources et Liens Officiels

*   **BOI-RPPM-PVAMC-20-10** : Détail officiel du calcul des plus-values
*   **Économie Gouv** : Régime fiscal des cryptomonnaies
*   **Tutoriel vidéo** : Méthode de calcul expliquée

---

## 🛠️ Configuration

La configuration centrale se trouve dans `scripts/config.py` :
*   Mapping des IDs Kraken (`KRAKEN_CRYPTO_ID`).
*   Dates de début et de fin de collecte.
*   Définition des dossiers de données.

Le fichier `scripts/module_global.py` contient les constantes partagées (ex: `FIAT_CURRENCIES`) et les outils de formatage Excel.
