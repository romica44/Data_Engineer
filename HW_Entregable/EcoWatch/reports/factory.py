"""
Factory Pattern para la creación de reportes
"""
from enum import Enum
from typing import Dict, Any, Optional, List
import logging

from .base import ReporteBase
from .strategies import EstrategiaAnalisis, AnalisisEstadistico, AnalisisTendencias, AnalisisComparativo

logger = logging.getLogger(__name__)

class TipoReporte(Enum):
    """Tipos de reportes disponibles en el sistema"""
    ESTADO_POR_SALA = "estado_por_sala"
    ALERTAS_CRITICAS = "alertas_criticas"
    TENDENCIAS_AMBIENTALES = "tendencias_ambientales"
    RESUMEN_EJECUTIVO = "resumen_ejecutivo"
    COMPARATIVO_SALAS = "comparativo_salas"
    ANALISIS_CALIDAD = "analisis_calidad"

class FactoryReportes:
    """
    Factory para la creación de diferentes tipos de reportes.
    
    Implementa el patrón Factory Method que encapsula la lógica de creación
    de reportes y permite agregar nuevos tipos sin modificar código existente.
    
    Ventajas:
    - Desacoplamiento: El cliente no necesita conocer las clases concretas
    - Extensibilidad: Fácil adición de nuevos tipos de reportes
    - Configurabilidad: Diferentes estrategias de análisis por tipo
    - Testing: Facilita la creación de mocks y stubs
    """
    
    # Registro de reportes disponibles
    _reportes_registrados: Dict[TipoReporte, type] = {}
    
    # Estrategias por defecto para cada tipo de reporte
    _estrategias_default: Dict[TipoReporte, type] = {
        TipoReporte.ESTADO_POR_SALA: AnalisisEstadistico,
        TipoReporte.ALERTAS_CRITICAS: AnalisisEstadistico,
        TipoReporte.TENDENCIAS_AMBIENTALES: AnalisisTendencias,
        TipoReporte.RESUMEN_EJECUTIVO: AnalisisComparativo,
        TipoReporte.COMPARATIVO_SALAS: AnalisisComparativo,
        TipoReporte.ANALISIS_CALIDAD: AnalisisEstadistico
    }
    
    @classmethod
    def registrar_reporte(cls, tipo_reporte: TipoReporte, clase_reporte: type):
        """
        Registra un nuevo tipo de reporte en la factory.
        
        Permite agregar nuevos reportes dinámicamente sin modificar
        el código del factory.
        
        Args:
            tipo_reporte: Tipo de reporte a registrar
            clase_reporte: Clase que implementa el reporte
        """
        if not issubclass(clase_reporte, ReporteBase):
            raise ValueError(f"La clase {clase_reporte.__name__} debe heredar de ReporteBase")
        
        cls._reportes_registrados[tipo_reporte] = clase_reporte
        logger.info(f"✅ Reporte registrado: {tipo_reporte.value} -> {clase_reporte.__name__}")
    
    @classmethod
    def crear_reporte(cls, 
                     tipo_reporte: TipoReporte, 
                     estrategia: Optional[EstrategiaAnalisis] = None,
                     configuracion: Optional[Dict[str, Any]] = None) -> ReporteBase:
        """
        Crea un reporte del tipo especificado con la estrategia de análisis apropiada.
        
        Args:
            tipo_reporte: Tipo de reporte a crear
            estrategia: Estrategia de análisis opcional, usa default si no se especifica
            configuracion: Configuración adicional para el reporte
        
        Returns:
            Instancia del reporte solicitado
        
        Raises:
            ValueError: Si el tipo de reporte no está soportado
            TypeError: Si la estrategia no es compatible
        """
        # Verificar que el reporte esté registrado
        if tipo_reporte not in cls._reportes_registrados:
            raise ValueError(f"Tipo de reporte no registrado: {tipo_reporte.value}")
        
        # Usar estrategia por defecto si no se especifica
        if estrategia is None:
            estrategia_clase = cls._estrategias_default.get(tipo_reporte, AnalisisEstadistico)
            estrategia = estrategia_clase()
        
        # Validar que la estrategia sea compatible
        if not isinstance(estrategia, EstrategiaAnalisis):
            raise TypeError(f"La estrategia debe implementar EstrategiaAnalisis")
        
        # Obtener la clase del reporte
        clase_reporte = cls._reportes_registrados[tipo_reporte]
        
        # Crear instancia con configuración
        try:
            if configuracion:
                # Si el reporte acepta configuración en el constructor
                reporte = clase_reporte(estrategia, **configuracion)
            else:
                reporte = clase_reporte(estrategia)
            
            logger.debug(f"✅ Reporte creado: {tipo_reporte.value} con {estrategia.__class__.__name__}")
            return reporte
            
        except Exception as e:
            logger.error(f"❌ Error creando reporte {tipo_reporte.value}: {str(e)}")
            raise
    
    @classmethod
    def crear_reporte_con_estrategia_personalizada(cls,
                                                  tipo_reporte: TipoReporte,
                                                  nombre_estrategia: str,
                                                  parametros_estrategia: Dict[str, Any] = None) -> ReporteBase:
        """
        Crea un reporte con una estrategia personalizada basada en nombre.
        
        Args:
            tipo_reporte: Tipo de reporte a crear
            nombre_estrategia: Nombre de la estrategia ('estadistico', 'tendencias', 'comparativo')
            parametros_estrategia: Parámetros adicionales para la estrategia
        
        Returns:
            Instancia del reporte con estrategia personalizada
        """
        estrategias_disponibles = {
            'estadistico': AnalisisEstadistico,
            'tendencias': AnalisisTendencias,
            'comparativo': AnalisisComparativo
        }
        
        if nombre_estrategia not in estrategias_disponibles:
            raise ValueError(f"Estrategia no disponible: {nombre_estrategia}")
        
        # Crear estrategia con parámetros si los acepta
        estrategia_clase = estrategias_disponibles[nombre_estrategia]
        
        if parametros_estrategia:
            try:
                estrategia = estrategia_clase(**parametros_estrategia)
            except TypeError:
                # Si la estrategia no acepta parámetros, crear sin ellos
                estrategia = estrategia_clase()
                logger.warning(f"Estrategia {nombre_estrategia} no acepta parámetros personalizados")
        else:
            estrategia = estrategia_clase()
        
        return cls.crear_reporte(tipo_reporte, estrategia)
    
    @classmethod
    def tipos_disponibles(cls) -> List[str]:
        """Retorna lista de tipos de reportes disponibles"""
        return [tipo.value for tipo in cls._reportes_registrados.keys()]
    
    @classmethod
    def estrategias_disponibles(cls) -> List[str]:
        """Retorna lista de estrategias de análisis disponibles"""
        return ['estadistico', 'tendencias', 'comparativo']
    
    @classmethod
    def get_info_reporte(cls, tipo_reporte: TipoReporte) -> Dict[str, Any]:
        """
        Obtiene información detallada sobre un tipo de reporte.
        
        Args:
            tipo_reporte: Tipo de reporte a consultar
            
        Returns:
            Diccionario con información del reporte
        """
        if tipo_reporte not in cls._reportes_registrados:
            return {'error': f'Reporte no registrado: {tipo_reporte.value}'}
        
        clase_reporte = cls._reportes_registrados[tipo_reporte]
        estrategia_default = cls._estrategias_default.get(tipo_reporte)
        
        return {
            'tipo': tipo_reporte.value,
            'clase': clase_reporte.__name__,
            'descripcion': clase_reporte.__doc__.split('\n')[0] if clase_reporte.__doc__ else 'Sin descripción',
            'estrategia_default': estrategia_default.__name__ if estrategia_default else 'No definida',
            'estrategias_compatibles': cls.estrategias_disponibles()
        }
    
    @classmethod
    def validar_configuracion(cls, tipo_reporte: TipoReporte, configuracion: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida la configuración para un tipo de reporte específico.
        
        Args:
            tipo_reporte: Tipo de reporte a validar
            configuracion: Configuración a validar
            
        Returns:
            Tupla (es_valida, lista_errores)
        """
        errores = []
        
        if tipo_reporte not in cls._reportes_registrados:
            errores.append(f"Tipo de reporte no registrado: {tipo_reporte.value}")
            return False, errores
        
        # Validaciones específicas por tipo de reporte
        if tipo_reporte == TipoReporte.TENDENCIAS_AMBIENTALES:
            if 'periodo_minimo_horas' in configuracion:
                if not isinstance(configuracion['periodo_minimo_horas'], (int, float)) or configuracion['periodo_minimo_horas'] <= 0:
                    errores.append("periodo_minimo_horas debe ser un número positivo")
        
        elif tipo_reporte == TipoReporte.COMPARATIVO_SALAS:
            if 'salas_minimas' in configuracion:
                if not isinstance(configuracion['salas_minimas'], int) or configuracion['salas_minimas'] < 2:
                    errores.append("salas_minimas debe ser un entero >= 2")
        
        return len(errores) == 0, errores

# Auto-registro de reportes
def _registrar_reportes_default():
    """Registra los reportes por defecto del sistema"""
    # Import here to avoid circular imports
    from .implementations import (
        ReporteEstadoPorSala,
        ReporteAlertasCriticas,
        ReporteTendenciasAmbientales,
        ReporteResumenEjecutivo
    )
    
    FactoryReportes.registrar_reporte(TipoReporte.ESTADO_POR_SALA, ReporteEstadoPorSala)
    FactoryReportes.registrar_reporte(TipoReporte.ALERTAS_CRITICAS, ReporteAlertasCriticas)
    FactoryReportes.registrar_reporte(TipoReporte.TENDENCIAS_AMBIENTALES, ReporteTendenciasAmbientales)
    FactoryReportes.registrar_reporte(TipoReporte.RESUMEN_EJECUTIVO, ReporteResumenEjecutivo)

# Ejecutar registro automático
_registrar_reportes_default()