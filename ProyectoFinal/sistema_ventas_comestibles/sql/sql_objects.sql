-- =========================================
-- OBJETOS SQL AVANZADOS PARA SISTEMA DE VENTAS
-- Funciones, Triggers, Vistas, Procedimientos e Índices
-- =========================================

-- **1. FUNCIÓN: Calcular Comisión de Empleado**
-- Calcula la comisión basada en ventas totales con escala progresiva

DELIMITER //

CREATE FUNCTION calculate_employee_commission(
    employee_id INT,
    start_date DATE,
    end_date DATE
) 
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
COMMENT 'Calcula comisión progresiva del empleado basada en ventas del período'
BEGIN
    DECLARE total_sales DECIMAL(10,2) DEFAULT 0;
    DECLARE commission_rate DECIMAL(5,4) DEFAULT 0;
    DECLARE final_commission DECIMAL(10,2) DEFAULT 0;
    
    -- Obtener total de ventas del empleado en el período
    SELECT COALESCE(SUM(TotalPrice), 0) 
    INTO total_sales
    FROM sales 
    WHERE SalesPersonID = employee_id 
      AND SalesDate BETWEEN start_date AND end_date;
    
    -- Determinar tasa de comisión progresiva
    CASE 
        WHEN total_sales >= 100000 THEN SET commission_rate = 0.08;  -- 8% para ventas > 100k
        WHEN total_sales >= 50000 THEN SET commission_rate = 0.06;   -- 6% para ventas > 50k
        WHEN total_sales >= 25000 THEN SET commission_rate = 0.04;   -- 4% para ventas > 25k
        WHEN total_sales >= 10000 THEN SET commission_rate = 0.03;   -- 3% para ventas > 10k
        ELSE SET commission_rate = 0.02;                             -- 2% base
    END CASE;
    
    SET final_commission = total_sales * commission_rate;
    
    RETURN final_commission;
END //

DELIMITER ;

-- **2. FUNCIÓN: Clasificar Cliente por Valor (Customer Lifetime Value Category)**

DELIMITER //

CREATE FUNCTION classify_customer_value(customer_id INT)
RETURNS VARCHAR(20)
READS SQL DATA
DETERMINISTIC
COMMENT 'Clasifica cliente por valor total de compras históricas'
BEGIN
    DECLARE total_purchases DECIMAL(10,2) DEFAULT 0;
    DECLARE purchase_count INT DEFAULT 0;
    DECLARE avg_purchase DECIMAL(10,2) DEFAULT 0;
    DECLARE customer_category VARCHAR(20) DEFAULT 'New';
    
    -- Obtener métricas del cliente
    SELECT 
        COALESCE(SUM(TotalPrice), 0),
        COUNT(*),
        COALESCE(AVG(TotalPrice), 0)
    INTO total_purchases, purchase_count, avg_purchase
    FROM sales 
    WHERE CustomerID = customer_id;
    
    -- Clasificar basado en valor total y frecuencia
    CASE 
        WHEN total_purchases >= 10000 AND purchase_count >= 20 THEN 
            SET customer_category = 'VIP';
        WHEN total_purchases >= 5000 AND purchase_count >= 10 THEN 
            SET customer_category = 'Premium';
        WHEN total_purchases >= 2000 AND purchase_count >= 5 THEN 
            SET customer_category = 'Gold';
        WHEN total_purchases >= 500 AND purchase_count >= 2 THEN 
            SET customer_category = 'Silver';
        WHEN purchase_count >= 1 THEN 
            SET customer_category = 'Bronze';
        ELSE 
            SET customer_category = 'New';
    END CASE;
    
    RETURN customer_category;
END //

DELIMITER ;

-- =========================================

-- **3. VISTA: Dashboard Ejecutivo de Ventas**
-- Vista consolidada para reportes gerenciales

