-- Schema pour la base de données Crypto Market Analytics
-- SQLite database schema

-- Table des cryptomonnaies
CREATE TABLE IF NOT EXISTS cryptocurrencies (
    crypto_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des prix historiques
CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crypto_id TEXT NOT NULL,
    date DATE NOT NULL,
    price_usd REAL NOT NULL,
    market_cap REAL,
    total_volume REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crypto_id) REFERENCES cryptocurrencies(crypto_id),
    UNIQUE(crypto_id, date)
);

-- Table des métriques calculées (volatilité, rendements, etc.)
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crypto_id TEXT NOT NULL,
    date DATE NOT NULL,
    daily_return REAL,
    volatility_7d REAL,
    volatility_30d REAL,
    volume_change_24h REAL,
    market_cap_rank INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crypto_id) REFERENCES cryptocurrencies(crypto_id),
    UNIQUE(crypto_id, date)
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS idx_price_crypto_date ON price_history(crypto_id, date);
CREATE INDEX IF NOT EXISTS idx_price_date ON price_history(date);
CREATE INDEX IF NOT EXISTS idx_metrics_crypto_date ON metrics(crypto_id, date);

-- Vue pour faciliter les analyses : prix avec symboles
CREATE VIEW IF NOT EXISTS vw_price_analysis AS
SELECT 
    c.symbol,
    c.name,
    ph.date,
    ph.price_usd,
    ph.market_cap,
    ph.total_volume,
    m.daily_return,
    m.volatility_30d,
    m.market_cap_rank
FROM price_history ph
JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
LEFT JOIN metrics m ON ph.crypto_id = m.crypto_id AND ph.date = m.date
ORDER BY ph.date DESC, c.symbol;

-- Vue pour les performances mensuelles
CREATE VIEW IF NOT EXISTS vw_monthly_performance AS
SELECT 
    c.symbol,
    c.name,
    strftime('%Y-%m', ph.date) as month,
    MIN(ph.price_usd) as min_price,
    MAX(ph.price_usd) as max_price,
    AVG(ph.price_usd) as avg_price,
    (MAX(ph.price_usd) - MIN(ph.price_usd)) / MIN(ph.price_usd) * 100 as monthly_range_pct,
    SUM(ph.total_volume) as total_volume_month
FROM price_history ph
JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
GROUP BY c.symbol, c.name, strftime('%Y-%m', ph.date)
ORDER BY month DESC, c.symbol;
