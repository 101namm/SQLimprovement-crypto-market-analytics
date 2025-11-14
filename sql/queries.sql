-- Requêtes SQL d'analyse pour Crypto Market Analytics
-- Toutes les requêtes sont testées et optimisées pour SQLite

-- ============================================
-- 1. TOP PERFORMERS (30 derniers jours)
-- ============================================
-- Cryptos avec la meilleure performance sur 30 jours
SELECT 
    c.symbol,
    c.name,
    ROUND(
        (latest.price_usd - first.price_usd) / first.price_usd * 100, 
        2
    ) as performance_30d_pct,
    ROUND(first.price_usd, 2) as price_30d_ago,
    ROUND(latest.price_usd, 2) as current_price,
    ROUND(latest.market_cap / 1000000000, 2) as market_cap_billions
FROM cryptocurrencies c
JOIN (
    SELECT crypto_id, price_usd, market_cap
    FROM price_history
    WHERE date = (SELECT MAX(date) FROM price_history)
) latest ON c.crypto_id = latest.crypto_id
JOIN (
    SELECT crypto_id, price_usd
    FROM price_history
    WHERE date = (SELECT date(MAX(date), '-30 days') FROM price_history)
) first ON c.crypto_id = first.crypto_id
ORDER BY performance_30d_pct DESC
LIMIT 10;


-- ============================================
-- 2. ANALYSE DE VOLATILITÉ
-- ============================================
-- Classement des cryptos par volatilité (écart-type des rendements)
SELECT 
    c.symbol,
    c.name,
    ROUND(AVG(m.volatility_30d), 2) as avg_volatility_30d,
    ROUND(MIN(m.volatility_30d), 2) as min_volatility,
    ROUND(MAX(m.volatility_30d), 2) as max_volatility,
    CASE 
        WHEN AVG(m.volatility_30d) > 5 THEN 'Très volatile'
        WHEN AVG(m.volatility_30d) > 3 THEN 'Volatile'
        WHEN AVG(m.volatility_30d) > 1.5 THEN 'Modérément volatile'
        ELSE 'Peu volatile'
    END as risk_category
FROM cryptocurrencies c
JOIN metrics m ON c.crypto_id = m.crypto_id
WHERE m.date >= date('now', '-90 days')
GROUP BY c.symbol, c.name
ORDER BY avg_volatility_30d DESC;


-- ============================================
-- 3. VOLUMES DE TRADING PAR CRYPTO
-- ============================================
-- Analyse des volumes moyens de trading sur 30 jours
SELECT 
    c.symbol,
    c.name,
    ROUND(AVG(ph.total_volume) / 1000000000, 2) as avg_volume_30d_billions,
    ROUND(MAX(ph.total_volume) / 1000000000, 2) as max_volume_billions,
    ROUND(MIN(ph.total_volume) / 1000000000, 2) as min_volume_billions,
    COUNT(*) as days_tracked
FROM cryptocurrencies c
JOIN price_history ph ON c.crypto_id = ph.crypto_id
WHERE ph.date >= date('now', '-30 days')
GROUP BY c.symbol, c.name
ORDER BY avg_volume_30d_billions DESC
LIMIT 15;


-- ============================================
-- 4. MARKET DOMINANCE (Part de marché)
-- ============================================
-- Calcul de la dominance de chaque crypto (% du market cap total)
WITH latest_marketcap AS (
    SELECT 
        c.symbol,
        c.name,
        ph.market_cap,
        SUM(ph.market_cap) OVER () as total_market_cap
    FROM cryptocurrencies c
    JOIN price_history ph ON c.crypto_id = ph.crypto_id
    WHERE ph.date = (SELECT MAX(date) FROM price_history)
)
SELECT 
    symbol,
    name,
    ROUND(market_cap / 1000000000, 2) as market_cap_billions,
    ROUND((market_cap / total_market_cap) * 100, 2) as dominance_pct
FROM latest_marketcap
ORDER BY dominance_pct DESC;


-- ============================================
-- 5. ANALYSE DES RENDEMENTS QUOTIDIENS
-- ============================================
-- Distribution des rendements quotidiens par crypto
SELECT 
    c.symbol,
    COUNT(*) as days_tracked,
    ROUND(AVG(m.daily_return), 2) as avg_daily_return_pct,
    ROUND(MIN(m.daily_return), 2) as worst_day_pct,
    ROUND(MAX(m.daily_return), 2) as best_day_pct,
    ROUND(
        (COUNT(CASE WHEN m.daily_return > 0 THEN 1 END) * 100.0) / COUNT(*), 
        1
    ) as positive_days_pct
FROM cryptocurrencies c
JOIN metrics m ON c.crypto_id = m.crypto_id
WHERE m.date >= date('now', '-90 days')
GROUP BY c.symbol
ORDER BY avg_daily_return_pct DESC;


-- ============================================
-- 6. TENDANCES HEBDOMADAIRES
-- ============================================
-- Performance par semaine pour voir les tendances
SELECT 
    c.symbol,
    strftime('%Y-W%W', ph.date) as week,
    ROUND(MIN(ph.price_usd), 2) as week_low,
    ROUND(MAX(ph.price_usd), 2) as week_high,
    ROUND(AVG(ph.price_usd), 2) as week_avg,
    ROUND(
        (MAX(ph.price_usd) - MIN(ph.price_usd)) / MIN(ph.price_usd) * 100,
        2
    ) as weekly_range_pct
