"""
Script para verificar el estado de la base de datos MySQL
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from database import DatabaseConnection, DatabaseMigrations, LogRepository, SalaRepository

def setup_logging():
    """Configura logging para el script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_database_connection():
    """Verifica la conexión a la base de datos"""
    print("🔍 Verificando conexión a MySQL...")
    
    try:
        if DatabaseConnection.test_connection():
            print("✅ Conexión a MySQL exitosa")
            return True
        else:
            print("❌ No se pudo conectar a MySQL")
            return False
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {str(e)}")
        return False

def check_database_schema():
    """Verifica el esquema de la base de datos"""
    print("\n🏗️ Verificando esquema de base de datos...")
    
    try:
        schema_status = DatabaseMigrations.verify_schema()
        
        all_tables_ok = True
        for table, exists in schema_status.items():
            status = "✅" if exists else "❌"
            print(f"   {status} Tabla '{table}': {'OK' if exists else 'FALTA'}")
            if not exists:
                all_tables_ok = False
        
        if all_tables_ok:
            print("✅ Esquema de base de datos completo")
        else:
            print("⚠️ Faltan algunas tablas del esquema")
        
        return all_tables_ok
        
    except Exception as e:
        print(f"❌ Error verificando esquema: {str(e)}")
        return False

def check_data_content():
    """Verifica el contenido de datos en las tablas"""
    print("\n📊 Verificando contenido de datos...")
    
    try:
        # Verificar logs
        logs_recientes = LogRepository.get_recent_logs(minutes=60)  # Última hora
        print(f"   📝 Logs última hora: {len(logs_recientes)}")
        
        # Verificar estadísticas por sala
        stats_salas = LogRepository.get_estadisticas_por_sala()
        print(f"   🏢 Salas con datos: {len(stats_salas)}")
        
        # Verificar logs críticos
        logs_criticos = LogRepository.get_critical_logs(hours=24)  # Último día
        print(f"   🚨 Logs críticos (24h): {len(logs_criticos)}")
        
        # Mostrar detalles de salas
        if stats_salas:
            print("\n   📈 Estadísticas por sala:")
            for sala, stats in stats_salas.items():
                print(f"      • {sala}: {stats['total_logs']} logs, "
                      f"{stats['logs_criticos']} críticos, "
                      f"temp prom: {stats['temperatura']['promedio']:.1f}°C")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando datos: {str(e)}")
        return False

def check_system_performance():
    """Verifica métricas de rendimiento del sistema"""
    print("\n⚡ Verificando rendimiento del sistema...")
    
    try:
        import time
        from services import CacheTemporalManager
        
        # Test de performance del caché
        cache_manager = CacheTemporalManager()
        
        start_time = time.time()
        stats_cache = cache_manager.obtener_estadisticas_cache()
        cache_time = time.time() - start_time
        
        print(f"   💾 Caché temporal: {stats_cache['logs_en_cache']} logs")
        print(f"   ⏱️ Tiempo consulta caché: {cache_time*1000:.2f}ms")
        
        # Test de conexión a BD
        start_time = time.time()
        with DatabaseConnection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM logs")
            total_logs = cursor.fetchone()[0]
        db_time = time.time() - start_time
        
        print(f"   🗄️ Total logs en BD: {total_logs}")
        print(f"   ⏱️ Tiempo consulta BD: {db_time*1000:.2f}ms")
        
        # Evaluación de rendimiento
        if cache_time < 0.001 and db_time < 0.1:
            print("✅ Rendimiento del sistema: EXCELENTE")
        elif cache_time < 0.01 and db_time < 0.5:
            print("✅ Rendimiento del sistema: BUENO")
        else:
            print("⚠️ Rendimiento del sistema: NECESITA OPTIMIZACIÓN")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando rendimiento: {str(e)}")
        return False

def generate_health_report():
    """Genera un reporte de salud del sistema"""
    print("\n📋 Generando reporte de salud del sistema...")
    
    from datetime import datetime
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'database_connection': False,
        'schema_complete': False,
        'data_available': False,
        'performance_ok': False,
        'overall_health': 'UNKNOWN'
    }
    
    # Ejecutar verificaciones
    report['database_connection'] = check_database_connection()
    report['schema_complete'] = check_database_schema()
    report['data_available'] = check_data_content()
    report['performance_ok'] = check_system_performance()
    
    # Calcular salud general
    checks_passed = sum([
        report['database_connection'],
        report['schema_complete'], 
        report['data_available'],
        report['performance_ok']
    ])
    
    if checks_passed == 4:
        report['overall_health'] = 'EXCELLENT'
        health_emoji = '🟢'
    elif checks_passed == 3:
        report['overall_health'] = 'GOOD'
        health_emoji = '🟡'
    elif checks_passed >= 2:
        report['overall_health'] = 'WARNING'
        health_emoji = '🟠'
    else:
        report['overall_health'] = 'CRITICAL'
        health_emoji = '🔴'
    
    print(f"\n{health_emoji} === REPORTE DE SALUD FINAL ===")
    print(f"Estado general: {report['overall_health']}")
    print(f"Verificaciones pasadas: {checks_passed}/4")
    
    if checks_passed < 4:
        print("\n🔧 Acciones recomendadas:")
        if not report['database_connection']:
            print("   • Verificar configuración de MySQL en .env")
            print("   • Asegurar que MySQL esté ejecutándose")
        if not report['schema_complete']:
            print("   • Ejecutar: python scripts/create_tables.py")
        if not report['data_available']:
            print("   • Cargar datos: python scripts/load_data.py --file datos.csv")
        if not report['performance_ok']:
            print("   • Revisar configuración de conexiones de BD")
            print("   • Considerar optimización de índices")
    
    return report

def main():
    """Función principal del script"""
    setup_logging()
    
    print("🏥 === DIAGNÓSTICO DE SALUD DEL SISTEMA ECOWATCH ===")
    print(f"Configuración actual:")
    print(f"   • Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"   • Base de datos: {settings.DB_NAME}")
    print(f"   • Usuario: {settings.DB_USER}")
    print()
    
    # Generar reporte completo
    health_report = generate_health_report()
    
    # Guardar reporte
    try:
        import json
        from pathlib import Path
        
        reports_dir = Path(settings.REPORTS_OUTPUT_DIR)
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(health_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {report_file}")
        
    except Exception as e:
        print(f"⚠️ No se pudo guardar el reporte: {str(e)}")
    
    print("\n🎯 === DIAGNÓSTICO COMPLETADO ===")
    return health_report['overall_health'] in ['EXCELLENT', 'GOOD']

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
