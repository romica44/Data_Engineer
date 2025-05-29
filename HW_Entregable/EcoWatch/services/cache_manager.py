"""
Cache Manager - Gestión de caché temporal para logs ambientales
Implementa cache FIFO con índices para búsquedas rápidas
"""

from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import threading
import logging
from dataclasses import asdict

from models import Log

class CacheTemporalManager:
    """
    Manager de caché temporal para logs ambientales
    Utiliza deque para FIFO automático e índices para búsquedas O(1)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Implementación Singleton thread-safe"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, duracion_minutos: int = 5, max_size: int = 1000):
        """
        Inicializa el cache manager
        
        Args:
            duracion_minutos: Duración del caché en minutos
            max_size: Tamaño máximo del caché
        """
        # Evitar reinicialización en Singleton
        if hasattr(self, '_initialized'):
            return
            
        self.duracion_minutos = duracion_minutos
        self.max_size = max_size
        self.logger = logging.getLogger(__name__)
        
        # Estructura principal de datos (FIFO)
        self._cache = deque(maxlen=max_size)
        
        # Índices para búsquedas rápidas
        self._index_por_sala = defaultdict(list)
        self._index_por_timestamp = defaultdict(list)
        self._index_por_estado = defaultdict(list)
        
        # Métricas del caché
        self._stats = {
            'hits': 0,
            'misses': 0,
            'total_inserciones': 0,
            'cleanup_count': 0,
            'last_cleanup': datetime.now()
        }
        
        # Lock para operaciones thread-safe
        self._cache_lock = threading.RLock()
        
        self._initialized = True
        self.logger.info(f"CacheTemporalManager inicializado: {duracion_minutos}min, max_size={max_size}")
    
    def agregar_log(self, log: Log) -> bool:
        """
        Agrega un nuevo log al caché
        
        Args:
            log: Log a agregar
            
        Returns:
            True si se agregó exitosamente
        """
        try:
            with self._cache_lock:
                # Cleanup automático si es necesario
                self._cleanup_si_necesario()
                
                # Agregar al cache principal
                self._cache.append(log)
                
                # Actualizar índices
                self._actualizar_indices(log, operacion='agregar')
                
                # Actualizar estadísticas
                self._stats['total_inserciones'] += 1
                
                self.logger.debug(f"Log agregado al caché: {log.sala} @ {log.timestamp}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error al agregar log al caché: {e}")
            return False
    
    def obtener_logs_recientes(self, minutos: int = None) -> List[Log]:
        """
        Obtiene logs de los últimos N minutos
        
        Args:
            minutos: Minutos hacia atrás (None = usar duración del caché)
            
        Returns:
            Lista de logs recientes
        """
        try:
            with self._cache_lock:
                minutos = minutos or self.duracion_minutos
                tiempo_limite = datetime.now() - timedelta(minutes=minutos)
                
                logs_recientes = [
                    log for log in self._cache 
                    if log.timestamp >= tiempo_limite
                ]
                
                self._stats['hits'] += 1
                self.logger.debug(f"Obtenidos {len(logs_recientes)} logs recientes")
                return logs_recientes
                
        except Exception as e:
            self.logger.error(f"Error al obtener logs recientes: {e}")
            self._stats['misses'] += 1
            return []
    
    def obtener_por_sala(self, sala: str, minutos: int = None) -> List[Log]:
        """
        Obtiene logs de una sala específica
        
        Args:
            sala: Nombre de la sala
            minutos: Minutos hacia atrás (None = usar duración del caché)
            
        Returns:
            Lista de logs de la sala
        """
        try:
            with self._cache_lock:
                minutos = minutos or self.duracion_minutos
                tiempo_limite = datetime.now() - timedelta(minutes=minutos)
                
                # Usar índice para búsqueda rápida
                logs_sala = [
                    log for log in self._index_por_sala[sala]
                    if log.timestamp >= tiempo_limite
                ]
                
                self._stats['hits'] += 1
                self.logger.debug(f"Obtenidos {len(logs_sala)} logs para sala {sala}")
                return logs_sala
                
        except Exception as e:
            self.logger.error(f"Error al obtener logs por sala {sala}: {e}")
            self._stats['misses'] += 1
            return []
    
    def obtener_ultimo_por_sala(self, sala: str) -> Optional[Log]:
        """
        Obtiene el último log de una sala específica
        
        Args:
            sala: Nombre de la sala
            
        Returns:
            Último log de la sala o None
        """
        try:
            with self._cache_lock:
                logs_sala = self._index_por_sala[sala]
                if logs_sala:
                    # Los logs están ordenados por timestamp, devolver el último
                    ultimo_log = max(logs_sala, key=lambda x: x.timestamp)
                    self._stats['hits'] += 1
                    return ultimo_log
                
                self._stats['misses'] += 1
                return None
                
        except Exception as e:
            self.logger.error(f"Error al obtener último log por sala {sala}: {e}")
            self._stats['misses'] += 1
            return None
    
    def obtener_por_estado(self, estado: str, minutos: int = None) -> List[Log]:
        """
        Obtiene logs por estado (INFO, WARNING, ERROR)
        
        Args:
            estado: Estado de los logs
            minutos: Minutos hacia atrás
            
        Returns:
            Lista de logs con el estado especificado
        """
        try:
            with self._cache_lock:
                minutos = minutos or self.duracion_minutos
                tiempo_limite = datetime.now() - timedelta(minutes=minutos)
                
                logs_estado = [
                    log for log in self._index_por_estado[estado.upper()]
                    if log.timestamp >= tiempo_limite
                ]
                
                self._stats['hits'] += 1
                return logs_estado
                
        except Exception as e:
            self.logger.error(f"Error al obtener logs por estado {estado}: {e}")
            self._stats['misses'] += 1
            return []
    
    def obtener_alertas_criticas(self, minutos: int = None) -> List[Log]:
        """
        Obtiene logs marcados como críticos
        
        Args:
            minutos: Minutos hacia atrás
            
        Returns:
            Lista de logs críticos
        """
        try:
            with self._cache_lock:
                minutos = minutos or self.duracion_minutos
                tiempo_limite = datetime.now() - timedelta(minutes=minutos)
                
                logs_criticos = [
                    log for log in self._cache
                    if log.is_critical and log.timestamp >= tiempo_limite
                ]
                
                self._stats['hits'] += 1
                return logs_criticos
                
        except Exception as e:
            self.logger.error(f"Error al obtener alertas críticas: {e}")
            self._stats['misses'] += 1
            return []
    
    def limpiar_cache(self) -> int:
        """
        Limpia el caché manualmente
        
        Returns:
            Número de elementos eliminados
        """
        try:
            with self._cache_lock:
                elementos_antes = len(self._cache)
                
                self._cache.clear()
                self._index_por_sala.clear()
                self._index_por_timestamp.clear()
                self._index_por_estado.clear()
                
                self._stats['cleanup_count'] += 1
                self._stats['last_cleanup'] = datetime.now()
                
                elementos_eliminados = elementos_antes
                self.logger.info(f"Cache limpiado: {elementos_eliminados} elementos eliminados")
                return elementos_eliminados
                
        except Exception as e:
            self.logger.error(f"Error al limpiar caché: {e}")
            return 0
    
    def _cleanup_si_necesario(self):
        """Realiza cleanup automático si el caché está lleno"""
        if len(self._cache) >= self.max_size * 0.9:  # Cleanup al 90% de capacidad
            self._cleanup_logs_antiguos()
    
    def _cleanup_logs_antiguos(self):
        """Elimina logs antiguos fuera del período de caché"""
        try:
            tiempo_limite = datetime.now() - timedelta(minutes=self.duracion_minutos)
            
            # Filtrar logs que están dentro del período
            logs_validos = [log for log in self._cache if log.timestamp >= tiempo_limite]
            
            # Reconstruir caché e índices
            self._cache.clear()
            self._cache.extend(logs_validos)
            
            self._reconstruir_indices()
            
            self._stats['cleanup_count'] += 1
            self._stats['last_cleanup'] = datetime.now()
            
            self.logger.debug(f"Cleanup automático: {len(logs_validos)} logs conservados")
            
        except Exception as e:
            self.logger.error(f"Error en cleanup automático: {e}")
    
    def _actualizar_indices(self, log: Log, operacion: str = 'agregar'):
        """Actualiza los índices después de agregar/eliminar un log"""
        try:
            if operacion == 'agregar':
                # Agregar a índices
                self._index_por_sala[log.sala].append(log)
                
                # Crear clave temporal (hora:minuto)
                timestamp_key = log.timestamp.strftime('%H:%M')
                self._index_por_timestamp[timestamp_key].append(log)
                
                # Índice por estado
                estado_value = log.estado.value if hasattr(log.estado, 'value') else str(log.estado)
                self._index_por_estado[estado_value].append(log)
                
        except Exception as e:
            self.logger.error(f"Error al actualizar índices: {e}")
    
    def _reconstruir_indices(self):
        """Reconstruye todos los índices desde cero"""
        try:
            # Limpiar índices existentes
            self._index_por_sala.clear()
            self._index_por_timestamp.clear()
            self._index_por_estado.clear()
            
            # Reconstruir desde el caché actual
            for log in self._cache:
                self._actualizar_indices(log, 'agregar')
                
        except Exception as e:
            self.logger.error(f"Error al reconstruir índices: {e}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            with self._cache_lock:
                total_requests = self._stats['hits'] + self._stats['misses']
                hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                
                # Distribución por sala
                distribucion_salas = {
                    sala: len(logs) for sala, logs in self._index_por_sala.items()
                }
                
                # Distribución por estado
                distribucion_estados = {
                    estado: len(logs) for estado, logs in self._index_por_estado.items()
                }
                
                return {
                    'tamaño_actual': len(self._cache),
                    'tamaño_maximo': self.max_size,
                    'duracion_minutos': self.duracion_minutos,
                    'hit_rate_porcentaje': round(hit_rate, 2),
                    'total_hits': self._stats['hits'],
                    'total_misses': self._stats['misses'],
                    'total_inserciones': self._stats['total_inserciones'],
                    'cleanup_count': self._stats['cleanup_count'],
                    'last_cleanup': self._stats['last_cleanup'].isoformat(),
                    'distribucion_por_sala': distribucion_salas,
                    'distribucion_por_estado': distribucion_estados,
                    'salas_activas': len(self._index_por_sala),
                    'timestamp_reporte': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def exportar_cache_completo(self) -> List[Dict[str, Any]]:
        """
        Exporta todo el contenido del caché como lista de diccionarios
        
        Returns:
            Lista de logs en formato diccionario
        """
        try:
            with self._cache_lock:
                return [log.to_dict() for log in self._cache]
                
        except Exception as e:
            self.logger.error(f"Error al exportar caché: {e}")
            return []
    
    def importar_logs(self, logs: List[Log]) -> int:
        """
        Importa una lista de logs al caché
        
        Args:
            logs: Lista de logs a importar
            
        Returns:
            Número de logs importados exitosamente
        """
        try:
            logs_importados = 0
            
            for log in logs:
                if self.agregar_log(log):
                    logs_importados += 1
            
            self.logger.info(f"Importados {logs_importados} logs al caché")
            return logs_importados
            
        except Exception as e:
            self.logger.error(f"Error al importar logs: {e}")
            return 0
    
    def reset(self):
        """Resetea completamente el caché (útil para testing)"""
        try:
            with self._cache_lock:
                self._cache.clear()
                self._index_por_sala.clear()
                self._index_por_timestamp.clear()
                self._index_por_estado.clear()
                
                # Reset de estadísticas
                self._stats = {
                    'hits': 0,
                    'misses': 0,
                    'total_inserciones': 0,
                    'cleanup_count': 0,
                    'last_cleanup': datetime.now()
                }
                
                self.logger.info("Cache reseteado completamente")
                
        except Exception as e:
            self.logger.error(f"Error al resetear caché: {e}")
    
    def __len__(self) -> int:
        """Retorna el tamaño actual del caché"""
        return len(self._cache)
    
    def __repr__(self) -> str:
        return (f"CacheTemporalManager(size={len(self._cache)}/{self.max_size}, "
                f"duracion={self.duracion_minutos}min)")

# === FUNCIONES DE UTILIDAD ===

def crear_cache_manager(duracion_minutos: int = 5, max_size: int = 1000) -> CacheTemporalManager:
    """
    Función de conveniencia para crear un cache manager
    
    Args:
        duracion_minutos: Duración del caché en minutos
        max_size: Tamaño máximo del caché
        
    Returns:
        Instancia de CacheTemporalManager
    """
    return CacheTemporalManager(duracion_minutos, max_size)

def obtener_cache_global() -> CacheTemporalManager:
    """
    Obtiene la instancia global del cache manager (Singleton)
    
    Returns:
        Instancia global de CacheTemporalManager
    """
    return CacheTemporalManager()