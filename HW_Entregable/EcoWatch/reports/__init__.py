"""
Sistema de reportes del EcoWatch con patrones de diseño
"""
from .base import ReporteBase
from .factory import FactoryReportes, TipoReporte
from .strategies import AnalisisEstadistico, AnalisisTendencias, AnalisisComparativo
from .implementations import (
    ReporteEstadoPorSala, 
    ReporteAlertasCriticas, 
    ReporteTendenciasAmbientales,
    ReporteResumenEjecutivo
)

__all__ = [
    'ReporteBase', 
    'FactoryReportes', 
    'TipoReporte',
    'AnalisisEstadistico', 
    'AnalisisTendencias', 
    'AnalisisComparativo',
    'ReporteEstadoPorSala', 
    'ReporteAlertasCriticas', 
    'ReporteTendenciasAmbientales',
    'ReporteResumenEjecutivo'
]