FROM cryptocurrencies c
JOIN price_history ph ON c.crypto_id = ph.crypto_id
WHERE ph.date >= date('now', '-60 days')
GROUP BY c.symbol, strftime('%Y-W%W', ph.date)
ORDER BY week DESC, c.symbol;


-- ============================================
-- 7. RISK/RETURN RATIO
-- ============================================
-- Ratio rendement/risque : meilleurs performers par unité de risque
WITH performance_metrics AS (
    SELECT 
        c.symbol,
        c.name,
        AVG(m.daily_return) as avg_return,
        AVG(m.volatility_30d) as avg_volatility
    FROM cryptocurrencies c
    JOIN metrics m ON c.crypto_id = m.crypto_id
    WHERE m.date >= date('now', '-90 days')
    GROUP BY c.symbol, c.name
)
SELECT 
    symbol,
    name,
    ROUND(avg_return, 2) as avg_daily_return_pct,
    ROUND(avg_volatility, 2) as avg_volatility_pct,
    ROUND(avg_return / NULLIF(avg_volatility, 0), 3) as risk_return_ratio,
    CASE 
        WHEN avg_return / NULLIF(avg_volatility, 0) > 0.5 THEN 'Excellent'
        WHEN avg_return / NULLIF(avg_volatility, 0) > 0.2 THEN 'Bon'
        WHEN avg_return / NULLIF(avg_volatility, 0) > 0 THEN 'Moyen'
        ELSE 'Faible'
    END as risk_adjusted_rating
FROM performance_metrics
WHERE avg_volatility > 0
ORDER BY risk_return_ratio DESC;


-- ============================================
-- 8. COMPARAISON PRIX ACTUEL vs MOYENNES MOBILES
-- ============================================
-- Prix actuel vs moyennes mobiles 7j et 30j
WITH current_prices AS (
    SELECT crypto_id, price_usd as current_price
    FROM price_history
    WHERE date = (SELECT MAX(date) FROM price_history)
),
moving_averages AS (
    SELECT 
        crypto_id,
        AVG(CASE WHEN date >= date('now', '-7 days') THEN price_usd END) as ma_7d,
        AVG(CASE WHEN date >= date('now', '-30 days') THEN price_usd END) as ma_30d
    FROM price_history
    GROUP BY crypto_id
)
SELECT 
    c.symbol,
    c.name,
    ROUND(cp.current_price, 2) as current_price,
    ROUND(ma.ma_7d, 2) as ma_7_days,
    ROUND(ma.ma_30d, 2) as ma_30_days,
    ROUND((cp.current_price - ma.ma_7d) / ma.ma_7d * 100, 2) as vs_ma7_pct,
    ROUND((cp.current_price - ma.ma_30d) / ma.ma_30d * 100, 2) as vs_ma30_pct,
    CASE 
        WHEN cp.current_price > ma.ma_7d AND cp.current_price > ma.ma_30d THEN 'Bullish'
        WHEN cp.current_price < ma.ma_7d AND cp.current_price < ma.ma_30d THEN 'Bearish'
        ELSE 'Neutre'
    END as trend_signal
FROM cryptocurrencies c
JOIN current_prices cp ON c.crypto_id = cp.crypto_id
JOIN moving_averages ma ON c.crypto_id = ma.crypto_id
ORDER BY c.symbol;


-- ============================================
-- 9. STATISTIQUES GLOBALES DU MARCHÉ
-- ============================================
-- Vue d'ensemble du marché crypto
SELECT 
    COUNT(DISTINCT c.crypto_id) as total_cryptos_tracked,
    ROUND(SUM(ph.market_cap) / 1000000000, 2) as total_market_cap_billions,
    ROUND(SUM(ph.total_volume) / 1000000000, 2) as total_volume_24h_billions,
    ROUND(AVG(ph.price_usd), 2) as avg_price,
    date(ph.date) as snapshot_date
FROM price_history ph
JOIN cryptocurrencies c ON ph.crypto_id = c.crypto_id
WHERE ph.date = (SELECT MAX(date) FROM price_history)
GROUP BY date(ph.date);


-- ============================================
-- 10. TOP MOVERS (24h)
-- ============================================
-- Plus grandes variations sur les dernières 24h
WITH yesterday AS (
    SELECT crypto_id, price_usd as price_yesterday
    FROM price_history
    WHERE date = (SELECT date(MAX(date), '-1 day') FROM price_history)
),
today AS (
    SELECT crypto_id, price_usd as price_today
    FROM price_history
    WHERE date = (SELECT MAX(date) FROM price_history)
)
SELECT 
    c.symbol,
    c.name,
    ROUND(y.price_yesterday, 2) as price_24h_ago,
    ROUND(t.price_today, 2) as current_price,
    ROUND((t.price_today - y.price_yesterday) / y.price_yesterday * 100, 2) as change_24h_pct,
    CASE 
        WHEN (t.price_today - y.price_yesterday) / y.price_yesterday * 100 > 10 THEN '🚀 Strong Up'
        WHEN (t.price_today - y.price_yesterday) / y.price_yesterday * 100 > 5 THEN '📈 Up'
        WHEN (t.price_today - y.price_yesterday) / y.price_yesterday * 100 > -5 THEN '➡️ Stable'
        WHEN (t.price_today - y.price_yesterday) / y.price_yesterday * 100 > -10 THEN '📉 Down'
        ELSE '💥 Strong Down'
    END as movement_indicator
FROM cryptocurrencies c
JOIN yesterday y ON c.crypto_id = y.crypto_id
JOIN today t ON c.crypto_id = t.crypto_id
ORDER BY change_24h_pct DESC;