CREATE OR REPLACE VIEW executive_sales_dashboard AS
SELECT 
    -- Información del empleado
    e.EmployeeID,
    CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
    e.Gender,
    TIMESTAMPDIFF(YEAR, e.HireDate, CURDATE()) AS years_experience,
    
    -- Información geográfica
    ct.CityName AS employee_city,
    co.CountryName AS employee_country,
    
    -- Métricas de ventas (últimos 12 meses)
    COUNT(s.SalesID) AS transactions_12m,
    SUM(s.TotalPrice) AS revenue_12m,
    AVG(s.TotalPrice) AS avg_transaction_value,
    SUM(s.Quantity) AS items_sold_12m,
    COUNT(DISTINCT s.CustomerID) AS unique_customers_12m,
    COUNT(DISTINCT s.ProductID) AS unique_products_sold,
    
    -- Métricas de descuentos
    SUM(s.Discount) AS total_discounts_given,
    ROUND((SUM(s.Discount) / SUM(s.TotalPrice)) * 100, 2) AS discount_percentage,
    
    -- Clasificación de rendimiento
    CASE 
        WHEN SUM(s.TotalPrice) >= 100000 THEN 'Top Performer'
        WHEN SUM(s.TotalPrice) >= 50000 THEN 'High Performer'
        WHEN SUM(s.TotalPrice) >= 25000 THEN 'Average Performer'
        WHEN SUM(s.TotalPrice) >= 10000 THEN 'Developing'
        ELSE 'New/Learning'
    END AS performance_tier,
    
    -- Comisión calculada usando nuestra función
    calculate_employee_commission(
        e.EmployeeID, 
        DATE_SUB(CURDATE(), INTERVAL 12 MONTH), 
        CURDATE()
    ) AS estimated_commission,
    
    -- Métricas de eficiencia
    ROUND(SUM(s.TotalPrice) / COUNT(s.SalesID), 2) AS revenue_per_transaction,
    ROUND(SUM(s.TotalPrice) / SUM(s.Quantity), 2) AS revenue_per_item,
    
    -- Fecha de última venta
    MAX(s.SalesDate) AS last_sale_date,
    DATEDIFF(CURDATE(), MAX(s.SalesDate)) AS days_since_last_sale

FROM employees e
LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID 
                 AND s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
LEFT JOIN cities ct ON e.CityID = ct.CityID
LEFT JOIN countries co ON ct.CountryID = co.CountryID
GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Gender, e.HireDate, 
         ct.CityName, co.CountryName
ORDER BY revenue_12m DESC;

-- **4. VISTA: Análisis de Productos por Categoría**

CREATE OR REPLACE VIEW product_category_analysis AS
SELECT 
    cat.CategoryID,
    cat.CategoryName,
    
    -- Métricas de productos
    COUNT(DISTINCT p.ProductID) AS total_products,
    COUNT(DISTINCT CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                       THEN p.ProductID END) AS active_products_12m,
    
    -- Métricas de ventas
    COALESCE(SUM(s.TotalPrice), 0) AS total_revenue_12m,
    COALESCE(SUM(s.Quantity), 0) AS total_quantity_sold,
    COALESCE(COUNT(s.SalesID), 0) AS total_transactions,
    COALESCE(AVG(s.TotalPrice), 0) AS avg_transaction_value,
    
    -- Métricas de precios
    MIN(p.Price) AS min_product_price,
    MAX(p.Price) AS max_product_price,
    AVG(p.Price) AS avg_product_price,
    
    -- Top selling product en la categoría
    (SELECT p2.ProductName 
     FROM products p2 
     INNER JOIN sales s2 ON p2.ProductID = s2.ProductID
     WHERE p2.CategoryID = cat.CategoryID 
       AND s2.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
     GROUP BY p2.ProductID, p2.ProductName
     ORDER BY SUM(s2.TotalPrice) DESC 
     LIMIT 1) AS top_selling_product,
     
    -- Participación en ventas totales
    ROUND((COALESCE(SUM(s.TotalPrice), 0) / 
           (SELECT SUM(TotalPrice) FROM sales 
            WHERE SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH))) * 100, 2) AS revenue_share_percent

