# SQLimprovement - Crypto Market Analytics 📊🚀 (Projet fun)

## 🎯 Objectif du projet

Projet d'analyse de données du marché des cryptomonnaies utilisant SQL pour explorer, analyser et extraire des insights business sur les performances, volatilités et corrélations des principales cryptomonnaies.

## 📋 Description

Ce projet démontre mes compétences en :
- **Data Engineering** : Collecte de données via API (CoinGecko)
- **SQL** : Requêtes analytiques avancées, agrégations, jointures
- **Data Analysis** : Analyse de séries temporelles, calculs de métriques financières
- **Visualisation** : Graphiques et dashboards pour insights business

## 🗂️ Structure du projet

```
SQLimprovement-crypto-market-analytics/
├── README.md                          # Documentation du projet
├── requirements.txt                   # Dépendances Python
├── .gitignore                        # Fichiers à ignorer par Git
├── data/
│   ├── raw/                          # Données brutes de l'API
│   ├── processed/                    # Données nettoyées
│   └── crypto_market.db              # Base de données SQLite
├── sql/
│   ├── schema.sql                    # Schéma de la base de données
│   └── queries.sql                   # Requêtes SQL d'analyse
├── src/
│   ├── data_collection.py            # Script de collecte API
│   ├── database.py                   # Gestion de la base de données
│   └── analysis.py                   # Analyses et visualisations
├── notebooks/
│   └── exploratory_analysis.ipynb    # Analyses exploratoires
└── visualizations/                    # Graphiques générés
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Setup

```bash
# Cloner le repository
git clone https://github.com/TON_USERNAME/SQLimprovement-crypto-market-analytics.git
cd SQLimprovement-crypto-market-analytics

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

## 📊 Utilisation

### 1. Collecter les données

```bash
python src/data_collection.py
```

Récupère les données historiques des top cryptomonnaies via l'API CoinGecko.

### 2. Créer la base de données

```bash
python src/database.py
```

Crée la base SQLite et importe les données collectées.

### 3. Lancer les analyses

```bash
python src/analysis.py
```

Exécute les requêtes SQL et génère les visualisations.

## 🔍 Analyses réalisées

### Requêtes SQL Business

1. **Top performers** : Cryptos avec la meilleure performance sur 30/90 jours
2. **Analyse de volatilité** : Identification des cryptos les plus/moins volatiles
3. **Corrélations** : Matrice de corrélation entre cryptos majeures
4. **Volumes de trading** : Analyse des volumes par crypto et période
5. **Market dominance** : Part de marché (market cap) de chaque crypto
6. **Tendances temporelles** : Évolution des prix sur différentes périodes
7. **Risk/Return analysis** : Ratio rendement/risque

### Visualisations

- Graphiques de prix historiques
- Heatmap de corrélations
- Distribution des rendements
- Comparaison de volatilités
- Évolution des market caps

## 🛠️ Technologies utilisées

- **Python 3.x** : Langage principal
- **SQLite** : Base de données relationnelle
- **Pandas** : Manipulation de données
- **Requests** : Appels API
- **Matplotlib/Seaborn** : Visualisations
- **NumPy** : Calculs numériques

## 📚 Compétences démontrées

✅ Collecte de données via API REST  
✅ Modélisation de base de données relationnelle  
✅ Requêtes SQL complexes (agrégations, jointures, window functions)  
✅ Analyse de séries temporelles financières  
✅ Calculs de métriques financières (volatilité, corrélation, rendement)  
✅ Data visualization  
✅ Documentation et code propre  

## 🔄 Améliorations futures

- [ ] Ajouter plus de cryptomonnaies (top 50)
- [ ] Intégrer des données de sentiment (Twitter/Reddit)
- [ ] Créer un dashboard interactif (Streamlit)
- [ ] Automatiser la collecte quotidienne (cron job)
- [ ] Ajouter des indicateurs techniques (RSI, MACD, Bollinger Bands)
- [ ] Analyse prédictive avec Machine Learning

## 📝 Licence

MIT License

## 👤 Auteur

**101namm**
- GitHub: [101namm](https://github.com/101namm)
- LinkedIn: [Mon profil](https://fr.linkedin.com/in/louischavaroche)

---

*Projet réalisé dans le cadre du développement de compétences en Data Analysis et SQL*
