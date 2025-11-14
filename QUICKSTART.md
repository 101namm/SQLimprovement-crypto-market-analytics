# 🚀 Guide de Démarrage Rapide

## Installation et lancement du projet

### 1. Setup initial

```bash
# Cloner ou télécharger le projet
cd SQLimprovement-crypto-market-analytics

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Collecter les données

```bash
python src/data_collection.py
```

⏱️ Temps estimé: 2-3 minutes
📦 Crée: `data/raw/crypto_info.csv` et `data/raw/price_history.csv`

### 3. Créer la base de données

```bash
python src/database.py
```

⏱️ Temps estimé: 10-15 secondes
📦 Crée: `data/crypto_market.db`

### 4. Lancer les analyses

```bash
python src/analysis.py
```

⏱️ Temps estimé: 20-30 secondes
📦 Crée: 6 visualisations dans `visualizations/`

---

## Que faire ensuite ?

### Explorer la base de données

```bash
sqlite3 data/crypto_market.db
```

Exemples de commandes:
```sql
.tables                          -- Liste les tables
.schema cryptocurrencies         -- Voir le schéma d'une table
SELECT * FROM vw_price_analysis LIMIT 10;  -- Query de test
```

### Modifier les requêtes SQL

Édite `sql/queries.sql` et teste tes propres requêtes!

### Ajouter d'autres cryptos

Dans `src/data_collection.py`, modifie la liste `TOP_CRYPTOS` pour ajouter d'autres cryptomonnaies.
Liste complète des IDs disponibles: https://api.coingecko.com/api/v3/coins/list

### Personnaliser les visualisations

Édite `src/analysis.py` pour créer tes propres graphiques!

---

## Checklist avant de publier sur GitHub

- [ ] Vérifier que tous les scripts fonctionnent
- [ ] Ajouter des screenshots des visualisations dans le README
- [ ] Remplir la section "Insights clés" du README avec tes observations
- [ ] Personnaliser avec ton nom et liens (GitHub, LinkedIn)
- [ ] Créer le repo GitHub et faire le premier commit
- [ ] Ajouter des badges au README (Python version, etc.)

---

## Troubleshooting

**Erreur: ModuleNotFoundError**
→ Vérifie que l'environnement virtuel est activé et que les dépendances sont installées

**Erreur API CoinGecko: 429 (Too Many Requests)**
→ Augmente le délai dans `data_collection.py` (ligne avec `time.sleep()`)

**Pas de données récupérées**
→ Vérifie ta connexion internet et l'état de l'API CoinGecko

**SQLite error**
→ Supprime `data/crypto_market.db` et relance `python src/database.py`

---

Bon projet! 🚀💪
