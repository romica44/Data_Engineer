"""
Script de demostración del sistema EcoWatch
"""
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from main import SistemaEcoWatch
from services import FuenteSimulada
from reports import TipoReporte
from config.settings import settings

def setup_logging():
    """Configura logging para la demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    """Función principal de demostración"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🌍 === DEMO SISTEMA ECOWATCH ===")
    print("Iniciando demostración del sistema de monitoreo ambiental...\n")
    
    try:
        # Inicializar sistema
        print("⚙️ Inicializando sistema...")
        sistema = SistemaEcoWatch()
        
        # Generar datos simulados
        print("🎭 Generando datos simulados...")
        fuente_simulada = FuenteSimulada(cantidad_logs=50)
        logs_cargados = sistema.cargar_datos_desde_fuente(fuente_simulada)
        print(f"✅ {logs_cargados} logs simulados cargados\n")
        
        # Mostrar dashboard ejecutivo
        print("📊 === DASHBOARD EJECUTIVO ===")
        dashboard = sistema.obtener_dashboard_ejecutivo()
        
        print(f"🏢 Salas monitoreadas: {dashboard['salas_monitoreadas']}")
        print(f"🚨 Alertas activas: {dashboard['alertas_activas']}")
        print(f"📈 Logs en caché: {dashboard['estado_cache']['logs_en_cache']}")
        print(f"💾 Logs procesados total: {dashboard['resumen_sistema']['estadisticas_procesamiento']['logs_procesados']}")
        print()
        
        # Generar reportes
        print("📋 === GENERANDO REPORTES ===")
        
        # Reporte 1: Estado por sala
        print("1️⃣ Reporte de estado por sala...")
        reporte_estado = sistema.generar_reporte(TipoReporte.ESTADO_POR_SALA)
        print(f"   Salas analizadas: {reporte_estado['resumen']['total_salas']}")
        print(f"   Salas críticas: {reporte_estado['resumen']['salas_criticas']}")
        
        # Reporte 2: Alertas críticas
        print("\n2️⃣ Reporte de alertas críticas...")
        reporte_alertas = sistema.generar_reporte(TipoReporte.ALERTAS_CRITICAS)
        print(f"   Total alertas: {reporte_alertas['resumen_alertas']['total_alertas']}")
        print(f"   Salas afectadas: {reporte_alertas['resumen_alertas']['salas_afectadas']}")
        
        if reporte_alertas.get('recomendaciones'):
            print("   Recomendaciones principales:")
            for i, rec in enumerate(reporte_alertas['recomendaciones'][:3], 1):
                print(f"     {i}. {rec}")
        
        # Consultas específicas
        print("\n🔍 === CONSULTAS ESPECÍFICAS ===")
        alertas_activas = sistema.obtener_alertas_activas()
        print(f"🚨 Alertas críticas activas: {len(alertas_activas)}")
        
        for alerta in alertas_activas[:3]:  # Mostrar máximo 3
            print(f"   • {alerta.sala}: {', '.join(alerta.condiciones_criticas)}")
        
        # Estadísticas del sistema
        print("\n💻 === ESTADÍSTICAS DEL SISTEMA ===")
        cache_stats = sistema.cache_manager.obtener_estadisticas_cache()
        print(f"📊 Eficiencia del caché:")
        print(f"   • Logs en caché: {cache_stats['logs_en_cache']}")
        print(f"   • Salas activas: {cache_stats['salas_activas']}")
        print(f"   • Consultas por sala: {cache_stats['consultas_sala']}")
        print(f"   • Logs críticos: {cache_stats['logs_criticos_activos']}")
        
        # Exportar reportes
        print("\n📁 === EXPORTANDO REPORTES ===")
        settings.crear_directorios()
        reportes_generados = sistema.exportar_reportes_completos()
        print(f"✅ {len(reportes_generados)} reportes exportados a {settings.REPORTS_OUTPUT_DIR}")
        
        print("\n🎉 === DEMO COMPLETADA ===")
        print("✨ Funcionalidades demostradas:")
        print("   • ✅ Generación de datos simulados")
        print("   • ✅ Procesamiento y validación de logs")
        print("   • ✅ Caché temporal optimizado")
        print("   • ✅ Generación de reportes ejecutivos")
        print("   • ✅ Detección de alertas críticas")
        print("   • ✅ Dashboard en tiempo real")
        print("   • ✅ Exportación de reportes")
        print("   • ✅ Arquitectura modular y extensible")
        
        print(f"\n🔗 Archivos generados en: {settings.REPORTS_OUTPUT_DIR}")
        print("🚀 ¡El sistema EcoWatch está funcionando perfectamente!")
        
    except Exception as e:
        logger.error(f"❌ Error en la demostración: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()