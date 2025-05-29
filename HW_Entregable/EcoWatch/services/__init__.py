"""
Services Package - Servicios del Sistema EcoWatch
Contiene todos los servicios y componentes de lógica de negocio
"""

# Importar servicios principales
from .cache_manager import CacheTemporalManager, crear_cache_manager, obtener_cache_global
from .log_processor import ProcesadorLogs
from .data_sources import (
    # Clases principales
    FuenteCSV, FuenteJSON, FuenteSimulada, FuenteDatabase,
    
    # Factory y utilidades
    FactoryFuentesDatos,
    crear_fuente_csv, crear_fuente_json, 
    crear_fuente_simulada, crear_fuente_database
)

# Versión del package de servicios
__version__ = "1.0.0"

# Lista de todos los servicios disponibles
__all__ = [
    # Cache Manager
    'CacheTemporalManager',
    'crear_cache_manager',
    'obtener_cache_global',
    
    # Log Processor
    'ProcesadorLogs',
    
    # Data Sources
    'FuenteCSV',
    'FuenteJSON', 
    'FuenteSimulada',
    'FuenteDatabase',
    
    # Factory y utilidades
    'FactoryFuentesDatos',
    'crear_fuente_csv',
    'crear_fuente_json',
    'crear_fuente_simulada',
    'crear_fuente_database'
]

# Metadatos del package
__author__ = "Sistema EcoWatch"
__description__ = "Servicios y lógica de negocio para monitoreo ambiental"

def obtener_version():
    """Retorna la versión actual del package de servicios"""
    return __version__

def listar_servicios():
    """Retorna una lista de todos los servicios disponibles"""
    return [
        'CacheTemporalManager', 
        'ProcesadorLogs', 
        'FuenteCSV', 
        'FuenteJSON', 
        'FuenteSimulada', 
        'FuenteDatabase'
    ]

def obtener_info_servicios():
    """Retorna información detallada de todos los servicios"""
    return {
        'CacheTemporalManager': {
            'descripcion': 'Gestión de caché temporal con índices para búsquedas rápidas',
            'patron': 'Singleton',
            'funcionalidades': ['FIFO automático', 'Índices O(1)', 'Thread-safe', 'Métricas automáticas']
        },
        'ProcesadorLogs': {
            'descripcion': 'Procesador principal de logs ambientales',
            'patron': 'Service',
            'funcionalidades': ['Validación', 'Evaluación ambiental', 'Detección de patrones', 'Análisis automático']
        },
        'FuenteCSV': {
            'descripcion': 'Fuente de datos CSV con mapeo automático de columnas',
            'protocolo': 'FuenteDatos',
            'funcionalidades': ['Auto-mapeo', 'Validación', 'Múltiples encodings', 'Fallback robusto']
        },
        'FuenteJSON': {
            'descripcion': 'Fuente de datos JSON con múltiples estructuras soportadas',
            'protocolo': 'FuenteDatos', 
            'funcionalidades': ['Múltiples formatos', 'Validación JSON', 'Conversión automática']
        },
        'FuenteSimulada': {
            'descripcion': 'Generador de datos sintéticos para testing y demos',
            'protocolo': 'FuenteDatos',
            'funcionalidades': ['Patrones realistas', 'Configuración por sala', 'Variabilidad temporal']
        },
        'FuenteDatabase': {
            'descripcion': 'Fuente de datos desde MySQL con queries optimizadas',
            'protocolo': 'FuenteDatos',
            'funcionalidades': ['Filtros avanzados', 'Paginación', 'Estadísticas de tabla']
        }
    }

# === CONFIGURACIÓN DE LOGGING PARA SERVICIOS ===
import logging

def configurar_logging_servicios(nivel: str = 'INFO'):
    """
    Configura logging específico para servicios
    
    Args:
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    """
    logger = logging.getLogger('services')
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, nivel.upper()))
    logger.info("Logging configurado para servicios EcoWatch")

# === FUNCIONES DE INICIALIZACIÓN ===

def inicializar_servicios_completos(config_cache: dict = None, 
                                  config_processor: dict = None) -> dict:
    """
    Inicializa todos los servicios con configuración
    
    Args:
        config_cache: Configuración para CacheTemporalManager
        config_processor: Configuración para ProcesadorLogs
        
    Returns:
        Diccionario con instancias de servicios inicializadas
    """
    # Configuración por defecto
    config_cache = config_cache or {'duracion_minutos': 5, 'max_size': 1000}
    config_processor = config_processor or {}
    
    # Crear instancias
    cache_manager = CacheTemporalManager(**config_cache)
    log_processor = ProcesadorLogs(cache_manager=cache_manager, **config_processor)
    
    # Factory de fuentes de datos
    factory_fuentes = FactoryFuentesDatos()
    
    servicios = {
        'cache_manager': cache_manager,
        'log_processor': log_processor,
        'factory_fuentes': factory_fuentes
    }
    
    logging.getLogger(__name__).info("Servicios EcoWatch inicializados completamente")
    return servicios

def crear_demo_completo(num_logs: int = 50) -> dict:
    """
    Crea un demo completo con datos simulados
    
    Args:
        num_logs: Número de logs a generar
        
    Returns:
        Diccionario con servicios y datos de demo
    """
    # Inicializar servicios
    servicios = inicializar_servicios_completos()
    
    # Crear fuente simulada
    fuente_simulada = crear_fuente_simulada(num_logs)
    
    # Generar logs
    logs_demo = fuente_simulada.leer_logs()
    
    # Procesar logs
    resultado_procesamiento = servicios['log_processor'].procesar_lote(logs_demo)
    
    return {
        'servicios': servicios,
        'logs_generados': logs_demo,
        'resultado_procesamiento': resultado_procesamiento,
        'estadisticas_cache': servicios['cache_manager'].obtener_estadisticas()
    }

# Auto-configurar logging al importar
configurar_logging_servicios()