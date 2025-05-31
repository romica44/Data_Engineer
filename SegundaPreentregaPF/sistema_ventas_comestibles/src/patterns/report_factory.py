from typing import Dict, Any, Optional
import pandas as pd
from enum import Enum
from src.models.reports import (
    BaseReport, SalesReport, EmployeeReport, 
    ProductReport, GeographicReport
)
from src.services.analytics_service import AnalyticsService
import logging

class ReportType(Enum):
    """
    Enumeración de tipos de reportes disponibles.
    Facilita la extensibilidad y previene errores de tipeo.
    """
    SALES = "sales"
    EMPLOYEE = "employee"
    PRODUCT = "product"
    GEOGRAPHIC = "geographic"
    TRENDS = "trends"
    DISCOUNT = "discount"

class ReportFactory:
    """
    Factory Pattern para crear diferentes tipos de reportes.
    
    Patrón implementado: Factory Method
    Problema que resuelve: 
    - Centraliza la lógica de creación de reportes
    - Encapsula la complejidad de obtener datos específicos para cada tipo de reporte
    - Permite agregar nuevos tipos de reportes sin modificar código existente
    - Desacopla el código cliente de las clases concretas de reportes
    
    Beneficios:
    - Código más limpio y mantenible
    - Facilita testing al poder mockear la factory
    - Cumple con el principio Open/Closed (abierto para extensión, cerrado para modificación)
    """
    
    def __init__(self):
        """Inicializa la factory con el servicio de análisis"""
        self.analytics_service = AnalyticsService()
        self.logger = logging.getLogger(__name__)
        
        # Registro de tipos de reportes disponibles
        self._report_creators = {
            ReportType.SALES: self._create_sales_report,
            ReportType.EMPLOYEE: self._create_employee_report,
            ReportType.PRODUCT: self._create_product_report,
            ReportType.GEOGRAPHIC: self._create_geographic_report,
            ReportType.TRENDS: self._create_trends_report,
            ReportType.DISCOUNT: self._create_discount_report,
        }
    
    def create_report(self, report_type: ReportType, **kwargs) -> BaseReport:
        """
        Método principal de la factory para crear reportes.
        
        Args:
            report_type (ReportType): Tipo de reporte a crear
            **kwargs: Parámetros específicos para cada tipo de reporte
            
        Returns:
            BaseReport: Instancia del reporte solicitado
            
        Raises:
            ValueError: Si el tipo de reporte no es soportado
        """
        try:
            if report_type not in self._report_creators:
                available_types = [rt.value for rt in ReportType]
                raise ValueError(f"Tipo de reporte '{report_type.value}' no soportado. "
                               f"Tipos disponibles: {available_types}")
            
            self.logger.info(f"🏭 Creando reporte tipo: {report_type.value}")
            
            # Delegar la creación al método específico
            report = self._report_creators[report_type](**kwargs)
            
            self.logger.info(f"✅ Reporte {report_type.value} creado exitosamente")
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error creando reporte {report_type.value}: {e}")
            raise
    
    def _create_sales_report(self, period: str = 'general', **kwargs) -> SalesReport:
        """
        Crea un reporte de ventas específico.
        
        Args:
            period (str): Período del análisis ('daily', 'monthly', 'general')
            **kwargs: Parámetros adicionales como start_date, end_date
            
        Returns:
            SalesReport: Reporte de ventas configurado
        """
        try:
            if period in ['daily', 'monthly']:
                data = self.analytics_service.get_sales_trends_by_period(period)
            else:
                # Reporte general de ventas por empleado
                start_date = kwargs.get('start_date')
                end_date = kwargs.get('end_date')
                data = self.analytics_service.get_sales_performance_by_employee(start_date, end_date)
            
            return SalesReport(data, period)
            
        except Exception as e:
            self.logger.error(f"Error creando reporte de ventas: {e}")
            # Retornar reporte con DataFrame vacío en caso de error
            return SalesReport(pd.DataFrame(), period)
    
    def _create_employee_report(self, **kwargs) -> EmployeeReport:
        """
        Crea un reporte de rendimiento de empleados.
        
        Args:
            **kwargs: Parámetros como start_date, end_date para filtrar período
            
        Returns:
            EmployeeReport: Reporte de empleados configurado
        """
        try:
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            
            data = self.analytics_service.get_sales_performance_by_employee(start_date, end_date)
            return EmployeeReport(data)
            
        except Exception as e:
            self.logger.error(f"Error creando reporte de empleados: {e}")
            return EmployeeReport(pd.DataFrame())
    
    def _create_product_report(self, **kwargs) -> ProductReport:
        """
        Crea un reporte de rendimiento de productos.
        
        Returns:
            ProductReport: Reporte de productos configurado
        """
        try:
            data = self.analytics_service.get_product_performance_analysis()
            return ProductReport(data)
            
        except Exception as e:
            self.logger.error(f"Error creando reporte de productos: {e}")
            return ProductReport(pd.DataFrame())
    
    def _create_geographic_report(self, **kwargs) -> GeographicReport:
        """
        Crea un reporte de análisis geográfico.
        
        Returns:
            GeographicReport: Reporte geográfico configurado
        """
        try:
            data = self.analytics_service.get_geographic_sales_analysis()
            return GeographicReport(data)
            
        except Exception as e:
            self.logger.error(f"Error creando reporte geográfico: {e}")
            return GeographicReport(pd.DataFrame())
    
    def _create_trends_report(self, period: str = 'daily', **kwargs) -> SalesReport:
        """
        Crea un reporte especializado en tendencias temporales.
        
        Args:
            period (str): Período de análisis ('daily' o 'monthly')
            
        Returns:
            SalesReport: Reporte de tendencias configurado
        """
        try:
            data = self.analytics_service.get_sales_trends_by_period(period)
            return SalesReport(data, f"tendencias_{period}")
            
        except Exception as e:
            self.logger.error(f"Error creando reporte de tendencias: {e}")
            return SalesReport(pd.DataFrame(), f"tendencias_{period}")
    
    def _create_discount_report(self, **kwargs) -> SalesReport:
        """
        Crea un reporte especializado en análisis de descuentos.
        
        Returns:
            SalesReport: Reporte de descuentos configurado
        """
        try:
            data = self.analytics_service.get_discount_effectiveness_analysis()
            return SalesReport(data, "descuentos")
            
        except Exception as e:
            self.logger.error(f"Error creando reporte de descuentos: {e}")
            return SalesReport(pd.DataFrame(), "descuentos")
    
    def get_available_report_types(self) -> Dict[str, str]:
        """
        Retorna los tipos de reportes disponibles con sus descripciones.
        
        Returns:
            dict: Diccionario con tipos y descripciones de reportes
        """
        return {
            ReportType.SALES.value: "Análisis general de ventas y rendimiento",
            ReportType.EMPLOYEE.value: "Rendimiento individual de empleados",
            ReportType.PRODUCT.value: "Análisis de rendimiento de productos",
            ReportType.GEOGRAPHIC.value: "Análisis de ventas por ubicación geográfica",
            ReportType.TRENDS.value: "Tendencias temporales de ventas",
            ReportType.DISCOUNT.value: "Efectividad de estrategias de descuentos"
        }
    
    def create_comprehensive_report(self, include_types: Optional[list] = None) -> Dict[str, BaseReport]:
        """
        Crea múltiples reportes de una vez para análisis comprehensive.
        
        Args:
            include_types (list, optional): Lista de tipos de reportes a incluir.
                                          Si None, incluye todos los tipos.
            
        Returns:
            dict: Diccionario con reportes creados, usando el tipo como clave
        """
        if include_types is None:
            include_types = list(ReportType)
        
        reports = {}
        
        for report_type in include_types:
            if isinstance(report_type, str):
                # Convertir string a enum
                try:
                    report_type = ReportType(report_type)
                except ValueError:
                    self.logger.warning(f"Tipo de reporte inválido ignorado: {report_type}")
                    continue
            
            try:
                report = self.create_report(report_type)
                reports[report_type.value] = report
            except Exception as e:
                self.logger.error(f"Error creando reporte {report_type.value}: {e}")
                # Continuar con los demás reportes
                continue
        
        self.logger.info(f"📊 Creados {len(reports)} reportes en lote")
        return reports
    
    def get_factory_info(self) -> Dict[str, Any]:
        """
        Información sobre la factory y su estado.
        
        Returns:
            dict: Información de la factory
        """
        return {
            'pattern_type': 'Factory Method',
            'total_report_types': len(self._report_creators),
            'available_types': [rt.value for rt in ReportType],
            'analytics_service_connected': self.analytics_service.test_connection(),
            'factory_initialized': True
        }

# Función de conveniencia para uso directo
def create_report(report_type: str, **kwargs) -> BaseReport:
    """
    Función de conveniencia para crear reportes sin instanciar la factory.
    
    Args:
        report_type (str): Tipo de reporte como string
        **kwargs: Parámetros específicos del reporte
        
    Returns:
        BaseReport: Reporte creado
    """
    factory = ReportFactory()
    report_enum = ReportType(report_type)
    return factory.create_report(report_enum, **kwargs)