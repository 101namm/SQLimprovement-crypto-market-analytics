"""
Script de gestion de la base de données SQLite
Crée la base, importe les données et calcule les métriques
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuration
DB_PATH = "data/crypto_market.db"
SCHEMA_PATH = "sql/schema.sql"
RAW_DATA_DIR = "data/raw"


def create_database():
    """Crée la base de données et exécute le schéma SQL"""
    print("\n" + "="*60)
    print("  CRÉATION DE LA BASE DE DONNÉES")
    print("="*60 + "\n")
    
    # Suppression de l'ancienne base si elle existe
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("✓ Ancienne base supprimée")
    
    # Création de la nouvelle base
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lecture et exécution du schéma
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    conn.commit()
    
    print(f"✓ Base de données créée: {DB_PATH}")
    print("✓ Schéma appliqué")
    
    return conn


def import_cryptocurrencies(conn):
    """Importe les données des cryptomonnaies"""
    print("\n" + "-"*60)
    print(" IMPORT DES CRYPTOMONNAIES")
    print("-"*60 + "\n")
    
    # Lecture du CSV
    info_path = os.path.join(RAW_DATA_DIR, "crypto_info.csv")
    df = pd.read_csv(info_path)
    
    # Préparation des données
    df_insert = df[["id", "symbol", "name"]].copy()
    df_insert.columns = ["crypto_id", "symbol", "name"]
    
    # Insertion dans la base
    df_insert.to_sql("cryptocurrencies", conn, if_exists="append", index=False)
    
    print(f"✓ {len(df_insert)} cryptomonnaies importées")
    print(f"  Exemples: {', '.join(df_insert['symbol'].head(5).tolist())}")
    
    return df


def import_price_history(conn):
    """Importe l'historique des prix"""
    print("\n" + "-"*60)
    print(" IMPORT DE L'HISTORIQUE DES PRIX")
    print("-"*60 + "\n")
    
    # Lecture du CSV
    history_path = os.path.join(RAW_DATA_DIR, "price_history.csv")
    df = pd.read_csv(history_path)
    
    # Préparation des données
    df_insert = df[["crypto_id", "date", "price", "market_cap", "volume"]].copy()
    df_insert.columns = ["crypto_id", "date", "price_usd", "market_cap", "total_volume"]
    
    # Conversion des types
    df_insert["date"] = pd.to_datetime(df_insert["date"]).dt.date
    
    #Suppression des doublons (garde la dernière valeur)
    df_insert = df_insert.drop_duplicates(subset=["crypto_id", "date"], keep="last")
    
    print(f"  Lignes après nettoyage des doublons: {len(df_insert)}")
    
    # Insertion dans la base
    df_insert.to_sql("price_history", conn, if_exists="append", index=False)
    
    print(f"✓ {len(df_insert)} lignes de prix importées")
    print(f"  Période: {df_insert['date'].min()} → {df_insert['date'].max()}")
    
    return df_insert

def calculate_metrics(conn):
    """Calcule et importe les métriques (rendements, volatilité)"""
    print("\n" + "-"*60)
    print(" CALCUL DES MÉTRIQUES")
    print("-"*60 + "\n")
    
    # Lecture des prix depuis la base
    df = pd.read_sql_query("""
        SELECT crypto_id, date, price_usd, total_volume
        FROM price_history
        ORDER BY crypto_id, date
    """, conn)
    
    df["date"] = pd.to_datetime(df["date"])
    
    metrics_list = []
    
    # Calcul des métriques par crypto
    for crypto_id in df["crypto_id"].unique():
        df_crypto = df[df["crypto_id"] == crypto_id].copy()
        df_crypto = df_crypto.sort_values("date")
        
        # Calcul du rendement quotidien (en %)
        df_crypto["daily_return"] = df_crypto["price_usd"].pct_change() * 100
        
        # Calcul de la volatilité sur 7 jours (écart-type mobile)
        df_crypto["volatility_7d"] = df_crypto["daily_return"].rolling(window=7).std()
        
        # Calcul de la volatilité sur 30 jours
        df_crypto["volatility_30d"] = df_crypto["daily_return"].rolling(window=30).std()
        
        # Changement de volume sur 24h
        df_crypto["volume_change_24h"] = df_crypto["total_volume"].pct_change() * 100
        
        # Ajout des données dans la liste
        for idx, row in df_crypto.iterrows():
            if pd.notna(row["daily_return"]):  # Évite les NaN
                metrics_list.append({
                    "crypto_id": crypto_id,
                    "date": row["date"].date(),
                    "daily_return": row["daily_return"],
                    "volatility_7d": row["volatility_7d"],
                    "volatility_30d": row["volatility_30d"],
                    "volume_change_24h": row["volume_change_24h"]
                })
    
    # Conversion en DataFrame et insertion
    df_metrics = pd.DataFrame(metrics_list)
    
    # Remplacement des NaN par None pour SQLite
    df_metrics = df_metrics.where(pd.notna(df_metrics), None)
    
    df_metrics.to_sql("metrics", conn, if_exists="append", index=False)
    
    print(f"✓ {len(df_metrics)} métriques calculées et importées")
    print(f"  Métriques: daily_return, volatility_7d, volatility_30d, volume_change_24h")