FROM categories cat
LEFT JOIN products p ON cat.CategoryID = p.CategoryID
LEFT JOIN sales s ON p.ProductID = s.ProductID 
                 AND s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY cat.CategoryID, cat.CategoryName
ORDER BY total_revenue_12m DESC;

-- =========================================

-- **5. TRIGGER: Auditoría de Cambios en Ventas**
-- Registra automáticamente cambios en la tabla sales

-- Primero crear tabla de auditoría
CREATE TABLE IF NOT EXISTS sales_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    sales_id INT NOT NULL,
    action_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_total_price DECIMAL(10,2),
    new_total_price DECIMAL(10,2),
    old_quantity INT,
    new_quantity INT,
    changed_by VARCHAR(100) DEFAULT USER(),
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_details JSON,
    INDEX idx_sales_audit_sales_id (sales_id),
    INDEX idx_sales_audit_timestamp (change_timestamp)
);

-- Trigger para INSERT
DELIMITER //

CREATE TRIGGER sales_audit_insert
    AFTER INSERT ON sales
    FOR EACH ROW
BEGIN
    INSERT INTO sales_audit (
        sales_id, action_type, new_total_price, new_quantity, 
        change_details
    ) VALUES (
        NEW.SalesID, 'INSERT', NEW.TotalPrice, NEW.Quantity,
        JSON_OBJECT(
            'customer_id', NEW.CustomerID,
            'product_id', NEW.ProductID,
            'sales_person_id', NEW.SalesPersonID,
            'sales_date', NEW.SalesDate,
            'discount', NEW.Discount
        )
    );
END //

DELIMITER ;

-- Trigger para UPDATE
DELIMITER //

CREATE TRIGGER sales_audit_update
    AFTER UPDATE ON sales
    FOR EACH ROW
BEGIN
    INSERT INTO sales_audit (
        sales_id, action_type, 
        old_total_price, new_total_price,
        old_quantity, new_quantity,
        change_details
    ) VALUES (
        NEW.SalesID, 'UPDATE', 
        OLD.TotalPrice, NEW.TotalPrice,
        OLD.Quantity, NEW.Quantity,
        JSON_OBJECT(
            'changes', JSON_OBJECT(
                'total_price', JSON_OBJECT('from', OLD.TotalPrice, 'to', NEW.TotalPrice),
                'quantity', JSON_OBJECT('from', OLD.Quantity, 'to', NEW.Quantity),
                'discount', JSON_OBJECT('from', OLD.Discount, 'to', NEW.Discount)
            )
        )
    );
END //

DELIMITER ;

-- **6. TRIGGER: Validación Automática de Ventas**
-- Previene ventas con datos inconsistentes

DELIMITER //

CREATE TRIGGER sales_validation_trigger
    BEFORE INSERT ON sales
    FOR EACH ROW
BEGIN
    DECLARE product_price DECIMAL(10,2);
    DECLARE calculated_total DECIMAL(10,2);
    DECLARE error_message VARCHAR(255);
    
    -- Obtener precio del producto
    SELECT Price INTO product_price 
    FROM products 
    WHERE ProductID = NEW.ProductID;
    
    -- Validar que el producto existe
    IF product_price IS NULL THEN
        SET error_message = CONCAT('Product ID ', NEW.ProductID, ' does not exist');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;
    
    -- Calcular total esperado
    SET calculated_total = (NEW.Quantity * product_price) - NEW.Discount;
    
    -- Validar que el total calculado coincide (con margen de error de 0.01)
    IF ABS(NEW.TotalPrice - calculated_total) > 0.01 THEN
        SET error_message = CONCAT('Invalid total price. Expected: ', calculated_total, ', Got: ', NEW.TotalPrice);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
    END IF;
    
    -- Validar cantidad positiva
    IF NEW.Quantity <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be positive';
    END IF;
    
    -- Validar descuento no mayor al 50% del subtotal
    IF NEW.Discount > (NEW.Quantity * product_price * 0.5) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Discount cannot exceed 50% of subtotal';
    END IF;
