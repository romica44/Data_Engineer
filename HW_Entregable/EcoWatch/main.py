"""
Sistema Principal EcoWatch - Monitoreo Ambiental Integrado
=========================================================
"""

import sys
import argparse
import logging
import signal
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configurar el path para imports
sys.path.append(str(Path(__file__).parent))

# Imports del sistema EcoWatch
from config.settings import (
    LOGGING_CONFIG,
    DATABASE_CONFIG,
    CACHE_CONFIG,
    THRESHOLDS,
    SYSTEM_CONFIG,
    REPORTS_CONFIG,
    validate_config,
    get_config_value,
    PATHS
)
from config.database import (
    DatabaseConfig,
    initialize_database,
    get_connection_string
)
from services import (
    CacheTemporalManager, ProcesadorLogs,
    FuenteCSV, FuenteJSON, FuenteSimulada, FuenteDatabase,
    FactoryFuentesDatos, crear_fuente_csv, crear_fuente_simulada
)
from reports import (
    FactoryReportes, 
    TipoReporte, 
    AnalisisEstadistico, 
    AnalisisTendencias,
    AnalisisComparativo
)
from models import (
    Log, Sala, Sensor,
    EstadoLog, TipoSala, EstadoSensor, TipoSensor,
    crear_log_desde_sensores, crear_sala_basica, crear_sensor_basico,
    validar_lote_logs, obtener_sensores_activos
)
from utils.decorators import benchmark, log_operation

# Configurar logging
def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

