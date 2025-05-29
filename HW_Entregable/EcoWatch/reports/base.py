"""
Clase base abstracta para todos los reportes del sistema
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd
import json
from pathlib import Path
import logging

from models import Log
from .strategies import EstrategiaAnalisis

logger = logging.getLogger(__name__)

class ReporteBase(ABC):
    """
    Clase base abstracta para todos los reportes del sistema EcoWatch.
    
    Define la interfaz común y comportamientos base que heredarán
    todos los tipos de reportes específicos.
    
    Implementa Template Method pattern para el flujo de generación
    y Decorator pattern para funcionalidades adicionales.
    """
    
    def __init__(self, estrategia_analisis: EstrategiaAnalisis, nombre_reporte: str = ""):
        self.estrategia_analisis = estrategia_analisis
        self.nombre_reporte = nombre_reporte or self.__class__.__name__
        self.timestamp_generacion = datetime.now()
        self.metadatos = {
            'version_reporte': '1.0',
            'generado_por': 'Sistema EcoWatch',
            'timestamp': self.timestamp_generacion.isoformat()
        }
    
    @abstractmethod
    def generar(self, logs: List[Log]) -> Dict[str, Any]:
        """
        Genera el reporte específico.
        
        Args:
            logs: Lista de logs a analizar
            
        Returns:
            Diccionario con los datos del reporte
        """
        pass
    
    def generar_completo(self, logs: List[Log], incluir_metadatos: bool = True) -> Dict[str, Any]:
        """
        Template method que define el flujo completo de generación.
        
        Este método implementa el patrón Template Method, definiendo
        los pasos comunes para todos los reportes.
        """
        # Pre-procesamiento
        logs_filtrados = self._preprocesar_logs(logs)
        
        # Validación
        if not self._validar_datos(logs_filtrados):
            return self._generar_reporte_error("Datos insuficientes o inválidos")
        
        # Generación del reporte específico
        datos_reporte = self.generar(logs_filtrados)
        
        # Post-procesamiento
        reporte_final = self._postprocesar_reporte(datos_reporte)
        
        # Agregar metadatos si se solicita
        if incluir_metadatos:
            reporte_final.update({
                'metadatos': self.metadatos,
                'estadisticas_generacion': self._generar_estadisticas_generacion(logs_filtrados)
            })
        
        return reporte_final
    
    def _preprocesar_logs(self, logs: List[Log]) -> List[Log]:
        """Pre-procesamiento común de logs"""
        # Filtrar logs inválidos
        logs_validos = [log for log in logs if log and log.timestamp]
        
        # Ordenar por timestamp
        logs_ordenados = sorted(logs_validos, key=lambda x: x.timestamp)
        
        logger.debug(f"Pre-procesamiento: {len(logs_validos)}/{len(logs)} logs válidos")
        return logs_ordenados
    
    def _validar_datos(self, logs: List[Log]) -> bool:
        """Validación de datos para generación de reportes"""
        if not logs:
            logger.warning(f"No hay logs para generar {self.nombre_reporte}")
            return False
        
        # Verificar diversidad mínima de datos
        salas_unicas = len(set(log.sala for log in logs))
        if salas_unicas == 0:
            logger.warning("No hay salas identificadas en los logs")
            return False
        
        return True
    
    def _postprocesar_reporte(self, datos_reporte: Dict[str, Any]) -> Dict[str, Any]:
        """Post-procesamiento común del reporte"""
        # Agregar información común a todos los reportes
        datos_reporte.update({
            'nombre_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat(),
            'estrategia_analisis': self.estrategia_analisis.__class__.__name__
        })
        
        return datos_reporte
    
    def _generar_reporte_error(self, mensaje_error: str) -> Dict[str, Any]:
        """Genera un reporte de error"""
        return {
            'error': True,
            'mensaje': mensaje_error,
            'nombre_reporte': self.nombre_reporte,
            'timestamp_generacion': self.timestamp_generacion.isoformat()
        }
    
    def _generar_estadisticas_generacion(self, logs: List[Log]) -> Dict[str, Any]:
        """Genera estadísticas sobre el proceso de generación"""
        tiempo_generacion = datetime.now() - self.timestamp_generacion
        
        return {
            'logs_analizados': len(logs),
            'salas_incluidas': len(set(log.sala for log in logs)),
            'periodo_datos': {
                'desde': min(log.timestamp for log in logs).isoformat() if logs else None,
                'hasta': max(log.timestamp for log in logs).isoformat() if logs else None
            },
            'tiempo_generacion_ms': tiempo_generacion.total_seconds() * 1000,
            'logs_criticos': sum(1 for log in logs if log.is_critical)
        }
    
    def exportar_csv(self, datos: Dict[str, Any], archivo_path: str) -> bool:
        """
        Exporta datos del reporte a CSV usando pandas.
        
        Args:
            datos: Datos del reporte a exportar
            archivo_path: Ruta del archivo de destino
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            # Preparar datos para CSV
            datos_csv = self._preparar_datos_para_csv(datos)
            
            if not datos_csv:
                logger.warning("No hay datos para exportar a CSV")
                return False
            
            # Crear DataFrame y exportar
            df = pd.DataFrame(datos_csv)
            df.to_csv(archivo_path, index=False, encoding='utf-8')
            
            logger.info(f"📄 Reporte exportado a CSV: {archivo_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando CSV: {str(e)}")
            return False
    
    def exportar_json(self, datos: Dict[str, Any], archivo_path: str) -> bool:
        """
        Exporta datos del reporte a JSON.
        
        Args:
            datos: Datos del reporte a exportar
            archivo_path: Ruta del archivo de destino
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            with open(archivo_path, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📄 Reporte exportado a JSON: {archivo_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando JSON: {str(e)}")
            return False
    
    def exportar_excel(self, datos: Dict[str, Any], archivo_path: str) -> bool:
        """
        Exporta datos del reporte a Excel con múltiples hojas.
        
        Args:
            datos: Datos del reporte a exportar
            archivo_path: Ruta del archivo de destino
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            with pd.ExcelWriter(archivo_path, engine='openpyxl') as writer:
                # Hoja principal con resumen
                resumen_data = self._extraer_resumen_para_excel(datos)
                if resumen_data:
                    df_resumen = pd.DataFrame(resumen_data)
                    df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Hoja con datos detallados
                datos_detalle = self._preparar_datos_para_csv(datos)
                if datos_detalle:
                    df_detalle = pd.DataFrame(datos_detalle)
                    df_detalle.to_excel(writer, sheet_name='Datos_Detalle', index=False)
                
                # Hoja con metadatos
                if 'metadatos' in datos:
                    df_meta = pd.DataFrame([datos['metadatos']])
                    df_meta.to_excel(writer, sheet_name='Metadatos', index=False)
            
            logger.info(f"📊 Reporte exportado a Excel: {archivo_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando Excel: {str(e)}")
            return False
    
    def _preparar_datos_para_csv(self, datos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepara los datos del reporte para exportación CSV.
        
        Debe ser implementado por las clases hijas según su estructura específica.
        """
        # Implementación por defecto: intentar extraer datos tabulares
        if isinstance(datos, dict):
            # Buscar listas de diccionarios que se puedan tabular
            for key, value in datos.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    return value
        
        return []
    
    def _extraer_resumen_para_excel(self, datos: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae datos de resumen para la hoja de Excel"""
        if 'resumen' in datos:
            return [datos['resumen']]
        return []