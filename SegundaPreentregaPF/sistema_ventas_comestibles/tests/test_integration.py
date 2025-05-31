import pytest
from datetime import datetime
from decimal import Decimal
from src.models.product import Product
from src.models.sale import Sale

def test_create_product_and_sale_integration():
    # Crear producto simulado
    product = Product(1, "Miel", 80.0, 1, "Regular", resistant=False, is_allergic=False, vitality_days=180)
    assert product.product_name == "Miel"
    
    # Crear venta basada en ese producto
    sale = Sale(None, 1, 1, product.product_id, 2, 0.10, 144.0, datetime.now(), "TX999")
    
    assert sale.product_id == product.product_id
    assert sale.total_price == Decimal("144.0")
    assert sale.get_discount_amount() == Decimal("14.4")