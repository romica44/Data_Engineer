"""
Servicio de Análisis Avanzado con CTE, Funciones Ventana y Objetos SQL
Versión MEJORADA con reconexión automática por consulta
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Dict, List, Tuple
import logging
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
import json

# Importar la conexión singleton existente
from src.database.connection import DatabaseConnection

class AdvancedAnalyticsService:
    """
    Servicio para ejecutar consultas SQL avanzadas con CTE y funciones ventana,
    y gestionar objetos SQL personalizados.
    VERSIÓN MEJORADA: Reconecta automáticamente en cada consulta.
    """
    
    def __init__(self):
        """Inicializar servicio con conexión existente."""
        self.db = DatabaseConnection()
        self.logger = logging.getLogger(__name__)
    
    def _execute_query_with_fresh_connection(self, query: str, params: Dict = None) -> pd.DataFrame:
        """
        Ejecuta una consulta con una conexión fresca a la base de datos
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (Dict, optional): Parámetros para la consulta
            
        Returns:
            pd.DataFrame: Resultado de la consulta
        """
        try:
            # Crear nueva conexión para cada consulta
            fresh_db = DatabaseConnection()
            result = fresh_db.execute_query_to_dataframe(query, params or {})
            
            # Cerrar conexión explícitamente si hay método disponible
            if hasattr(fresh_db, 'close_connection'):
                fresh_db.close_connection()
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error ejecutando consulta avanzada: {e}")
            return pd.DataFrame()
    
    def _execute_sql_command_with_fresh_connection(self, query: str) -> bool:
        """
        Ejecuta un comando SQL (CREATE, DROP, etc.) con una conexión fresca
        
        Args:
            query (str): Comando SQL a ejecutar
            
        Returns:
            bool: True si se ejecutó exitosamente
        """
        try:
            # Crear nueva conexión para cada comando
            fresh_db = DatabaseConnection()
            
            with fresh_db.get_connection() as conn:
                conn.execute(text(query))
                conn.commit()
                
            # Cerrar conexión explícitamente si hay método disponible
            if hasattr(fresh_db, 'close_connection'):
                fresh_db.close_connection()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error ejecutando comando SQL: {e}")
            return False
        
    # =====================================
    # CONSULTAS AVANZADAS CON CTE Y FUNCIONES VENTANA
    # =====================================
    
    def get_employee_performance_ranking(self, months_back: int = 12) -> pd.DataFrame:
        """
        Ejecuta consulta avanzada con CTE y funciones ventana para ranking de empleados.
        
        Args:
            months_back: Número de meses hacia atrás para el análisis
            
        Returns:
            DataFrame con ranking y métricas de rendimiento de empleados
        """
        query = """
        WITH employee_sales_summary AS (
            SELECT 
                e.EmployeeID,
                CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
                e.Gender,
                YEAR(e.HireDate) AS hire_year,
                COUNT(s.SalesID) AS total_transactions,
                COALESCE(SUM(s.Quantity), 0) AS total_items_sold,
                COALESCE(SUM(s.TotalPrice), 0) AS total_revenue,
                COALESCE(AVG(s.TotalPrice), 0) AS avg_transaction_value,
                COALESCE(SUM(s.Discount), 0) AS total_discounts_given,
                c2.CountryName
            FROM employees e
            LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID
                             AND s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL :months_back MONTH)
            LEFT JOIN cities c ON e.CityID = c.CityID
            LEFT JOIN countries c2 ON c.CountryID = c2.CountryID
            GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Gender, e.HireDate, c2.CountryName
        ),
        employee_rankings AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
                RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank_tied,
                DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_dense_rank,
                ROW_NUMBER() OVER (ORDER BY total_transactions DESC) AS transaction_rank,
                ROW_NUMBER() OVER (ORDER BY avg_transaction_value DESC) AS avg_value_rank,
                PERCENT_RANK() OVER (ORDER BY total_revenue) AS revenue_percentile,
                CUME_DIST() OVER (ORDER BY total_revenue) AS revenue_cumulative_dist,
                ROW_NUMBER() OVER (PARTITION BY CountryName ORDER BY total_revenue DESC) AS country_revenue_rank,
                ROW_NUMBER() OVER (PARTITION BY Gender ORDER BY total_revenue DESC) AS gender_revenue_rank,
                SUM(total_revenue) OVER (ORDER BY total_revenue DESC ROWS UNBOUNDED PRECEDING) AS cumulative_revenue,
                AVG(total_revenue) OVER (ORDER BY total_revenue DESC ROWS 2 PRECEDING) AS moving_avg_3_employees
            FROM employee_sales_summary
            WHERE total_revenue > 0
        )
        SELECT 
            employee_name,
            Gender,
            hire_year,
            CountryName,
            total_revenue,
            avg_transaction_value,
            total_transactions,
            total_items_sold,
            revenue_rank,
            transaction_rank,
            avg_value_rank,
            country_revenue_rank,
            gender_revenue_rank,
            ROUND(revenue_percentile * 100, 1) AS revenue_percentile_pct,
            ROUND(revenue_cumulative_dist * 100, 1) AS cumulative_distribution_pct,
            CASE 
                WHEN revenue_percentile >= 0.9 THEN 'Top Performer (10%)'
                WHEN revenue_percentile >= 0.7 THEN 'High Performer (30%)'
                WHEN revenue_percentile >= 0.4 THEN 'Average Performer (40%)'
                WHEN revenue_percentile >= 0.2 THEN 'Below Average (20%)'
                ELSE 'Needs Improvement (Bottom 20%)'
            END AS performance_category,
            CASE 
                WHEN total_revenue > 0 
                THEN ROUND((total_discounts_given / total_revenue) * 100, 2)
                ELSE 0 
            END AS discount_percentage,
            cumulative_revenue
        FROM employee_rankings
        ORDER BY revenue_rank
        """
        
        try:
            self.logger.info(f"Ejecutando ranking avanzado de empleados - {months_back} meses")
            df = self._execute_query_with_fresh_connection(query, {"months_back": months_back})
            self.logger.info(f"Employee performance ranking retrieved: {len(df)} employees")
            return df
        except Exception as e:
            self.logger.error(f"Error executing employee performance ranking: {e}")
            return pd.DataFrame()
    
    def get_sales_trends_analysis(self, start_year: int = 2023, months_to_analyze: int = 24) -> pd.DataFrame:
        """
        Ejecuta análisis de tendencias con CTE recursivo y funciones ventana.
        
        Args:
            start_year: Año de inicio del análisis
            months_to_analyze: Número de meses a analizar
            
        Returns:
            DataFrame con análisis de tendencias mensuales
        """
        query = """
        WITH RECURSIVE date_series AS (
            SELECT 
                DATE(:start_date) AS month_start,
                LAST_DAY(:start_date) AS month_end,
                1 AS month_number
            
            UNION ALL
            
            SELECT 
                DATE_ADD(month_start, INTERVAL 1 MONTH),
                LAST_DAY(DATE_ADD(month_start, INTERVAL 1 MONTH)),
                month_number + 1
            FROM date_series
            WHERE month_number < :months_to_analyze
        ),
        monthly_sales_data AS (
            SELECT 
                ds.month_start,
                ds.month_end,
                ds.month_number,
                YEAR(ds.month_start) AS sales_year,
                MONTH(ds.month_start) AS sales_month,
                MONTHNAME(ds.month_start) AS month_name,
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
            SELECT 
                *,
                LAG(total_revenue, 1) OVER (ORDER BY month_start) AS prev_month_revenue,
                LAG(total_revenue, 12) OVER (ORDER BY month_start) AS same_month_prev_year,
                LEAD(total_revenue, 1) OVER (ORDER BY month_start) AS next_month_revenue,
                AVG(total_revenue) OVER (ORDER BY month_start ROWS 2 PRECEDING) AS moving_avg_3_months,
                AVG(total_revenue) OVER (ORDER BY month_start ROWS 5 PRECEDING) AS moving_avg_6_months,
                AVG(total_revenue) OVER (ORDER BY month_start ROWS 11 PRECEDING) AS moving_avg_12_months,
                SUM(total_revenue) OVER (ORDER BY month_start ROWS 2 PRECEDING) AS rolling_sum_3_months,
                SUM(total_revenue) OVER (PARTITION BY sales_year ORDER BY month_start) AS ytd_revenue,
                SUM(total_revenue) OVER (ORDER BY month_start) AS cumulative_revenue,
                STDDEV(total_revenue) OVER (ORDER BY month_start ROWS 11 PRECEDING) AS revenue_volatility_12m,
                ROW_NUMBER() OVER (PARTITION BY sales_month ORDER BY total_revenue DESC) AS month_performance_rank,
                PERCENT_RANK() OVER (PARTITION BY sales_month ORDER BY total_revenue) AS month_percentile
            FROM monthly_sales_data
        )
        SELECT 
            DATE_FORMAT(month_start, '%Y-%m') AS period,
            month_name,
            sales_year,
            total_revenue AS revenue,
            COALESCE(moving_avg_3_months, 0) AS avg_3m,
            COALESCE(moving_avg_12_months, 0) AS avg_12m,
            total_transactions,
            unique_customers,
            CASE 
                WHEN prev_month_revenue > 0 THEN 
                    ROUND(((total_revenue - prev_month_revenue) / prev_month_revenue) * 100, 2)
                ELSE NULL 
            END AS mom_growth_percent,
            CASE 
                WHEN same_month_prev_year > 0 THEN 
                    ROUND(((total_revenue - same_month_prev_year) / same_month_prev_year) * 100, 2)
                ELSE NULL 
            END AS yoy_growth_percent,
            CASE 
                WHEN moving_avg_12_months > 0 AND total_revenue > moving_avg_12_months THEN 'Above Trend'
                WHEN moving_avg_12_months > 0 AND total_revenue < moving_avg_12_months * 0.95 THEN 'Below Trend'
                ELSE 'On Trend'
            END AS trend_indicator,
            CASE 
                WHEN month_percentile >= 0.8 THEN 'Peak Season'
                WHEN month_percentile >= 0.6 THEN 'High Season'
                WHEN month_percentile >= 0.4 THEN 'Normal Season'
                WHEN month_percentile >= 0.2 THEN 'Low Season'
                ELSE 'Off Season'
            END AS seasonal_classification,
            CASE 
                WHEN ytd_revenue > 0 
                THEN ROUND((total_revenue / ytd_revenue) * 100, 2)
                ELSE 0 
            END AS month_contribution_to_ytd,
            CASE 
                WHEN revenue_volatility_12m IS NOT NULL 
                THEN ROUND(revenue_volatility_12m, 2) 
                ELSE NULL 
            END AS revenue_volatility
        FROM sales_with_trends
        WHERE month_start <= CURDATE()
        ORDER BY month_start
        """
        
        start_date = f"{start_year}-01-01"
        
        try:
            self.logger.info(f"Ejecutando análisis de tendencias - desde {start_year}, {months_to_analyze} meses")
            df = self._execute_query_with_fresh_connection(
                query, 
                {
                    "start_date": start_date,
                    "months_to_analyze": months_to_analyze
                }
            )
            self.logger.info(f"Sales trends analysis retrieved: {len(df)} months")
            return df
        except Exception as e:
            self.logger.error(f"Error executing sales trends analysis: {e}")
            return pd.DataFrame()
    
    # =====================================
    # GESTIÓN DE OBJETOS SQL
    # =====================================
    
    def create_advanced_sql_objects(self) -> Dict[str, bool]:
        """
        Crea todos los objetos SQL avanzados (funciones, triggers, vistas, procedimientos).
        
        Returns:
            Diccionario con el estado de creación de cada objeto
        """
        results = {}
        
        self.logger.info("Iniciando creación de objetos SQL avanzados")
        
        # Funciones
        results['function_calculate_commission'] = self._create_commission_function()
        results['function_classify_customer'] = self._create_customer_classification_function()
        
        # Vistas
        results['view_executive_dashboard'] = self._create_executive_dashboard_view()
        results['view_product_category_analysis'] = self._create_product_category_view()
        
        # Triggers
        results['trigger_sales_audit'] = self._create_sales_audit_triggers()
        results['trigger_sales_validation'] = self._create_sales_validation_trigger()
        
        # Procedimientos almacenados
        results['procedure_monthly_report'] = self._create_monthly_report_procedure()
        results['procedure_top_customers'] = self._create_top_customers_procedure()
        
        # Índices
        results['indexes_advanced'] = self._create_advanced_indexes()
        
        return results
    
    def _create_commission_function(self) -> bool:
        """Crea función para calcular comisiones."""
        query = """
        DROP FUNCTION IF EXISTS calculate_employee_commission;
        
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
            
            SELECT COALESCE(SUM(TotalPrice), 0) 
            INTO total_sales
            FROM sales 
            WHERE SalesPersonID = employee_id 
              AND SalesDate BETWEEN start_date AND end_date;
            
            CASE 
                WHEN total_sales >= 100000 THEN SET commission_rate = 0.08;
                WHEN total_sales >= 50000 THEN SET commission_rate = 0.06;
                WHEN total_sales >= 25000 THEN SET commission_rate = 0.04;
                WHEN total_sales >= 10000 THEN SET commission_rate = 0.03;
                ELSE SET commission_rate = 0.02;
            END CASE;
            
            SET final_commission = total_sales * commission_rate;
            
            RETURN final_commission;
        END
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Commission calculation function created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating commission function: {e}")
            return False
    
    def _create_customer_classification_function(self) -> bool:
        """Crea función para clasificar clientes."""
        query = """
        DROP FUNCTION IF EXISTS classify_customer_value;
        
        CREATE FUNCTION classify_customer_value(customer_id INT)
        RETURNS VARCHAR(20)
        READS SQL DATA
        DETERMINISTIC
        COMMENT 'Clasifica cliente por valor total de compras históricas'
        BEGIN
            DECLARE total_purchases DECIMAL(10,2) DEFAULT 0;
            DECLARE purchase_count INT DEFAULT 0;
            DECLARE customer_category VARCHAR(20) DEFAULT 'New';
            
            SELECT 
                COALESCE(SUM(TotalPrice), 0),
                COUNT(*)
            INTO total_purchases, purchase_count
            FROM sales 
            WHERE CustomerID = customer_id;
            
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
        END
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Customer classification function created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating customer classification function: {e}")
            return False
    
    def _create_executive_dashboard_view(self) -> bool:
        """Crea vista del dashboard ejecutivo."""
        query = """
        CREATE OR REPLACE VIEW executive_sales_dashboard AS
        SELECT 
            e.EmployeeID,
            CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
            e.Gender,
            TIMESTAMPDIFF(YEAR, e.HireDate, CURDATE()) AS years_experience,
            ct.CityName AS employee_city,
            co.CountryName AS employee_country,
            COUNT(s.SalesID) AS transactions_12m,
            COALESCE(SUM(s.TotalPrice), 0) AS revenue_12m,
            COALESCE(AVG(s.TotalPrice), 0) AS avg_transaction_value,
            COALESCE(SUM(s.Quantity), 0) AS items_sold_12m,
            COUNT(DISTINCT s.CustomerID) AS unique_customers_12m,
            COUNT(DISTINCT s.ProductID) AS unique_products_sold,
            COALESCE(SUM(s.Discount), 0) AS total_discounts_given,
            CASE 
                WHEN COALESCE(SUM(s.TotalPrice), 0) > 0 
                THEN ROUND((COALESCE(SUM(s.Discount), 0) / SUM(s.TotalPrice)) * 100, 2)
                ELSE 0 
            END AS discount_percentage,
            CASE 
                WHEN COALESCE(SUM(s.TotalPrice), 0) >= 100000 THEN 'Top Performer'
                WHEN COALESCE(SUM(s.TotalPrice), 0) >= 50000 THEN 'High Performer'
                WHEN COALESCE(SUM(s.TotalPrice), 0) >= 25000 THEN 'Average Performer'
                WHEN COALESCE(SUM(s.TotalPrice), 0) >= 10000 THEN 'Developing'
                ELSE 'New/Learning'
            END AS performance_tier,
            CASE 
                WHEN COUNT(s.SalesID) > 0 
                THEN ROUND(COALESCE(SUM(s.TotalPrice), 0) / COUNT(s.SalesID), 2)
                ELSE 0 
            END AS revenue_per_transaction,
            CASE 
                WHEN COALESCE(SUM(s.Quantity), 0) > 0 
                THEN ROUND(COALESCE(SUM(s.TotalPrice), 0) / SUM(s.Quantity), 2)
                ELSE 0 
            END AS revenue_per_item,
            MAX(s.SalesDate) AS last_sale_date,
            CASE 
                WHEN MAX(s.SalesDate) IS NOT NULL 
                THEN DATEDIFF(CURDATE(), MAX(s.SalesDate))
                ELSE NULL 
            END AS days_since_last_sale
        FROM employees e
        LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID 
                         AND s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        LEFT JOIN cities ct ON e.CityID = ct.CityID
        LEFT JOIN countries co ON ct.CountryID = co.CountryID
        GROUP BY e.EmployeeID, e.FirstName, e.LastName, e.Gender, e.HireDate, 
                 ct.CityName, co.CountryName
        ORDER BY revenue_12m DESC
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Executive dashboard view created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating executive dashboard view: {e}")
            return False
    
    def _create_product_category_view(self) -> bool:
        """Crea vista de análisis por categoría de productos."""
        query = """
        CREATE OR REPLACE VIEW product_category_analysis AS
        SELECT 
            cat.CategoryID,
            cat.CategoryName,
            COUNT(DISTINCT p.ProductID) AS total_products,
            COUNT(DISTINCT CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                               THEN p.ProductID END) AS active_products_12m,
            COALESCE(SUM(CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                             THEN s.TotalPrice END), 0) AS total_revenue_12m,
            COALESCE(SUM(CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                             THEN s.Quantity END), 0) AS total_quantity_sold,
            COUNT(CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                      THEN s.SalesID END) AS total_transactions,
            COALESCE(AVG(CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                             THEN s.TotalPrice END), 0) AS avg_transaction_value,
            COALESCE(MIN(p.Price), 0) AS min_product_price,
            COALESCE(MAX(p.Price), 0) AS max_product_price,
            COALESCE(AVG(p.Price), 0) AS avg_product_price,
            CASE 
                WHEN (SELECT SUM(TotalPrice) FROM sales 
                      WHERE SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)) > 0
                THEN ROUND(
                    (COALESCE(SUM(CASE WHEN s.SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH) 
                                      THEN s.TotalPrice END), 0) / 
                     (SELECT SUM(TotalPrice) FROM sales 
                      WHERE SalesDate >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH))) * 100, 2)
                ELSE 0 
            END AS revenue_share_percent
        FROM categories cat
        LEFT JOIN products p ON cat.CategoryID = p.CategoryID
        LEFT JOIN sales s ON p.ProductID = s.ProductID
        GROUP BY cat.CategoryID, cat.CategoryName
        ORDER BY total_revenue_12m DESC
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Product category analysis view created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating product category view: {e}")
            return False
    
    def _create_sales_audit_triggers(self) -> bool:
        """Crea tabla de auditoría y triggers."""
        try:
            # Crear tabla de auditoría
            audit_table_query = """
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
            )
            """
            
            if not self._execute_sql_command_with_fresh_connection(audit_table_query):
                return False
            
            # Triggers
            insert_trigger = """
            DROP TRIGGER IF EXISTS sales_audit_insert;
            
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
            END
            """
            
            if not self._execute_sql_command_with_fresh_connection(insert_trigger):
                return False
            
            update_trigger = """
            DROP TRIGGER IF EXISTS sales_audit_update;
            
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
            END
            """
            
            result = self._execute_sql_command_with_fresh_connection(update_trigger)
            if result:
                self.logger.info("Sales audit triggers created successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating sales audit triggers: {e}")
            return False
    
    def _create_sales_validation_trigger(self) -> bool:
        """Crea trigger de validación de ventas."""
        query = """
        DROP TRIGGER IF EXISTS sales_validation_trigger;
        
        CREATE TRIGGER sales_validation_trigger
            BEFORE INSERT ON sales
            FOR EACH ROW
        BEGIN
            DECLARE product_price DECIMAL(10,2);
            DECLARE calculated_total DECIMAL(10,2);
            DECLARE error_message VARCHAR(255);
            
            SELECT Price INTO product_price 
            FROM products 
            WHERE ProductID = NEW.ProductID;
            
            IF product_price IS NULL THEN
                SET error_message = CONCAT('Product ID ', NEW.ProductID, ' does not exist');
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
            END IF;
            
            SET calculated_total = (NEW.Quantity * product_price) - NEW.Discount;
            
            IF ABS(NEW.TotalPrice - calculated_total) > 0.01 THEN
                SET error_message = CONCAT('Invalid total price. Expected: ', calculated_total, ', Got: ', NEW.TotalPrice);
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = error_message;
            END IF;
            
            IF NEW.Quantity <= 0 THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantity must be positive';
            END IF;
            
            IF NEW.Discount > (NEW.Quantity * product_price * 0.5) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Discount cannot exceed 50% of subtotal';
            END IF;
        END
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Sales validation trigger created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating sales validation trigger: {e}")
            return False
    
    def _create_monthly_report_procedure(self) -> bool:
        """Crea procedimiento almacenado para reporte mensual."""
        query = """
        DROP PROCEDURE IF EXISTS generate_monthly_performance_report;
        
        CREATE PROCEDURE generate_monthly_performance_report(
            IN report_year INT,
            IN report_month INT,
            IN min_revenue DECIMAL(10,2) DEFAULT 0
        )
        COMMENT 'Genera reporte detallado de rendimiento mensual por empleado'
        BEGIN
            DECLARE start_date DATE;
            DECLARE end_date DATE;
            
            SET start_date = DATE(CONCAT(report_year, '-', LPAD(report_month, 2, '0'), '-01'));
            SET end_date = LAST_DAY(start_date);
            
            SELECT 
                ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(s.TotalPrice), 0) DESC) AS ranking,
                e.EmployeeID,
                CONCAT(e.FirstName, ' ', e.LastName) AS employee_name,
                COUNT(s.SalesID) AS transactions,
                COALESCE(SUM(s.TotalPrice), 0) AS revenue,
                COALESCE(AVG(s.TotalPrice), 0) AS avg_transaction,
                COALESCE(SUM(s.Quantity), 0) AS items_sold,
                COUNT(DISTINCT s.CustomerID) AS unique_customers,
                CASE 
                    WHEN (SELECT SUM(TotalPrice) FROM sales 
                          WHERE SalesDate BETWEEN start_date AND end_date) > 0
                    THEN ROUND(
                        (COALESCE(SUM(s.TotalPrice), 0) / 
                         (SELECT SUM(TotalPrice) FROM sales 
                          WHERE SalesDate BETWEEN start_date AND end_date)) * 100, 2)
                    ELSE 0 
                END AS revenue_share_percent,
                CASE 
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 10000 THEN 'Excellent'
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 5000 THEN 'Good'
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 2000 THEN 'Average'
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 500 THEN 'Below Average'
                    ELSE 'Poor'
                END AS performance_rating
            FROM employees e
            LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID 
                             AND s.SalesDate BETWEEN start_date AND end_date
            GROUP BY e.EmployeeID, e.FirstName, e.LastName
            HAVING COALESCE(SUM(s.TotalPrice), 0) >= min_revenue
            ORDER BY revenue DESC;
        END
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Monthly performance report procedure created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating monthly report procedure: {e}")
            return False
    
    def _create_top_customers_procedure(self) -> bool:
        """Crea procedimiento almacenado para análisis de mejores clientes."""
        query = """
        DROP PROCEDURE IF EXISTS analyze_top_customers;
        
        CREATE PROCEDURE analyze_top_customers(
            IN top_n INT DEFAULT 20,
            IN analysis_months INT DEFAULT 12
        )
        COMMENT 'Analiza los mejores clientes por valor y frecuencia'
        BEGIN
            DECLARE analysis_start_date DATE;
            SET analysis_start_date = DATE_SUB(CURDATE(), INTERVAL analysis_months MONTH);
            
            SELECT 
                ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(s.TotalPrice), 0) DESC) AS customer_rank,
                c.CustomerID,
                CONCAT(c.FirstName, ' ', c.LastName) AS customer_name,
                ct.CityName,
                co.CountryName,
                COUNT(s.SalesID) AS total_purchases,
                COALESCE(SUM(s.TotalPrice), 0) AS total_spent,
                COALESCE(AVG(s.TotalPrice), 0) AS avg_purchase_value,
                COALESCE(SUM(s.Quantity), 0) AS total_items_purchased,
                MIN(s.SalesDate) AS first_purchase_date,
                MAX(s.SalesDate) AS last_purchase_date,
                CASE 
                    WHEN MIN(s.SalesDate) IS NOT NULL AND MAX(s.SalesDate) IS NOT NULL
                    THEN DATEDIFF(MAX(s.SalesDate), MIN(s.SalesDate))
                    ELSE 0 
                END AS customer_lifetime_days,
                CASE 
                    WHEN MAX(s.SalesDate) IS NOT NULL
                    THEN DATEDIFF(CURDATE(), MAX(s.SalesDate))
                    ELSE NULL 
                END AS days_since_last_purchase,
                CASE 
                    WHEN MIN(s.SalesDate) IS NOT NULL AND DATEDIFF(CURDATE(), MIN(s.SalesDate)) > 0
                    THEN ROUND(COUNT(s.SalesID) / (DATEDIFF(CURDATE(), MIN(s.SalesDate)) / 30), 2)
                    ELSE 0 
                END AS avg_purchases_per_month,
                COUNT(DISTINCT s.ProductID) AS unique_products_purchased,
                COUNT(DISTINCT p.CategoryID) AS unique_categories_purchased
            FROM customers c
            INNER JOIN sales s ON c.CustomerID = s.CustomerID 
                              AND s.SalesDate >= analysis_start_date
            INNER JOIN cities ct ON c.CityID = ct.CityID
            INNER JOIN countries co ON ct.CountryID = co.CountryID
            INNER JOIN products p ON s.ProductID = p.ProductID
            GROUP BY c.CustomerID, c.FirstName, c.LastName, ct.CityName, co.CountryName
            ORDER BY total_spent DESC
            LIMIT top_n;
        END
        """
        
        try:
            result = self._execute_sql_command_with_fresh_connection(query)
            if result:
                self.logger.info("Top customers analysis procedure created successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error creating top customers procedure: {e}")
            return False
    
    def _create_advanced_indexes(self) -> bool:
        """Crea índices adicionales para optimización."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_sales_date_employee ON sales(SalesDate, SalesPersonID)",
            "CREATE INDEX IF NOT EXISTS idx_sales_date_customer_product ON sales(SalesDate, CustomerID, ProductID)",
            "CREATE INDEX IF NOT EXISTS idx_sales_totalprice_date ON sales(TotalPrice, SalesDate)",
            "CREATE INDEX IF NOT EXISTS idx_customer_name ON customers(FirstName, LastName)",
            "CREATE INDEX IF NOT EXISTS idx_employee_name ON employees(FirstName, LastName)",
            "CREATE INDEX IF NOT EXISTS idx_product_name_category ON products(ProductName, CategoryID)",
            "CREATE INDEX IF NOT EXISTS idx_employee_hiredate ON employees(HireDate)",
            "CREATE INDEX IF NOT EXISTS idx_sales_discount ON sales(Discount)"
        ]
        
        try:
            for index_query in indexes:
                if not self._execute_sql_command_with_fresh_connection(index_query):
                    return False
            self.logger.info("Advanced indexes created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error creating advanced indexes: {e}")
            return False
    
    # =====================================
    # MÉTODOS PARA USAR OBJETOS SQL CREADOS
    # =====================================
    
    def get_executive_dashboard(self) -> pd.DataFrame:
        """Obtiene datos del dashboard ejecutivo usando la vista creada."""
        query = "SELECT * FROM executive_sales_dashboard"
        try:
            self.logger.info("Obteniendo dashboard ejecutivo desde vista")
            df = self._execute_query_with_fresh_connection(query)
            self.logger.info(f"Executive dashboard data retrieved: {len(df)} employees")
            return df
        except Exception as e:
            self.logger.error(f"Error retrieving executive dashboard: {e}")
            return pd.DataFrame()
    
    def get_product_category_analysis(self) -> pd.DataFrame:
        """Obtiene análisis por categoría usando la vista creada."""
        query = "SELECT * FROM product_category_analysis"
        try:
            self.logger.info("Obteniendo análisis de categorías desde vista")
            df = self._execute_query_with_fresh_connection(query)
            self.logger.info(f"Product category analysis retrieved: {len(df)} categories")
            return df
        except Exception as e:
            self.logger.error(f"Error retrieving product category analysis: {e}")
            return pd.DataFrame()
    
    def calculate_employee_commission(self, employee_id: int, start_date: date, end_date: date) -> float:
        """Calcula comisión usando la función SQL creada."""
        query = """
        SELECT calculate_employee_commission(:employee_id, :start_date, :end_date) AS commission
        """
        try:
            self.logger.info(f"Calculando comisión para empleado {employee_id}")
            result = self._execute_query_with_fresh_connection(
                query, 
                {
                    "employee_id": employee_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            commission = result.iloc[0]['commission'] if len(result) > 0 else 0
            self.logger.info(f"Commission calculated for employee {employee_id}: {commission}")
            return float(commission) if commission else 0.0
        except Exception as e:
            self.logger.error(f"Error calculating commission: {e}")
            return 0.0
    
    def classify_customer_value(self, customer_id: int) -> str:
        """Clasifica cliente usando la función SQL creada."""
        query = "SELECT classify_customer_value(:customer_id) AS customer_tier"
        try:
            self.logger.info(f"Clasificando cliente {customer_id}")
            result = self._execute_query_with_fresh_connection(
                query, 
                {"customer_id": customer_id}
            )
            tier = result.iloc[0]['customer_tier'] if len(result) > 0 else 'New'
            self.logger.info(f"Customer {customer_id} classified as: {tier}")
            return tier
        except Exception as e:
            self.logger.error(f"Error classifying customer: {e}")
            return 'New'
    
    def generate_monthly_report(self, year: int, month: int, min_revenue: float = 0) -> pd.DataFrame:
        """Genera reporte mensual usando el procedimiento almacenado."""
        query = "CALL generate_monthly_performance_report(:year, :month, :min_revenue)"
        try:
            self.logger.info(f"Generando reporte mensual {year}-{month:02d}")
            df = self._execute_query_with_fresh_connection(
                query, 
                {
                    "year": year,
                    "month": month,
                    "min_revenue": min_revenue
                }
            )
            self.logger.info(f"Monthly report generated for {year}-{month:02d}: {len(df)} employees")
            return df
        except Exception as e:
            self.logger.error(f"Error generating monthly report: {e}")
            return pd.DataFrame()
    
    def analyze_top_customers(self, top_n: int = 20, analysis_months: int = 12) -> pd.DataFrame:
        """Analiza mejores clientes usando el procedimiento almacenado."""
        query = "CALL analyze_top_customers(:top_n, :analysis_months)"
        try:
            self.logger.info(f"Analizando top {top_n} clientes")
            df = self._execute_query_with_fresh_connection(
                query, 
                {
                    "top_n": top_n,
                    "analysis_months": analysis_months
                }
            )
            self.logger.info(f"Top customers analysis completed: {len(df)} customers")
            return df
        except Exception as e:
            self.logger.error(f"Error analyzing top customers: {e}")
            return pd.DataFrame()
    
    def get_sales_audit_log(self, days_back: int = 30) -> pd.DataFrame:
        """Obtiene registro de auditoría de ventas."""
        query = """
        SELECT 
            audit_id,
            sales_id,
            action_type,
            old_total_price,
            new_total_price,
            old_quantity,
            new_quantity,
            changed_by,
            change_timestamp,
            change_details
        FROM sales_audit 
        WHERE change_timestamp >= DATE_SUB(CURDATE(), INTERVAL :days_back DAY)
        ORDER BY change_timestamp DESC
        """
        try:
            self.logger.info(f"Obteniendo log de auditoría - últimos {days_back} días")
            df = self._execute_query_with_fresh_connection(query, {"days_back": days_back})
            self.logger.info(f"Sales audit log retrieved: {len(df)} entries")
            return df
        except Exception as e:
            self.logger.error(f"Error retrieving sales audit log: {e}")
            return pd.DataFrame()


# =====================================
# FUNCIONES DE UTILIDAD PARA EL NOTEBOOK
# =====================================

def setup_advanced_analytics() -> AdvancedAnalyticsService:
    """
    Configura e inicializa el servicio de análisis avanzado.
    Para usar en el notebook.
    """
    service = AdvancedAnalyticsService()
    
    print("🚀 Configurando objetos SQL avanzados...")
    results = service.create_advanced_sql_objects()
    
    print("\n📊 Resultados de la configuración:")
    for obj_name, success in results.items():
        status = "✅ Éxito" if success else "❌ Error"
        print(f"  {obj_name}: {status}")
    
    print("\n🎉 Servicio de análisis avanzado listo para usar!")
    return service