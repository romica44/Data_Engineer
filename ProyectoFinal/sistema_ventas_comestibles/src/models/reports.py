from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from src.services.helpers import format_currency, format_percentage

class BaseReport(ABC):
    """
    Clase base abstracta para todos los reportes.
    Define la interfaz común que deben implementar todos los tipos de reportes.
    """
    
    def __init__(self, title: str, data: pd.DataFrame):
        self.title = title
        self.data = data
        self.created_at = datetime.now()
        self.metadata = {}
    
    @abstractmethod
    def generate_summary(self) -> Dict[str, Any]:
        """Genera un resumen del reporte"""
        pass
    
    @abstractmethod
    def format_for_display(self) -> str:
        """Formatea el reporte para mostrar en consola"""
        pass
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """Estadísticas básicas comunes a todos los reportes"""
        if self.data.empty:
            return {'status': 'empty', 'rows': 0, 'columns': 0}
        
        return {
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'report_type': self.__class__.__name__
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporta el reporte completo a diccionario"""
        return {
            'title': self.title,
            'metadata': self.metadata,
            'summary': self.generate_summary(),
            'basic_stats': self.get_basic_stats(),
            'data': self.data.to_dict('records') if not self.data.empty else []
        }

class SalesReport(BaseReport):
    """
    Reporte especializado en análisis de ventas.
    Incluye métricas específicas de ingresos, cantidad de ventas, etc.
    """
    
    def __init__(self, data: pd.DataFrame, period: str = 'general'):
        super().__init__(f"Reporte de Ventas - {period.title()}", data)
        self.period = period
        self.metadata = {'period': period, 'focus': 'sales_performance'}
    
    def generate_summary(self) -> Dict[str, Any]:
        """Genera resumen específico para ventas"""
        if self.data.empty:
            return {'error': 'No hay datos disponibles'}
        
        # Intentar obtener métricas de ventas del DataFrame
        summary = {}
        
        if 'total_revenue' in self.data.columns:
            summary['total_revenue'] = format_currency(self.data['total_revenue'].sum())
            summary['avg_revenue'] = format_currency(self.data['total_revenue'].mean())
            summary['max_revenue'] = format_currency(self.data['total_revenue'].max())
        
        if 'total_sales' in self.data.columns:
            summary['total_transactions'] = int(self.data['total_sales'].sum())
            summary['avg_transactions'] = round(self.data['total_sales'].mean(), 2)
        
        if 'total_units_sold' in self.data.columns:
            summary['total_units'] = int(self.data['total_units_sold'].sum())
        
        summary['period_analyzed'] = self.period
        summary['top_performer'] = self._get_top_performer()
        
        return summary
    
    def _get_top_performer(self) -> str:
        """Identifica el mejor performer según el tipo de datos"""
        if self.data.empty:
            return "N/A"
        
        if 'total_revenue' in self.data.columns:
            top_row = self.data.loc[self.data['total_revenue'].idxmax()]
            
            # Determinar el campo de nombre según las columnas disponibles
            name_field = None
            for field in ['employee_name', 'ProductName', 'customer_name', 'CountryName']:
                if field in self.data.columns:
                    name_field = field
                    break
            
            if name_field:
                return f"{top_row[name_field]} ({format_currency(top_row['total_revenue'])})"
        
        return "N/A"
    
    def format_for_display(self) -> str:
        """Formato específico para reportes de ventas"""
        output = []
        output.append(f"🔷 {self.title}")
        output.append("=" * 50)
        
        summary = self.generate_summary()
        
        if 'error' in summary:
            output.append(f"❌ {summary['error']}")
            return "\n".join(output)
        
        output.append("📊 RESUMEN EJECUTIVO:")
        if 'total_revenue' in summary:
            output.append(f"  💰 Ingresos Totales: {summary['total_revenue']}")
        if 'total_transactions' in summary:
            output.append(f"  📈 Total Transacciones: {summary['total_transactions']}")
        if 'top_performer' in summary:
            output.append(f"  🏆 Mejor Performer: {summary['top_performer']}")
        
        output.append(f"\n📅 Período: {summary.get('period_analyzed', 'N/A')}")
        output.append(f"🕒 Generado: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)

class EmployeeReport(BaseReport):
    """
    Reporte especializado en análisis de rendimiento de empleados.
    """
    
    def __init__(self, data: pd.DataFrame):
        super().__init__("Reporte de Rendimiento de Empleados", data)
        self.metadata = {'focus': 'employee_performance'}
    
    def generate_summary(self) -> Dict[str, Any]:
        """Resumen específico para empleados"""
        if self.data.empty:
            return {'error': 'No hay datos de empleados'}
        
        summary = {
            'total_employees': len(self.data),
            'active_employees': len(self.data[self.data['total_sales'] > 0]) if 'total_sales' in self.data.columns else 0,
        }
        
        if 'total_revenue' in self.data.columns:
            summary['total_revenue_generated'] = format_currency(self.data['total_revenue'].sum())
            summary['avg_revenue_per_employee'] = format_currency(self.data['total_revenue'].mean())
            summary['top_employee'] = self._get_top_employee()
        
        if 'unique_customers_served' in self.data.columns:
            summary['total_customers_served'] = int(self.data['unique_customers_served'].sum())
        
        return summary
    
    def _get_top_employee(self) -> str:
        """Encuentra el empleado con mejor rendimiento"""
        if self.data.empty or 'total_revenue' not in self.data.columns:
            return "N/A"
        
        top_employee = self.data.loc[self.data['total_revenue'].idxmax()]
        name = top_employee.get('employee_name', 'Empleado desconocido')
        revenue = format_currency(top_employee['total_revenue'])
        
        return f"{name} ({revenue})"
    
    def format_for_display(self) -> str:
        """Formato específico para reportes de empleados"""
        output = []
        output.append(f"👥 {self.title}")
        output.append("=" * 50)
        
        summary = self.generate_summary()
        
        if 'error' in summary:
            output.append(f"❌ {summary['error']}")
            return "\n".join(output)
        
        output.append("📊 MÉTRICAS DE EQUIPO:")
        output.append(f"  👔 Total Empleados: {summary['total_employees']}")
        output.append(f"  ✅ Empleados Activos: {summary['active_employees']}")
        
        if 'total_revenue_generated' in summary:
            output.append(f"  💰 Ingresos Generados: {summary['total_revenue_generated']}")
            output.append(f"  📊 Promedio por Empleado: {summary['avg_revenue_per_employee']}")
        
        if 'top_employee' in summary:
            output.append(f"  🏆 Mejor Empleado: {summary['top_employee']}")
        
        output.append(f"\n🕒 Generado: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)

class ProductReport(BaseReport):
    """
    Reporte especializado en análisis de productos.
    """
    
    def __init__(self, data: pd.DataFrame):
        super().__init__("Reporte de Rendimiento de Productos", data)
        self.metadata = {'focus': 'product_performance'}
    
    def generate_summary(self) -> Dict[str, Any]:
        """Resumen específico para productos"""
        if self.data.empty:
            return {'error': 'No hay datos de productos'}
        
        summary = {
            'total_products': len(self.data),
            'products_with_sales': len(self.data[self.data['total_sales'] > 0]) if 'total_sales' in self.data.columns else 0,
        }
        
        if 'total_revenue' in self.data.columns:
            summary['total_product_revenue'] = format_currency(self.data['total_revenue'].sum())
            summary['avg_revenue_per_product'] = format_currency(self.data['total_revenue'].mean())
        
        if 'total_units_sold' in self.data.columns:
            summary['total_units_sold'] = int(self.data['total_units_sold'].sum())
            summary['avg_units_per_product'] = round(self.data['total_units_sold'].mean(), 2)
        
        summary['top_product'] = self._get_top_product()
        summary['categories_analysis'] = self._get_categories_summary()
        
        return summary
    
    def _get_top_product(self) -> str:
        """Encuentra el producto con mejor rendimiento"""
        if self.data.empty or 'total_revenue' not in self.data.columns:
            return "N/A"
        
        top_product = self.data.loc[self.data['total_revenue'].idxmax()]
        name = top_product.get('ProductName', 'Producto desconocido')
        revenue = format_currency(top_product['total_revenue'])
        
        return f"{name} ({revenue})"
    
    def _get_categories_summary(self) -> Dict[str, int]:
        """Resumen por categorías"""
        if 'CategoryName' not in self.data.columns:
            return {}
        
        return self.data['CategoryName'].value_counts().to_dict()
    
    def format_for_display(self) -> str:
        """Formato específico para reportes de productos"""
        output = []
        output.append(f"📦 {self.title}")
        output.append("=" * 50)
        
        summary = self.generate_summary()
        
        if 'error' in summary:
            output.append(f"❌ {summary['error']}")
            return "\n".join(output)
        
        output.append("📊 MÉTRICAS DE PRODUCTOS:")
        output.append(f"  📦 Total Productos: {summary['total_products']}")
        output.append(f"  ✅ Productos con Ventas: {summary['products_with_sales']}")
        
        if 'total_product_revenue' in summary:
            output.append(f"  💰 Ingresos Totales: {summary['total_product_revenue']}")
            output.append(f"  📊 Promedio por Producto: {summary['avg_revenue_per_product']}")
        
        if 'total_units_sold' in summary:
            output.append(f"  📈 Unidades Vendidas: {summary['total_units_sold']}")
        
        if 'top_product' in summary:
            output.append(f"  🏆 Mejor Producto: {summary['top_product']}")
        
        if summary.get('categories_analysis'):
            output.append("\n📂 CATEGORÍAS:")
            for category, count in list(summary['categories_analysis'].items())[:5]:
                output.append(f"  • {category}: {count} productos")
        
        output.append(f"\n🕒 Generado: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)

class GeographicReport(BaseReport):
    """
    Reporte especializado en análisis geográfico.
    """
    
    def __init__(self, data: pd.DataFrame):
        super().__init__("Reporte de Análisis Geográfico", data)
        self.metadata = {'focus': 'geographic_analysis'}
    
    def generate_summary(self) -> Dict[str, Any]:
        """Resumen específico para análisis geográfico"""
        if self.data.empty:
            return {'error': 'No hay datos geográficos'}
        
        summary = {}
        
        if 'CountryName' in self.data.columns:
            summary['total_countries'] = self.data['CountryName'].nunique()
            summary['top_country'] = self._get_top_location('CountryName')
        
        if 'CityName' in self.data.columns:
            summary['total_cities'] = self.data['CityName'].nunique()
            summary['top_city'] = self._get_top_location('CityName')
        
        if 'total_revenue' in self.data.columns:
            summary['total_geographic_revenue'] = format_currency(self.data['total_revenue'].sum())
        
        return summary
    
    def _get_top_location(self, location_field: str) -> str:
        """Encuentra la ubicación con mejor rendimiento"""
        if self.data.empty or location_field not in self.data.columns or 'total_revenue' not in self.data.columns:
            return "N/A"
        
        location_revenue = self.data.groupby(location_field)['total_revenue'].sum()
        top_location = location_revenue.idxmax()
        top_revenue = format_currency(location_revenue.max())
        
        return f"{top_location} ({top_revenue})"
    
    def format_for_display(self) -> str:
        """Formato específico para reportes geográficos"""
        output = []
        output.append(f"🌍 {self.title}")
        output.append("=" * 50)
        
        summary = self.generate_summary()
        
        if 'error' in summary:
            output.append(f"❌ {summary['error']}")
            return "\n".join(output)
        
        output.append("🌎 COBERTURA GEOGRÁFICA:")
        
        if 'total_countries' in summary:
            output.append(f"  🏴 Total Países: {summary['total_countries']}")
            output.append(f"  🏆 Mejor País: {summary['top_country']}")
        
        if 'total_cities' in summary:
            output.append(f"  🏙️ Total Ciudades: {summary['total_cities']}")
            output.append(f"  🏆 Mejor Ciudad: {summary['top_city']}")
        
        if 'total_geographic_revenue' in summary:
            output.append(f"  💰 Ingresos Totales: {summary['total_geographic_revenue']}")
        
        output.append(f"\n🕒 Generado: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)