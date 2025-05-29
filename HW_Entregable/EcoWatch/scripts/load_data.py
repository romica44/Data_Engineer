"""
Script para cargar datos desde CSV a la base de datos MySQL
"""
import sys
import argparse
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from services import FuenteCSV, FuenteJSON, ProcesadorLogs
from database import DatabaseConnection, DatabaseMigrations
from config.settings import settings

def setup_logging():
    """Configura logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('load_data.log')
        ]
    )

def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Cargar datos al sistema EcoWatch')
    parser.add_argument('--file', '-f', required=True, help='Archivo de datos a cargar')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Formato del archivo')
    parser.add_argument('--batch-size', type=int, default=1000, help='Tamaño de lote para inserción')
    parser.add_argument('--validate-only', action='store_true', help='Solo validar, no insertar')
    parser.add_argument('--create-tables', action='store_true', help='Crear tablas si no existen')
    
    return parser.parse_args()

def main():
    """Función principal para cargar datos"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    args = parse_arguments()
    
    logger.info(f"📁 Cargando datos desde: {args.file}")
    logger.info(f"📊 Formato: {args.format}")
    
    # Verificar que el archivo existe
    archivo_path = Path(args.file)
    if not archivo_path.exists():
        logger.error(f"❌ Archivo no encontrado: {args.file}")
        sys.exit(1)
    
    try:
        # Verificar/crear base de datos si es necesario
        if args.create_tables:
            logger.info("🏗️ Verificando/creando tablas...")
            DatabaseMigrations.create_all_tables()
        
        # Verificar conexión
        if not DatabaseConnection.test_connection():
            logger.error("❌ No se pudo conectar a la base de datos")
            sys.exit(1)
        
        # Crear fuente de datos apropiada
        if args.format == 'csv':
            fuente = FuenteCSV(str(archivo_path))
        elif args.format == 'json':
            fuente = FuenteJSON(str(archivo_path))
        else:
            logger.error(f"❌ Formato no soportado: {args.format}")
            sys.exit(1)
        
        # Leer datos
        logger.info("📖 Leyendo datos desde archivo...")
        logs_data = fuente.leer_logs()
        
        if not logs_data:
            logger.warning("⚠️ No se encontraron datos válidos en el archivo")
            sys.exit(0)
        
        logger.info(f"✅ Leídos {len(logs_data)} registros válidos")
        
        if args.validate_only:
            logger.info("✅ Validación completada. No se insertaron datos (--validate-only)")
            sys.exit(0)
        
        # Procesar datos
        logger.info("💾 Iniciando carga a base de datos...")
        procesador = ProcesadorLogs()
        
        # Procesar en lotes si el archivo es grande
        if len(logs_data) > args.batch_size:
            logger.info(f"📦 Procesando en lotes de {args.batch_size}")
            total_procesados = 0
            
            for i in range(0, len(logs_data), args.batch_size):
                lote = logs_data[i:i + args.batch_size]
                procesados = procesador.procesar_lote_logs(lote)
                total_procesados += procesados
                
                logger.info(f"📊 Progreso: {total_procesados}/{len(logs_data)} registros procesados")
        else:
            # Procesar todo de una vez
            total_procesados = procesador.procesar_lote_logs(logs_data)
        
        # Mostrar resumen
        resumen = procesador.obtener_resumen_procesamiento()
        logger.info("📈 Resumen de carga:")
        logger.info(f"  ✅ Logs procesados: {resumen['estadisticas_procesamiento']['logs_procesados']}")
        logger.info(f"  ❌ Logs inválidos: {resumen['estadisticas_procesamiento']['logs_invalidos']}")
        logger.info(f"  🚨 Logs críticos: {resumen['estadisticas_procesamiento']['logs_criticos']}")
        logger.info(f"  📊 Tasa de éxito: {resumen['estadisticas_procesamiento']['tasa_exito']:.1f}%")
        logger.info(f"  🏢 Salas detectadas: {resumen['estado_sistema']['salas_monitoreadas']}")
        
        logger.info("🎉 ¡Carga de datos completada exitosamente!")
        
    except Exception as e:
        logger.error(f"❌ Error durante la carga de datos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
