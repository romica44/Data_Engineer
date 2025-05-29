"""
Estrategias de análisis para reportes (Strategy Pattern)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import logging

from models import Log, EstadoLog
from config.settings import settings

logger = logging.getLogger(__name__)

class EstrategiaAnalisis(ABC):
    """
    Estrategia abstracta para diferentes algoritmos de análisis.
    
    Implementa el patrón Strategy permitiendo intercambiar algoritmos
    de análisis sin modificar el código cliente.
    """
    
    @abstractmethod
    def analizar(self, logs: List[Log]) -> Dict[str, Any]:
        """
        Ejecuta el análisis específico de la estrategia.
        
        Args:
            logs: Lista de logs a analizar
            
        Returns:
            Diccionario con resultados del análisis
        """
        pass
    
    @abstractmethod
    def get_nombre_estrategia(self) -> str:
        """Retorna el nombre de la estrategia"""
        pass

class AnalisisEstadistico(EstrategiaAnalisis):
    """
    Estrategia de análisis estadístico completo.
    
    Proporciona estadísticas descriptivas, distribuciones
    y métricas de calidad de datos.
    """
    
    def analizar(self, logs: List[Log]) -> Dict[str, Any]:
        """Realiza análisis estadístico completo"""
        if not logs:
            return {'error': 'No hay logs para analizar'}
        
        # Extraer métricas numéricas
        temperaturas = [log.temperatura for log in logs]
        humedades = [log.humedad for log in logs]
        co2_levels = [log.co2 for log in logs]
        
        # Estadísticas descriptivas
        estadisticas = {
            'total_registros': len(logs),
            'periodo_analisis': {
                'inicio': min(log.timestamp for log in logs).isoformat(),
                'fin': max(log.timestamp for log in logs).isoformat(),
                'duracion_horas': (max(log.timestamp for log in logs) - min(log.timestamp for log in logs)).total_seconds() / 3600
            },
            'metricas_ambientales': {
                'temperatura': self._calcular_estadisticas_variable(temperaturas, '°C'),
                'humedad': self._calcular_estadisticas_variable(humedades, '%'),
                'co2': self._calcular_estadisticas_variable(co2_levels, 'ppm')
            },
            'distribucion_estados': self._analizar_distribucion_estados(logs),
            'alertas_criticas': self._analizar_alertas_criticas(logs),
            'calidad_datos': self._evaluar_calidad_datos(logs),
            'correlaciones': self._calcular_correlaciones_basicas(logs)
        }
        
        return estadisticas
    
    def _calcular_estadisticas_variable(self, valores: List[float], unidad: str) -> Dict[str, Any]:
        """Calcula estadísticas descriptivas para una variable"""
        if not valores:
            return {}
        
        valores_ordenados = sorted(valores)
        n = len(valores)
        
        return {
            'promedio': round(statistics.mean(valores), 2),
            'mediana': round(statistics.median(valores), 2),
            'minimo': min(valores),
            'maximo': max(valores),
            'desviacion_estandar': round(statistics.stdev(valores) if n > 1 else 0, 2),
            'percentil_25': round(valores_ordenados[n//4], 2),
            'percentil_75': round(valores_ordenados[3*n//4], 2),
            'rango': max(valores) - min(valores),
            'unidad': unidad,
            'valores_extremos': self._detectar_valores_extremos(valores)
        }
    
    def _detectar_valores_extremos(self, valores: List[float], umbral_z: float = 2.5) -> Dict[str, Any]:
        """Detecta valores extremos usando Z-score"""
        if len(valores) < 3:
            return {'outliers': [], 'cantidad': 0}
        
        media = statistics.mean(valores)
        desv_std = statistics.stdev(valores)
        
        if desv_std == 0:
            return {'outliers': [], 'cantidad': 0}
        
        outliers = []
        for valor in valores:
            z_score = abs(valor - media) / desv_std
            if z_score > umbral_z:
                outliers.append({'valor': valor, 'z_score': round(z_score, 2)})
        
        return {
            'outliers': outliers[:10],  # Máximo 10 para evitar reportes muy largos
            'cantidad': len(outliers)
        }
    
    def _analizar_distribucion_estados(self, logs: List[Log]) -> Dict[str, Any]:
        """Analiza la distribución de estados de los logs"""
        contador_estados = Counter(log.estado for log in logs)
        total = len(logs)
        
        return {
            'conteos': {estado.value: count for estado, count in contador_estados.items()},
            'porcentajes': {
                estado.value: round(count / total * 100, 1) 
                for estado, count in contador_estados.items()
            },
            'estado_predominante': contador_estados.most_common(1)[0][0].value if contador_estados else None
        }
    
    def _analizar_alertas_criticas(self, logs: List[Log]) -> Dict[str, Any]:
        """Analiza las alertas críticas en detalle"""
        logs_criticos = [log for log in logs if log.is_critical]
        
        if not logs_criticos:
            return {'total': 0, 'porcentaje': 0, 'tipos': {}}
        
        # Clasificar tipos de criticidad
        tipos_criticidad = defaultdict(int)
        for log in logs_criticos:
            for condicion in log.condiciones_criticas:
                tipos_criticidad[condicion] += 1
        
        return {
            'total': len(logs_criticos),
            'porcentaje': round(len(logs_criticos) / len(logs) * 100, 1),
            'tipos': dict(tipos_criticidad),
            'tipo_mas_frecuente': max(tipos_criticidad.items(), key=lambda x: x[1])[0] if tipos_criticidad else None,
            'salas_mas_afectadas': self._salas_con_mas_alertas(logs_criticos)
        }
    
    def _salas_con_mas_alertas(self, logs_criticos: List[Log]) -> List[Dict[str, Any]]:
        """Identifica las salas con más alertas críticas"""
        contador_salas = Counter(log.sala for log in logs_criticos)
        
        return [
            {'sala': sala, 'alertas': count}
            for sala, count in contador_salas.most_common(5)
        ]
    
    def _evaluar_calidad_datos(self, logs: List[Log]) -> Dict[str, Any]:
        """Evalúa la calidad de los datos"""
        total_logs = len(logs)
        
        # Verificar completitud de datos
        logs_completos = sum(1 for log in logs if all([
            log.temperatura is not None,
            log.humedad is not None,
            log.co2 is not None,
            log.sala and log.sala.strip(),
            log.mensaje and log.mensaje.strip()
        ]))
        
        # Verificar consistencia temporal
        timestamps_ordenados = sorted(log.timestamp for log in logs)
        gaps_grandes = 0
        for i in range(1, len(timestamps_ordenados)):
            diff = (timestamps_ordenados[i] - timestamps_ordenados[i-1]).total_seconds()
            if diff > 300:  # Mayor a 5 minutos
                gaps_grandes += 1
        
        return {
            'completitud_porcentaje': round(logs_completos / total_logs * 100, 1),
            'gaps_temporales_grandes': gaps_grandes,
            'frecuencia_promedio_segundos': self._calcular_frecuencia_promedio(timestamps_ordenados),
            'calificacion_general': self._calcular_calificacion_calidad(logs_completos, total_logs, gaps_grandes)
        }
    
    def _calcular_frecuencia_promedio(self, timestamps: List[datetime]) -> float:
        """Calcula la frecuencia promedio entre registros"""
        if len(timestamps) < 2:
            return 0
        
        diferencias = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            diferencias.append(diff)
        
        return round(statistics.mean(diferencias), 2)
    
    def _calcular_calificacion_calidad(self, logs_completos: int, total_logs: int, gaps_grandes: int) -> str:
        """Calcula una calificación general de calidad"""
        completitud = logs_completos / total_logs
        penalizacion_gaps = min(gaps_grandes / total_logs, 0.2)  # Máximo 20% de penalización
        
        score = completitud - penalizacion_gaps
        
        if score >= 0.95:
            return "Excelente"
        elif score >= 0.85:
            return "Buena"
        elif score >= 0.70:
            return "Aceptable"
        else:
            return "Deficiente"
    
    def _calcular_correlaciones_basicas(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula correlaciones básicas entre variables"""
        if len(logs) < 10:
            return {'mensaje': 'Datos insuficientes para correlaciones'}
        
        # Extraer datos
        temperaturas = [log.temperatura for log in logs]
        humedades = [log.humedad for log in logs]
        co2_levels = [log.co2 for log in logs]
        
        return {
            'temp_humedad': self._correlacion_pearson(temperaturas, humedades),
            'temp_co2': self._correlacion_pearson(temperaturas, co2_levels),
            'humedad_co2': self._correlacion_pearson(humedades, co2_levels)
        }
    
    def _correlacion_pearson(self, x: List[float], y: List[float]) -> float:
        """Calcula correlación de Pearson entre dos variables"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        try:
            return round(statistics.correlation(x, y), 3)
        except statistics.StatisticsError:
            return 0
    
    def get_nombre_estrategia(self) -> str:
        return "Análisis Estadístico Completo"

class AnalisisTendencias(EstrategiaAnalisis):
    """
    Estrategia de análisis de tendencias temporales.
    
    Se enfoca en la evolución temporal de las variables
    y la detección de patrones.
    """
    
    def analizar(self, logs: List[Log]) -> Dict[str, Any]:
        """Realiza análisis de tendencias temporales"""
        if not logs:
            return {'error': 'No hay logs para análizar'}
        
        # Ordenar por timestamp
        logs_ordenados = sorted(logs, key=lambda x: x.timestamp)
        
        analisis = {
            'tendencias_variables': self._analizar_tendencias_variables(logs_ordenados),
            'patrones_temporales': self._detectar_patrones_temporales(logs_ordenados),
            'volatilidad': self._calcular_volatilidad(logs_ordenados),
            'ciclos_detectados': self._detectar_ciclos(logs_ordenados),
            'predicciones_simples': self._generar_predicciones_simples(logs_ordenados),
            'anomalias_temporales': self._detectar_anomalias_temporales(logs_ordenados)
        }
        
        return analisis
    
    def _analizar_tendencias_variables(self, logs: List[Log]) -> Dict[str, Any]:
        """Analiza tendencias de las variables principales"""
        if len(logs) < 3:
            return {'mensaje': 'Datos insuficientes para análisis de tendencias'}
        
        # Dividir en segmentos para análisis
        tercio = len(logs) // 3
        
        # Promedios por segmento
        seg1 = logs[:tercio]
        seg2 = logs[tercio:2*tercio]
        seg3 = logs[2*tercio:]
        
        def promedio_segmento(logs_seg, attr):
            return statistics.mean(getattr(log, attr) for log in logs_seg) if logs_seg else 0
        
        tendencias = {}
        for variable in ['temperatura', 'humedad', 'co2']:
            prom1 = promedio_segmento(seg1, variable)
            prom2 = promedio_segmento(seg2, variable)
            prom3 = promedio_segmento(seg3, variable)
            
            # Calcular tendencia
            if prom3 > prom1 * 1.05:
                tendencia = "Creciente"
            elif prom3 < prom1 * 0.95:
                tendencia = "Decreciente"
            else:
                tendencia = "Estable"
            
            tendencias[variable] = {
                'tendencia': tendencia,
                'inicio': round(prom1, 2),
                'medio': round(prom2, 2),
                'final': round(prom3, 2),
                'cambio_porcentual': round((prom3 - prom1) / prom1 * 100, 2) if prom1 != 0 else 0
            }
        
        return tendencias
    
    def _detectar_patrones_temporales(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta patrones temporales en los datos"""
        # Agrupar por hora del día
        logs_por_hora = defaultdict(list)
        for log in logs:
            hora = log.timestamp.hour
            logs_por_hora[hora].append(log)
        
        # Calcular promedios por hora
        patrones_horarios = {}
        for hora, logs_hora in logs_por_hora.items():
            if logs_hora:
                patrones_horarios[f"hora_{hora:02d}"] = {
                    'temperatura_promedio': round(statistics.mean(log.temperatura for log in logs_hora), 2),
                    'registros': len(logs_hora),
                    'alertas_criticas': sum(1 for log in logs_hora if log.is_critical)
                }
        
        # Detectar hora pico de actividad
        hora_max_actividad = max(patrones_horarios.items(), key=lambda x: x[1]['registros']) if patrones_horarios else None
        
        return {
            'patrones_horarios': patrones_horarios,
            'hora_mayor_actividad': hora_max_actividad[0] if hora_max_actividad else None,
            'variacion_diaria': self._calcular_variacion_diaria(logs_por_hora)
        }
    
    def _calcular_variacion_diaria(self, logs_por_hora: Dict[int, List[Log]]) -> Dict[str, float]:
        """Calcula la variación de variables a lo largo del día"""
        temps_por_hora = []
        for hora in range(24):
            if hora in logs_por_hora and logs_por_hora[hora]:
                temp_promedio = statistics.mean(log.temperatura for log in logs_por_hora[hora])
                temps_por_hora.append(temp_promedio)
        
        return {
            'variacion_temperatura': round(max(temps_por_hora) - min(temps_por_hora), 2) if temps_por_hora else 0,
            'horas_con_datos': len(temps_por_hora)
        }
    
    def _calcular_volatilidad(self, logs: List[Log]) -> Dict[str, Any]:
        """Calcula la volatilidad de las variables"""
        if len(logs) < 2:
            return {}
        
        # Calcular cambios entre mediciones consecutivas
        cambios_temp = []
        cambios_hum = []
        cambios_co2 = []
        
        for i in range(1, len(logs)):
            cambios_temp.append(abs(logs[i].temperatura - logs[i-1].temperatura))
            cambios_hum.append(abs(logs[i].humedad - logs[i-1].humedad))
            cambios_co2.append(abs(logs[i].co2 - logs[i-1].co2))
        
        return {
            'volatilidad_temperatura': round(statistics.mean(cambios_temp), 2),
            'volatilidad_humedad': round(statistics.mean(cambios_hum), 2),
            'volatilidad_co2': round(statistics.mean(cambios_co2), 2),
            'estabilidad_general': self._evaluar_estabilidad(cambios_temp, cambios_hum, cambios_co2)
        }
    
    def _evaluar_estabilidad(self, cambios_temp: List[float], cambios_hum: List[float], cambios_co2: List[float]) -> str:
        """Evalúa la estabilidad general del sistema"""
        vol_temp = statistics.mean(cambios_temp)
        vol_hum = statistics.mean(cambios_hum)
        vol_co2 = statistics.mean(cambios_co2)
        
        # Umbrales de estabilidad
        if vol_temp < 0.5 and vol_hum < 2.0 and vol_co2 < 50:
            return "Muy estable"
        elif vol_temp < 1.0 and vol_hum < 5.0 and vol_co2 < 100:
            return "Estable"
        elif vol_temp < 2.0 and vol_hum < 10.0 and vol_co2 < 200:
            return "Moderadamente variable"
        else:
            return "Altamente variable"
    
    def _detectar_ciclos(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta ciclos simples en los datos"""
        # Implementación simplificada: buscar patrones de subida/bajada
        if len(logs) < 10:
            return {'mensaje': 'Datos insuficientes para detectar ciclos'}
        
        # Analizar temperatura como proxy para ciclos
        temperaturas = [log.temperatura for log in logs]
        
        # Detectar picos y valles simples
        picos = 0
        valles = 0
        
        for i in range(1, len(temperaturas) - 1):
            if temperaturas[i] > temperaturas[i-1] and temperaturas[i] > temperaturas[i+1]:
                picos += 1
            elif temperaturas[i] < temperaturas[i-1] and temperaturas[i] < temperaturas[i+1]:
                valles += 1
        
        return {
            'picos_detectados': picos,
            'valles_detectados': valles,
            'frecuencia_ciclos': f"Aproximadamente {(picos + valles) / (len(logs) / 10):.1f} cambios por decena de mediciones" if logs else "N/A"
        }
    
    def _generar_predicciones_simples(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera predicciones muy básicas basadas en tendencias"""
        if len(logs) < 5:
            return {'mensaje': 'Datos insuficientes para predicciones'}
        
        # Tomar últimas 5 mediciones para calcular tendencia
        ultimos_logs = logs[-5:]
        
        # Tendencia de temperatura
        temps = [log.temperatura for log in ultimos_logs]
        pendiente_temp = (temps[-1] - temps[0]) / len(temps)
        
        # Predicción simple: extrapolar tendencia
        pred_temp = temps[-1] + pendiente_temp * 3  # 3 períodos adelante
        
        # Nivel de confianza basado en volatilidad
        volatilidad_temp = statistics.stdev(temps) if len(temps) > 1 else 0
        confianza = "Alta" if volatilidad_temp < 1.0 else "Media" if volatilidad_temp < 2.0 else "Baja"
        
        return {
            'prediccion_temperatura': {
                'valor_pronosticado': round(pred_temp, 1),
                'confianza': confianza,
                'metodo': 'Extrapolación lineal simple'
            },
            'recomendacion': self._generar_recomendacion_prediccion(pred_temp, logs[-1])
        }
    
    def _generar_recomendacion_prediccion(self, pred_temp: float, ultimo_log: Log) -> str:
        """Genera recomendación basada en predicción"""
        if pred_temp > settings.TEMP_MAX:
            return "⚠️ Se prevé temperatura alta - verificar sistema de climatización"
        elif pred_temp < settings.TEMP_MIN:
            return "🧊 Se prevé temperatura baja - revisar calefacción"
        elif abs(pred_temp - ultimo_log.temperatura) > 3:
            return "📊 Se prevé cambio significativo de temperatura - monitorear de cerca"
        else:
            return "✅ Condiciones de temperatura estables previstas"
    
    def _detectar_anomalias_temporales(self, logs: List[Log]) -> Dict[str, Any]:
        """Detecta anomalías en la secuencia temporal"""
        anomalias = []
        
        for i in range(1, len(logs)):
            log_actual = logs[i]
            log_anterior = logs[i-1]
            
            # Detectar saltos temporales grandes
            diff_tiempo = (log_actual.timestamp - log_anterior.timestamp).total_seconds()
            if diff_tiempo > 600:  # Más de 10 minutos
                anomalias.append({
                    'tipo': 'gap_temporal',
                    'timestamp': log_actual.timestamp.isoformat(),
                    'gap_segundos': diff_tiempo
                })
            
            # Detectar cambios bruscos en variables
            diff_temp = abs(log_actual.temperatura - log_anterior.temperatura)
            if diff_temp > 5:  # Cambio mayor a 5°C
                anomalias.append({
                    'tipo': 'cambio_brusco_temperatura',
                    'timestamp': log_actual.timestamp.isoformat(),
                    'cambio': diff_temp
                })
        
        return {
            'total_anomalias': len(anomalias),
            'anomalias': anomalias[:10],  # Máximo 10 para no saturar el reporte
            'tipos_frecuentes': Counter(anomalia['tipo'] for anomalia in anomalias)
        }
    
    def get_nombre_estrategia(self) -> str:
        return "Análisis de Tendencias Temporales"

class AnalisisComparativo(EstrategiaAnalisis):
    """
    Estrategia de análisis comparativo entre salas y períodos.
    
    Se enfoca en comparaciones relativas y ranking de salas.
    """
    
    def analizar(self, logs: List[Log]) -> Dict[str, Any]:
        """Realiza análisis comparativo entre salas"""
        if not logs:
            return {'error': 'No hay logs para analizar'}
        
        # Agrupar logs por sala
        logs_por_sala = defaultdict(list)
        for log in logs:
            logs_por_sala[log.sala].append(log)
        
        analisis = {
            'comparacion_salas': self._comparar_salas(logs_por_sala),
            'ranking_salas': self._crear_ranking_salas(logs_por_sala),
            'benchmarking': self._calcular_benchmarks(logs_por_sala),
            'variabilidad_inter_salas': self._analizar_variabilidad_salas(logs_por_sala),
            'correlaciones_salas': self._analizar_correlaciones_salas(logs_por_sala)
        }
        
        return analisis
    
    def _comparar_salas(self, logs_por_sala: Dict[str, List[Log]]) -> Dict[str, Dict[str, Any]]:
        """Compara métricas entre salas"""
        comparacion = {}
        
        for sala, logs_sala in logs_por_sala.items():
            if not logs_sala:
                continue
            
            # Calcular métricas para la sala
            temperaturas = [log.temperatura for log in logs_sala]
            humedades = [log.humedad for log in logs_sala]
            co2_levels = [log.co2 for log in logs_sala]
            
            comparacion[sala] = {
                'total_registros': len(logs_sala),
                'alertas_criticas': sum(1 for log in logs_sala if log.is_critical),
                'tasa_alertas': round(sum(1 for log in logs_sala if log.is_critical) / len(logs_sala) * 100, 1),
                'temperatura_promedio': round(statistics.mean(temperaturas), 2),
                'humedad_promedio': round(statistics.mean(humedades), 2),
                'co2_promedio': round(statistics.mean(co2_levels), 2),
                'variabilidad_temperatura': round(statistics.stdev(temperaturas) if len(temperaturas) > 1 else 0, 2),
                'condicion_general': self._evaluar_condicion_sala(logs_sala)
            }
        
        return comparacion
    
    def _evaluar_condicion_sala(self, logs_sala: List[Log]) -> str:
        """Evalúa la condición general de una sala"""
        total = len(logs_sala)
        criticos = sum(1 for log in logs_sala if log.is_critical)
        tasa_criticos = criticos / total if total > 0 else 0
        
        if tasa_criticos >= 0.3:
            return "Crítica"
        elif tasa_criticos >= 0.1:
            return "Atención requerida"
        elif tasa_criticos > 0:
            return "Estable con alertas menores"
        else:
            return "Excelente"
    
    def _crear_ranking_salas(self, logs_por_sala: Dict[str, List[Log]]) -> Dict[str, List[Dict[str, Any]]]:
        """Crea rankings de salas por diferentes criterios"""
        
        # Calcular scores para cada sala
        scores_salas = []
        
        for sala, logs_sala in logs_por_sala.items():
            if not logs_sala:
                continue
            
            # Score basado en múltiples factores
            tasa_criticos = sum(1 for log in logs_sala if log.is_critical) / len(logs_sala)
            temp_promedio = statistics.mean(log.temperatura for log in logs_sala)
            co2_promedio = statistics.mean(log.co2 for log in logs_sala)
            
            # Score de calidad (menor es mejor)
            score_calidad = (
                tasa_criticos * 100 +  # Penalización por alertas críticas
                abs(temp_promedio - 22) * 2 +  # Penalización por desviación de temperatura ideal
                max(0, co2_promedio - 600) / 10  # Penalización por CO2 alto
            )
            
            scores_salas.append({
                'sala': sala,
                'score_calidad': round(score_calidad, 2),
                'tasa_criticos': round(tasa_criticos * 100, 1),
                'temperatura_promedio': round(temp_promedio, 2),
                'co2_promedio': round(co2_promedio, 2)
            })
        
        # Crear rankings
        ranking_calidad = sorted(scores_salas, key=lambda x: x['score_calidad'])
        ranking_alertas = sorted(scores_salas, key=lambda x: x['tasa_criticos'], reverse=True)
        ranking_temperatura = sorted(scores_salas, key=lambda x: abs(x['temperatura_promedio'] - 22))
        
        return {
            'mejor_calidad_general': ranking_calidad,
            'mas_alertas_criticas': ranking_alertas,
            'mejor_temperatura': ranking_temperatura
        }
    
    def _calcular_benchmarks(self, logs_por_sala: Dict[str, List[Log]]) -> Dict[str, Any]:
        """Calcula benchmarks del sistema"""
        todas_temps = []
        todas_hums = []
        todos_co2 = []
        
        for logs_sala in logs_por_sala.values():
            todas_temps.extend(log.temperatura for log in logs_sala)
            todas_hums.extend(log.humedad for log in logs_sala)
            todos_co2.extend(log.co2 for log in logs_sala)
        
        if not todas_temps:
            return {}
        
        return {
            'benchmarks_sistema': {
                'temperatura_objetivo': 22.0,
                'temperatura_promedio_sistema': round(statistics.mean(todas_temps), 2),
                'humedad_objetivo': 50.0,
                'humedad_promedio_sistema': round(statistics.mean(todas_hums), 2),
                'co2_objetivo': 600,
                'co2_promedio_sistema': round(statistics.mean(todos_co2), 2)
            },
            'salas_sobre_benchmark': self._salas_sobre_benchmark(logs_por_sala),
            'mejores_practicas': self._identificar_mejores_practicas(logs_por_sala)
        }
    
    def _salas_sobre_benchmark(self, logs_por_sala: Dict[str, List[Log]]) -> List[str]:
        """Identifica salas que superan los benchmarks"""
        salas_destacadas = []
        
        for sala, logs_sala in logs_por_sala.items():
            if not logs_sala:
                continue
            
            temp_prom = statistics.mean(log.temperatura for log in logs_sala)
            co2_prom = statistics.mean(log.co2 for log in logs_sala)
            tasa_criticos = sum(1 for log in logs_sala if log.is_critical) / len(logs_sala)
            
            # Criterios para estar "sobre benchmark"
            if (20 <= temp_prom <= 24 and  # Temperatura en rango ideal
                co2_prom <= 700 and  # CO2 bajo
                tasa_criticos <= 0.05):  # Menos del 5% de alertas críticas
                salas_destacadas.append(sala)
        
        return salas_destacadas
    
    def _identificar_mejores_practicas(self, logs_por_sala: Dict[str, List[Log]]) -> List[str]:
        """Identifica mejores prácticas basadas en los datos"""
        practicas = []
        
        # Encontrar la sala con mejor desempeño
        mejor_sala = None
        mejor_score = float('inf')
        
        for sala, logs_sala in logs_por_sala.items():
            if len(logs_sala) < 10:  # Mínimo de datos
                continue
            
            tasa_criticos = sum(1 for log in logs_sala if log.is_critical) / len(logs_sala)
            if tasa_criticos < mejor_score:
                mejor_score = tasa_criticos
                mejor_sala = sala
        
        if mejor_sala:
            practicas.append(f"Replicar condiciones de operación de {mejor_sala} (menor tasa de alertas)")
        
        # Analizar correlaciones temporales
        for sala, logs_sala in logs_por_sala.items():
            if len(logs_sala) < 20:
                continue
            
            # Verificar si hay patrones de mejora
            primera_mitad = logs_sala[:len(logs_sala)//2]
            segunda_mitad = logs_sala[len(logs_sala)//2:]
            
            tasa_primera = sum(1 for log in primera_mitad if log.is_critical) / len(primera_mitad)
            tasa_segunda = sum(1 for log in segunda_mitad if log.is_critical) / len(segunda_mitad)
            
            if tasa_segunda < tasa_primera * 0.7:  # Mejora significativa
                practicas.append(f"Investigar cambios implementados en {sala} - mejora del {((tasa_primera - tasa_segunda) / tasa_primera * 100):.1f}%")
        
        return practicas[:5]  # Máximo 5 prácticas
    
    def _analizar_variabilidad_salas(self, logs_por_sala: Dict[str, List[Log]]) -> Dict[str, Any]:
        """Analiza la variabilidad entre salas"""
        promedios_temp = []
        promedios_hum = []
        promedios_co2 = []
        
        for logs_sala in logs_por_sala.values():
            if logs_sala:
                promedios_temp.append(statistics.mean(log.temperatura for log in logs_sala))
                promedios_hum.append(statistics.mean(log.humedad for log in logs_sala))
                promedios_co2.append(statistics.mean(log.co2 for log in logs_sala))
        
        return {
            'variabilidad_temperatura': round(statistics.stdev(promedios_temp) if len(promedios_temp) > 1 else 0, 2),
            'variabilidad_humedad': round(statistics.stdev(promedios_hum) if len(promedios_hum) > 1 else 0, 2),
            'variabilidad_co2': round(statistics.stdev(promedios_co2) if len(promedios_co2) > 1 else 0, 2),
            'homogeneidad_sistema': self._evaluar_homogeneidad(promedios_temp, promedios_hum, promedios_co2)
        }
    
    def _evaluar_homogeneidad(self, temps: List[float], hums: List[float], co2s: List[float]) -> str:
        """Evalúa la homogeneidad del sistema"""
        if not temps:
            return "No evaluable"
        
        var_temp = statistics.stdev(temps) if len(temps) > 1 else 0
        var_hum = statistics.stdev(hums) if len(hums) > 1 else 0
        var_co2 = statistics.stdev(co2s) if len(co2s) > 1 else 0
        
        # Umbrales para evaluar homogeneidad
        if var_temp < 1.0 and var_hum < 5.0 and var_co2 < 100:
            return "Sistema muy homogéneo"
        elif var_temp < 2.0 and var_hum < 10.0 and var_co2 < 200:
            return "Sistema homogéneo"
        elif var_temp < 3.0 and var_hum < 15.0 and var_co2 < 300:
            return "Variabilidad moderada"
        else:
            return "Alta variabilidad entre salas"
    
    def _analizar_correlaciones_salas(self, logs_por_sala: Dict[str, List[Log]]) -> Dict[str, Any]:
        """Analiza correlaciones en el comportamiento de las salas"""
        if len(logs_por_sala) < 2:
            return {'mensaje': 'Necesarias al menos 2 salas para análisis de correlaciones'}
        
        # Simplificado: analizar si las salas tienden a tener problemas al mismo tiempo
        salas_con_suficientes_datos = {
            sala: logs_sala for sala, logs_sala in logs_por_sala.items() 
            if len(logs_sala) >= 10
        }
        
        if len(salas_con_suficientes_datos) < 2:
            return {'mensaje': 'Datos insuficientes para correlaciones'}
        
        # Calcular correlación de alertas críticas entre salas
        correlaciones = []
        salas_lista = list(salas_con_suficientes_datos.keys())
        
        for i in range(len(salas_lista)):
            for j in range(i + 1, len(salas_lista)):
                sala1 = salas_lista[i]
                sala2 = salas_lista[j]
                
                # Simplificado: contar alertas por hora
                alertas_sala1 = self._contar_alertas_por_hora(salas_con_suficientes_datos[sala1])
                alertas_sala2 = self._contar_alertas_por_hora(salas_con_suficientes_datos[sala2])
                
                # Correlación simple
                horas_comunes = set(alertas_sala1.keys()) & set(alertas_sala2.keys())
                if len(horas_comunes) >= 5:
                    valores1 = [alertas_sala1[hora] for hora in horas_comunes]
                    valores2 = [alertas_sala2[hora] for hora in horas_comunes]
                    
                    try:
                        corr = statistics.correlation(valores1, valores2) if len(valores1) > 1 else 0
                        correlaciones.append({
                            'salas': f"{sala1} - {sala2}",
                            'correlacion': round(corr, 3)
                        })
                    except:
                        pass
        
        return {
            'correlaciones_alertas': correlaciones,
            'interpretacion': self._interpretar_correlaciones(correlaciones)
        }
    
    def _contar_alertas_por_hora(self, logs_sala: List[Log]) -> Dict[int, int]:
        """Cuenta alertas críticas por hora del día"""
        alertas_por_hora = defaultdict(int)
        
        for log in logs_sala:
            if log.is_critical:
                hora = log.timestamp.hour
                alertas_por_hora[hora] += 1
        
        return dict(alertas_por_hora)
    
    def _interpretar_correlaciones(self, correlaciones: List[Dict[str, Any]]) -> str:
        """Interpreta las correlaciones encontradas"""
        if not correlaciones:
            return "No se encontraron correlaciones significativas"
        
        correlaciones_altas = [c for c in correlaciones if c['correlacion'] > 0.7]
        correlaciones_moderadas = [c for c in correlaciones if 0.3 < c['correlacion'] <= 0.7]
        
        if correlaciones_altas:
            return f"Se detectaron {len(correlaciones_altas)} correlaciones altas - posible causa común de problemas"
        elif correlaciones_moderadas:
            return f"Se detectaron {len(correlaciones_moderadas)} correlaciones moderadas - revisar factores ambientales compartidos"
        else:
            return "Las salas muestran comportamientos independientes - problemas probablemente localizados"
    
    def get_nombre_estrategia(self) -> str:
        return "Análisis Comparativo Entre Salas"