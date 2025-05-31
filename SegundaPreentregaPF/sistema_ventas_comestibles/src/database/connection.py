import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any

# Cargar variables de entorno
load_dotenv()

class DatabaseConnection:
    """
    Clase Singleton para manejar la conexión a MySQL usando SQLAlchemy.
    
    Patrón implementado: Singleton
    Problema que resuelve: Garantiza una única instancia de conexión a la base de datos
    en toda la aplicación, evitando múltiples conexiones innecesarias y mejorando
    el rendimiento y control de recursos.
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls) -> 'DatabaseConnection':
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión solo una vez"""
        if not hasattr(self, 'initialized'):
            self._setup_database_config()
            self._setup_logging()
            self.initialized = True
    
    def _setup_database_config(self):
        """Configura los parámetros de conexión desde variables de entorno"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        
        # Validar que las credenciales estén disponibles
        if not all([self.user, self.password, self.database]):
            raise ValueError("Faltan credenciales de base de datos en el archivo .env")
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Establece la conexión con MySQL usando SQLAlchemy
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            if self._engine is None:
                # Crear la URL de conexión para MySQL
                connection_url = (
                    f"mysql+mysqlconnector://{self.user}:{self.password}"
                    f"@{self.host}:{self.port}/{self.database}"
                    f"?charset=utf8mb4&collation=utf8mb4_unicode_ci"
                )
                
                # Crear el engine de SQLAlchemy
                self._engine = create_engine(
                    connection_url,
                    echo=False,  # Cambiar a True para ver las consultas SQL
                    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
                    pool_recycle=3600,   # Reciclar conexiones cada hora
                    pool_size=5,         # Tamaño del pool de conexiones
                    max_overflow=10      # Conexiones adicionales permitidas
                )
                
                # Crear factory de sesiones
                self._session_factory = sessionmaker(bind=self._engine)
                
                # Probar la conexión
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                self.logger.info("✅ Conexión exitosa a MySQL usando SQLAlchemy")
                return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error al conectar con SQLAlchemy: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self.logger.info("🔒 Conexión cerrada")
    
    def execute_query_to_dataframe(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Ejecuta una consulta SQL y retorna los resultados como DataFrame de pandas
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (dict, optional): Parámetros para la consulta
            
        Returns:
            pd.DataFrame: Resultados de la consulta
            
        Raises:
            SQLAlchemyError: Si hay error en la consulta
        """
        try:
            if not self.connect():
                raise SQLAlchemyError("No se pudo establecer conexión a la base de datos")
            
            # Ejecutar la consulta y convertir a DataFrame
            df = pd.read_sql(
                sql=text(query),
                con=self._engine,
                params=params or {}
            )
            
            self.logger.info(f"📊 Consulta ejecutada exitosamente. Filas retornadas: {len(df)}")
            return df
            
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error ejecutando consulta: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list:
        """
        Ejecuta una consulta SQL y retorna los resultados como lista de diccionarios
        (Método mantenido para compatibilidad con código existente)
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (dict, optional): Parámetros para la consulta
            
        Returns:
            list: Resultados de la consulta como lista de diccionarios
        """
        df = self.execute_query_to_dataframe(query, params)
        return df.to_dict('records')
    
    def execute_insert(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Ejecuta una consulta de inserción SQL
        
        Args:
            query (str): Consulta SQL de inserción
            params (dict, optional): Parámetros para la consulta
            
        Returns:
            int: ID del último registro insertado
        """
        try:
            if not self.connect():
                raise SQLAlchemyError("No se pudo establecer conexión a la base de datos")
            
            with self._engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                last_id = result.lastrowid
                
            self.logger.info(f"✅ Inserción exitosa. ID generado: {last_id}")
            return last_id
            
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error en inserción: {e}")
            raise
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Ejecuta una consulta de actualización SQL
        
        Args:
            query (str): Consulta SQL de actualización
            params (dict, optional): Parámetros para la consulta
            
        Returns:
            int: Número de filas afectadas
        """
        try:
            if not self.connect():
                raise SQLAlchemyError("No se pudo establecer conexión a la base de datos")
            
            with self._engine.begin() as conn:
                result = conn.execute(text(query), params or {})
                rows_affected = result.rowcount
                
            self.logger.info(f"✅ Actualización exitosa. Filas afectadas: {rows_affected}")
            return rows_affected
            
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error en actualización: {e}")
            raise
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre la conexión actual
        
        Returns:
            dict: Información de la conexión
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'engine_connected': self._engine is not None,
            'pattern': 'Singleton'
        }
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión a la base de datos
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            df = self.execute_query_to_dataframe("SELECT 1 as test_column")
            return len(df) > 0 and df.iloc[0]['test_column'] == 1
        except:
            return False