from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'scanner'

# Router برای API
router = DefaultRouter()
router.register('scans', api_views.ScanViewSet, basename='scan')
router.register('hosts', api_views.HostViewSet, basename='host')
router.register('ports', api_views.PortViewSet, basename='port')
router.register('vulnerabilities', api_views.VulnerabilityViewSet, basename='vulnerability')

# URLهای معمولی (Template)
template_urls = [
    path('', views.ScanListView.as_view(), name='scan_list'),
    path('new/', views.ScanCreateView.as_view(), name='scan_create'),
    path('<int:pk>/', views.ScanDetailView.as_view(), name='scan_detail'),
]

# URLهای API
api_urls = [
    path('', include(router.urls)),
]

# ترکیب: مسیرهای معمولی + API
urlpatterns = template_urls + [path('api/', include(api_urls))]