END //

DELIMITER ;

-- =========================================

-- **7. PROCEDIMIENTO ALMACENADO: Reporte de Rendimiento Mensual**

DELIMITER //

CREATE PROCEDURE generate_monthly_performance_report(
    IN report_year INT,
    IN report_month INT,
    IN min_revenue DECIMAL(10,2) DEFAULT 0
)
COMMENT 'Genera reporte detallado de rendimiento mensual por empleado'
BEGIN
    DECLARE start_date DATE;
    DECLARE end_date DATE;
    
    -- Calcular fechas del mes
    SET start_date = DATE(CONCAT(report_year, '-', LPAD(report_month, 2, '0'), '-01'));
    SET end_date = LAST_DAY(start_date);
    
    -- Reporte principal
    SELECT 
        'MONTHLY PERFORMANCE REPORT' AS report_title,
        CONCAT(MONTHNAME(start_date), ' ', report_year) AS period,
        COUNT(DISTINCT e.EmployeeID) AS total_employees_active,
        COUNT(DISTINCT s.CustomerID) AS total_customers_served,
        SUM(s.TotalPrice) AS total_company_revenue,
        AVG(s.TotalPrice) AS avg_transaction_value
    FROM employees e
    LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID 
                     AND s.SalesDate BETWEEN start_date AND end_date;
    
    -- Detalle por empleado
    SELECT 
        ROW_NUMBER() OVER (ORDER BY SUM(s.TotalPrice) DESC) AS ranking,
        e.EmployeeID,
        CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
        COUNT(s.SalesID) AS transactions,
        SUM(s.TotalPrice) AS revenue,
        AVG(s.TotalPrice) AS avg_transaction,
        SUM(s.Quantity) AS items_sold,
        COUNT(DISTINCT s.CustomerID) AS unique_customers,
        
        -- Usar nuestra función de comisión
        calculate_employee_commission(e.EmployeeID, start_date, end_date) AS commission,
        
        -- Participación en ventas totales del mes
        ROUND((SUM(s.TotalPrice) / 
               (SELECT SUM(TotalPrice) FROM sales 
                WHERE SalesDate BETWEEN start_date AND end_date)) * 100, 2) AS revenue_share_percent,
                
        -- Clasificación de rendimiento
        CASE 
            WHEN SUM(s.TotalPrice) >= 10000 THEN 'Excellent'
            WHEN SUM(s.TotalPrice) >= 5000 THEN 'Good'
            WHEN SUM(s.TotalPrice) >= 2000 THEN 'Average'
            WHEN SUM(s.TotalPrice) >= 500 THEN 'Below Average'
            ELSE 'Poor'
        END AS performance_rating
        
    FROM employees e
    LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID 
                     AND s.SalesDate BETWEEN start_date AND end_date
    GROUP BY e.EmployeeID, e.FirstName, e.LastName
    HAVING SUM(COALESCE(s.TotalPrice, 0)) >= min_revenue
    ORDER BY revenue DESC;
    
END //

DELIMITER ;

-- **8. PROCEDIMIENTO ALMACENADO: Análisis de Clientes Top**

DELIMITER //

