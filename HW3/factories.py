"""
Fábricas para crear diferentes tipos de reportes
"""

from abc import ABC, abstractmethod
from typing import List
from models import BaseSalesReport, SalesReport
from strategies import (
    TotalSalesByCategoryStrategy,
    DetailedSalesByCategoryStrategy,
    SalesByChannelStrategy,
    SalesBySellerStrategy
)


class ReportFactory(ABC):
    """Fábrica abstracta para crear reportes"""
    
    @abstractmethod
    def create_report(self) -> SalesReport:
        """Crear un reporte específico"""
        pass


class TotalSalesReportFactory(ReportFactory):
    """Fábrica para crear reportes de total de ventas por categoría"""
    
    def create_report(self) -> BaseSalesReport:
        strategy = TotalSalesByCategoryStrategy()
        return BaseSalesReport(strategy)


class DetailedSalesReportFactory(ReportFactory):
    """Fábrica para crear reportes detallados por categoría"""
    
    def create_report(self) -> BaseSalesReport:
        strategy = DetailedSalesByCategoryStrategy()
        return BaseSalesReport(strategy)


class ChannelSalesReportFactory(ReportFactory):
    """Fábrica para crear reportes de ventas por canal"""
    
    def create_report(self) -> BaseSalesReport:
        strategy = SalesByChannelStrategy()
        return BaseSalesReport(strategy)


class SellerPerformanceReportFactory(ReportFactory):
    """Fábrica para crear reportes de rendimiento por vendedor"""
    
    def create_report(self) -> BaseSalesReport:
        strategy = SalesBySellerStrategy()
        return BaseSalesReport(strategy)


class ReportFactoryProvider:
    """Proveedor de fábricas de reportes"""
    
    _factories = {
        'total_sales': TotalSalesReportFactory,
        'detailed_sales': DetailedSalesReportFactory,
        'channel_sales': ChannelSalesReportFactory,
        'seller_performance': SellerPerformanceReportFactory
    }
    
    @classmethod
    def get_factory(cls, report_type: str) -> ReportFactory:
        """Obtener fábrica por tipo de reporte"""
        factory_class = cls._factories.get(report_type)
        if factory_class:
            return factory_class()
        raise ValueError(f"Tipo de reporte no soportado: {report_type}")
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Obtener tipos de reporte disponibles"""
        return list(cls._factories.keys())
    
    @classmethod
    def register_factory(cls, report_type: str, factory_class: type):
        """Registrar nueva fábrica de reporte"""
        cls._factories[report_type] = factory_class

