import subprocess, sys
from pathlib import Path
import pandas as pd
import os

# Ajouter le dossier scripts au path pour pouvoir importer config
sys.path.append(str(Path(__file__).parent / "scripts"))
import config

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "scripts"

scripts = [
    "1a_kraken_convert.py",
    "1b_crypto_com_convert_date.py", 
    "1c_merge_and_sort_all_trades.py",
    "2_create_account_situation.py",
    # "3_enrich_account_situation.py",
    # "4a_compute_crypto_positions.py",
    # "4b_compute_pv.py",
    # "5_extract_taxable_trades.py"
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


def show_holdings():
    """Lit la dernière ligne de account_situation.csv et affiche les holdings triés."""
    csv_path = config.FILE_ACCOUNT_SITUATION
    
    if not csv_path.exists():
        print(f"⚠️  Fichier non trouvé : {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    if df.empty:
        print("⚠️  Le fichier account_situation.csv est vide")
        return
    
    last_row = df.iloc[-1]
    
    # Convertir toutes les valeurs en numérique (les erreurs deviennent NaN)
    holdings = {}
    for col in df.columns:
        try:
            val = float(last_row[col])
            if val > 0:
                holdings[col] = val
        except (ValueError, TypeError):
            # Ignore les colonnes non numériques ou valeurs non convertibles
            pass
    
    sorted_holdings = dict(sorted(holdings.items(), key=lambda x: x[1], reverse=True))
    
    print("\n" + "="*40)
    print("📊 HOLDINGS (dernière ligne)")
    print("="*40)
    for crypto, qty in sorted_holdings.items():
        print(f"  {crypto}: {qty}")


def export_all_csv_to_excel():
    """Convertit tous les CSV du dossier Data en fichiers Excel dans Data/excel."""
    excel_dir = config.DIR_EXCEL
    
    # Vider le dossier excel s'il existe
    if excel_dir.exists():
        import shutil
        # Utiliser ignore_errors=True pour éviter les blocages liés à OneDrive ou des fichiers ouverts
        shutil.rmtree(excel_dir, ignore_errors=True)
        print(f"  🗑️ Nettoyage du dossier {excel_dir} (les fichiers verrouillés sont conservés)")
    
    excel_dir.mkdir(parents=True, exist_ok=True)
    
    csv_count = 0
    for root, dirs, files in os.walk(config.DATA_DIR, topdown=True):
        # Ignorer le dossier de destination 'excel' et les dossiers 'old' pour éviter les conflits d'accès
        dirs[:] = [d for d in dirs if d.lower() not in ['excel', 'old']]
        for file in files:
            if file.endswith('.csv'):
                csv_path = Path(root) / file
                # Calculer le chemin relatif pour préserver la structure
                rel_path = csv_path.relative_to(config.DATA_DIR)
                excel_path = excel_dir / rel_path.with_suffix('.xlsx')
                
                # Créer les sous-dossiers si nécessaire
                excel_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    df = pd.read_csv(csv_path, sep=',')
                    df.to_excel(excel_path, index=False)
                    csv_count += 1
                    print(f"  ✓ {rel_path} -> {excel_path.relative_to(BASE_DIR)}")
                except Exception as e:
                    print(f"  ✗ Erreur lors de la conversion de {rel_path}: {e}")
    
    print(f"\n📊 {csv_count} fichiers CSV convertis en Excel dans Data/excel/")


def main():
    run_pipeline()
    show_holdings()
    print("\n" + "="*40)
    print("📁 Export Excel")
    print("="*40)
    export_all_csv_to_excel()


if __name__ == "__main__":
    main()