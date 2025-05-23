import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class DatabaseConnection:
    """Clase singleton para manejar la conexión a la base de datos MySQL"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.host = os.getenv('DB_HOST', 'localhost')
            self.port = int(os.getenv('DB_PORT', 3306))
            self.user = os.getenv('DB_USER')
            self.password = os.getenv('DB_PASSWORD')
            self.database = os.getenv('DB_NAME')
            self.initialized = True
            
            # Configurar logging
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            if self._connection is None or not self._connection.is_connected():
                self._connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset='utf8mb4',
                    collation='utf8mb4_unicode_ci'
                )
                self.logger.info("Conexión exitosa a MySQL")
            return self._connection
        except Error as e:
            self.logger.error(f"Error al conectar a MySQL: {e}")
            raise
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            self.logger.info("Conexión cerrada")
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SQL de selección"""
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params)
            return cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error ejecutando consulta: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_insert(self, query, params=None):
        """Ejecuta una consulta SQL de inserción"""
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            connection.rollback()
            self.logger.error(f"Error ejecutando inserción: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_update(self, query, params=None):
        """Ejecuta una consulta SQL de actualización"""
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.rowcount
        finally:
            if cursor:
                cursor.close()