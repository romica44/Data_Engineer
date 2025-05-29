"""
Log Processor - Procesador principal de logs ambientales
Maneja la lógica de negocio para procesar y analizar logs
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from models import Log, EstadoLog, validar_lote_logs
from .cache_manager import CacheTemporalManager
from utils.decorators import benchmark, log_operation

class ProcesadorLogs:
    """
    Procesador principal de logs ambientales
    Coordina el procesamiento, validación y análisis de logs
    """
    
    def __init__(self, cache_manager: CacheTemporalManager = None, 
                 repositorio=None, umbrales: Dict[str, Any] = None):
        """
        Inicializa el procesador de logs
        
        Args:
            cache_manager: Manager del caché temporal
            repositorio: Repositorio de datos (base de datos)
            umbrales: Umbrales ambientales para evaluación
        """
        self.logger = logging.getLogger(__name__)
        self.cache_manager = cache_manager or CacheTemporalManager()
        self.repositorio = repositorio
        
        # Umbrales por defecto si no se proporcionan
        self.umbrales = umbrales or {
            'temperatura': {'min': 18.0, 'max': 30.0, 'critical_low': 15.0, 'critical_high': 35.0},
            'humedad': {'min': 20.0, 'max': 80.0, 'critical_low': 10.0, 'critical_high': 90.0},
            'co2': {'max': 1000, 'critical': 1500, 'danger': 2000}
        }
        
        # Estadísticas del procesador
        self._stats = {
            'logs_procesados': 0,
            'logs_validados': 0,
            'logs_invalidos': 0,
            'alertas_generadas': 0,
            'ultimo_procesamiento': None
        }
        
        self.logger.info("ProcesadorLogs inicializado")
    
    @benchmark
    @log_operation
    def procesar_log_individual(self, log: Log) -> Tuple[bool, Dict[str, Any]]:
        """
        Procesa un log individual
        
        Args:
            log: Log a procesar
            
        Returns:
            Tupla con (éxito, información_procesamiento)
        """
        try:
            # 1. Validar log
            resultado_validacion = self._validar_log(log)
            if not resultado_validacion['valido']:
                self._stats['logs_invalidos'] += 1
                return False, resultado_validacion
            
            # 2. Evaluar condiciones ambientales
            evaluacion = self._evaluar_condiciones_ambientales(log)
            
            # 3. Determinar estado automáticamente si no está definido
            if not hasattr(log, 'estado') or log.estado is None:
                log.estado = self._determinar_estado_automatico(log, evaluacion)
            
            # 4. Marcar como crítico si es necesario
            if evaluacion['es_critico']:
                log.is_critical = True
                self._stats['alertas_generadas'] += 1
            
            # 5. Agregar timestamp de procesamiento
            log.processed_at = datetime.now()
            
            # 6. Agregar al caché
            self.cache_manager.agregar_log(log)
            
            # 7. Guardar en repositorio si está disponible
            if self.repositorio:
                # self.repositorio.guardar_log(log)
                pass
            
            # 8. Actualizar estadísticas
            self._stats['logs_procesados'] += 1
            self._stats['logs_validados'] += 1
            self._stats['ultimo_procesamiento'] = datetime.now()
            
            resultado = {
                'valido': True,
                'estado_asignado': log.estado.value,
                'es_critico': log.is_critical,
                'evaluacion_ambiental': evaluacion,
                'timestamp_procesamiento': log.processed_at.isoformat()
            }
            
            self.logger.debug(f"Log procesado: {log.sala} - {log.estado.value}")
            return True, resultado
            
        except Exception as e:
            self.logger.error(f"Error al procesar log: {e}")
            self._stats['logs_invalidos'] += 1
            return False, {'valido': False, 'error': str(e)}
    
    @benchmark
    def procesar_lote(self, logs: List[Log]) -> Dict[str, Any]:
        """
        Procesa un lote de logs
        
        Args:
            logs: Lista de logs a procesar
            
        Returns:
            Resultado del procesamiento del lote
        """
        try:
            self.logger.info(f"Iniciando procesamiento de lote: {len(logs)} logs")
            
            # 1. Validación inicial del lote
            logs_validos, logs_invalidos, errores = validar_lote_logs(logs)
            
            # 2. Procesar logs válidos
            resultados_procesamiento = []
            logs_procesados_exitosamente = []
            
            for log in logs_validos:
                exito, resultado = self.procesar_log_individual(log)
                resultados_procesamiento.append({
                    'log': log,
                    'exito': exito,
                    'resultado': resultado
                })
                
                if exito:
                    logs_procesados_exitosamente.append(log)
            
            # 3. Análisis del lote
            analisis_lote = self._analizar_lote(logs_procesados_exitosamente)
            
            # 4. Detectar patrones y anomalías
            patrones = self._detectar_patrones(logs_procesados_exitosamente)
            
            # 5. Generar resumen
            resumen = {
                'total_logs': len(logs),
                'logs_validos': len(logs_validos),
                'logs_invalidos': len(logs_invalidos),
                'logs_procesados_exitosamente': len(logs_procesados_exitosamente),
                'logs_criticos': len([l for l in logs_procesados_exitosamente if l.is_critical]),
                'salas_afectadas': len(set(l.sala for l in logs_procesados_exitosamente)),
                'periodo_datos': self._calcular_periodo_datos(logs_procesados_exitosamente),
                'analisis_lote': analisis_lote,
                'patrones_detectados': patrones,
                'errores_validacion': errores,
                'timestamp_procesamiento': datetime.now().isoformat()
            }
            
            self.logger.info(f"Lote procesado: {resumen['logs_procesados_exitosamente']}/{resumen['total_logs']} logs")
            return resumen
            
        except Exception as e:
            self.logger.error(f"Error al procesar lote: {e}")
            return {'error': str(e), 'logs_procesados': 0}
    
    def _validar_log(self, log: Log) -> Dict[str, Any]:
        """Valida un log individual"""
        try:
            # Validaciones básicas
            if not isinstance(log, Log):
                return {'valido': False, 'error': 'No es una instancia de Log'}
            
            if not log.timestamp:
                return {'valido': False, 'error': 'Timestamp requerido'}
            
            if not log.sala or not log.sala.strip():
                return {'valido': False, 'error': 'Sala requerida'}
            
            # Validaciones de rangos
            if not isinstance(log.temperatura, (int, float)):
                return {'valido': False, 'error': 'Temperatura debe ser numérica'}
            
            if not isinstance(log.humedad, (int, float)):
                return {'valido': False, 'error': 'Humedad debe ser numérica'}
            
            if not isinstance(log.co2, int):
                return {'valido': False, 'error': 'CO2 debe ser entero'}
            
            # Validaciones de rangos razonables
            if not -50 <= log.temperatura <= 80:
                return {'valido': False, 'error': f'Temperatura fuera de rango: {log.temperatura}°C'}
            
            if not 0 <= log.humedad <= 100:
                return {'valido': False, 'error': f'Humedad fuera de rango: {log.humedad}%'}
            
            if not 0 <= log.co2 <= 10000:
                return {'valido': False, 'error': f'CO2 fuera de rango: {log.co2} ppm'}
            
            return {'valido': True, 'mensaje': 'Log válido'}
            
        except Exception as e:
            return {'valido': False, 'error': f'Error en validación: {str(e)}'}
    
    def _evaluar_condiciones_ambientales(self, log: Log) -> Dict[str, Any]:
        """Evalúa las condiciones ambientales del log"""
        try:
            # Evaluar temperatura
            temp_eval = self._evaluar_temperatura(log.temperatura)
            
            # Evaluar humedad
            humedad_eval = self._evaluar_humedad(log.humedad)
            
            # Evaluar CO2
            co2_eval = self._evaluar_co2(log.co2)
            
            # Evaluación general
            es_critico = (temp_eval['nivel'] == 'critico' or 
                         humedad_eval['nivel'] == 'critico' or 
                         co2_eval['nivel'] == 'critico')
            
            es_warning = (temp_eval['nivel'] == 'warning' or 
                         humedad_eval['nivel'] == 'warning' or 
                         co2_eval['nivel'] == 'warning')
            
            # Calcular score de confort (0-100)
            score_confort = self._calcular_score_confort(log)
            
            return {
                'temperatura': temp_eval,
                'humedad': humedad_eval,
                'co2': co2_eval,
                'es_critico': es_critico,
                'es_warning': es_warning,
                'score_confort': score_confort,
                'evaluacion_general': 'critico' if es_critico else 'warning' if es_warning else 'normal'
            }
            
        except Exception as e:
            self.logger.error(f"Error en evaluación ambiental: {e}")
            return {'error': str(e)}
    
    def _evaluar_temperatura(self, temperatura: float) -> Dict[str, Any]:
        """Evalúa la temperatura según umbrales"""
        temp_config = self.umbrales['temperatura']
        
        if temperatura < temp_config['critical_low'] or temperatura > temp_config['critical_high']:
            nivel = 'critico'
            mensaje = f"Temperatura crítica: {temperatura}°C"
        elif temperatura < temp_config['min'] or temperatura > temp_config['max']:
            nivel = 'warning'
            mensaje = f"Temperatura fuera de rango óptimo: {temperatura}°C"
        else:
            nivel = 'normal'
            mensaje = f"Temperatura normal: {temperatura}°C"
        
        return {
            'valor': temperatura,
            'nivel': nivel,
            'mensaje': mensaje,
            'dentro_rango_optimo': temp_config['min'] <= temperatura <= temp_config['max']
        }
    
    def _evaluar_humedad(self, humedad: float) -> Dict[str, Any]:
        """Evalúa la humedad según umbrales"""
        humedad_config = self.umbrales['humedad']
        
        if humedad < humedad_config['critical_low'] or humedad > humedad_config['critical_high']:
            nivel = 'critico'
            mensaje = f"Humedad crítica: {humedad}%"
        elif humedad < humedad_config['min'] or humedad > humedad_config['max']:
            nivel = 'warning'
            mensaje = f"Humedad fuera de rango óptimo: {humedad}%"
        else:
            nivel = 'normal'
            mensaje = f"Humedad normal: {humedad}%"
        
        return {
            'valor': humedad,
            'nivel': nivel,
            'mensaje': mensaje,
            'dentro_rango_optimo': humedad_config['min'] <= humedad <= humedad_config['max']
        }
    
    def _evaluar_co2(self, co2: int) -> Dict[str, Any]:
        """Evalúa el CO2 según umbrales"""
        co2_config = self.umbrales['co2']
        
        if co2 > co2_config['danger']:
            nivel = 'critico'
            mensaje = f"CO2 peligroso: {co2} ppm"
        elif co2 > co2_config['critical']:
            nivel = 'warning'
            mensaje = f"CO2 elevado: {co2} ppm"
        elif co2 > co2_config['max']:
            nivel = 'warning'
            mensaje = f"CO2 por encima del límite: {co2} ppm"
        else:
            nivel = 'normal'
            mensaje = f"CO2 normal: {co2} ppm"
        
        return {
            'valor': co2,
            'nivel': nivel,
            'mensaje': mensaje,
            'dentro_rango_optimo': co2 <= co2_config['max']
        }
    
    def _calcular_score_confort(self, log: Log) -> int:
        """Calcula un score de confort de 0-100"""
        score = 0
        
        # Temperatura (40 puntos max)
        temp_config = self.umbrales['temperatura']
        if temp_config['min'] <= log.temperatura <= temp_config['max']:
            score += 40
        elif temp_config['min'] - 2 <= log.temperatura <= temp_config['max'] + 2:
            score += 20
        
        # Humedad (30 puntos max)
        humedad_config = self.umbrales['humedad']
        if humedad_config['min'] <= log.humedad <= humedad_config['max']:
            score += 30
        elif humedad_config['min'] - 10 <= log.humedad <= humedad_config['max'] + 10:
            score += 15
        
        # CO2 (30 puntos max)
        co2_config = self.umbrales['co2']
        if log.co2 <= co2_config['max']:
            score += 30
        elif log.co2 <= co2_config['critical']:
            score += 15
        
        return min(score, 100)
    
    def _determinar_estado_automatico(self, log: Log, evaluacion: Dict[str, Any]) -> EstadoLog:
        """Determina el estado automáticamente basado en la evaluación"""
        if evaluacion.get('es_critico', False):
            return EstadoLog.ERROR
        elif evaluacion.get('es_warning', False):
            return EstadoLog.WARNING
        else:
            return EstadoLog.INFO
    
    def _analizar_lote(self, logs: List[Log]) -> Dict[str, Any]:
        """Analiza un lote de logs para obtener estadísticas"""
        if not logs:
            return {}
        
        try:
            # Estadísticas por sala
            stats_por_sala = defaultdict(list)
            for log in logs:
                stats_por_sala[log.sala].append(log)
            
            # Distribución de estados
            distribucion_estados = Counter(log.estado.value for log in logs)
            
            # Promedios globales
            temperaturas = [log.temperatura for log in logs]
            humedades = [log.humedad for log in logs]
            co2_values = [log.co2 for log in logs]
            
            return {
                'total_salas': len(stats_por_sala),
                'distribucion_estados': dict(distribucion_estados),
                'promedios': {
                    'temperatura': round(statistics.mean(temperaturas), 2),
                    'humedad': round(statistics.mean(humedades), 2),
                    'co2': round(statistics.mean(co2_values), 2)
                },
                'rangos': {
                    'temperatura': {'min': min(temperaturas), 'max': max(temperaturas)},
                    'humedad': {'min': min(humedades), 'max': max(humedades)},
                    'co2': {'min': min(co2_values), 'max': max(co2_values)}
                },
                'estadisticas_por_sala': {
                    sala: {
                        'cantidad_logs': len(logs_sala),
                        'temp_promedio': round(statistics.mean([l.temperatura for l in logs_sala]), 2),
                        'humedad_promedio': round(statistics.mean([l.humedad for l in logs_sala]), 2),
                        'co2_promedio': round(statistics.mean([l.co2 for l in logs_sala]), 2)
                    }
                    for sala, logs_sala in stats_por_sala.items()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error en análisis de lote: {e}")
            return {'error': str(e)}
    
    def _detectar_patrones(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta patrones en los logs"""
        if not logs:
            return {}
        
        try:
            # Ordenar logs por timestamp
            logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
            
            # Detectar tendencias
            tendencias = self._analizar_tendencias(logs_ordenados)
            
            # Detectar anomalías
            anomalias = self._detectar_anomalias(logs_ordenados)
            
            # Detectar salas problemáticas
            salas_problematicas = self._detectar_salas_problematicas(logs)
            
            return {
                'tendencias': tendencias,
                'anomalias': anomalias,
                'salas_problematicas': salas_problematicas,
                'periodo_analizado': {
                    'inicio': logs_ordenados[0].timestamp.isoformat(),
                    'fin': logs_ordenados[-1].timestamp.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error al detectar patrones: {e}")
            return {'error': str(e)}
    
    def _analizar_tendencias(self, logs_ordenados: List[Log]) -> Dict[str, str]:
        """Analiza tendencias en los datos"""
        if len(logs_ordenados) < 3:
            return {}
        
        # Simplificado: comparar primera mitad vs segunda mitad
        mitad = len(logs_ordenados) // 2
        primera_mitad = logs_ordenados[:mitad]
        segunda_mitad = logs_ordenados[mitad:]
        
        # Promedios
        temp_inicio = statistics.mean([l.temperatura for l in primera_mitad])
        temp_fin = statistics.mean([l.temperatura for l in segunda_mitad])
        
        humedad_inicio = statistics.mean([l.humedad for l in primera_mitad])
        humedad_fin = statistics.mean([l.humedad for l in segunda_mitad])
        
        co2_inicio = statistics.mean([l.co2 for l in primera_mitad])
        co2_fin = statistics.mean([l.co2 for l in segunda_mitad])
        
        return {
            'temperatura': 'subiendo' if temp_fin > temp_inicio else 'bajando' if temp_fin < temp_inicio else 'estable',
            'humedad': 'subiendo' if humedad_fin > humedad_inicio else 'bajando' if humedad_fin < humedad_inicio else 'estable',
            'co2': 'subiendo' if co2_fin > co2_inicio else 'bajando' if co2_fin < co2_inicio else 'estable'
        }
    
    def _detectar_anomalias(self, logs: List[Log]) -> List[Dict[str, Any]]:
        """Detecta anomalías en los logs"""
        anomalias = []
        
        # Detectar valores extremos
        temperaturas = [l.temperatura for l in logs]
        humedades = [l.humedad for l in logs]
        co2_values = [l.co2 for l in logs]
        
        # Usar desviación estándar para detectar outliers
        if len(temperaturas) > 1:
            temp_mean = statistics.mean(temperaturas)
            temp_stdev = statistics.stdev(temperaturas)
            
            for log in logs:
                if abs(log.temperatura - temp_mean) > 2 * temp_stdev:
                    anomalias.append({
                        'tipo': 'temperatura_anomala',
                        'sala': log.sala,
                        'valor': log.temperatura,
                        'timestamp': log.timestamp.isoformat(),
                        'mensaje': f'Temperatura anómala: {log.temperatura}°C'
                    })
        
        return anomalias
    
    def _detectar_salas_problematicas(self, logs: List[Log]) -> List[Dict[str, Any]]:
        """Detecta salas con problemas recurrentes"""
        # Agrupar por sala
        logs_por_sala = defaultdict(list)
        for log in logs:
            logs_por_sala[log.sala].append(log)
        
        salas_problematicas = []
        
        for sala, logs_sala in logs_por_sala.items():
            # Calcular porcentaje de logs críticos
            logs_criticos = [l for l in logs_sala if l.is_critical]
            porcentaje_criticos = (len(logs_criticos) / len(logs_sala)) * 100
            
            if porcentaje_criticos > 50:  # Más del 50% son críticos
                salas_problematicas.append({
                    'sala': sala,
                    'total_logs': len(logs_sala),
                    'logs_criticos': len(logs_criticos),
                    'porcentaje_criticos': round(porcentaje_criticos, 2),
                    'problemas_principales': self._identificar_problemas_principales(logs_sala)
                })
        
        return salas_problematicas
    
    def _identificar_problemas_principales(self, logs_sala: List[Log]) -> List[str]:
        """Identifica los problemas principales de una sala"""
        problemas = []
        
        # Analizar temperatura
        temps_altas = len([l for l in logs_sala if l.temperatura > self.umbrales['temperatura']['max']])
        temps_bajas = len([l for l in logs_sala if l.temperatura < self.umbrales['temperatura']['min']])
        
        if temps_altas > len(logs_sala) * 0.3:
            problemas.append('temperatura_alta_frecuente')
        if temps_bajas > len(logs_sala) * 0.3:
            problemas.append('temperatura_baja_frecuente')
        
        # Analizar humedad
        humedad_alta = len([l for l in logs_sala if l.humedad > self.umbrales['humedad']['max']])
        humedad_baja = len([l for l in logs_sala if l.humedad < self.umbrales['humedad']['min']])
        
        if humedad_alta > len(logs_sala) * 0.3:
            problemas.append('humedad_alta_frecuente')
        if humedad_baja > len(logs_sala) * 0.3:
            problemas.append('humedad_baja_frecuente')
        
        # Analizar CO2
        co2_alto = len([l for l in logs_sala if l.co2 > self.umbrales['co2']['max']])
        
        if co2_alto > len(logs_sala) * 0.3:
            problemas.append('co2_elevado_frecuente')
        
        return problemas
    
    def _calcular_periodo_datos(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula el período de tiempo que cubren los datos"""
        if not logs:
            return {}
        
        timestamps = [log.timestamp for log in logs if log.timestamp]
        if not timestamps:
            return {}
        
        inicio = min(timestamps)
        fin = max(timestamps)
        duracion = fin - inicio
        
        return {
            'inicio': inicio.isoformat(),
            'fin': fin.isoformat(),
            'duracion_horas': round(duracion.total_seconds() / 3600, 2),
            'duracion_minutos': round(duracion.total_seconds() / 60, 2)
        }
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del procesador"""
        return {
            'logs_procesados': self._stats['logs_procesados'],
            'logs_validados': self._stats['logs_validados'],
            'logs_invalidos': self._stats['logs_invalidos'],
            'alertas_generadas': self._stats['alertas_generadas'],
            'ultimo_procesamiento': self._stats['ultimo_procesamiento'].isoformat() if self._stats['ultimo_procesamiento'] else None,
            'tasa_exito': (self._stats['logs_validados'] / max(self._stats['logs_procesados'], 1)) * 100,
            'umbrales_configurados': self.umbrales
        }
    
    def reset_estadisticas(self):
        """Resetea las estadísticas del procesador"""
        self._stats = {
            'logs_procesados': 0,
            'logs_validados': 0,
            'logs_invalidos': 0,
            'alertas_generadas': 0,
            'ultimo_procesamiento': None
        }
        self.logger.info("Estadísticas del procesador reseteadas")