"""
Tests para funcionalidades SQL avanzadas
Pruebas de CTE, Funciones Ventana, Objetos SQL y Análisis Avanzado
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from services.advanced_analytics_service import AdvancedAnalyticsService
from database.connection import DatabaseConnection


class TestDatabaseConnection:
    """Tests para la conexión de base de datos en el contexto SQL avanzado."""
    
    def test_singleton_pattern(self):
        """Prueba que DatabaseConnection implementa Singleton correctamente."""
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        
        assert db1 is db2, "DatabaseConnection debe ser Singleton"
    
    @patch('src.database.connection.create_engine')
    def test_connection_pool_configuration(self, mock_create_engine):
        """Prueba la configuración del pool de conexiones."""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConnection()
        
        # Verificar que se creó el engine con configuración de pool
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        
        # Verificar parámetros de pool en la URL o kwargs
        assert any('pool' in str(arg) for arg in call_args[0] + tuple(call_args[1].values()))


class TestAdvancedAnalyticsService:
    """Tests para el servicio de análisis avanzado."""
    
    @pytest.fixture
    def mock_service(self):
        """Fixture que proporciona un servicio mockeado."""
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_service_initialization(self, mock_service):
        """Prueba la inicialización del servicio."""
        service, mock_db = mock_service
        
        assert service.db is not None
        assert hasattr(service, 'logger')
    
    def test_get_employee_performance_ranking_structure(self, mock_service):
        """Prueba la estructura del DataFrame retornado por ranking de empleados."""
        service, mock_db = mock_service
        
        # Mock de datos de retorno
        mock_df = pd.DataFrame({
            'employee_name': ['Juan Pérez', 'María García'],
            'Gender': ['M', 'F'],
            'total_revenue': [50000.0, 45000.0],
            'revenue_rank': [1, 2],
            'performance_category': ['Top Performer (10%)', 'High Performer (30%)']
        })
        
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        result = service.get_employee_performance_ranking(months_back=12)
        
        # Verificar estructura del DataFrame
        expected_columns = ['employee_name', 'Gender', 'total_revenue', 'revenue_rank', 'performance_category']
        for col in expected_columns:
            assert col in result.columns, f"Columna {col} debe estar presente"
        
        # Verificar tipos de datos
        assert result['revenue_rank'].dtype in [np.int64, int], "revenue_rank debe ser entero"
        assert result['total_revenue'].dtype in [np.float64, float], "total_revenue debe ser float"
        
        # Verificar que se llamó con parámetros correctos
        mock_db.execute_query_to_dataframe.assert_called_once()
        call_args = mock_db.execute_query_to_dataframe.call_args
        assert 'months_back' in call_args[1]
        assert call_args[1]['months_back'] == 12
    
    def test_get_sales_trends_analysis_structure(self, mock_service):
        """Prueba la estructura del análisis de tendencias."""
        service, mock_db = mock_service
        
        # Mock de datos de tendencias
        mock_df = pd.DataFrame({
            'period': ['2023-01', '2023-02', '2023-03'],
            'revenue': [100000.0, 110000.0, 105000.0],
            'mom_growth_percent': [0.0, 10.0, -4.5],
            'trend_indicator': ['On Trend', 'Above Trend', 'Below Trend'],
            'seasonal_classification': ['Normal Season', 'High Season', 'Normal Season']
        })
        
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        result = service.get_sales_trends_analysis(start_year=2023, months_to_analyze=12)
        
        # Verificar columnas clave
        expected_columns = ['period', 'revenue', 'mom_growth_percent', 'trend_indicator']
        for col in expected_columns:
            assert col in result.columns, f"Columna {col} debe estar presente"
        
        # Verificar valores de categorías
        trend_values = result['trend_indicator'].unique()
        valid_trends = ['Above Trend', 'On Trend', 'Below Trend']
        for trend in trend_values:
            assert trend in valid_trends, f"Valor de tendencia {trend} no es válido"


class TestSQLObjects:
    """Tests para objetos SQL personalizados."""
    
    @pytest.fixture
    def mock_service(self):
        """Fixture para servicio con conexión mockeada."""
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_create_advanced_sql_objects(self, mock_service):
        """Prueba la creación de objetos SQL avanzados."""
        service, mock_db = mock_service
        
        # Mock de contexto de conexión
        mock_connection = Mock()
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_db.get_connection.return_value.__exit__.return_value = None
        
        result = service.create_advanced_sql_objects()
        
        # Verificar que retorna un diccionario con resultados
        assert isinstance(result, dict), "Debe retornar un diccionario"
        
        # Verificar que contiene las claves esperadas
        expected_keys = [
            'function_calculate_commission',
            'function_classify_customer',
            'view_executive_dashboard',
            'view_product_category_analysis',
            'trigger_sales_audit',
            'trigger_sales_validation',
            'procedure_monthly_report',
            'procedure_top_customers',
            'indexes_advanced'
        ]
        
        for key in expected_keys:
            assert key in result, f"Clave {key} debe estar presente"
            assert isinstance(result[key], bool), f"Valor de {key} debe ser booleano"
    
    def test_calculate_employee_commission_parameters(self, mock_service):
        """Prueba el cálculo de comisiones con parámetros válidos."""
        service, mock_db = mock_service
        
        # Mock del resultado de la función SQL
        mock_df = pd.DataFrame({'commission': [2500.00]})
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        employee_id = 1
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        
        result = service.calculate_employee_commission(employee_id, start_date, end_date)
        
        # Verificar que retorna un float
        assert isinstance(result, float), "Comisión debe ser un float"
        assert result >= 0, "Comisión debe ser no negativa"
        
        # Verificar que se llamó con parámetros correctos
        mock_db.execute_query_to_dataframe.assert_called_once()
        call_args = mock_db.execute_query_to_dataframe.call_args
        params = call_args[1]
        
        assert params['employee_id'] == employee_id
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
    
    def test_classify_customer_value_categories(self, mock_service):
        """Prueba la clasificación de clientes."""
        service, mock_db = mock_service
        
        # Test diferentes categorías
        test_cases = [
            ('VIP', 1),
            ('Premium', 2),
            ('Gold', 3),
            ('Silver', 4),
            ('Bronze', 5),
            ('New', 6)
        ]
        
        for expected_tier, customer_id in test_cases:
            mock_df = pd.DataFrame({'customer_tier': [expected_tier]})
            mock_db.execute_query_to_dataframe.return_value = mock_df
            
            result = service.classify_customer_value(customer_id)
            
            assert isinstance(result, str), "Clasificación debe ser string"
            assert result == expected_tier, f"Esperado {expected_tier}, obtenido {result}"
            
            # Verificar que se llamó con el customer_id correcto
            call_args = mock_db.execute_query_to_dataframe.call_args
            assert call_args[1]['customer_id'] == customer_id


class TestCTEQueries:
    """Tests específicos para consultas CTE."""
    
    @pytest.fixture
    def mock_service(self):
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_cte_employee_ranking_query_structure(self, mock_service):
        """Prueba que la consulta CTE de ranking tenga la estructura correcta."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'employee_name': ['Test Employee'],
            'revenue_rank': [1],
            'revenue_percentile_pct': [95.5],
            'performance_category': ['Top Performer (10%)']
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        result = service.get_employee_performance_ranking()
        
        # Verificar que se ejecutó una query
        mock_db.execute_query_to_dataframe.assert_called_once()
        
        # Verificar la query contiene CTE
        call_args = mock_db.execute_query_to_dataframe.call_args
        query = call_args[0][0]
        
        assert 'WITH' in query.upper(), "Query debe contener CTE (WITH clause)"
        assert 'ROW_NUMBER()' in query.upper() or 'RANK()' in query.upper(), "Query debe usar funciones ventana"
        assert 'OVER' in query.upper(), "Query debe usar OVER clause"
    
    def test_cte_trends_analysis_recursive(self, mock_service):
        """Prueba que el análisis de tendencias use CTE recursivo."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'period': ['2023-01'],
            'revenue': [100000.0],
            'mom_growth_percent': [5.0]
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        result = service.get_sales_trends_analysis()
        
        # Verificar query
        call_args = mock_db.execute_query_to_dataframe.call_args
        query = call_args[0][0]
        
        assert 'RECURSIVE' in query.upper(), "Query debe usar CTE recursivo"
        assert 'UNION ALL' in query.upper(), "CTE recursivo debe usar UNION ALL"


class TestWindowFunctions:
    """Tests para funciones ventana."""
    
    def test_window_function_results_consistency(self):
        """Prueba la consistencia de resultados de funciones ventana."""
        # Datos de prueba simulados
        test_data = pd.DataFrame({
            'employee_name': ['A', 'B', 'C', 'D', 'E'],
            'total_revenue': [100000, 80000, 60000, 40000, 20000],
            'revenue_rank': [1, 2, 3, 4, 5],
            'revenue_percentile_pct': [100.0, 75.0, 50.0, 25.0, 0.0]
        })
        
        # Verificar que los rankings estén ordenados correctamente
        assert test_data['revenue_rank'].is_monotonic_increasing, "Rankings deben ser crecientes"
        
        # Verificar que los ingresos estén en orden descendente según rank
        sorted_by_rank = test_data.sort_values('revenue_rank')
        assert sorted_by_rank['total_revenue'].is_monotonic_decreasing, "Ingresos deben decrecer con rank"
        
        # Verificar rango de percentiles
        percentiles = test_data['revenue_percentile_pct']
        assert percentiles.min() >= 0, "Percentiles deben ser >= 0"
        assert percentiles.max() <= 100, "Percentiles deben ser <= 100"


class TestStoredProcedures:
    """Tests para procedimientos almacenados."""
    
    @pytest.fixture
    def mock_service(self):
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_generate_monthly_report_parameters(self, mock_service):
        """Prueba la generación de reportes mensuales."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'ranking': [1, 2],
            'employee_name': ['Employee 1', 'Employee 2'],
            'revenue': [50000.0, 40000.0],
            'performance_rating': ['Excellent', 'Good']
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        year = 2024
        month = 3
        min_revenue = 1000.0
        
        result = service.generate_monthly_report(year, month, min_revenue)
        
        # Verificar parámetros de llamada
        call_args = mock_db.execute_query_to_dataframe.call_args
        params = call_args[1]
        
        assert params['year'] == year
        assert params['month'] == month
        assert params['min_revenue'] == min_revenue
        
        # Verificar estructura del resultado
        assert 'ranking' in result.columns
        assert 'employee_name' in result.columns
        assert 'revenue' in result.columns
    
    def test_analyze_top_customers_parameters(self, mock_service):
        """Prueba el análisis de mejores clientes."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'customer_rank': [1, 2],
            'customer_name': ['Customer 1', 'Customer 2'],
            'total_spent': [25000.0, 20000.0],
            'total_purchases': [50, 40]
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        top_n = 20
        analysis_months = 12
        
        result = service.analyze_top_customers(top_n, analysis_months)
        
        # Verificar parámetros
        call_args = mock_db.execute_query_to_dataframe.call_args
        params = call_args[1]
        
        assert params['top_n'] == top_n
        assert params['analysis_months'] == analysis_months
        
        # Verificar que los resultados estén ordenados
        assert result['customer_rank'].is_monotonic_increasing, "Rankings deben ser crecientes"


class TestAuditSystem:
    """Tests para sistema de auditoría."""
    
    @pytest.fixture
    def mock_service(self):
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_get_sales_audit_log_structure(self, mock_service):
        """Prueba la estructura del log de auditoría."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'audit_id': [1, 2],
            'sales_id': [100, 101],
            'action_type': ['INSERT', 'UPDATE'],
            'change_timestamp': [datetime.now(), datetime.now()],
            'changed_by': ['user1@domain.com', 'user2@domain.com']
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        result = service.get_sales_audit_log(days_back=30)
        
        # Verificar columnas obligatorias
        required_columns = ['audit_id', 'sales_id', 'action_type', 'change_timestamp']
        for col in required_columns:
            assert col in result.columns, f"Columna {col} debe estar presente"
        
        # Verificar tipos de acción válidos
        valid_actions = ['INSERT', 'UPDATE', 'DELETE']
        for action in result['action_type'].unique():
            assert action in valid_actions, f"Acción {action} no es válida"
    
    def test_audit_log_date_filtering(self, mock_service):
        """Prueba el filtrado por fechas en auditoría."""
        service, mock_db = mock_service
        
        mock_df = pd.DataFrame({
            'audit_id': [1],
            'sales_id': [100],
            'action_type': ['INSERT'],
            'change_timestamp': [datetime.now()]
        })
        mock_db.execute_query_to_dataframe.return_value = mock_df
        
        days_back = 7
        result = service.get_sales_audit_log(days_back=days_back)
        
        # Verificar que se pasó el parámetro correcto
        call_args = mock_db.execute_query_to_dataframe.call_args
        params = call_args[1]
        assert params['days_back'] == days_back


