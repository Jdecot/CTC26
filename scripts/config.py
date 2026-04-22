from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "Data"

# Dossiers de données
DIR_0_ORIGINAL = DATA_DIR / "0_original_trade_files"
DIR_1_RFI = DATA_DIR / "1_ready_for_ingest"
DIR_2_AS = DATA_DIR / "2_account_situation"
DIR_3_ENRICHED = DATA_DIR / "3_enriched_as"
DIR_4_COMPUTED = DATA_DIR / "4_computed_as"
DIR_5_TAXABLE = DATA_DIR / "5_taxable_trades_as"
DIR_OTHER = DATA_DIR / "other"
DIR_KRAKEN_PRICES = Path("D:/Data_crypto_tax_calculator/Kraken_History_Update_merged")
DIR_EXCEL = DATA_DIR / "excel"

# Fichiers spécifiques
FILE_KRAKEN_ALL_TRADES = DIR_0_ORIGINAL / "kraken_all_trades.csv"
FILE_CRYPTOCOM_2023 = DIR_0_ORIGINAL / "cryptocom_2023_ready_for_ingest.csv"
FILE_BITMART_2024 = DIR_0_ORIGINAL / "bitmart_2024.csv"

FILE_ALL_TRADES = DIR_1_RFI / "all_trades.csv"
FILE_ACCOUNT_SITUATION = DIR_2_AS / "account_situation.csv"
FILE_AS_WITH_PRICES = DIR_3_ENRICHED / "as_with_crypto_prices.csv"
FILE_ES_WITH_FEES_WORTH = DIR_3_ENRICHED / "es_with_fees_worth.csv"
FILE_PRICE_DB = DIR_3_ENRICHED / "price_db.csv"

FILE_CRYPTO_POSITIONS = DIR_4_COMPUTED / "crypto_positions.csv"
FILE_COMPUTED_PV = DIR_4_COMPUTED / "computed_pv.csv"

FILE_TAXABLE_TRADES = DIR_5_TAXABLE / "taxable_trades.csv"

FILE_DEPOSIT_WITHDRAWAL = DIR_OTHER / "deposit_withdrawal.csv"

# Configuration des fichiers pour le merge
MERGE_CONFIG = {
    "cryptocom_2023_ready_for_ingest_date_reworked.csv" : "cryptocom_2023",
    "kraken_all_trades_ready_for_ingest.csv" : "kraken_all",
    "bitmart_2024.csv" : "bitmart_2024"
}
