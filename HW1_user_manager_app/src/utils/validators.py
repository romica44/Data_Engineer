"""
Utilidades de Validación
Funciones para validar datos de entrada
"""

import re


def validate_email(email: str) -> bool:
    """
    Valida si un email tiene un formato correcto
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True si el email es válido
    """
    if not email:
        return False
    
    # Patrón básico para validar emails
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, email))


def validate_password(password: str, min_length: int = 6) -> bool:
    """
    Valida si una contraseña cumple con los requisitos mínimos
    
    Args:
        password (str): Contraseña a validar
        min_length (int): Longitud mínima de la contraseña
        
    Returns:
        bool: True si la contraseña es válida
    """
    if not password:
        return False
    
    return len(password) >= min_length


def validate_name(name: str, min_length: int = 2, max_length: int = 50) -> bool:
    """
    Valida si un nombre cumple con los requisitos
    
    Args:
        name (str): Nombre a validar
        min_length (int): Longitud mínima del nombre
        max_length (int): Longitud máxima del nombre
        
    Returns:
        bool: True si el nombre es válido
    """
    if not name or not name.strip():
        return False
    
    name = name.strip()
    return min_length <= len(name) <= max_length


def sanitize_string(input_string: str) -> str:
    """
    Limpia y sanitiza una cadena de texto
    
    Args:
        input_string (str): Cadena a sanitizar
        
    Returns:
        str: Cadena sanitizada
    """
    if not input_string:
        return ""
    
    # Eliminar espacios al inicio y final
    sanitized = input_string.strip()
    
    # Eliminar caracteres de control
    sanitized = ''.join(char for char in sanitized if char.isprintable())
    
    return sanitized