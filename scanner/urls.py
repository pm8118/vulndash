from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.ScanListView.as_view(), name='scan_list'),
    path('new/', views.ScanCreateView.as_view(), name='scan_create'),
    path('<int:pk>/', views.ScanDetailView.as_view(), name='scan_detail'),
]