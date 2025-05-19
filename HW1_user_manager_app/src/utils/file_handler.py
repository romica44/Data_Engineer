"""
Utilidades para manejo de archivos
Funciones auxiliares para operaciones con archivos
"""

import os
import json
from typing import Dict, List, Any, Optional


def ensure_directory_exists(filepath: str) -> None:
    """
    Asegura que el directorio para un archivo exista, creándolo si es necesario
    
    Args:
        filepath (str): Ruta del archivo
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def file_exists(filepath: str) -> bool:
    """
    Verifica si un archivo existe
    
    Args:
        filepath (str): Ruta del archivo
        
    Returns:
        bool: True si el archivo existe
    """
    return os.path.isfile(filepath)


def read_json_file(filepath: str) -> Optional[List[Dict[str, Any]]]:
    """
    Lee un archivo JSON y devuelve su contenido
    
    Args:
        filepath (str): Ruta del archivo JSON
        
    Returns:
        Optional[List[Dict[str, Any]]]: Contenido del archivo o None si hay error
    """
    try:
        if not file_exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error al leer archivo JSON '{filepath}': {e}")
        return None


def write_json_file(filepath: str, data: List[Dict[str, Any]]) -> bool:
    """
    Escribe datos en un archivo JSON
    
    Args:
        filepath (str): Ruta del archivo JSON
        data (List[Dict[str, Any]]): Datos a escribir
        
    Returns:
        bool: True si se escribió exitosamente
    """
    try:
        ensure_directory_exists(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except IOError as e:
        print(f"Error al escribir archivo JSON '{filepath}': {e}")
        return False


def read_text_file(filepath: str) -> Optional[List[str]]:
    """
    Lee un archivo de texto y devuelve sus líneas
    
    Args:
        filepath (str): Ruta del archivo de texto
        
    Returns:
        Optional[List[str]]: Líneas del archivo o None si hay error
    """
    try:
        if not file_exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    except IOError as e:
        print(f"Error al leer archivo de texto '{filepath}': {e}")
        return None


def write_text_file(filepath: str, lines: List[str]) -> bool:
    """
    Escribe líneas en un archivo de texto
    
    Args:
        filepath (str): Ruta del archivo de texto
        lines (List[str]): Líneas a escribir
        
    Returns:
        bool: True si se escribió exitosamente
    """
    try:
        ensure_directory_exists(filepath)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(f"{line}\n")
        
        return True
    except IOError as e:
        print(f"Error al escribir archivo de texto '{filepath}': {e}")
        return False


def get_files_with_extension(directory: str, extension: str) -> List[str]:
    """
    Obtiene una lista de archivos con cierta extensión en un directorio
    
    Args:
        directory (str): Directorio donde buscar
        extension (str): Extensión a filtrar (sin el punto, ej: 'json')
        
    Returns:
        List[str]: Lista de rutas de archivos
    """
    if not os.path.isdir(directory):
        return []
    
    extension = extension.lower()
    if not extension.startswith('.'):
        extension = f".{extension}"
    
    result = []
    for file in os.listdir(directory):
        if file.lower().endswith(extension):
            result.append(os.path.join(directory, file))
    
    return result


def get_filename_without_extension(filepath: str) -> str:
    """
    Obtiene el nombre de archivo sin extensión
    
    Args:
        filepath (str): Ruta del archivo
        
    Returns:
        str: Nombre del archivo sin extensión
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def get_file_extension(filepath: str) -> str:
    """
    Obtiene la extensión de un archivo
    
    Args:
        filepath (str): Ruta del archivo
        
    Returns:
        str: Extensión del archivo
    """
    return os.path.splitext(filepath)[1]