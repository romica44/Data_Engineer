"""
Decoradores para visualización y formateo de reportes
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from config import Config
from utils import FormatUtils
from exporters import DataExporter


class ReportDecorator(ABC):
    """Decorador base para reportes"""
    
    def __init__(self, component=None):
        self._component = component
    
    @abstractmethod
    def display(self, data: Dict[str, Any]) -> str:
        pass


class ConsoleReportDecorator(ReportDecorator):
    """Decorador para mostrar reportes en consola con formato mejorado"""
    
    def display(self, data: Dict[str, Any]) -> str:
        output = []
        emojis = Config.EMOJIS
        
        # Encabezado
        output.append(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        output.append(f"{emojis['report']} {data['titulo'].upper()}")
        output.append(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        output.append(f"{emojis['date']} Generado: {FormatUtils.format_timestamp()}")
        output.append(Config.SUB_SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        
        # Datos principales
        if 'datos' in data:
            self._format_main_data(output, data['datos'], emojis)
        
        # Total general
        if 'total_general' in data:
            output.append(Config.SUB_SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
            output.append(f"{emojis['money']} TOTAL GENERAL: {FormatUtils.format_currency(data['total_general'])}")
        
        # Resumen
        if 'resumen' in data:
            self._format_summary(output, data['resumen'], emojis)
        
        output.append(Config.SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        return "\n".join(output)
    
    def _format_main_data(self, output: list, datos: Dict[str, Any], emojis: Dict[str, str]):
        """Formatear datos principales"""
        for categoria, valor in datos.items():
            if isinstance(valor, dict):
                output.append(f"\n{emojis['category']} {categoria.upper()}:")
                for metrica, val in valor.items():
                    formatted_value = self._format_value(val)
                    metric_name = FormatUtils.format_metric_name(metrica)
                    output.append(f"   {metric_name}: {formatted_value}")
            else:
                formatted_value = self._format_value(valor)
                output.append(f"{emojis['category']} {categoria}: {formatted_value}")
    
    def _format_summary(self, output: list, resumen: Dict[str, Any], emojis: Dict[str, str]):
        """Formatear sección de resumen"""
        output.append(Config.SUB_SEPARATOR_CHAR * Config.CONSOLE_WIDTH)
        output.append(f"{emojis['summary']} RESUMEN GENERAL:")
        for clave, valor in resumen.items():
            formatted_value = self._format_value(valor)
            key_name = FormatUtils.format_metric_name(clave)
            output.append(f"   {key_name}: {formatted_value}")
    
    def _format_value(self, value: Any) -> str:
        """Formatear valor según su tipo"""
        if isinstance(value, float):
            return FormatUtils.format_currency(value)
        elif isinstance(value, int):
            return FormatUtils.format_number(value)
        else:
            return str(value)


class ExportDecorator(ReportDecorator):
    """Decorador para exportar reportes a archivos"""
    
    def __init__(self, component=None, export_format='csv'):
        super().__init__(component)
        self.export_format = export_format
        self.exporter = DataExporter()
    
    def display(self, data: Dict[str, Any]) -> str:
        # Mostrar en consola primero si hay componente
        console_output = self._component.display(data) if self._component else ""
        
        # Exportar a archivo
        try:
            filename = self.exporter.export(data, self.export_format)
            export_message = f"\n\n{Config.EMOJIS['file']} Datos exportados a: {filename}"
        except Exception as e:
            export_message = f"\n\n{Config.EMOJIS['error']} Error al exportar: {str(e)}"
        
        return console_output + export_message


class ColorDecorator(ReportDecorator):
    """Decorador para añadir colores a la consola (ANSI)"""
    
    COLORS = {
        'header': '\033[1;36m',      # Cian brillante
        'category': '\033[1;33m',    # Amarillo brillante
        'value': '\033[1;32m',       # Verde brillante
        'total': '\033[1;31m',       # Rojo brillante
        'reset': '\033[0m'           # Reset
    }
    
    def display(self, data: Dict[str, Any]) -> str:
        if self._component:
            output = self._component.display(data)
            # Aplicar colores a elementos específicos
            for color_type, color_code in self.COLORS.items():
                if color_type == 'reset':
                    continue
                # Aquí podrías implementar lógica específica de coloreo
            return output
        return ""
