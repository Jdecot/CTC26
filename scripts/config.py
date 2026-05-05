from pathlib import Path


# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "Data"

# Dossiers de données
DIR_0_ORIGINAL = DATA_DIR / "0_original_trade_files"
DIR_1_RFI = DATA_DIR / "1_ready_for_ingest"
DIR_2_AS = DATA_DIR / "2_account_situation"
DIR_3_TAXABLE_EVENT = DATA_DIR / "3_taxable_event"
DIR_4_REQUIRED_PRICES = DATA_DIR / "4_required_prices"
DIR_5_GET_PRICES = DATA_DIR / "5_get_prices"
DIR_6_TAXABLE_EVENT_WITH_PRICES = DATA_DIR / "6_add_price_to_taxable_event"
DIR_EXCEL = DATA_DIR / "excel"

# Fichiers spécifiques
FILE_KRAKEN_ALL_TRADES = DIR_0_ORIGINAL / "kraken_all_trades.csv"
FILE_CRYPTOCOM_2023 = DIR_0_ORIGINAL / "cryptocom_2023_ready_for_ingest.csv"
FILE_CRYPTOCOM_REWORKED_SOURCE = DIR_0_ORIGINAL / "cryptoapp_2023_reworked.csv"
FILE_CRYPTOCOM_RAW = DIR_0_ORIGINAL / "crypto_enregistrement_transactions_20240218_212641.csv"
FILE_CRYPTOCOM_RFI_V2 = DIR_1_RFI / "cryptocom_2023_ready_for_ingest.csv"
FILE_BITMART_2024 = DIR_0_ORIGINAL / "bitmart_2024.csv"

FILE_ALL_TRADES = DIR_1_RFI / "all_trades.csv"
FILE_ALL_TRADES_NORMALIZED = DIR_1_RFI / "all_trades_normalized.csv"
FILE_ACCOUNT_SITUATION = DIR_2_AS / "account_situation.csv"
FILE_TAXABLE_EVENT = DIR_3_TAXABLE_EVENT / "taxable_event.csv"
FILE_REQUIRED_PRICES = DIR_4_REQUIRED_PRICES / "required_prices.csv"
FILE_GET_YFINANCE_PRICES = DIR_5_GET_PRICES / "get_yfinance_prices.csv"
FILE_GET_MANUAL_PRICES = DIR_5_GET_PRICES / "get_manual_prices.csv"
FILE_MERGED_PRICES = DIR_5_GET_PRICES / "price_db.csv"
FILE_TAXABLE_EVENT_WITH_PRICES = DIR_6_TAXABLE_EVENT_WITH_PRICES / "taxable_events_with_price.csv"

# Configuration des fichiers pour le merge
MERGE_CONFIG = {
    "cryptocom_2023_ready_for_ingest_date_reworked.csv" : "cryptocom_2023",
    "kraken_all_trades_ready_for_ingest.csv" : "kraken_all",
    "bitmart_2024.csv" : "bitmart_2024",
    "tangem_rfi.csv" : "tangem_rfi"
}




# --- CONFIGURATION COLLECTE KRAKEN ---
KRAKEN_START_DATE = "2023-01-01"
KRAKEN_END_DATE = "2026-05-01"
# On utilise le chemin déjà défini DIR_0_ORIGINAL pour la cohérence
KRAKEN_COLLECT_OUTPUT_FILE = DIR_0_ORIGINAL / "kraken_all_trades.csv"



KRAKEN_CRYPTO_ID = {
# --- BITCOIN & ETHEREUM ---
    "XXBT": "BTC", "XXBT.F": "BTC", "XXBT.B": "BTC", "XBT.M": "BTC", "XBT": "BTC",
    "XETH": "ETH", "XETH.F": "ETH", "ETH2.S": "ETH", "ETH": "ETH", "XETH.B" : "ETH",
    
    # --- FIAT & STABLES ---
    "ZEUR": "EUR", "EUR": "EUR", "ZUSD": "USD", "USD": "USD",
    "USDC": "USDC", "USDC.F": "USDC", "USDC.M": "USDC",
    "USDT": "USDT", "USDT.F": "USDT",
    
    # --- ALTCOINS (Vérifiés et validés) ---
    "LINK": "LINK",
    "EIGEN": "EIGEN",
    "TRUMP": "TRUMP",
    "ADA": "ADA", "ADA.F": "ADA", "ADA.S": "ADA",
    "SOL": "SOL", "SOL.F": "SOL", "SOL.S": "SOL", "SOL03.S": "SOL",
    "TRX": "TRX", "TRX.F": "TRX",
    "INJ": "INJ", "INJ.F": "INJ", "INJ.B": "INJ",
    "MATIC": "MATIC", "MATIC.S": "MATIC", "MATIC04.S": "MATIC", "MATIC.F" : "MATIC",
    "POL.F": "POL", "POL": "POL",
    "XXDG": "DOGE", "DOGE": "DOGE",
    "XXRP": "XRP", "XRP": "XRP",
    "JUP": "JUP", "TAO": "TAO", "NEAR": "NEAR", "PEPE": "PEPE",
    "ALGO": "ALGO", "SUI": "SUI", "ONDO": "ONDO", "BIT": "BIT",
    "ANKR": "ANKR", "GALA": "GALA", "DOT": "DOT", "QNT": "QNT",
    "ATOM": "ATOM", "AVAX": "AVAX", "PYTH": "PYTH", "FIL": "FIL",
    "GRT": "GRT", "FET": "FET", "RNDR": "RNDR", "ARB": "ARB",
    "ASTR": "ASTR", "ORCA": "ORCA", "ICP": "ICP", "OP": "OP", "IMX": "IMX",
    
    # --- ACTIF VIRTUEL ---
    "DUST_VIRTUAL": "DUST_VIRTUAL"
}