def verify_data(conn):
    """Vérifie l'intégrité des données importées"""
    print("\n" + "-"*60)
    print(" VÉRIFICATION DES DONNÉES")
    print("-"*60 + "\n")
    
    cursor = conn.cursor()
    
    # Compte des enregistrements
    counts = {
        "cryptocurrencies": cursor.execute("SELECT COUNT(*) FROM cryptocurrencies").fetchone()[0],
        "price_history": cursor.execute("SELECT COUNT(*) FROM price_history").fetchone()[0],
        "metrics": cursor.execute("SELECT COUNT(*) FROM metrics").fetchone()[0]
    }
    
    for table, count in counts.items():
        print(f"  {table}: {count:,} lignes")
    
    # Dates disponibles
    date_range = cursor.execute("""
        SELECT MIN(date) as min_date, MAX(date) as max_date 
        FROM price_history
    """).fetchone()
    
    print(f"\n  Période de données: {date_range[0]} → {date_range[1]}")
    
    # Exemple de données via la vue
    print("\n  Aperçu via vw_price_analysis:")
    df_sample = pd.read_sql_query("""
        SELECT * FROM vw_price_analysis 
        LIMIT 5
    """, conn)
    print(df_sample.to_string(index=False))
    
    print("\n✓ Vérification terminée - Base de données opérationnelle!")


def run_sample_queries(conn):
    """Exécute quelques requêtes d'exemple pour vérifier que tout fonctionne"""
    print("\n" + "-"*60)
    print(" TEST DES REQUÊTES SQL")
    print("-"*60 + "\n")
    
    # Requête 1: Top 5 cryptos par market cap
    print("Top 5 cryptos par market cap actuel:")
    df = pd.read_sql_query("""
        SELECT 
            c.symbol,
            c.name,
            ROUND(ph.market_cap / 1000000000, 2) as market_cap_billions,
            ROUND(ph.price_usd, 2) as price
        FROM price_history ph
        JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
        WHERE ph.date = (SELECT MAX(date) FROM price_history)
        ORDER BY ph.market_cap DESC
        LIMIT 5
    """, conn)
    print(df.to_string(index=False))
    
    # Requête 2: Crypto la plus volatile
    print("\n\nTop 3 cryptos les plus volatiles (30j):")
    df = pd.read_sql_query("""
        SELECT 
            c.symbol,
            ROUND(AVG(m.volatility_30d), 2) as avg_volatility
        FROM metrics m
        JOIN cryptocurrencies c ON m.crypto_id = c.crypto_id
        WHERE m.volatility_30d IS NOT NULL
        GROUP BY c.symbol
        ORDER BY avg_volatility DESC
        LIMIT 3
    """, conn)
    print(df.to_string(index=False))
    
    print("\n✓ Requêtes exécutées avec succès!")


def main():
    """Fonction principale"""
    try:
        # Création de la base
        conn = create_database()
        
        # Import des données
        import_cryptocurrencies(conn)
        import_price_history(conn)
        calculate_metrics(conn)
        
        # Vérifications
        verify_data(conn)
        run_sample_queries(conn)
        
        # Fermeture de la connexion
        conn.close()
        
        print("\n" + "="*60)
        print(" BASE DE DONNÉES CRÉÉE ET PEUPLÉE AVEC SUCCÈS!")
        print("="*60)
        print(f"\n Emplacement: {DB_PATH}")
        print("\n Prochaine étape: python src/analysis.py")
        print("   ou explore avec: sqlite3 data/crypto_market.db\n")
        
    except Exception as e:
        print(f"\n ERREUR: {e}")
        raise


if __name__ == "__main__":
    main()
