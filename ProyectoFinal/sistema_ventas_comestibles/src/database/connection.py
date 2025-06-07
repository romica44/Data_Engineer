import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any
import mysql.connector
from mysql.connector import Error as MySQLError

# Cargar variables de entorno
load_dotenv()

class DatabaseConnection:
    """
    Clase Singleton para manejar la conexión a MySQL usando SQLAlchemy.
    VERSIÓN MEJORADA con diagnóstico automático de problemas de conexión.
    
    Patrón implementado: Singleton
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
        self.user = os.getenv('DB_USER', "root")
        self.password = os.getenv('DB_PASSWORD', "")  # Valor por defecto vacío
        
        # 🔧 CAMBIO CRÍTICO: Múltiples nombres de BD posibles
        self.database = os.getenv('DB_NAME', None)
        if not self.database:
            # Probar nombres comunes
            possible_databases = [
                'ventas_comestibles',  # Nombre más probable
                'grocery_sales_db',
                'ventas',
                'sales_db',
                'sistema_ventas'
            ]
            self.database = possible_databases[0]  # Por defecto usar el primero
            self.possible_databases = possible_databases
        else:
            self.possible_databases = [self.database]
        
        # Drivers disponibles en orden de preferencia
        self.drivers = [
            'mysql+pymysql',           # Más compatible
            'mysql+mysqlconnector',    # Driver oficial
            'mysql'                    # Driver básico
        ]
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _test_mysql_service(self) -> bool:
        """Prueba si MySQL está ejecutándose"""
        try:
            # Intentar conectar sin especificar base de datos
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            connection.close()
            self.logger.info("✅ Servicio MySQL está ejecutándose")
            return True
        except MySQLError as e:
            self.logger.error(f"❌ MySQL no está disponible: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error verificando MySQL: {e}")
            return False
    
    def _get_available_databases(self) -> list:
        """Obtiene lista de bases de datos disponibles"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            cursor.close()
            connection.close()
            return databases
        except Exception:
            return []
    
    def _find_best_database(self) -> Optional[str]:
        """Encuentra la mejor base de datos disponible"""
        available_dbs = self._get_available_databases()
        self.logger.info(f"📋 Bases de datos disponibles: {available_dbs}")
        
        # Buscar coincidencias con nuestras opciones
        for db_name in self.possible_databases:
            if db_name in available_dbs:
                self.logger.info(f"✅ Base de datos encontrada: {db_name}")
                return db_name
        
        # Buscar patrones similares
        for available_db in available_dbs:
            if any(keyword in available_db.lower() for keyword in ['ventas', 'sales', 'grocery']):
                self.logger.info(f"🎯 Base de datos candidata encontrada: {available_db}")
                return available_db
        
        return None
    
    def _test_driver(self, driver: str, database: str) -> Optional[object]:
        """Prueba un driver específico"""
        try:
            connection_url = (
                f"{driver}://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{database}"
                f"?charset=utf8mb4"
            )
            
            engine = create_engine(
                connection_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=2,
                max_overflow=5
            )
            
            # Probar conexión
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                if test_value == 1:
                    self.logger.info(f"✅ Driver {driver} funciona correctamente")
                    return engine
            
        except Exception as e:
            self.logger.warning(f"⚠️  Driver {driver} falló: {e}")
            
        return None
    
    def diagnose_connection_issues(self) -> Dict[str, Any]:
        """Ejecuta diagnóstico completo de problemas de conexión"""
        diagnosis = {
            'mysql_service_running': False,
            'available_databases': [],
            'working_drivers': [],
            'config': {},
            'recommendations': []
        }
        
        # 1. Verificar configuración
        diagnosis['config'] = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password_set': bool(self.password),
            'target_database': self.database
        }
        
        print("🔍 EJECUTANDO DIAGNÓSTICO DE CONEXIÓN")
        print("=" * 50)
        
        # 2. Probar servicio MySQL
        print(f"📡 Probando conexión a MySQL en {self.host}:{self.port}...")
        diagnosis['mysql_service_running'] = self._test_mysql_service()
        
        if not diagnosis['mysql_service_running']:
            diagnosis['recommendations'].extend([
                "Verificar que MySQL esté instalado y ejecutándose",
                "Verificar host y puerto de conexión",
                "Verificar credenciales de usuario"
            ])
            return diagnosis
        
        # 3. Listar bases de datos disponibles
        print("📋 Obteniendo bases de datos disponibles...")
        diagnosis['available_databases'] = self._get_available_databases()
        print(f"   Encontradas: {diagnosis['available_databases']}")
        
        # 4. Probar drivers
        print("🔧 Probando drivers disponibles...")
        best_db = self._find_best_database()
        
        if best_db:
            for driver in self.drivers:
                print(f"   Probando {driver} con {best_db}...")
                engine = self._test_driver(driver, best_db)
                if engine:
                    diagnosis['working_drivers'].append({
                        'driver': driver,
                        'database': best_db
                    })
                    engine.dispose()  # Limpiar
        
        # 5. Generar recomendaciones
        if not diagnosis['working_drivers']:
            diagnosis['recommendations'].extend([
                "Instalar driver MySQL: pip install pymysql",
                "Verificar nombre de base de datos",
                "Crear base de datos si no existe"
            ])
        
        return diagnosis
    
    def connect(self) -> bool:
        """
        Establece la conexión con MySQL usando SQLAlchemy con diagnóstico automático
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            if self._engine is not None:
                # Ya tenemos conexión, probar si funciona
                try:
                    with self._engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    return True
                except:
                    # Conexión antigua no funciona, crear nueva
                    self._engine.dispose()
                    self._engine = None
            
            # Ejecutar diagnóstico para encontrar mejor configuración
            diagnosis = self.diagnose_connection_issues()
            
            if not diagnosis['mysql_service_running']:
                self.logger.error("❌ MySQL no está disponible")
                return False
            
            if not diagnosis['working_drivers']:
                self.logger.error("❌ No se encontró driver funcional")
                print("\n💡 RECOMENDACIONES:")
                for rec in diagnosis['recommendations']:
                    print(f"   • {rec}")
                return False
            
            # Usar el mejor driver encontrado
            best_config = diagnosis['working_drivers'][0]
            driver = best_config['driver']
            database = best_config['database']
            
            # Actualizar configuración
            self.database = database
            
            # Crear conexión final
            connection_url = (
                f"{driver}://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{database}"
                f"?charset=utf8mb4"
            )
            
            self._engine = create_engine(
                connection_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5,
                max_overflow=10
            )
            
            # Crear factory de sesiones
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Verificar conexión final
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.logger.info(f"✅ Conexión exitosa usando {driver} → {database}")
            return True
                
        except SQLAlchemyError as e:
            self.logger.error(f"❌ Error SQLAlchemy: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error inesperado: {e}")
            return False
    
    def get_connection(self):
        """Obtiene una conexión del engine"""
        if not self.connect():
            raise SQLAlchemyError("No se pudo establecer conexión a la base de datos")
        return self._engine.connect()
    
    def close_connection(self):
        """Cierra conexión específica (para compatibilidad)"""
        # No hacer nada aquí para mantener el pool activo
        pass
    
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