CREATE PROCEDURE analyze_top_customers(
    IN top_n INT DEFAULT 20,
    IN analysis_months INT DEFAULT 12
)
COMMENT 'Analiza los mejores clientes por valor y frecuencia'
BEGIN
    DECLARE analysis_start_date DATE;
    SET analysis_start_date = DATE_SUB(CURDATE(), INTERVAL analysis_months MONTH);
    
    SELECT 
        ROW_NUMBER() OVER (ORDER BY SUM(s.TotalPrice) DESC) AS customer_rank,
        c.CustomerID,
        CONCAT(c.FirstName, ' ', c.LastName) AS customer_name,
        ct.CityName,
        co.CountryName,
        
        -- Métricas de compra
        COUNT(s.SalesID) AS total_purchases,
        SUM(s.TotalPrice) AS total_spent,
        AVG(s.TotalPrice) AS avg_purchase_value,
        SUM(s.Quantity) AS total_items_purchased,
        
        -- Análisis temporal
        MIN(s.SalesDate) AS first_purchase_date,
        MAX(s.SalesDate) AS last_purchase_date,
        DATEDIFF(MAX(s.SalesDate), MIN(s.SalesDate)) AS customer_lifetime_days,
        DATEDIFF(CURDATE(), MAX(s.SalesDate)) AS days_since_last_purchase,
        
        -- Frecuencia de compra
        ROUND(COUNT(s.SalesID) / (DATEDIFF(CURDATE(), MIN(s.SalesDate)) / 30), 2) AS avg_purchases_per_month,
        
        -- Clasificación usando nuestra función
        classify_customer_value(c.CustomerID) AS customer_tier,
        
        -- Diversidad de productos
        COUNT(DISTINCT s.ProductID) AS unique_products_purchased,
        COUNT(DISTINCT p.CategoryID) AS unique_categories_purchased,
        
        -- Tendencia reciente (últimos 3 meses vs 3 meses anteriores)
        (SELECT COALESCE(SUM(TotalPrice), 0) 
         FROM sales s_recent 
         WHERE s_recent.CustomerID = c.CustomerID 
           AND s_recent.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)) AS revenue_last_3m,
           
        (SELECT COALESCE(SUM(TotalPrice), 0) 
         FROM sales s_prev 
         WHERE s_prev.CustomerID = c.CustomerID 
           AND s_prev.SalesDate BETWEEN DATE_SUB(CURDATE(), INTERVAL 6 MONTH) 
           AND DATE_SUB(CURDATE(), INTERVAL 3 MONTH)) AS revenue_prev_3m
        
    FROM customers c
    INNER JOIN sales s ON c.CustomerID = s.CustomerID 
                      AND s.SalesDate >= analysis_start_date
    INNER JOIN cities ct ON c.CityID = ct.CityID
    INNER JOIN countries co ON ct.CountryID = co.CountryID
    INNER JOIN products p ON s.ProductID = p.ProductID
    GROUP BY c.CustomerID, c.FirstName, c.LastName, ct.CityName, co.CountryName
    ORDER BY total_spent DESC
    LIMIT top_n;
    
END //

DELIMITER ;

-- =========================================

-- **9. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN**

-- Índices compuestos para consultas complejas
CREATE INDEX idx_sales_date_employee ON sales(SalesDate, SalesPersonID);
CREATE INDEX idx_sales_date_customer_product ON sales(SalesDate, CustomerID, ProductID);
CREATE INDEX idx_sales_totalprice_date ON sales(TotalPrice, SalesDate);

-- Índices para joins frecuentes
CREATE INDEX idx_customer_name ON customers(FirstName, LastName);
CREATE INDEX idx_employee_name ON employees(FirstName, LastName);
CREATE INDEX idx_product_name_category ON products(ProductName, CategoryID);

-- Índices para búsquedas por fecha
CREATE INDEX idx_employee_hiredate ON employees(HireDate);
CREATE INDEX idx_sales_month_year ON sales((YEAR(SalesDate)), (MONTH(SalesDate)));

-- Índices parciales para datos recientes (MySQL 8.0+)
-- CREATE INDEX idx_sales_recent ON sales(SalesPersonID, TotalPrice) 
-- WHERE SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH);

-- Índice para análisis de descuentos
CREATE INDEX idx_sales_discount ON sales(Discount) WHERE Discount > 0;