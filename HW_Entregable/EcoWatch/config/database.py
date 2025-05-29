"""
Configuración específica de la base de datos MySQL
Gestiona conexiones, pools y configuraciones de MySQL
"""

import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
import logging
from typing import Optional, Dict, Any, Generator
import time
from .settings import DATABASE_CONFIG, SYSTEM_CONFIG

# Configurar logging para este módulo
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN DE POOL DE CONEXIONES ===
POOL_CONFIG = {
    'pool_name': 'ecowatch_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'autocommit': True,
    'use_unicode': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'time_zone': '+00:00'
}

# === CONFIGURACIÓN DE CONEXIÓN ===
CONNECTION_CONFIG = {
    **DATABASE_CONFIG,
    **POOL_CONFIG,
    'connect_timeout': 10,
    'auth_plugin': 'mysql_native_password',
    'raise_on_warnings': True,
    'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
}

# === QUERIES PREDEFINIDAS ===
QUERIES = {
    'check_connection': "SELECT 1",
    'check_tables': """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = %s
    """,
    'table_exists': """
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_name = %s
    """,
    'get_table_info': """
        DESCRIBE %s
    """,
    'get_db_status': """
        SHOW STATUS LIKE 'Threads_connected'
    """
}

class DatabaseConfig:
    """
    Clase para gestionar la configuración y conexiones de la base de datos
    """
    
    _pool: Optional[pooling.MySQLConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls) -> None:
        """
        Inicializa el pool de conexiones de MySQL
        
        Raises:
            Error: Si no se puede establecer el pool de conexiones
        """
        try:
            if cls._pool is None:
                logger.info("Inicializando pool de conexiones MySQL...")
                cls._pool = pooling.MySQLConnectionPool(**CONNECTION_CONFIG)
                logger.info(f"Pool inicializado: {cls._pool.pool_name} con {cls._pool.pool_size} conexiones")
            else:
                logger.debug("Pool ya inicializado")
        except Error as e:
            logger.error(f"Error al inicializar pool de conexiones: {e}")
            raise
    
    @classmethod
    def get_connection(cls) -> mysql.connector.MySQLConnection:
        """
        Obtiene una conexión del pool
        
        Returns:
            Conexión MySQL del pool
            
        Raises:
            Error: Si no se puede obtener una conexión
        """
        if cls._pool is None:
            cls.initialize_pool()
        
        try:
            connection = cls._pool.get_connection()
            if not connection.is_connected():
                connection.reconnect(attempts=SYSTEM_CONFIG['retry_attempts'], 
                                   delay=SYSTEM_CONFIG['retry_delay'])
            return connection
        except Error as e:
            logger.error(f"Error al obtener conexión del pool: {e}")
            raise
    
    @classmethod
    @contextmanager
    def get_cursor(cls, dictionary: bool = True) -> Generator[mysql.connector.cursor.MySQLCursor, None, None]:
        """
        Context manager para obtener un cursor de forma segura
        
        Args:
            dictionary: Si devolver resultados como diccionarios
            
        Yields:
            Cursor MySQL
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=dictionary, buffered=True)
            yield cursor
        except Error as e:
            if connection and connection.is_connected():
                connection.rollback()
            logger.error(f"Error en operación de base de datos: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        Prueba la conexión a la base de datos
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            with cls.get_cursor() as cursor:
                cursor.execute(QUERIES['check_connection'])
                result = cursor.fetchone()
                logger.info("Conexión a base de datos exitosa")
                return result is not None
        except Error as e:
            logger.error(f"Error al probar conexión: {e}")
            return False
    
    @classmethod
    def get_database_info(cls) -> Dict[str, Any]:
        """
        Obtiene información sobre la base de datos
        
        Returns:
            Diccionario con información de la base de datos
        """
        info = {
            'database': DATABASE_CONFIG['database'],
            'host': DATABASE_CONFIG['host'],
            'port': DATABASE_CONFIG['port'],
            'connected': False,
            'tables': [],
            'pool_size': POOL_CONFIG['pool_size'] if cls._pool else 0
        }
        
        try:
            with cls.get_cursor() as cursor:
                info['connected'] = True
                
                # Obtener lista de tablas
                cursor.execute(QUERIES['check_tables'], (DATABASE_CONFIG['database'],))
                tables = cursor.fetchall()
                info['tables'] = [table['table_name'] for table in tables]
                
                # Obtener estado de conexiones
                cursor.execute(QUERIES['get_db_status'])
                status = cursor.fetchone()
                if status:
                    info['active_connections'] = status['Value']
                    
        except Error as e:
            logger.error(f"Error al obtener información de base de datos: {e}")
            info['error'] = str(e)
        
        return info
    
    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos
        
        Args:
            table_name: Nombre de la tabla a verificar
            
        Returns:
            True si la tabla existe, False en caso contrario
        """
        try:
            with cls.get_cursor() as cursor:
                cursor.execute(QUERIES['table_exists'], 
                             (DATABASE_CONFIG['database'], table_name))
                result = cursor.fetchone()
                return result and result['COUNT(*)'] > 0
        except Error as e:
            logger.error(f"Error al verificar tabla {table_name}: {e}")
            return False
    
    @classmethod
    def get_table_schema(cls, table_name: str) -> Optional[list]:
        """
        Obtiene el esquema de una tabla
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista con información de columnas o None si hay error
        """
        try:
            with cls.get_cursor() as cursor:
                # Usar query interpolada de forma segura para DESCRIBE
                query = f"DESCRIBE `{table_name}`"
                cursor.execute(query)
                return cursor.fetchall()
        except Error as e:
            logger.error(f"Error al obtener esquema de tabla {table_name}: {e}")
            return None
    
    @classmethod
    def execute_script(cls, script: str) -> bool:
        """
        Ejecuta un script SQL (útil para migraciones)
        
        Args:
            script: Script SQL a ejecutar
            
        Returns:
            True si se ejecutó exitosamente, False en caso contrario
        """
        try:
            with cls.get_cursor() as cursor:
                # Dividir script en statements individuales
                statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]
                
                for statement in statements:
                    cursor.execute(statement)
                    
                logger.info(f"Script ejecutado exitosamente: {len(statements)} statements")
                return True
                
        except Error as e:
            logger.error(f"Error al ejecutar script: {e}")
            return False
    
    @classmethod
    def close_pool(cls) -> None:
        """
        Cierra el pool de conexiones
        """
        if cls._pool:
            try:
                # No hay método directo para cerrar pool en mysql-connector-python
                # Solo asignamos None para permitir garbage collection
                cls._pool = None
                logger.info("Pool de conexiones cerrado")
            except Exception as e:
                logger.error(f"Error al cerrar pool: {e}")

