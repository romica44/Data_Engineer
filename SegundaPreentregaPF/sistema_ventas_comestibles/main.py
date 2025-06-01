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
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe en lugar de execute_query
            return self.db.execute_query_to_dataframe(query, params)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de rendimiento de empleados: {e}")
            return pd.DataFrame()  # 🔄 CAMBIO: retornar DataFrame vacío en lugar de lista vacía
    
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
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe
            return self.db.execute_query_to_dataframe(query)
            
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
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe
            return self.db.execute_query_to_dataframe(query)
            
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
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe
            return self.db.execute_query_to_dataframe(query)
            
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
                SUM(s.TotalPrice) as total_revenue,
                AVG(s.TotalPrice) as avg_sale_amount,
                SUM(s.Quantity) as total_units_sold,
                COUNT(DISTINCT s.CustomerID) as unique_customers
            FROM sales s
            GROUP BY {group_by}
            ORDER BY period
            """
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe
            return self.db.execute_query_to_dataframe(query)
            
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
                    WHEN s.Discount <= 0.05 THEN '1% - 5%'
                    WHEN s.Discount <= 0.10 THEN '6% - 10%'
                    WHEN s.Discount <= 0.15 THEN '11% - 15%'
                    WHEN s.Discount <= 0.20 THEN '16% - 20%'
                    ELSE '> 20%'
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
            
            # 🔄 CAMBIO CRÍTICO: usar execute_query_to_dataframe
            return self.db.execute_query_to_dataframe(query)
            
        except Exception as e:
            self.logger.error(f"Error en análisis de descuentos: {e}")
            return pd.DataFrame()
    
    def generate_executive_dashboard(self) -> Dict:
        """
        Genera un dashboard ejecutivo con métricas clave
        
        Returns:
            dict: Dashboard con métricas clave (mantiene formato dict para compatibilidad)
        """
        try:
            # Métricas generales - convertir DataFrame a dict para mantener compatibilidad
            general_metrics_df = self.db.execute_query_to_dataframe("""
                SELECT 
                    COUNT(SalesID) as total_sales,
                    SUM(TotalPrice) as total_revenue,
                    AVG(TotalPrice) as avg_sale_amount,
                    COUNT(DISTINCT CustomerID) as unique_customers,
                    COUNT(DISTINCT ProductID) as products_sold
                FROM sales
            """)
            general_metrics = general_metrics_df.iloc[0].to_dict() if len(general_metrics_df) > 0 else {}
            
            # Top 5 productos
            top_products_df = self.db.execute_query_to_dataframe("""
                SELECT p.ProductName, SUM(s.TotalPrice) as revenue
                FROM sales s
                JOIN products p ON s.ProductID = p.ProductID
                GROUP BY p.ProductID, p.ProductName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            top_products = top_products_df.to_dict('records') if len(top_products_df) > 0 else []
            
            # Top 5 empleados
            top_employees_df = self.db.execute_query_to_dataframe("""
                SELECT CONCAT(e.FirstName, ' ', e.LastName) as employee_name, 
                       SUM(s.TotalPrice) as revenue
                FROM sales s
                JOIN employees e ON s.SalesPersonID = e.EmployeeID
                GROUP BY e.EmployeeID, e.FirstName, e.LastName
                ORDER BY revenue DESC
                LIMIT 5
            """)
            top_employees = top_employees_df.to_dict('records') if len(top_employees_df) > 0 else []
            
            # Ventas por país
            sales_by_country_df = self.db.execute_query_to_dataframe("""
                SELECT co.CountryName, SUM(s.TotalPrice) as revenue
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
    
    # 🆕 MÉTODOS ADICIONALES para trabajar con DataFrames
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Para ver logs si hay
    service = AnalyticsService()
    
    try:
        print("Probando conexión...")
        info = service.db.get_connection_info()
        print("Conexión:", info)

        print("\nEjecutando análisis de productos...")
        df = service.get_product_performance_analysis()
        print(df.head())
    except Exception as e:
        print("❌ Error al ejecutar análisis:", e)
    
   