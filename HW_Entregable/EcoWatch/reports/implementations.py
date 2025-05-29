"""
Implementaciones específicas de reportes del sistema EcoWatch
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import logging

from models import Log, EstadoLog
from config.settings import settings
from .base import ReporteBase
from .strategies import EstrategiaAnalisis

logger = logging.getLogger(__name__)

class ReporteEstadoPorSala(ReporteBase):
    """
    Reporte del estado actual y estadísticas por sala monitoreada.
    
    Proporciona una vista consolidada del estado operacional
    de cada sala con métricas clave y alertas activas.
    """
    
    def __init__(self, estrategia_analisis: EstrategiaAnalisis):
        super().__init__(estrategia_analisis, "Reporte Estado por Sala")
    
    def generar(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera reporte detallado del estado por sala"""
        # Agrupar logs por sala
        logs_por_sala = defaultdict(list)
        for log in logs:
            logs_por_sala[log.sala].append(log)
        
        estado_salas = {}
        resumen_general = {
            'total_salas': 0,
            'salas_criticas': 0,
            'salas_normales': 0,
            'total_logs_analizados': len(logs),
            'alertas_activas_sistema': 0
        }
        
        for sala, logs_sala in logs_por_sala.items():
            if not logs_sala:
                continue
            
            # Obtener el log más reciente
            ultimo_log = max(logs_sala, key=lambda x: x.timestamp)
            
            # Realizar análisis con la estrategia configurada
            analisis_sala = self.estrategia_analisis.analizar(logs_sala)
            
            # Calcular métricas específicas de la sala
            alertas_criticas = sum(1 for log in logs_sala if log.is_critical)
            
            # Evaluar tendencia reciente (últimos 10 logs)
            logs_recientes = sorted(logs_sala, key=lambda x: x.timestamp)[-10:]
            tendencia_temperatura = self._calcular_tendencia_temperatura(logs_recientes)
            
            # Determinar estado general de la sala
            estado_sala = self._determinar_estado_sala(ultimo_log, alertas_criticas, len(logs_sala))
            
            estado_salas[sala] = {
                'informacion_general': {
                    'nombre': sala,
                    'ultimo_estado': ultimo_log.estado.value,
                    'ultima_actualizacion': ultimo_log.timestamp.isoformat(),
                    'total_registros_periodo': len(logs_sala),
                    'estado_general': estado_sala
                },
                'condiciones_actuales': {
                    'temperatura': ultimo_log.temperatura,
                    'humedad': ultimo_log.humedad,
                    'co2': ultimo_log.co2,
                    'es_critica': ultimo_log.is_critical,
                    'condiciones_criticas': ultimo_log.condiciones_criticas
                },
                'metricas_periodo': {
                    'alertas_criticas': alertas_criticas,
                    'tasa_alertas': round(alertas_criticas / len(logs_sala) * 100, 1),
                    'tendencia_temperatura': tendencia_temperatura,
                    'tiempo_desde_ultima_alerta': self._tiempo_desde_ultima_alerta(logs_sala)
                },
                'analisis_detallado': analisis_sala,
                'recomendaciones': self._generar_recomendaciones_sala(ultimo_log, logs_sala)
            }
            
            # Actualizar resumen general
            resumen_general['total_salas'] += 1
            if estado_sala == 'Crítica':
                resumen_general['salas_criticas'] += 1
            else:
                resumen_general['salas_normales'] += 1
            
            resumen_general['alertas_activas_sistema'] += alertas_criticas
        
        return {
            'tipo_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'resumen_general': resumen_general,
            'estado_por_sala': estado_salas,
            'alertas_sistema': self._generar_alertas_sistema(estado_salas),
            'recomendaciones_generales': self._generar_recomendaciones_generales(estado_salas)
        }
    
    def _calcular_tendencia_temperatura(self, logs_recientes: List[Log]) -> str:
        """Calcula la tendencia de temperatura en los logs recientes"""
        if len(logs_recientes) < 3:
            return "Datos insuficientes"
        
        # Comparar primeros y últimos valores
        primera_mitad = logs_recientes[:len(logs_recientes)//2]
        segunda_mitad = logs_recientes[len(logs_recientes)//2:]
        
        temp_inicial = statistics.mean(log.temperatura for log in primera_mitad)
        temp_final = statistics.mean(log.temperatura for log in segunda_mitad)
        
        diferencia = temp_final - temp_inicial
        
        if diferencia > 0.5:
            return f"↗️ Subiendo (+{diferencia:.1f}°C)"
        elif diferencia < -0.5:
            return f"↘️ Bajando ({diferencia:.1f}°C)"
        else:
            return "→ Estable"
    
    def _determinar_estado_sala(self, ultimo_log: Log, alertas_criticas: int, total_logs: int) -> str:
        """Determina el estado general de una sala"""
        tasa_alertas = alertas_criticas / total_logs if total_logs > 0 else 0
        
        if ultimo_log.is_critical or tasa_alertas > 0.2:
            return "Crítica"
        elif tasa_alertas > 0.1:
            return "Atención requerida"
        elif tasa_alertas > 0.05:
            return "Vigilancia"
        else:
            return "Normal"
    
    def _tiempo_desde_ultima_alerta(self, logs_sala: List[Log]) -> str:
        """Calcula el tiempo transcurrido desde la última alerta crítica"""
        logs_criticos = [log for log in logs_sala if log.is_critical]
        
        if not logs_criticos:
            return "Sin alertas en el período"
        
        ultima_alerta = max(log.timestamp for log in logs_criticos)
        tiempo_transcurrido = datetime.now() - ultima_alerta
        
        if tiempo_transcurrido.days > 0:
            return f"{tiempo_transcurrido.days} días"
        elif tiempo_transcurrido.seconds > 3600:
            horas = tiempo_transcurrido.seconds // 3600
            return f"{horas} horas"
        else:
            minutos = tiempo_transcurrido.seconds // 60
            return f"{minutos} minutos"
    
    def _generar_recomendaciones_sala(self, ultimo_log: Log, logs_sala: List[Log]) -> List[str]:
        """Genera recomendaciones específicas para una sala"""
        recomendaciones = []
        
        # Recomendaciones basadas en condiciones actuales
        if ultimo_log.temperatura > settings.TEMP_MAX:
            recomendaciones.append("🌡️ Verificar sistema de climatización - temperatura elevada")
        elif ultimo_log.temperatura < settings.TEMP_MIN:
            recomendaciones.append("🔥 Revisar calefacción - temperatura baja")
        
        if ultimo_log.humedad > settings.HUMEDAD_MAX:
            recomendaciones.append("💧 Implementar deshumidificación")
        elif ultimo_log.humedad < settings.HUMEDAD_MIN:
            recomendaciones.append("💨 Aumentar humidificación")
        
        if ultimo_log.co2 > settings.CO2_MAX:
            recomendaciones.append("🌪️ Mejorar ventilación - CO2 elevado")
        
        # Recomendaciones basadas en patrones históricos
        alertas_criticas = sum(1 for log in logs_sala if log.is_critical)
        tasa_alertas = alertas_criticas / len(logs_sala) if logs_sala else 0
        
        if tasa_alertas > 0.3:
            recomendaciones.append("🔧 Realizar mantenimiento integral - alta frecuencia de alertas")
        elif tasa_alertas > 0.1:
            recomendaciones.append("👀 Incrementar frecuencia de monitoreo")
        
        # Recomendaciones por estado del sistema
        if ultimo_log.estado == EstadoLog.ERROR:
            recomendaciones.append("🛠️ Revisar sensores - errores del sistema detectados")
        
        return recomendaciones[:5]  # Máximo 5 recomendaciones
    
    def _generar_alertas_sistema(self, estado_salas: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera alertas a nivel de sistema"""
        alertas = []
        
        salas_criticas = [
            sala for sala, datos in estado_salas.items()
            if datos['informacion_general']['estado_general'] == 'Crítica'
        ]
        
        if len(salas_criticas) > len(estado_salas) * 0.5:
            alertas.append({
                'nivel': 'SISTEMA',
                'tipo': 'MULTIPLE_SALAS_CRITICAS',
                'mensaje': f"⚠️ {len(salas_criticas)} de {len(estado_salas)} salas en estado crítico",
                'salas_afectadas': salas_criticas
            })
        
        # Alertas por patrones específicos
        for sala, datos in estado_salas.items():
            condiciones = datos['condiciones_actuales']
            if condiciones['es_critica']:
                alertas.append({
                    'nivel': 'SALA',
                    'tipo': 'CONDICIONES_CRITICAS',
                    'mensaje': f"🚨 {sala}: {', '.join(condiciones['condiciones_criticas'])}",
                    'sala': sala
                })
        
        return alertas
    
    def _generar_recomendaciones_generales(self, estado_salas: Dict[str, Dict[str, Any]]) -> List[str]:
        """Genera recomendaciones a nivel de sistema"""
        recomendaciones = []
        
        # Análisis general del sistema
        total_salas = len(estado_salas)
        salas_criticas = sum(
            1 for datos in estado_salas.values()
            if datos['informacion_general']['estado_general'] == 'Crítica'
        )
        
        if salas_criticas > total_salas * 0.3:
            recomendaciones.append("🏢 Revisar infraestructura general - múltiples salas comprometidas")
        
        # Recomendaciones basadas en patrones comunes
        problemas_comunes = defaultdict(int)
        for datos in estado_salas.values():
            for condicion in datos['condiciones_actuales']['condiciones_criticas']:
                if 'temperatura' in condicion.lower():
                    problemas_comunes['temperatura'] += 1
                elif 'humedad' in condicion.lower():
                    problemas_comunes['humedad'] += 1
                elif 'co2' in condicion.lower():
                    problemas_comunes['ventilacion'] += 1
        
        for problema, frecuencia in problemas_comunes.items():
            if frecuencia > total_salas * 0.5:
                if problema == 'temperatura':
                    recomendaciones.append("🌡️ Revisar sistema de climatización central")
                elif problema == 'humedad':
                    recomendaciones.append("💧 Evaluar sistema de control de humedad")
                elif problema == 'ventilacion':
                    recomendaciones.append("🌪️ Optimizar sistema de ventilación general")
        
        return recomendaciones[:3]  # Máximo 3 recomendaciones generales
    
    def _preparar_datos_para_csv(self, datos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara datos para exportación CSV"""
        rows = []
        
        for sala, info in datos.get('estado_por_sala', {}).items():
            row = {
                'sala': sala,
                'estado_general': info['informacion_general']['estado_general'],
                'ultimo_estado': info['informacion_general']['ultimo_estado'],
                'temperatura_actual': info['condiciones_actuales']['temperatura'],
                'humedad_actual': info['condiciones_actuales']['humedad'],
                'co2_actual': info['condiciones_actuales']['co2'],
                'es_critica': info['condiciones_actuales']['es_critica'],
                'alertas_criticas': info['metricas_periodo']['alertas_criticas'],
                'tasa_alertas': info['metricas_periodo']['tasa_alertas'],
                'tendencia_temperatura': info['metricas_periodo']['tendencia_temperatura'],
                'ultima_actualizacion': info['informacion_general']['ultima_actualizacion']
            }
            rows.append(row)
        
        return rows

class ReporteAlertasCriticas(ReporteBase):
    """
    Reporte especializado en alertas críticas del sistema.
    
    Analiza en detalle las condiciones críticas, patrones de alertas
    y proporciona recomendaciones de acción inmediata.
    """
    
    def __init__(self, estrategia_analisis: EstrategiaAnalisis):
        super().__init__(estrategia_analisis, "Reporte Alertas Críticas")
    
    def generar(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera análisis detallado de alertas críticas"""
        logs_criticos = [log for log in logs if log.is_critical]
        
        # Si no hay alertas críticas, generar reporte básico
        if not logs_criticos:
            return self._generar_reporte_sin_alertas(len(logs))
        
        # Análisis detallado de alertas críticas
        analisis_alertas = self.estrategia_analisis.analizar(logs_criticos)
        
        # Clasificación y análisis de alertas
        clasificacion_alertas = self._clasificar_alertas(logs_criticos)
        analisis_temporal = self._analizar_patron_temporal(logs_criticos)
        impacto_por_sala = self._analizar_impacto_por_sala(logs_criticos)
        
        return {
            'tipo_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'resumen_alertas': {
                'total_alertas': len(logs_criticos),
                'total_logs_analizados': len(logs),
                'porcentaje_alertas': round(len(logs_criticos) / len(logs) * 100, 2),
                'salas_afectadas': len(set(log.sala for log in logs_criticos)),
                'nivel_severidad_sistema': self._calcular_severidad_sistema(logs_criticos, logs)
            },
            'clasificacion_alertas': clasificacion_alertas,
            'analisis_temporal': analisis_temporal,
            'impacto_por_sala': impacto_por_sala,
            'analisis_detallado': analisis_alertas,
            'alertas_activas': self._generar_alertas_activas(logs_criticos),
            'recomendaciones_criticas': self._generar_recomendaciones_criticas(logs_criticos),
            'plan_accion': self._generar_plan_accion(logs_criticos, clasificacion_alertas)
        }
    
    def _generar_reporte_sin_alertas(self, total_logs: int) -> Dict[str, Any]:
        """Genera reporte cuando no hay alertas críticas"""
        return {
            'tipo_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'resumen_alertas': {
                'total_alertas': 0,
                'total_logs_analizados': total_logs,
                'porcentaje_alertas': 0.0,
                'salas_afectadas': 0,
                'nivel_severidad_sistema': 'NORMAL'
            },
            'mensaje': '✅ No se detectaron alertas críticas en el período analizado',
            'recomendaciones': [
                '📊 Mantener monitoreo continuo',
                '🔄 Revisar configuración de umbrales si es necesario',
                '📈 Sistema operando dentro de parámetros normales'
            ]
        }
    
    def _clasificar_alertas(self, logs_criticos: List[Log]) -> Dict[str, Any]:
        """Clasifica las alertas críticas por tipo y severidad"""
        clasificacion = {
            'por_tipo': defaultdict(list),
            'por_severidad': defaultdict(int),
            'por_causa_raiz': defaultdict(int)
        }
        
        for log in logs_criticos:
            # Clasificar por tipo de condición crítica
            for condicion in log.condiciones_criticas:
                clasificacion['por_tipo'][condicion].append({
                    'timestamp': log.timestamp.isoformat(),
                    'sala': log.sala,
                    'valor': self._extraer_valor_condicion(condicion),
                    'mensaje': log.mensaje
                })
            
            # Clasificar por severidad
            severidad = self._determinar_severidad_alerta(log)
            clasificacion['por_severidad'][severidad] += 1
            
            # Clasificar por causa raíz probable
            causa = self._determinar_causa_raiz(log)
            clasificacion['por_causa_raiz'][causa] += 1
        
        # Convertir defaultdict a dict regular para serialización
        return {
            'por_tipo': dict(clasificacion['por_tipo']),
            'por_severidad': dict(clasificacion['por_severidad']),
            'por_causa_raiz': dict(clasificacion['por_causa_raiz']),
            'tipo_mas_frecuente': self._obtener_mas_frecuente(clasificacion['por_tipo']),
            'severidad_predominante': self._obtener_mas_frecuente(clasificacion['por_severidad']),
            'causa_principal': self._obtener_mas_frecuente(clasificacion['por_causa_raiz'])
        }
    
    def _extraer_valor_condicion(self, condicion: str) -> str:
        """Extrae el valor numérico de una condición crítica"""
        import re
        match = re.search(r'\(([\d.]+)[°%ppm]*\)', condicion)
        return match.group(1) if match else "N/A"
    
    def _determinar_severidad_alerta(self, log: Log) -> str:
        """Determina la severidad de una alerta crítica"""
        if log.estado == EstadoLog.ERROR:
            return "CRÍTICA"
        
        # Evaluar severidad basada en desviación de valores normales
        severidad_temp = abs(log.temperatura - 22) / 10  # Normalizado
        severidad_co2 = max(0, log.co2 - settings.CO2_MAX) / 500  # Normalizado
        severidad_hum = max(abs(log.humedad - 50) - 30, 0) / 20  # Normalizado
        
        severidad_total = max(severidad_temp, severidad_co2, severidad_hum)
        
        if severidad_total > 0.8:
            return "CRÍTICA"
        elif severidad_total > 0.4:
            return "ALTA"
        else:
            return "MEDIA"
    
    def _determinar_causa_raiz(self, log: Log) -> str:
        """Determina la probable causa raíz de una alerta"""
        if log.estado == EstadoLog.ERROR:
            return "Falla de sensor/sistema"
        
        # Análisis de patrones para determinar causa
        if log.temperatura > settings.TEMP_MAX and log.co2 > settings.CO2_MAX:
            return "Problema de ventilación/climatización"
        elif log.temperatura > settings.TEMP_MAX:
            return "Falla en climatización"
        elif log.co2 > settings.CO2_MAX:
            return "Ventilación insuficiente"
        elif log.humedad > settings.HUMEDAD_MAX:
            return "Problema de humidificación"
        else:
            return "Condición ambiental adversa"
    
    def _obtener_mas_frecuente(self, contador: Dict[str, Any]) -> str:
        """Obtiene el elemento más frecuente de un contador"""
        if not contador:
            return "N/A"
        
        if isinstance(list(contador.values())[0], list):
            # Para diccionarios con listas (por_tipo)
            return max(contador.items(), key=lambda x: len(x[1]))[0]
        else:
            # Para diccionarios con conteos (por_severidad, por_causa_raiz)
            return max(contador.items(), key=lambda x: x[1])[0]
    
    def _analizar_patron_temporal(self, logs_criticos: List[Log]) -> Dict[str, Any]:
        """Analiza patrones temporales en las alertas críticas"""
        # Agrupar por hora del día
        alertas_por_hora = defaultdict(int)
        alertas_por_dia = defaultdict(int)
        
        for log in logs_criticos:
            hora = log.timestamp.hour
            dia = log.timestamp.strftime('%Y-%m-%d')
            alertas_por_hora[hora] += 1
            alertas_por_dia[dia] += 1
        
        # Calcular intervalos entre alertas
        timestamps = sorted(log.timestamp for log in logs_criticos)
        intervalos = []
        for i in range(1, len(timestamps)):
            intervalo = (timestamps[i] - timestamps[i-1]).total_seconds() / 60  # minutos
            intervalos.append(intervalo)
        
        return {
            'distribucion_horaria': dict(alertas_por_hora),
            'distribucion_diaria': dict(alertas_por_dia),
            'hora_pico': max(alertas_por_hora.items(), key=lambda x: x[1])[0] if alertas_por_hora else None,
            'dia_mas_critico': max(alertas_por_dia.items(), key=lambda x: x[1])[0] if alertas_por_dia else None,
            'intervalo_promedio_minutos': round(statistics.mean(intervalos), 2) if intervalos else None,
            'frecuencia_alertas': self._calcular_frecuencia_alertas(logs_criticos),
            'tendencia_temporal': self._analizar_tendencia_alertas(logs_criticos)
        }
    
    def _calcular_frecuencia_alertas(self, logs_criticos: List[Log]) -> str:
        """Calcula la frecuencia de alertas críticas"""
        if len(logs_criticos) < 2:
            return "Datos insuficientes"
        
        periodo_total = (max(log.timestamp for log in logs_criticos) - 
                        min(log.timestamp for log in logs_criticos))
        horas_periodo = periodo_total.total_seconds() / 3600
        
        frecuencia_por_hora = len(logs_criticos) / horas_periodo if horas_periodo > 0 else 0
        
        if frecuencia_por_hora >= 2:
            return f"Alta ({frecuencia_por_hora:.1f} alertas/hora)"
        elif frecuencia_por_hora >= 0.5:
            return f"Moderada ({frecuencia_por_hora:.1f} alertas/hora)"
        else:
            return f"Baja ({frecuencia_por_hora:.2f} alertas/hora)"
    
    def _analizar_tendencia_alertas(self, logs_criticos: List[Log]) -> str:
        """Analiza la tendencia temporal de las alertas"""
        if len(logs_criticos) < 4:
            return "Datos insuficientes para tendencia"
        
        # Dividir en dos mitades y comparar frecuencia
        logs_ordenados = sorted(logs_criticos, key=lambda x: x.timestamp)
        mitad = len(logs_ordenados) // 2
        
        primera_mitad = logs_ordenados[:mitad]
        segunda_mitad = logs_ordenados[mitad:]
        
        periodo1 = (max(log.timestamp for log in primera_mitad) - 
                   min(log.timestamp for log in primera_mitad)).total_seconds() / 3600
        periodo2 = (max(log.timestamp for log in segunda_mitad) - 
                   min(log.timestamp for log in segunda_mitad)).total_seconds() / 3600
        
        freq1 = len(primera_mitad) / periodo1 if periodo1 > 0 else 0
        freq2 = len(segunda_mitad) / periodo2 if periodo2 > 0 else 0
        
        if freq2 > freq1 * 1.5:
            return "📈 Empeorando - frecuencia de alertas en aumento"
        elif freq2 < freq1 * 0.67:
            return "📉 Mejorando - frecuencia de alertas en descenso"
        else:
            return "→ Estable - frecuencia constante"
    
    def _analizar_impacto_por_sala(self, logs_criticos: List[Log]) -> Dict[str, Any]:
        """Analiza el impacto de alertas críticas por sala"""
        impacto_salas = defaultdict(lambda: {
            'total_alertas': 0,
            'tipos_alertas': defaultdict(int),
            'severidad_maxima': 'BAJA',
            'primera_alerta': None,
            'ultima_alerta': None,
            'duracion_problemas': 0
        })
        
        for log in logs_criticos:
            sala_data = impacto_salas[log.sala]
            sala_data['total_alertas'] += 1
            
            # Tipos de alertas
            for condicion in log.condiciones_criticas:
                sala_data['tipos_alertas'][condicion] += 1
            
            # Severidad máxima
            severidad = self._determinar_severidad_alerta(log)
            if self._comparar_severidad(severidad, sala_data['severidad_maxima']) > 0:
                sala_data['severidad_maxima'] = severidad
            
            # Timestamps
            if sala_data['primera_alerta'] is None or log.timestamp < sala_data['primera_alerta']:
                sala_data['primera_alerta'] = log.timestamp
            if sala_data['ultima_alerta'] is None or log.timestamp > sala_data['ultima_alerta']:
                sala_data['ultima_alerta'] = log.timestamp
        
        # Calcular duración de problemas
        for sala_data in impacto_salas.values():
            if sala_data['primera_alerta'] and sala_data['ultima_alerta']:
                duracion = (sala_data['ultima_alerta'] - sala_data['primera_alerta']).total_seconds() / 3600
                sala_data['duracion_problemas'] = round(duracion, 2)
        
        # Convertir a formato serializable
        resultado = {}
        for sala, data in impacto_salas.items():
            resultado[sala] = {
                'total_alertas': data['total_alertas'],
                'tipos_alertas': dict(data['tipos_alertas']),
                'severidad_maxima': data['severidad_maxima'],
                'primera_alerta': data['primera_alerta'].isoformat() if data['primera_alerta'] else None,
                'ultima_alerta': data['ultima_alerta'].isoformat() if data['ultima_alerta'] else None,
                'duracion_problemas_horas': data['duracion_problemas'],
                'nivel_impacto': self._calcular_nivel_impacto(data)
            }
        
        # Ranking de salas más afectadas
        ranking = sorted(resultado.items(), key=lambda x: x[1]['total_alertas'], reverse=True)
        
        return {
            'detalle_por_sala': resultado,
            'ranking_mas_afectadas': [{'sala': sala, **datos} for sala, datos in ranking],
            'sala_mas_critica': ranking[0][0] if ranking else None,
            'total_salas_afectadas': len(resultado)
        }
    
    def _comparar_severidad(self, sev1: str, sev2: str) -> int:
        """Compara dos niveles de severidad (-1, 0, 1)"""
        orden = {'BAJA': 0, 'MEDIA': 1, 'ALTA': 2, 'CRÍTICA': 3}
        return orden.get(sev1, 0) - orden.get(sev2, 0)
    
    def _calcular_nivel_impacto(self, data: Dict[str, Any]) -> str:
        """Calcula el nivel de impacto de una sala"""
        total_alertas = data['total_alertas']
        severidad = data['severidad_maxima']
        duracion = data['duracion_problemas']
        
        # Score basado en múltiples factores
        score = total_alertas
        if severidad == 'CRÍTICA':
            score *= 3
        elif severidad == 'ALTA':
            score *= 2
        
        if duracion > 24:  # Más de un día
            score *= 2
        elif duracion > 4:  # Más de 4 horas
            score *= 1.5
        
        if score >= 30:
            return "CRÍTICO"
        elif score >= 15:
            return "ALTO"
        elif score >= 5:
            return "MEDIO"
        else:
            return "BAJO"
    
    def _calcular_severidad_sistema(self, logs_criticos: List[Log], todos_logs: List[Log]) -> str:
        """Calcula la severidad general del sistema"""
        tasa_criticos = len(logs_criticos) / len(todos_logs) if todos_logs else 0
        
        # Contar alertas de máxima severidad
        alertas_criticas = sum(1 for log in logs_criticos if self._determinar_severidad_alerta(log) == 'CRÍTICA')
        tasa_criticas = alertas_criticas / len(logs_criticos) if logs_criticos else 0
        
        if tasa_criticos > 0.3 or tasa_criticas > 0.5:
            return "CRÍTICO"
        elif tasa_criticos > 0.1 or tasa_criticas > 0.2:
            return "ALTO"
        elif tasa_criticos > 0.05:
            return "MEDIO"
        else:
            return "BAJO"
    
    def _generar_alertas_activas(self, logs_criticos: List[Log]) -> List[Dict[str, Any]]:
        """Genera lista de alertas activas que requieren atención inmediata"""
        # Consideramos "activas" las alertas de las últimas 2 horas
        ahora = datetime.now()
        limite_activo = ahora - timedelta(hours=2)
        
        alertas_activas = []
        for log in logs_criticos:
            if log.timestamp >= limite_activo:
                alertas_activas.append({
                    'timestamp': log.timestamp.isoformat(),
                    'sala': log.sala,
                    'severidad': self._determinar_severidad_alerta(log),
                    'condiciones': log.condiciones_criticas,
                    'valores': {
                        'temperatura': log.temperatura,
                        'humedad': log.humedad,
                        'co2': log.co2
                    },
                    'tiempo_transcurrido_minutos': int((ahora - log.timestamp).total_seconds() / 60),
                    'requiere_accion_inmediata': self._requiere_accion_inmediata(log)
                })
        
        return sorted(alertas_activas, key=lambda x: x['timestamp'], reverse=True)
    
    def _requiere_accion_inmediata(self, log: Log) -> bool:
        """Determina si una alerta requiere acción inmediata"""
        return (log.estado == EstadoLog.ERROR or 
                log.temperatura > settings.TEMP_MAX + 5 or 
                log.co2 > settings.CO2_MAX + 500)
    
    def _generar_recomendaciones_criticas(self, logs_criticos: List[Log]) -> List[Dict[str, Any]]:
        """Genera recomendaciones críticas basadas en las alertas"""
        recomendaciones = []
        
        # Análisis de patrones para recomendaciones específicas
        tipos_alertas = defaultdict(int)
        salas_afectadas = set()
        
        for log in logs_criticos:
            salas_afectadas.add(log.sala)
            for condicion in log.condiciones_criticas:
                tipos_alertas[condicion] += 1
        
        # Recomendaciones basadas en tipos de alertas más frecuentes
        for tipo, frecuencia in tipos_alertas.items():
            if frecuencia >= len(logs_criticos) * 0.3:  # 30% o más de las alertas
                if 'temperatura alta' in tipo.lower():
                    recomendaciones.append({
                        'prioridad': 'ALTA',
                        'categoria': 'Climatización',
                        'accion': 'Revisar sistema de aire acondicionado',
                        'descripcion': f'Detectadas {frecuencia} alertas de temperatura alta',
                        'plazo': 'Inmediato'
                    })
                elif 'co2 elevado' in tipo.lower():
                    recomendaciones.append({
                        'prioridad': 'ALTA',
                        'categoria': 'Ventilación',
                        'accion': 'Verificar sistema de ventilación',
                        'descripcion': f'Detectadas {frecuencia} alertas de CO2 elevado',
                        'plazo': 'Inmediato'
                    })
        
        # Recomendaciones por número de salas afectadas
        if len(salas_afectadas) > 3:
            recomendaciones.append({
                'prioridad': 'CRÍTICA',
                'categoria': 'Sistema',
                'accion': 'Revisar infraestructura central',
                'descripcion': f'Múltiples salas afectadas ({len(salas_afectadas)})',
                'plazo': 'Inmediato'
            })
        
        return recomendaciones
    
    def _generar_plan_accion(self, logs_criticos: List[Log], clasificacion: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un plan de acción estructurado"""
        plan = {
            'acciones_inmediatas': [],
            'acciones_corto_plazo': [],
            'acciones_largo_plazo': [],
            'recursos_necesarios': [],
            'timeline': {}
        }
        
        # Acciones inmediatas (0-2 horas)
        alertas_recientes = [log for log in logs_criticos 
                           if (datetime.now() - log.timestamp).total_seconds() < 7200]
        
        if alertas_recientes:
            plan['acciones_inmediatas'].extend([
                '🚨 Verificar alertas activas en tiempo real',
                '👥 Notificar al equipo de mantenimiento',
                '📊 Confirmar lecturas de sensores'
            ])
        
        # Acciones corto plazo (2-24 horas)
        causa_principal = clasificacion.get('causa_principal', '')
        if 'ventilación' in causa_principal.lower():
            plan['acciones_corto_plazo'].append('🌪️ Inspeccionar y limpiar sistema de ventilación')
        if 'climatización' in causa_principal.lower():
            plan['acciones_corto_plazo'].append('❄️ Mantenimiento de sistema HVAC')
        
        # Acciones largo plazo (1-7 días)
        if len(logs_criticos) > 50:
            plan['acciones_largo_plazo'].extend([
                '📈 Análisis de tendencias y patrones',
                '🔧 Evaluación integral de infraestructura',
                '📋 Actualización de procedimientos de mantenimiento'
            ])
        
        return plan
    
    def _preparar_datos_para_csv(self, datos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara datos de alertas para exportación CSV"""
        rows = []
        
        for sala, info in datos.get('impacto_por_sala', {}).get('detalle_por_sala', {}).items():
            row = {
                'sala': sala,
                'total_alertas': info['total_alertas'],
                'severidad_maxima': info['severidad_maxima'],
                'nivel_impacto': info['nivel_impacto'],
                'duracion_problemas_horas': info['duracion_problemas_horas'],
                'primera_alerta': info['primera_alerta'],
                'ultima_alerta': info['ultima_alerta']
            }
            
            # Agregar tipos de alertas más frecuentes
            if info['tipos_alertas']:
                tipo_principal = max(info['tipos_alertas'].items(), key=lambda x: x[1])
                row['tipo_alerta_principal'] = tipo_principal[0]
                row['frecuencia_principal'] = tipo_principal[1]
            
            rows.append(row)
        
        return rows

class ReporteTendenciasAmbientales(ReporteBase):
    """
    Reporte de análisis de tendencias ambientales y predicciones.
    
    Se enfoca en la evolución temporal de las variables ambientales,
    detección de patrones y generación de predicciones básicas.
    """
    
    def __init__(self, estrategia_analisis: EstrategiaAnalisis):
        super().__init__(estrategia_analisis, "Reporte Tendencias Ambientales")
    
    def generar(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera análisis completo de tendencias ambientales"""
        if len(logs) < 10:
            return self._generar_reporte_datos_insuficientes(len(logs))
        
        # Análisis principal con estrategia configurada
        analisis_principal = self.estrategia_analisis.analizar(logs)
        
        # Análisis específicos de tendencias
        tendencias_variables = self._analizar_tendencias_detalladas(logs)
        patrones_estacionales = self._detectar_patrones_estacionales(logs)
        correlaciones_ambientales = self._analizar_correlaciones_ambientales(logs)
        predicciones = self._generar_predicciones_avanzadas(logs)
        
        return {
            'tipo_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'periodo_analisis': self._calcular_periodo_analisis(logs),
            'resumen_tendencias': self._generar_resumen_tendencias(logs),
            'analisis_principal': analisis_principal,
            'tendencias_detalladas': tendencias_variables,
            'patrones_temporales': patrones_estacionales,
            'correlaciones': correlaciones_ambientales,
            'predicciones': predicciones,
            'recomendaciones_tendencias': self._generar_recomendaciones_tendencias(logs, predicciones),
            'metricas_calidad_aire': self._calcular_metricas_calidad_aire(logs)
        }
    
    def _generar_reporte_datos_insuficientes(self, total_logs: int) -> Dict[str, Any]:
        """Genera reporte cuando hay datos insuficientes para análisis de tendencias"""
        return {
            'tipo_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'mensaje': f'⚠️ Datos insuficientes para análisis de tendencias (solo {total_logs} logs)',
            'minimo_requerido': 10,
            'recomendacion': 'Esperar más datos o ampliar el período de análisis'
        }
    
    def _calcular_periodo_analisis(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula información del período de análisis"""
        timestamps = [log.timestamp for log in logs]
        inicio = min(timestamps)
        fin = max(timestamps)
        duracion = fin - inicio
        
        return {
            'inicio': inicio.isoformat(),
            'fin': fin.isoformat(),
            'duracion_horas': round(duracion.total_seconds() / 3600, 2),
            'duracion_dias': duracion.days,
            'total_registros': len(logs),
            'frecuencia_promedio_minutos': round(duracion.total_seconds() / 60 / len(logs), 2) if len(logs) > 1 else None
        }
    
    def _generar_resumen_tendencias(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera un resumen ejecutivo de las tendencias principales"""
        # Dividir logs en segmentos para análisis de tendencia
        n_segmentos = min(5, len(logs) // 2)
        tamaño_segmento = len(logs) // n_segmentos
        
        segmentos = []
        for i in range(n_segmentos):
            inicio = i * tamaño_segmento
            fin = inicio + tamaño_segmento if i < n_segmentos - 1 else len(logs)
            segmentos.append(logs[inicio:fin])
        
        # Calcular promedios por segmento
        promedios_temp = [statistics.mean(log.temperatura for log in seg) for seg in segmentos]
        promedios_hum = [statistics.mean(log.humedad for log in seg) for seg in segmentos]
        promedios_co2 = [statistics.mean(log.co2 for log in seg) for seg in segmentos]
        
        return {
            'tendencia_temperatura': self._calcular_tendencia_lineal(promedios_temp),
            'tendencia_humedad': self._calcular_tendencia_lineal(promedios_hum),
            'tendencia_co2': self._calcular_tendencia_lineal(promedios_co2),
            'variabilidad_sistema': self._calcular_variabilidad_sistema(logs),
            'estabilidad_general': self._evaluar_estabilidad_general(logs),
            'alertas_tendencia': self._generar_alertas_tendencia(promedios_temp, promedios_hum, promedios_co2)
        }
    
    def _calcular_tendencia_lineal(self, valores: List[float]) -> Dict[str, Any]:
        """Calcula la tendencia lineal de una serie de valores"""
        if len(valores) < 2:
            return {'direccion': 'indeterminada', 'pendiente': 0, 'magnitud': 'N/A'}
        
        # Regresión lineal simple
        n = len(valores)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(valores)
        sum_xy = sum(x[i] * valores[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        # Calcular pendiente
        pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determinar dirección y magnitud
        if abs(pendiente) < 0.01:
            direccion = 'estable'
            magnitud = 'mínima'
        elif pendiente > 0:
            direccion = 'creciente'
            magnitud = 'significativa' if abs(pendiente) > 0.1 else 'moderada'
        else:
            direccion = 'decreciente'
            magnitud = 'significativa' if abs(pendiente) > 0.1 else 'moderada'
        
        return {
            'direccion': direccion,
            'pendiente': round(pendiente, 4),
            'magnitud': magnitud,
            'r_cuadrado': self._calcular_r_cuadrado(x, valores, pendiente)
        }
    
    def _calcular_r_cuadrado(self, x: List[int], y: List[float], pendiente: float) -> float:
        """Calcula el coeficiente de determinación R²"""
        if len(y) < 2:
            return 0
        
        # Calcular intercepto
        n = len(y)
        intercepto = (sum(y) - pendiente * sum(x)) / n
        
        # Valores predichos
        y_pred = [pendiente * xi + intercepto for xi in x]
        
        # R²
        y_mean = statistics.mean(y)
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        return round(max(0, r2), 3)  # Asegurar que R² >= 0
    
    def _calcular_variabilidad_sistema(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula métricas de variabilidad del sistema"""
        temperaturas = [log.temperatura for log in logs]
        humedades = [log.humedad for log in logs]
        co2_levels = [log.co2 for log in logs]
        
        return {
            'coeficiente_variacion_temperatura': round(statistics.stdev(temperaturas) / statistics.mean(temperaturas) * 100, 2) if temperaturas else 0,
            'coeficiente_variacion_humedad': round(statistics.stdev(humedades) / statistics.mean(humedades) * 100, 2) if humedades else 0,
            'coeficiente_variacion_co2': round(statistics.stdev(co2_levels) / statistics.mean(co2_levels) * 100, 2) if co2_levels else 0,
            'rango_temperatura': max(temperaturas) - min(temperaturas) if temperaturas else 0,
            'rango_humedad': max(humedades) - min(humedades) if humedades else 0,
            'rango_co2': max(co2_levels) - min(co2_levels) if co2_levels else 0
        }
    
    def _evaluar_estabilidad_general(self, logs: List[Log]) -> str:
        """Evalúa la estabilidad general del sistema"""
        # Calcular cambios entre mediciones consecutivas
        cambios_temp = []
        cambios_hum = []
        cambios_co2 = []
        
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        for i in range(1, len(logs_ordenados)):
            cambios_temp.append(abs(logs_ordenados[i].temperatura - logs_ordenados[i-1].temperatura))
            cambios_hum.append(abs(logs_ordenados[i].humedad - logs_ordenados[i-1].humedad))
            cambios_co2.append(abs(logs_ordenados[i].co2 - logs_ordenados[i-1].co2))
        
        if not cambios_temp:
            return "Indeterminada"
        
        volatilidad_temp = statistics.mean(cambios_temp)
        volatilidad_hum = statistics.mean(cambios_hum)
        volatilidad_co2 = statistics.mean(cambios_co2)
        
        # Evaluar estabilidad basada en umbrales
        if volatilidad_temp < 0.3 and volatilidad_hum < 1.5 and volatilidad_co2 < 30:
            return "Muy estable"
        elif volatilidad_temp < 0.7 and volatilidad_hum < 3.0 and volatilidad_co2 < 70:
            return "Estable"
        elif volatilidad_temp < 1.5 and volatilidad_hum < 6.0 and volatilidad_co2 < 150:
            return "Moderadamente variable"
        else:
            return "Altamente variable"
    
    def _generar_alertas_tendencia(self, temps: List[float], hums: List[float], co2s: List[float]) -> List[str]:
        """Genera alertas basadas en tendencias detectadas"""
        alertas = []
        
        # Verificar tendencias preocupantes
        if len(temps) >= 2:
            if temps[-1] > temps[0] + 2:
                alertas.append("📈 Tendencia al alza en temperatura - revisar climatización")
            elif temps[-1] < temps[0] - 2:
                alertas.append("📉 Tendencia a la baja en temperatura - verificar calefacción")
        
        if len(co2s) >= 2:
            if co2s[-1] > co2s[0] + 200:
                alertas.append("🌪️ CO2 en aumento - mejorar ventilación")
        
        if len(hums) >= 2:
            if hums[-1] > hums[0] + 15:
                alertas.append("💧 Humedad en aumento - revisar deshumidificación")
        
        return alertas
    
    def _analizar_tendencias_detalladas(self, logs: List[Log]) -> Dict[str, Any]:
        """Análisis detallado de tendencias por variable"""
        # Análisis por ventanas de tiempo
        ventanas = self._crear_ventanas_temporales(logs)
        
        return {
            'analisis_por_ventanas': ventanas,
            'ciclos_detectados': self._detectar_ciclos_avanzados(logs),
            'puntos_inflexion': self._detectar_puntos_inflexion(logs),
            'velocidad_cambio': self._calcular_velocidad_cambio(logs)
        }
    
    def _crear_ventanas_temporales(self, logs: List[Log]) -> Dict[str, Any]:
        """Crea ventanas temporales para análisis de tendencias"""
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        
        # Ventanas de 1 hora, 4 horas y 12 horas
        ventanas = {}
        duraciones = [1, 4, 12]  # horas
        
        for duracion in duraciones:
            ventana_logs = []
            tiempo_limite = datetime.now() - timedelta(hours=duracion)
            
            for log in reversed(logs_ordenados):  # Desde el más reciente
                if log.timestamp >= tiempo_limite:
                    ventana_logs.append(log)
                else:
                    break
            
            if ventana_logs:
                ventanas[f'{duracion}h'] = {
                    'registros': len(ventana_logs),
                    'temp_promedio': round(statistics.mean(log.temperatura for log in ventana_logs), 2),
                    'temp_tendencia': self._calcular_tendencia_simple(ventana_logs, 'temperatura'),
                    'alertas_criticas': sum(1 for log in ventana_logs if log.is_critical),
                    'estabilidad': self._evaluar_estabilidad_ventana(ventana_logs)
                }
        
        return ventanas
    
    def _calcular_tendencia_simple(self, logs: List[Log], variable: str) -> str:
        """Calcula tendencia simple para una variable en una ventana"""
        if len(logs) < 3:
            return "Datos insuficientes"
        
        valores = [getattr(log, variable) for log in logs]
        
        # Comparar primer tercio con último tercio
        n = len(valores)
        primer_tercio = statistics.mean(valores[:n//3])
        ultimo_tercio = statistics.mean(valores[2*n//3:])
        
        diferencia = ultimo_tercio - primer_tercio
        porcentaje_cambio = abs(diferencia / primer_tercio * 100) if primer_tercio != 0 else 0
        
        if porcentaje_cambio < 2:
            return "Estable"
        elif diferencia > 0:
            return f"Subiendo (+{porcentaje_cambio:.1f}%)"
        else:
            return f"Bajando (-{porcentaje_cambio:.1f}%)"
    
    def _evaluar_estabilidad_ventana(self, logs: List[Log]) -> str:
        """Evalúa la estabilidad en una ventana temporal"""
        if len(logs) < 2:
            return "Indeterminada"
        
        temperaturas = [log.temperatura for log in logs]
        cv_temp = statistics.stdev(temperaturas) / statistics.mean(temperaturas) * 100
        
        if cv_temp < 2:
            return "Muy estable"
        elif cv_temp < 5:
            return "Estable"
        elif cv_temp < 10:
            return "Variable"
        else:
            return "Muy variable"
    
    def _detectar_ciclos_avanzados(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta ciclos más avanzados en los datos"""
        if len(logs) < 24:  # Mínimo para detectar ciclos diarios
            return {'mensaje': 'Datos insuficientes para detectar ciclos'}
        
        # Agrupar por hora del día para detectar ciclos diarios
        temps_por_hora = defaultdict(list)
        for log in logs:
            hora = log.timestamp.hour
            temps_por_hora[hora].append(log.temperatura)
        
        # Calcular promedio por hora
        promedio_horario = {}
        for hora, temps in temps_por_hora.items():
            if temps:
                promedio_horario[hora] = statistics.mean(temps)
        
        # Detectar patrón de ciclo diario
        if len(promedio_horario) >= 12:  # Al menos 12 horas de datos
            valores_ordenados = [promedio_horario[h] for h in sorted(promedio_horario.keys())]
            
            # Buscar picos y valles
            picos = []
            valles = []
            
            for i in range(1, len(valores_ordenados) - 1):
                if (valores_ordenados[i] > valores_ordenados[i-1] and 
                    valores_ordenados[i] > valores_ordenados[i+1]):
                    picos.append(i)
                elif (valores_ordenados[i] < valores_ordenados[i-1] and 
                      valores_ordenados[i] < valores_ordenados[i+1]):
                    valles.append(i)
            
            return {
                'ciclo_diario_detectado': len(picos) > 0 and len(valles) > 0,
                'horas_pico': [list(promedio_horario.keys())[p] for p in picos],
                'horas_valle': [list(promedio_horario.keys())[v] for v in valles],
                'amplitud_ciclo': max(valores_ordenados) - min(valores_ordenados) if valores_ordenados else 0,
                'regularidad': self._calcular_regularidad_ciclo(valores_ordenados)
            }
        
        return {'mensaje': 'Datos insuficientes para ciclos diarios completos'}
    
    def _calcular_regularidad_ciclo(self, valores: List[float]) -> str:
        """Calcula la regularidad de un ciclo"""
        if len(valores) < 4:
            return "Indeterminada"
        
        # Calcular variabilidad entre períodos
        cv = statistics.stdev(valores) / statistics.mean(valores) * 100
        
        if cv < 5:
            return "Muy regular"
        elif cv < 10:
            return "Regular"
        elif cv < 20:
            return "Moderadamente irregular"
        else:
            return "Irregular"
    
    def _detectar_puntos_inflexion(self, logs: List[Log]) -> List[Dict[str, Any]]:
        """Detecta puntos de inflexión significativos en las tendencias"""
        if len(logs) < 10:
            return []
        
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        temperaturas = [log.temperatura for log in logs_ordenados]
        
        puntos_inflexion = []
        ventana = 5  # Ventana para detectar cambios
        
        for i in range(ventana, len(temperaturas) - ventana):
            # Tendencia antes y después del punto
            antes = temperaturas[i-ventana:i]
            despues = temperaturas[i:i+ventana]
            
            tendencia_antes = (antes[-1] - antes[0]) / len(antes)
            tendencia_despues = (despues[-1] - despues[0]) / len(despues)
            
            # Detectar cambio significativo de tendencia
            if abs(tendencia_despues - tendencia_antes) > 0.5:  # Umbral de cambio
                puntos_inflexion.append({
                    'timestamp': logs_ordenados[i].timestamp.isoformat(),
                    'valor': temperaturas[i],
                    'cambio_tendencia': round(tendencia_despues - tendencia_antes, 3),
                    'tipo': 'aceleracion' if tendencia_despues > tendencia_antes else 'desaceleracion'
                })
        
        return puntos_inflexion[:10]  # Máximo 10 puntos más significativos
    
    def _calcular_velocidad_cambio(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula la velocidad de cambio de las variables"""
        if len(logs) < 2:
            return {}
        
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        
        velocidades_temp = []
        velocidades_hum = []
        velocidades_co2 = []
        
        for i in range(1, len(logs_ordenados)):
            dt = (logs_ordenados[i].timestamp - logs_ordenados[i-1].timestamp).total_seconds() / 3600  # horas
            
            if dt > 0:
                vel_temp = abs(logs_ordenados[i].temperatura - logs_ordenados[i-1].temperatura) / dt
                vel_hum = abs(logs_ordenados[i].humedad - logs_ordenados[i-1].humedad) / dt
                vel_co2 = abs(logs_ordenados[i].co2 - logs_ordenados[i-1].co2) / dt
                
                velocidades_temp.append(vel_temp)
                velocidades_hum.append(vel_hum)
                velocidades_co2.append(vel_co2)
        
        return {
            'velocidad_promedio_temp': round(statistics.mean(velocidades_temp), 3) if velocidades_temp else 0,
            'velocidad_maxima_temp': round(max(velocidades_temp), 3) if velocidades_temp else 0,
            'velocidad_promedio_hum': round(statistics.mean(velocidades_hum), 3) if velocidades_hum else 0,
            'velocidad_promedio_co2': round(statistics.mean(velocidades_co2), 3) if velocidades_co2 else 0,
            'unidades': {
                'temperatura': '°C/hora',
                'humedad': '%/hora',
                'co2': 'ppm/hora'
            }
        }
    
    def _detectar_patrones_estacionales(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta patrones estacionales o cíclicos en los datos"""
        # Simplificado: análisis por día de la semana y hora del día
        patrones_dia = defaultdict(list)
        patrones_hora = defaultdict(list)
        
        for log in logs:
            dia_semana = log.timestamp.weekday()  # 0=Lunes, 6=Domingo
            hora_dia = log.timestamp.hour
            
            patrones_dia[dia_semana].append(log.temperatura)
            patrones_hora[hora_dia].append(log.temperatura)
        
        # Calcular promedios
        temp_por_dia = {
            dia: round(statistics.mean(temps), 2) 
            for dia, temps in patrones_dia.items() if temps
        }
        
        temp_por_hora = {
            hora: round(statistics.mean(temps), 2) 
            for hora, temps in patrones_hora.items() if temps
        }
        
        return {
            'patron_semanal': {
                'temperaturas_por_dia': temp_por_dia,
                'dia_mas_calido': max(temp_por_dia.items(), key=lambda x: x[1]) if temp_por_dia else None,
                'dia_mas_frio': min(temp_por_dia.items(), key=lambda x: x[1]) if temp_por_dia else None,
                'variacion_semanal': max(temp_por_dia.values()) - min(temp_por_dia.values()) if temp_por_dia else 0
            },
            'patron_diario': {
                'temperaturas_por_hora': temp_por_hora,
                'hora_mas_calida': max(temp_por_hora.items(), key=lambda x: x[1]) if temp_por_hora else None,
                'hora_mas_fria': min(temp_por_hora.items(), key=lambda x: x[1]) if temp_por_hora else None,
                'variacion_diaria': max(temp_por_hora.values()) - min(temp_por_hora.values()) if temp_por_hora else 0
            }
        }
    
    def _analizar_correlaciones_ambientales(self, logs: List[Log]) -> Dict[str, Any]:
        """Analiza correlaciones entre variables ambientales"""
        if len(logs) < 10:
            return {'mensaje': 'Datos insuficientes para análisis de correlaciones'}
        
        temperaturas = [log.temperatura for log in logs]
        humedades = [log.humedad for log in logs]
        co2_levels = [log.co2 for log in logs]
        
        correlaciones = {}
        
        try:
            correlaciones['temp_humedad'] = {
                'coeficiente': round(statistics.correlation(temperaturas, humedades), 3),
                'interpretacion': self._interpretar_correlacion(statistics.correlation(temperaturas, humedades))
            }
        except:
            correlaciones['temp_humedad'] = {'coeficiente': 0, 'interpretacion': 'No calculable'}
        
        try:
            correlaciones['temp_co2'] = {
                'coeficiente': round(statistics.correlation(temperaturas, co2_levels), 3),
                'interpretacion': self._interpretar_correlacion(statistics.correlation(temperaturas, co2_levels))
            }
        except:
            correlaciones['temp_co2'] = {'coeficiente': 0, 'interpretacion': 'No calculable'}
        
        try:
            correlaciones['humedad_co2'] = {
                'coeficiente': round(statistics.correlation(humedades, co2_levels), 3),
                'interpretacion': self._interpretar_correlacion(statistics.correlation(humedades, co2_levels))
            }
        except:
            correlaciones['humedad_co2'] = {'coeficiente': 0, 'interpretacion': 'No calculable'}
        
        return {
            'correlaciones_bivariadas': correlaciones,
            'analisis_multivariado': self._analisis_multivariado_simple(temperaturas, humedades, co2_levels)
        }
    
    def _interpretar_correlacion(self, r: float) -> str:
        """Interpreta el coeficiente de correlación"""
        abs_r = abs(r)
        
        if abs_r >= 0.8:
            fuerza = "muy fuerte"
        elif abs_r >= 0.6:
            fuerza = "fuerte"
        elif abs_r >= 0.4:
            fuerza = "moderada"
        elif abs_r >= 0.2:
            fuerza = "débil"
        else:
            fuerza = "muy débil o nula"
        
        direccion = "positiva" if r >= 0 else "negativa"
        
        return f"Correlación {direccion} {fuerza}"
    
    def _analisis_multivariado_simple(self, temps: List[float], hums: List[float], co2s: List[float]) -> Dict[str, Any]:
        """Análisis multivariado simplificado"""
        # Análisis de combinaciones críticas
        combinaciones_criticas = 0
        
        for i in range(len(temps)):
            temp_alta = temps[i] > settings.TEMP_MAX
            co2_alto = co2s[i] > settings.CO2_MAX
            hum_alta = hums[i] > settings.HUMEDAD_MAX
            
            # Contar combinaciones problemáticas
            if sum([temp_alta, co2_alto, hum_alta]) >= 2:
                combinaciones_criticas += 1
        
        return {
            'combinaciones_criticas': combinaciones_criticas,
            'porcentaje_combinaciones_criticas': round(combinaciones_criticas / len(temps) * 100, 1),
            'patron_mas_comun': self._identificar_patron_mas_comun(temps, hums, co2s)
        }
    
    def _identificar_patron_mas_comun(self, temps: List[float], hums: List[float], co2s: List[float]) -> str:
        """Identifica el patrón más común en los datos"""
        patrones = {
            'temp_alta_co2_alto': 0,
            'temp_alta_hum_alta': 0,
            'co2_alto_hum_alta': 0,
            'todas_altas': 0,
            'todas_normales': 0
        }
        
        for i in range(len(temps)):
            temp_alta = temps[i] > settings.TEMP_MAX
            co2_alto = co2s[i] > settings.CO2_MAX
            hum_alta = hums[i] > settings.HUMEDAD_MAX
            
            if temp_alta and co2_alto and hum_alta:
                patrones['todas_altas'] += 1
            elif temp_alta and co2_alto:
                patrones['temp_alta_co2_alto'] += 1
            elif temp_alta and hum_alta:
                patrones['temp_alta_hum_alta'] += 1
            elif co2_alto and hum_alta:
                patrones['co2_alto_hum_alta'] += 1
            elif not (temp_alta or co2_alto or hum_alta):
                patrones['todas_normales'] += 1
        
        patron_dominante = max(patrones.items(), key=lambda x: x[1])
        return f"{patron_dominante[0]}: {patron_dominante[1]} ocurrencias"
    
    def _generar_predicciones_avanzadas(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera predicciones más avanzadas basadas en tendencias"""
        if len(logs) < 20:
            return {'mensaje': 'Datos insuficientes para predicciones confiables'}
        
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        
        # Usar últimos 10 registros para predicción
        logs_recientes = logs_ordenados[-10:]
        
        # Predicción basada en tendencia lineal
        predicciones = {}
        
        for variable in ['temperatura', 'humedad', 'co2']:
            valores = [getattr(log, variable) for log in logs_recientes]
            
            # Calcular tendencia
            x = list(range(len(valores)))
            tendencia = self._calcular_tendencia_lineal(valores)
            
            if tendencia['direccion'] != 'indeterminada':
                # Predicción para los próximos 3 períodos
                ultimo_valor = valores[-1]
                prediccion_1 = ultimo_valor + tendencia['pendiente']
                prediccion_2 = ultimo_valor + 2 * tendencia['pendiente']
                prediccion_3 = ultimo_valor + 3 * tendencia['pendiente']
                
                predicciones[variable] = {
                    'prediccion_1_periodo': round(prediccion_1, 2),
                    'prediccion_2_periodos': round(prediccion_2, 2),
                    'prediccion_3_periodos': round(prediccion_3, 2),
                    'confianza': self._calcular_confianza_prediccion(tendencia['r_cuadrado']),
                    'alertas_prediccion': self._generar_alertas_prediccion(variable, [prediccion_1, prediccion_2, prediccion_3])
                }
        
        return {
            'predicciones_por_variable': predicciones,
            'horizonte_prediccion': '3 períodos de medición',
            'metodo': 'Regresión lineal simple',
            'limitaciones': 'Predicciones válidas para condiciones estables similares al período analizado'
        }
    
    def _calcular_confianza_prediccion(self, r_cuadrado: float) -> str:
        """Calcula el nivel de confianza de una predicción"""
        if r_cuadrado >= 0.8:
            return "Alta"
        elif r_cuadrado >= 0.5:
            return "Media"
        elif r_cuadrado >= 0.2:
            return "Baja"
        else:
            return "Muy baja"
    
    def _generar_alertas_prediccion(self, variable: str, predicciones: List[float]) -> List[str]:
        """Genera alertas basadas en predicciones"""
        alertas = []
        
        for i, pred in enumerate(predicciones, 1):
            if variable == 'temperatura':
                if pred > settings.TEMP_MAX:
                    alertas.append(f"⚠️ Período {i}: Temperatura alta prevista ({pred:.1f}°C)")
                elif pred < settings.TEMP_MIN:
                    alertas.append(f"🧊 Período {i}: Temperatura baja prevista ({pred:.1f}°C)")
            
            elif variable == 'co2':
                if pred > settings.CO2_MAX:
                    alertas.append(f"🌪️ Período {i}: CO2 elevado previsto ({pred:.0f}ppm)")
            
            elif variable == 'humedad':
                if pred > settings.HUMEDAD_MAX:
                    alertas.append(f"💧 Período {i}: Humedad alta prevista ({pred:.1f}%)")
                elif pred < settings.HUMEDAD_MIN:
                    alertas.append(f"🏜️ Período {i}: Humedad baja prevista ({pred:.1f}%)")
        
        return alertas
    
    def _generar_recomendaciones_tendencias(self, logs: List[Log], predicciones: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en análisis de tendencias"""
        recomendaciones = []
        
        # Recomendaciones basadas en predicciones
        if 'predicciones_por_variable' in predicciones:
            for variable, pred_data in predicciones['predicciones_por_variable'].items():
                if pred_data.get('alertas_prediccion'):
                    recomendaciones.append({
                        'categoria': 'Predictiva',
                        'prioridad': 'MEDIA',
                        'accion': f'Monitorear evolución de {variable}',
                        'descripcion': f"Tendencia detectada en {variable} puede requerir ajustes",
                        'plazo': '1-3 períodos de medición'
                    })
        
        # Recomendaciones basadas en variabilidad
        if len(logs) >= 10:
            logs_recientes = sorted(logs, key=lambda x: x.timestamp)[-10:]
            temps = [log.temperatura for log in logs_recientes]
            
            if statistics.stdev(temps) > 2:  # Alta variabilidad
                recomendaciones.append({
                    'categoria': 'Estabilización',
                    'prioridad': 'ALTA',
                    'accion': 'Revisar sistema de control de temperatura',
                    'descripcion': 'Alta variabilidad en temperatura detectada',
                    'plazo': 'Inmediato'
                })
        
        # Recomendaciones basadas en patrones detectados
        recomendaciones.append({
            'categoria': 'Optimización',
            'prioridad': 'BAJA',
            'accion': 'Implementar control predictivo',
            'descripcion': 'Aprovechar patrones detectados para control proactivo',
            'plazo': 'Largo plazo'
        })
        
        return recomendaciones[:5]  # Máximo 5 recomendaciones
    
    def _calcular_metricas_calidad_aire(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula métricas específicas de calidad del aire"""
        co2_levels = [log.co2 for log in logs]
        
        # Clasificación de calidad según niveles de CO2
        excelente = sum(1 for co2 in co2_levels if co2 <= 400)
        buena = sum(1 for co2 in co2_levels if 400 < co2 <= 600)
        aceptable = sum(1 for co2 in co2_levels if 600 < co2 <= 1000)
        deficiente = sum(1 for co2 in co2_levels if 1000 < co2 <= 1500)
        mala = sum(1 for co2 in co2_levels if co2 > 1500)
        
        total = len(co2_levels)
        
        return {
            'distribucion_calidad': {
                'excelente': {'count': excelente, 'porcentaje': round(excelente/total*100, 1) if total > 0 else 0},
                'buena': {'count': buena, 'porcentaje': round(buena/total*100, 1) if total > 0 else 0},
                'aceptable': {'count': aceptable, 'porcentaje': round(aceptable/total*100, 1) if total > 0 else 0},
                'deficiente': {'count': deficiente, 'porcentaje': round(deficiente/total*100, 1) if total > 0 else 0},
                'mala': {'count': mala, 'porcentaje': round(mala/total*100, 1) if total > 0 else 0}
            },
            'calidad_predominante': self._determinar_calidad_predominante(excelente, buena, aceptable, deficiente, mala),
            'indice_calidad_promedio': self._calcular_indice_calidad(co2_levels),
            'tiempo_exposicion_deficiente': round((deficiente + mala) / total * 100, 1) if total > 0 else 0
        }
    
    def _determinar_calidad_predominante(self, excelente: int, buena: int, aceptable: int, deficiente: int, mala: int) -> str:
        """Determina la calidad de aire predominante"""
        valores = [
            (excelente, 'Excelente'),
            (buena, 'Buena'),
            (aceptable, 'Aceptable'),
            (deficiente, 'Deficiente'),
            (mala, 'Mala')
        ]
        
        return max(valores, key=lambda x: x[0])[1]
    
    def _calcular_indice_calidad(self, co2_levels: List[int]) -> float:
        """Calcula un índice de calidad del aire basado en CO2"""
        if not co2_levels:
            return 0
        
        # Índice simple: 100 - (promedio_co2 - 400) / 10
        # Donde 400ppm = índice 100, 1000ppm = índice 40
        promedio_co2 = statistics.mean(co2_levels)
        indice = max(0, min(100, 100 - (promedio_co2 - 400) / 10))
        
        return round(indice, 1)
    
    def _preparar_datos_para_csv(self, datos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepara datos de tendencias para exportación CSV"""
        rows = []
        
        # Datos del período de análisis
        if 'periodo_analisis' in datos:
            periodo = datos['periodo_analisis']
            rows.append({
                'tipo_dato': 'periodo_analisis',
                'inicio': periodo.get('inicio', ''),
                'fin': periodo.get('fin', ''),
                'duracion_horas': periodo.get('duracion_horas', 0),
                'total_registros': periodo.get('total_registros', 0)
            })
        
        # Tendencias por variable
        if 'resumen_tendencias' in datos:
            resumen = datos['resumen_tendencias']
            for variable in ['temperatura', 'humedad', 'co2']:
                if f'tendencia_{variable}' in resumen:
                    tendencia = resumen[f'tendencia_{variable}']
                    rows.append({
                        'tipo_dato': f'tendencia_{variable}',
                        'direccion': tendencia.get('direccion', ''),
                        'pendiente': tendencia.get('pendiente', 0),
                        'magnitud': tendencia.get('magnitud', ''),
                        'r_cuadrado': tendencia.get('r_cuadrado', 0)
                    })
        
        return rows

class ReporteResumenEjecutivo(ReporteBase):
    """
    Reporte ejecutivo consolidado con métricas clave y recomendaciones estratégicas.
    
    Diseñado para la alta dirección, combina datos operacionales
    con insights estratégicos y recomendaciones de acción.
    """
    
    def __init__(self, estrategia_analisis: EstrategiaAnalisis):
        super().__init__(estrategia_analisis, "Resumen Ejecutivo")