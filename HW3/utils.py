"""
Utilidades comunes para el sistema de reportes
"""

from datetime import datetime
from typing import Any, Dict
import pandas as pd


class FormatUtils:
    """Utilidades para formateo de datos"""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Formatear cantidad como moneda"""
        return f"${amount:,.2f}"
    
    @staticmethod
    def format_number(number: int) -> str:
        """Formatear número con separadores de miles"""
        return f"{number:,}"
    
    @staticmethod
    def format_timestamp() -> str:
        """Formatear timestamp actual"""
        return datetime.now().strftime(Config.DISPLAY_TIMESTAMP_FORMAT)
    
    @staticmethod
    def clean_text_for_filename(text: str) -> str:
        """Limpiar texto para uso en nombres de archivo"""
        return text.replace(' ', '_').lower().replace('ó', 'o').replace('í', 'i')
    
    @staticmethod
    def format_metric_name(metric_name: str) -> str:
        """Formatear nombre de métrica para visualización"""
        return metric_name.replace('_', ' ').title()


class DataUtils:
    """Utilidades para manipulación de datos"""
    
    @staticmethod
    def calculate_total_sale(row: pd.Series) -> float:
        """Calcular venta total para una fila"""
        return row['precio'] * row['cantidad']
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Obtener resumen de datos"""
        return {
            'total_records': len(df),
            'unique_categories': df['categoria'].unique().tolist(),
            'unique_sellers': df['vendedor'].unique().tolist(),
            'unique_channels': df['medio_venta'].unique().tolist(),
            'price_range': {
                'min': df['precio'].min(),
                'max': df['precio'].max(),
                'mean': df['precio'].mean()
            }
        }
