import pytest
from datetime import datetime, timedelta
from src.services.analytics_service import AnalyticsService

@pytest.fixture
def analytics_service():
    return AnalyticsService()

def test_employee_performance_no_crash(analytics_service):
    results = analytics_service.get_sales_performance_by_employee()
    assert isinstance(results, list)

def test_geographic_sales_analysis(analytics_service):
    result = analytics_service.get_geographic_sales_analysis()
    assert isinstance(result, list)

def test_product_performance_metrics(analytics_service):
    result = analytics_service.get_product_performance_analysis()
    assert isinstance(result, list)

def test_customer_segmentation_analysis(analytics_service):
    result = analytics_service.get_customer_segmentation()
    assert isinstance(result, list)

def test_sales_trends_daily_and_monthly(analytics_service):
    daily = analytics_service.get_sales_trends_by_period("daily")
    monthly = analytics_service.get_sales_trends_by_period("monthly")
    assert isinstance(daily, list)
    assert isinstance(monthly, list)

def test_invalid_sales_trend_period(analytics_service):
    with pytest.raises(ValueError):
        analytics_service.get_sales_trends_by_period("yearly")

def test_discount_range_analysis_runs(analytics_service):
    result = analytics_service.get_discount_effectiveness_analysis()
    assert isinstance(result, list)

def test_dashboard_generation(analytics_service):
    dashboard = analytics_service.generate_executive_dashboard()
    assert "general_metrics" in dashboard
    assert "top_products" in dashboard
    assert "top_employees" in dashboard
    assert "sales_by_country" in dashboard