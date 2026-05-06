import subprocess, sys
from pathlib import Path
import pandas as pd
import os
import shutil

# Ajouter le dossier scripts au path pour pouvoir importer config
sys.path.append(str(Path(__file__).parent / "scripts"))
import module_global
import config

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"

scripts = [
    # "0_collect_kraken.py",
    "1a_kraken_convert.py",
    "1b0_raw_crypto_com_data_convert.py",
    "1b_crypto_com_convert_date.py", 
    "1c_merge_and_sort_all_trades.py",
    "1d_normalize.py",
    "2_create_account_situation.py",
    "2b_check_amount_quality.py",
    "3_identify_taxable_event.py",
    "4_list_required_prices.py",
    "5a_get_yfinance_prices.py",
    "5b_merge_prices.py",
    "5c_check_missing_price_in_price_db.py",
    "5d_check_prices_quality_in_price_db.py",
    "6a_add_price_to_taxable_event.py",
    "6b_validate_taxable_prices.py",
    "7_calculate_fiat_values.py",
    "8_calculate_wallet_values.py",
    "9_PTA_sell_ratio.py",
    "10_compute_PTA.py",
    "11_compute_pv.py"
]


def run_pipeline():
    """Exécute la suite de scripts."""
    for s in scripts:
        print(f"\n{'='*40}\n▶ {s}\n{'='*40}")
        r = subprocess.run([sys.executable, str(SCRIPTS_DIR / s)])
        if r.returncode != 0:
            print(f"❌ {s} a échoué")
            sys.exit(1)
    print("\n✅ Pipeline terminé avec succès !")



def export_all_csv_to_excel(source_dir, target_dir):
    """
    Scans the source directory for CSV files and converts them to Excel 
    using the convert_csv_to_excel helper function.
    """
    # 1. Cleanup target directory
    if target_dir.exists():
        # shutil.rmtree with ignore_errors handles locked files (e.g., OneDrive)
        shutil.rmtree(target_dir, ignore_errors=True)
        print(f"  🗑️ Cleaned up target directory: {target_dir}")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    processed_files_count = 0
    
    # 2. Iterate through directory tree
    for root, sub_dirs, files in os.walk(source_dir, topdown=True):
        # Exclude specific directories to prevent conflicts or infinite loops
        sub_dirs[:] = [d for d in sub_dirs if d.lower() not in ['excel', 'old', 'debug']]
        
        for file_name in files:
            if file_name.endswith('.csv'):
                current_csv_path = Path(root) / file_name
                
                # Maintain original folder structure in the target directory
                relative_file_path = current_csv_path.relative_to(source_dir)
                current_excel_path = target_dir / relative_file_path.with_suffix('.xlsx')
                
                # Execute single file conversion
                is_successful = module_global.convert_csv_to_excel(current_csv_path, current_excel_path)
                if is_successful:
                    processed_files_count += 1
    
    print(f"\n📊 Batch conversion finished: {processed_files_count} files processed.")

def main():
    run_pipeline()
    
    print("\n" + "="*40)
    print("📁 Export Excel")
    print("="*40)
    
    # Pass the required arguments from your config module
    export_all_csv_to_excel(config.DATA_DIR, config.DIR_EXCEL)

if __name__ == "__main__":
    main()