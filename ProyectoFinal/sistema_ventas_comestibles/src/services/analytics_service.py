from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from src.database.connection import DatabaseConnection
import logging

class AnalyticsService:
    """Servicio para análisis avanzados de datos de ventas"""
    
    def __init__(self):
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
            self.logger.error(f"Error ejecutando consulta: {e}")
            return pd.DataFrame()
    
    def get_sales_performance_by_employee(self, start_date: datetime = None, 
                                        end_date: datetime = None) -> pd.DataFrame:
        """
        Analiza el rendimiento de ventas por empleado
        
        Args:
            start_date (datetime, optional): Fecha de inicio del análisis
            end_date (datetime, optional): Fecha de fin del análisis
            
        Returns:
            pd.DataFrame: DataFrame con el rendimiento de cada empleado
        """
        try:
            where_clause = ""
            params = {}
            
            if start_date and end_date:
                where_clause = "WHERE s.SalesDate BETWEEN :start_date AND :end_date"
                params = {'start_date': start_date, 'end_date': end_date}
            
            query = f"""
            SELECT 
                e.EmployeeID,
                CONCAT(e.FirstName, ' ', e.LastName) as employee_name,
                COUNT(s.SalesID) as total_sales,
                COALESCE(SUM(s.TotalPrice), 0) as total_revenue,
                COALESCE(AVG(s.TotalPrice), 0) as avg_sale_amount,
                COALESCE(SUM(s.Quantity), 0) as total_units_sold,
                COUNT(DISTINCT s.CustomerID) as unique_customers_served,
                RANK() OVER (ORDER BY COALESCE(SUM(s.TotalPrice), 0) DESC) as revenue_rank
            FROM employees e
            LEFT JOIN sales s ON e.EmployeeID = s.SalesPersonID
            {where_clause}
            GROUP BY e.EmployeeID, e.FirstName, e.LastName
            ORDER BY total_revenue DESC
            """
            
            self.logger.info("Ejecutando análisis de rendimiento de empleados")
            return self._execute_query_with_fresh_connection(query, params)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de rendimiento de empleados: {e}")
            return pd.DataFrame()
    
    def get_geographic_sales_analysis(self) -> pd.DataFrame:
        """
        Análisis geográfico de ventas por país y ciudad
        
        Returns:
            pd.DataFrame: DataFrame con análisis geográfico de ventas
        """
        try:
            query = """
            SELECT 
                co.CountryName,
                ci.CityName,
                COUNT(s.SalesID) as total_sales,
                COALESCE(SUM(s.TotalPrice), 0) as total_revenue,
                COALESCE(AVG(s.TotalPrice), 0) as avg_sale_amount,
                COUNT(DISTINCT s.CustomerID) as unique_customers,
                COUNT(DISTINCT s.ProductID) as products_sold
            FROM sales s
            JOIN customers cu ON s.CustomerID = cu.CustomerID
            JOIN cities ci ON cu.CityID = ci.CityID
            JOIN countries co ON ci.CountryID = co.CountryID
            GROUP BY co.CountryID, ci.CityID, co.CountryName, ci.CityName
            ORDER BY co.CountryName, total_revenue DESC
            """
            
            self.logger.info("Ejecutando análisis geográfico")
            return self._execute_query_with_fresh_connection(query)
            
        except Exception as e:
            self.logger.error(f"Error en análisis geográfico: {e}")
            return pd.DataFrame()
    
    def get_product_performance_analysis(self) -> pd.DataFrame:
        """
        Análisis de rendimiento de productos
        
        Returns:
            pd.DataFrame: DataFrame con análisis de rendimiento de productos
        """
        try:
            query = """
            SELECT 
                p.ProductID,
                p.ProductName,
                c.CategoryName,
                p.Class as product_class,
                COUNT(s.SalesID) as total_sales,
                COALESCE(SUM(s.Quantity), 0) as total_units_sold,
                COALESCE(SUM(s.TotalPrice), 0) as total_revenue,
                COALESCE(AVG(s.TotalPrice), 0) as avg_sale_amount,
                COUNT(DISTINCT s.CustomerID) as unique_customers,
                p.Price as current_price,
                CASE 
                    WHEN COALESCE(SUM(s.Quantity), 0) > 0 
                    THEN ROUND((COALESCE(SUM(s.TotalPrice), 0) / SUM(s.Quantity)), 2)
                    ELSE 0 
                END as avg_selling_price
            FROM products p
            LEFT JOIN sales s ON p.ProductID = s.ProductID
            LEFT JOIN categories c ON p.CategoryID = c.CategoryID
            GROUP BY p.ProductID, p.ProductName, c.CategoryName, p.Class, p.Price
            ORDER BY total_revenue DESC
            """
            
            self.logger.info("Ejecutando análisis de productos")
            return self._execute_query_with_fresh_connection(query)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de productos: {e}")
            return pd.DataFrame()
    
    def get_customer_segmentation(self) -> pd.DataFrame:
        """
        Segmentación de clientes basada en comportamiento de compra
        
        Returns:
            pd.DataFrame: DataFrame con segmentación de clientes
        """
        try:
            query = """
            SELECT 
                c.CustomerID,
                CONCAT(c.FirstName, ' ', c.LastName) as customer_name,
                ci.CityName,
                co.CountryName,
                COUNT(s.SalesID) as total_purchases,
                COALESCE(SUM(s.TotalPrice), 0) as total_spent,
                COALESCE(AVG(s.TotalPrice), 0) as avg_purchase_amount,
                MAX(s.SalesDate) as last_purchase_date,
                CASE 
                    WHEN MAX(s.SalesDate) IS NOT NULL 
                    THEN DATEDIFF(CURDATE(), MAX(s.SalesDate))
                    ELSE NULL 
                END as days_since_last_purchase,
                CASE 
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 500 THEN 'High Value'
                    WHEN COALESCE(SUM(s.TotalPrice), 0) >= 200 THEN 'Medium Value'
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
            
            self.logger.info("Ejecutando segmentación de clientes")
            return self._execute_query_with_fresh_connection(query)
            
        except Exception as e:
            self.logger.error(f"Error en segmentación de clientes: {e}")
            return pd.DataFrame()
    
    def get_sales_trends_by_period(self, period: str = 'daily') -> pd.DataFrame:
        """
        Análisis de tendencias de ventas por período
        
        Args:
            period (str): Período de análisis ('daily' o 'monthly')
            
        Returns:
            pd.DataFrame: DataFrame con tendencias de ventas
        """
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
                COALESCE(SUM(s.TotalPrice), 0) as total_revenue,
                COALESCE(AVG(s.TotalPrice), 0) as avg_sale_amount,
                COALESCE(SUM(s.Quantity), 0) as total_units_sold,
                COUNT(DISTINCT s.CustomerID) as unique_customers
            FROM sales s
            GROUP BY {group_by}
            ORDER BY period
            """
            
            self.logger.info(f"Ejecutando análisis de tendencias - período: {period}")
            return self._execute_query_with_fresh_connection(query)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de tendencias: {e}")
            return pd.DataFrame()
    
    def get_discount_effectiveness_analysis(self) -> pd.DataFrame:
        """
        Análisis de efectividad de descuentos
        
        Returns:
            pd.DataFrame: DataFrame con análisis de efectividad de descuentos
        """
        try:
            query = """
            SELECT 
                CASE 
                    WHEN s.Discount = 0 THEN 'No Discount'
                    WHEN s.Discount <= 5 THEN '1% - 5%'
                    WHEN s.Discount <= 10 THEN '6% - 10%'
                    WHEN s.Discount <= 15 THEN '11% - 15%'
                    WHEN s.Discount <= 20 THEN '16% - 20%'
                    ELSE '> 20%'
                END as discount_range,
                COUNT(s.SalesID) as total_sales,
                COALESCE(AVG(s.TotalPrice), 0) as avg_sale_amount,
                COALESCE(SUM(s.TotalPrice), 0) as total_revenue,
                COALESCE(AVG(s.Quantity), 0) as avg_quantity,
                COUNT(DISTINCT s.CustomerID) as unique_customers
            FROM sales s
            GROUP BY discount_range
            ORDER BY 
                CASE 
                    WHEN s.Discount = 0 THEN 0
                    WHEN s.Discount <= 5 THEN 1
                    WHEN s.Discount <= 10 THEN 2
                    WHEN s.Discount <= 15 THEN 3
                    WHEN s.Discount <= 20 THEN 4
                    ELSE 5
                END
            """
            
            self.logger.info("Ejecutando análisis de descuentos")
            return self._execute_query_with_fresh_connection(query)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de descuentos: {e}")
            return pd.DataFrame()
    
    def generate_executive_dashboard(self) -> Dict:
        """
        Genera un dashboard ejecutivo con métricas clave
        
        Returns:
            dict: Dashboard con métricas clave
        """
        try:
            self.logger.info("Generando dashboard ejecutivo")
            
            # Métricas generales
            general_metrics_df = self._execute_query_with_fresh_connection("""
                SELECT 
                    COUNT(SalesID) as total_sales,
                    COALESCE(SUM(TotalPrice), 0) as total_revenue,
                    COALESCE(AVG(TotalPrice), 0) as avg_sale_amount,
                    COUNT(DISTINCT CustomerID) as unique_customers,
                    COUNT(DISTINCT ProductID) as products_sold
                FROM sales
            """)
            general_metrics = general_metrics_df.iloc[0].to_dict() if len(general_metrics_df) > 0 else {}
            
            # Top 5 productos
            top_products_df = self._execute_query_with_fresh_connection("""
                SELECT p.ProductName, COALESCE(SUM(s.TotalPrice), 0) as revenue
                FROM sales s
                JOIN products p ON s.ProductID = p.ProductID
                GROUP BY p.ProductID, p.ProductName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            top_products = top_products_df.to_dict('records') if len(top_products_df) > 0 else []
            
            # Top 5 empleados
            top_employees_df = self._execute_query_with_fresh_connection("""
                SELECT CONCAT(e.FirstName, ' ', e.LastName) as employee_name, 
                       COALESCE(SUM(s.TotalPrice), 0) as revenue
                FROM sales s
                JOIN employees e ON s.SalesPersonID = e.EmployeeID
                GROUP BY e.EmployeeID, e.FirstName, e.LastName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            top_employees = top_employees_df.to_dict('records') if len(top_employees_df) > 0 else []
            
            # Ventas por país
            sales_by_country_df = self._execute_query_with_fresh_connection("""
                SELECT co.CountryName, COALESCE(SUM(s.TotalPrice), 0) as revenue
                FROM sales s
                JOIN customers cu ON s.CustomerID = cu.CustomerID
                JOIN cities ci ON cu.CityID = ci.CityID
                JOIN countries co ON ci.CountryID = co.CountryID
                GROUP BY co.CountryID, co.CountryName
                ORDER BY revenue DESC
            """)
            sales_by_country = sales_by_country_df.to_dict('records') if len(sales_by_country_df) > 0 else []
            
            return {
                'general_metrics': general_metrics,
                'top_products': top_products,
                'top_employees': top_employees,
                'sales_by_country': sales_by_country
            }
            
        except Exception as e:
            self.logger.error(f"Error generando dashboard ejecutivo: {e}")
            return {}
    
    def get_dataframe_info(self, df: pd.DataFrame) -> Dict:
        """
        Obtiene información resumida de un DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame a analizar
            
        Returns:
            dict: Información del DataFrame
        """
        if df.empty:
            return {'status': 'empty', 'rows': 0, 'columns': 0}
        
        return {
            'status': 'success',
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """
        Exporta un DataFrame a CSV
        
        Args:
            df (pd.DataFrame): DataFrame a exportar
            filename (str): Nombre del archivo
            
        Returns:
            bool: True si la exportación fue exitosa
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"DataFrame exportado exitosamente a {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error exportando DataFrame: {e}")
            return False