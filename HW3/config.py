"""
Configuraciones generales del sistema de reportes
"""

class Config:
    """Configuraciones del sistema"""
    
    # Formatos de exportación soportados
    SUPPORTED_EXPORT_FORMATS = ['csv', 'excel', 'json']
    
    # Tipos de reportes disponibles
    REPORT_TYPES = {
        'total_sales': 'Total de Ventas por Categoría',
        'detailed_sales': 'Métricas Detalladas por Categoría'
    }
    
    # Configuración de archivos
    DEFAULT_ENCODING = 'utf-8'
    TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'
    DISPLAY_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Configuración de visualización
    CONSOLE_WIDTH = 80
    SEPARATOR_CHAR = "="
    SUB_SEPARATOR_CHAR = "-"
    
    # Emojis para la interfaz
    EMOJIS = {
        'report': '📊',
        'date': '📅',
        'category': '🏷️',
        'money': '💰',
        'summary': '📈',
        'file': '📁',
        'rocket': '🚀',
        'error': '❌',
        'success': '✅',
        'search': '🔍'
    }