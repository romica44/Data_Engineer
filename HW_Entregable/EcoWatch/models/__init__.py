"""
Modelos del Sistema EcoWatch
Contiene las definiciones de todos los modelos de datos del sistema
"""

# Importar modelos principales
from .log import Log, EstadoLog, crear_log_desde_sensores, validar_lote_logs
from .sala import Sala, TipoSala, EstadoSala, crear_sala_basica, obtener_salas_por_tipo, calcular_capacidad_total
from .sensor import (
    Sensor, TipoSensor, EstadoSensor, CalidadSenal,
    crear_sensor_basico, obtener_sensores_por_sala, obtener_sensores_activos,
    obtener_sensores_por_tipo, generar_reporte_salud_sensores
)

# Versión del package de modelos
__version__ = "1.0.0"

# Lista de todos los modelos disponibles
__all__ = [
    # Modelos principales
    'Log',
    'Sala', 
    'Sensor',
    
    # Enums
    'EstadoLog',
    'TipoSala',
    'EstadoSala',
    'TipoSensor',
    'EstadoSensor',
    'CalidadSenal',
    
    # Funciones de utilidad para Log
    'crear_log_desde_sensores',
    'validar_lote_logs',
    
    # Funciones de utilidad para Sala
    'crear_sala_basica',
    'obtener_salas_por_tipo',
    'calcular_capacidad_total',
    
    # Funciones de utilidad para Sensor
    'crear_sensor_basico',
    'obtener_sensores_por_sala',
    'obtener_sensores_activos',
    'obtener_sensores_por_tipo',
    'generar_reporte_salud_sensores'
]

# Metadatos del package
__author__ = "Sistema EcoWatch"
__description__ = "Modelos de datos para monitoreo ambiental"

def obtener_version():
    """Retorna la versión actual del package de modelos"""
    return __version__

def listar_modelos():
    """Retorna una lista de todos los modelos disponibles"""
    return ['Log', 'Sala', 'Sensor']

def obtener_info_modelos():
    """Retorna información detallada de todos los modelos"""
    return {
        'Log': {
            'descripcion': 'Registros de monitoreo ambiental',
            'tabla_mysql': 'logs',
            'campos_principales': ['timestamp', 'sala', 'estado', 'temperatura', 'humedad', 'co2'],
            'enums': ['EstadoLog']
        },
        'Sala': {
            'descripcion': 'Salas monitoreadas del sistema',
            'tabla_mysql': 'salas', 
            'campos_principales': ['nombre', 'ubicacion', 'capacidad_personas', 'tipo_sala'],
            'enums': ['TipoSala', 'EstadoSala']
        },
        'Sensor': {
            'descripcion': 'Sensores de monitoreo ambiental',
            'tabla_mysql': 'sensores',
            'campos_principales': ['id_sensor', 'sala_id', 'tipo', 'activo', 'ultima_lectura'],
            'enums': ['TipoSensor', 'EstadoSensor', 'CalidadSenal']
        }
    }