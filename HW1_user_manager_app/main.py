import os
import sys
import traceback
from src.services.user_service import UserService
from src.config.settings import APP_NAME, DEBUG
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)


class AppError(Exception):
    """Excepción personalizada para errores de la aplicación"""
    pass


def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu():
    """Muestra el menú principal"""
    print(f"\n{Fore.CYAN}========= {APP_NAME} =========")
    print(f"{Fore.GREEN}1. {Style.RESET_ALL}Registrar nuevo usuario")
    print(f"{Fore.GREEN}2. {Style.RESET_ALL}Listar usuarios registrados")
    print(f"{Fore.GREEN}3. {Style.RESET_ALL}Buscar usuario por nombre")
    print(f"{Fore.GREEN}4. {Style.RESET_ALL}Eliminar usuario")
    print(f"{Fore.GREEN}5. {Style.RESET_ALL}Guardar usuarios en archivo")
    print(f"{Fore.GREEN}6. {Style.RESET_ALL}Cargar usuarios desde archivo")
    print(f"{Fore.RED}0. {Style.RESET_ALL}Salir")
    print(f"{Fore.CYAN}{'=' * 40}")


def show_success(message):
    """Muestra un mensaje de éxito"""
    print(f"\n{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def show_error(message):
    """Muestra un mensaje de error"""
    print(f"\n{Fore.RED}✗ {message}{Style.RESET_ALL}")


def show_info(message):
    """Muestra un mensaje informativo"""
    print(f"\n{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def register_user(service):
    """Maneja el registro de usuarios"""
    try:
        print(f"\n{Fore.CYAN}--- Registrar Usuario ---{Style.RESET_ALL}")
        
        # Obtener datos del usuario
        name = input(f"{Fore.YELLOW}Nombre: {Style.RESET_ALL}").strip()
        email = input(f"{Fore.YELLOW}Email: {Style.RESET_ALL}").strip()
        password = input(f"{Fore.YELLOW}Contraseña: {Style.RESET_ALL}").strip()
        
        # Llamar al servicio y manejar respuesta
        success, message = service.register_user(name, email, password)
        
        if success:
            show_success(message)
        else:
            show_error(message)
            
    except Exception as e:
        show_error(f"Error inesperado: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def list_users(service):
    """Lista todos los usuarios"""
    try:
        users = service.list_users()
        
        if not users:
            show_info("No hay usuarios registrados")
            return
        
        print(f"\n{Fore.CYAN}--- Usuarios Registrados ---{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'ID':<5} {'Nombre':<20} {'Email':<30}{Style.RESET_ALL}")
        print("-" * 55)
        
        for user in users:
            print(f"{user.id:<5} {user.name:<20} {user.email:<30}")
            
    except Exception as e:
        show_error(f"Error al listar usuarios: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def search_user(service):
    """Busca usuarios por nombre"""
    try:
        print(f"\n{Fore.CYAN}--- Buscar Usuario ---{Style.RESET_ALL}")
        
        search_term = input(f"{Fore.YELLOW}Ingrese nombre a buscar: {Style.RESET_ALL}").strip()
        if not search_term:
            show_error("El término de búsqueda no puede estar vacío")
            return
        
        users = service.search_users_by_name(search_term)
        
        if not users:
            show_info(f"No se encontraron usuarios con el nombre '{search_term}'")
            return
        
        print(f"\n{Fore.GREEN}Resultados para '{search_term}':{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'ID':<5} {'Nombre':<20} {'Email':<30}{Style.RESET_ALL}")
        print("-" * 55)
        
        for user in users:
            print(f"{user.id:<5} {user.name:<20} {user.email:<30}")
            
    except Exception as e:
        show_error(f"Error en la búsqueda: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def delete_user(service):
    """Elimina un usuario"""
    try:
        print(f"\n{Fore.CYAN}--- Eliminar Usuario ---{Style.RESET_ALL}")
        
        # Mostrar usuarios disponibles
        users = service.list_users()
        if not users:
            show_info("No hay usuarios registrados para eliminar")
            return
        
        print(f"{Fore.YELLOW}--- Usuarios disponibles ---{Style.RESET_ALL}")
        for user in users:
            print(f"ID: {user.id} - {user.name}")
        
        # Solicitar ID
        try:
            user_id = int(input(f"\n{Fore.YELLOW}ID del usuario a eliminar: {Style.RESET_ALL}"))
        except ValueError:
            show_error("ID inválido. Debe ser un número.")
            return
        
        # Confirmar eliminación
        confirm = input(f"{Fore.YELLOW}¿Está seguro de eliminar el usuario con ID {user_id}? (s/n): {Style.RESET_ALL}")
        if confirm.lower() not in ('s', 'si', 'sí', 'y', 'yes'):
            show_info("Operación cancelada")
            return
        
        # Eliminar usuario
        success, message = service.delete_user(user_id)
        
        if success:
            show_success(message)
        else:
            show_error(message)
            
    except Exception as e:
        show_error(f"Error al eliminar usuario: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def save_to_file(service):
    """Guarda usuarios en archivo"""
    try:
        print(f"\n{Fore.CYAN}--- Guardar Usuarios ---{Style.RESET_ALL}")
        
        if not service.list_users():
            show_info("No hay usuarios para guardar")
            return
        
        filename = input(f"{Fore.YELLOW}Nombre del archivo (sin extensión): {Style.RESET_ALL}").strip() or "users"
        
        print(f"\n{Fore.BLUE}Formato:{Style.RESET_ALL}")
        print("1. JSON")
        print("2. TXT")
        
        format_choice = input(f"{Fore.YELLOW}Opción: {Style.RESET_ALL}").strip()
        
        if format_choice == "1":
            success, message = service.save_to_json(f"{filename}.json")
        elif format_choice == "2":
            success, message = service.export_to_txt(f"{filename}.txt")
        else:
            show_error("Opción inválida")
            return
        
        if success:
            show_success(message)
        else:
            show_error(message)
            
    except Exception as e:
        show_error(f"Error al guardar archivo: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def load_from_file(service):
    """Carga usuarios desde archivo"""
    try:
        print(f"\n{Fore.CYAN}--- Cargar Usuarios ---{Style.RESET_ALL}")
        
        filename = input(f"{Fore.YELLOW}Nombre del archivo (con extensión): {Style.RESET_ALL}").strip()
        if not filename:
            show_error("Debe ingresar un nombre de archivo")
            return
        
        if not os.path.exists(filename):
            show_error(f"El archivo '{filename}' no existe")
            return
        
        if filename.endswith('.json'):
            success, message = service.load_from_json(filename)
        elif filename.endswith('.txt'):
            success, message = service.load_from_txt(filename)
        else:
            show_error("Formato no soportado (use .json o .txt)")
            return
        
        if success:
            show_success(message)
        else:
            show_error(message)
            
    except Exception as e:
        show_error(f"Error al cargar archivo: {str(e)}")
        if DEBUG:
            traceback.print_exc()


def main():
    """Función principal"""
    try:
        # Crear una sola instancia del servicio
        service = UserService()
        
        # Intentar cargar usuarios desde archivo por defecto
        default_file = 'users.json'
        if os.path.exists(default_file):
            try:
                success, message = service.load_from_json(default_file)
                if success:
                    show_success(message)
            except Exception as e:
                show_error(f"Error al cargar archivo predeterminado: {str(e)}")
        
        # Bucle principal
        while True:
            display_menu()
            
            try:
                choice = input(f"\n{Fore.YELLOW}Seleccione una opción: {Style.RESET_ALL}").strip()
                
                if choice == "0":
                    # Preguntar si guardar antes de salir
                    if service.has_unsaved_changes():
                        save_prompt = input(f"{Fore.YELLOW}Hay cambios sin guardar. ¿Guardar antes de salir? (s/n): {Style.RESET_ALL}")
                        if save_prompt.lower() in ('s', 'si', 'sí', 'y', 'yes'):
                            service.save_to_json(default_file)
                    
                    print(f"\n{Fore.GREEN}¡Hasta luego!{Style.RESET_ALL}")
                    sys.exit(0)
                    
                elif choice == "1":
                    register_user(service)
                elif choice == "2":
                    list_users(service)
                elif choice == "3":
                    search_user(service)
                elif choice == "4":
                    delete_user(service)
                elif choice == "5":
                    save_to_file(service)
                elif choice == "6":
                    load_from_file(service)
                else:
                    show_error("Opción inválida")
                    
            except Exception as e:
                show_error(f"Error inesperado: {str(e)}")
                if DEBUG:
                    traceback.print_exc()
            
            input(f"\n{Fore.YELLOW}Presione Enter para continuar...{Style.RESET_ALL}")
            clear_screen()
    
    except Exception as e:
        show_error(f"Error crítico: {str(e)}")
        if DEBUG:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Programa interrumpido por el usuario{Style.RESET_ALL}")
        sys.exit(0)