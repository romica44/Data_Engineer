"""
Servicios principales del sistema de reportes
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from data import datos_ventas
from factories import ReportFactoryProvider
from decorators import ConsoleReportDecorator, ExportDecorator, ColorDecorator
from utils import DataUtils, FormatUtils
from config import Config


class SalesReportingService:
    """Servicio principal para generar reportes de ventas"""
    
    def __init__(self, data_source: Optional[List[Dict]] = None):
        self.data = data_source or datos_ventas
        self.df = pd.DataFrame(self.data)
    
    def generate_report(self, report_type: str, export_formats: List[str] = None, 
                       use_colors: bool = False) -> str:
        """Generar un reporte específico"""
        try:
            # Crear reporte usando Factory
            factory = ReportFactoryProvider.get_factory(report_type)
            report = factory.create_report()
            
            # Generar datos del reporte
            report_data = report.generate_report(self.data)
            
            # Configurar decoradores
            decorator = ConsoleReportDecorator()
            
            if use_colors:
                decorator = ColorDecorator(decorator)
            
            # Añadir decoradores de exportación
            if export_formats:
                for export_format in export_formats:
                    if export_format in Config.SUPPORTED_EXPORT_FORMATS:
                        decorator = ExportDecorator(decorator, export_format)
            
            # Mostrar reporte
            return decorator.display(report_data)
            
        except Exception as e:
            return f"{Config.EMOJIS['error']} Error al generar reporte {report_type}: {str(e)}"
    
    def generate_all_reports(self, export_formats: List[str] = None) -> List[str]:
        """Generar todos los reportes disponibles"""
        results = []
        
        for report_type in ReportFactoryProvider.get_available_types():
            result = self.generate_report(report_type, export_formats)
            results.append(result)
        
        return results
    
    def get_data_summary(self) -> str:
        """Obtener resumen de los datos cargados"""
        summary = DataUtils.get_data_summary(self.df)
        
        output = []
        output.append(f"{Config.EMOJIS['report']} RESUMEN DE DATOS CARGADOS")
        output.append(Config.SEPARATOR_CHAR[:50])
        output.append(f"Total de registros: {FormatUtils.format_number(summary['total_records'])}")
        output.append(f"Categorías únicas: {', '.join(summary['unique_categories'])}")
        output.append(f"Vendedores únicos: {', '.join(summary['unique_sellers'])}")
        output.append(f"Medios de venta: {', '.join(summary['unique_channels'])}")
        
        price_range = summary['price_range']
        output.append(f"Rango de precios: {FormatUtils.format_currency(price_range['min'])} - {FormatUtils.format_currency(price_range['max'])}")
        output.append(f"Precio promedio: {FormatUtils.format_currency(price_range['mean'])}")
        output.append(Config.SEPARATOR_CHAR[:50])
        
        return "\n".join(output)
    
    def get_available_reports(self) -> Dict[str, str]:
        """Obtener tipos de reportes disponibles"""
        return {
            report_type: Config.REPORT_TYPES.get(report_type, report_type.replace('_', ' ').title())
            for report_type in ReportFactoryProvider.get_available_types()
        }