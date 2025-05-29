"""
Configuraciones generales del sistema EcoWatch
Centraliza todas las constantes y configuraciones del sistema
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# === CONFIGURACIÓN DE BASE DE DATOS ===
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ecowatch_db'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'use_unicode': True
}

# === CONFIGURACIÓN DEL CACHÉ ===
CACHE_CONFIG = {
    'duration_minutes': int(os.getenv('CACHE_DURATION_MINUTES', 5)),
    'max_size': 1000,  # Máximo número de registros en caché
    'cleanup_threshold': 50  # Eliminar registros cuando se exceda el max_size
}

# === UMBRALES AMBIENTALES ===
THRESHOLDS = {
    'temperatura': {
        'min': float(os.getenv('TEMP_MIN', 18.0)),
        'max': float(os.getenv('TEMP_MAX', 30.0)),
        'critical_low': 15.0,
        'critical_high': 35.0
    },
    'humedad': {
        'min': float(os.getenv('HUMEDAD_MIN', 20.0)),
        'max': float(os.getenv('HUMEDAD_MAX', 80.0)),
        'critical_low': 10.0,
        'critical_high': 90.0
    },
    'co2': {
        'max': int(os.getenv('CO2_MAX', 1000)),
        'critical': 1500,
        'danger': 2000
    }
}

# === CONFIGURACIÓN DE LOGGING ===
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.getenv('LOG_FILE', 'ecowatch_system.log'),
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# === CONFIGURACIÓN DE REPORTES ===
REPORTS_CONFIG = {
    'output_dir': Path(os.getenv('REPORTS_OUTPUT_DIR', './reportes/')),
    'export_formats': os.getenv('EXPORT_FORMAT', 'json,csv').split(','),
    'max_records_per_report': 10000,
    'date_format': '%Y-%m-%d_%H-%M-%S'
}

# === CONFIGURACIÓN DEL SISTEMA ===
SYSTEM_CONFIG = {
    'timezone': 'America/Argentina/Buenos_Aires',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'batch_size': 1000,  # Registros a procesar por lote
    'retry_attempts': 3,
    'retry_delay': 1.0  # segundos
}

# === VALIDACIÓN DE DATOS ===
VALIDATION_CONFIG = {
    'required_fields': {'timestamp', 'sala', 'estado', 'temperatura', 'humedad', 'co2'},
    'allowed_estados': {'INFO', 'WARNING', 'ERROR'},
    'max_sala_name_length': 50,
    'max_message_length': 1000
}

# === CONFIGURACIÓN DE ALERTAS ===
ALERTS_CONFIG = {
    'enable_email': False,
    'enable_slack': False,
    'enable_webhook': False,
    'cooldown_minutes': 15,  # Tiempo mínimo entre alertas del mismo tipo
    'severity_levels': ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
}

# === CONFIGURACIÓN DE ANÁLISIS ===
ANALYSIS_CONFIG = {
    'window_size_minutes': 60,  # Ventana de análisis en minutos
    'trend_analysis_points': 10,  # Puntos mínimos para análisis de tendencias
    'statistical_confidence': 0.95,
    'outlier_threshold': 2.0  # Desviaciones estándar para detectar outliers
}

# === CONFIGURACIÓN DE DESARROLLO ===
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
TESTING = os.getenv('TESTING', 'False').lower() == 'true'

# === PATHS IMPORTANTES ===
PATHS = {
    'data_dir': BASE_DIR / 'data',
    'logs_dir': BASE_DIR / 'logs',
    'reports_dir': REPORTS_CONFIG['output_dir'],
    'config_dir': BASE_DIR / 'config',
    'scripts_dir': BASE_DIR / 'scripts'
}

# Crear directorios si no existen
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

# === FUNCIONES DE UTILIDAD ===
def get_config_value(section: str, key: str, default=None):
    """
    Obtiene un valor de configuración de manera segura
    
    Args:
        section: Sección de configuración (ej: 'DATABASE_CONFIG')
        key: Clave dentro de la sección
        default: Valor por defecto si no se encuentra
    
    Returns:
        Valor de configuración o default
    """
    config_map = {
        'database': DATABASE_CONFIG,
        'cache': CACHE_CONFIG,
        'thresholds': THRESHOLDS,
        'logging': LOGGING_CONFIG,
        'reports': REPORTS_CONFIG,
        'system': SYSTEM_CONFIG,
        'validation': VALIDATION_CONFIG,
        'alerts': ALERTS_CONFIG,
        'analysis': ANALYSIS_CONFIG
    }
    
    section_config = config_map.get(section.lower())
    if section_config is None:
        return default
    
    return section_config.get(key, default)

def validate_config():
    """
    Valida que todas las configuraciones críticas estén presentes
    
    Raises:
        ValueError: Si falta alguna configuración crítica
    """
    required_configs = [
        ('DATABASE_CONFIG', 'host'),
        ('DATABASE_CONFIG', 'database'),
        ('THRESHOLDS', 'temperatura'),
        ('THRESHOLDS', 'humedad'),
        ('THRESHOLDS', 'co2')
    ]
    
    for section, key in required_configs:
        config_section = globals().get(section)
        if not config_section or key not in config_section:
            raise ValueError(f"Configuración requerida faltante: {section}.{key}")

# Validar configuración al importar
if not TESTING:
    validate_config()

# === CONFIGURACIÓN ESPECÍFICA POR AMBIENTE ===
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()

if ENVIRONMENT == 'production':
    LOGGING_CONFIG['level'] = 'WARNING'
    CACHE_CONFIG['max_size'] = 5000
    SYSTEM_CONFIG['batch_size'] = 5000
elif ENVIRONMENT == 'testing':
    LOGGING_CONFIG['level'] = 'DEBUG'
    DATABASE_CONFIG['database'] = 'ecowatch_test_db'
    CACHE_CONFIG['max_size'] = 100