"""
Modelo de Usuario
Representa un usuario en el sistema
"""

import hashlib
from datetime import datetime


class User:
    """Clase que representa un usuario"""
    
    _next_id = 1  # Contador para generar IDs únicos
    
    def __init__(self, name, email, password, user_id=None, created_at=None):
        """
        Inicializa un usuario
        
        Args:
            name (str): Nombre del usuario
            email (str): Email del usuario
            password (str): Contraseña del usuario
            user_id (int, optional): ID del usuario. Si no se proporciona, se genera automáticamente
            created_at (datetime, optional): Fecha de creación. Si no se proporciona, se usa la fecha actual
        """
        if user_id is None:
            self.id = User._next_id
            User._next_id += 1
        else:
            self.id = user_id
            if user_id >= User._next_id:
                User._next_id = user_id + 1
        
        self.name = name
        self.email = email
        self.password_hash = self._hash_password(password)
        
        if created_at is None:
            self.created_at = datetime.now()
        elif isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at)
            except ValueError:
                self.created_at = datetime.now()
        else:
            self.created_at = created_at
    
    @staticmethod
    def _hash_password(password):
        """
        Genera un hash de la contraseña
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """
        Verifica si una contraseña coincide con la del usuario
        
        Args:
            password (str): Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta
        """
        return self.password_hash == self._hash_password(password)
    
    def to_dict(self):
        """
        Convierte el usuario a un diccionario
        
        Returns:
            dict: Representación del usuario como diccionario
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un usuario desde un diccionario
        
        Args:
            data (dict): Diccionario con los datos del usuario
            
        Returns:
            User: Instancia del usuario
        """
        # Manejo para compatibilidad con diferentes formatos
        if 'password_hash' in data:
            # Si ya viene con password_hash (formato original)
            user = cls.__new__(cls)
            user.id = data['id']
            user.name = data['name']
            user.email = data['email']
            user.password_hash = data['password_hash']
            
            if isinstance(data['created_at'], str):
                user.created_at = datetime.fromisoformat(data['created_at'])
            else:
                user.created_at = data['created_at']
            
        else:
            # Si viene con password en texto plano (formato nuevo)
            user = cls(
                name=data['name'],
                email=data['email'],
                password=data['password'],  # Será hasheado en __init__
                user_id=data.get('id'),
                created_at=data.get('created_at')
            )
        
        # Actualizar el contador de IDs
        if user.id >= cls._next_id:
            cls._next_id = user.id + 1
        
        return user
    
    def __str__(self):
        """Representación en string del usuario"""
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
    
    def __repr__(self):
        """Representación oficial del usuario"""
        return self.__str__()