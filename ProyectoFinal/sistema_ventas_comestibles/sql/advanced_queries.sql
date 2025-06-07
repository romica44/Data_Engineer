-- =========================================
-- CONSULTAS SQL AVANZADAS PARA SISTEMA DE VENTAS
-- CTE + Funciones Ventana + Análisis Empresarial
-- =========================================

-- **CONSULTA 1: Ranking de Empleados por Rendimiento con CTE y Funciones Ventana**
-- Analiza el rendimiento de empleados con múltiples métricas de ranking

WITH employee_sales_summary AS (
    -- CTE: Resumen de ventas por empleado
    SELECT 
        e.EmployeeID,
        CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
        e.Gender,
        YEAR(e.HireDate) AS hire_year,
        COUNT(s.SalesID) AS total_transactions,
        SUM(s.Quantity) AS total_items_sold,
        SUM(s.TotalPrice) AS total_revenue,
        AVG(s.TotalPrice) AS avg_transaction_value,
        SUM(s.Discount) AS total_discounts_given,
        c2.CountryName
    FROM employees e
    INNER JOIN sales s ON e.EmployeeID = s.SalesPersonID
    INNER JOIN cities c ON e.CityID = c.CityID
    INNER JOIN countries c2 ON c.CountryID = c2.CountryID
    WHERE s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
    GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Gender, e.HireDate, c2.CountryName
),
employee_rankings AS (
    -- CTE: Aplicar funciones ventana para rankings múltiples
    SELECT 
        *,
        -- Ranking por ingresos totales
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
        RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank_tied,
        DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_dense_rank,
        
        -- Ranking por número de transacciones
        ROW_NUMBER() OVER (ORDER BY total_transactions DESC) AS transaction_rank,
        
        -- Ranking por valor promedio de transacción
        ROW_NUMBER() OVER (ORDER BY avg_transaction_value DESC) AS avg_value_rank,
        
        -- Percentiles de rendimiento
        PERCENT_RANK() OVER (ORDER BY total_revenue) AS revenue_percentile,
        CUME_DIST() OVER (ORDER BY total_revenue) AS revenue_cumulative_dist,
        
        -- Comparaciones dentro del mismo país
        ROW_NUMBER() OVER (PARTITION BY CountryName ORDER BY total_revenue DESC) AS country_revenue_rank,
        
        -- Comparaciones por género
        ROW_NUMBER() OVER (PARTITION BY Gender ORDER BY total_revenue DESC) AS gender_revenue_rank,
        
        -- Running totals y moving averages
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC ROWS UNBOUNDED PRECEDING) AS cumulative_revenue,
        AVG(total_revenue) OVER (ORDER BY total_revenue DESC ROWS 2 PRECEDING) AS moving_avg_3_employees
    FROM employee_sales_summary
)
-- Consulta final con clasificaciones de rendimiento
SELECT 
    employee_name,
    Gender,
    hire_year,
    CountryName,
    FORMAT(total_revenue, 2) AS formatted_revenue,
    FORMAT(avg_transaction_value, 2) AS formatted_avg_transaction,
    total_transactions,
    total_items_sold,
    
    -- Rankings principales
    revenue_rank,
    transaction_rank,
    avg_value_rank,
    
    -- Rankings contextuales
    country_revenue_rank,
    gender_revenue_rank,
    
    -- Métricas estadísticas
    ROUND(revenue_percentile * 100, 1) AS revenue_percentile_pct,
    ROUND(revenue_cumulative_dist * 100, 1) AS cumulative_distribution_pct,
    
    -- Clasificación de rendimiento personalizada
    CASE 
        WHEN revenue_percentile >= 0.9 THEN 'Top Performer (10%)'
        WHEN revenue_percentile >= 0.7 THEN 'High Performer (30%)'
        WHEN revenue_percentile >= 0.4 THEN 'Average Performer (40%)'
        WHEN revenue_percentile >= 0.2 THEN 'Below Average (20%)'
        ELSE 'Needs Improvement (Bottom 20%)'
    END AS performance_category,
    
    -- Análisis de eficiencia de descuentos
    ROUND((total_discounts_given / total_revenue) * 100, 2) AS discount_percentage,
    
    FORMAT(cumulative_revenue, 2) AS running_total_revenue
FROM employee_rankings
ORDER BY revenue_rank;

-- =========================================

-- **CONSULTA 2: Análisis de Tendencias de Ventas con CTE Recursivo y Funciones Ventana**
-- Analiza patrones de crecimiento mensual y estacionalidad

