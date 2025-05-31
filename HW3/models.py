"""
Modelos y clases base del sistema de reportes
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol
import pandas as pd


class SalesReport(Protocol):
    """Protocolo para reportes de ventas"""
    
    def generate_report(self, data: List[Dict]) -> Dict[str, Any]:
        """Genera el reporte con los datos proporcionados"""
        ...


class MetricStrategy(ABC):
    """Interfaz abstracta para estrategias de cálculo de métricas"""
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calcula la métrica específica"""
        pass


class BaseSalesReport:
    """Clase base para reportes de ventas"""
    
    def __init__(self, strategy: MetricStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: MetricStrategy):
        """Cambiar la estrategia de cálculo"""
        self._strategy = strategy
    
    def generate_report(self, data: List[Dict]) -> Dict[str, Any]:
        """Generar reporte usando la estrategia actual"""
        df = pd.DataFrame(data)
        return self._strategy.calculate(df)


class ReportData:
    """Modelo para datos de reporte"""
    
    def __init__(self, titulo: str, datos: Dict[str, Any], **kwargs):
        self.titulo = titulo
        self.datos = datos
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        result = {
            'titulo': self.titulo,
            'datos': self.datos
        }
        result.update(self.metadata)
        return result

