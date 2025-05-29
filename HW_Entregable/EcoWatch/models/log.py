"""
Modelo Log - Representa los registros de monitoreo ambiental
Corresponde a la tabla 'logs' en MySQL
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json

class EstadoLog(Enum):
    """Estados posibles de un log ambiental"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class Log:
    """
    Modelo para registros de monitoreo ambiental
    
    Attributes:
        id: ID único del registro (auto-generado por MySQL)
        timestamp: Momento del registro
        sala: Nombre de la sala monitoreada
        estado: Estado del registro (INFO, WARNING, ERROR)
        temperatura: Temperatura en grados Celsius
        humedad: Humedad relativa en porcentaje
        co2: Niveles de CO2 en ppm
        mensaje: Mensaje descriptivo opcional
        processed_at: Timestamp de cuando fue procesado
        is_critical: Indica si es un registro crítico
    """
    
    # Campos obligatorios
    timestamp: datetime
    sala: str
    estado: EstadoLog
    temperatura: float
    humedad: float
    co2: int
    
    # Campos opcionales
    id: Optional[int] = None
    mensaje: Optional[str] = None
    processed_at: Optional[datetime] = None
    is_critical: bool = False
    
    # Metadatos adicionales
    _metadata: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Validaciones y normalizaciones después de la inicialización"""
        # Convertir string a enum si es necesario
        if isinstance(self.estado, str):
            self.estado = EstadoLog(self.estado.upper())
        
        # Validar rangos de valores
        self._validar_valores()
        
        # Determinar si es crítico automáticamente
        if not hasattr(self, '_is_critical_set'):
            self.is_critical = self._evaluar_criticidad()
    
    def _validar_valores(self):
        """Valida que los valores estén en rangos razonables"""
        if not isinstance(self.temperatura, (int, float)):
            raise ValueError(f"Temperatura debe ser numérica: {self.temperatura}")
        
        if not isinstance(self.humedad, (int, float)):
            raise ValueError(f"Humedad debe ser numérica: {self.humedad}")
        
        if not isinstance(self.co2, int):
            raise ValueError(f"CO2 debe ser entero: {self.co2}")
        
        # Rangos razonables (no estrictos, solo para detectar errores obvios)
        if not -50 <= self.temperatura <= 80:
            raise ValueError(f"Temperatura fuera de rango razonable: {self.temperatura}°C")
        
        if not 0 <= self.humedad <= 100:
            raise ValueError(f"Humedad fuera de rango: {self.humedad}%")
        
        if not 0 <= self.co2 <= 10000:
            raise ValueError(f"CO2 fuera de rango razonable: {self.co2} ppm")
        
        if self.sala and len(self.sala) > 50:
            raise ValueError(f"Nombre de sala muy largo (max 50): {len(self.sala)}")
    
    def _evaluar_criticidad(self) -> bool:
        """
        Evalúa si el registro debe marcarse como crítico
        
        Returns:
            True si es crítico, False en caso contrario
        """
        # Umbrales críticos (más estrictos que los de warning)
        temp_critica = self.temperatura < 15 or self.temperatura > 35
        humedad_critica = self.humedad < 10 or self.humedad > 90
        co2_critico = self.co2 > 1500
        estado_critico = self.estado == EstadoLog.ERROR
        
        return temp_critica or humedad_critica or co2_critico or estado_critico
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el log a diccionario para JSON/serialización
        
        Returns:
            Diccionario con todos los campos
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'sala': self.sala,
            'estado': self.estado.value if isinstance(self.estado, EstadoLog) else self.estado,
            'temperatura': self.temperatura,
            'humedad': self.humedad,
            'co2': self.co2,
            'mensaje': self.mensaje,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'is_critical': self.is_critical,
            **self._metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Log':
        """
        Crea un Log desde un diccionario
        
        Args:
            data: Diccionario con los datos del log
            
        Returns:
            Instancia de Log
        """
        # Procesar timestamp
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Procesar processed_at
        processed_at = data.get('processed_at')
        if isinstance(processed_at, str):
            processed_at = datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
        
        # Extraer campos conocidos
        campos_conocidos = {
            'id', 'timestamp', 'sala', 'estado', 'temperatura', 
            'humedad', 'co2', 'mensaje', 'processed_at', 'is_critical'
        }
        
        campos_log = {k: v for k, v in data.items() if k in campos_conocidos}
        metadata = {k: v for k, v in data.items() if k not in campos_conocidos}
        
        # Crear instancia
        log = cls(
            timestamp=timestamp,
            sala=campos_log.get('sala', ''),
            estado=campos_log.get('estado', EstadoLog.INFO),
            temperatura=float(campos_log.get('temperatura', 0)),
            humedad=float(campos_log.get('humedad', 0)),
            co2=int(campos_log.get('co2', 0)),
            id=campos_log.get('id'),
            mensaje=campos_log.get('mensaje'),
            processed_at=processed_at,
            is_critical=campos_log.get('is_critical', False)
        )
        
        # Agregar metadata
        log._metadata.update(metadata)
        
        return log
    
    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'Log':
        """
        Crea un Log desde una fila de CSV
        
        Args:
            row: Diccionario con datos de la fila CSV
            
        Returns:
            Instancia de Log
        """
        # Mapeo de nombres de columnas comunes
        column_mapping = {
            'timestamp': ['timestamp', 'fecha', 'time', 'datetime'],
            'sala': ['sala', 'room', 'location', 'ubicacion'],
            'estado': ['estado', 'status', 'level', 'severity'],
            'temperatura': ['temperatura', 'temp', 'temperature'],
            'humedad': ['humedad', 'humidity', 'humid'],
            'co2': ['co2', 'carbon_dioxide', 'dioxido_carbono'],
            'mensaje': ['mensaje', 'message', 'description', 'desc']
        }
        
        # Encontrar el nombre correcto de cada columna
        valores = {}
        for campo, posibles_nombres in column_mapping.items():
            for nombre in posibles_nombres:
                if nombre in row:
                    valores[campo] = row[nombre]
                    break
        
        # Convertir tipos
        timestamp = datetime.fromisoformat(valores.get('timestamp', datetime.now().isoformat()))
        
        return cls(
            timestamp=timestamp,
            sala=valores.get('sala', 'Unknown'),
            estado=EstadoLog(valores.get('estado', 'INFO').upper()),
            temperatura=float(valores.get('temperatura', 0)),
            humedad=float(valores.get('humedad', 0)),
            co2=int(valores.get('co2', 0)),
            mensaje=valores.get('mensaje')
        )
    
    def to_mysql_tuple(self) -> tuple:
        """
        Convierte el log a tupla para inserción en MySQL
        
        Returns:
            Tupla con valores en orden de columnas MySQL
        """
        return (
            self.timestamp,
            self.sala,
            self.estado.value,
            self.temperatura,
            self.humedad,
            self.co2,
            self.mensaje,
            self.processed_at or datetime.now(),
            self.is_critical
        )
    
    @classmethod
    def from_mysql_row(cls, row: tuple, columns: list = None) -> 'Log':
        """
        Crea un Log desde una fila de MySQL
        
        Args:
            row: Tupla con los valores de la fila
            columns: Lista opcional con nombres de columnas
            
        Returns:
            Instancia de Log
        """
        if columns is None:
            # Orden estándar de columnas en la tabla logs
            columns = [
                'id', 'timestamp', 'sala', 'estado', 'temperatura',
                'humedad', 'co2', 'mensaje', 'processed_at', 'is_critical'
            ]
        
        # Crear diccionario columna -> valor
        data = dict(zip(columns, row))
        
        return cls.from_dict(data)
    
    def calcular_confort_ambiental(self) -> Dict[str, Any]:
        """
        Calcula métricas de confort ambiental
        
        Returns:
            Diccionario con métricas de confort
        """
        # Rangos de confort (estándares internacionales)
        temp_confort = 20 <= self.temperatura <= 26
        humedad_confort = 40 <= self.humedad <= 60
        co2_confort = self.co2 <= 800
        
        # Score general (0-100)
        score = 0
        if temp_confort:
            score += 40
        elif 18 <= self.temperatura <= 28:
            score += 20
        
        if humedad_confort:
            score += 30
        elif 30 <= self.humedad <= 70:
            score += 15
        
        if co2_confort:
            score += 30
        elif self.co2 <= 1000:
            score += 15
        
        return {
            'score_confort': score,
            'temperatura_ok': temp_confort,
            'humedad_ok': humedad_confort,
            'co2_ok': co2_confort,
            'nivel_confort': 'Excelente' if score >= 80 else 
                           'Bueno' if score >= 60 else
                           'Regular' if score >= 40 else 'Malo'
        }
    
    def __str__(self) -> str:
        """Representación string legible"""
        return (f"Log({self.sala} @ {self.timestamp.strftime('%H:%M:%S')}: "
                f"{self.temperatura}°C, {self.humedad}%, {self.co2}ppm - {self.estado.value})")
    
    def __repr__(self) -> str:
        """Representación string para debugging"""
        return (f"Log(id={self.id}, sala='{self.sala}', "
                f"temp={self.temperatura}, estado={self.estado.value})")

# === FUNCIONES DE UTILIDAD ===

def crear_log_desde_sensores(temperatura: float, humedad: float, co2: int, 
                           sala: str, mensaje: str = None) -> Log:
    """
    Función de conveniencia para crear logs desde lecturas de sensores
    
    Args:
        temperatura: Temperatura en °C
        humedad: Humedad en %
        co2: CO2 en ppm
        sala: Nombre de la sala
        mensaje: Mensaje opcional
        
    Returns:
        Instancia de Log
    """
    # Determinar estado basado en valores
    estado = EstadoLog.INFO
    
    if temperatura < 18 or temperatura > 30 or humedad < 20 or humedad > 80 or co2 > 1000:
        estado = EstadoLog.WARNING
    
    if temperatura < 15 or temperatura > 35 or humedad < 10 or humedad > 90 or co2 > 1500:
        estado = EstadoLog.ERROR
    
    return Log(
        timestamp=datetime.now(),
        sala=sala,
        estado=estado,
        temperatura=temperatura,
        humedad=humedad,
        co2=co2,
        mensaje=mensaje
    )

def validar_lote_logs(logs: list) -> tuple:
    """
    Valida un lote de logs y separa válidos de inválidos
    
    Args:
        logs: Lista de logs a validar
        
    Returns:
        Tupla con (logs_válidos, logs_inválidos, errores)
    """
    validos = []
    invalidos = []
    errores = []
    
    for i, log in enumerate(logs):
        try:
            if isinstance(log, Log):
                # Re-validar por si acaso
                log._validar_valores()
                validos.append(log)
            else:
                invalidos.append((i, log, "No es instancia de Log"))
        except Exception as e:
            invalidos.append((i, log, str(e)))
            errores.append(f"Log {i}: {e}")
    
    return validos, invalidos, errores