class SistemaEcoWatch:
    """
    Sistema principal que orquesta todos los componentes del monitoreo ambiental.
    
    Implementa el patrón Facade proporcionando una interfaz simplificada
    para interactuar con el sistema completo.
    
    Características principales:
    - Gestión automática de conexiones a base de datos
    - Procesamiento en tiempo real de logs
    - Caché temporal para consultas rápidas
    - Generación de reportes ejecutivos
    - API REST integrada
    - Manejo robusto de errores
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.procesador = None
        self.cache_manager = None
        self.factory_reportes = None
        self.is_initialized = False
        self.stats = {
            'inicio_sistema': datetime.now(),
            'logs_procesados_total': 0,
            'reportes_generados': 0,
            'consultas_api': 0
        }
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("🌍 Sistema EcoWatch inicializado")
    
    @log_operation
    def inicializar_sistema(self) -> bool:
        """
        Inicializa todos los componentes del sistema.
        
        Returns:
            True si la inicialización fue exitosa
        """
        try:
            self.logger.info("⚙️ Iniciando componentes del sistema...")
            
            # 1. Verificar configuración
            if not self._verificar_configuracion():
                return False
            
            # 2. Inicializar base de datos
            if not self._inicializar_base_datos():
                return False
            
            # 3. Inicializar componentes principales
            self._inicializar_componentes()
            
            # 4. Verificar estado del sistema
            if not self._verificar_estado_sistema():
                return False
            
            self.is_initialized = True
            self.logger.info("✅ Sistema EcoWatch inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando sistema: {str(e)}")
            return False
    
    def _verificar_configuracion(self) -> bool:
        """Verifica que la configuración sea válida"""
        try:
            # Verificar configuración de base de datos
            if not all([settings.DB_HOST, settings.DB_USER, settings.DB_NAME]):
                self.logger.error("❌ Configuración de base de datos incompleta")
                return False
            
            # Crear directorios necesarios
            settings.crear_directorios()
            
            self.logger.info("✅ Configuración verificada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando configuración: {str(e)}")
            return False
    
    def _inicializar_base_datos(self) -> bool:
        """Inicializa la conexión y estructura de base de datos"""
        try:
            # Crear base de datos si no existe
            DatabaseConfig.create_database_if_not_exists()
            
            # Inicializar pool de conexiones
            DatabaseConnection.initialize_pool()
            
            # Verificar conexión
            if not DatabaseConnection.test_connection():
                self.logger.error("❌ No se pudo conectar a MySQL")
                return False
            
            # Crear tablas si no existen
            DatabaseMigrations.create_all_tables()
            
            # Verificar esquema
            schema_status = DatabaseMigrations.verify_schema()
            if not all(schema_status.values()):
                self.logger.error(f"❌ Esquema de base de datos incompleto: {schema_status}")
                return False
            
            self.logger.info("✅ Base de datos inicializada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando base de datos: {str(e)}")
            return False
    
    def _inicializar_componentes(self):
        """Inicializa los componentes principales del sistema"""
        # Inicializar procesador de logs
        self.procesador = ProcesadorLogs()
        
        # Inicializar caché temporal (singleton)
        self.cache_manager = CacheTemporalManager()
        
        # Inicializar factory de reportes
        self.factory_reportes = FactoryReportes()
        
        self.logger.info("✅ Componentes principales inicializados")
    
    def _verificar_estado_sistema(self) -> bool:
        """Verifica que todos los componentes estén funcionando"""
        try:
            # Verificar procesador
            if not self.procesador:
                return False
            
            # Verificar caché
            stats_cache = self.cache_manager.obtener_estadisticas_cache()
            if 'total_logs_procesados' not in stats_cache:
                return False
            
            # Verificar factory de reportes
            tipos_disponibles = self.factory_reportes.tipos_disponibles()
            if not tipos_disponibles:
                return False
            
            self.logger.info(f"✅ Sistema verificado - {len(tipos_disponibles)} tipos de reportes disponibles")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando estado del sistema: {str(e)}")
            return False
    
    @benchmark
    def cargar_datos_desde_archivo(self, archivo_path: str, formato: str = None) -> int:
        """
        Carga datos desde un archivo externo.
        
        Args:
            archivo_path: Ruta del archivo a cargar
            formato: Formato del archivo ('csv', 'json', auto-detectar si None)
            
        Returns:
            Número de logs procesados exitosamente
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado. Ejecutar inicializar_sistema() primero.")
        
        archivo = Path(archivo_path)
        if not archivo.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {archivo_path}")
        
        # Auto-detectar formato si no se especifica
        if formato is None:
            formato = archivo.suffix.lower().lstrip('.')
        
        # Crear fuente de datos apropiada
        if formato == 'csv':
            fuente = FuenteCSV(str(archivo))
        elif formato == 'json':
            fuente = FuenteJSON(str(archivo))
        else:
            raise ValueError(f"Formato no soportado: {formato}")
        
        # Procesar datos
        logs_procesados = self.procesador.procesar_fuente(fuente)
        self.stats['logs_procesados_total'] += logs_procesados
        
        self.logger.info(f"✅ Cargados {logs_procesados} logs desde {archivo_path}")
        return logs_procesados
    
    def cargar_datos_desde_fuente(self, fuente) -> int:
        """
        Carga datos desde una fuente de datos personalizada.
        
        Args:
            fuente: Instancia que implementa el protocolo FuenteDatos
            
        Returns:
            Número de logs procesados
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        logs_procesados = self.procesador.procesar_fuente(fuente)
        self.stats['logs_procesados_total'] += logs_procesados
        return logs_procesados
    
    @benchmark
    def generar_reporte(self, 
                       tipo_reporte: TipoReporte, 
                       estrategia: str = None,
                       filtros: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Genera un reporte del tipo especificado.
        
        Args:
            tipo_reporte: Tipo de reporte a generar
            estrategia: Estrategia de análisis ('estadistico', 'tendencias', 'comparativo')
            filtros: Filtros opcionales (sala, tiempo, etc.)
            
        Returns:
            Diccionario con el reporte generado
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        # Obtener logs según filtros
        logs = self._obtener_logs_filtrados(filtros)
        
        if not logs:
            self.logger.warning("No se encontraron logs para generar el reporte")
            return {'error': 'No hay datos disponibles para el reporte'}
        
        # Crear reporte con estrategia específica
        if estrategia:
            reporte = self.factory_reportes.crear_reporte_con_estrategia_personalizada(
                tipo_reporte, estrategia
            )
        else:
            reporte = self.factory_reportes.crear_reporte(tipo_reporte)
        
        # Generar reporte
        resultado = reporte.generar_completo(logs)
        self.stats['reportes_generados'] += 1
        
        self.logger.info(f"✅ Reporte generado: {tipo_reporte.value}")
        return resultado
    
    def _obtener_logs_filtrados(self, filtros: Dict[str, Any] = None) -> List[Log]:
        """Obtiene logs aplicando filtros especificados"""
        if not filtros:
            # Sin filtros: obtener logs recientes del caché
            return self.cache_manager.obtener_logs_recientes()
        
        # Aplicar filtros específicos
        if 'sala' in filtros and 'minutos_atras' not in filtros:
            # Filtro solo por sala: usar caché
            return self.cache_manager.obtener_logs_por_sala(filtros['sala'])
        
        # Filtros complejos: consultar base de datos
        from database import LogRepository
        return LogRepository.get_logs_by_filters(filtros)
    
    def consultar_estado_sala(self, nombre_sala: str) -> Optional[Dict[str, Any]]:
        """
        Consulta el estado actual de una sala específica.
        
        Args:
            nombre_sala: Nombre de la sala a consultar
            
        Returns:
            Diccionario con el estado de la sala o None si no se encuentra
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        # Buscar en salas del procesador
        if nombre_sala in self.procesador.salas:
            sala = self.procesador.salas[nombre_sala]
            return sala.condiciones_actuales
        
        # Buscar en caché
        logs_sala = self.cache_manager.obtener_logs_por_sala(nombre_sala)
        if logs_sala:
            ultimo_log = max(logs_sala, key=lambda x: x.timestamp)
            return {
                'sala': nombre_sala,
                'timestamp': ultimo_log.timestamp.isoformat(),
                'temperatura': ultimo_log.temperatura,
                'humedad': ultimo_log.humedad,
                'co2': ultimo_log.co2,
                'estado': ultimo_log.estado.value,
                'is_critical': ultimo_log.is_critical,
                'condiciones_criticas': ultimo_log.condiciones_criticas
            }
        
        return None
    
    def obtener_alertas_activas(self, horas_atras: int = 2) -> List[Log]:
        """
        Obtiene todas las alertas críticas activas.
        
        Args:
            horas_atras: Considerar alertas de las últimas N horas
            
        Returns:
            Lista de logs críticos
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        # Obtener logs recientes del caché
        logs_recientes = self.cache_manager.obtener_logs_recientes(horas_atras * 60)
        
        # Filtrar solo los críticos
        return [log for log in logs_recientes if log.is_critical]
    
    def obtener_dashboard_ejecutivo(self) -> Dict[str, Any]:
        """
        Genera un dashboard ejecutivo con métricas clave.
        
        Returns:
            Diccionario con métricas del dashboard
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        # Obtener datos del sistema
        logs_recientes = self.cache_manager.obtener_logs_recientes()
        alertas_activas = self.obtener_alertas_activas()
        
        # Estadísticas del procesador
        stats_procesador = self.procesador.obtener_resumen_procesamiento()
        
        # Estadísticas del caché
        stats_cache = self.cache_manager.obtener_estadisticas_cache()
        
        # Métricas por sala
        metricas_salas = {}
        for nombre_sala, sala in self.procesador.salas.items():
            condiciones = sala.condiciones_actuales
            if condiciones:
                metricas_salas[nombre_sala] = {
                    **condiciones,
                    'nivel_criticidad': 'CRÍTICA' if condiciones.get('is_critical') else 'NORMAL'
                }
        
        return {
            'timestamp_dashboard': datetime.now().isoformat(),
            'estado_general': self._calcular_estado_general(alertas_activas, len(self.procesador.salas)),
            'metricas_principales': {
                'salas_monitoreadas': len(self.procesador.salas),
                'alertas_activas': len(alertas_activas),
                'logs_ultimos_5_min': len(logs_recientes),
                'uptime_sistema': self._calcular_uptime(),
                'logs_procesados_total': self.stats['logs_procesados_total']
            },
            'rendimiento_sistema': {
                'procesador': stats_procesador,
                'cache': stats_cache,
                'estadisticas_generales': self.stats
            },
            'salas_detalle': metricas_salas,
            'alertas_resumen': self._generar_resumen_alertas(alertas_activas),
            'recomendaciones_inmediatas': self._generar_recomendaciones_dashboard(alertas_activas)
        }
    
    def _calcular_estado_general(self, alertas_activas: List[Log], total_salas: int) -> str:
        """Calcula el estado general del sistema"""
        if not total_salas:
            return "🔶 Sin datos"
        
        salas_con_alertas = len(set(log.sala for log in alertas_activas))
        porcentaje_afectado = salas_con_alertas / total_salas
        
        if porcentaje_afectado >= 0.5:
            return "🔴 Crítico"
        elif porcentaje_afectado >= 0.2:
            return "🟡 Atención requerida"
        elif len(alertas_activas) > 0:
            return "🟢 Alertas menores"
        else:
            return "✅ Óptimo"
    
    def _calcular_uptime(self) -> str:
        """Calcula el uptime del sistema"""
        uptime = datetime.now() - self.stats['inicio_sistema']
        
        if uptime.days > 0:
            return f"{uptime.days} días, {uptime.seconds // 3600} horas"
        else:
            horas = uptime.seconds // 3600
            minutos = (uptime.seconds % 3600) // 60
            return f"{horas}h {minutos}m"
    
    def _generar_resumen_alertas(self, alertas_activas: List[Log]) -> Dict[str, Any]:
        """Genera resumen de alertas activas"""
        if not alertas_activas:
            return {'total': 0, 'mensaje': 'No hay alertas activas'}
        
        # Agrupar por tipo de alerta
        tipos_alertas = {}
        for alerta in alertas_activas:
            for condicion in alerta.condiciones_criticas:
                tipos_alertas[condicion] = tipos_alertas.get(condicion, 0) + 1
        
        return {
            'total': len(alertas_activas),
            'por_tipo': tipos_alertas,
            'salas_afectadas': len(set(alerta.sala for alerta in alertas_activas)),
            'mas_reciente': max(alertas_activas, key=lambda x: x.timestamp).timestamp.isoformat()
        }
    
    def _generar_recomendaciones_dashboard(self, alertas_activas: List[Log]) -> List[str]:
        """Genera recomendaciones inmediatas para el dashboard"""
        recomendaciones = []
        
        if not alertas_activas:
            recomendaciones.append("✅ Sistema funcionando normalmente")
            return recomendaciones
        
        # Recomendaciones basadas en alertas
        salas_criticas = set(alerta.sala for alerta in alertas_activas)
        
        if len(salas_criticas) > 3:
            recomendaciones.append(f"🚨 Revisar {len(salas_criticas)} salas con alertas críticas")
        
        # Recomendaciones por tipo de alerta
        temp_alta = any('temperatura alta' in str(alerta.condiciones_criticas) 
                       for alerta in alertas_activas)
        co2_alto = any('CO2 elevado' in str(alerta.condiciones_criticas) 
                      for alerta in alertas_activas)
        
        if temp_alta:
            recomendaciones.append("❄️ Verificar sistema de climatización")
        if co2_alto:
            recomendaciones.append("🌪️ Mejorar ventilación en salas afectadas")
        
        return recomendaciones[:5]  # Máximo 5 recomendaciones
    
    @benchmark
    def exportar_reportes_completos(self, directorio_salida: str = None) -> List[str]:
        """
        Exporta todos los tipos de reportes disponibles.
        
        Args:
            directorio_salida: Directorio donde guardar los reportes
            
        Returns:
            Lista de archivos generados
        """
        if not self.is_initialized:
            raise RuntimeError("Sistema no inicializado")
        
        if directorio_salida is None:
            directorio_salida = settings.REPORTS_OUTPUT_DIR
        
        directorio = Path(directorio_salida)
        directorio.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivos_generados = []
        
        # Generar todos los tipos de reportes
        for tipo_reporte in TipoReporte:
            try:
                # Generar reporte con análisis estadístico
                reporte_data = self.generar_reporte(tipo_reporte)
                
                if 'error' not in reporte_data:
                    # Guardar como JSON
                    archivo_json = directorio / f"{tipo_reporte.value}_{timestamp}.json"
                    with open(archivo_json, 'w', encoding='utf-8') as f:
                        import json
                        json.dump(reporte_data, f, indent=2, ensure_ascii=False, default=str)
                    
                    archivos_generados.append(str(archivo_json))
                    self.logger.info(f"✅ Reporte generado: {archivo_json}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error generando reporte {tipo_reporte.value}: {str(e)}")
        
        # Generar dashboard ejecutivo
        try:
            dashboard = self.obtener_dashboard_ejecutivo()
            archivo_dashboard = directorio / f"dashboard_ejecutivo_{timestamp}.json"
            
            with open(archivo_dashboard, 'w', encoding='utf-8') as f:
                import json
                json.dump(dashboard, f, indent=2, ensure_ascii=False, default=str)
            
            archivos_generados.append(str(archivo_dashboard))
            
        except Exception as e:
            self.logger.error(f"❌ Error generando dashboard: {str(e)}")
        
        self.logger.info(f"📊 Total de reportes generados: {len(archivos_generados)}")
        return archivos_generados
    
    def obtener_estadisticas_sistema(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema"""
        if not self.is_initialized:
            return {'error': 'Sistema no inicializado'}
        
        return {
            'sistema': {
                'inicializado': self.is_initialized,
                'uptime': self._calcular_uptime(),
                'inicio': self.stats['inicio_sistema'].isoformat()
            },
            'procesamiento': self.procesador.obtener_resumen_procesamiento() if self.procesador else {},
            'cache': self.cache_manager.obtener_estadisticas_cache() if self.cache_manager else {},
            'reportes': {
                'tipos_disponibles': self.factory_reportes.tipos_disponibles() if self.factory_reportes else [],
                'generados_total': self.stats['reportes_generados']
            },
            'base_datos': {
                'conectado': DatabaseConnection.test_connection(),
                'esquema_completo': all(DatabaseMigrations.verify_schema().values())
            }
        }
    
    def _signal_handler(self, signum, frame):
        """Manejador de señales para cierre graceful"""
        self.logger.info(f"📡 Señal {signum} recibida, cerrando sistema...")
        self.cerrar_sistema()
        sys.exit(0)
    
    def cerrar_sistema(self):
        """Cierra el sistema de manera ordenada"""
        if self.is_initialized:
            self.logger.info("🔄 Cerrando sistema EcoWatch...")
            
            # Limpiar caché
            if self.cache_manager:
                self.cache_manager.limpiar_cache_completo()
            
            # Estadísticas finales
            uptime = datetime.now() - self.stats['inicio_sistema']
            self.logger.info(f"📊 Estadísticas finales:")
            self.logger.info(f"   • Uptime: {uptime}")
            self.logger.info(f"   • Logs procesados: {self.stats['logs_procesados_total']}")
            self.logger.info(f"   • Reportes generados: {self.stats['reportes_generados']}")
            
            self.is_initialized = False
            self.logger.info("✅ Sistema EcoWatch cerrado correctamente")

# ============================================================================
# FUNCIONES DE LÍNEA DE COMANDOS
# ============================================================================

def ejecutar_demo():
    """Ejecuta una demostración completa del sistema"""
    print("🌍 === DEMO SISTEMA ECOWATCH ===")
    print("Iniciando demostración del sistema de monitoreo ambiental...\n")
    
    # Inicializar sistema
    sistema = SistemaEcoWatch()
    
    if not sistema.inicializar_sistema():
        print("❌ Error inicializando sistema")
        return False
    
    try:
        # Generar datos simulados
        print("🎭 Generando datos simulados...")
        fuente_simulada = FuenteSimulada(cantidad_logs=100, salas=['Sala_1', 'Sala_2', 'Sala_3'])
        logs_cargados = sistema.cargar_datos_desde_fuente(fuente_simulada)
        print(f"✅ {logs_cargados} logs simulados cargados\n")
        
        # Mostrar dashboard ejecutivo
        print("📊 === DASHBOARD EJECUTIVO ===")
        dashboard = sistema.obtener_dashboard_ejecutivo()
        
        print(f"🏢 Salas monitoreadas: {dashboard['metricas_principales']['salas_monitoreadas']}")
        print(f"🚨 Alertas activas: {dashboard['metricas_principales']['alertas_activas']}")
        print(f"📈 Logs procesados: {dashboard['metricas_principales']['logs_procesados_total']}")
        print(f"⏱️ Uptime: {dashboard['metricas_principales']['uptime_sistema']}")
        print(f"📊 Estado general: {dashboard['estado_general']}\n")
        
        # Generar reportes de ejemplo
        print("📋 === GENERANDO REPORTES ===")
        
        reportes_demo = [
            (TipoReporte.ESTADO_POR_SALA, "Estado por Sala"),
            (TipoReporte.ALERTAS_CRITICAS, "Alertas Críticas"),
            (TipoReporte.TENDENCIAS_AMBIENTALES, "Tendencias Ambientales")
        ]
        
        for tipo, nombre in reportes_demo:
            try:
                reporte = sistema.generar_reporte(tipo)
                if 'error' not in reporte:
                    print(f"✅ {nombre}: Generado exitosamente")
                else:
                    print(f"⚠️ {nombre}: {reporte['error']}")
            except Exception as e:
                print(f"❌ {nombre}: Error - {str(e)}")
        
        print()
        
        # Consultas específicas
        print("🔍 === CONSULTAS ESPECÍFICAS ===")
        alertas_activas = sistema.obtener_alertas_activas()
        print(f"🚨 Alertas críticas encontradas: {len(alertas_activas)}")
        
        for i, alerta in enumerate(alertas_activas[:3], 1):
            print(f"   {i}. {alerta.sala}: {', '.join(alerta.condiciones_criticas)}")
        
        # Estadísticas del sistema
        print(f"\n💻 === ESTADÍSTICAS DEL SISTEMA ===")
        stats = sistema.obtener_estadisticas_sistema()
        print(f"📊 Base de datos conectada: {stats['base_datos']['conectado']}")
        print(f"💾 Logs en caché: {stats['cache']['logs_en_cache']}")
        print(f"📈 Eficiencia procesamiento: {stats['procesamiento']['estadisticas_procesamiento']['tasa_exito']:.1f}%")
        
        # Exportar reportes
        print(f"\n📁 === EXPORTANDO REPORTES ===")
        reportes_generados = sistema.exportar_reportes_completos()
        print(f"✅ {len(reportes_generados)} reportes exportados a {settings.REPORTS_OUTPUT_DIR}")
        
        print("\n🎉 === DEMO COMPLETADA ===")
        print("✨ El sistema EcoWatch ha demostrado todas sus capacidades!")
        print(f"🔗 Archivos generados en: {settings.REPORTS_OUTPUT_DIR}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la demostración: {str(e)}")
        return False
    finally:
        sistema.cerrar_sistema()

def cargar_desde_csv(archivo_csv: str):
    """Carga datos desde un archivo CSV específico"""
    print(f"📁 Cargando datos desde {archivo_csv}...")
    
    sistema = SistemaEcoWatch()
    
    if not sistema.inicializar_sistema():
        print("❌ Error inicializando sistema")
        return False
    
    try:
        logs_cargados = sistema.cargar_datos_desde_archivo(archivo_csv, 'csv')
        print(f"✅ {logs_cargados} logs cargados exitosamente")
        
        # Mostrar resumen
        dashboard = sistema.obtener_dashboard_ejecutivo()
        print(f"📊 Resumen: {dashboard['metricas_principales']['salas_monitoreadas']} salas, "
              f"{dashboard['metricas_principales']['alertas_activas']} alertas activas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando archivo: {str(e)}")
        return False
    finally:
        sistema.cerrar_sistema()

def ejecutar_api():
    """Ejecuta solo el servidor API REST"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        import uvicorn
        
        app = FastAPI(
            title="EcoWatch API",
            description="API REST para el Sistema de Monitoreo Ambiental EcoWatch",
            version="1.0.0"
        )
        
        # Inicializar sistema
        sistema = SistemaEcoWatch()
        
        @app.on_event("startup")
        async def startup_event():
            if not sistema.inicializar_sistema():
                raise RuntimeError("No se pudo inicializar el sistema EcoWatch")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            sistema.cerrar_sistema()
        
        # Endpoints de la API
        @app.get("/")
        async def root():
            return {"message": "EcoWatch API - Sistema de Monitoreo Ambiental", "version": "1.0.0"}
        
        @app.get("/dashboard")
        async def get_dashboard():
            try:
                return sistema.obtener_dashboard_ejecutivo()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/salas/{sala_id}")
        async def get_sala_estado(sala_id: str):
            estado = sistema.consultar_estado_sala(sala_id)
            if estado is None:
                raise HTTPException(status_code=404, detail=f"Sala {sala_id} no encontrada")
            return estado
        
        @app.get("/alertas")
        async def get_alertas_activas():
            try:
                alertas = sistema.obtener_alertas_activas()
                return {
                    "total_alertas": len(alertas),
                    "alertas": [alerta.to_dict() for alerta in alertas]
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/reportes/{tipo_reporte}")
        async def generar_reporte_api(tipo_reporte: str, estrategia: str = None):
            try:
                # Convertir string a enum
                tipo_enum = TipoReporte(tipo_reporte)
                return sistema.generar_reporte(tipo_enum, estrategia)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Tipo de reporte inválido: {tipo_reporte}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/stats")
        async def get_estadisticas():
            return sistema.obtener_estadisticas_sistema()
        
        print("🚀 Iniciando servidor API EcoWatch...")
        print(f"📡 API disponible en: http://localhost:8000")
        print(f"📚 Documentación en: http://localhost:8000/docs")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError:
        print("❌ FastAPI no está instalado. Instalar con: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Error ejecutando API: {str(e)}")

def main():
    """Función principal del sistema"""
    parser = argparse.ArgumentParser(description="Sistema EcoWatch - Monitoreo Ambiental")
    parser.add_argument('--demo', action='store_true', help='Ejecutar demostración del sistema')
    parser.add_argument('--load-csv', type=str, help='Cargar datos desde archivo CSV')
    parser.add_argument('--api-only', action='store_true', help='Ejecutar solo servidor API')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Ejecutar modo seleccionado
    if args.demo:
        return ejecutar_demo()
    elif args.load_csv:
        return cargar_desde_csv(args.load_csv)
    elif args.api_only:
        return ejecutar_api()
    else:
        # Modo interactivo por defecto
        print("🌍 Sistema EcoWatch - Monitoreo Ambiental")
        print("Opciones disponibles:")
        print("  --demo          : Ejecutar demostración completa")
        print("  --load-csv FILE : Cargar datos desde CSV")
        print("  --api-only      : Ejecutar servidor API REST")
        print("  --help          : Mostrar ayuda completa")
        print("\nEjemplo: python main.py --demo")

if __name__ == "__main__":
    main()