WITH RECURSIVE date_series AS (
    -- CTE Recursivo: Generar serie de meses para análisis completo
    SELECT 
        DATE('2023-01-01') AS month_start,
        LAST_DAY('2023-01-01') AS month_end,
        1 AS month_number
    
    UNION ALL
    
    SELECT 
        DATE_ADD(month_start, INTERVAL 1 MONTH),
        LAST_DAY(DATE_ADD(month_start, INTERVAL 1 MONTH)),
        month_number + 1
    FROM date_series
    WHERE month_number < 24  -- 24 meses de análisis
),
monthly_sales_data AS (
    -- CTE: Agregar datos de ventas por mes
    SELECT 
        ds.month_start,
        ds.month_end,
        ds.month_number,
        YEAR(ds.month_start) AS sales_year,
        MONTH(ds.month_start) AS sales_month,
        MONTHNAME(ds.month_start) AS month_name,
        
        -- Métricas de ventas (usando COALESCE para meses sin ventas)
        COALESCE(COUNT(s.SalesID), 0) AS total_transactions,
        COALESCE(SUM(s.TotalPrice), 0) AS total_revenue,
        COALESCE(SUM(s.Quantity), 0) AS total_items_sold,
        COALESCE(AVG(s.TotalPrice), 0) AS avg_transaction_value,
        COALESCE(COUNT(DISTINCT s.CustomerID), 0) AS unique_customers,
        COALESCE(COUNT(DISTINCT s.ProductID), 0) AS unique_products_sold,
        COALESCE(SUM(s.Discount), 0) AS total_discounts
        
    FROM date_series ds
    LEFT JOIN sales s ON s.SalesDate BETWEEN ds.month_start AND ds.month_end
    GROUP BY ds.month_start, ds.month_end, ds.month_number
),
sales_with_trends AS (
    -- CTE: Aplicar funciones ventana para análisis de tendencias
    SELECT 
        *,
        -- Análisis temporal con LAG/LEAD
        LAG(total_revenue, 1) OVER (ORDER BY month_start) AS prev_month_revenue,
        LAG(total_revenue, 12) OVER (ORDER BY month_start) AS same_month_prev_year,
        LEAD(total_revenue, 1) OVER (ORDER BY month_start) AS next_month_revenue,
        
        -- Moving averages para suavizar tendencias
        AVG(total_revenue) OVER (ORDER BY month_start ROWS 2 PRECEDING) AS moving_avg_3_months,
        AVG(total_revenue) OVER (ORDER BY month_start ROWS 5 PRECEDING) AS moving_avg_6_months,
        AVG(total_revenue) OVER (ORDER BY month_start ROWS 11 PRECEDING) AS moving_avg_12_months,
        
        -- Rolling sums y acumulativos
        SUM(total_revenue) OVER (ORDER BY month_start ROWS 2 PRECEDING) AS rolling_sum_3_months,
        SUM(total_revenue) OVER (PARTITION BY sales_year ORDER BY month_start) AS ytd_revenue,
        SUM(total_revenue) OVER (ORDER BY month_start) AS cumulative_revenue,
        
        -- Análisis de variabilidad
        STDDEV(total_revenue) OVER (ORDER BY month_start ROWS 11 PRECEDING) AS revenue_volatility_12m,
        
        -- Rankings y percentiles por mes del año (estacionalidad)
        ROW_NUMBER() OVER (PARTITION BY sales_month ORDER BY total_revenue DESC) AS month_performance_rank,
        PERCENT_RANK() OVER (PARTITION BY sales_month ORDER BY total_revenue) AS month_percentile
        
    FROM monthly_sales_data
)
-- Consulta final con análisis completo de tendencias
SELECT 
    DATE_FORMAT(month_start, '%Y-%m') AS period,
    month_name,
    sales_year,
    
    -- Métricas base formateadas
    FORMAT(total_revenue, 2) AS revenue,
    FORMAT(moving_avg_3_months, 2) AS avg_3m,
    FORMAT(moving_avg_12_months, 2) AS avg_12m,
    total_transactions,
    unique_customers,
    
    -- Análisis de crecimiento mes a mes
    CASE 
        WHEN prev_month_revenue > 0 THEN 
            ROUND(((total_revenue - prev_month_revenue) / prev_month_revenue) * 100, 2)
        ELSE NULL 
    END AS mom_growth_percent,
    
    -- Análisis año contra año
    CASE 
        WHEN same_month_prev_year > 0 THEN 
            ROUND(((total_revenue - same_month_prev_year) / same_month_prev_year) * 100, 2)
        ELSE NULL 
    END AS yoy_growth_percent,
    
    -- Indicadores de tendencia
    CASE 
        WHEN total_revenue > moving_avg_12_months THEN 'Above Trend'
        WHEN total_revenue < moving_avg_12_months * 0.95 THEN 'Below Trend'
        ELSE 'On Trend'
    END AS trend_indicator,
    
    -- Clasificación estacional
    CASE 
        WHEN month_percentile >= 0.8 THEN 'Peak Season'
        WHEN month_percentile >= 0.6 THEN 'High Season'
        WHEN month_percentile >= 0.4 THEN 'Normal Season'
        WHEN month_percentile >= 0.2 THEN 'Low Season'
        ELSE 'Off Season'
    END AS seasonal_classification,
    
    -- Participación en el año
    ROUND((total_revenue / ytd_revenue) * 100, 2) AS month_contribution_to_ytd,
    
    -- Volatilidad (solo mostrar si tenemos suficientes datos)
    CASE 
        WHEN revenue_volatility_12m IS NOT NULL 
        THEN ROUND(revenue_volatility_12m, 2) 
        ELSE NULL 
    END AS revenue_volatility
    
FROM sales_with_trends
WHERE month_start <= CURDATE()  -- Solo mostrar meses hasta la fecha actual
ORDER BY month_start;