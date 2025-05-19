
"""
Pruebas unitarias para el sistema de gestión de usuarios
"""

import unittest
import os
import sys
import json
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ahora podemos importar los módulos del proyecto
from src.models.user import User
from src.services.user_service import UserService
from src.utils.file_handler import write_json_file, read_json_file


class TestUserModel(unittest.TestCase):
    """Pruebas para el modelo de Usuario"""
    
    def test_user_creation(self):
        """Prueba la creación de un usuario"""
        user = User("Test User", "test@example.com", "password123")
        
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(hasattr(user, "password_hash"))
        self.assertTrue(hasattr(user, "id"))
        self.assertTrue(isinstance(user.created_at, datetime))
    
    def test_verify_password(self):
        """Prueba la verificación de contraseña"""
        user = User("Test User", "test@example.com", "password123")
        
        self.assertTrue(user.verify_password("password123"))
        self.assertFalse(user.verify_password("wrongpassword"))
    
    def test_to_dict_from_dict(self):
        """Prueba la conversión a/desde diccionario"""
        user = User("Test User", "test@example.com", "password123")
        user_dict = user.to_dict()
        
        self.assertTrue(isinstance(user_dict, dict))
        self.assertEqual(user_dict["name"], "Test User")
        self.assertEqual(user_dict["email"], "test@example.com")
        
        # Recrear usuario desde diccionario
        recreated_user = User.from_dict(user_dict)
        self.assertEqual(recreated_user.id, user.id)
        self.assertEqual(recreated_user.name, user.name)
        self.assertEqual(recreated_user.email, user.email)
        self.assertEqual(recreated_user.password_hash, user.password_hash)


class TestUserService(unittest.TestCase):
    """Pruebas para el servicio de usuarios"""
    
    def setUp(self):
        """Configuración para cada prueba"""
        self.service = UserService()
        # Agregar algunos usuarios de prueba
        self.service.register_user("User One", "one@example.com", "password1")
        self.service.register_user("User Two", "two@example.com", "password2")
        self.service.register_user("Another User", "another@example.com", "password3")
    
    def test_register_user(self):
        """Prueba el registro de usuarios"""
        # Usuario nuevo
        success, _ = self.service.register_user("New User", "new@example.com", "password")
        self.assertTrue(success)
        
        # Email duplicado
        success, _ = self.service.register_user("Duplicate", "one@example.com", "password")
        self.assertFalse(success)
        
        # Datos inválidos
        success, _ = self.service.register_user("", "invalid", "pass")
        self.assertFalse(success)
    
    def test_list_users(self):
        """Prueba el listado de usuarios"""
        users = self.service.list_users()
        self.assertEqual(len(users), 3)
    
    def test_search_by_name(self):
        """Prueba la búsqueda de usuarios por nombre"""
        # Búsqueda exacta
        results = self.service.search_users_by_name("User One")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "User One")
        
        # Búsqueda parcial
        results = self.service.search_users_by_name("User")
        self.assertEqual(len(results), 3)  # Debería encontrar los tres
        
        # Búsqueda inexistente
        results = self.service.search_users_by_name("NonExistent")
        self.assertEqual(len(results), 0)
    
    def test_delete_user(self):
        """Prueba la eliminación de usuarios"""
        # Obtener el ID del primer usuario
        user_id = self.service.list_users()[0].id
        
        # Eliminar usuario existente
        success, _ = self.service.delete_user(user_id)
        self.assertTrue(success)
        self.assertEqual(len(self.service.list_users()), 2)
        
        # Eliminar usuario inexistente
        success, _ = self.service.delete_user(999)
        self.assertFalse(success)
    
    def test_save_load_json(self):
        """Prueba guardar y cargar usuarios en JSON"""
        # Archivo de prueba
        test_file = "test_users.json"
        
        # Guardar
        success, _ = self.service.save_to_json(test_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        # Crear un nuevo servicio y cargar
        new_service = UserService()
        success, _ = new_service.load_from_json(test_file)
        self.assertTrue(success)
        
        # Verificar que los datos sean iguales
        self.assertEqual(len(new_service.list_users()), 3)
        
        # Limpiar
        if os.path.exists(test_file):
            os.remove(test_file)


# Ejecutar las pruebas si se llama directamente
if __name__ == "__main__":
    unittest.main()