class TestIntegrationScenarios:
    """Tests de integración para escenarios completos."""
    
    @pytest.fixture
    def mock_service(self):
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            return service, mock_db_instance
    
    def test_complete_analytics_workflow(self, mock_service):
        """Prueba un flujo completo de análisis."""
        service, mock_db = mock_service
        
        # Mock de datos para diferentes consultas
        dashboard_data = pd.DataFrame({
            'EmployeeID': [1, 2],
            'employee_name': ['Employee 1', 'Employee 2'],
            'revenue_12m': [50000.0, 40000.0]
        })
        
        ranking_data = pd.DataFrame({
            'employee_name': ['Employee 1', 'Employee 2'],
            'revenue_rank': [1, 2]
        })
        
        # Simular llamadas secuenciales
        mock_db.execute_query_to_dataframe.side_effect = [dashboard_data, ranking_data]
        
        # Ejecutar workflow
        dashboard = service.get_executive_dashboard()
        ranking = service.get_employee_performance_ranking()
        
        # Verificar que ambas consultas se ejecutaron
        assert mock_db.execute_query_to_dataframe.call_count == 2
        
        # Verificar consistencia de datos
        assert len(dashboard) > 0, "Dashboard debe tener datos"
        assert len(ranking) > 0, "Ranking debe tener datos"
    
    def test_error_handling_in_sql_objects(self, mock_service):
        """Prueba el manejo de errores en objetos SQL."""
        service, mock_db = mock_service
        
        # Simular error en la base de datos
        from sqlalchemy.exc import SQLAlchemyError
        mock_db.execute_query_to_dataframe.side_effect = SQLAlchemyError("Test error")
        
        # Verificar que se manejan las excepciones
        with pytest.raises(SQLAlchemyError):
            service.get_executive_dashboard()


class TestPerformanceMetrics:
    """Tests para métricas de rendimiento."""
    
    def test_query_parameter_binding(self):
        """Prueba que las consultas usen parámetros bindados."""
        # Mock de servicio
        with patch('src.services.advanced_analytics_service.DatabaseConnection') as mock_db:
            mock_db_instance = Mock()
            mock_db.return_value = mock_db_instance
            
            service = AdvancedAnalyticsService()
            service.db = mock_db_instance
            
            mock_df = pd.DataFrame({'test': [1]})
            mock_db_instance.execute_query_to_dataframe.return_value = mock_df
            
            # Ejecutar consulta con parámetros
            service.get_employee_performance_ranking(months_back=6)
            
            # Verificar que se pasaron parámetros
            call_args = mock_db_instance.execute_query_to_dataframe.call_args
            assert len(call_args) >= 2, "Debe haber query y parámetros"
            
            params = call_args[1] if len(call_args) > 1 else {}
            assert isinstance(params, dict), "Parámetros deben ser diccionario"
            assert 'months_back' in params, "Debe incluir parámetro months_back"


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, '-v', '--tb=short'])