
"""
Estrategias de cálculo para métricas de ventas
"""

import pandas as pd
from typing import Dict, Any
from models import MetricStrategy
from utils import DataUtils


class TotalSalesByCategoryStrategy(MetricStrategy):
    """Estrategia para calcular total de ventas por categoría"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Calcular total de ventas (precio * cantidad) por categoría
        data['total_venta'] = data.apply(DataUtils.calculate_total_sale, axis=1)
        total_por_categoria = data.groupby('categoria')['total_venta'].sum().to_dict()
        
        return {
            'titulo': 'Total de Ventas por Categoría',
            'datos': total_por_categoria,
            'total_general': sum(total_por_categoria.values())
        }


class DetailedSalesByCategoryStrategy(MetricStrategy):
    """Estrategia para calcular métricas detalladas por categoría"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        data['total_venta'] = data.apply(DataUtils.calculate_total_sale, axis=1)
        
        # Agrupar por categoría y calcular múltiples métricas
        metricas_por_categoria = data.groupby('categoria').agg({
            'total_venta': 'sum',
            'precio': 'mean',
            'cantidad': 'sum',
            'producto': 'count'
        }).round(2)
        
        # Renombrar columnas para mayor claridad
        metricas_por_categoria.columns = ['Total_Ventas', 'Precio_Promedio', 'Cantidad_Total', 'Productos_Vendidos']
        
        return {
            'titulo': 'Métricas Detalladas por Categoría',
            'datos': metricas_por_categoria.to_dict('index'),
            'resumen': {
                'total_ventas_general': metricas_por_categoria['Total_Ventas'].sum(),
                'precio_promedio_general': data['precio'].mean(),
                'cantidad_total_general': metricas_por_categoria['Cantidad_Total'].sum(),
                'total_productos_vendidos': metricas_por_categoria['Productos_Vendidos'].sum()
            }
        }


class SalesByChannelStrategy(MetricStrategy):
    """Estrategia para calcular ventas por canal de venta"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        data['total_venta'] = data.apply(DataUtils.calculate_total_sale, axis=1)
        
        ventas_por_canal = data.groupby('medio_venta').agg({
            'total_venta': 'sum',
            'cantidad': 'sum',
            'producto': 'count'
        }).round(2)
        
        ventas_por_canal.columns = ['Total_Ventas', 'Cantidad_Total', 'Transacciones']
        
        return {
            'titulo': 'Ventas por Canal de Venta',
            'datos': ventas_por_canal.to_dict('index'),
            'total_general': ventas_por_canal['Total_Ventas'].sum()
        }


class SalesBySellerStrategy(MetricStrategy):
    """Estrategia para calcular ventas por vendedor"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        data['total_venta'] = data.apply(DataUtils.calculate_total_sale, axis=1)
        
        ventas_por_vendedor = data.groupby('vendedor').agg({
            'total_venta': 'sum',
            'cantidad': 'sum',
            'producto': 'count'
        }).round(2)
        
        ventas_por_vendedor.columns = ['Total_Ventas', 'Cantidad_Total', 'Productos_Vendidos']
        
        return {
            'titulo': 'Rendimiento por Vendedor',
            'datos': ventas_por_vendedor.to_dict('index'),
            'total_general': ventas_por_vendedor['Total_Ventas'].sum()
        }
