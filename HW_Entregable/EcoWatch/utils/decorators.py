# utils/decorators.py
"""
Decoradores para funcionalidades transversales del sistema EcoWatch
"""
import functools
import time
import logging
from typing import Any, Callable, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

def benchmark(func: Callable) -> Callable:
    """
    Decorador para medir el tiempo de ejecución de funciones.
    
    Útil para identificar cuellos de botella y optimizar el rendimiento.
    Registra automáticamente métricas de timing en logs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            # Log detallado para análisis de rendimiento
            logger.info(f"🚀 {func.__module__}.{func.__name__} ejecutado en {execution_time:.4f}s")
            
            # Para funciones que procesan lotes, calcular throughput
            if hasattr(result, '__len__') and len(result) > 0:
                throughput = len(result) / execution_time
                logger.info(f"📊 Throughput: {throughput:.2f} elementos/segundo")
            
            return result
            
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            logger.error(f"❌ {func.__module__}.{func.__name__} falló después de {execution_time:.4f}s: {str(e)}")
            raise
    
    return wrapper

def validate_log_data(func: Callable) -> Callable:
    """
    Decorador para validar datos de logs antes del procesamiento.
    
    Implementa el principio "fail-fast" para detectar errores
    de datos temprano en el pipeline de procesamiento.
    """
    @functools.wraps(func)
    def wrapper(self, log_data: Dict[str, Any], *args, **kwargs) -> Any:
        # Verificar que el objeto tenga el método de validación
        if not hasattr(self, '_validar_estructura_log'):
            raise AttributeError(f"Clase {self.__class__.__name__} debe implementar _validar_estructura_log")
        
        # Validar estructura del log
        if not self._validar_estructura_log(log_data):
            error_msg = f"Estructura de log inválida: {log_data}"
            logger.warning(f"⚠️ Validación fallida: {error_msg}")
            raise ValueError(error_msg)
        
        # Continuar con la ejecución si la validación es exitosa
        return func(self, log_data, *args, **kwargs)
    
    return wrapper

def log_operation(func: Callable) -> Callable:
    """
    Decorador para logging automático de operaciones del sistema.
    
    Proporciona trazabilidad completa de operaciones críticas
    con manejo estructurado de errores y logging de contexto.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Logging de inicio con contexto
        logger.info(f"🔄 Iniciando operación: {func_name}")
        
        # Capturar contexto adicional si está disponible
        context = {}
        if args and hasattr(args[0], '__class__'):
            context['clase'] = args[0].__class__.__name__
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ Operación completada: {func_name} (duración: {duration:.3f}s)")
            
            # Log adicional para operaciones que retornan métricas
            if isinstance(result, (int, float)) and result > 0:
                logger.info(f"📈 Resultado: {result} elementos procesados")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_context = {
                'funcion': func_name,
                'duracion_antes_error': duration,
                'contexto': context,
                'argumentos': len(args),
                'kwargs': list(kwargs.keys()) if kwargs else []
            }
            
            logger.error(f"❌ Error en operación {func_name}: {str(e)}", extra=error_context)
            raise
    
    return wrapper

def cache_result(ttl_seconds: int = 300):
    """
    Decorador para cachear resultados de funciones costosas.
    
    Args:
        ttl_seconds: Tiempo de vida del caché en segundos (default: 5 minutos)
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Crear clave del caché
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Verificar si el resultado está en caché y es válido
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    logger.debug(f"🎯 Cache hit para {func.__name__}")
                    return result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            logger.debug(f"💾 Resultado cacheado para {func.__name__}")
            return result
        
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """
    Decorador para reintentar operaciones que pueden fallar temporalmente.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial entre intentos
        exponential_backoff: Si usar backoff exponencial
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(f"❌ {func.__name__} falló después de {max_attempts} intentos")
                        raise last_exception
                    
                    wait_time = delay * (2 ** (attempt - 1)) if exponential_backoff else delay
                    logger.warning(f"⚠️ {func.__name__} falló (intento {attempt}/{max_attempts}), reintentando en {wait_time}s")
                    time.sleep(wait_time)
            
            raise last_exception
        
        return wrapper
    return decorator