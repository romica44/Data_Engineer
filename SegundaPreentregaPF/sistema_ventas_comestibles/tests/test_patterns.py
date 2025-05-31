"""
Pruebas unitarias para los patrones de diseño implementados.
Enfocadas en probar la funcionalidad de Singleton, Factory, Builder y Strategy.

Ejecutar con: pytest tests/test_patterns.py -v
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports de nuestros patrones
from src.database.connection import DatabaseConnection
from src.patterns.report_factory import ReportFactory, ReportType
from src.patterns.query_builder import SQLQueryBuilder, SalesQueryBuilder, create_query, create_sales_query
from src.patterns.analysis_strategies import (
    TrendAnalysisStrategy, PerformanceComparisonStrategy, 
    SegmentationStrategy, AnalysisContext
)
from src.models.reports import SalesReport, EmployeeReport, ProductReport, GeographicReport


class TestSingletonPattern:
    """
    Pruebas para verificar que el patrón Singleton funciona correctamente.
    """
    
    def test_singleton_instance_uniqueness(self):
        """Verifica que DatabaseConnection siempre retorna la misma instancia"""
        # Crear múltiples instancias
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        db3 = DatabaseConnection()
        
        # Verificar que todas son la misma instancia
        assert db1 is db2, "db1 y db2 no son la misma instancia"
        assert db2 is db3, "db2 y db3 no son la misma instancia"
        assert db1 is db3, "db1 y db3 no son la misma instancia"
    
    def test_singleton_same_id(self):
        """Verifica que múltiples instancias tienen el mismo ID"""
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        
        assert id(db1) == id(db2), "Las instancias tienen IDs diferentes"
    
    def test_singleton_shared_state(self):
        """Verifica que las instancias comparten el mismo estado"""
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        
        # Verificar que comparten los mismos atributos
        assert db1.host == db2.host, "Las instancias no comparten el mismo host"
        assert db1.database == db2.database, "Las instancias no comparten la misma BD"
    
    def test_singleton_initialization_once(self):
        """Verifica que la inicialización solo ocurre una vez"""
        # Resetear cualquier instancia previa para esta prueba
        DatabaseConnection._instance = None
        
        db1 = DatabaseConnection()
        assert hasattr(db1, 'initialized'), "Primera instancia no fue inicializada"
        
        db2 = DatabaseConnection()
        assert db1 is db2, "Segunda instancia no es la misma que la primera"
    
    def test_singleton_pattern_info(self):
        """Verifica que el patrón Singleton está correctamente documentado"""
        db = DatabaseConnection()
        connection_info = db.get_connection_info()
        
        assert 'pattern' in connection_info, "No se reporta información del patrón"
        assert connection_info['pattern'] == 'Singleton', "Patrón incorrecto reportado"


class TestFactoryPattern:
    """
    Pruebas para verificar que el patrón Factory funciona correctamente.
    """
    
    def setup_method(self):
        """Configuración para cada prueba"""
        self.factory = ReportFactory()
    
    def test_factory_initialization(self):
        """Verifica que la factory se inicializa correctamente"""
        assert self.factory is not None, "Factory no se inicializó"
        assert hasattr(self.factory, 'analytics_service'), "Factory no tiene analytics_service"
        assert hasattr(self.factory, '_report_creators'), "Factory no tiene _report_creators"
    
    def test_factory_available_report_types(self):
        """Verifica que la factory conoce todos los tipos de reportes"""
        available_types = self.factory.get_available_report_types()
        
        assert isinstance(available_types, dict), "get_available_report_types no retorna dict"
        assert len(available_types) > 0, "No hay tipos de reportes disponibles"
        
        # Verificar tipos específicos
        expected_types = ['sales', 'employee', 'product', 'geographic']
        for report_type in expected_types:
            assert report_type in available_types, f"Tipo {report_type} no está disponible"
    
    @patch('src.patterns.report_factory.AnalyticsService')
    def test_factory_creates_sales_report(self, mock_analytics):
        """Verifica que la factory puede crear reportes de ventas"""
        # Mock del servicio de analytics
        mock_analytics.return_value.get_sales_trends_by_period.return_value = pd.DataFrame({
            'period': ['2023-01', '2023-02'],
            'total_revenue': [1000, 1200],
            'total_sales': [10, 12]
        })
        
        # Crear reporte de ventas
        report = self.factory.create_report(ReportType.SALES, period='monthly')
        
        assert isinstance(report, SalesReport), "No se creó un SalesReport"
        assert report.title is not None, "Reporte no tiene título"
        assert hasattr(report, 'data'), "Reporte no tiene data"
    
    @patch('src.patterns.report_factory.AnalyticsService')
    def test_factory_creates_employee_report(self, mock_analytics):
        """Verifica que la factory puede crear reportes de empleados"""
        # Mock del servicio de analytics
        mock_analytics.return_value.get_sales_performance_by_employee.return_value = pd.DataFrame({
            'employee_name': ['Juan Pérez', 'María García'],
            'total_revenue': [5000, 6000],
            'total_sales': [50, 60]
        })
        
        # Crear reporte de empleados
        report = self.factory.create_report(ReportType.EMPLOYEE)
        
        assert isinstance(report, EmployeeReport), "No se creó un EmployeeReport"
        assert report.title is not None, "Reporte no tiene título"
    
    def test_factory_invalid_report_type(self):
        """Verifica que la factory maneja tipos inválidos correctamente"""
        with pytest.raises(ValueError, match="no soportado"):
            # Intentar crear un tipo que no existe
            invalid_type = type('InvalidType', (), {'value': 'invalid'})()
            self.factory.create_report(invalid_type)
    
    @patch('src.patterns.report_factory.AnalyticsService')
    def test_factory_comprehensive_report(self, mock_analytics):
        """Verifica que la factory puede crear múltiples reportes"""
        # Mock para diferentes métodos
        mock_service = mock_analytics.return_value
        mock_service.get_sales_performance_by_employee.return_value = pd.DataFrame({'col': [1]})
        mock_service.get_product_performance_analysis.return_value = pd.DataFrame({'col': [1]})
        mock_service.get_geographic_sales_analysis.return_value = pd.DataFrame({'col': [1]})
        
        # Crear múltiples reportes
        reports = self.factory.create_comprehensive_report(['employee', 'product', 'geographic'])
        
        assert isinstance(reports, dict), "create_comprehensive_report no retorna dict"
        assert len(reports) == 3, "No se crearon todos los reportes solicitados"
        assert 'employee' in reports, "No se creó reporte de empleados"
        assert 'product' in reports, "No se creó reporte de productos"
        assert 'geographic' in reports, "No se creó reporte geográfico"
    
    def test_factory_info(self):
        """Verifica que la factory proporciona información correcta"""
        factory_info = self.factory.get_factory_info()
        
        assert isinstance(factory_info, dict), "get_factory_info no retorna dict"
        assert 'pattern_type' in factory_info, "No se reporta el tipo de patrón"
        assert factory_info['pattern_type'] == 'Factory Method', "Tipo de patrón incorrecto"
        assert 'total_report_types' in factory_info, "No se reporta total de tipos"
        assert factory_info['total_report_types'] > 0, "Total de tipos debe ser mayor a 0"


class TestBuilderPattern:
    """
    Pruebas para verificar que el patrón Builder funciona correctamente.
    """
    
    def setup_method(self):
        """Configuración para cada prueba"""
        self.builder = SQLQueryBuilder()
    
    def test_builder_initialization(self):
        """Verifica que el builder se inicializa correctamente"""
        assert self.builder is not None, "Builder no se inicializó"
        assert len(self.builder._select_fields) == 0, "Builder no está limpio al inicializar"
        assert self.builder._from_table == "", "Builder no está limpio al inicializar"
    
    def test_builder_reset(self):
        """Verifica que reset limpia el builder correctamente"""
        # Configurar builder con datos
        self.builder.select("field1").from_table("table1").where("condition1")
        
        # Verificar que tiene datos
        assert len(self.builder._select_fields) > 0, "Builder debería tener datos"
        assert self.builder._from_table != "", "Builder debería tener tabla"
        
        # Reset y verificar limpieza
        self.builder.reset()
        assert len(self.builder._select_fields) == 0, "Reset no limpió select_fields"
        assert self.builder._from_table == "", "Reset no limpió from_table"
    
    def test_builder_fluent_interface(self):
        """Verifica que el builder soporta fluent interface (method chaining)"""
        result = (self.builder
                 .select("field1", "field2")
                 .from_table("test_table")
                 .where("field1 > 0")
                 .order_by("field1"))
        
        # Verificar que retorna self para chaining
        assert result is self.builder, "Builder no soporta method chaining"
    
    def test_builder_simple_query_construction(self):
        """Verifica que el builder puede construir consultas simples"""
        query = (self.builder
                .select("id", "name")
                .from_table("users")
                .where("active = 1")
                .order_by("name")
                .build())
        
        assert "SELECT id, name" in query, "SELECT no se construyó correctamente"
        assert "FROM users" in query, "FROM no se construyó correctamente"
        assert "WHERE active = 1" in query, "WHERE no se construyó correctamente"
        assert "ORDER BY name ASC" in query, "ORDER BY no se construyó correctamente"
    
    def test_builder_with_aggregates(self):
        """Verifica que el builder puede manejar funciones agregadas"""
        query = (self.builder
                .select_aggregate("COUNT", "*", "total_count")
                .select_aggregate("SUM", "amount", "total_amount")
                .from_table("sales")
                .build())
        
        assert "COUNT(*) as total_count" in query, "Agregado COUNT no se construyó"
        assert "SUM(amount) as total_amount" in query, "Agregado SUM no se construyó"
    
    def test_builder_with_joins(self):
        """Verifica que el builder puede manejar JOINs"""
        query = (self.builder
                .select("u.name", "p.title")
                .from_table("users u")
                .inner_join("posts p", "u.id = p.user_id")
                .left_join("comments c", "p.id = c.post_id")
                .build())
        
        assert "INNER JOIN posts p ON u.id = p.user_id" in query, "INNER JOIN no se construyó"
        assert "LEFT JOIN comments c ON p.id = c.post_id" in query, "LEFT JOIN no se construyó"
    
    def test_builder_with_parameters(self):
        """Verifica que el builder maneja parámetros correctamente"""
        self.builder.select("*").from_table("users").where_equals("id", 123)
        
        query = self.builder.build()
        params = self.builder._parameters
        
        assert ":id_eq" in query, "Parámetro no se incluyó en la consulta"
        assert "id_eq" in params, "Parámetro no se agregó a la lista"
        assert params["id_eq"] == 123, "Valor del parámetro incorrecto"
    
    def test_builder_validation(self):
        """Verifica que el builder valida consultas incompletas"""
        # Consulta sin SELECT
        with pytest.raises(ValueError, match="SELECT"):
            self.builder.from_table("test").build()
        
        # Consulta sin FROM
        with pytest.raises(ValueError, match="FROM"):
            self.builder.select("*").build()
    
    def test_sales_query_builder_specialization(self):
        """Verifica que SalesQueryBuilder funciona correctamente"""
        sales_builder = create_sales_query()
        
        # Verificar que se configuró con tabla de ventas
        assert "sales s" in sales_builder._from_table, "SalesQueryBuilder no se configuró con tabla sales"
        
        # Verificar métodos especializados
        sales_builder.with_employee_info().with_sales_metrics()
        
        # Verificar que se agregaron JOINs y campos
        assert len(sales_builder._joins) > 0, "with_employee_info no agregó JOINs"
        assert any("employee_name" in field for field in sales_builder._select_fields), "No se agregó employee_name"
    
    def test_builder_info(self):
        """Verifica que el builder proporciona información correcta"""
        # Consulta válida
        self.builder.select("*").from_table("test")
        info = self.builder.get_query_info()
        
        assert isinstance(info, dict), "get_query_info no retorna dict"
        assert info['pattern_type'] == 'Builder', "Tipo de patrón incorrecto"
        assert info['is_valid'] == True, "Consulta válida reportada como inválida"
        assert 'components' in info, "No se reportan componentes"


class TestStrategyPattern:
    """
    Pruebas para verificar que el patrón Strategy funciona correctamente.
    """
    
    def setup_method(self):
        """Configuración para cada prueba"""
        self.trend_strategy = TrendAnalysisStrategy()
        self.comparison_strategy = PerformanceComparisonStrategy()
        self.segmentation_strategy = SegmentationStrategy()
    
    def test_strategy_initialization(self):
        """Verifica que las estrategias se inicializan correctamente"""
        strategies = [self.trend_strategy, self.comparison_strategy, self.segmentation_strategy]
        
        for strategy in strategies:
            assert strategy is not None, f"Estrategia {strategy.__class__.__name__} no se inicializó"
            assert hasattr(strategy, 'analyze'), f"Estrategia {strategy.__class__.__name__} no tiene método analyze"
            assert hasattr(strategy, 'get_strategy_info'), f"Estrategia {strategy.__class__.__name__} no tiene get_strategy_info"
    
    def test_strategy_info(self):
        """Verifica que las estrategias proporcionan información correcta"""
        strategies = [self.trend_strategy, self.comparison_strategy, self.segmentation_strategy]
        
        for strategy in strategies:
            info = strategy.get_strategy_info()
            assert isinstance(info, dict), f"get_strategy_info de {strategy.__class__.__name__} no retorna dict"
            assert 'name' in info, f"Estrategia {strategy.__class__.__name__} no reporta nombre"
            assert 'description' in info, f"Estrategia {strategy.__class__.__name__} no reporta descripción"
    
    @patch('src.patterns.analysis_strategies.create_sales_query')
    def test_trend_analysis_with_data(self, mock_query_builder):
        """Verifica que TrendAnalysisStrategy analiza datos correctamente"""
        # Mock del query builder
        mock_builder = Mock()
        mock_builder.select.return_value = mock_builder
        mock_builder.with_sales_metrics.return_value = mock_builder
        mock_builder.group_by.return_value = mock_builder
        mock_builder.order_by.return_value = mock_builder
        mock_builder.execute.return_value = pd.DataFrame({
            'period': ['2023-01', '2023-02', '2023-03'],
            'total_revenue': [1000, 1200, 1100],
            'total_sales': [10, 12, 11]
        })
        mock_query_builder.return_value = mock_builder
        
        # Ejecutar análisis
        result = self.trend_strategy.analyze(period='monthly')
        
        assert isinstance(result, dict), "analyze no retorna dict"
        assert 'strategy_type' in result, "No se reporta strategy_type"
        assert result['strategy_type'] == 'trend_analysis', "strategy_type incorrecto"
        assert 'period_analyzed' in result, "No se reporta period_analyzed"
    
    def test_trend_analysis_with_empty_data(self):
        """Verifica manejo de datos vacíos en TrendAnalysisStrategy"""
        empty_data = pd.DataFrame()
        result = self.trend_strategy.analyze(data=empty_data)
        
        assert 'error' in result, "No se maneja correctamente datos vacíos"
        assert result['strategy'] == 'trend', "Strategy incorrecta en error"
    
    @patch('src.patterns.analysis_strategies.create_sales_query')
    def test_performance_comparison_analysis(self, mock_query_builder):
        """Verifica que PerformanceComparisonStrategy funciona correctamente"""
        # Mock del query builder
        mock_builder = Mock()
        mock_builder.with_employee_info.return_value = mock_builder
        mock_builder.with_sales_metrics.return_value = mock_builder
        mock_builder.group_by.return_value = mock_builder
        mock_builder.order_by_desc.return_value = mock_builder
        mock_builder.execute.return_value = pd.DataFrame({
            'employee_name': ['Juan Pérez', 'María García', 'Carlos López'],
            'total_revenue': [5000, 6000, 4500],
            'total_sales': [50, 60, 45]
        })
        mock_query_builder.return_value = mock_builder
        
        # Ejecutar análisis
        result = self.comparison_strategy.analyze(comparison_type='employees')
        
        assert isinstance(result, dict), "analyze no retorna dict"
        assert 'strategy_type' in result, "No se reporta strategy_type"
        assert result['strategy_type'] == 'performance_comparison', "strategy_type incorrecto"
        assert 'comparison_type' in result, "No se reporta comparison_type"
        assert 'top_performers' in result, "No se reportan top_performers"
    
    def test_analysis_context_strategy_switching(self):
        """Verifica que AnalysisContext puede cambiar estrategias dinámicamente"""
        context = AnalysisContext()
        
        # Inicialmente sin estrategia
        with pytest.raises(ValueError, match="No hay estrategia"):
            context.execute_analysis()
        
        # Configurar estrategia inicial
        context.set_strategy(self.trend_strategy)
        assert context._strategy is self.trend_strategy, "Estrategia no se configuró correctamente"
        
        # Cambiar estrategia
        context.set_strategy(self.comparison_strategy)
        assert context._strategy is self.comparison_strategy, "Estrategia no se cambió correctamente"
        
        # Verificar información de estrategia
        info = context.get_strategy_info()
        assert 'name' in info, "AnalysisContext no reporta info de estrategia"
    
    def test_strategy_pattern_extensibility(self):
        """Verifica que el patrón Strategy es extensible"""
        # Crear una nueva estrategia de prueba
        class TestStrategy(TrendAnalysisStrategy):
            def analyze(self, **kwargs):
                return {'strategy_type': 'test_strategy', 'test': True}
            
            def get_strategy_info(self):
                return {'name': 'Test Strategy', 'description': 'Strategy for testing'}
        
        # Usar la nueva estrategia
        test_strategy = TestStrategy()
        context = AnalysisContext(test_strategy)
        
        result = context.execute_analysis()
        assert result['strategy_type'] == 'test_strategy', "Nueva estrategia no funciona"
        assert result['test'] == True, "Nueva estrategia no retorna datos correctos"


class TestIntegratedPatterns:
    """
    Pruebas de integración para verificar que todos los patrones funcionan juntos.
    """
    
    @patch('src.database.connection.DatabaseConnection.test_connection')
    @patch('src.patterns.report_factory.AnalyticsService')
    def test_singleton_factory_integration(self, mock_analytics, mock_connection):
        """Verifica integración entre Singleton y Factory"""
        mock_connection.return_value = True
        mock_analytics.return_value.get_sales_performance_by_employee.return_value = pd.DataFrame({
            'employee_name': ['Test Employee'],
            'total_revenue': [1000]
        })
        
        # Usar Singleton para verificar conexión
        db = DatabaseConnection()
        connection_ok = db.test_connection()
        assert connection_ok, "Singleton no reporta conexión OK"
        
        # Usar Factory para crear reporte
        factory = ReportFactory()
        report = factory.create_report(ReportType.EMPLOYEE)
        
        assert isinstance(report, EmployeeReport), "Factory no creó reporte correcto"
    
    @patch('src.patterns.query_builder.DatabaseConnection')
    def test_builder_strategy_integration(self, mock_db_class):
        """Verifica integración entre Builder y Strategy"""
        # Mock de la conexión en el builder
        mock_db = Mock()
        mock_db.execute_query_to_dataframe.return_value = pd.DataFrame({
            'period': ['2023-01'],
            'total_revenue': [1000],
            'total_sales': [10]
        })
        mock_db_class.return_value = mock_db
        
        # Crear consulta con Builder
        builder = create_sales_query()
        query = builder.with_sales_metrics().build()
        
        assert "COUNT(s.SalesID)" in query, "Builder no construyó métricas correctamente"
        
        # Usar resultado con Strategy
        strategy = TrendAnalysisStrategy()
        result = strategy.analyze(data=pd.DataFrame({
            'period': ['2023-01'],
            'total_revenue': [1000],
            'total_sales': [10]
        }))
        
        assert 'strategy_type' in result, "Strategy no procesó datos del Builder"
    
    def test_all_patterns_documented(self):
        """Verifica que todos los patrones están correctamente documentados"""
        # Verificar Singleton
        db = DatabaseConnection()
        assert db.__class__.__doc__ is not None, "Singleton no tiene documentación"
        
        # Verificar Factory
        factory = ReportFactory()
        assert factory.__class__.__doc__ is not None, "Factory no tiene documentación"
        assert "Factory Pattern" in factory.__class__.__doc__, "Factory no documenta el patrón"
        
        # Verificar Builder
        builder = SQLQueryBuilder()
        assert builder.__class__.__doc__ is not None, "Builder no tiene documentación"
        assert "Builder Pattern" in builder.__class__.__doc__, "Builder no documenta el patrón"
        
        # Verificar Strategy
        strategy = TrendAnalysisStrategy()
        assert strategy.__class__.__doc__ is not None, "Strategy no tiene documentación"
        assert "Strategy" in strategy.__class__.__doc__, "Strategy no documenta el patrón"


# Fixtures para pytest
@pytest.fixture
def sample_sales_data():
    """Fixture que proporciona datos de muestra para las pruebas"""
    return pd.DataFrame({
        'employee_name': ['Juan Pérez', 'María García', 'Carlos López'],
        'total_revenue': [5000, 6000, 4500],
        'total_sales': [50, 60, 45],
        'total_units_sold': [100, 120, 90]
    })

@pytest.fixture
def sample_trend_data():
    """Fixture que proporciona datos de tendencias para las pruebas"""
    return pd.DataFrame({
        'period': ['2023-01', '2023-02', '2023-03'],
        'total_revenue': [10000, 12000, 11000],
        'total_sales': [100, 120, 110]
    })

if __name__ == "__main__":
    # Ejecutar pruebas directamente
    pytest.main([__file__, "-v", "--tb=short"])