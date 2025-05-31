"""
Módulo de exportación de datos
"""

import csv
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from config import Config
from utils import FormatUtils


class DataExporter:
    """Exportador de datos a diferentes formatos"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime(Config.TIMESTAMP_FORMAT)
    
    def export(self, data: Dict[str, Any], format_type: str) -> str:
        """Exportar datos al formato especificado"""
        if format_type not in Config.SUPPORTED_EXPORT_FORMATS:
            raise ValueError(f"Formato no soportado: {format_type}")
        
        titulo_limpio = FormatUtils.clean_text_for_filename(data['titulo'])
        filename = f"{titulo_limpio}_{self.timestamp}.{format_type}"
        
        if format_type == 'csv':
            self._export_to_csv(data, filename)
        elif format_type == 'excel':
            self._export_to_excel(data, filename)
        elif format_type == 'json':
            self._export_to_json(data, filename)
        
        return filename
    
    def _export_to_csv(self, data: Dict[str, Any], filename: str):
        """Exportar datos a CSV"""
        with open(filename, 'w', newline='', encoding=Config.DEFAULT_ENCODING) as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir encabezados
            if self._has_nested_data(data['datos']):
                writer.writerow(['Categoria', 'Metrica', 'Valor'])
                for categoria, valor in data['datos'].items():
                    if isinstance(valor, dict):
                        for metrica, val in valor.items():
                            writer.writerow([categoria, metrica, val])
                    else:
                        writer.writerow([categoria, 'Total_Ventas', valor])
            else:
                writer.writerow(['Categoria', 'Valor'])
                for categoria, valor in data['datos'].items():
                    writer.writerow([categoria, valor])
    
    def _export_to_excel(self, data: Dict[str, Any], filename: str):
        """Exportar datos a Excel"""
        if 'datos' in data:
            df = pd.DataFrame.from_dict(data['datos'], orient='index')
            # Limitar nombre de hoja a 31 caracteres (límite de Excel)
            sheet_name = data['titulo'][:31]
            df.to_excel(filename, sheet_name=sheet_name)
    
    def _export_to_json(self, data: Dict[str, Any], filename: str):
        """Exportar datos a JSON"""
        export_data = {
            **data,
            'timestamp': FormatUtils.format_timestamp(),
            'exported_by': 'Sistema de Reportes de Ventas'
        }
        
        with open(filename, 'w', encoding=Config.DEFAULT_ENCODING) as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
    
    def _has_nested_data(self, datos: Dict[str, Any]) -> bool:
        """Verificar si los datos tienen estructura anidada"""
        return any(isinstance(valor, dict) for valor in datos.values())
