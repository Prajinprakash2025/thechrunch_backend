from django.urls import path
from . import views

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customer-list'),
    path('<int:user_id>/toggle-block/', views.ToggleBlockCustomerView.as_view(), name='toggle-block'),
    path('export/csv/', views.ExportCustomersCSV.as_view(), name='export-csv'),
]