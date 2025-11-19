"""
Script d'analyse et de visualisation des données crypto
Exécute les requêtes SQL et génère des graphiques
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Configuration
DB_PATH = "data/crypto_market.db"
QUERIES_PATH = "sql/queries.sql"
VIZ_DIR = "visualizations"

# Style des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def create_viz_directory():
    """Crée le dossier pour les visualisations"""
    os.makedirs(VIZ_DIR, exist_ok=True)


def connect_db():
    """Établit la connexion à la base de données"""
    return sqlite3.connect(DB_PATH)


def execute_query(conn, query_name, query):
    """
    Exécute une requête SQL et retourne le résultat
    
    Args:
        conn: Connexion à la base
        query_name: Nom de la requête (pour affichage)
        query: Requête SQL à exécuter
    
    Returns:
        pd.DataFrame: Résultat de la requête
    """
    print(f"\n{'='*60}")
    print(f" {query_name}")
    print('='*60)
    
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))
    
    return df


def plot_price_evolution(conn):
    """Graphique de l'évolution des prix (normalisé à 100 pour comparaison)"""
    print("\n\n Génération: Évolution des prix...")
    
    # Récupère TOUTES les cryptos disponibles dynamiquement
    query = """
    SELECT 
        c.symbol,
        ph.date,
        ph.price_usd
    FROM price_history ph
    JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
    ORDER BY ph.date, c.symbol
    """
    
    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    
    # Normalisation à 100 pour chaque crypto (base = premier jour)
    df_normalized = df.copy()
    for symbol in df['symbol'].unique():
        mask = df['symbol'] == symbol
        first_price = df.loc[mask, 'price_usd'].iloc[0]
        df_normalized.loc[mask, 'price_normalized'] = (df.loc[mask, 'price_usd'] / first_price) * 100
    
    plt.figure(figsize=(14, 8))
    
    for symbol in df_normalized['symbol'].unique():
        df_symbol = df_normalized[df_normalized['symbol'] == symbol]
        plt.plot(df_symbol['date'], df_symbol['price_normalized'], 
                label=symbol, linewidth=2.5, marker='o', markersize=2, alpha=0.8)
    
    plt.title('Évolution des Prix (Base 100)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Performance (Base 100 = premier jour)', fontsize=12)
    plt.axhline(y=100, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Base')
    plt.legend(loc='best', fontsize=11, framealpha=0.9)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '01_price_evolution.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def plot_volatility_comparison(conn):
    """Comparaison des volatilités"""
    print("\n Génération: Comparaison des volatilités...")
    
    query = """
    SELECT 
        c.symbol,
        c.name,
        ROUND(AVG(m.volatility_30d), 2) as avg_volatility
    FROM cryptocurrencies c
    JOIN metrics m ON c.crypto_id = m.crypto_id
    WHERE m.volatility_30d IS NOT NULL
    GROUP BY c.symbol, c.name
    ORDER BY avg_volatility DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    plt.figure(figsize=(12, 8))
    colors = sns.color_palette("RdYlGn_r", len(df))
    
    bars = plt.barh(df['symbol'], df['avg_volatility'], color=colors)
    
    plt.title('Volatilité Moyenne (30 jours) par Crypto', fontsize=16, fontweight='bold')
    plt.xlabel('Volatilité (%)', fontsize=12)
    plt.ylabel('Crypto', fontsize=12)
    plt.grid(True, alpha=0.3, axis='x')
    
    # Ajout des valeurs sur les barres
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}%',
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '02_volatility_comparison.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def plot_correlation_heatmap(conn):
    """Heatmap des corrélations entre cryptos"""
    print("\n Génération: Heatmap de corrélations...")
    
    query = """
    SELECT 
        c.symbol,
        ph.date,
        ph.price_usd
    FROM price_history ph
    JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
    ORDER BY c.symbol, ph.date
    """
    
    df = pd.read_sql_query(query, conn)
    
    # Pivot pour avoir les cryptos en colonnes
    df_pivot = df.pivot(index='date', columns='symbol', values='price_usd')
    
    # Calcul des rendements quotidiens
    returns = df_pivot.pct_change().dropna()
    
    # Matrice de corrélation
    corr_matrix = returns.corr()
    
    # Taille dynamique selon nombre de cryptos
    n_cryptos = len(corr_matrix)
    fig_size = max(10, n_cryptos * 2)
    
    plt.figure(figsize=(fig_size, fig_size))
    
    # Afficher la heatmap complète (pas de masque)
    sns.heatmap(corr_matrix, 
                annot=True, 
                fmt='.2f', 
                cmap='coolwarm', 
                center=0, 
                square=True,
                linewidths=2,
                linecolor='white',
                cbar_kws={"shrink": 0.8},
                vmin=-1, 
                vmax=1)
    
    plt.title('Corrélations des Rendements entre Cryptos', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '03_correlation_heatmap.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def plot_market_dominance(conn):
    """Camembert de la dominance du marché"""
    print("\n Génération: Market dominance...")
    
    query = """
    WITH latest_marketcap AS (
        SELECT 
            c.symbol,
            c.name,
            ph.market_cap
        FROM cryptocurrencies c
        JOIN price_history ph ON c.crypto_id = ph.crypto_id
        WHERE ph.date = (SELECT MAX(date) FROM price_history)
    )
    SELECT 
        symbol,
        name,
        market_cap / 1000000000 as market_cap_billions
    FROM latest_marketcap
    ORDER BY market_cap DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    plt.figure(figsize=(14, 10))
    colors = sns.color_palette('Set3', len(df))
    
    # Fonction pour formater les labels avec pourcentage
    def make_autopct(values):
        def my_autopct(pct):
            if pct > 2:  # Affiche le % seulement si > 2%
                return f'{pct:.1f}%'
            return ''
        return my_autopct
    
    wedges, texts, autotexts = plt.pie(
        df['market_cap_billions'], 
        labels=None,  # Pas de labels directs sur le pie
        autopct=make_autopct(df['market_cap_billions']),
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11, 'fontweight': 'bold'},
        pctdistance=0.85
    )
    
    plt.title('Market Cap Dominance', fontsize=16, fontweight='bold', pad=20)
    
    # Légende claire à côté avec les noms complets
    legend_labels = [
        f"{row['symbol']}: {row['name']}\n(${row['market_cap_billions']:.1f}B)" 
        for _, row in df.iterrows()
    ]
    plt.legend(
        legend_labels, 
        loc='center left', 
        bbox_to_anchor=(1, 0.5), 
        fontsize=10,
        frameon=True,
        shadow=True
    )
    
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '04_market_dominance.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def plot_performance_comparison(conn):
    """Comparaison des performances sur 30 jours"""
    print("\n Génération: Comparaison des performances...")
    
    query = """
    SELECT 
        c.symbol,
        ROUND(
            (latest.price_usd - first.price_usd) / first.price_usd * 100, 
            2
        ) as performance_30d
    FROM cryptocurrencies c
    JOIN (
        SELECT crypto_id, price_usd
        FROM price_history
        WHERE date = (SELECT MAX(date) FROM price_history)
    ) latest ON c.crypto_id = latest.crypto_id
    JOIN (
        SELECT crypto_id, price_usd
        FROM price_history
        WHERE date = (SELECT date(MAX(date), '-30 days') FROM price_history)
    ) first ON c.crypto_id = first.crypto_id
    ORDER BY performance_30d DESC
    """
    
    df = pd.read_sql_query(query, conn)
    
    plt.figure(figsize=(12, 8))
    
    # Couleurs: vert pour positif, rouge pour négatif
    colors = ['green' if x > 0 else 'red' for x in df['performance_30d']]
    
    bars = plt.barh(df['symbol'], df['performance_30d'], color=colors, alpha=0.7)
    
    plt.title('Performance sur 30 jours (%)', fontsize=16, fontweight='bold')
    plt.xlabel('Performance (%)', fontsize=12)
    plt.ylabel('Crypto', fontsize=12)
    plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    plt.grid(True, alpha=0.3, axis='x')
    
    # Ajout des valeurs
    for i, bar in enumerate(bars):
        width = bar.get_width()
        label_x_pos = width + 0.5 if width > 0 else width - 0.5
        plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}%',
                ha='left' if width > 0 else 'right', 
                va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '05_performance_30d.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def plot_volume_analysis(conn):
    """Analyse des volumes de trading - toutes les cryptos disponibles"""
    print("\n Génération: Analyse des volumes...")
    
    # Récupère TOUTES les cryptos disponibles
    query = """
    SELECT 
        c.symbol,
        ph.date,
        ph.total_volume / 1000000000 as volume_billions
    FROM price_history ph
    JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
    ORDER BY ph.date, c.symbol
    """
    
    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    
    symbols = sorted(df['symbol'].unique())
    n_symbols = len(symbols)
    
    # Configuration de la grille selon le nombre de cryptos
    if n_symbols <= 2:
        n_rows, n_cols = 1, n_symbols
        figsize = (8 * n_symbols, 6)
    elif n_symbols <= 4:
        n_rows, n_cols = 2, 2
        figsize = (16, 10)
    elif n_symbols <= 6:
        n_rows, n_cols = 2, 3
        figsize = (18, 10)
    else:
        n_rows, n_cols = 3, 3
        figsize = (18, 14)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    
    # Convertir en liste 1D si nécessaire
    if n_symbols == 1:
        axes = [axes]
    else:
        axes = axes.ravel() if n_symbols > 1 else [axes]
    
    colors = sns.color_palette("husl", n_symbols)
    
    for i, symbol in enumerate(symbols):
        if i >= len(axes):
            break
            
        df_symbol = df[df['symbol'] == symbol]
        
        axes[i].plot(df_symbol['date'], df_symbol['volume_billions'], 
                    linewidth=2, color=colors[i], alpha=0.8)
        axes[i].fill_between(df_symbol['date'], df_symbol['volume_billions'], 
                             alpha=0.3, color=colors[i])
        axes[i].set_title(f'{symbol} - Volume de Trading', fontsize=12, fontweight='bold')
        axes[i].set_xlabel('Date', fontsize=10)
        axes[i].set_ylabel('Volume (Milliards $)', fontsize=10)
        axes[i].grid(True, alpha=0.3)
        axes[i].tick_params(axis='x', rotation=45)
    
    # Cache les axes inutilisés
    for i in range(n_symbols, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle('Évolution des Volumes de Trading', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filepath = os.path.join(VIZ_DIR, '06_volume_analysis.png')
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Sauvegardé: {filepath}")


def run_all_analyses():
    """Exécute toutes les analyses et génère tous les graphiques"""
    print("\n" + "="*60)
    print(" DÉBUT DES ANALYSES SQL ET VISUALISATIONS")
    print("="*60 + "\n")
    
    create_viz_directory()
    conn = connect_db()
    
    # Lecture du fichier de requêtes
    with open(QUERIES_PATH, 'r') as f:
        queries_content = f.read()
    
    # Extraction de quelques requêtes clés à afficher
    queries = {
        "Top Performers (30j)": """
            SELECT 
                c.symbol,
                c.name,
                ROUND((latest.price_usd - first.price_usd) / first.price_usd * 100, 2) as perf_30d,
                ROUND(latest.price_usd, 2) as prix_actuel
            FROM cryptocurrencies c
            JOIN (SELECT crypto_id, price_usd FROM price_history 
                  WHERE date = (SELECT MAX(date) FROM price_history)) latest 
                  ON c.crypto_id = latest.crypto_id
            JOIN (SELECT crypto_id, price_usd FROM price_history 
                  WHERE date = (SELECT date(MAX(date), '-30 days') FROM price_history)) first 
                  ON c.crypto_id = first.crypto_id
            ORDER BY perf_30d DESC LIMIT 5
        """,
        
        "Analyse de Volatilité": """
            SELECT 
                c.symbol,
                ROUND(AVG(m.volatility_30d), 2) as volatilite_moy,
                CASE 
                    WHEN AVG(m.volatility_30d) > 5 THEN 'Très volatile'
                    WHEN AVG(m.volatility_30d) > 3 THEN 'Volatile'
                    ELSE 'Modéré'
                END as categorie_risque
            FROM cryptocurrencies c
            JOIN metrics m ON c.crypto_id = m.crypto_id
            WHERE m.volatility_30d IS NOT NULL
            GROUP BY c.symbol
            ORDER BY volatilite_moy DESC LIMIT 5
        """,
        
        "Market Dominance": """
            WITH latest AS (
                SELECT c.symbol, ph.market_cap,
                       SUM(ph.market_cap) OVER () as total_cap
                FROM cryptocurrencies c
                JOIN price_history ph ON c.crypto_id = ph.crypto_id
                WHERE ph.date = (SELECT MAX(date) FROM price_history)
            )
            SELECT symbol,
                   ROUND(market_cap / 1000000000, 2) as cap_milliards,
                   ROUND((market_cap / total_cap) * 100, 2) as dominance_pct
            FROM latest
            ORDER BY dominance_pct DESC LIMIT 5
        """
    }
    
    # Exécution des requêtes
    for query_name, query in queries.items():
        execute_query(conn, query_name, query)
    
    # Génération des visualisations
    print("\n\n" + "="*60)
    print(" GÉNÉRATION DES VISUALISATIONS")
    print("="*60)
    
    plot_price_evolution(conn)
    plot_volatility_comparison(conn)
    plot_correlation_heatmap(conn)
    plot_market_dominance(conn)
    plot_performance_comparison(conn)
    plot_volume_analysis(conn)
    
    conn.close()
    
    print("\n" + "="*60)
    print(" ANALYSES TERMINÉES!")
    print("="*60)
    print(f"\n {len(os.listdir(VIZ_DIR))} visualisations générées dans: {VIZ_DIR}/")
    print("\n Tu peux maintenant:")
    print("   1. Consulter les graphiques dans le dossier visualizations/")
    print("   2. Explorer la base avec: sqlite3 data/crypto_market.db")
    print("   3. Tester tes propres requêtes SQL depuis sql/queries.sql")
    print("   4. Publier le projet sur GitHub! \n")


def main():
    """Fonction principale"""
    try:
        run_all_analyses()
    except Exception as e:
        print(f"\n ERREUR: {e}")
        raise


if __name__ == "__main__":
    main()
