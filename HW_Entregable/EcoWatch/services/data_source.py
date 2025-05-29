"""
Data Sources - Fuentes de datos para el sistema EcoWatch
Implementa diferentes adaptadores para leer datos desde múltiples fuentes
"""

import csv
import json
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Protocol
import pandas as pd

from models import Log, EstadoLog, crear_log_desde_sensores

class FuenteDatos(Protocol):
    """Protocol que define la interfaz para fuentes de datos"""
    
    def leer_logs(self) -> List[Log]:
        """Lee logs desde la fuente de datos"""
        ...
    
    def validar_fuente(self) -> bool:
        """Valida que la fuente de datos esté disponible"""
        ...

class FuenteCSV:
    """
    Fuente de datos CSV para logs ambientales
    Maneja la lectura y conversión de archivos CSV a objetos Log
    """
    
    def __init__(self, archivo_csv: str, encoding: str = 'utf-8', delimiter: str = ','):
        """
        Inicializa la fuente CSV
        
        Args:
            archivo_csv: Ruta al archivo CSV
            encoding: Codificación del archivo
            delimiter: Delimitador del CSV
        """
        self.archivo_csv = Path(archivo_csv)
        self.encoding = encoding
        self.delimiter = delimiter
        self.logger = logging.getLogger(__name__)
        
        # Mapeo de columnas comunes
        self.mapeo_columnas = {
            'timestamp': ['timestamp', 'fecha', 'time', 'datetime', 'fecha_hora'],
            'sala': ['sala', 'room', 'location', 'ubicacion', 'area'],
            'estado': ['estado', 'status', 'level', 'severity', 'tipo'],
            'temperatura': ['temperatura', 'temp', 'temperature', 'celsius'],
            'humedad': ['humedad', 'humidity', 'humid', 'rh'],
            'co2': ['co2', 'carbon_dioxide', 'dioxido_carbono', 'ppm'],
            'mensaje': ['mensaje', 'message', 'description', 'desc', 'comentario']
        }
    
    def leer_logs(self) -> List[Log]:
        """
        Lee logs desde el archivo CSV
        
        Returns:
            Lista de objetos Log
        """
        try:
            if not self.validar_fuente():
                raise FileNotFoundError(f"Archivo CSV no encontrado: {self.archivo_csv}")
            
            logs = []
            
            # Leer CSV usando pandas para mejor manejo de tipos
            try:
                df = pd.read_csv(
                    self.archivo_csv, 
                    encoding=self.encoding,
                    delimiter=self.delimiter
                )
                
                # Normalizar nombres de columnas
                df_normalizado = self._normalizar_columnas(df)
                
                # Convertir cada fila a Log
                for index, row in df_normalizado.iterrows():
                    try:
                        log = self._convertir_fila_a_log(row.to_dict(), index)
                        if log:
                            logs.append(log)
                    except Exception as e:
                        self.logger.warning(f"Error al procesar fila {index}: {e}")
                        continue
                
            except Exception as e:
                # Fallback a CSV reader estándar
                self.logger.warning(f"Error con pandas, usando csv reader: {e}")
                logs = self._leer_con_csv_reader()
            
            self.logger.info(f"Leídos {len(logs)} logs desde {self.archivo_csv}")
            return logs
            
        except Exception as e:
            self.logger.error(f"Error al leer CSV {self.archivo_csv}: {e}")
            return []
    
    def _leer_con_csv_reader(self) -> List[Log]:
        """Método fallback usando csv.reader estándar"""
        logs = []
        
        with open(self.archivo_csv, 'r', encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            
            for index, row in enumerate(reader):
                try:
                    # Normalizar columnas
                    row_normalizada = self._normalizar_fila(row)
                    log = self._convertir_fila_a_log(row_normalizada, index)
                    if log:
                        logs.append(log)
                except Exception as e:
                    self.logger.warning(f"Error al procesar fila {index}: {e}")
                    continue
        
        return logs
    
    def _normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de columnas del DataFrame"""
        columnas_normalizadas = {}
        
        for columna in df.columns:
            columna_lower = columna.lower().strip()
            
            # Buscar mapeo
            for campo_estandar, posibles_nombres in self.mapeo_columnas.items():
                if columna_lower in posibles_nombres:
                    columnas_normalizadas[columna] = campo_estandar
                    break
            else:
                # Mantener nombre original si no hay mapeo
                columnas_normalizadas[columna] = columna_lower
        
        return df.rename(columns=columnas_normalizadas)
    
    def _normalizar_fila(self, row: Dict[str, str]) -> Dict[str, str]:
        """Normaliza una fila individual"""
        fila_normalizada = {}
        
        for columna, valor in row.items():
            columna_lower = columna.lower().strip()
            
            # Buscar mapeo
            for campo_estandar, posibles_nombres in self.mapeo_columnas.items():
                if columna_lower in posibles_nombres:
                    fila_normalizada[campo_estandar] = valor
                    break
            else:
                fila_normalizada[columna_lower] = valor
        
        return fila_normalizada
    
    def _convertir_fila_a_log(self, row: Dict[str, Any], index: int) -> Optional[Log]:
        """Convierte una fila del CSV a objeto Log"""
        try:
            # Procesar timestamp
            timestamp_str = row.get('timestamp', '')
            if not timestamp_str:
                # Usar timestamp actual si no hay
                timestamp = datetime.now()
            else:
                timestamp = self._parsear_timestamp(timestamp_str)
            
            # Extraer valores obligatorios
            sala = str(row.get('sala', f'Sala_Desconocida_{index}')).strip()
            
            # Convertir valores numéricos
            temperatura = self._convertir_a_float(row.get('temperatura', 0))
            humedad = self._convertir_a_float(row.get('humedad', 0))
            co2 = self._convertir_a_int(row.get('co2', 0))
            
            # Procesar estado
            estado_str = str(row.get('estado', 'INFO')).upper().strip()
            try:
                estado = EstadoLog(estado_str)
            except ValueError:
                # Estado por defecto basado en valores
                estado = self._determinar_estado_por_valores(temperatura, humedad, co2)
            
            # Mensaje opcional
            mensaje = row.get('mensaje', None)
            if mensaje:
                mensaje = str(mensaje).strip()
            
            # Crear log
            log = Log(
                timestamp=timestamp,
                sala=sala,
                estado=estado,
                temperatura=temperatura,
                humedad=humedad,
                co2=co2,
                mensaje=mensaje
            )
            
            return log
            
        except Exception as e:
            self.logger.error(f"Error al convertir fila {index} a Log: {e}")
            return None
    
    def _parsear_timestamp(self, timestamp_str: str) -> datetime:
        """Parsea diferentes formatos de timestamp"""
        formatos = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(timestamp_str.strip(), formato)
            except ValueError:
                continue
        
        # Si no se puede parsear, usar timestamp actual
        self.logger.warning(f"No se pudo parsear timestamp: {timestamp_str}")
        return datetime.now()
    
    def _convertir_a_float(self, valor: Any) -> float:
        """Convierte un valor a float de forma segura"""
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            if isinstance(valor, str):
                # Limpiar string (remover espacios, comas como separadores decimales)
                valor_limpio = valor.strip().replace(',', '.')
                return float(valor_limpio)
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _convertir_a_int(self, valor: Any) -> int:
        """Convierte un valor a int de forma segura"""
        try:
            if isinstance(valor, int):
                return valor
            if isinstance(valor, float):
                return int(valor)
            if isinstance(valor, str):
                valor_limpio = valor.strip()
                return int(float(valor_limpio))  # Convertir a float primero para manejar decimales
            return 0
        except (ValueError, TypeError):
            return 0
    
    def _determinar_estado_por_valores(self, temperatura: float, humedad: float, co2: int) -> EstadoLog:
        """Determina el estado basándose en los valores ambientales"""
        # Umbrales básicos para determinación automática
        if temperatura < 15 or temperatura > 35 or humedad < 10 or humedad > 90 or co2 > 1500:
            return EstadoLog.ERROR
        elif temperatura < 18 or temperatura > 30 or humedad < 20 or humedad > 80 or co2 > 1000:
            return EstadoLog.WARNING
        else:
            return EstadoLog.INFO
    
    def validar_fuente(self) -> bool:
        """Valida que el archivo CSV existe y es accesible"""
        return self.archivo_csv.exists() and self.archivo_csv.is_file()
    
    def obtener_info_archivo(self) -> Dict[str, Any]:
        """Obtiene información del archivo CSV"""
        if not self.validar_fuente():
            return {'error': 'Archivo no encontrado'}
        
        try:
            stat = self.archivo_csv.stat()
            
            # Leer primeras líneas para obtener columnas
            with open(self.archivo_csv, 'r', encoding=self.encoding) as file:
                reader = csv.reader(file, delimiter=self.delimiter)
                headers = next(reader, [])
                primera_fila = next(reader, [])
            
            return {
                'ruta': str(self.archivo_csv),
                'tamaño_bytes': stat.st_size,
                'ultima_modificacion': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'encoding': self.encoding,
                'delimiter': self.delimiter,
                'columnas': headers,
                'ejemplo_primera_fila': primera_fila,
                'columnas_detectadas': len(headers)
            }
            
        except Exception as e:
            return {'error': str(e)}

class FuenteJSON:
    """
    Fuente de datos JSON para logs ambientales
    """
    
    def __init__(self, archivo_json: str, encoding: str = 'utf-8'):
        """
        Inicializa la fuente JSON
        
        Args:
            archivo_json: Ruta al archivo JSON
            encoding: Codificación del archivo
        """
        self.archivo_json = Path(archivo_json)
        self.encoding = encoding
        self.logger = logging.getLogger(__name__)
    
    def leer_logs(self) -> List[Log]:
        """Lee logs desde el archivo JSON"""
        try:
            if not self.validar_fuente():
                raise FileNotFoundError(f"Archivo JSON no encontrado: {self.archivo_json}")
            
            with open(self.archivo_json, 'r', encoding=self.encoding) as file:
                data = json.load(file)
            
            logs = []
            
            # Manejar diferentes estructuras JSON
            if isinstance(data, list):
                # Array de logs
                for index, item in enumerate(data):
                    log = self._convertir_item_a_log(item, index)
                    if log:
                        logs.append(log)
            elif isinstance(data, dict):
                if 'logs' in data:
                    # {"logs": [...]}
                    for index, item in enumerate(data['logs']):
                        log = self._convertir_item_a_log(item, index)
                        if log:
                            logs.append(log)
                else:
                    # Objeto único
                    log = self._convertir_item_a_log(data, 0)
                    if log:
                        logs.append(log)
            
            self.logger.info(f"Leídos {len(logs)} logs desde {self.archivo_json}")
            return logs
            
        except Exception as e:
            self.logger.error(f"Error al leer JSON {self.archivo_json}: {e}")
            return []
    
    def _convertir_item_a_log(self, item: Dict[str, Any], index: int) -> Optional[Log]:
        """Convierte un item JSON a objeto Log"""
        try:
            # Si ya es un log válido, usar from_dict
            if all(key in item for key in ['timestamp', 'sala', 'temperatura', 'humedad', 'co2']):
                return Log.from_dict(item)
            
            # Crear log desde campos individuales
            timestamp_str = item.get('timestamp', datetime.now().isoformat())
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
            
            sala = str(item.get('sala', f'Sala_{index}'))
            temperatura = float(item.get('temperatura', 0))
            humedad = float(item.get('humedad', 0))
            co2 = int(item.get('co2', 0))
            
            estado_str = item.get('estado', 'INFO')
            estado = EstadoLog(estado_str.upper()) if isinstance(estado_str, str) else EstadoLog.INFO
            
            return Log(
                timestamp=timestamp,
                sala=sala,
                estado=estado,
                temperatura=temperatura,
                humedad=humedad,
                co2=co2,
                mensaje=item.get('mensaje')
            )
            
        except Exception as e:
            self.logger.error(f"Error al convertir item JSON {index}: {e}")
            return None
    
    def validar_fuente(self) -> bool:
        """Valida que el archivo JSON existe y es válido"""
        if not self.archivo_json.exists():
            return False
        
        try:
            with open(self.archivo_json, 'r', encoding=self.encoding) as file:
                json.load(file)
            return True
        except json.JSONDecodeError:
            return False

class FuenteSimulada:
    """
    Fuente de datos simulada para testing y demos
    Genera logs sintéticos para pruebas
    """
    
    def __init__(self, num_logs: int = 100, salas: List[str] = None, 
                 periodo_horas: int = 24, variabilidad: bool = True):
        """
        Inicializa la fuente simulada
        
        Args:
            num_logs: Número de logs a generar
            salas: Lista de nombres de salas
            periodo_horas: Período de tiempo a simular en horas
            variabilidad: Si incluir variabilidad realista
        """
        self.num_logs = num_logs
        self.salas = salas or [
            'Oficina_A', 'Oficina_B', 'Laboratorio_1', 
            'Sala_Reuniones', 'Almacen', 'Servidor'
        ]
        self.periodo_horas = periodo_horas
        self.variabilidad = variabilidad
        self.logger = logging.getLogger(__name__)
        
        # Configuraciones base por tipo de sala
        self.configs_sala = {
            'Oficina_A': {'temp_base': 22, 'humedad_base': 45, 'co2_base': 400},
            'Oficina_B': {'temp_base': 23, 'humedad_base': 50, 'co2_base': 450},
            'Laboratorio_1': {'temp_base': 20, 'humedad_base': 40, 'co2_base': 350},
            'Sala_Reuniones': {'temp_base': 24, 'humedad_base': 55, 'co2_base': 600},
            'Almacen': {'temp_base': 18, 'humedad_base': 60, 'co2_base': 300},
            'Servidor': {'temp_base': 19, 'humedad_base': 45, 'co2_base': 250}
        }
    
    def leer_logs(self) -> List[Log]:
        """Genera logs simulados"""
        try:
            logs = []
            inicio = datetime.now() - timedelta(hours=self.periodo_horas)
            
            for i in range(self.num_logs):
                # Distribuir logs uniformemente en el período
                timestamp = inicio + timedelta(
                    seconds=(self.periodo_horas * 3600 * i) / self.num_logs
                )
                
                # Seleccionar sala aleatoriamente
                sala = random.choice(self.salas)
                
                # Generar valores basados en configuración
                log = self._generar_log_para_sala(sala, timestamp)
                logs.append(log)
            
            self.logger.info(f"Generados {len(logs)} logs simulados")
            return logs
            
        except Exception as e:
            self.logger.error(f"Error al generar logs simulados: {e}")
            return []
    
    def _generar_log_para_sala(self, sala: str, timestamp: datetime) -> Log:
        """Genera un log para una sala específica"""
        config = self.configs_sala.get(sala, {
            'temp_base': 22, 'humedad_base': 45, 'co2_base': 400
        })
        
        # Valores base
        temp_base = config['temp_base']
        humedad_base = config['humedad_base']
        co2_base = config['co2_base']
        
        if self.variabilidad:
            # Añadir variaciones realistas
            
            # Variación por hora del día (oficinas más calientes por la tarde)
            hora = timestamp.hour
            factor_hora = 1 + 0.1 * abs(hora - 12) / 12  # Máximo al mediodía
            
            # Variación aleatoria
            temp_variation = random.uniform(-3, 4) * factor_hora
            humedad_variation = random.uniform(-10, 15)
            co2_variation = random.uniform(-100, 200)
            
            # Simular patrones de ocupación (CO2 más alto en horario laboral)
            if 8 <= hora <= 18:
                co2_variation += random.uniform(100, 400)
                temp_variation += random.uniform(0, 2)  # Calor humano
        else:
            temp_variation = random.uniform(-1, 1)
            humedad_variation = random.uniform(-5, 5)
            co2_variation = random.uniform(-50, 50)
        
        # Calcular valores finales
        temperatura = round(temp_base + temp_variation, 1)
        humedad = max(0, min(100, round(humedad_base + humedad_variation, 1)))
        co2 = max(0, int(co2_base + co2_variation))
        
        # Determinar estado basado en valores
        estado = self._determinar_estado(temperatura, humedad, co2)
        
        # Mensaje ocasional
        mensaje = None
        if random.random() < 0.1:  # 10% de probabilidad de mensaje
            mensajes_posibles = [
                "Lectura automática",
                "Sistema funcionando normalmente",
                "Verificación periódica",
                "Monitoreo continuo"
            ]
            if estado != EstadoLog.INFO:
                mensajes_posibles.extend([
                    "Condiciones fuera del rango óptimo",
                    "Requiere atención",
                    "Verificar sistema HVAC"
                ])
            mensaje = random.choice(mensajes_posibles)
        
        return Log(
            timestamp=timestamp,
            sala=sala,
            estado=estado,
            temperatura=temperatura,
            humedad=humedad,
            co2=co2,
            mensaje=mensaje
        )
    
    def _determinar_estado(self, temperatura: float, humedad: float, co2: int) -> EstadoLog:
        """Determina el estado basándose en los valores"""
        if temperatura < 15 or temperatura > 35 or humedad < 10 or humedad > 90 or co2 > 1500:
            return EstadoLog.ERROR
        elif temperatura < 18 or temperatura > 30 or humedad < 20 or humedad > 80 or co2 > 1000:
            return EstadoLog.WARNING
        else:
            return EstadoLog.INFO
    
    def validar_fuente(self) -> bool:
        """La fuente simulada siempre está disponible"""
        return True
    
    def configurar_salas(self, nuevas_configs: Dict[str, Dict[str, float]]):
        """Configura parámetros base para las salas"""
        self.configs_sala.update(nuevas_configs)

class FuenteDatabase:
    """
    Fuente de datos desde base de datos MySQL
    Lee logs directamente desde la base de datos
    """
    
    def __init__(self, connection_manager=None, tabla: str = 'logs'):
        """
        Inicializa la fuente de base de datos
        
        Args:
            connection_manager: Manager de conexiones a la BD
            tabla: Nombre de la tabla de logs
        """
        self.connection_manager = connection_manager
        self.tabla = tabla
        self.logger = logging.getLogger(__name__)
    
    def leer_logs(self, limite: int = None, desde: datetime = None, 
                  hasta: datetime = None, salas: List[str] = None) -> List[Log]:
        """
        Lee logs desde la base de datos
        
        Args:
            limite: Número máximo de logs a leer
            desde: Timestamp de inicio
            hasta: Timestamp de fin
            salas: Lista de salas a filtrar
            
        Returns:
            Lista de logs desde la base de datos
        """
        try:
            if not self.validar_fuente():
                raise ConnectionError("No se puede conectar a la base de datos")
            
            # Construir query
            query = f"SELECT * FROM {self.tabla}"
            condiciones = []
            parametros = []
            
            if desde:
                condiciones.append("timestamp >= %s")
                parametros.append(desde)
            
            if hasta:
                condiciones.append("timestamp <= %s")
                parametros.append(hasta)
            
            if salas:
                placeholders = ','.join(['%s'] * len(salas))
                condiciones.append(f"sala IN ({placeholders})")
                parametros.extend(salas)
            
            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)
            
            query += " ORDER BY timestamp DESC"
            
            if limite:
                query += f" LIMIT {limite}"
            
            # Ejecutar query
            with self.connection_manager.get_cursor() as cursor:
                cursor.execute(query, parametros)
                rows = cursor.fetchall()
                
                # Convertir filas a objetos Log
                logs = []
                for row in rows:
                    try:
                        log = Log.from_mysql_row(tuple(row.values()), list(row.keys()))
                        logs.append(log)
                    except Exception as e:
                        self.logger.warning(f"Error al convertir fila de BD: {e}")
                        continue
                
                self.logger.info(f"Leídos {len(logs)} logs desde base de datos")
                return logs
                
        except Exception as e:
            self.logger.error(f"Error al leer desde base de datos: {e}")
            return []
    
    def validar_fuente(self) -> bool:
        """Valida la conexión a la base de datos"""
        try:
            if not self.connection_manager:
                return False
            
            return self.connection_manager.test_connection()
            
        except Exception:
            return False
    
    def obtener_estadisticas_tabla(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la tabla de logs"""
        try:
            if not self.validar_fuente():
                return {'error': 'No se puede conectar a la base de datos'}
            
            with self.connection_manager.get_cursor() as cursor:
                # Contar total de registros
                cursor.execute(f"SELECT COUNT(*) as total FROM {self.tabla}")
                total = cursor.fetchone()['total']
                
                # Rango de fechas
                cursor.execute(f"SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM {self.tabla}")
                fechas = cursor.fetchone()
                
                # Distribución por sala
                cursor.execute(f"SELECT sala, COUNT(*) as count FROM {self.tabla} GROUP BY sala")
                distribucion_salas = {row['sala']: row['count'] for row in cursor.fetchall()}
                
                # Distribución por estado
                cursor.execute(f"SELECT estado, COUNT(*) as count FROM {self.tabla} GROUP BY estado")
                distribucion_estados = {row['estado']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_registros': total,
                    'fecha_inicio': fechas['min_date'].isoformat() if fechas['min_date'] else None,
                    'fecha_fin': fechas['max_date'].isoformat() if fechas['max_date'] else None,
                    'salas_distintas': len(distribucion_salas),
                    'distribucion_por_sala': distribucion_salas,
                    'distribucion_por_estado': distribucion_estados
                }
                
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {'error': str(e)}

# === FACTORY PARA FUENTES DE DATOS ===

class FactoryFuentesDatos:
    """Factory para crear diferentes tipos de fuentes de datos"""
    
    @staticmethod
    def crear_fuente(tipo: str, **kwargs) -> FuenteDatos:
        """
        Crea una fuente de datos del tipo especificado
        
        Args:
            tipo: Tipo de fuente ('csv', 'json', 'simulada', 'database')
            **kwargs: Argumentos específicos para cada tipo
            
        Returns:
            Instancia de la fuente de datos
        """
        if tipo.lower() == 'csv':
            return FuenteCSV(**kwargs)
        elif tipo.lower() == 'json':
            return FuenteJSON(**kwargs)
        elif tipo.lower() == 'simulada':
            return FuenteSimulada(**kwargs)
        elif tipo.lower() == 'database':
            return FuenteDatabase(**kwargs)
        else:
            raise ValueError(f"Tipo de fuente desconocido: {tipo}")

# === FUNCIONES DE UTILIDAD ===

def crear_fuente_csv(archivo: str) -> FuenteCSV:
    """Función de conveniencia para crear fuente CSV"""
    return FuenteCSV(archivo)

def crear_fuente_json(archivo: str) -> FuenteJSON:
    """Función de conveniencia para crear fuente JSON"""
    return FuenteJSON(archivo)

def crear_fuente_simulada(num_logs: int = 100) -> FuenteSimulada:
    """Función de conveniencia para crear fuente simulada"""
    return FuenteSimulada(num_logs=num_logs)

def crear_fuente_database(connection_manager) -> FuenteDatabase:
    """Función de conveniencia para crear fuente de base de datos"""
    return FuenteDatabase(connection_manager)