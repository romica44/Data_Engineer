from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.database.connection import DatabaseConnection
import logging

class AnalyticsService:
    """Servicio para análisis avanzados de datos de ventas"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = logging.getLogger(__name__)
    
    def get_sales_performance_by_employee(self, start_date: datetime = None, 
                                        end_date: datetime = None) -> List[Dict]:
        """Analiza el rendimiento de ventas por empleado"""
        try:
            where_clause = ""
            params = []
            
            if start_date and end_date:
                where_clause = "WHERE s.SalesDate BETWEEN %s AND %s"
                params = [start_date, end_date]
            
            query = f"""
            SELECT 
                e.EmployeeID,
                CONCAT(e.FirstName, ' ', e.LastName) as employee_name,
                COUNT(s.SalesID) as total_sales,
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.TotalPrice) as avg_sale_amount,
                SUM(s.Quantity) as total_units_sold,
                COUNT(DISTINCT s.CustomerID) as unique_customers_served,
                RANK() OVER (ORDER BY SUM(s.TotalPrice) DESC) as revenue_rank
            FROM employees e
            LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID
            {where_clause}
            GROUP BY e.EmployeeID, e.FirstName, e.LastName
            ORDER BY total_revenue DESC
            """
            
            return self.db.execute_query(query, params)
        except Exception as e:
            self.logger.error(f"Error en análisis de rendimiento de empleados: {e}")
            return []
    
    def get_geographic_sales_analysis(self) -> List[Dict]:
        """Análisis geográfico de ventas por país y ciudad"""
        try:
            query = """
            SELECT 
                co.CountryName,
                ci.CityName,
                COUNT(s.SalesID) as total_sales,
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.TotalPrice) as avg_sale_amount,
                COUNT(DISTINCT s.CustomerID) as unique_customers,
                COUNT(DISTINCT s.ProductID) as products_sold
            FROM sales s
            JOIN customers cu ON s.CustomerID = cu.CustomerID
            JOIN cities ci ON cu.CityID = ci.CityID
            JOIN countries co ON ci.CountryID = co.CountryID
            GROUP BY co.CountryID, ci.CityID, co.CountryName, ci.CityName
            ORDER BY co.CountryName, total_revenue DESC
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error en análisis geográfico: {e}")
            return []
    
    def get_product_performance_analysis(self) -> List[Dict]:
        """Análisis de rendimiento de productos"""
        try:
            query = """
            SELECT 
                p.ProductID,
                p.ProductName,
                c.CategoryName,
                p.Class as product_class,
                COUNT(s.SalesID) as total_sales,
                SUM(s.Quantity) as total_units_sold,
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.TotalPrice) as avg_sale_amount,
                COUNT(DISTINCT s.CustomerID) as unique_customers,
                p.Price as current_price,
                ROUND((SUM(s.TotalPrice) / SUM(s.Quantity)), 2) as avg_selling_price
            FROM products p
            LEFT JOIN sales s ON p.ProductID = s.ProductID
            LEFT JOIN categories c ON p.CategoryID = c.CategoryID
            GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.Class, p.Price
            ORDER BY total_revenue DESC
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error en análisis de productos: {e}")
            return []
    
    def get_customer_segmentation(self) -> List[Dict]:
        """Segmentación de clientes basada en comportamiento de compra"""
        try:
            query = """
            SELECT 
                c.CustomerID,
                CONCAT(c.FirstName, ' ', c.LastName) as customer_name,
                ci.CityName,
                co.CountryName,
                COUNT(s.SalesID) as total_purchases,
                SUM(s.TotalPrice) as total_spent,
                AVG(s.TotalPrice) as avg_purchase_amount,
                MAX(s.SalesDate) as last_purchase_date,
                DATEDIFF(CURDATE(), MAX(s.SalesDate)) as days_since_last_purchase,
                CASE 
                    WHEN SUM(s.TotalPrice) >= 500 THEN 'High Value'
                    WHEN SUM(s.TotalPrice) >= 200 THEN 'Medium Value'
                    ELSE 'Low Value'
                END as customer_segment,
                CASE 
                    WHEN COUNT(s.SalesID) >= 10 THEN 'Frequent'
                    WHEN COUNT(s.SalesID) >= 5 THEN 'Regular'
                    ELSE 'Occasional'
                END as purchase_frequency
            FROM customers c
            LEFT JOIN sales s ON c.CustomerID = s.CustomerID
            LEFT JOIN cities ci ON c.CityID = ci.CityID
            LEFT JOIN countries co ON ci.CountryID = co.CountryID
            GROUP BY c.CustomerID, c.FirstName, c.LastName, ci.CityName, co.CountryName
            ORDER BY total_spent DESC
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error en segmentación de clientes: {e}")
            return []
    
    def get_sales_trends_by_period(self, period: str = 'daily') -> List[Dict]:
        """Análisis de tendencias de ventas por período"""
        try:
            if period == 'daily':
                date_format = '%Y-%m-%d'
                group_by = 'DATE(s.SalesDate)'
            elif period == 'monthly':
                date_format = '%Y-%m'
                group_by = 'DATE_FORMAT(s.SalesDate, "%Y-%m")'
            else:
                raise ValueError("Período debe ser 'daily' o 'monthly'")
            
            query = f"""
            SELECT 
                DATE_FORMAT(s.SalesDate, '{date_format}') as period,
                COUNT(s.SalesID) as total_sales,
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.TotalPrice) as avg_sale_amount,
                SUM(s.Quantity) as total_units_sold,
                COUNT(DISTINCT s.CustomerID) as unique_customers
            FROM sales s
            GROUP BY {group_by}
            ORDER BY period
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error en análisis de tendencias: {e}")
            return []
    
    def get_discount_effectiveness_analysis(self) -> List[Dict]:
        """Análisis de efectividad de descuentos"""
        try:
            query = """
            SELECT 
                CASE 
                    WHEN s.Discount = 0 THEN 'No Discount'
                    WHEN s.Discount <= 0.05 THEN '1-5%'
                    WHEN s.Discount <= 0.10 THEN '6-10%'
                    WHEN s.Discount <= 0.15 THEN '11-15%'
                    WHEN s.Discount <= 0.20 THEN '16-20%'
                    ELSE 'More than 20%'
                END as discount_range,
                COUNT(s.SalesID) as total_sales,
                AVG(s.TotalPrice) as avg_sale_amount,
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.Quantity) as avg_quantity,
                COUNT(DISTINCT s.CustomerID) as unique_customers
            FROM sales s
            GROUP BY discount_range
            ORDER BY 
                CASE 
                    WHEN s.Discount = 0 THEN 0
                    WHEN s.Discount <= 0.05 THEN 1
                    WHEN s.Discount <= 0.10 THEN 2
                    WHEN s.Discount <= 0.15 THEN 3
                    WHEN s.Discount <= 0.20 THEN 4
                    ELSE 5
                END
            """
            
            return self.db.execute_query(query)
        except Exception as e:
            self.logger.error(f"Error en análisis de descuentos: {e}")
            return []
    
    def generate_executive_dashboard(self) -> Dict:
        """Genera un dashboard ejecutivo con métricas clave"""
        try:
            # Métricas generales
            general_metrics = self.db.execute_query("""
                SELECT 
                    COUNT(SalesID) as total_sales,
                    SUM(TotalPrice) as total_revenue,
                    AVG(TotalPrice) as avg_sale_amount,
                    COUNT(DISTINCT CustomerID) as unique_customers,
                    COUNT(DISTINCT ProductID) as products_sold
                FROM sales
            """)[0]
            
            # Top 5 productos
            top_products = self.db.execute_query("""
                SELECT p.ProductName, SUM(s.TotalPrice) as revenue
                FROM sales s
                JOIN products p ON s.ProductID = p.ProductID
                GROUP BY p.ProductID, p.ProductName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            
            # Top 5 empleados
            top_employees = self.db.execute_query("""
                SELECT CONCAT(e.FirstName, ' ', e.LastName) as employee_name, 
                       SUM(s.TotalPrice) as revenue
                FROM sales s
                JOIN employees e ON s.SalesPersonID = e.EmployeeID
                GROUP BY e.EmployeeID, e.FirstName, e.LastName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            
            # Ventas por país
            sales_by_country = self.db.execute_query("""
                SELECT co.CountryName, SUM(s.TotalPrice) as revenue
                FROM sales s
                JOIN customers cu ON s.CustomerID = cu.CustomerID
                JOIN cities ci ON cu.CityID = ci.CityID
                JOIN countries co ON ci.CountryID = co.CountryID
                GROUP BY co.CountryID, co.CountryName
                ORDER BY revenue DESC
            """)
            
            return {
                'general_metrics': general_metrics,
                'top_products': top_products,
                'top_employees': top_employees,
                'sales_by_country': sales_by_country
            }
        except Exception as e:
            self.logger.error(f"Error generando dashboard ejecutivo: {e}")
            return {}