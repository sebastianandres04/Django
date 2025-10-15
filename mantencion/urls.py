from django.urls import path
from . import views

app_name = 'mantencion'
urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),
    
    # Gestión de vehículos
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    
    # Gestión de mantenimientos
    path('maintenances/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenances/<int:pk>/', views.MaintenanceDetailView.as_view(), name='maintenance_detail'),
    
    # Evaluaciones de servicios
    path('evaluations/', views.ServiceEvaluationListView.as_view(), name='evaluation_list'),
    path('evaluations/<int:pk>/', views.ServiceEvaluationDetailView.as_view(), name='evaluation_detail'),
    path('evaluations/<int:pk>/results/', views.ServiceEvaluationResultsView.as_view(), name='evaluation_results'),
    path('evaluations/<int:evaluation_id>/vote/', views.vote_evaluation, name='vote_evaluation'),
]
