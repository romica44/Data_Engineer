from typing import List, Optional
from src.database.connection import DatabaseConnection

class Category:
    """Clase que representa una categoría de productos"""
    
    def __init__(self, category_id: int, category_name: str):
        """
        Constructor de la clase Category
        
        Args:
            category_id (int): ID único de la categoría
            category_name (str): Nombre de la categoría
        """
        self.__category_id = category_id
        self.__category_name = category_name
        self.__products = []
    
    # Getters (Encapsulamiento)
    @property
    def category_id(self) -> int:
        return self.__category_id
    
    @property
    def category_name(self) -> str:
        return self.__category_name
    
    @property
    def products(self) -> List:
        return self.__products.copy()
    
    # Setters con validación
    @category_name.setter
    def category_name(self, name: str):
        if len(name.strip()) > 0:
            self.__category_name = name.strip()
        else:
            raise ValueError("El nombre de la categoría no puede estar vacío")
    
    # Métodos de negocio
    def add_product(self, product):
        """Agrega un producto a la categoría"""
        if product not in self.__products:
            self.__products.append(product)
    
    def get_products_count(self) -> int:
        """Retorna el número de productos en la categoría"""
        return len(self.__products)
    
    def get_category_sales_stats(self) -> dict:
        """Obtiene estadísticas de ventas de la categoría"""
        db = DatabaseConnection()
        query = """
        SELECT 
            COUNT(s.SalesID) as total_sales,
            SUM(s.TotalPrice) as total_revenue,
            AVG(s.TotalPrice) as avg_sale,
            SUM(s.Quantity) as total_units_sold
        FROM sales s
        JOIN products p ON s.ProductID = p.ProductID
        WHERE p.CategoryID = %s
        """
        result = db.execute_query(query, (self.__category_id,))
        return result[0] if result else {}
    
    def get_top_products(self, limit: int = 5) -> List[dict]:
        """Obtiene los productos más vendidos de la categoría"""
        db = DatabaseConnection()
        query = """
        SELECT 
            p.ProductName,
            SUM(s.Quantity) as units_sold,
            SUM(s.TotalPrice) as revenue
        FROM sales s
        JOIN products p ON s.ProductID = p.ProductID
        WHERE p.CategoryID = %s
        GROUP BY p.ProductID, p.ProductName
        ORDER BY units_sold DESC
        LIMIT %s
        """
        return db.execute_query(query, (self.__category_id, limit))
    
    @classmethod
    def find_by_id(cls, category_id: int) -> Optional['Category']:
        """Busca una categoría por ID"""
        db = DatabaseConnection()
        query = "SELECT * FROM categories WHERE CategoryID = %s"
        result = db.execute_query(query, (category_id,))
        
        if result:
            row = result[0]
            return cls(row['CategoryID'], row['CategoryName'])
        return None
    
    @classmethod
    def get_all(cls) -> List['Category']:
        """Obtiene todas las categorías"""
        db = DatabaseConnection()
        query = "SELECT * FROM categories ORDER BY CategoryName"
        results = db.execute_query(query)
        
        categories = []
        for row in results:
            categories.append(cls(row['CategoryID'], row['CategoryName']))
        return categories
    
    def save(self) -> int:
        """Guarda la categoría en la base de datos"""
        db = DatabaseConnection()
        if self.__category_id is None:
            query = "INSERT INTO categories (CategoryName) VALUES (%s)"
            self.__category_id = db.execute_insert(query, (self.__category_name,))
        else:
            query = "UPDATE categories SET CategoryName = %s WHERE CategoryID = %s"
            db.execute_update(query, (self.__category_name, self.__category_id))
        return self.__category_id
    
    def __str__(self) -> str:
        return self.__category_name
    
    def __repr__(self) -> str:
        return f"Category(id={self.__category_id}, name='{self.__category_name}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Category):
            return self.__category_id == other.__category_id
        return False