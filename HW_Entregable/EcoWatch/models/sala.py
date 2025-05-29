"""
Modelo Sala - Representa las salas monitoreadas
Corresponde a la tabla 'salas' en MySQL
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class TipoSala(Enum):
    """Tipos de salas disponibles"""
    OFICINA = "oficina"
    LABORATORIO = "laboratorio"
    ALMACEN = "almacen"
    SALA_REUNIONES = "sala_reuniones"
    PRODUCCION = "produccion"
    SERVIDOR = "servidor"
    OTRO = "otro"

class EstadoSala(Enum):
    """Estados operativos de una sala"""
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    MANTENIMIENTO = "mantenimiento"
    FUERA_SERVICIO = "fuera_servicio"

@dataclass
class Sala:
    """
    Modelo para salas monitoreadas
    
    Attributes:
        id: ID único de la sala (auto-generado por MySQL)
        nombre: Nombre único de la sala
        ubicacion: Ubicación física de la sala
        capacidad_personas: Capacidad máxima de personas
        tipo_sala: Tipo de sala (oficina, laboratorio, etc.)
        estado: Estado operativo actual
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """
    
    # Campos obligatorios
    nombre: str
    
    # Campos opcionales con valores por defecto
    id: Optional[int] = None
    ubicacion: Optional[str] = None
    capacidad_personas: int = 0
    tipo_sala: TipoSala = TipoSala.OFICINA
    estado: EstadoSala = EstadoSala.ACTIVA
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Metadatos adicionales
    configuracion: Dict[str, Any] = field(default_factory=dict, repr=False)
    _umbrales_personalizados: Dict[str, Dict[str, float]] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Validaciones y normalizaciones después de la inicialización"""
        # Validar nombre
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre de la sala es obligatorio")
        
        self.nombre = self.nombre.strip()
        
        # Validar longitud del nombre
        if len(self.nombre) > 50:
            raise ValueError(f"Nombre de sala muy largo (max 50): {len(self.nombre)}")
        
        # Convertir strings a enums si es necesario
        if isinstance(self.tipo_sala, str):
            self.tipo_sala = TipoSala(self.tipo_sala.lower())
        
        if isinstance(self.estado, str):
            self.estado = EstadoSala(self.estado.lower())
        
        # Validar capacidad
        if self.capacidad_personas < 0:
            raise ValueError(f"Capacidad no puede ser negativa: {self.capacidad_personas}")
        
        # Establecer timestamps si no existen
        if self.created_at is None:
            self.created_at = datetime.now()
        
        self.updated_at = datetime.now()
        
        # Configurar umbrales por defecto según tipo de sala
        self._configurar_umbrales_por_tipo()
    
    def _configurar_umbrales_por_tipo(self):
        """Configura umbrales ambientales específicos según el tipo de sala"""
        umbrales_por_tipo = {
            TipoSala.OFICINA: {
                'temperatura': {'min': 20, 'max': 26},
                'humedad': {'min': 40, 'max': 60},
                'co2': {'max': 800}
            },
            TipoSala.LABORATORIO: {
                'temperatura': {'min': 18, 'max': 24},
                'humedad': {'min': 30, 'max': 50},
                'co2': {'max': 600}
            },
            TipoSala.ALMACEN: {
                'temperatura': {'min': 15, 'max': 30},
                'humedad': {'min': 20, 'max': 70},
                'co2': {'max': 1000}
            },
            TipoSala.SERVIDOR: {
                'temperatura': {'min': 18, 'max': 22},
                'humedad': {'min': 40, 'max': 55},
                'co2': {'max': 600}
            },
            TipoSala.PRODUCCION: {
                'temperatura': {'min': 16, 'max': 28},
                'humedad': {'min': 30, 'max': 70},
                'co2': {'max': 1200}
            }
        }
        
        if self.tipo_sala in umbrales_por_tipo:
            self._umbrales_personalizados = umbrales_por_tipo[self.tipo_sala]
        else:
            # Umbrales por defecto
            self._umbrales_personalizados = umbrales_por_tipo[TipoSala.OFICINA]
    
    def obtener_umbrales(self) -> Dict[str, Dict[str, float]]:
        """Obtiene los umbrales ambientales para esta sala"""
        return self._umbrales_personalizados.copy()
    
    def actualizar_umbrales(self, nuevos_umbrales: Dict[str, Dict[str, float]]):
        """Actualiza los umbrales ambientales para esta sala"""
        self._umbrales_personalizados.update(nuevos_umbrales)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sala a diccionario para JSON/serialización"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ubicacion': self.ubicacion,
            'capacidad_personas': self.capacidad_personas,
            'tipo_sala': self.tipo_sala.value,
            'estado': self.estado.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'configuracion': self.configuracion,
            'umbrales': self._umbrales_personalizados
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sala':
        """Crea una Sala desde un diccionario"""
        # Procesar timestamps
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        
        # Crear instancia
        sala = cls(
            nombre=data['nombre'],
            id=data.get('id'),
            ubicacion=data.get('ubicacion'),
            capacidad_personas=data.get('capacidad_personas', 0),
            tipo_sala=data.get('tipo_sala', TipoSala.OFICINA),
            estado=data.get('estado', EstadoSala.ACTIVA),
            created_at=created_at,
            updated_at=updated_at
        )
        
        # Aplicar configuración si existe
        if 'configuracion' in data:
            sala.configuracion.update(data['configuracion'])
        
        if 'umbrales' in data:
            sala._umbrales_personalizados.update(data['umbrales'])
        
        return sala
    
    def to_mysql_tuple(self) -> tuple:
        """Convierte la sala a tupla para inserción en MySQL"""
        return (
            self.nombre,
            self.ubicacion,
            self.capacidad_personas,
            self.created_at or datetime.now(),
            self.updated_at or datetime.now()
        )
    
    @classmethod
    def from_mysql_row(cls, row: tuple, columns: list = None) -> 'Sala':
        """Crea una Sala desde una fila de MySQL"""
        if columns is None:
            # Orden estándar de columnas en la tabla salas
            columns = [
                'id', 'nombre', 'ubicacion', 'capacidad_personas',
                'created_at', 'updated_at'
            ]
        
        # Crear diccionario columna -> valor
        data = dict(zip(columns, row))
        return cls.from_dict(data)
    
    def cambiar_estado(self, nuevo_estado: EstadoSala, razon: str = None):
        """Cambia el estado de la sala"""
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.updated_at = datetime.now()
        
        # Registrar en configuración
        if 'historial_estados' not in self.configuracion:
            self.configuracion['historial_estados'] = []
        
        self.configuracion['historial_estados'].append({
            'timestamp': datetime.now().isoformat(),
            'estado_anterior': estado_anterior.value,
            'estado_nuevo': nuevo_estado.value,
            'razon': razon
        })
    
    def __str__(self) -> str:
        return f"Sala({self.nombre} - {self.tipo_sala.value} - {self.estado.value})"
    
    def __repr__(self) -> str:
        return (f"Sala(id={self.id}, nombre='{self.nombre}', "
                f"tipo={self.tipo_sala.value}, capacidad={self.capacidad_personas})")

# === FUNCIONES DE UTILIDAD ===

def crear_sala_basica(nombre: str, tipo_sala: str = 'oficina', 
                     capacidad: int = 10, ubicacion: str = None) -> Sala:
    """Función de conveniencia para crear salas básicas"""
    return Sala(
        nombre=nombre,
        tipo_sala=TipoSala(tipo_sala.lower()),
        capacidad_personas=capacidad,
        ubicacion=ubicacion
    )

def obtener_salas_por_tipo(salas: List[Sala], tipo: TipoSala) -> List[Sala]:
    """Filtra salas por tipo"""
    return [sala for sala in salas if sala.tipo_sala == tipo]

def calcular_capacidad_total(salas: List[Sala]) -> int:
    """Calcula la capacidad total de una lista de salas"""
    return sum(sala.capacidad_personas for sala in salas)