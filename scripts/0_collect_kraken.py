import base64
import csv
import hashlib
import hmac
import json
import os
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
import config


KRAKEN_API_URL = "https://api.kraken.com"
KRAKEN_PRIVATE_PATH = "/0/private/Ledgers"
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = config.DATA_DIR
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "0_collect_configs.json"

# Délai entre les appels API (en secondes) pour éviter le rate limit
API_DELAY_SECONDS = 2


def _kraken_signature(url_path: str, data: Dict[str, str], secret_b64: str) -> str:
    post_data = urllib.parse.urlencode(data)
    encoded = (data["nonce"] + post_data).encode()
    message = url_path.encode() + hashlib.sha256(encoded).digest()
    secret = base64.b64decode(secret_b64)
    mac = hmac.new(secret, message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()


def _parse_date_to_unix(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())



def _fetch_ledger_page(api_key: str, api_secret: str, start: int, end: int, ofs: int = 0) -> Dict[str, Any]:
    """
    Fetch one page of ledger entries from Kraken API.
    Returns the full response body.
    """
    nonce = str(int(time.time() * 1000))
    payload = {
        "nonce": nonce,
        "type": "all",
        "start": str(start),
        "end": str(end),
        "ofs": str(ofs),
    }
    headers = {
        "API-Key": api_key,
        "API-Sign": _kraken_signature(KRAKEN_PRIVATE_PATH, payload, api_secret),
    }

    response = requests.post(
        f"{KRAKEN_API_URL}{KRAKEN_PRIVATE_PATH}",
        headers=headers,
        data=payload,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    errors = body.get("error", [])
    if errors:
        raise RuntimeError(f"Kraken API returned errors: {errors}")

    return body


def _append_rows_to_csv(output_path: Path, rows: List[Dict[str, Any]]) -> None:
    """
    Ajoute des lignes à la fin du fichier CSV (sans réécrire l'en-tête si le fichier existe déjà).
    """
    fieldnames = [
        "source",
        "txid",
        "refid",
        "time",
        "type",
        "subtype",
        "aclass",
        "asset",
        "wallet",
        "amount",
        "fee",
        "balance",
    ]

    file_exists = output_path.exists() and output_path.stat().st_size > 0

    with output_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def collect_kraken_transactions() -> int:
    load_dotenv()
    
    # 1. Récupération des clés API
    api_key = os.getenv("KRAKEN_API_KEY", "").strip()
    api_secret = (
        os.getenv("KRAKEN_SECRET_KEY", "").strip()
        or os.getenv("KRAKEN_API_SECRET", "").strip()
    )
    if not api_key or not api_secret:
        raise RuntimeError(
            "Missing KRAKEN_API_KEY and secret key (KRAKEN_SECRET_KEY or KRAKEN_API_SECRET)."
        )

    # 2. Utilisation des constantes de config.py
    # On utilise des points . au lieu des crochets [] car c'est un module importé
    output_path = config.KRAKEN_COLLECT_OUTPUT_FILE
    start_unix = _parse_date_to_unix(config.KRAKEN_START_DATE)
    end_unix = _parse_date_to_unix(config.KRAKEN_END_DATE) + 86399

    # 3. Création du dossier si inexistant
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    existing_ids = set() 
    ofs = 0
    page_size = 50  
    total_new_rows = 0

    # On écrit l'en-tête immédiatement pour écraser l'ancien contenu
    fieldnames = [
        "source", "txid", "refid", "time", "type", "subtype", "aclass", 
        "asset", "wallet", "amount", "fee", "balance"
    ]
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    # Correction de l'affichage print ici aussi
    print(f"Fetching Kraken ledger from {config.KRAKEN_START_DATE} to {config.KRAKEN_END_DATE}...")

    while True:
        try:
            time.sleep(API_DELAY_SECONDS)
            body = _fetch_ledger_page(api_key, api_secret, start_unix, end_unix, ofs)
            ledger_map = body.get("result", {}).get("ledger", {})

            if not ledger_map:
                break

            new_rows = []
            for transaction_id, entry in ledger_map.items():
                if transaction_id in existing_ids:
                    continue
                existing_ids.add(transaction_id)


                new_rows.append({
                    "txid": transaction_id,
                    "refid": entry.get("refid", ""),
                    "time": entry.get("time", ""),
                    "type": entry.get("type", ""),
                    "subtype": entry.get("subtype", ""),
                    "aclass": entry.get("aclass", ""),
                    "asset": entry.get("asset", ""),
                    "wallet": entry.get("wallet", ""),
                    "amount": entry.get("amount", ""),
                    "fee": entry.get("fee", ""),
                    "balance": entry.get("balance", ""),
                })

            if new_rows:
                # On utilise 'a' ici car l'en-tête a déjà été créé par 'w' plus haut
                _append_rows_to_csv(output_path, new_rows)
                total_new_rows += len(new_rows)
                print(f"  Page {ofs//page_size + 1}: {len(new_rows)} transactions ajoutées")

            if len(ledger_map) < page_size:
                break
            ofs += page_size

        except RuntimeError as e:
            if "Rate limit exceeded" in str(e):
                print("Rate limit atteint ! Pause...")
                time.sleep(10)
                continue
            else:
                raise

    return total_new_rows

if __name__ == "__main__":
    total = collect_kraken_transactions()
    print(
        f"Completed: Step 0 - Collect Kraken data : {total} transactions totales"
    )