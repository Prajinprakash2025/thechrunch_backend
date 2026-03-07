from django.urls import path
from . import views

urlpatterns = [
    # GET /api/customers/ (Supports search: /api/customers/?search=9876543210)
    path('', views.CustomerListView.as_view(), name='customer-list'),
    
    # POST /api/customers/<user_id>/toggle-block/
    path('<int:user_id>/toggle-block/', views.ToggleBlockCustomerView.as_view(), name='toggle-block'),
    
    # GET /api/customers/export/csv/
path('export/csv/', views.ExportCustomersCSV.as_view(), name='export-csv'),]