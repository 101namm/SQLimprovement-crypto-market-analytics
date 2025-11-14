"""
Script de collecte de données crypto via l'API CoinGecko
Récupère les prix historiques et informations des principales cryptomonnaies
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import os

# Configuration
API_BASE_URL = "https://api.coingecko.com/api/v3"
DATA_DIR = "data/raw"

# Crypto à suivre
TOP_CRYPTOS = [
    "bitcoin",
    "ethereum",
    "binancecoin",
    "algorand",
    "cosmos",
]

# Nombre de jours d'historique à récupérer
DAYS_OF_HISTORY = 90


def create_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    print(f"✓ Dossiers créés : {DATA_DIR}")


def get_crypto_info(crypto_id):
    """
    Récupère les informations de base d'une crypto
    
    Args:
        crypto_id (str): ID de la crypto sur CoinGecko
    
    Returns:
        dict: Informations de la crypto
    """
    url = f"{API_BASE_URL}/coins/{crypto_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "false",
        "developer_data": "false"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "id": data["id"],
            "symbol": data["symbol"].upper(),
            "name": data["name"],
            "market_cap_rank": data.get("market_cap_rank"),
            "current_price": data["market_data"]["current_price"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"],
            "total_volume": data["market_data"]["total_volume"]["usd"],
        }
    except requests.exceptions.RequestException as e:
        print(f"✗ Erreur lors de la récupération de {crypto_id}: {e}")
        return None


def get_historical_prices(crypto_id, days=90):
    """
    Récupère l'historique des prix d'une crypto
    
    Args:
        crypto_id (str): ID de la crypto sur CoinGecko
        days (int): Nombre de jours d'historique
    
    Returns:
        pd.DataFrame: DataFrame avec l'historique des prix
    """
    url = f"{API_BASE_URL}/coins/{crypto_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Conversion en DataFrame
        df = pd.DataFrame({
            "timestamp": [item[0] for item in data["prices"]],
            "price": [item[1] for item in data["prices"]],
            "market_cap": [item[1] for item in data["market_caps"]],
            "volume": [item[1] for item in data["total_volumes"]]
        })
        
        # Conversion timestamp -> date
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms").dt.date
        df["crypto_id"] = crypto_id
        
        # Réorganisation des colonnes
        df = df[["crypto_id", "date", "price", "market_cap", "volume"]]
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Erreur lors de la récupération de l'historique de {crypto_id}: {e}")
        return pd.DataFrame()


def collect_all_data():
    """
    Collecte toutes les données pour les cryptos configurées
    """
    print("\n" + "="*60)
    print("🚀 DÉBUT DE LA COLLECTE DE DONNÉES CRYPTO")
    print("="*60 + "\n")
    
    create_directories()
    
    # Collecte des infos de base
    crypto_info_list = []
    historical_data_list = []
    
    for i, crypto_id in enumerate(TOP_CRYPTOS, 1):
        print(f"[{i}/{len(TOP_CRYPTOS)}] Traitement de {crypto_id}...")
        
        # Info de base
        info = get_crypto_info(crypto_id)
        if info:
            crypto_info_list.append(info)
            print(f"  ✓ Info récupérée: {info['name']} ({info['symbol']})")
        
        # Historique des prix
        historical = get_historical_prices(crypto_id, DAYS_OF_HISTORY)
        if not historical.empty:
            historical_data_list.append(historical)
            print(f"  ✓ Historique récupéré: {len(historical)} jours")
        
        # Pause pour respecter les limites de l'API (rate limiting)
        if i < len(TOP_CRYPTOS):
            time.sleep(17.5) #Pour pas trop surcharger coingeeko vu que c'est une api gratuite mais pouvoir recup des crypto en polus grand nombre
    
    # Sauvegarde des données
    print("\n" + "-"*60)
    print("💾 SAUVEGARDE DES DONNÉES")
    print("-"*60 + "\n")
    
    # DataFrame des infos
    if crypto_info_list:
        df_info = pd.DataFrame(crypto_info_list)
        info_path = os.path.join(DATA_DIR, "crypto_info.csv")
        df_info.to_csv(info_path, index=False)
        print(f"✓ Infos sauvegardées: {info_path}")
        print(f"  → {len(df_info)} cryptos")
    
    # DataFrame de l'historique
    if historical_data_list:
        df_historical = pd.concat(historical_data_list, ignore_index=True)
        historical_path = os.path.join(DATA_DIR, "price_history.csv")
        df_historical.to_csv(historical_path, index=False)
        print(f"✓ Historique sauvegardé: {historical_path}")
        print(f"  → {len(df_historical)} lignes de données")
    
    # Métadonnées de la collecte
    metadata = {
        "collection_date": datetime.now().isoformat(),
        "cryptos_count": len(crypto_info_list),
        "days_of_history": DAYS_OF_HISTORY,
        "data_points": len(df_historical) if historical_data_list else 0,
        "cryptos": TOP_CRYPTOS
    }
    
    metadata_path = os.path.join(DATA_DIR, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Métadonnées sauvegardées: {metadata_path}")
    
    print("\n" + "="*60)
    print("✅ COLLECTE TERMINÉE AVEC SUCCÈS!")
    print("="*60 + "\n")
    
    return df_info, df_historical


def main():
    """Fonction principale"""
    try:
        df_info, df_historical = collect_all_data()
        
        # Affichage d'un aperçu
        print("\n📊 APERÇU DES DONNÉES COLLECTÉES\n")
        
        print("Top 5 cryptos par market cap:")
        print(df_info.nlargest(5, "market_cap")[["name", "symbol", "current_price", "market_cap"]])
        
        print("\n" + "-"*60)
        print("Dernières données de prix:")
        print(df_historical.tail(10))
        
        print("\n" + "="*60)
        print("✨ Prochaine étape: python src/database.py")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        raise


if __name__ == "__main__":
    main()
