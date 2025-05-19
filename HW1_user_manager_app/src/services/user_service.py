"""
Servicio de Gestión de Usuarios
Contiene la lógica de negocio para gestionar usuarios
"""

import json
from typing import List, Optional
from src.models.user import User
from src.utils.file_handler import read_json_file, write_json_file, read_text_file, write_text_file


class UserService:
    """Servicio para gestionar usuarios"""
    
    """
Servicio de Gestión de Usuarios
Contiene la lógica de negocio para gestionar usuarios
"""

import json
from typing import List, Optional, Tuple
from src.models.user import User
from src.utils.file_handler import read_json_file, write_json_file, read_text_file, write_text_file


class UserService:
    """Servicio para gestionar usuarios"""
    
    def __init__(self):
        """Inicializa el servicio de usuarios"""
        self.users = []
        self._unsaved_changes = False
    
    def register_user(self, name: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario
        
        Args:
            name (str): Nombre del usuario
            email (str): Email del usuario
            password (str): Contraseña del usuario
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        # Verificar datos de entrada
        if not name or not name.strip():
            return False, "El nombre no puede estar vacío"
        
        if not email or '@' not in email:
            return False, "El email no es válido"
        
        if not password or len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        # Verificar si el email ya existe
        if self._email_exists(email):
            return False, f"Ya existe un usuario con el email '{email}'"
        
        # Crear nuevo usuario
        user = User(name, email, password)
        self.users.append(user)
        self._unsaved_changes = True
        
        return True, f"Usuario '{name}' registrado exitosamente"
        
    def list_users(self) -> List[User]:
        """
        Lista todos los usuarios registrados
        
        Returns:
            List[User]: Lista de usuarios
        """
        return self.users.copy()
    
    """
    Método de búsqueda correcto en la clase UserService
    """

    def search_users_by_name(self, search_term: str) -> List[User]:
        """
        Busca usuarios por nombre
        
        Args:
            search_term (str): Término de búsqueda
            
        Returns:
            List[User]: Lista de usuarios que coinciden con la búsqueda
        """
        search_term = search_term.lower()
        return [user for user in self.users if search_term in user.name.lower()]
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            Optional[User]: Usuario si existe, None en caso contrario
        """
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    """
    Método delete_user que devuelve una tupla (success, message)
    """

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """
        Elimina un usuario por su ID
        
        Args:
            user_id (int): ID del usuario a eliminar
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        user = self.get_user_by_id(user_id)
        if user:
            self.users.remove(user)
            self._unsaved_changes = True
            return True, f"Usuario con ID {user_id} eliminado exitosamente"
        return False, f"No se encontró un usuario con ID {user_id}"
    
    """
    Métodos de guardado y carga de archivos en UserService
    """

    def save_to_json(self, filename: str) -> Tuple[bool, str]:
        """
        Guarda los usuarios en un archivo JSON
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        try:
            data = [user.to_dict() for user in self.users]
            if write_json_file(filename, data):
                self._unsaved_changes = False
                return True, f"Usuarios guardados en '{filename}'"
            return False, f"Error al guardar en '{filename}'"
        except Exception as e:
            return False, f"Error al guardar archivo JSON: {str(e)}"

    def export_to_txt(self, filename: str) -> Tuple[bool, str]:
        """
        Guarda los usuarios en un archivo de texto
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        try:
            lines = []
            for user in self.users:
                line = f"{user.id}|{user.name}|{user.email}|{user.password_hash}|{user.created_at.isoformat()}"
                lines.append(line)
            
            if write_text_file(filename, lines):
                self._unsaved_changes = False
                return True, f"Usuarios guardados en '{filename}'"
            return False, f"Error al guardar en '{filename}'"
        except Exception as e:
            return False, f"Error al guardar archivo TXT: {str(e)}"
    """
    Métodos de carga de archivos en UserService
    """

    def load_from_json(self, filename: str) -> Tuple[bool, str]:
        """
        Carga usuarios desde un archivo JSON
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        try:
            data = read_json_file(filename)
            if data is None:
                return False, f"No se pudo leer el archivo '{filename}'"
            
            self.users.clear()
            User._next_id = 1  # Reiniciar contador de IDs
            
            for user_data in data:
                user = User.from_dict(user_data)
                self.users.append(user)
            
            self._unsaved_changes = False
            return True, f"Se cargaron {len(self.users)} usuarios desde '{filename}'"
        except Exception as e:
            return False, f"Error al cargar archivo JSON: {str(e)}"

    def load_from_txt(self, filename: str) -> Tuple[bool, str]:
        """
        Carga usuarios desde un archivo de texto
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            Tuple[bool, str]: Tupla con (éxito, mensaje)
        """
        try:
            lines = read_text_file(filename)
            if lines is None:
                return False, f"No se pudo leer el archivo '{filename}'"
            
            self.users.clear()
            User._next_id = 1  # Reiniciar contador de IDs
            
            count = 0
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split('|')
                    if len(parts) == 5:
                        user_data = {
                            'id': int(parts[0]),
                            'name': parts[1],
                            'email': parts[2],
                            'password_hash': parts[3],
                            'created_at': parts[4]
                        }
                        user = User.from_dict(user_data)
                        self.users.append(user)
                        count += 1
            
            self._unsaved_changes = False
            return True, f"Se cargaron {count} usuarios desde '{filename}'"
        except Exception as e:
            return False, f"Error al cargar archivo TXT: {str(e)}"
            
    def has_unsaved_changes(self) -> bool:
        """
        Verifica si hay cambios sin guardar
        
        Returns:
            bool: True si hay cambios sin guardar
        """
        return self._unsaved_changes
    
    def _email_exists(self, email: str) -> bool:
        """
        Verifica si un email ya existe
        
        Args:
            email (str): Email a verificar
            
        Returns:
            bool: True si el email ya existe
        """
        return any(user.email.lower() == email.lower() for user in self.users)