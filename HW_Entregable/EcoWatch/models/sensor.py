"""
Modelo Sensor - Representa los sensores de monitoreo ambiental
Corresponde a la tabla 'sensores' en MySQL
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

class TipoSensor(Enum):
    """Tipos de sensores disponibles"""
    TEMPERATURA = "temperatura"
    HUMEDAD = "humedad"
    CO2 = "co2"
    MULTI = "multi"  # Sensor que mide múltiples variables

class EstadoSensor(Enum):
    """Estados operativos de un sensor"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"
    ERROR = "error"
    DESCONECTADO = "desconectado"

class CalidadSenal(Enum):
    """Calidad de señal del sensor"""
    EXCELENTE = "excelente"
    BUENA = "buena"
    REGULAR = "regular"
    MALA = "mala"
    SIN_SENAL = "sin_senal"

@dataclass
class Sensor:
    """
    Modelo para sensores de monitoreo ambiental
    
    Attributes:
        id: ID único del sensor (auto-generado por MySQL)
        id_sensor: Identificador único del sensor (hardware)
        sala_id: ID de la sala donde está instalado
        tipo: Tipo de sensor (temperatura, humedad, co2, multi)
        activo: Estado de activación del sensor
        ultima_lectura: Timestamp de la última lectura recibida
        created_at: Timestamp de creación/instalación
        estado: Estado operativo actual
        ubicacion_especifica: Ubicación específica dentro de la sala
        modelo: Modelo del sensor
        fabricante: Fabricante del sensor
    """
    
    # Campos obligatorios
    id_sensor: str
    tipo: TipoSensor
    
    # Campos opcionales con valores por defecto
    id: Optional[int] = None
    sala_id: Optional[int] = None
    activo: bool = True
    ultima_lectura: Optional[datetime] = None
    created_at: Optional[datetime] = None
    estado: EstadoSensor = EstadoSensor.ACTIVO
    ubicacion_especifica: Optional[str] = None
    modelo: Optional[str] = None
    fabricante: Optional[str] = None
    
    # Configuración y metadatos
    configuracion: Dict[str, Any] = field(default_factory=dict, repr=False)
    historial_mantenimiento: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    _metricas_rendimiento: Dict[str, float] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Validaciones y normalizaciones después de la inicialización"""
        # Validar id_sensor
        if not self.id_sensor or not self.id_sensor.strip():
            # Generar ID automático si no se proporciona
            self.id_sensor = f"sensor_{uuid.uuid4().hex[:8]}"
        
        self.id_sensor = self.id_sensor.strip()
        
        # Validar longitud del id_sensor
        if len(self.id_sensor) > 50:
            raise ValueError(f"ID de sensor muy largo (max 50): {len(self.id_sensor)}")
        
        # Convertir strings a enums si es necesario
        if isinstance(self.tipo, str):
            self.tipo = TipoSensor(self.tipo.lower())
        
        if isinstance(self.estado, str):
            self.estado = EstadoSensor(self.estado.lower())
        
        # Establecer timestamps si no existen
        if self.created_at is None:
            self.created_at = datetime.now()
        
        # Inicializar métricas de rendimiento
        self._inicializar_metricas()
        
        # Configuración por defecto según tipo
        self._configurar_por_tipo()
    
    def _inicializar_metricas(self):
        """Inicializa las métricas de rendimiento del sensor"""
        self._metricas_rendimiento.update({
            'precision': 0.0,
            'lecturas_exitosas': 0,
            'lecturas_fallidas': 0,
            'uptime_porcentaje': 100.0,
            'tiempo_respuesta_ms': 0.0
        })
    
    def _configurar_por_tipo(self):
        """Configura parámetros específicos según el tipo de sensor"""
        configuraciones_tipo = {
            TipoSensor.TEMPERATURA: {
                'rango_min': -40.0,
                'rango_max': 85.0,
                'precision': 0.1,
                'unidad': '°C',
                'intervalo_lectura_s': 30
            },
            TipoSensor.HUMEDAD: {
                'rango_min': 0.0,
                'rango_max': 100.0,
                'precision': 1.0,
                'unidad': '%RH',
                'intervalo_lectura_s': 30
            },
            TipoSensor.CO2: {
                'rango_min': 0,
                'rango_max': 10000,
                'precision': 1,
                'unidad': 'ppm',
                'intervalo_lectura_s': 60
            },
            TipoSensor.MULTI: {
                'sensores_incluidos': ['temperatura', 'humedad', 'co2'],
                'intervalo_lectura_s': 30
            }
        }
        
        if self.tipo in configuraciones_tipo:
            self.configuracion.update(configuraciones_tipo[self.tipo])
    
    def registrar_lectura(self, exitosa: bool = True):
        """Registra el resultado de una lectura"""
        self.ultima_lectura = datetime.now()
        
        if exitosa:
            self._metricas_rendimiento['lecturas_exitosas'] += 1
        else:
            self._metricas_rendimiento['lecturas_fallidas'] += 1
        
        # Calcular porcentaje de éxito
        total_lecturas = (self._metricas_rendimiento['lecturas_exitosas'] + 
                         self._metricas_rendimiento['lecturas_fallidas'])
        
        if total_lecturas > 0:
            self._metricas_rendimiento['uptime_porcentaje'] = (
                self._metricas_rendimiento['lecturas_exitosas'] / total_lecturas * 100
            )
    
    def esta_en_linea(self, timeout_minutos: int = 10) -> bool:
        """Verifica si el sensor está en línea basado en la última lectura"""
        if not self.ultima_lectura:
            return False
        
        tiempo_limite = datetime.now() - timedelta(minutes=timeout_minutos)
        return self.ultima_lectura > tiempo_limite
    
    def obtener_calidad_senal(self) -> CalidadSenal:
        """Evalúa la calidad de señal basada en métricas de rendimiento"""
        uptime = self._metricas_rendimiento.get('uptime_porcentaje', 0)
        
        if not self.esta_en_linea():
            return CalidadSenal.SIN_SENAL
        elif uptime >= 95:
            return CalidadSenal.EXCELENTE
        elif uptime >= 85:
            return CalidadSenal.BUENA
        elif uptime >= 70:
            return CalidadSenal.REGULAR
        else:
            return CalidadSenal.MALA
    
    def cambiar_estado(self, nuevo_estado: EstadoSensor, razon: str = None):
        """Cambia el estado del sensor"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Registrar cambio en historial
        cambio = {
            'timestamp': datetime.now().isoformat(),
            'estado_anterior': estado_anterior.value,
            'estado_nuevo': nuevo_estado.value,
            'razon': razon
        }
        
        if 'historial_estados' not in self.configuracion:
            self.configuracion['historial_estados'] = []
        
        self.configuracion['historial_estados'].append(cambio)
        
        # Actualizar activo según estado
        self.activo = nuevo_estado in [EstadoSensor.ACTIVO]
    
    def validar_lectura(self, valor: float, tipo_medicion: str = None) -> bool:
        """Valida si una lectura está dentro del rango válido"""
        # Para sensores multi, usar el tipo de medición específico
        if self.tipo == TipoSensor.MULTI and tipo_medicion:
            if tipo_medicion == 'temperatura':
                return -40 <= valor <= 85
            elif tipo_medicion == 'humedad':
                return 0 <= valor <= 100
            elif tipo_medicion == 'co2':
                return 0 <= valor <= 10000
        
        # Para sensores específicos, usar configuración
        rango_min = self.configuracion.get('rango_min', float('-inf'))
        rango_max = self.configuracion.get('rango_max', float('inf'))
        
        return rango_min <= valor <= rango_max
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el sensor a diccionario para JSON/serialización"""
        return {
            'id': self.id,
            'id_sensor': self.id_sensor,
            'sala_id': self.sala_id,
            'tipo': self.tipo.value,
            'activo': self.activo,
            'ultima_lectura': self.ultima_lectura.isoformat() if self.ultima_lectura else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'estado': self.estado.value,
            'ubicacion_especifica': self.ubicacion_especifica,
            'modelo': self.modelo,
            'fabricante': self.fabricante,
            'configuracion': self.configuracion,
            'metricas_rendimiento': self._metricas_rendimiento,
            'calidad_senal': self.obtener_calidad_senal().value,
            'en_linea': self.esta_en_linea()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sensor':
        """Crea un Sensor desde un diccionario"""
        # Procesar timestamps
        ultima_lectura = data.get('ultima_lectura')
        if isinstance(ultima_lectura, str):
            ultima_lectura = datetime.fromisoformat(ultima_lectura.replace('Z', '+00:00'))
        
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        # Crear instancia
        sensor = cls(
            id_sensor=data['id_sensor'],
            tipo=data.get('tipo', TipoSensor.MULTI),
            id=data.get('id'),
            sala_id=data.get('sala_id'),
            activo=data.get('activo', True),
            ultima_lectura=ultima_lectura,
            created_at=created_at,
            estado=data.get('estado', EstadoSensor.ACTIVO),
            ubicacion_especifica=data.get('ubicacion_especifica'),
            modelo=data.get('modelo'),
            fabricante=data.get('fabricante')
        )
        
        # Aplicar configuración y métricas si existen
        if 'configuracion' in data:
            sensor.configuracion.update(data['configuracion'])
        
        if 'metricas_rendimiento' in data:
            sensor._metricas_rendimiento.update(data['metricas_rendimiento'])
        
        return sensor
    
    def to_mysql_tuple(self) -> tuple:
        """Convierte el sensor a tupla para inserción en MySQL"""
        return (
            self.id_sensor,
            self.sala_id,
            self.tipo.value,
            self.activo,
            self.ultima_lectura,
            self.created_at or datetime.now()
        )
    
    @classmethod
    def from_mysql_row(cls, row: tuple, columns: list = None) -> 'Sensor':
        """Crea un Sensor desde una fila de MySQL"""
        if columns is None:
            # Orden estándar de columnas en la tabla sensores
            columns = [
                'id', 'id_sensor', 'sala_id', 'tipo', 'activo',
                'ultima_lectura', 'created_at'
            ]
        
        # Crear diccionario columna -> valor
        data = dict(zip(columns, row))
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        estado_str = "🟢" if self.estado == EstadoSensor.ACTIVO else "🔴"
        return f"Sensor({self.id_sensor} - {self.tipo.value} {estado_str})"
    
    def __repr__(self) -> str:
        return (f"Sensor(id={self.id}, id_sensor='{self.id_sensor}', "
                f"tipo={self.tipo.value}, sala_id={self.sala_id})")

# === FUNCIONES DE UTILIDAD ===

def crear_sensor_basico(id_sensor: str, tipo: str, sala_id: int = None) -> Sensor:
    """Función de conveniencia para crear sensores básicos"""
    return Sensor(
        id_sensor=id_sensor,
        tipo=TipoSensor(tipo.lower()),
        sala_id=sala_id
    )

def obtener_sensores_por_sala(sensores: List[Sensor], sala_id: int) -> List[Sensor]:
    """Filtra sensores por sala"""
    return [sensor for sensor in sensores if sensor.sala_id == sala_id]

def obtener_sensores_activos(sensores: List[Sensor]) -> List[Sensor]:
    """Filtra sensores activos y en línea"""
    return [sensor for sensor in sensores 
            if sensor.activo and sensor.estado == EstadoSensor.ACTIVO and sensor.esta_en_linea()]

def obtener_sensores_por_tipo(sensores: List[Sensor], tipo: TipoSensor) -> List[Sensor]:
    """Filtra sensores por tipo"""
    return [sensor for sensor in sensores if sensor.tipo == tipo]

def generar_reporte_salud_sensores(sensores: List[Sensor]) -> Dict[str, Any]:
    """Genera un reporte de salud de los sensores"""
    total = len(sensores)
    if total == 0:
        return {'total': 0, 'error': 'No hay sensores'}
    
    activos = len([s for s in sensores if s.activo])
    en_linea = len([s for s in sensores if s.esta_en_linea()])
    
    # Distribución por calidad de señal
    calidad_distribucion = {}
    for sensor in sensores:
        calidad = sensor.obtener_calidad_senal().value
        calidad_distribucion[calidad] = calidad_distribucion.get(calidad, 0) + 1
    
    return {
        'total_sensores': total,
        'activos': activos,
        'en_linea': en_linea,
        'desconectados': total - en_linea,
        'porcentaje_uptime': (en_linea / total * 100) if total > 0 else 0,
        'distribucion_calidad': calidad_distribucion,
        'timestamp_reporte': datetime.now().isoformat()
    }