import subprocess, sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent

scripts = ["1a_kraken_convert.py", "1b_crypto_com_convert_date.py", "1c_merge_and_sort_all_trades.py", "2_create_account_situation.py"]


def run_pipeline():
    """Exécute la suite de scripts."""
    for s in scripts:
        print(f"\n{'='*40}\n▶ {s}\n{'='*40}")
        r = subprocess.run([sys.executable, str(BASE_DIR / s)])
        if r.returncode != 0:
            print(f"❌ {s} a échoué")
            sys.exit(1)
    print("\n✅ Pipeline terminé avec succès !")


def show_holdings():
    """Lit la dernière ligne de account_situation.csv et affiche les holdings triés."""
    csv_path = BASE_DIR / "Data" / "2_account_situation" / "account_situation.csv"
    
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


def main():
    run_pipeline()
    show_holdings()


if __name__ == "__main__":
    main()