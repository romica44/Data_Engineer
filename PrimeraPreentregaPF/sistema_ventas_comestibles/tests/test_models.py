import pytest
from datetime import datetime, date
from decimal import Decimal
from src.models.country import Country
from src.models.category import Category
from src.models.product import Product
from src.models.sale import Sale

class TestCountry:
    """Pruebas unitarias para la clase Country"""
    
    def setup_method(self):
        self.country = Country(1, "Estados Unidos", "US")
    
    def test_constructor(self):
        assert self.country.country_id == 1
        assert self.country.country_name == "Estados Unidos"
        assert self.country.country_code == "US"
    
    def test_country_name_setter_valid(self):
        self.country.country_name = "México"
        assert self.country.country_name == "México"
    
    def test_country_name_setter_invalid(self):
        with pytest.raises(ValueError):
            self.country.country_name = ""
    
    def test_country_code_setter_valid(self):
        self.country.country_code = "mx"
        assert self.country.country_code == "MX"
    
    def test_country_code_setter_invalid(self):
        with pytest.raises(ValueError):
            self.country.country_code = "USA"
    
    def test_cities_count_initial(self):
        assert self.country.get_cities_count() == 0
    
    def test_equality(self):
        country2 = Country(1, "Otro País", "XX")
        assert self.country == country2
        
        country3 = Country(2, "Estados Unidos", "US")
        assert self.country != country3

class TestCategory:
    """Pruebas unitarias para la clase Category"""
    
    def setup_method(self):
        self.category = Category(1, "Frutas y Verduras")
    
    def test_constructor(self):
        assert self.category.category_id == 1
        assert self.category.category_name == "Frutas y Verduras"
    
    def test_category_name_setter_valid(self):
        self.category.category_name = "Lácteos"
        assert self.category.category_name == "Lácteos"
    
    def test_category_name_setter_invalid(self):
        with pytest.raises(ValueError):
            self.category.category_name = ""
    
    def test_products_count_initial(self):
        assert self.category.get_products_count() == 0

class TestProduct:
    """Pruebas unitarias para la clase Product"""
    
    def setup_method(self):
        self.product = Product(1, "Manzanas Rojas", 2.50, 1, "Premium", 
                              date(2024, 1, 15), "Si", "A1", 7.0)
    
    def test_constructor(self):
        assert self.product.product_id == 1
        assert self.product.product_name == "Manzanas Rojas"
        assert self.product.price == Decimal('2.50')
        assert self.product.category_id == 1
        assert self.product.class_type == "Premium"
    
    def test_apply_discount(self):
        discounted_price = self.product.apply_discount(10)
        assert discounted_price == Decimal('2.25')
    
    def test_apply_discount_invalid(self):
        with pytest.raises(ValueError):
            self.product.apply_discount(150)
    
    def test_is_premium(self):
        assert self.product.is_premium() == True
        
        regular_product = Product(2, "Bananas", 1.80, 1, "Regular")
        assert regular_product.is_premium() == False
    
    def test_is_resistant(self):
        assert self.product.is_resistant() == True
        
        non_resistant = Product(2, "Pan", 2.90, 4, "Regular", resistant="No")
        assert non_resistant.is_resistant() == False
    
    def test_is_perishable(self):
        assert self.product.is_perishable() == True  # 7 días <= 30
        
        non_perishable = Product(2, "Conserva", 3.50, 6, variable_date=365.0)
        assert non_perishable.is_perishable() == False
    
    def test_price_setter_valid(self):
        self.product.price = 3.00
        assert self.product.price == Decimal('3.00')
    
    def test_price_setter_invalid(self):
        with pytest.raises(ValueError):
            self.product.price = -1.0
    
    def test_class_type_setter_valid(self):
        self.product.class_type = "Regular"
        assert self.product.class_type == "Regular"
    
    def test_class_type_setter_invalid(self):
        with pytest.raises(ValueError):
            self.product.class_type = "Inexistente"

class TestSale:
    """Pruebas unitarias para la clase Sale"""
    
    def setup_method(self):
        self.sale = Sale(1, 1, 1, 1, 5, 0.10, 11.25, 
                        datetime(2024, 1, 15, 10, 30), "TXN001", 1, 1, 1)
    
    def test_constructor(self):
        assert self.sale.sales_id == 1
        assert self.sale.sales_person_id == 1
        assert self.sale.customer_id == 1
        assert self.sale.product_id == 1
        assert self.sale.quantity == 5
        assert self.sale.discount == Decimal('0.10')
        assert self.sale.total_price == Decimal('11.25')
    
    def test_get_unit_price(self):
        # Precio antes del descuento: 11.25 / (1 - 0.10) = 12.50
        # Precio unitario: 12.50 / 5 = 2.50
        unit_price = self.sale.get_unit_price()
        expected = Decimal('11.25') / (Decimal('1') - Decimal('0.10')) / 5
        assert abs(unit_price - expected) < Decimal('0.01')
    
    def test_get_discount_amount(self):
        discount_amount = self.sale.get_discount_amount()
        assert discount_amount > 0
    
    def test_is_bulk_sale(self):
        assert self.sale.is_bulk_sale(3) == True
        assert self.sale.is_bulk_sale(10) == False
    
    def test_is_discounted(self):
        assert self.sale.is_discounted() == True
        
        no_discount_sale = Sale(2, 1, 1, 1, 2, 0.0, 5.00, 
                               datetime.now(), "TXN002", 1, 1, 1)
        assert no_discount_sale.is_discounted() == False
    
    def test_quantity_setter_valid(self):
        self.sale.quantity = 3
        assert self.sale.quantity == 3
    
    def test_quantity_setter_invalid(self):
        with pytest.raises(ValueError):
            self.sale.quantity = 0
    
    def test_discount_setter_valid(self):
        self.sale.discount = 0.15
        assert self.sale.discount == Decimal('0.15')
    
    def test_discount_setter_invalid(self):
        with pytest.raises(ValueError):
            self.sale.discount = 1.5