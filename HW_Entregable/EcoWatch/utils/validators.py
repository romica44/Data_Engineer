"""
Validadores de datos para el sistema EcoWatch
"""
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from models import EstadoLog
from config.settings import settings

class DataValidator:
    """Validador genérico de datos con reglas configurables"""
    
    @staticmethod
    def validate_timestamp(timestamp_str: str) -> Tuple[bool, Optional[datetime]]:
        """
        Valida y parsea un timestamp.
        
        Returns:
            Tupla (es_valido, datetime_parseado)
        """
        if not timestamp_str:
            return False, None
        
        # Formatos soportados
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str.replace('Z', '+0000'), fmt.replace('%z', ''))
                return True, dt
            except ValueError:
                continue
        
        return False, None
    
    @staticmethod
    def validate_sala_name(sala: str) -> Tuple[bool, str]:
        """
        Valida el nombre de una sala.
        
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not sala or not isinstance(sala, str):
            return False, "Nombre de sala no puede estar vacío"
        
        sala = sala.strip()
        
        if len(sala) < 2:
            return False, "Nombre de sala debe tener al menos 2 caracteres"
        
        if len(sala) > 50:
            return False, "Nombre de sala no puede exceder 50 caracteres"
        
        # Permitir letras, números, guiones bajos y espacios
        if not re.match(r'^[a-zA-Z0-9_\s]+$', sala):
            return False, "Nombre de sala contiene caracteres inválidos"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_range(value: Any, min_val: float, max_val: float, field_name: str) -> Tuple[bool, str]:
        """
        Valida que un valor numérico esté en el rango especificado.
        
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        try:
            num_val = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número válido"
        
        if not min_val <= num_val <= max_val:
            return False, f"{field_name} debe estar entre {min_val} y {max_val}"
        
        return True, ""

class LogValidator:
    """Validador especializado para logs de monitoreo ambiental"""
    
    def __init__(self):
        self.errores: List[str] = []
    
    def validate_complete_log(self, log_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validación completa de un log con todas las reglas de negocio.
        
        Returns:
            Tupla (es_valido, lista_errores)
        """
        self.errores.clear()
        
        # Validaciones estructurales
        self._validate_required_fields(log_data)
        
        if not self.errores:  # Solo continuar si estructura es válida
            # Validaciones de contenido
            self._validate_timestamp(log_data.get('timestamp'))
            self._validate_sala(log_data.get('sala'))
            self._validate_estado(log_data.get('estado'))
            self._validate_temperatura(log_data.get('temperatura'))
            self._validate_humedad(log_data.get('humedad'))
            self._validate_co2(log_data.get('co2'))
            self._validate_mensaje(log_data.get('mensaje'))
            
            # Validaciones de lógica de negocio
            self._validate_business_rules(log_data)
        
        return len(self.errores) == 0, self.errores.copy()
    
    def _validate_required_fields(self, log_data: Dict[str, Any]):
        """Valida que todos los campos requeridos estén presentes"""
        required_fields = {'timestamp', 'sala', 'estado', 'temperatura', 'humedad', 'co2', 'mensaje'}
        
        missing_fields = required_fields - set(log_data.keys())
        if missing_fields:
            self.errores.append(f"Campos faltantes: {', '.join(missing_fields)}")
        
        # Verificar valores no vacíos
        for field in required_fields:
            if field in log_data:
                value = log_data[field]
                if value is None or (isinstance(value, str) and not value.strip()):
                    self.errores.append(f"Campo '{field}' no puede estar vacío")
    
    def _validate_timestamp(self, timestamp):
        """Valida el timestamp del log"""
        if timestamp:
            is_valid, parsed_dt = DataValidator.validate_timestamp(str(timestamp))
            if not is_valid:
                self.errores.append("Formato de timestamp inválido")
            elif parsed_dt:
                # Verificar que no sea muy futuro (máximo 1 hora adelante)
                now = datetime.now()
                if parsed_dt > now.replace(hour=now.hour + 1):
                    self.errores.append("Timestamp no puede ser muy futuro")
    
    def _validate_sala(self, sala):
        """Valida el nombre de la sala"""
        if sala:
            is_valid, error_msg = DataValidator.validate_sala_name(str(sala))
            if not is_valid:
                self.errores.append(f"Sala inválida: {error_msg}")
    
    def _validate_estado(self, estado):
        """Valida el estado del log"""
        if estado:
            try:
                EstadoLog(str(estado).upper())
            except ValueError:
                valid_states = [e.value for e in EstadoLog]
                self.errores.append(f"Estado inválido. Valores válidos: {', '.join(valid_states)}")
    
    def _validate_temperatura(self, temperatura):
        """Valida la temperatura"""
        if temperatura is not None:
            is_valid, error_msg = DataValidator.validate_numeric_range(
                temperatura, -50, 100, "Temperatura"
            )
            if not is_valid:
                self.errores.append(error_msg)
    
    def _validate_humedad(self, humedad):
        """Valida la humedad"""
        if humedad is not None:
            is_valid, error_msg = DataValidator.validate_numeric_range(
                humedad, 0, 100, "Humedad"
            )
            if not is_valid:
                self.errores.append(error_msg)
    
    def _validate_co2(self, co2):
        """Valida el nivel de CO2"""
        if co2 is not None:
            is_valid, error_msg = DataValidator.validate_numeric_range(
                co2, 0, 10000, "CO2"
            )
            if not is_valid:
                self.errores.append(error_msg)
    
    def _validate_mensaje(self, mensaje):
        """Valida el mensaje del log"""
        if mensaje:
            mensaje_str = str(mensaje).strip()
            if len(mensaje_str) > 1000:
                self.errores.append("Mensaje no puede exceder 1000 caracteres")
    
    def _validate_business_rules(self, log_data: Dict[str, Any]):
        """Valida reglas de negocio específicas"""
        try:
            temperatura = float(log_data.get('temperatura', 0))
            humedad = float(log_data.get('humedad', 0))
            co2 = int(log_data.get('co2', 0))
            estado = str(log_data.get('estado', '')).upper()
            
            # Regla: Si temperatura o CO2 están muy altos, el estado no debería ser INFO
            if (temperatura > settings.TEMP_MAX or co2 > settings.CO2_MAX) and estado == 'INFO':
                self.errores.append("Estado inconsistente: condiciones críticas marcadas como INFO")
            
            # Regla: Combinaciones imposibles de temperatura y humedad
            if temperatura < 0 and humedad > 90:
                self.errores.append("Combinación imposible: temperatura bajo cero con humedad muy alta")
            
            # Regla: CO2 extremadamente alto debe ser ERROR
            if co2 > 2000 and estado != 'ERROR':
                self.errores.append("CO2 extremadamente alto debe marcarse como ERROR")
                
        except (ValueError, TypeError):
            # Los errores de tipo ya fueron capturados en validaciones anteriores
            pass