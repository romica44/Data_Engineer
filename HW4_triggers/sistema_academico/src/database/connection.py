import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Optional, Dict, Any
import pandas as pd

# Cargar variables de entorno si existen
load_dotenv()

class DatabaseConnection:
    """
    Clase Singleton para manejar la conexión a MySQL usando SQLAlchemy.
    Adaptada para el sistema académico.
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls) -> 'DatabaseConnection':
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._setup_config()
            self._setup_logging()
            self.initialized = True
    
    def _setup_config(self):
        """Configura conexión, ya sea desde .env o valores por defecto"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'sistema_academico')

        if not all([self.user, self.database]):
            raise ValueError("Faltan credenciales para conexión (usuario o base de datos)")

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Establece la conexión con SQLAlchemy"""
        try:
            if self._engine is None:
                url = (
                    f"mysql+mysqlconnector://{self.user}:{self.password}"
                    f"@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
                )
                self._engine = create_engine(
                    url,
                    echo=False,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_size=5,
                    max_overflow=10
                )
                self._session_factory = sessionmaker(bind=self._engine)
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.logger.info("✅ Conexión exitosa a MySQL")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error de conexión SQLAlchemy: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            return False

    def disconnect(self):
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self.logger.info("🔒 Conexión cerrada")

    def execute_query_to_dataframe(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Ejecuta una consulta SQL y la retorna como DataFrame"""
        try:
            if not self.connect():
                raise SQLAlchemyError("No se pudo conectar a la base de datos")

            df = pd.read_sql(text(query), con=self._engine, params=params or {})
            self.logger.info(f"📊 Consulta ejecutada. Filas: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando query: {e}")
            raise

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list:
        """Retorna resultado como lista de diccionarios"""
        df = self.execute_query_to_dataframe(query, params)
        return df.to_dict("records")

    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "engine_connected": self._engine is not None
        }