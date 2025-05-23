from decimal import Decimal
from datetime import date
from typing import Optional, List
from src.database.connection import DatabaseConnection

class Product:
    """Clase que representa un producto en el sistema"""
    
    def __init__(self, product_id: int, product_name: str, price: float, category_id: int,
                 class_type: str = "Regular", modify_date: date = None, resistant: str = "No",
                 ju_miergc: str = "", variable_date: float = 0.0):
        """
        Constructor de la clase Product
        
        Args:
            product_id (int): ID único del producto
            product_name (str): Nombre del producto
            price (float): Precio del producto
            category_id (int): ID de la categoría
            class_type (str): Tipo/clase del producto
            modify_date (date): Fecha de modificación
            resistant (str): Si es resistente o no
            ju_miergc (str): Campo específico del sistema
            variable_date (float): Fecha variable en días
        """
        self.__product_id = product_id
        self.__product_name = product_name
        self.__price = Decimal(str(price))
        self.__category_id = category_id
        self.__class_type = class_type
        self.__modify_date = modify_date or date.today()
        self.__resistant = resistant
        self.__ju_miergc = ju_miergc
        self.__variable_date = variable_date
    
    # Getters (Encapsulamiento)
    @property
    def product_id(self) -> int:
        return self.__product_id
    
    @property
    def product_name(self) -> str:
        return self.__product_name
    
    @property
    def price(self) -> Decimal:
        return self.__price
    
    @property
    def category_id(self) -> int:
        return self.__category_id
    
    @property
    def class_type(self) -> str:
        return self.__class_type
    
    @property
    def modify_date(self) -> date:
        return self.__modify_date
    
    @property
    def resistant(self) -> str:
        return self.__resistant
    
    @property
    def ju_miergc(self) -> str:
        return self.__ju_miergc
    
    @property
    def variable_date(self) -> float:
        return self.__variable_date
    
    # Setters con validación
    @product_name.setter
    def product_name(self, name: str):
        if len(name.strip()) > 0:
            self.__product_name = name.strip()
        else:
            raise ValueError("El nombre del producto no puede estar vacío")
    
    @price.setter
    def price(self, price: float):
        if price > 0:
            self.__price = Decimal(str(price))
        else:
            raise ValueError("El precio debe ser mayor a 0")
    
    @class_type.setter
    def class_type(self, class_type: str):
        valid_classes = ["Regular", "Premium", "Economy"]
        if class_type in valid_classes:
            self.__class_type = class_type
        else:
            raise ValueError(f"Clase inválida. Clases válidas: {valid_classes}")
    
    # Métodos de negocio
    def apply_discount(self, percentage: float) -> Decimal:
        """Aplica un descuento al precio del producto"""
        if 0 <= percentage <= 100:
            discount = self.__price * (Decimal(str(percentage)) / 100)
            return self.__price - discount
        else:
            raise ValueError("El porcentaje debe estar entre 0 y 100")
    
    def is_premium(self) -> bool:
        """Determina si el producto es premium"""
        return self.__class_type == "Premium"
    
    def is_resistant(self) -> bool:
        """Determina si el producto es resistente"""
        return self.__resistant.lower() == "si"
    
    def get_shelf_life_days(self) -> float:
        """Retorna la vida útil del producto en días"""
        return self.__variable_date
    
    def is_perishable(self) -> bool:
        """Determina si el producto es perecedero (vida útil <= 30 días)"""
        return self.__variable_date <= 30.0
    
    def get_sales_stats(self) -> dict:
        """Obtiene estadísticas de ventas del producto"""
        db = DatabaseConnection()
        query = """
        SELECT 
            COUNT(SalesID) as total_sales,
            SUM(Quantity) as total_units_sold,
            SUM(TotalPrice) as total_revenue,
            AVG(TotalPrice) as avg_sale_price,
            MAX(SalesDate) as last_sale_date
        FROM sales 
        WHERE ProductID = %s
        """
        result = db.execute_query(query, (self.__product_id,))
        return result[0] if result else {}
    
    def get_top_customers(self, limit: int = 5) -> List[dict]:
        """Obtiene los mejores clientes de este producto"""
        db = DatabaseConnection()
        query = """
        SELECT 
            CONCAT(c.FirstName, ' ', c.LastName) as customer_name,
            SUM(s.Quantity) as total_quantity,
            SUM(s.TotalPrice) as total_spent
        FROM sales s
        JOIN customers c ON s.CustomerID = c.CustomerID
        WHERE s.ProductID = %s
        GROUP BY s.CustomerID, c.FirstName, c.LastName
        ORDER BY total_quantity DESC
        LIMIT %s
        """
        return db.execute_query(query, (self.__product_id, limit))
    
    @classmethod
    def find_by_id(cls, product_id: int) -> Optional['Product']:
        """Busca un producto por ID"""
        db = DatabaseConnection()
        query = "SELECT * FROM products WHERE ProductID = %s"
        result = db.execute_query(query, (product_id,))
        
        if result:
            row = result[0]
            return cls(
                row['ProductID'], row['ProductName'], float(row['Price']),
                row['CategoryID'], row['Class'], row['ModifyDate'],
                row['Resistant'], row['JuMiergc'], float(row['VariableDate'])
            )
        return None
    
    @classmethod
    def get_by_category(cls, category_id: int) -> List['Product']:
        """Obtiene productos por categoría"""
        db = DatabaseConnection()
        query = "SELECT * FROM products WHERE CategoryID = %s ORDER BY ProductName"
        results = db.execute_query(query, (category_id,))
        
        products = []
        for row in results:
            products.append(cls(
                row['ProductID'], row['ProductName'], float(row['Price']),
                row['CategoryID'], row['Class'], row['ModifyDate'],
                row['Resistant'], row['JuMiergc'], float(row['VariableDate'])
            ))
        return products
    
    def save(self) -> int:
        """Guarda el producto en la base de datos"""
        db = DatabaseConnection()
        if self.__product_id is None:
            query = """
            INSERT INTO products (ProductName, Price, CategoryID, Class, ModifyDate, 
                                Resistant, JuMiergc, VariableDate) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.__product_id = db.execute_insert(query, (
                self.__product_name, float(self.__price), self.__category_id,
                self.__class_type, self.__modify_date, self.__resistant,
                self.__ju_miergc, self.__variable_date
            ))
        else:
            query = """
            UPDATE products SET ProductName = %s, Price = %s, CategoryID = %s,
                              Class = %s, ModifyDate = %s, Resistant = %s,
                              JuMiergc = %s, VariableDate = %s
            WHERE ProductID = %s
            """
            db.execute_update(query, (
                self.__product_name, float(self.__price), self.__category_id,
                self.__class_type, self.__modify_date, self.__resistant,
                self.__ju_miergc, self.__variable_date, self.__product_id
            ))
        return self.__product_id
    
    def __str__(self) -> str:
        return f"{self.__product_name} - ${self.__price:.2f} ({self.__class_type})"
    
    def __repr__(self) -> str:
        return f"Product(id={self.__product_id}, name='{self.__product_name}', price={self.__price})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Product):
            return self.__product_id == other.__product_id
        return False