# === FUNCIONES DE UTILIDAD ===
def get_connection_string() -> str:
    """
    Genera una cadena de conexión para logging (sin password)
    
    Returns:
        String de conexión para logs
    """
    return (f"mysql://{DATABASE_CONFIG['user']}@"
            f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/"
            f"{DATABASE_CONFIG['database']}")

def retry_on_failure(retries: int = 3, delay: float = 1.0):
    """
    Decorador para reintentar operaciones de base de datos
    
    Args:
        retries: Número de reintentos
        delay: Delay entre reintentos en segundos
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Error as e:
                    last_exception = e
                    if attempt < retries:
                        logger.warning(f"Intento {attempt + 1} falló, reintentando en {delay}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"Todos los intentos fallaron para {func.__name__}")
                        
            raise last_exception
        return wrapper
    return decorator

# === INICIALIZACIÓN ===
def initialize_database():
    """
    Inicializa la configuración de base de datos
    """
    try:
        DatabaseConfig.initialize_pool()
        
        if DatabaseConfig.test_connection():
            logger.info("Base de datos inicializada correctamente")
            info = DatabaseConfig.get_database_info()
            logger.info(f"Conectado a: {get_connection_string()}")
            logger.info(f"Tablas disponibles: {', '.join(info['tables'])}")
        else:
            logger.error("No se pudo establecer conexión con la base de datos")
            
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        raise

# Auto-inicialización si no estamos en testing
if not SYSTEM_CONFIG.get('testing', False):
    try:
        initialize_database()
    except Exception as e:
        logger.warning(f"Auto-inicialización falló: {e}")

# === CLEANUP ===
import atexit

def cleanup_database():
    """Función de limpieza al salir del programa"""
    DatabaseConfig.close_pool()

atexit.register(cleanup_database)