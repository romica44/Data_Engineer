"""
Script para crear todas las tablas del sistema EcoWatch en MySQL
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from database import DatabaseMigrations, DatabaseConnection

def setup_logging():
    """Configura logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('create_tables.log')
        ]
    )

def main():
    """Función principal para crear tablas"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🏗️ Iniciando creación de tablas del sistema EcoWatch")
    
    try:
        # Verificar configuración
        logger.info(f"Conectando a: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        
        # Probar conexión
        if not DatabaseConnection.test_connection():
            logger.error("❌ No se pudo conectar a la base de datos")
            sys.exit(1)
        
        # Crear base de datos y tablas
        logger.info("📋 Creando base de datos...")
        DatabaseMigrations.create_database()
        
        logger.info("🏗️ Creando tablas...")
        DatabaseMigrations.create_all_tables()
        
        # Verificar esquema
        logger.info("✅ Verificando esquema creado...")
        schema_status = DatabaseMigrations.verify_schema()
        
        for table, exists in schema_status.items():
            status = "✅" if exists else "❌"
            logger.info(f"  {status} Tabla '{table}': {'OK' if exists else 'FALTA'}")
        
        if all(schema_status.values()):
            logger.info("🎉 ¡Todas las tablas fueron creadas exitosamente!")
        else:
            logger.error("❌ Algunas tablas no fueron creadas correctamente")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error durante la creación de tablas: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()